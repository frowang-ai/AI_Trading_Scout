# 仓库清理审计 2026-05-22

本文记录对仓库顶层文件、旧数据目录和临时脚本的清理判断。结论基于当前工作区文件、引用检索和 live docs；2026-05-22 已按本文建议清理旧 CSV 目录和临时脚本。

## 当前工作区状态

- 当前仓库只有一个历史提交，工作区存在大量未提交删除、修改和未跟踪文件。
- `data/` 已在 `.gitignore` 中，当前约 7.8GB。
- `财联社电报数据/` 清理前约 486MB，未跟踪，已删除，并已加入 `.gitignore`，避免后续误提交同名大目录。
- `test.py` 是已跟踪文件，内容是本地 LLM 网关连通性测试草稿，已删除。

## 顶层目录判断

| 路径 | 当前用途 | 清理建议 |
| --- | --- | --- |
| `get_data_cls/` | 财联社线上抓取、旧 CSV 标准化、full-fields raw 倒序抓取和 Parquet 构建 | 保留 |
| `data/` | 本地数据湖，含 raw、processed、reports、external | 保留本地，不进 Git |
| `财联社电报数据/` | 2014-2025 财联社旧 CSV 原始输入，曾供 `get_data_cls/build_cls_telegraph_parquet.py` 和 `_test_cls_preview.py` 读取 | 已删除 |
| `demo/demo1-逆向总分/output/` | 约 3.6GB 的实验输出 | 优先清理候选；如结论已沉淀到文档或可复现，可删除 |
| `production_output/` | 生产流水线输出 | 默认不进 Git；可按日期归档或清理 |
| `logs/` | 运行日志 | 默认不进 Git；长期结论转写到 docs 后可清理 |
| `.venv/` | 本地虚拟环境 | 保留本地，不进 Git |
| `.claude/`、`.serena/` | 本地 agent/工具状态 | 保留本地，不进 Git |

## `财联社电报数据/` 是否可以删除

短结论：已删除。

证据：

- 目录当前未被 Git 跟踪。
- 目录内 14 个 CSV，合计约 486MB。
- 删除前只有两个代码文件直接引用该目录，二者已同步删除：
  - `get_data_cls/_test_cls_preview.py`
  - `get_data_cls/build_cls_telegraph_parquet.py`
- 已存在标准化结果：
  - `data/processed/cls_telegraph/cls_telegraph_2014_2025.parquet`
  - `data/processed/cls_telegraph/cls_telegraph_2014_20260521.parquet`
- `docs/data/cls_telegraph_data.md` 已记录旧 CSV 到 Parquet 的生成口径。

后续主线：

1. 事件分析和常规使用直接读取 `data/processed/cls_telegraph/cls_telegraph_2014_20260521.parquet`。
2. full-fields 原始字段通过 `get_data_cls/backfill_cls_telegraph_raw_reverse.py` 和 `get_data_cls/build_cls_telegraph_full_fields_parquet.py` 维护。
3. 不再支持从根目录旧 CSV 重建 `cls_telegraph_2014_2025.parquet`。

## `test.py` 是否还有用

短结论：已删除。

证据：

- 当前 `test.py` 只做 OpenAI SDK 和 Anthropic SDK 对本地 `http://localhost:8045` 网关的 Hello 测试。
- 未发现项目代码 import 或调用 `test.py`。
- 文件包含明文 `api_key`，即使是本地网关 key，也不应放在已跟踪代码文件中。
- 更合适的落点是 `LLMClient_v2/` 下的最小示例，或根目录删除，仅保留 `.env.example` 中的环境变量说明。

后续如仍需要本地网关连通性测试，应迁移为 `LLMClient_v2/examples/_test_local_gateway.py`，并从环境变量读取 key。

## 建议的清理顺序

1. 先处理敏感/临时脚本：删除或迁移 `test.py`。
2. 再处理旧财联社 CSV：删除或迁移 `财联社电报数据/`。
3. 再处理大体积实验输出：从 `demo/demo1-逆向总分/output/` 开始。
4. 最后整理 Git 状态：区分历史删除、文档迁移、新增模块和数据清理，不要一次性混成一个提交。

## 可执行命令草案

删除 `test.py`：

```powershell
Remove-Item -LiteralPath .\test.py
```

删除旧财联社 CSV 目录：

```powershell
Remove-Item -LiteralPath .\财联社电报数据 -Recurse
```

迁移旧财联社 CSV 到规范数据目录：

```powershell
New-Item -ItemType Directory -Force -Path .\data\raw\cls_telegraph\legacy_csv_2014_20250211
Move-Item -LiteralPath .\财联社电报数据\*.csv -Destination .\data\raw\cls_telegraph\legacy_csv_2014_20250211
Remove-Item -LiteralPath .\财联社电报数据 -Recurse
```

执行删除前应确认没有正在运行的脚本仍依赖这些路径。
