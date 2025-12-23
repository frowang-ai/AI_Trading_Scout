# 工程开发规范 (Engineering Specifications)

## 1. 环境要求 (Environment)
- **Python 版本**：必须使用 **Python 3.12** 或更高版本。
- **兼容性**：代码无需向后兼容 Python 3.9 / 3.10 等旧版本，充分利用新版本的语法特性（如类型提示改进、性能优化）。

## 2. 设计原则 (Design Principles)
- **SOLID 原则**：
  - **S (SRP)**：单一职责原则，每个类/函数只做一件事。
  - **O (OCP)**：开闭原则，对扩展开放，对修改关闭（新增因子时应增加新类而非修改旧逻辑）。
  - **L (LSP)**：里氏替换原则，子类应能替换父类。
  - **I (ISP)**：接口隔离原则，不强迫客户端依赖不使用的方法。
  - **D (DIP)**：依赖倒置原则，依赖抽象而非具体实现。

## 3. 命名规范 (Naming Conventions)
- **变量与函数**：使用 `snake_case`（蛇形命名法），如 `get_stock_price`, `daily_return`。
- **类名**：使用 `PascalCase`（大驼峰命名法），如 `DataFetcher`, `MomentumFactor`。
- **常量**：使用 `UPPER_CASE`（全大写），如 `MAX_RETRY_COUNT`, `DEFAULT_START_DATE`。
- **私有成员**：使用单下划线前缀 `_variable` 表示内部使用。

## 4. 导入规范 (Import Requirements)
- **顺序**：
  1. 标准库 (Standard Library)
  2. 第三方库 (Third-party Libraries, e.g., pandas, numpy)
  3. 本地模块 (Local Application/Library Specific)
- **方式**：
  - 推荐使用绝对导入。
  - 避免使用 `from module import *`，必须显式导入所需对象。
  - 未使用的引用必须清理。

## 5. 代码质量与注释
- **类型提示 (Type Hints)**：所有函数参数与返回值必须添加类型注解。
- **文档字符串 (Docstrings)**：核心类与函数需编写 Docstring，说明功能、参数与返回值。
- **异常处理**：避免裸露的 `try...except`，应捕获特定异常并记录日志。

## 6. 路径处理
- 严禁使用硬编码的绝对路径（如 `C:\Users\...`）。
- 必须使用 `pathlib` 模块处理路径，基于项目根目录 (`PROJECT_ROOT`) 进行相对定位。
