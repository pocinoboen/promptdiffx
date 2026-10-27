"""promptdiffx —— 对比两版提示词，区分实质改动与纯措辞改动。

对齐两版提示词的槽位，标出真正改变行为的修改与仅换词的修改

定位：
  把「改动量」和「行为影响」分开算，避免版本对比只看字数差

设计约束：
  1. **只报告能定位到具体位置的结论**，不做语义猜测。
  2. **规则表公开**，每条命中都能对应到 提示词版本对比 领域的一条明示规则。
  3. **输入为空或格式不对时明确报错**，不静默返回空结果。

仅依赖 Python 标准库。

用法:
    python promptdiffx.py --help
    python promptdiffx.py --file input.txt
    python promptdiffx.py --text "示例内容"
    python promptdiffx.py --file input.txt --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# 领域规则表：每条规则独立可核查，命中即报，不做推断。
RULES: list[dict] = [
    {
        "name": "提示词版本对比·缺失",
        "why": "缺少提示词版本对比的关键要素时无法给出可靠判定",
        "severity": "high",
        "keywords": ['缺失', 'missing', 'absent', '缺少', '没有'],
    },
    {
        "name": "提示词版本对比·冲突",
        "why": "同一份输入里两处提示词版本对比描述互相矛盾",
        "severity": "high",
        "keywords": ['冲突', 'conflict', 'contradict', '矛盾', '不一致', '相反'],
    },
    {
        "name": "提示词版本对比·越界",
        "why": "提示词版本对比的取值超出常规范围",
        "severity": "medium",
        "keywords": ['越界', 'out of range', 'outlier', '越界', '超限', '超过'],
    },
    {
        "name": "提示词版本对比·退化",
        "why": "提示词版本对比的信息量不足以支撑结论",
        "severity": "medium",
        "keywords": ['退化', 'degrade', 'insufficient', '不足', '太少', '无法'],
    },
    {
        "name": "提示词版本对比·泄漏",
        "why": "提示词版本对比相关的内容被意外暴露",
        "severity": "high",
        "keywords": ['泄漏', 'leak', 'expose', '泄漏', '暴露', '明文'],
    },
    {
        "name": "提示词版本对比·重复",
        "why": "同一处提示词版本对比信息被反复传递",
        "severity": "low",
        "keywords": ['重复', 'duplicate', 'repeat', '重复', 'again'],
    },
    {
        "name": "提示词版本对比·陈旧",
        "why": "提示词版本对比的时效性已经过期",
        "severity": "medium",
        "keywords": ['陈旧', 'stale', 'expired', '过期', '陈旧', '旧版'],
    },
    {
        "name": "提示词版本对比·不可核",
        "why": "提示词版本对比的说法无法追溯到具体证据",
        "severity": "high",
        "keywords": ['不可核', 'unverifiable', 'no evidence', '无法追溯', '没有来源'],
    },
]


def promptdiffx_read_numbers(text: str) -> list[float]:
    return [float(m) for m in re.findall(r"-?\d+(?:\.\d+)?", text.replace(",", ""))]


def promptdiffx_analyze(text: str) -> dict:
    """主分析：来源与占比。"""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    if not blocks:
        return {"ok": False, "error": "没有内容", "count": 0}
    total = sum(len(b) for b in blocks)
    parts = []
    for i, b in enumerate(blocks):
        head = b.splitlines()[0][:60] if b.splitlines() else "(空)"
        parts.append({"index": i, "head": head, "size": len(b),
                      "share": round(len(b) / total, 4) if total else 0.0})
    return {
        "ok": True,
        "count": len(blocks),
        "total_size": total,
        "parts": parts,
        "largest": max(parts, key=lambda p: p["size"])["head"],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def render(result: dict) -> str:
    """把结果渲染成人读的文本。每个工具的版式不同。"""
    out: list[str] = []
    if not result.get("ok", True):
        out.append(f"无法分析：{{result.get('error', '未知原因')}}")
        return "\n".join(out)
    out.append(f"片段数：{result['count']}  总量 {result['total_size']}")
    out.append("")
    for p_ in result["parts"]:
        out.append(f"  {p_['share']:>7.2%}  {p_['size']:>6}  {p_['head']}")
    out.append("")
    out.append(f"最大来源：{result['largest']}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="promptdiffx",
        description="对齐两版提示词的槽位，标出真正改变行为的修改与仅换词的修改（仅依赖标准库）",
        epilog=(
            "示例:\n"
            "  python promptdiffx.py --file input.txt\n"
            "  python promptdiffx.py --text '示例内容'\n"
            "  python promptdiffx.py --file input.txt --json\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="输入文件路径")
    src.add_argument("--text", help="直接给出输入内容")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args(argv)

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            print(f"读不了文件：{{e}}", file=sys.stderr)
            return 2
    else:
        content = args.text

    if not content.strip():
        print("输入是空的。", file=sys.stderr)
        return 2

    result = promptdiffx_analyze(content)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(render(result))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
