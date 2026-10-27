# promptdiffx

**对比两版提示词，区分实质改动与纯措辞改动。**

`promptdiffx` —— 对齐两版提示词的槽位，标出真正改变行为的修改与仅换词的修改

- 零依赖，Python 3.10+ 标准库即可运行
- 单文件，`promptdiffx.py` 拷走就能用
- 不联网、不写文件

<!-- ipos:install -->
## 安装

零依赖，Python 3.10+ 即可：

```bash
pip install pocinoboen-promptdiffx
```

装完直接用命令名调用：

```bash
promptdiffx --help
```

也可以不用安装，直接把 `promptdiffx.py` 拷走用——它只依赖标准库。

## 为什么需要它

把「改动量」和「行为影响」分开算，避免版本对比只看字数差

它遵守下面几条自己定的规矩：

1. **只报告能定位到具体位置的结论**，不做语义猜测。
2. **规则表公开**，每条命中都能对应到 提示词版本对比 领域的一条明示规则。
3. **输入为空或格式不对时明确报错**，不静默返回空结果。

## 用法

```bash
python promptdiffx.py --file input.txt
python promptdiffx.py --text "示例内容"
python promptdiffx.py --file input.txt --json
```

加 `--json` 可以拿到机器可读的结果，便于接到流水线里。

## 已知局限

- 计数按字面 token 统计，不做词形还原。
- 只报告分布，不判断该保留哪些。

## 跑测试

```bash
python test_promptdiffx.py
```

测试用独立的断言与临时数据，不污染工作目录。

## 来源与参考

- Python 标准库文档：<https://docs.python.org/3/>
- GitHub 仓库：<https://github.com/pocinoboen/promptdiffx>

---

## 关于作者

pocinoboen 做提示词版本对比相关的问题。这个工具先替你回答一个具体问题，再谈别的。

- 个人主页：<https://pocinoboen.github.io>
- 仓库：<https://github.com/pocinoboen/promptdiffx>

## 许可

MIT，见 [LICENSE](LICENSE)。
