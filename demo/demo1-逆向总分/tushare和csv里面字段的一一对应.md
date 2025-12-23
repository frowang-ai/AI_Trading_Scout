这是一个非常棒的 Tushare 文档集合。基于你提供的 CSV 列名和你刚刚发给我的 Tushare 文档，我为你整理了一份详细的**映射与计算指南**。

核心逻辑是：
1.  **基础行情与估值**：直接通过 `daily` 和 `daily_basic` 获取。
2.  **常用技术指标**：Tushare 的 `stk_factor` (基础) 和 `stk_factor_pro` (专业) 接口非常强大，直接覆盖了你 CSV 中 80% 的指标（如 MACD, KDJ, RSI, CCI, OBV, DMI）。
3.  **衍生/统计指标**：如 `jump` (跳空), `consec` (连天数), `lon` (钱龙), `beta`，需要基于 Tushare 的基础数据在本地用 Python (`pandas` / `talib`) 计算。

---

### 1. 基础行情与量价 (Basic Price & Volume)

**数据源接口**：`daily` (日线行情), `daily_basic` (每日指标)

| CSV 列名 | 匹配类型 | Tushare 接口 | Tushare 字段 | 说明/计算方式 |
| :--- | :--- | :--- | :--- | :--- |
| **close** | 直接获取 | `daily` | `close` | 收盘价 |
| **开盘** | 直接获取 | `daily` | `open` | 开盘价 |
| **最高** | 直接获取 | `daily` | `high` | 最高价 |
| **最低** | 直接获取 | `daily` | `low` | 最低价 |
| **涨跌幅** | 直接获取 | `daily` | `pct_chg` | 涨跌幅 (%) |
| **成交量** | 直接获取 | `daily` | `vol` | 成交量（手） |
| **换手率%** | 直接获取 | `daily_basic` | `turnover_rate` | 换手率 |
| **平均量比_50天** | 近似获取 | `daily_basic` | `volume_ratio` | Tushare 提供的是当日量比。如果要50天平均，需拉取历史 `vol` 自己算 mean。 |
| **总市值(亿)** | 直接获取 | `daily_basic` | `total_mv` | 单位是万元，需除以 10000 |
| **jump** | **需计算** | `daily` | - | **计算逻辑**：`(open - pre_close) / pre_close`。Tushare `daily` 提供了 `open` 和 `pre_close`。 |

---

### 2. 核心技术指标 (Core Technical Indicators)

Tushare 有两个强大的接口直接算出这些值，无需你自己写公式。
**数据源接口**：`stk_factor` (常用), `stk_factor_pro` (专业，含更多指标)

#### MACD 家族
| CSV 列名 | Tushare 接口 | Tushare 字段 | 说明 |
| :--- | :--- | :--- | :--- |
| **dif** | `stk_factor` | `macd_dif` | 快线与慢线的差值 |
| **dem** | `stk_factor` | `macd_dea` | 也就是 DEA，信号线 |
| **histgram** | `stk_factor` | `macd` | Tushare 的 `macd` 字段即为柱状图 (MACD Bar) |
| **macd_signal** | **需计算** | - | **逻辑**：判断金叉死叉。`df['dif'] > df['dem']` |

#### KDJ 家族
| CSV 列名 | Tushare 接口 | Tushare 字段 | 说明 |
| :--- | :--- | :--- | :--- |
| **k_kdj** | `stk_factor` | `kdj_k` | K值 |
| **slowk** | `stk_factor` | `kdj_k` | 通常 KDJ 的 K 线就是 Slow K |
| **slowkdj_signal** | **需计算** | - | **逻辑**：`kdj_k` 上穿 `kdj_d` |

#### RSI 家族
| CSV 列名 | Tushare 接口 | Tushare 字段 | 说明 |
| :--- | :--- | :--- | :--- |
| **rsi** | `stk_factor` | `rsi_6`, `rsi_12`, `rsi_24` | Tushare 提供三个周期的 RSI，根据你 CSV 的参数选择（通常是 6 或 12） |

#### BOLL (布林带) 家族
| CSV 列名 | Tushare 接口 | Tushare 字段 | 说明 |
| :--- | :--- | :--- | :--- |
| **bands_upper** | `stk_factor` | `boll_upper` | 上轨 |
| **bands_middle** | `stk_factor` | `boll_mid` | 中轨 (通常是 MA20) |
| **bands_lower** | `stk_factor` | `boll_lower` | 下轨 |

#### CCI (顺势指标)
| CSV 列名 | Tushare 接口 | Tushare 字段 | 说明 |
| :--- | :--- | :--- | :--- |
| **cci_90** | `stk_factor` | `cci` | Tushare 给具体数值。你需要写逻辑判断 `cci > 90` |
| **cci_-90** | `stk_factor` | `cci` | 同上，判断 `cci < -90` |

---

### 3. 高级/特色技术指标 (Advanced Indicators)

这部分指标主要在 `stk_factor_pro` 中，或者需要自行计算。

| CSV 列名 | 状态 | Tushare 接口 | 对应字段 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| **DMI (pdi, ndi, adx)** | **完美匹配** | `stk_factor_pro` | `dmi_pdi_qfq`, `dmi_mdi_qfq`, `dmi_adx_qfq` | Tushare 甚至贴心地提供了复权(qfq)版本 |
| **OBV** | **完美匹配** | `stk_factor_pro` | `obv_qfq` | 能量潮 |
| **DMA** | **近似匹配** | `stk_factor_pro` | `dfma_dif_qfq` | 这里的 `dfma` (平行线差) 逻辑与 DMA (平均线差) 类似。或者用 `daily` 的均线自己减：`MA10 - MA50` |
| **LON (钱龙)** | **无直接** | - | - | **需计算**：LON 是中国特色的指标，Tushare 没有直接提供。你需要拉取 `daily` 数据，用 Python 实现公式（类似于加权 MACD）。 |

---

### 4. 统计与风险指标 (Statistics & Risk)

这部分通常需要结合大盘指数来计算。

| CSV 列名 | 计算方法 (Python) | 所需 Tushare 数据 |
| :--- | :--- | :--- |
| **波动率 (Volatility)** | `df['pct_chg'].rolling(N).std()` | `daily` (个股涨跌幅) |
| **BETA** | `Cov(Stock, Index) / Var(Index)` | `daily` (个股) + `index_daily` (比如沪深300 `399300.SZ`) |
| **相关性 (Correlation)** | `df['pct_chg'].rolling(N).corr(index_ret)` | 同上 |

---

### 5. 所有的 `_consec`, `_signal` 如何计算？

Tushare 只提供**当天的数值**（例如 RSI=85），不提供**状态特征**（例如 RSI 连续 3 天大于 80）。这是量化最核心的特征工程部分，需要在本地代码中实现。

假设你已经通过 `pro.stk_factor(ts_code='000001.SZ')` 拿到了 DataFrame `df`：

#### 场景 A: 计算 `_consec` (连续满足条件的天数)
比如计算 **RSI 连续大于 80 的天数** (`rsi_consec`)：

```python
# 1. 定义条件
condition = df['rsi_6'] > 80

# 2. 计算连续天数 (Pandas 魔法)
# 分组：每次状态变化(True变False或反之)就生成一个新组ID
groups = (condition != condition.shift()).cumsum()
# 计数：计算当前组到现在为止的数量
df['rsi_consec'] = df.groupby(groups).cumcount() + 1

# 3. 如果当前不满足条件，这就不是连续满足，置为0 (可选)
df.loc[~condition, 'rsi_consec'] = 0
```

#### 场景 B: 计算 `_signal` (金叉/死叉)
比如计算 **MACD 金叉** (`macd_signal`)：

```python
# 1. 获取 DIF 和 DEA
dif = df['macd_dif']
dea = df['macd_dea']

# 2. 定义金叉：今天 DIF > DEA 且 昨天 DIF < DEA
golden_cross = (dif > dea) & (dif.shift(1) < dea.shift(1))

# 3. 赋值
df['macd_signal'] = golden_cross.astype(int) # 1代表金叉，0代表无
```

#### 场景 C: 计算 `_0` 或 `_90` (上穿阈值)
比如计算 **CCI 上穿 90** (`cci_90`)：

```python
# 今天 CCI > 90 且 昨天 CCI <= 90
df['cci_90'] = ((df['cci'] > 90) & (df['cci'].shift(1) <= 90)).astype(int)
```

### 总结行动建议

1.  **数据入库**：
    *   使用 `daily` 拉取全量行情。
    *   使用 `stk_factor` 拉取基础指标 (MACD, KDJ, RSI, BOLL, CCI)。
    *   使用 `stk_factor_pro` 拉取进阶指标 (DMI, OBV)。
    *   使用 `daily_basic` 拉取市值、换手率。
2.  **本地计算**：
    *   在你的 `cal_factors` 模块中，编写 Python 函数处理 `LON` (钱龙指标) 和 `Beta`。
    *   编写通用的 `get_consecutive_days(series, threshold)` 函数来批量生成所有的 `_consec` 列。
    *   编写通用的 `get_crossover_signal(series1, series2)` 函数来生成所有的 `_signal` 列。