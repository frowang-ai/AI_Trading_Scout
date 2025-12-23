Always respond in Chinese-simplified
# 工程实践规范

## 1）文件路径与资源定位规范（强制）

**目的**：保证跨平台（Windows/mac/Linux）稳定访问项目内文件，避免依赖进程工作目录（`cwd`）与硬编码相对路径带来的不确定性。

**强制约定**

* **一律使用 `pathlib.Path` 与 `__file__`** 来定位**当前代码文件所在目录**及其**父目录**，再进行路径拼接。
* **禁止**直接依赖 `os.getcwd()` / 相对路径字符串进行资源定位（除非特别说明并在代码注释中注明理由）。
* 读写文本文件默认使用 `utf-8` 编码，并捕获 I/O 异常进行明确报错。
* 在交互式环境（如 REPL、notebook）里，如 `__file__` 不可用，需在代码中提供**显式回退策略**（例如使用 `Path.cwd()` 并在注释中说明差异）。

**标准模板（Python）**

```python
from pathlib import Path

# 1) 获取当前代码文件所在目录与其父目录（跨平台）
current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent.resolve()

# 2) 拼接项目内资源路径（推荐）
# 文件在当前代码同级目录
path_gdp_map = current_dir / "gdp_id_region_mapping.csv"

# 文件在父目录
path_panel_data = parent_dir / "annual_panel_data_enhanced_with_status.csv"

# 3) 读取示例（文本/CSV）
# - 文本读取示例
try:
    content = path_gdp_map.read_text(encoding="utf-8")
except FileNotFoundError:
    raise FileNotFoundError(f"文件不存在：{path_gdp_map}")
except Exception as e:
    raise RuntimeError(f"读取失败：{path_gdp_map}；原因：{e}")

# - CSV 读取（pandas 示例）
# import pandas as pd
# df = pd.read_csv(path_panel_data, encoding="utf-8")
```

**补充说明**

* `Path(__file__).parent.resolve()` 与 `Path(...).parent.resolve()` 自动处理路径分隔符与符号链接，**无需**手写 `\\` 或 `/`。
* 任何需要**写入**的产物（如缓存、日志、模型文件），应基于上述基准目录进行拼接，避免污染用户任意工作目录。
* 单元测试中，若构造临时文件，请显式传入基准目录或使用 `tmp_path`/`tmp_path_factory`（pytest）。

**反例（不要这样做）**

```python
import os

# 反例：依赖当前工作目录，易在 IDE/CI/CD 不同上下文下失效
open("data/gdp_id_region_mapping.csv")

# 反例：手写分隔符，不可移植
os.path.join("..\\data", "annual_panel_data_enhanced_with_status.csv")
```

---

## 2）当需要使用 Python 画图时

* 原则上**优先使用英文**作为图片图例。
* 若需使用 matplotlib 且包含中文，请参考下述设置以避免中文乱码（按系统择一）：

```python
import numpy as np
import matplotlib.pyplot as plt
# mac
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
# Windows
plt.rcParams['font.sans-serif'] = ['SimHei']
```

## 3）测试先行与最小改动策略

**政策声明（专业表述）**
收到任务后，**默认不直接修改核心代码**。先创建**以 `_test_` 开头**的测试脚本/用例，针对核心模块与公共接口进行验证；依据测试结论**梳理问题与回答问题**，仅在确有必要时再提出并实施**最小可行的核心代码修改**（Small, Safe Steps）。

**命名与位置**

* 测试文件统一命名：`_test_<模块或能力>.py`，例如：`_test_data_loader.py`、`_test_api_contract.py`。
* 放置位置优先放在与被测模块同级目录
* 如果测试文件 `_test_<模块或能力>.py` 中有结果要产出，也需要以 `_test_` 的前缀命名，方便与其他结果/报告相区分

**最小修改与提交策略**

* **先证伪后改动**：只有当 `_test_` 用例明确暴露问题或差距时，才对核心代码提出改动，并确保每一次改动都有对应的通过用例。
* **最小化提交**：将核心代码修改拆分为小步提交或独立分支/PR，便于审查与回滚。
* **回归保障**：合并前必须保证所有 `_test_` 用例通过，并按需补充回归测试。

已按你的要求把“先预览再读取”的做法专业化为一段**可直接粘贴**进《工程实践规范》的新章节（放在“2）测试先行与最小改动策略”之后）。原“当需要使用 Python 画图时”顺延为第 **4）节**。

---

## 4）数据读取前的“轻量预览”策略

**政策声明**  
对体量未知或可能较大的数据文件（如 `.csv`、`.xlsx`、`.dta`、`.json` 等），**禁止直接整表载入**。必须先进行**前若干行的轻量预览**以确认结构（列名、分隔符、编码、缺失/异常值形态），再决定后续读入与清洗策略。预览优先级：**pandas 前 5 行**（推荐）或**命令行前若干行**（适用于纯文本表格与换行分割的 JSONL）。

**与既有规范的衔接**

- 路径定位：严格沿用《1）文件路径与资源定位规范（强制）》中 `pathlib.Path` 的做法。
  
- 测试先行：先在 `_test_*.py` 中实现预览与结构检查用例，再对核心读取逻辑做最小修改。

### A. 使用 pandas 做最小读取（推荐）

> 仅取前 5 行；必要时配合 `usecols`、`dtype`、`sep`、`encoding` 等参数校准。

```python
from pathlib import Path
import pandas as pd

current_dir = Path(__file__).parent.resolve()
data_path = current_dir / "your_file.csv"  # 示例：按需替换

# CSV（文本表格）
df_head = pd.read_csv(
    data_path, nrows=5,
    # 可按需指定：sep=",", encoding="utf-8", usecols=["col1", "col2"], on_bad_lines="skip"
)
print("CSV 预览列：", list(df_head.columns))
print(df_head.head())

# Excel（.xlsx，注意是二进制格式，无法用 head 命令预览）
# 需 openpyxl/pyxlsb 等引擎；按需指定 sheet_name
# pandas 1.4+ 支持 nrows；若旧版本无 nrows，可用 skiprows+usecols 退化预览
# df_xlsx_head = pd.read_excel(data_path_xlsx, sheet_name=0, nrows=5, engine="openpyxl")

# Stata（.dta）——使用分块读取获取首块
# it = pd.read_stata(data_path_dta, chunksize=5)
# df_dta_head = next(it)

# JSON Lines（.jsonl，每行一个 JSON 对象）
# it = pd.read_json(data_path_jsonl, lines=True, chunksize=5)
# df_jsonl_head = next(it)

# 大 CSV 的分块扫描（示例）
# chunk_iter = pd.read_csv(data_path, chunksize=100_000)
# first_chunk = next(chunk_iter)  # 仅拿第一块做结构检查
```

**JSON（数组）注意**

- 若是**单个巨大 JSON 数组**（不是一行一对象的 JSONL），不建议在 Python 里 `json.load`（会整表进内存）。
  
- 优先使用命令行 `jq` 做流式预览（见下），或采用流式解析库（如 `ijson`）按需迭代前若干对象。
  

### B. 使用命令行轻量预览（文本文件/JSONL）

> 平台选择：若处于 **Windows**，**优先使用 bash**（WSL/Git Bash/Cygwin）。若无法使用 bash，再用 PowerShell 等价命令。

**mac/Linux（或 Windows 的 bash 环境）**

```bash
# 预览前 5 行（CSV/TSV/文本）
head -n 5 your_file.csv

# 仅显示第 1~5 行（兼容性更好）
sed -n '1,5p' your_file.csv

# JSON Lines：逐对象流式预览前 5 条
head -n 5 your_file.jsonl

# JSON（数组）：流式输出对象并截取前 5 条（需安装 jq）
jq -c '.[]' your_file.json | head -n 5
```

**Windows（PowerShell）**

```powershell
# 文本/CSV 前 5 行
Get-Content your_file.csv -TotalCount 5
# 或
Get-Content your_file.csv | Select-Object -First 5

# 建议：优先使用 bash 或安装 jq 后按 *nix 示例执行
```

> 提示：`.xlsx` 等二进制表格**不适合**用 `head` 预览；请用 pandas 的 `read_excel(..., nrows=5)` 或将其转换为 CSV 后再预览（如 `in2csv file.xlsx | head -n 5`，需安装 csvkit）。

### C. 预览后的最小验证与防呆

- **记录结构**：输出列名、数据类型、示例行；可在 `_test_*.py` 中断言关键列存在、枚举值范围合理。
  
- **异常探测**：若发现分隔符、编码、日期解析、千分位/小数点等异常，先在 `_test_*.py` 里复现与修正；核心代码延后最小改动。
  
- **大文件策略**：确认行数与列数后，采用 `usecols`、`dtype`、`parse_dates`、`chunksize` 等减压参数分批读入，避免 OOM。
  
- **日志与可追溯**：预览阶段打印（或记录日志）文件路径、行列维度、推断编码与分隔符，便于问题定位。

---

### 环境配置

当你（coding agent）配置一个 python 环境时，如果处于 Windows 设备上，请遵循下面的流程：

1. 用 uv+venv 的形式，在文件夹下创建虚拟环境
```
      # 首先检查是否安装了uv
      uv --version
      # 先cd到项目文件夹下面
      # 创建虚拟环境，指定python版本
      uv venv --python 3.12
      # 激活虚拟环境
      source .venv/Scripts/activate
      conda deactivate
      # 如果已经有pyproject.toml文件
      uv pip install -e .
      # or如果已经有requirements.txt文件
      uv pip install -r requirements.txt
```

2. 完成虚拟环境的配置之后，当需要运行 python代码了，请直接使用 venv 虚拟环境下的 `python.exe` 进行运行，如：
   `/f/codeF/llm_projects/phone_autoglm/Open-AutoGLM/.venv/Scripts/python.exe main.py --help`。此处具体的路径需要你自己 figure out 出来，如果使用的是 bash 环境，需要检查路径是否适配。