# Modules

这里放可执行研究模块。每个模块建议结构：

```text
<module_name>/
  README.md
  _test_*.py
  outputs/
  logs/
```

脚本必须用 `pathlib.Path` 和 `__file__` 定位路径，不依赖当前工作目录。诊断输出优先写到模块自己的 `outputs/`。
