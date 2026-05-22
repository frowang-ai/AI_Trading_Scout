# 蓝色光标（300058.SZ）四状态日频交易系统 — 数据需求规格书

> 供 GPT 5.5 Pro 实现完整回测系统使用。所有数据通过 Tushare Pro API 获取。

---

## 一、数据总览

| # | 数据集 | API | 频率 | 时间跨度 | 用途 |
|---|--------|-----|------|----------|------|
| D1 | A股日线行情 | `daily` | 日 | 2023-01-01 ~ 今 | OHLCV 基础行情 |
| D2 | 每日指标 | `daily_basic` | 日 | 2023-01-01 ~ 今 | 换手率、量比、PE/PB、市值 |
| D3 | 个股资金流向 | `moneyflow` | 日 | 2023-01-01 ~ 今 | 大/中/小/特大单买卖 |
| D4 | 复权因子 | `adj_factor` | 日 | 2023-01-01 ~ 今 | 前复权计算 |
| D5 | 每日涨跌停价 | `stk_limit` | 日 | 2023-01-01 ~ 今 | 涨停/跌停价格 |
| D6 | 开盘集合竞价 | `stk_auction_o` | 日 | 2023-01-01 ~ 今 | 开盘价形成过程 |
| D7 | 收盘集合竞价 | `stk_auction_c` | 日 | 2023-01-01 ~ 今 | 收盘价形成过程 |
| D8 | 股票分钟行情 | `stk_mins` | 1min | 2023-01-01 ~ 今 | 日内微观结构特征 |
| D9 | 创业板指日线 | `index_daily` | 日 | 2023-01-01 ~ 今 | 大盘基准 |
| D10 | 传媒板块日线 | `sw_daily` | 日 | 2023-01-01 ~ 今 | 行业基准 |
| D11 | AI概念板块日线 | `ths_daily` | 日 | 2023-01-01 ~ 今 | 概念板块基准 |

---

## 二、各数据集详细字段

### D1: A股日线行情 (`daily`)

**调用方式：**
```python
pro.daily(ts_code="300058.SZ", start_date="20230101", end_date="20260512")
```

**输出字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `ts_code` | str | 股票代码 300058.SZ |
| `trade_date` | str | 交易日期 YYYYMMDD |
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `close` | float | 收盘价 |
| `pre_close` | float | 昨收价 |
| `change` | float | 涨跌额 |
| `pct_chg` | float | 涨跌幅 % |
| `vol` | float | 成交量（手） |
| `amount` | float | 成交额（千元） |

**注意事项：**
- `amount` 单位是**千元**，需换算：`amount_wan = amount / 10`（万元），`amount_yi = amount / 10000`（亿元）
- `vol` 单位是**手**（1手 = 100股）
- 这是**未复权**数据，做回测时需结合 D4 复权因子

---

### D2: 每日指标 (`daily_basic`)

**调用方式：**
```python
pro.daily_basic(
    ts_code="300058.SZ",
    start_date="20230101",
    end_date="20260512",
    fields="ts_code,trade_date,turnover_rate,turnover_rate_f,volume_ratio,pe,pe_ttm,pb,total_mv,circ_mv,float_share,free_share"
)
```

**输出字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `turnover_rate` | float | 换手率%（基于流通股本） |
| `turnover_rate_f` | float | 换手率%（基于自由流通股本） |
| `volume_ratio` | float | 量比（今日均速 / 过去5日均速） |
| `pe` | float | 市盈率（日） |
| `pe_ttm` | float | 市盈率TTM |
| `pb` | float | 市净率 |
| `total_mv` | float | 总市值（万元） |
| `circ_mv` | float | 流通市值（万元） |
| `float_share` | float | 流通股本（万股） |
| `free_share` | float | 自由流通股本（万股） |

**关键说明：**
- `turnover_rate` 和 `turnover_rate_f` **不要同时使用**，选一个即可。推荐用 `turnover_rate_f`（自由流通换手率更准确）
- `volume_ratio` > 1 表示放量，< 1 表示缩量

---

### D3: 个股资金流向 (`moneyflow`)

**调用方式：**
```python
pro.moneyflow(ts_code="300058.SZ", start_date="20230101", end_date="20260512")
```

**输出字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `buy_sm_vol` | float | 小单买入量（手） |
| `buy_sm_amount` | float | 小单买入额（万元） |
| `sell_sm_vol` | float | 小单卖出量（手） |
| `sell_sm_amount` | float | 小单卖出额（万元） |
| `buy_md_vol` | float | 中单买入量（手） |
| `buy_md_amount` | float | 中单买入额（万元） |
| `sell_md_vol` | float | 中单卖出量（手） |
| `sell_md_amount` | float | 中单卖出额（万元） |
| `buy_lg_vol` | float | 大单买入量（手） |
| `buy_lg_amount` | float | 大单买入额（万元） |
| `sell_lg_vol` | float | 大单卖出量（手） |
| `sell_lg_amount` | float | 大单卖出额（万元） |
| `buy_elg_vol` | float | 特大单买入量（手） |
| `buy_elg_amount` | float | 特大单买入额（万元） |
| `sell_elg_vol` | float | 特大单卖出量（手） |
| `sell_elg_amount` | float | 特大单卖出额（万元） |
| `net_mf_vol` | float | 净流入量（手） |
| `net_mf_amount` | float | 净流入额（万元） |

**派生指标定义（系统核心）：**
```python
# 主力 = 大单 + 特大单
main_buy_amount  = buy_lg_amount + buy_elg_amount    # 万元
main_sell_amount = sell_lg_amount + sell_elg_amount   # 万元
main_net_amount  = main_buy_amount - main_sell_amount # 万元（正=净买入）

# 散户 = 小单
retail_net_amount = buy_sm_amount - sell_sm_amount     # 万元

# 订单流不平衡 OFI = 主力净流入 / 总成交额
ofi = main_net_amount / amount_wan                     # [-1, +1]

# 主力参与度 = 主力总成交 / 全市场总成交
main_participation = (main_buy_amount + main_sell_amount) / amount_wan
```

**冗余警告：**
- `ofi` ≈ `main_net_amount / amount_wan`，不要同时用 `ofi` 和 `main_net_amount/amount_wan`
- `net_mf_amount` = 全部净流入（含散户），与 `main_net_amount` 不同
- 优先使用 `main_net_amount` 和 `ofi`，而非 `net_mf_amount`

---

### D4: 复权因子 (`adj_factor`)

**调用方式：**
```python
pro.adj_factor(ts_code="300058.SZ", start_date="20230101", end_date="20260512")
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `ts_code` | str | 股票代码 |
| `trade_date` | str | 交易日期 |
| `adj_factor` | float | 复权因子 |

**前复权计算：**
```python
# 前复权价 = 原始价 × (最新复权因子 / 当日复权因子)
latest_adj = df['adj_factor'].iloc[-1]
df['close_adj'] = df['close'] * (latest_adj / df['adj_factor'])
```

---

### D5: 每日涨跌停价格 (`stk_limit`)

**调用方式：**
```python
pro.stk_limit(ts_code="300058.SZ", start_date="20230101", end_date="20260512")
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `trade_date` | str | 交易日期 |
| `ts_code` | str | 股票代码 |
| `pre_close` | float | 昨收价 |
| `up_limit` | float | 涨停价 |
| `down_limit` | float | 跌停价 |

**用途：**
- 判断当日是否涨停/跌停：`close >= up_limit * 0.995` 视为涨停
- 标记涨停板日，涨停板日次日往往高开（风险标记）
- 创业板涨跌幅 20%，蓝色光标属于创业板

---

### D6: 开盘集合竞价 (`stk_auction_o`)

**调用方式：**
```python
pro.stk_auction_o(ts_code="300058.SZ", start_date="20230101", end_date="20260512")
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `ts_code` | str | 股票代码 |
| `trade_date` | str | 交易日期 |
| `close` | float | 竞价撮合价（即开盘价） |
| `open` | float | 竞价起始价 |
| `high` | float | 竞价期间最高价 |
| `low` | float | 竞价期间最低价 |
| `vol` | float | 竞价成交量（手） |
| `amount` | float | 竞价成交额 |
| `vwap` | float | 竞价VWAP |

**用途：**
- 竞价量 / 全天量 = 集合竞价参与度
- 竞价 VWAP vs 开盘价偏离 = 竞价阶段买卖力量
- **对蓝色光标极其重要**：高开低走的信息大量蕴含在集合竞价中

---

### D7: 收盘集合竞价 (`stk_auction_c`)

**调用方式：**
```python
pro.stk_auction_c(ts_code="300058.SZ", start_date="20230101", end_date="20260512")
```

字段同 D6，额外提供收盘竞价 VWAP。

**用途：**
- 收盘竞价 VWAP vs 收盘价偏离
- 大单尾盘偷袭 / 尾盘砸盘识别

---

### D8: 股票分钟行情 (`stk_mins`)

**调用方式：**
```python
# 单次最多返回 8000 行，1min 约 33 天，需分段循环拉取
pro.stk_mins(
    ts_code="300058.SZ",
    freq="1min",
    start_date="2023-01-01 09:00:00",
    end_date="2023-02-15 20:00:00"  # 每次约30天
)
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `ts_code` | str | 股票代码 |
| `trade_time` | datetime | 分钟时间戳 |
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `close` | float | 收盘价 |
| `vol` | float | 成交量（手） |
| `amount` | float | 成交额（元） |

**分段拉取模板：**
```python
import pandas as pd
import time

all_dfs = []
segments = pd.date_range("2023-01-01", "2026-05-12", freq="30D")
for i in range(len(segments) - 1):
    start = segments[i].strftime("%Y-%m-%d 09:00:00")
    end   = segments[i+1].strftime("%Y-%m-%d 20:00:00")
    df = pro.stk_mins(ts_code="300058.SZ", freq="1min",
                      start_date=start, end_date=end)
    if df is not None and not df.empty:
        all_dfs.append(df)
    time.sleep(0.4)  # 限流

mins = pd.concat(all_dfs, ignore_index=True)
```

**限额说明：**
- 每日限额 2 次（基础积分），每次最多 8000 行
- 3 年 1min 数据 ≈ 34 次调用 → 17 天
- **替代方案**：使用 5min 频率，3 年仅需约 7 次调用，3-4 天完成

**从分钟数据提取的关键特征：**
```python
# 按 trade_date 分组后计算
first_5m_ret        = 前5分钟收益率（开→第5根close）
first_15m_ret       = 前15分钟收益率
first_15m_vwap_dev  = 前15分钟收盘价 vs 前15分钟VWAP偏离%
morning_fade        = 10:30收盘 / 09:30-10:30最高 - 1（冲高回落程度）
vol_30m_ratio       = 09:30-10:00成交量 / 全天成交量（早盘参与度）
pm_reclaim          = 收盘价 / 14:30收盘价 - 1（午后回补力度）
```

**A股分钟线规则：**
- 上午 09:30 - 11:30（120根）
- 下午 13:00 - 15:00（120根）
- 全天共 240 根 1min K线
- 分钟序号 0-119 = 上午，120-239 = 下午

---

### D9: 创业板指日线 (`index_daily`)

**调用方式：**
```python
pro.index_daily(ts_code="399006.SZ", start_date="20230101", end_date="20260512")
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `ts_code` | str | 指数代码 399006.SZ |
| `trade_date` | str | 交易日期 |
| `close` | float | 收盘点位 |
| `open` | float | 开盘点位 |
| `high` | float | 最高 |
| `low` | float | 最低 |
| `pre_close` | float | 昨收 |
| `pct_chg` | float | 涨跌幅% |
| `vol` | float | 成交量 |
| `amount` | float | 成交额 |

**用途：**
- 个股收益 vs 创业板指收益 = 超额收益
- 大盘强弱过滤：创业板指连续下跌时，暂停买入信号

---

### D10: 传媒板块日线 (`sw_daily`)

**调用方式：**
```python
# 申万传媒板块代码：801760.SI
pro.sw_daily(ts_code="801760.SI", start_date="20230101", end_date="20260512")
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `ts_code` | str | 行业指数代码 |
| `trade_date` | str | 交易日期 |
| `close` | float | 收盘 |
| `open` | float | 开盘 |
| `high` | float | 最高 |
| `low` | float | 最低 |
| `pct_chg` | float | 涨跌幅% |
| `vol` | float | 成交量 |
| `pe` | float | 行业PE |
| `pb` | float | 行业PB |

---

### D11: AI概念板块日线 (`ths_daily`)

**调用方式：**
```python
# 同花顺AI概念板块代码需先查 ths_index 获取
# 常见：AIGC概念、ChatGPT概念、人工智能等
pro.ths_daily(ts_code="<查到的代码>", start_date="20230101", end_date="20260512")
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `ts_code` | str | 概念指数代码 |
| `trade_date` | str | 交易日期 |
| `close` | float | 收盘 |
| `pct_chg` | float | 涨跌幅% |
| `vol` | float | 成交量 |
| `turnover_rate` | float | 换手率 |

---

## 三、已计算的指标（可直接提供，无需重新计算）

项目已有 `_test_indicators_result.csv`，724行 × 40列，覆盖 2023-05 ~ 2026-05。

### 指标清单与分类

**Layer 1 - 成交量异常：**
| 字段 | 说明 | 公式 |
|------|------|------|
| `rvol_20` | 相对成交量 | vol / MA20(vol) |
| `vol_shock` | 量冲击 | log(vol) - log(MA20(vol)) |
| `vol_zscore` | 量z-score | (vol - MA20) / STD20 |
| `volume_ratio` | 量比 | 来自 daily_basic（今日均速/5日均速） |

**Layer 2 - 买卖压力：**
| 字段 | 说明 | 公式 |
|------|------|------|
| `main_net_amount` | 主力净流入(万元) | (大单+特大单)买 - (大单+特大单)卖 |
| `ofi` | 订单流不平衡 | main_net_amount / amount_wan |
| `main_participation` | 主力参与度 | 主力总成交 / 总成交额 |
| `net_mf_amount` | 全口径净流入(万元) | 来自 moneyflow 原始字段 |
| `retail_net_amount` | 散户净流入(万元) | 小单买 - 小单卖 |

**Layer 3 - 价格冲击：**
| 字段 | 说明 | 公式 |
|------|------|------|
| `ret_pct` | 日收益率% | = pct_chg |
| `price_impact` | 价格冲击 | |ret_pct| / amount_yi（%/亿元） |
| `price_impact_20ma` | 冲击20日均值 | MA20(price_impact) |

**Layer 4 - 量价组合：**
| 字段 | 说明 | 公式 |
|------|------|------|
| `open_ret_pct` | 开盘跳空% | (open/pre_close - 1) × 100 |
| `intraday_ret_pct` | 日内收益% | (close/open - 1) × 100 |
| `amplitude_pct` | 振幅% | (high - low) / pre_close × 100 |
| `close_position` | 收盘位置 | (close - low) / (high - low)，0=最低 1=最高 |
| `vol_x_intraday` | 量价交互 | vol_shock × intraday_ret_pct |

**Layer 5 - VWAP：**
| 字段 | 说明 | 公式 |
|------|------|------|
| `vwap` | 日VWAP(元) | amount × 10 / vol |
| `close_vs_vwap_pct` | 收盘vs VWAP偏离% | (close - vwap) / vwap × 100 |

**Layer 6 - 流动性：**
| 字段 | 说明 | 公式 |
|------|------|------|
| `turnover_rate` | 换手率%(流通) | 来自 daily_basic |
| `turnover_rate_f` | 换手率%(自由流通) | 来自 daily_basic |
| `realized_vol_20d` | 20日已实现波动率(年化) | STD20(pct_chg) × √252 |
| `amount_yi_20ma` | 20日成交额均值(亿) | MA20(amount_yi) |

**Layer 7 - 综合信号（布尔标签）：**
| 字段 | 说明 | 条件 |
|------|------|------|
| `sig_high_vol` | 异常放量 | rvol_20 > 2.0 |
| `sig_high_open_low_close` | 高开低走放量 | open_ret>1% & intraday<-1% & close<vwap & rvol>1.5 |
| `sig_healthy_pullback` | 缩量健康回调 | -2%<ret<0 & rvol<0.8 & close_position>0.4 |
| `sig_strong_up` | 放量强势上涨 | ret>0 & rvol>1.5 & close>vwap & close_position>0.6 |
| `sig_main_outflow` | 主力净流出 | main_net_amount < 0 |

### 冗余字段剔除建议

以下字段存在信息重复，建模时**只选其一**：

| 保留 | 剔除 | 原因 |
|------|------|------|
| `turnover_rate_f` | `turnover_rate` | 自由流通换手更准确 |
| `ofi` | `main_net_amount / amount_wan` | 完全等价 |
| `amount_yi` | `amount_wan`, `amount` | 仅单位不同 |
| `rvol_20` | `vol_shock`, `vol_zscore` | 三者高度相关，rvol最直观 |
| `ret_pct` | `pct_chg` | 完全相同 |
| 原始信号层特征 | `sig_*` 标签 | sig_* 是派生标签，不应直接做模型输入 |

---

## 四、还需额外计算的日内特征（从 D8 分钟数据提取）

以下是系统必需但当前**尚未落地**的特征，必须从 `stk_mins` 分钟数据计算：

```python
# ==============================
# 每日日内微观结构特征（从1分钟K线计算）
# ==============================

# 1. 早盘收益特征
first_5m_ret       = day.iloc[4]['close']  / day.iloc[0]['open'] - 1   # 前5分钟收益
first_15m_ret      = day.iloc[14]['close'] / day.iloc[0]['open'] - 1   # 前15分钟收益

# 2. 早盘VWAP偏离
first_15m_amount   = day.iloc[:15]['amount'].sum()    # 前15分钟总成交额（元）
first_15m_vol      = day.iloc[:15]['vol'].sum()        # 前15分钟总成交量（手）
first_15m_vwap     = first_15m_amount / (first_15m_vol * 100)  # 元/股
first_15m_vwap_dev = (day.iloc[14]['close'] / first_15m_vwap - 1) * 100  # %

# 3. 冲高回落（早盘最关键指标）
morning_high       = day.iloc[:30]['high'].max()       # 09:30-10:00 最高价
price_at_1030      = day.iloc[120]['close']             # 10:30 收盘价（第120根=10:30）
morning_fade       = price_at_1030 / morning_high - 1   # 负值=冲高回落

# 4. 早盘参与度
vol_first_30m      = day.iloc[:30]['vol'].sum()         # 前30分钟成交量
vol_30m_ratio      = vol_first_30m / day['vol'].sum()   # 占全天比例

# 5. 午后回补
price_at_1430      = day.iloc[180]['close']              # 14:30 收盘价
pm_reclaim         = day.iloc[-1]['close'] / price_at_1430 - 1  # 正=午后走强

# 6. 日内速度不对称（已有代码 _test_intraday_asymmetry.py）
peak_frac          = 最高价出现的分钟序号 / 240           # 0=开盘 1=收盘
speed_ratio        = 上涨速度 / 下跌速度                  # >1=快涨慢跌
path_corr          = 日内收益率序列 lag-1 自相关           # 负=冲高回落
```

---

## 五、数据格式统一规范

### 1. 日期字段
- Tushare 原始格式：`YYYYMMDD`（str，如 "20230417"）
- 分钟数据时间格式：`YYYY-MM-DD HH:MM:SS`（datetime）
- **统一建议**：日线数据保留 `YYYYMMDD`，分钟数据保留原始 datetime

### 2. 价格单位
- 所有价格（open/high/low/close/pre_close/vwap/up_limit/down_limit）：**元/股**
- 成交量（vol）：**手**（1手 = 100股）
- 成交额（amount）：日线为**千元**，分钟线为**元**，资金流向为**万元**

### 3. 缺失值处理
- 停牌日：Tushare 不返回数据，需用交易日历补齐后 fillna
- 涨跌停价缺失：非创业板个股有时无数据，300058 属创业板应有完整数据
- 分钟数据缺失：半天交易（如节假日前后）可能不足 240 根

### 4. 交易日历
```python
# 获取交易日历
cal = pro.trade_cal(exchange='SSE', start_date='20230101', end_date='20260512')
trade_dates = cal[cal['is_open'] == 1]['cal_date'].tolist()
```

---

## 六、数据获取脚本模板

### 完整拉取脚本（一次性获取全部日线数据）

```python
import tushare as ts
import pandas as pd
import time

TOKEN = "你的Tushare Token"
pro = ts.pro_api(TOKEN)
TS_CODE = "300058.SZ"
START = "20230101"
END = "20260512"

# D1: 日线
daily = pro.daily(ts_code=TS_CODE, start_date=START, end_date=END)
time.sleep(0.4)

# D2: 每日指标
basic = pro.daily_basic(
    ts_code=TS_CODE, start_date=START, end_date=END,
    fields="ts_code,trade_date,turnover_rate,turnover_rate_f,volume_ratio,pe,pe_ttm,pb,total_mv,circ_mv,float_share,free_share"
)
time.sleep(0.4)

# D3: 资金流向
moneyflow = pro.moneyflow(ts_code=TS_CODE, start_date=START, end_date=END)
time.sleep(0.4)

# D4: 复权因子
adj = pro.adj_factor(ts_code=TS_CODE, start_date=START, end_date=END)
time.sleep(0.4)

# D5: 涨跌停价
limit = pro.stk_limit(ts_code=TS_CODE, start_date=START, end_date=END)
time.sleep(0.4)

# D6: 开盘集合竞价
auction_o = pro.stk_auction_o(ts_code=TS_CODE, start_date=START, end_date=END)
time.sleep(0.4)

# D7: 收盘集合竞价
auction_c = pro.stk_auction_c(ts_code=TS_CODE, start_date=START, end_date=END)
time.sleep(0.4)

# D9: 创业板指
index_cyb = pro.index_daily(ts_code="399006.SZ", start_date=START, end_date=END)
time.sleep(0.4)

# D10: 传媒板块
sector_media = pro.sw_daily(ts_code="801760.SI", start_date=START, end_date=END)

# 合并保存
daily = daily.sort_values("trade_date").reset_index(drop=True)
daily.to_csv("300058_daily.csv", index=False)
basic.to_csv("300058_daily_basic.csv", index=False)
moneyflow.to_csv("300058_moneyflow.csv", index=False)
adj.to_csv("300058_adj_factor.csv", index=False)
limit.to_csv("300058_stk_limit.csv", index=False)
auction_o.to_csv("300058_auction_open.csv", index=False)
auction_c.to_csv("300058_auction_close.csv", index=False)
index_cyb.to_csv("index_399006_cyb.csv", index=False)
sector_media.to_csv("sw_801760_media.csv", index=False)
```

### 分钟数据分段拉取脚本

```python
import tushare as ts
import pandas as pd
import time

TOKEN = "你的Tushare Token"
pro = ts.pro_api(TOKEN)
TS_CODE = "300058.SZ"

all_dfs = []
segments = pd.date_range("2023-01-01", "2026-05-12", freq="30D")

for i in range(len(segments) - 1):
    start = segments[i].strftime("%Y-%m-%d 09:00:00")
    end   = segments[i+1].strftime("%Y-%m-%d 20:00:00")
    print(f"拉取 {start[:10]} ~ {end[:10]} ...")
    try:
        df = pro.stk_mins(ts_code=TS_CODE, freq="1min",
                          start_date=start, end_date=end)
        if df is not None and not df.empty:
            all_dfs.append(df)
            print(f"  → {len(df)} 行")
    except Exception as e:
        print(f"  ✗ 失败: {e}")
    time.sleep(0.4)

mins = pd.concat(all_dfs, ignore_index=True)
mins = mins.sort_values("trade_time").reset_index(drop=True)
mins.to_csv("300058_mins_1min.csv", index=False)
print(f"分钟数据总计: {len(mins)} 行")
```

**限额提醒：**
- `stk_mins` 每日限额 2 次（基础积分），3 年 1min 数据需约 34 次调用
- 建议先拉最近 3 个月（2 次）验证，确认格式无误后再全量拉取
- 如时间紧迫，可改用 5min 频率，数据量减少 80%

---

## 七、数据验证检查清单

提供给 GPT 5.5 Pro 之前，建议做以下验证：

```python
# 1. 日期对齐：所有日线数据的 trade_date 应完全一致
assert set(daily['trade_date']) == set(basic['trade_date'])
assert set(daily['trade_date']) == set(moneyflow['trade_date'])

# 2. 价格合理性
assert (daily['close'] > 0).all()
assert (daily['high'] >= daily['low']).all()
assert (daily['high'] >= daily['open']).all()

# 3. 成交量与换手率一致性
# turnover_rate ≈ vol × 100 / float_share × 10000 × 100
# 允许 1% 误差

# 4. 资金流向平衡
# buy_sm + buy_md + buy_lg + buy_elg ≈ sell_sm + sell_md + sell_lg + sell_elg + net_mf
# 总买 ≈ 总卖 + 净流入（允许小误差）

# 5. 分钟数据完整性
for date in trade_dates:
    day_mins = mins[mins['trade_time'].dt.strftime('%Y%m%d') == date]
    assert len(day_mins) >= 120, f"{date} 只有 {len(day_mins)} 根分钟线"
```

---

## 八、给 GPT 5.5 Pro 的推荐交付格式

**方式一：CSV 文件包**（推荐，最通用）

```
data/
├── 300058_daily.csv          # D1 日线行情
├── 300058_daily_basic.csv    # D2 每日指标
├── 300058_moneyflow.csv      # D3 资金流向
├── 300058_adj_factor.csv     # D4 复权因子
├── 300058_stk_limit.csv      # D5 涨跌停价
├── 300058_auction_open.csv   # D6 开盘竞价
├── 300058_auction_close.csv  # D7 收盘竞价
├── 300058_mins_1min.csv      # D8 1分钟K线（可能很大，考虑parquet）
├── 300058_indicators.csv     # 已算好的40列指标
├── index_399006_cyb.csv      # D9 创业板指
├── sw_801760_media.csv       # D10 传媒板块
└── ths_ai_concept.csv        # D11 AI概念板块
```

**方式二：合并宽表**（更方便，推荐用于建模）

将 D1-D7, D9-D11 按 `trade_date` inner join 成一张日线宽表，D8 分钟数据单独文件：

```
data/
├── 300058_daily_wide.csv     # 日线宽表（~30列原始 + 40列指标）
├── 300058_mins_1min.csv      # 分钟K线（单独文件）
└── DATA_SPEC.md              # 本文档
```

---

## 九、权限与限额速查

| API | 积分要求 | 每日限额 | 备注 |
|-----|----------|----------|------|
| `daily` | 0 | 无特别限制 | 免费 |
| `daily_basic` | 2000 | 有流控 | 基础积分即可 |
| `moneyflow` | 2000 | 单次≤6000行 | 基础积分即可 |
| `adj_factor` | 2000 | 有流控 | 基础积分即可 |
| `stk_limit` | 2000 | 单次≤5800行 | 基础积分即可 |
| `stk_auction_o` | 需开通分钟权限 | 单次≤10000行 | 需单独申请 |
| `stk_auction_c` | 需开通分钟权限 | 单次≤10000行 | 需单独申请 |
| `stk_mins` | 需单独申请 | 每日2次(基础) | **关键瓶颈** |
| `index_daily` | 2000 | 有流控 | 基础积分即可 |
| `sw_daily` | 5000 | 有流控 | 需较高积分 |
| `ths_daily` | 6000 | 有流控 | 需较高积分 |

**关键限制：`stk_mins` 分钟数据是整个系统的瓶颈。**
- 基础积分：2次/天，3年1min数据需17天
- 如已开高级权限：可大幅加速
- 替代方案：5min 频率仅需 3-4 天

---

## 十、不需要提供的数据（明确排除）

| 数据 | 排除原因 |
|------|----------|
| Tick 逐笔数据 | Tushare 的 `realtime_tick` 是爬虫版，不稳定且无历史；无官方逐笔API |
| 盘口数据（bid/ask） | Tushare 不提供历史盘口 |
| 融资融券数据 | 当前系统不做融券，后续再加 |
| 龙虎榜数据 | 事件驱动，不适合日频系统 |
| 期权/期货数据 | 当前系统仅做A股现货 |

**关于 Tick 的说明：**
Tushare 没有可靠的逐笔历史数据接口。对于"前15分钟主动买卖强度"的需求，可以用分钟线的 `close vs (high+low)/2` 来近似：
```python
# 近似主动买卖方向
tick_direction = np.where(
    bar['close'] > (bar['high'] + bar['low']) / 2, 1,  # 收在上半=买方主导
    np.where(bar['close'] < (bar['high'] + bar['low']) / 2, -1, 0)  # 收在下半=卖方主导
)
signed_amount_15m = (tick_direction[:15] * bar['amount'][:15]).sum()
```
