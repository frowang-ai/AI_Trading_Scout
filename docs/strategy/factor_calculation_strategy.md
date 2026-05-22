# 因子计算模块详细设计与性能优化策略

## 1. 核心设计理念

在构建因子计算模块 (`cal_factors`) 时，我们面临着**逻辑准确性**与**计算性能**的双重挑战。针对全市场（5000+ 股票）跨越长周期（20年+）的海量数据处理需求，本平台采取**“逻辑先行，多轨演进，AI 驱动优化”**的策略。

### 1.1 两大核心目标
1.  **逻辑清晰与正确 (Logic Clarity & Correctness)**：
    *   这是首要任务。代码必须易于阅读、易于调试，能够清晰地表达金融逻辑。
    *   作为系统的“真值标准 (Ground Truth)”，用于验证后续优化版本的正确性。
2.  **极致速度 (High Performance)**：
    *   在逻辑验证无误后，针对大规模回测和生产环境进行性能优化。
    *   目标是能够在秒级/分钟级完成全市场长周期因子的计算。

## 2. 多框架演进架构 (Multi-Framework Architecture)

为了兼顾开发效率与运行效率，我们不局限于单一的计算库，而是设计一套支持多后端的计算架构。利用 **Coding Agent** 强大的代码理解与重构能力，我们可以低成本地维护多套实现。

### 2.1 版本规划

#### **v1: 基准实现版 (Baseline Implementation)**
*   **技术栈**：`Pandas` + `NumPy` + 基础python库
*   **定位**：逻辑验证、快速原型开发、标准对照组。
*   **优势**：
    *   生态最成熟，文档最丰富。
    *   向量化操作逻辑直观，符合大多数量化工程师的直觉。
*   **适用场景**：单只股票分析、小规模验证、复杂逻辑的初步实现。

#### **v2: 高性能进化版 (High-Performance Implementation)**
*   **技术栈**：`Polars` (优先) / `Numba`
*   **定位**：大规模数据清洗、全市场因子计算、生产环境。
*   **优势**：
    *   **Polars**：基于 Rust 开发，原生支持多线程并行计算，内存管理极其高效，支持 Lazy Evaluation（惰性求值）。
    *   **Numba**：针对特定复杂循环逻辑进行 JIT 编译加速。
*   **适用场景**：全市场 20 年数据跑批、高频因子计算。

### 2.2 AI 驱动的开发流程 (AI-Driven Workflow)

我们利用 Coding Agent 来弥合不同框架间的开发成本：

1.  **人类/Agent 开发 v1**：使用 Pandas/NumPy 编写逻辑最清晰的代码，确保金融逻辑无误。
2.  **建立测试基准**：基于 v1 的计算结果生成测试用例（Input -> Expected Output）。
3.  **Agent 自动重构 v2**：指令 Coding Agent 阅读 v1 代码，将其“翻译”为 Polars 版本。
4.  **一致性校验**：运行对比测试，确保 `Result(v1) == Result(v2)`（允许浮点数微小误差）。
5.  **持续迭代**：未来若出现更快的框架（如 GPU 加速库），同样由 Agent 基于 v1 逻辑进行迁移。

## 3. 模块接口设计 (Interface Design)

为了实现底层的无缝切换，因子计算模块需遵循**策略模式**，对外暴露统一的接口。

```python
# 伪代码示例：统一接口设计

class FactorCalculator:
    def __init__(self, backend='pandas'):
        self.backend = backend

    def calculate_ma(self, data, window=20):
        """
        计算移动平均线
        :param data: 输入数据 (DataFrame)
        :param window: 窗口大小
        :return: 计算结果
        """
        if self.backend == 'pandas':
            return self._calculate_ma_pandas(data, window)
        elif self.backend == 'polars':
            return self._calculate_ma_polars(data, window)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def _calculate_ma_pandas(self, df, window):
        # v1: Pandas 实现，逻辑清晰
        return df['close'].rolling(window=window).mean()

    def _calculate_ma_polars(self, df, window):
        # v2: Polars 实现，速度极快
        import polars as pl
        return df.select(pl.col('close').rolling_mean(window_size=window))
```