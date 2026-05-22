# 股票曾用名

**路径**: 股票数据/基础数据
**接口**: `namechange`
**描述**: 历史名称变更记录

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码 |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | TS代码 |
| name | str | 证券名称 |
| start_date | str | 开始日期 |
| end_date | str | 结束日期 |
| ann_date | str | 公告日期 |
| change_reason | str | 变更原因 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.namechange(ts_code='600848.SH', fields='ts_code,name,start_date,end_date,change_reason')
```
# 分红送股

**路径**: 股票数据/财务数据
**接口**: `dividend`
**积分**: 2000
**描述**: 分红送股数据权限：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码 |
| ann_date | str | N | 公告日 |
| record_date | str | N | 股权登记日期 |
| ex_date | str | N | 除权除息日 |
| imp_ann_date | str | N | 实施公告日 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| end_date | str | Y | 分红年度 |
| ann_date | str | Y | 预案公告日 |
| div_proc | str | Y | 实施进度 |
| stk_div | float | Y | 每股送转 |
| stk_bo_rate | float | Y | 每股送股比例 |
| stk_co_rate | float | Y | 每股转增比例 |
| cash_div | float | Y | 每股分红（税后） |
| cash_div_tax | float | Y | 每股分红（税前） |
| record_date | str | Y | 股权登记日 |
| ex_date | str | Y | 除权除息日 |
| pay_date | str | Y | 派息日 |
| div_listdate | str | Y | 红股上市日 |
| imp_ann_date | str | Y | 实施公告日 |
| base_date | str | N | 基准日 |
| base_share | float | N | 基准股本（万） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.dividend(ts_code='600848.SH', fields='ts_code,div_proc,stk_div,record_date,ex_date')
```
# 龙虎榜每日明细

**路径**: 股票数据/打板专题数据
**接口**: `top_list`
**积分**: 2000
**描述**: 龙虎榜每日交易明细数据历史： 2005年至今限量：单次请求返回最大10000行数据，可通过参数循环获取全部历史积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次请求返回最大10000行数据，可通过参数循环获取全部历史积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | N | 股票代码 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | TS代码 |
| name | str | Y | 名称 |
| close | float | Y | 收盘价 |
| pct_change | float | Y | 涨跌幅 |
| turnover_rate | float | Y | 换手率 |
| amount | float | Y | 总成交额 |
| l_sell | float | Y | 龙虎榜卖出额 |
| l_buy | float | Y | 龙虎榜买入额 |
| l_amount | float | Y | 龙虎榜成交额 |
| net_amount | float | Y | 龙虎榜净买入额 |
| net_rate | float | Y | 龙虎榜净买额占比 |
| amount_rate | float | Y | 龙虎榜成交额占比 |
| float_values | float | Y | 当日流通市值 |
| reason | str | Y | 上榜理由 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.top_list(trade_date='20180928')

或者

df = pro.query('top_list', trade_date='20180928', ts_code='002219.SZ')
```
# 龙虎榜机构明细

**路径**: 股票数据/打板专题数据
**接口**: `top_inst`
**积分**: 5000
**描述**: 龙虎榜机构成交明细限量：单次请求最大返回10000行数据，可根据参数循环获取全部历史积分：用户需要至少5000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次请求最大返回10000行数据，可根据参数循环获取全部历史积分：用户需要至少5000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | N | TS代码 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | TS代码 |
| exalter | str | Y | 营业部名称 |
| side | str | Y | 买卖类型0：买入金额最大的前5名， 1：卖出金额最大的前5名 |
| buy | float | Y | 买入额（元） |
| buy_rate | float | Y | 买入占总成交比例 |
| sell | float | Y | 卖出额（元） |
| sell_rate | float | Y | 卖出占总成交比例 |
| net_buy | float | Y | 净成交额（元） |
| reason | str | Y | 上榜理由 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.top_inst(trade_date='20210525')

或者

df = pro.query('top_inst', trade_date='20210524', ts_code='000592.SZ', fileds='trade_date,buy,sell,side,reason')
```
# 通用行情接口

**路径**: 股票数据/行情数据
**接口**: `pro_bar`
**积分**: 600
**描述**: 目前整合了股票（未复权、前复权、后复权）、指数、数字货币、ETF基金、期货、期权的行情数据，未来还将整合包括外汇在内的所有交易行情数据，同时提供分钟数据。不同数据对应不同的积分要求，具体请参阅每类数据的文档说明。其它：由于本接口是集成接口，在SDK层做了一些逻辑处理，目前暂时没法用http的方式调取通用行情接口。用户可以访问Tushare的Github，查看源代码完成类似功能。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 证券代码，不支持多值输入，多值输入获取结果会有重复记录 |
| start_date | str | N | 开始日期 (日线格式：YYYYMMDD，提取分钟数据请用2019-09-01 09:00:00这种格式) |
| end_date | str | N | 结束日期 (日线格式：YYYYMMDD) |
| asset | str | Y | 资产类别：E股票 I沪深指数 C数字货币 FT期货 FD基金 O期权 CB可转债（v1.2.39），默认E |
| adj | str | N | 复权类型(只针对股票)：None未复权 qfq前复权 hfq后复权 , 默认None，目前只支持日线复权，同时复权机制是根据设定的end_date参数动态复权，采用分红再投模式，具体请参考常见问题列表里的说明。 |
| freq | str | Y | 数据频度 ：支持分钟(min)/日(D)/周(W)/月(M)K线，其中1min表示1分钟（类推1/5/15/30/60分钟） ，默认D。对于分钟数据有600积分用户可以试用（请求2次），正式权限可以参考权限列表说明 ，使用方法请参考股票分钟使用方法。 |
| ma | list | N | 均线，支持任意合理int数值。注：均线是动态计算，要设置一定时间范围才能获得相应的均线，比如5日均线，开始和结束日期参数跨度必须要超过5日。目前只支持单一个股票提取均线，即需要输入ts_code参数。e.g: ma_5表示5日均价，ma_v_5表示5日均量 |
| factors | list | N | 股票因子（asset='E'有效）支持 tor换手率 vr量比 |
| adjfactor | str | N | 复权因子，在复权数据时，如果此参数为True，返回的数据中则带复权因子，默认为False。 该功能从1.2.33版本开始生效 |

## 调用示例

```python
#均线

df = ts.pro_bar(ts_code='000001.SZ', start_date='20180101', end_date='20181011', ma=[5, 20, 50])
```

```python
#换手率tor，量比vr

df = ts.pro_bar(ts_code='000001.SZ', start_date='20180101', end_date='20181011', factors=['tor', 'vr'])
```

```python
df = ts.pro_bar(ts_code='000001.SH', asset='I', start_date='20180101', end_date='20181011')
```
# 股权质押统计数据

**路径**: 股票数据/参考数据
**接口**: `pledge_stat`
**积分**: 1000
**描述**: 获取股票质押统计数据限量：单次最大1000积分：用户需要至少500积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大1000积分：用户需要至少500积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| end_date | str | N | 截止日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| end_date | str | Y | 截止日期 |
| pledge_count | int | Y | 质押次数 |
| unrest_pledge | float | Y | 无限售股质押数量（万） |
| rest_pledge | float | Y | 限售股份质押数量（万） |
| total_share | float | Y | 总股本 |
| pledge_ratio | float | Y | 质押比例 |

## 调用示例

```python
pro = ts.pro_api()
#或者
#pro = ts.pro_api('your token')


df = pro.pledge_stat(ts_code='000014.SZ')
```

```python
df = pro.query('pledge_stat', ts_code='000014.SZ')
```
# 股权质押明细

**路径**: 股票数据/参考数据
**接口**: `pledge_detail`
**积分**: 1000
**描述**: 获取股票质押明细数据
**限量**: 单次最大1000

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS股票代码 |
| ann_date | str | Y | 公告日期 |
| holder_name | str | Y | 股东名称 |
| pledge_amount | float | Y | 质押数量（万股） |
| start_date | str | Y | 质押开始日期 |
| end_date | str | Y | 质押结束日期 |
| is_release | str | Y | 是否已解押 |
| release_date | str | Y | 解押日期 |
| pledgor | str | Y | 质押方 |
| holding_amount | float | Y | 持股总数（万股） |
| pledged_amount | float | Y | 质押总数（万股） |
| p_total_ratio | float | Y | 本次质押占总股本比例 |
| h_total_ratio | float | Y | 持股总数占总股本比例 |
| is_buyback | str | Y | 是否回购（0否 1是） |

## 调用示例

```python
pro = ts.pro_api()
#或者
#pro = ts.pro_api('your token')


df = pro.pledge_detail(ts_code='000014.SZ')
```

```python
df = pro.query('pledge_detail', ts_code='000014.SZ')
```
# 上市公司基本信息

**路径**: 股票数据/基础数据
**接口**: `stock_company`
**积分**: 120
**描述**: 获取上市公司基础信息，单次提取4500条，可以根据交易所分批提取积分：用户需要至少120积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str |  | 股票代码 |
| exchange | str |  | 交易所代码 ，SSE上交所 SZSE深交所 BSE北交所 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| com_name | str | Y | 公司全称 |
| com_id | str | Y | 统一社会信用代码 |
| exchange | str | Y | 交易所代码 |
| chairman | str | Y | 法人代表 |
| manager | str | Y | 总经理 |
| secretary | str | Y | 董秘 |
| reg_capital | float | Y | 注册资本(万元) |
| setup_date | str | Y | 注册日期 |
| province | str | Y | 所在省份 |
| city | str | Y | 所在城市 |
| introduction | str | N | 公司介绍 |
| website | str | Y | 公司主页 |
| email | str | Y | 电子邮件 |
| office | str | N | 办公室 |
| employees | int | Y | 员工人数 |
| main_business | str | N | 主要业务及产品 |
| business_scope | str | N | 经营范围 |

## 调用示例

```python
pro = ts.pro_api()

#或者
#pro = ts.pro_api('your token')

df = pro.stock_company(exchange='SZSE', fields='ts_code,chairman,manager,secretary,reg_capital,setup_date,province')
```
# 电影月度票房

**路径**: 行业经济/TMT行业
**接口**: `bo_monthly`
**积分**: 500
**描述**: 获取电影月度票房数据数据更新：本月更新上一月数据数据历史： 数据从2008年1月1日开始，超过10年历史数据。数据权限：用户需要至少500积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | Y | 日期（每月1号，格式YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| name | str | Y | 影片名称 |
| list_date | str | Y | 上映日期 |
| avg_price | float | Y | 平均票价 |
| month_amount | float | Y | 当月票房（万） |
| list_day | int | Y | 月内天数 |
| p_pc | int | Y | 场均人次 |
| wom_index | float | Y | 口碑指数 |
| m_ratio | float | Y | 月度占比（%） |
| rank | int | Y | 排名 |

## 调用示例

```python
pro = ts.pro_api()
#或者
#pro = ts.pro_api('your token')

df = pro.bo_monthly(date='20180901')
```
# 电影周度票房

**路径**: 行业经济/TMT行业
**接口**: `bo_weekly`
**积分**: 500
**描述**: 获取周度票房数据数据更新：本周更新上一周数据数据历史： 数据从2008年第一周开始，超过10年历史数据。数据权限：用户需要至少500积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | Y | 日期（每周一日期，格式YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| name | str | Y | 影片名称 |
| avg_price | float | Y | 平均票价 |
| week_amount | float | Y | 当周票房（万） |
| total | float | Y | 累计票房（万） |
| list_day | int | Y | 上映天数 |
| p_pc | int | Y | 场均人次 |
| wom_index | float | Y | 口碑指数 |
| up_ratio | float | Y | 环比变化 （%） |
| rank | int | Y | 排名 |

## 调用示例

```python
pro = ts.pro_api()
#或者
#pro = ts.pro_api('your token')

df = pro.bo_weekly(date='20181008')
```
# 电影日度票房

**路径**: 行业经济/TMT行业
**接口**: `bo_daily`
**积分**: 500
**描述**: 获取电影日度票房数据更新：当日更新上一日数据数据历史： 数据从2018年9月开始，更多历史数据正在补充数据权限：用户需要至少500积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | Y | 日期 （格式YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| name | str | Y | 影片名称 |
| avg_price | float | Y | 平均票价 |
| day_amount | float | Y | 当日票房（万） |
| total | float | Y | 累计票房（万） |
| list_day | int | Y | 上映天数 |
| p_pc | int | Y | 场均人次 |
| wom_index | float | Y | 口碑指数 |
| up_ratio | float | Y | 环比变化 （%） |
| rank | int | Y | 排名 |

## 调用示例

```python
pro = ts.pro_api()
#或者
#pro = ts.pro_api('your token')

df = pro.bo_daily(date='20181014')
```
# 影院每日票房

**路径**: 行业经济/TMT行业
**接口**: `bo_cinema`
**积分**: 500
**描述**: 获取每日各影院的票房数据数据历史： 数据从2018年9月开始，更多历史数据正在补充数据权限：用户需要至少500积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | Y | 日期(格式:YYYYMMDD) |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| c_name | str | Y | 影院名称 |
| aud_count | int | Y | 观众人数 |
| att_ratio | float | Y | 上座率 |
| day_amount | float | Y | 当日票房 |
| day_showcount | float | Y | 当日场次 |
| avg_price | float | Y | 场均票价（元） |
| p_pc | float | Y | 场均人次 |
| rank | int | Y | 排名 |

## 调用示例

```python
pro = ts.pro_api()
#或者
#pro = ts.pro_api('your token')

df = pro.bo_cinema(date='20181014')
```
# 公募基金公司

**路径**: 公募基金
**接口**: `fund_company`
**积分**: 1500
**描述**: 获取公募基金管理人列表积分：用户需要1500积分才可以调取，一次可以提取全部数据。具体请参阅积分获取办法

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| name | str | Y | 基金公司名称 |
| shortname | str | Y | 简称 |
| short_enname | str | N | 英文缩写 |
| province | str | Y | 省份 |
| city | str | Y | 城市 |
| address | str | Y | 注册地址 |
| phone | str | Y | 电话 |
| office | str | Y | 办公地址 |
| website | str | Y | 公司网址 |
| chairman | str | Y | 法人代表 |
| manager | str | Y | 总经理 |
| reg_capital | float | Y | 注册资本 |
| setup_date | str | Y | 成立日期 |
| end_date | str | Y | 公司终止日期 |
| employees | float | Y | 员工总数 |
| main_business | str | Y | 主要产品及业务 |
| org_code | str | Y | 组织机构代码 |
| credit_code | str | Y | 统一社会信用代码 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.fund_company()
```
# 公募基金净值

**路径**: 公募基金
**接口**: `fund_nav`
**积分**: 2000
**描述**: 获取公募基金净值数据积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS基金代码 （二选一） |
| nav_date | str | N | 净值日期 （二选一） |
| market | str | N | E场内 O场外 |
| start_date | str | N | 净值开始日期 |
| end_date | str | N | 净值结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| ann_date | str | Y | 公告日期 |
| nav_date | str | Y | 净值日期 |
| unit_nav | float | Y | 单位净值 |
| accum_nav | float | Y | 累计净值 |
| accum_div | float | Y | 累计分红 |
| net_asset | float | Y | 资产净值 |
| total_netasset | float | Y | 合计资产净值 |
| adj_nav | float | Y | 复权单位净值 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.fund_nav(ts_code='165509.SZ')
```
# 公募基金分红

**路径**: 公募基金
**接口**: `fund_div`
**积分**: 400
**描述**: 获取公募基金分红数据积分：用户需要至少400积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ann_date | str | N | 公告日（以下参数四选一） |
| ex_date | str | N | 除息日 |
| pay_date | str | N | 派息日 |
| ts_code | str | N | 基金代码 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| ann_date | str | Y | 公告日期 |
| imp_anndate | str | Y | 分红实施公告日 |
| base_date | str | Y | 分配收益基准日 |
| div_proc | str | Y | 方案进度 |
| record_date | str | Y | 权益登记日 |
| ex_date | str | Y | 除息日 |
| pay_date | str | Y | 派息日 |
| earpay_date | str | Y | 收益支付日 |
| net_ex_date | str | Y | 净值除权日 |
| div_cash | float | Y | 每股派息(元) |
| base_unit | float | Y | 基准基金份额(万份) |
| ear_distr | float | Y | 可分配收益(元) |
| ear_amount | float | Y | 收益分配金额(元) |
| account_date | str | Y | 红利再投资到账日 |
| base_year | str | Y | 份额基准年度 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.fund_div(ann_date='20181018')
```
# 公募基金持仓数据

**路径**: 公募基金
**接口**: `fund_portfolio`
**积分**: 5000
**描述**: 获取公募基金持仓数据，季度更新积分：5000积分以上每分钟请求200次，8000积分以上每分钟请求500次，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 基金代码 (ts_code,ann_date,period至少输入一个参数) |
| symbol | str | N | 股票代码 |
| ann_date | str | N | 公告日期（YYYYMMDD格式） |
| period | str | N | 季度（每个季度最后一天的日期，比如20131231表示2013年年报） |
| start_date | str | N | 报告期开始日期（YYYYMMDD格式） |
| end_date | str | N | 报告期结束日期（YYYYMMDD格式） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS基金代码 |
| ann_date | str | Y | 公告日期 |
| end_date | str | Y | 截止日期 |
| symbol | str | Y | 股票代码 |
| mkv | float | Y | 持有股票市值(元) |
| amount | float | Y | 持有股票数量（股） |
| stk_mkv_ratio | float | Y | 占股票市值比 |
| stk_float_ratio | float | Y | 占流通股本比例 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.fund_portfolio(ts_code='001753.OF')
```
# IPO新股列表

**路径**: 股票数据/基础数据
**接口**: `new_share`
**积分**: 120
**描述**: 获取新股上市列表数据限量：单次最大2000条，总量不限制积分：用户需要至少120积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大2000条，总量不限制积分：用户需要至少120积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| start_date | str | N | 上网发行开始日期 |
| end_date | str | N | 上网发行结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS股票代码 |
| sub_code | str | Y | 申购代码 |
| name | str | Y | 名称 |
| ipo_date | str | Y | 上网发行日期 |
| issue_date | str | Y | 上市日期 |
| amount | float | Y | 发行总量（万股） |
| market_amount | float | Y | 上网发行总量（万股） |
| price | float | Y | 发行价格 |
| pe | float | Y | 市盈率 |
| limit_amount | float | Y | 个人申购上限（万股） |
| funds | float | Y | 募集资金（亿元） |
| ballot | float | Y | 中签率 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.new_share(start_date='20180901', end_date='20181018')
```
# 股票回购

**路径**: 股票数据/参考数据
**接口**: `repurchase`
**积分**: 600
**描述**: 获取上市公司回购股票数据积分：用户需要至少600积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ann_date | str | N | 公告日期（任意填参数，如果都不填，单次默认返回2000条） |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| ann_date | str | Y | 公告日期 |
| end_date | str | Y | 截止日期 |
| proc | str | Y | 进度 |
| exp_date | str | Y | 过期日期 |
| vol | float | Y | 回购数量 |
| amount | float | Y | 回购金额 |
| high_limit | float | Y | 回购最高价 |
| low_limit | float | Y | 回购最低价 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.repurchase(ann_date='', start_date='20180101', end_date='20180510')

#取某日
df = pro.repurchase(ann_date='20181010')
```
# ETF日线行情

**路径**: ETF专题
**接口**: `fund_daily`
**积分**: 2000
**描述**: 获取ETF行情每日收盘后成交数据，历史超过10年
**限量**: 单次最大2000行记录，可以根据ETF代码和日期循环获取历史，总量不限制

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 基金代码 |
| trade_date | str | N | 交易日期(YYYYMMDD格式，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| trade_date | str | Y | 交易日期 |
| open | float | Y | 开盘价(元) |
| high | float | Y | 最高价(元) |
| low | float | Y | 最低价(元) |
| close | float | Y | 收盘价(元) |
| pre_close | float | Y | 昨收盘价(元) |
| change | float | Y | 涨跌额(元) |
| pct_chg | float | Y | 涨跌幅(%) |
| vol | float | Y | 成交量(手) |
| amount | float | Y | 成交额(千元) |

## 调用示例

```python
pro = ts.pro_api()

#获取”沪深300ETF华夏”ETF2025年以来的行情，并通过fields参数指定输出了部分字段
df = pro.fund_daily(ts_code='510330.SH', start_date='20250101', end_date='20250618', fields='trade_date,open,high,low,close,vol,amount')
```
# 大盘指数每日指标

**路径**: 指数专题
**接口**: `index_dailybasic`
**积分**: 400
**描述**: 目前只提供上证综指，深证成指，上证50，中证500，中小板指，创业板指的每日指标数据数据来源：Tushare社区统计计算数据历史：从2004年1月开始提供数据权限：用户需要至少400积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期 （格式：YYYYMMDD，比如20181018，下同） |
| ts_code | str | N | TS代码 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| trade_date | str | Y | 交易日期 |
| total_mv | float | Y | 当日总市值（元） |
| float_mv | float | Y | 当日流通市值（元） |
| total_share | float | Y | 当日总股本（股） |
| float_share | float | Y | 当日流通股本（股） |
| free_share | float | Y | 当日自由流通股本（股） |
| turnover_rate | float | Y | 换手率 |
| turnover_rate_f | float | Y | 换手率(基于自由流通股本) |
| pe | float | Y | 市盈率 |
| pe_ttm | float | Y | 市盈率TTM |
| pb | float | Y | 市净率 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.index_dailybasic(trade_date='20181018', fields='ts_code,trade_date,turnover_rate,pe')
```
# Tushare期货数据

# 期货合约信息表

**路径**: 期货数据
**接口**: `fut_basic`
**积分**: 10000
**描述**: 获取期货合约列表数据限量：单次最大10000积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大10000积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| exchange | str | Y | 交易所代码 CFFEX-中金所 DCE-大商所 CZCE-郑商所 SHFE-上期所 INE-上海国际能源交易中心 GFEX-广州期货交易所 |
| fut_type | str | N | 合约类型 (1 普通合约 2主力与连续合约 默认取全部) |
| fut_code | str | N | 标准合约代码，如白银AG、AP鲜苹果等 |
| list_date | str | N | 上市开始日期(格式YYYYMMDD，从某日开始以来所有合约） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 合约代码 |
| symbol | str | Y | 交易标识 |
| exchange | str | Y | 交易市场 |
| name | str | Y | 中文简称 |
| fut_code | str | Y | 合约产品代码 |
| multiplier | float | Y | 合约乘数(只适用于国债期货、指数期货) |
| trade_unit | str | Y | 交易计量单位 |
| per_unit | float | Y | 交易单位(每手) |
| quote_unit | str | Y | 报价单位 |
| quote_unit_desc | str | Y | 最小报价单位说明 |
| d_mode_desc | str | Y | 交割方式说明 |
| list_date | str | Y | 上市日期 |
| delist_date | str | Y | 最后交易日期 |
| d_month | str | Y | 交割月份 |
| last_ddate | str | Y | 最后交割日 |
| trade_time_desc | str | N | 交易时间说明 |

## 调用示例

```python
pro = ts.pro_api('your token')

df = pro.fut_basic(exchange='DCE', fut_type='1', fields='ts_code,symbol,name,list_date,delist_date')
```
# 交易日历

**路径**: 期货数据
**接口**: `trade_cal`
**积分**: 2000
**描述**: 获取各大期货交易所交易日历数据积分：需2000积分才可以提取数据

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| exchange | str | N | 交易所 SHFE 上期所 DCE 大商所 CFFEX中金所  CZCE郑商所 INE上海国际能源交易所 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| is_open | int | N | 是否交易 0休市 1交易 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| exchange | str | Y | 交易所 同参数部分描述 |
| cal_date | str | Y | 日历日期 |
| is_open | int | Y | 是否交易 0休市 1交易 |
| pretrade_date | str | N | 上一个交易日 |

## 调用示例

```python
pro = ts.pro_api('your token')


df = pro.trade_cal(exchange='DCE', start_date='20180101', end_date='20181231')
```

```python
df = pro.query('trade_cal', exchange='DCE', start_date='20180101', end_date='20181231')
```
# 期货日线行情

**路径**: 期货数据
**接口**: `fut_daily`
**积分**: 2000
**描述**: 期货日线行情数据限量：单次最大2000条，总量不限制积分：用户需要至少2000积分才可以调取，未来可能调整积分，请尽量多的积累积分。具体请参阅积分获取办法
**限量**: 单次最大2000条，总量不限制积分：用户需要至少2000积分才可以调取，未来可能调整积分，请尽量多的积累积分。具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期(YYYYMMDD格式，下同) |
| ts_code | str | N | 合约代码 |
| exchange | str | N | 交易所代码 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS合约代码 |
| trade_date | str | Y | 交易日期 |
| pre_close | float | Y | 昨收盘价 |
| pre_settle | float | Y | 昨结算价 |
| open | float | Y | 开盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| close | float | Y | 收盘价 |
| settle | float | Y | 结算价 |
| change1 | float | Y | 涨跌1 收盘价-昨结算价 |
| change2 | float | Y | 涨跌2 结算价-昨结算价 |
| vol | float | Y | 成交量(手) |
| amount | float | Y | 成交金额(万元) |
| oi | float | Y | 持仓量(手) |
| oi_chg | float | Y | 持仓量变化 |
| delv_settle | float | N | 交割结算价 |

## 调用示例

```python
pro = ts.pro_api()

#获取CU1811合约20180101～20181113期间的行情
df = pro.fut_daily(ts_code='CU1811.SHF', start_date='20180101', end_date='20181113')

#获取2018年11月13日大商所全部合约行情数据
df = pro.fut_daily(trade_date='20181113', exchange='DCE', fields='ts_code,trade_date,pre_close,pre_settle,open,high,low,close,settle,vol')
```
# 每日成交持仓排名

**路径**: 期货数据
**接口**: `fut_holding`
**积分**: 2000
**描述**: 获取每日成交持仓排名数据限量：单次最大2000，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大2000，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期 （trade_date/symbol至少输入一个参数） |
| symbol | str | N | 合约或产品代码 |
| start_date | str | N | 开始日期(YYYYMMDD格式，下同) |
| end_date | str | N | 结束日期 |
| exchange | str | N | 交易所代码 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| symbol | str | Y | 合约代码或类型 |
| broker | str | Y | 期货公司会员简称 |
| vol | int | Y | 成交量 |
| vol_chg | int | Y | 成交量变化 |
| long_hld | int | Y | 持买仓量 |
| long_chg | int | Y | 持买仓量变化 |
| short_hld | int | Y | 持卖仓量 |
| short_chg | int | Y | 持卖仓量变化 |
| exchange | str | N | 交易所 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.fut_holding(trade_date='20181113', symbol='C1905', exchange='DCE')
```
# 沪深股票

# 仓单日报

**路径**: 期货数据
**接口**: `fut_wsr`
**积分**: 2000
**描述**: 获取仓单日报数据，了解各仓库/厂库的仓单变化限量：单次最大1000，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大1000，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期 |
| symbol | str | N | 产品代码 |
| start_date | str | N | 开始日期(YYYYMMDD格式，下同) |
| end_date | str | N | 结束日期 |
| exchange | str | N | 交易所代码 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| symbol | str | Y | 产品代码 |
| fut_name | str | Y | 产品名称 |
| warehouse | str | Y | 仓库名称 |
| wh_id | str | N | 仓库编号 |
| pre_vol | int | Y | 昨日仓单量 |
| vol | int | Y | 今日仓单量 |
| vol_chg | int | Y | 增减量 |
| area | str | N | 地区 |
| year | str | N | 年度 |
| grade | str | N | 等级 |
| brand | str | N | 品牌 |
| place | str | N | 产地 |
| pd | int | N | 升贴水 |
| is_ct | str | N | 是否折算仓单 |
| unit | str | Y | 单位 |
| exchange | str | N | 交易所 |

## 调用示例

```python
pro = ts.pro_api('your token')

df = pro.fut_wsr(trade_date='20181113', symbol='ZN')
```
# 结算参数

**路径**: 期货数据
**接口**: `fut_settle`
**积分**: 2000
**描述**: 获取每日结算参数数据，包括交易和交割费率等限量：单次最大返回1600行数据，可根据日期循环，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大返回1600行数据，可根据日期循环，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期 （trade_date/ts_code至少需要输入一个参数） |
| ts_code | str | N | 合约代码 |
| start_date | str | N | 开始日期(YYYYMMDD格式，下同) |
| end_date | str | N | 结束日期 |
| exchange | str | N | 交易所代码 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 合约代码 |
| trade_date | str | Y | 交易日期 |
| settle | float | Y | 结算价 |
| trading_fee_rate | float | Y | 交易手续费率 |
| trading_fee | float | Y | 交易手续费 |
| delivery_fee | float | Y | 交割手续费 |
| b_hedging_margin_rate | float | Y | 买套保交易保证金率 |
| s_hedging_margin_rate | float | Y | 卖套保交易保证金率 |
| long_margin_rate | float | Y | 买投机交易保证金率 |
| short_margin_rate | float | Y | 卖投机交易保证金率 |
| offset_today_fee | float | N | 平今仓手续率 |
| exchange | str | N | 交易所 |

## 调用示例

```python
pro = ts.pro_api('your token')

df = pro.fut_settle(trade_date='20181114', exchange='SHFE')
```
# 特色大数据

# 新闻快讯

**路径**: 大模型语料专题数据
**接口**: `news`
**描述**: 获取主流新闻网站的快讯新闻数据,提供超过6年以上历史新闻。限量：单次最大1500条新闻，可根据时间参数循环提取历史积分：本接口需单独开权限（跟积分没关系），具体请参阅权限说明
**限量**: 单次最大1500条新闻，可根据时间参数循环提取历史积分：本接口需单独开权限（跟积分没关系），具体请参阅权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| start_date | datetime | Y | 开始日期(格式：2018-11-20 09:00:00） |
| end_date | datetime | Y | 结束日期 |
| src | str | Y | 新闻来源 见下表 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| datetime | str | Y | 新闻时间 |
| content | str | Y | 内容 |
| title | str | Y | 标题 |
| channels | str | N | 分类 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.news(src='sina', start_date='2018-11-21 09:00:00', end_date='2018-11-22 10:10:00')
```
# 周线行情

**路径**: 股票数据/行情数据
**接口**: `weekly`
**积分**: 2000
**描述**: 获取A股周线行情，本接口每周最后一个交易日更新，如需要使用每天更新的周线数据，请使用日度更新的周线行情接口。限量：单次最大6000行，可使用交易日期循环提取，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大6000行，可使用交易日期循环提取，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码 （ts_code,trade_date两个参数任选一） |
| trade_date | str | N | 交易日期 （每周最后一个交易日期，YYYYMMDD格式） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| close | float | Y | 周收盘价 |
| open | float | Y | 周开盘价 |
| high | float | Y | 周最高价 |
| low | float | Y | 周最低价 |
| pre_close | float | Y | 上一周收盘价 |
| change | float | Y | 周涨跌额 |
| pct_chg | float | Y | 周涨跌 （未复权，未100，如果是复权请用 通用行情接口，如需%单位请100 ） |
| vol | float | Y | 周成交量 |
| amount | float | Y | 周成交额 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.weekly(ts_code='000001.SZ', start_date='20180101', end_date='20181101', fields='ts_code,trade_date,open,high,low,close,vol,amount')
```

```python
df = pro.weekly(trade_date='20181123', fields='ts_code,trade_date,open,high,low,close,vol,amount')
```
# 月线行情

**路径**: 股票数据/行情数据
**接口**: `monthly`
**积分**: 2000
**描述**: 获取A股月线数据限量：单次最大4500行，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大4500行，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码 （ts_code,trade_date两个参数任选一） |
| trade_date | str | N | 交易日期 （每月最后一个交易日日期，YYYYMMDD格式） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| close | float | Y | 月收盘价 |
| open | float | Y | 月开盘价 |
| high | float | Y | 月最高价 |
| low | float | Y | 月最低价 |
| pre_close | float | Y | 上月收盘价 |
| change | float | Y | 月涨跌额 |
| pct_chg | float | Y | 月涨跌幅 （未复权，如果是复权请用 通用行情接口 ） |
| vol | float | Y | 月成交量 |
| amount | float | Y | 月成交额 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.monthly(ts_code='000001.SZ', start_date='20180101', end_date='20181101', fields='ts_code,trade_date,open,high,low,close,vol,amount')
```

```python
df = pro.monthly(trade_date='20181031', fields='ts_code,trade_date,open,high,low,close,vol,amount')
```
# A股复权行情

**路径**: 股票数据/行情数据

## 调用示例

```python
#取000001的前复权行情
df = ts.pro_bar(ts_code='000001.SZ', adj='qfq', start_date='20180101', end_date='20181011')

#取000001的后复权行情
df = ts.pro_bar(ts_code='000001.SZ', adj='hfq', start_date='20180101', end_date='20181011')
```

```python
#取000001的周线前复权行情
df = ts.pro_bar( ts_code='000001.SZ', freq='W', adj='qfq', start_date='20180101', end_date='20181011')

#取000001的周线后复权行情
df = ts.pro_bar(ts_code='000001.SZ', freq='W', adj='hfq', start_date='20180101', end_date='20181011')
```

```python
#取000001的月线前复权行情
df = ts.pro_bar(ts_code='000001.SZ', freq='M', adj='qfq', start_date='20180101', end_date='20181011')

#取000001的月线后复权行情
df = ts.pro_bar(ts_code='000001.SZ', freq='M', adj='hfq', start_date='20180101', end_date='20181011')
```
# 未知接口

# 利率数据

**路径**: 宏观经济/国内宏观
# Shibor利率数据

**路径**: 宏观经济/国内宏观/利率数据
**接口**: `shibor`
**积分**: 120
**描述**: shibor利率限量：单次最大2000，总量不限制，可通过设置开始和结束日期分段获取积分：用户积累120积分可以调取，具体请参阅积分获取办法
**限量**: 单次最大2000，总量不限制，可通过设置开始和结束日期分段获取积分：用户积累120积分可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期 (日期输入格式：YYYYMMDD，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| on | float | Y | 隔夜 |
| 1w | float | Y | 1周 |
| 2w | float | Y | 2周 |
| 1m | float | Y | 1个月 |
| 3m | float | Y | 3个月 |
| 6m | float | Y | 6个月 |
| 9m | float | Y | 9个月 |
| 1y | float | Y | 1年 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.shibor(start_date='20180101', end_date='20181101')
```
# 行情数据

**路径**: 股票数据
# Shibor报价数据

**路径**: 宏观经济/国内宏观/利率数据
**接口**: `shibor_quote`
**积分**: 120
**描述**: Shibor报价数据限量：单次最大4000行数据，总量不限制，可通过设置开始和结束日期分段获取积分：用户积累120积分可以调取，具体请参阅积分获取办法
**限量**: 单次最大4000行数据，总量不限制，可通过设置开始和结束日期分段获取积分：用户积累120积分可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期 (日期输入格式：YYYYMMDD，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| bank | str | N | 银行名称 （中文名称，例如 农业银行） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| bank | str | Y | 报价银行 |
| on_b | float | Y | 隔夜_Bid |
| on_a | float | Y | 隔夜_Ask |
| 1w_b | float | Y | 1周_Bid |
| 1w_a | float | Y | 1周_Ask |
| 2w_b | float | Y | 2周_Bid |
| 2w_a | float | Y | 2周_Ask |
| 1m_b | float | Y | 1月_Bid |
| 1m_a | float | Y | 1月_Ask |
| 3m_b | float | Y | 3月_Bid |
| 3m_a | float | Y | 3月_Ask |
| 6m_b | float | Y | 6月_Bid |
| 6m_a | float | Y | 6月_Ask |
| 9m_b | float | Y | 9月_Bid |
| 9m_a | float | Y | 9月_Ask |
| 1y_b | float | Y | 1年_Bid |
| 1y_a | float | Y | 1年_Ask |

## 调用示例

```python
pro = ts.pro_api()

df = pro.shibor_quote(start_date='20180101', end_date='20181101')
```
# LPR贷款基础利率

**路径**: 宏观经济/国内宏观/利率数据
**接口**: `shibor_lpr`
**积分**: 120
**描述**: LPR贷款基础利率限量：单次最大4000(相当于单次可提取18年历史)，总量不限制，可通过设置开始和结束日期分段获取积分：用户积累120积分可以调取，具体请参阅积分获取办法
**限量**: 单次最大4000(相当于单次可提取18年历史)，总量不限制，可通过设置开始和结束日期分段获取积分：用户积累120积分可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期  (日期输入格式：YYYYMMDD，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| 1y | float | Y | 1年贷款利率 |
| 5y | float | Y | 5年贷款利率 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.shibor_lpr(start_date='20180101', end_date='20181130', fields='date,1y')
```
# Libor拆借利率

**路径**: 宏观经济/国内宏观/利率数据
**接口**: `libor`
**积分**: 120
**描述**: Libor拆借利率限量：单次最大4000行数据，总量不限制，可通过设置开始和结束日期分段获取积分：用户积累120积分可以调取，具体请参阅积分获取办法
**限量**: 单次最大4000行数据，总量不限制，可通过设置开始和结束日期分段获取积分：用户积累120积分可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期 (日期输入格式：YYYYMMDD，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| curr_type | str | N | 货币代码  (USD美元  EUR欧元  JPY日元  GBP英镑  CHF瑞郎，默认是USD) |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| curr_type | str | Y | 货币 |
| on | float | Y | 隔夜 |
| 1w | float | Y | 1周 |
| 1m | float | Y | 1个月 |
| 2m | float | Y | 2个月 |
| 3m | float | Y | 3个月 |
| 6m | float | Y | 6个月 |
| 12m | float | Y | 12个月 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.libor(curr_type='USD', start_date='20180101', end_date='20181130')
```
# Hibor利率

**路径**: 宏观经济/国内宏观/利率数据
**接口**: `hibor`
**积分**: 120
**描述**: Hibor利率限量：单次最大4000行数据，总量不限制，可通过设置开始和结束日期分段获取积分：用户积累120积分可以调取，具体请参阅积分获取办法
**限量**: 单次最大4000行数据，总量不限制，可通过设置开始和结束日期分段获取积分：用户积累120积分可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期  (日期输入格式：YYYYMMDD，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| on | float | Y | 隔夜 |
| 1w | float | Y | 1周 |
| 2w | float | Y | 2周 |
| 1m | float | Y | 1个月 |
| 2m | float | Y | 2个月 |
| 3m | float | Y | 3个月 |
| 6m | float | Y | 6个月 |
| 12m | float | Y | 12个月 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.hibor(start_date='20180101', end_date='20181130')
```
# 新闻联播

**路径**: 大模型语料专题数据
**接口**: `cctv_news`
**描述**: 获取新闻联播文字稿数据，数据开始于2006年6月，超过12年历史限量：可根据日期参数循环提取，总量不限制积分：本接口需单独开权限（跟积分没关系），具体请参阅权限说明
**限量**: 可根据日期参数循环提取，总量不限制积分：本接口需单独开权限（跟积分没关系），具体请参阅权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | Y | 日期（输入格式：YYYYMMDD 比如：20181211） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| title | str | Y | 标题 |
| content | str | Y | 内容 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.cctv_news(date='20181211')
```
# 南华期货指数日线行情

**路径**: 期货数据
**接口**: `index_daily`
**积分**: 2000
**描述**: 获取南华指数每日行情，指数行情也可以通过通用行情接口获取数据．权限：用户需要累积2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 指数代码（南华期货指数以 .NH 结尾，具体请参考本文最下方） |
| trade_date | str | N | 交易日期 （日期格式：YYYYMMDD，下同） |
| start_date | str | N | 开始日期 |
| end_date | None | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | TS指数代码 |
| trade_date | str | 交易日 |
| close | float | 收盘点位 |
| open | float | 开盘点位 |
| high | float | 最高点位 |
| low | float | 最低点位 |
| pre_close | float | 昨日收盘点 |
| change | float | 涨跌点 |
| pct_chg | float | 涨跌幅 |
| vol | float | 成交量（手） |
| amount | float | 成交额（千元） |

## 调用示例

```python
pro = ts.pro_api()

#获取南华沪铜指数
df = pro.index_daily(ts_code='CU.NH', start_date='20180101', end_date='20181201')
```
# 全国电影剧本备案数据

**路径**: 行业经济/TMT行业
**接口**: `film_record`
**积分**: 120
**描述**: 获取全国电影剧本备案的公示数据限量：单次最大500，总量不限制数据权限：用户需要至少120积分才可以调取，积分越多调取频次越高，具体请参阅积分获取办法
**限量**: 单次最大500，总量不限制数据权限：用户需要至少120积分才可以调取，积分越多调取频次越高，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ann_date | str | N | 公布日期 （至少输入一个参数，格式：YYYYMMDD，日期不连续，定期公布） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| rec_no | str | Y | 备案号 |
| film_name | str | Y | 影片名称 |
| rec_org | str | Y | 备案单位 |
| script_writer | str | Y | 编剧 |
| rec_result | str | Y | 备案结果 |
| rec_area | str | Y | 备案地（备案时间） |
| classified | str | Y | 影片分类 |
| date_range | str | Y | 备案日期区间 |
| ann_date | str | Y | 备案结果发布时间 |

## 调用示例

```python
pro = ts.pro_api()
#或者
#pro = ts.pro_api('your token')

df = pro.film_record(start_date='20181014', end_date='20181214')
```
# Tushare期权数据

# 期权合约信息

**路径**: 期权数据
**接口**: `opt_basic`
**积分**: 5000
**描述**: 获取期权合约信息积分：用户需要至少5000积分可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS期权代码 |
| exchange | str | N | 交易所代码 （包括上交所SSE等交易所） |
| opt_code | str | N | 标准合约代码，OP+期货合约TS_CODE，如棕榈油2207合约，输入OPP2207.DCE |
| call_put | str | N | 期权类型 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| exchange | str | Y | 交易市场 |
| name | str | Y | 合约名称 |
| per_unit | str | Y | 合约单位 |
| opt_code | str | Y | 标的合约代码 |
| opt_type | str | Y | 合约类型 |
| call_put | str | Y | 期权类型 |
| exercise_type | str | Y | 行权方式 |
| exercise_price | float | Y | 行权价格 |
| s_month | str | Y | 结算月 |
| maturity_date | str | Y | 到期日 |
| list_price | float | Y | 挂牌基准价 |
| list_date | str | Y | 开始交易日期 |
| delist_date | str | Y | 最后交易日期 |
| last_edate | str | Y | 最后行权日期 |
| last_ddate | str | Y | 最后交割日期 |
| quote_unit | str | Y | 报价单位 |
| min_price_chg | str | Y | 最小价格波幅 |

## 调用示例

```python
pro = ts.pro_api('your token')

df = pro.opt_basic(exchange='DCE', fields='ts_code,name,exercise_type,list_date,delist_date')
```
# 期权日线行情

**路径**: 期权数据
**接口**: `opt_daily`
**积分**: 2000
**描述**: 获取期权日线行情限量：单次最大15000条数据，可跟进日线或者代码循环，总量不限制积分：用户需要至少2000积分才可以调取，但有流量控制，请自行提高积分，积分越多权限越大，具体请参阅积分获取办法
**限量**: 单次最大15000条数据，可跟进日线或者代码循环，总量不限制积分：用户需要至少2000积分才可以调取，但有流量控制，请自行提高积分，积分越多权限越大，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS合约代码（输入代码或时间至少任意一个参数） |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| exchange | str | N | 交易所(SSE/SZSE/CFFEX/DCE/SHFE/CZCE） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| trade_date | str | Y | 交易日期 |
| exchange | str | Y | 交易市场 |
| pre_settle | float | Y | 昨结算价 |
| pre_close | float | Y | 前收盘价 |
| open | float | Y | 开盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| close | float | Y | 收盘价 |
| settle | float | Y | 结算价 |
| vol | float | Y | 成交量(手) |
| amount | float | Y | 成交金额(万元) |
| oi | float | Y | 持仓量(手) |

## 调用示例

```python
pro = ts.pro_api('your token')

df = pro.opt_daily(trade_date='20181212')
```
# 财务数据

**路径**: 股票数据
# 限售股解禁

**路径**: 股票数据/参考数据
**接口**: `share_float`
**积分**: 5000
**描述**: 获取限售股解禁限量：单次最大6000条，总量不限制积分：120分可调取，每分钟内限制次数，超过5000积分频次相对较高，具体请参阅积分获取办法
**限量**: 单次最大6000条，总量不限制积分：120分可调取，每分钟内限制次数，超过5000积分频次相对较高，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS股票代码 |
| ann_date | str | N | 公告日期（日期格式：YYYYMMDD，下同） |
| float_date | str | N | 解禁日期 |
| start_date | str | N | 解禁开始日期 |
| end_date | str | N | 解禁结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| ann_date | str | Y | 公告日期 |
| float_date | str | Y | 解禁日期 |
| float_share | float | Y | 流通股份(股) |
| float_ratio | float | Y | 流通股份占总股本比率 |
| holder_name | str | Y | 股东名称 |
| share_type | str | Y | 股份类型 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.share_float(ann_date='20181220')
```
# 大宗交易

**路径**: 股票数据/参考数据
**接口**: `block_trade`
**积分**: 300
**描述**: 大宗交易限量：单次最大1000条，总量不限制积分：300积分可调取，每分钟内限制次数，超过5000积分频次相对较高，具体请参阅积分获取办法
**限量**: 单次最大1000条，总量不限制积分：300积分可调取，每分钟内限制次数，超过5000积分频次相对较高，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码（股票代码和日期至少输入一个参数） |
| trade_date | str | N | 交易日期（格式：YYYYMMDD，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| trade_date | str | Y | 交易日历 |
| price | float | Y | 成交价 |
| vol | float | Y | 成交量（万股） |
| amount | float | Y | 成交金额 |
| buyer | str | Y | 买方营业部 |
| seller | str | Y | 卖方营业部 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.block_trade(trade_date='20181227')
```
# 财报披露计划

**路径**: 股票数据/财务数据
**接口**: `disclosure_date`
**积分**: 500
**描述**: 获取财报披露计划日期限量：单次最大3000，总量不限制积分：用户需要至少500积分才可以调取，积分越多权限越大，具体请参阅积分获取办法
**限量**: 单次最大3000，总量不限制积分：用户需要至少500积分才可以调取，积分越多权限越大，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS股票代码 |
| end_date | str | N | 财报周期（每个季度最后一天的日期，比如20181231表示2018年年报，20180630表示中报) |
| pre_date | str | N | 计划披露日期 |
| ann_date | str | N | 最新披露公告日 |
| actual_date | str | N | 实际披露日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| ann_date | str | Y | 最新披露公告日 |
| end_date | str | Y | 报告期 |
| pre_date | str | Y | 预计披露日期 |
| actual_date | str | Y | 实际披露日期 |
| modify_date | str | N | 披露日期修正记录 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.disclosure_date(end_date='20181231')
```
# 股票账户开户数据

**路径**: 股票数据/参考数据
**接口**: `stk_account`
**积分**: 600
**描述**: 获取股票账户开户数据，统计周期为一周积分：600积分可调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 统计周期 |
| weekly_new | float | Y | 本周新增（万） |
| total | float | Y | 期末总账户数（万） |
| weekly_hold | float | Y | 本周持仓账户数（万） |
| weekly_trade | float | Y | 本周参与交易账户数（万） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.stk_account(start_date='20180101', end_date='20181231')
```
# 股票账户开户数据（旧）

**路径**: 股票数据/参考数据
**接口**: `stk_account_old`
**积分**: 600
**描述**: 获取股票账户开户数据旧版格式数据，数据从2008年1月开始，到2015年5月29，新数据请通过股票开户数据获取。积分：600积分可调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 统计周期 |
| new_sh | int | Y | 本周新增（上海，户） |
| new_sz | int | Y | 本周新增（深圳，户） |
| active_sh | float | Y | 期末有效账户（上海，万户） |
| active_sz | float | Y | 期末有效账户（深圳，万户） |
| total_sh | float | Y | 期末账户数（上海，万户） |
| total_sz | float | Y | 期末账户数（深圳，万户） |
| trade_sh | float | Y | 参与交易账户数（上海，万户） |
| trade_sz | float | Y | 参与交易账户数（深圳，万户） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.stk_account_old(start_date='20140101', end_date='20141231')
```
# 股东人数

**路径**: 股票数据/参考数据
**接口**: `stk_holdernumber`
**积分**: 600
**描述**: 获取上市公司股东户数数据，数据不定期公布限量：单次最大3000,总量不限制积分：600积分可调取，基础积分每分钟调取100次，5000积分以上频次相对较高。具体请参阅积分获取办法
**限量**: 单次最大3000,总量不限制积分：600积分可调取，基础积分每分钟调取100次，5000积分以上频次相对较高。具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS股票代码 |
| ann_date | str | N | 公告日期 |
| enddate | str | N | 截止日期 |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS股票代码 |
| ann_date | str | Y | 公告日期 |
| end_date | str | Y | 截止日期 |
| holder_num | int | Y | 股东户数 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.stk_holdernumber(ts_code='300199.SZ', start_date='20160101', end_date='20181231')
```
# 市场参考数据

**路径**: 股票数据
# 个股资金流向

**路径**: 股票数据/资金流向数据
**接口**: `moneyflow`
**积分**: 2000
**描述**: 获取沪深A股票资金流向数据，分析大单小单成交情况，用于判别资金动向，数据开始于2010年。限量：单次最大提取6000行记录，总量不限制积分：用户需要至少2000积分才可以调取，基础积分有流量控制，积分越多权限越大，请自行提高积分，具体请参阅积分获取办法
**限量**: 单次最大提取6000行记录，总量不限制积分：用户需要至少2000积分才可以调取，基础积分有流量控制，积分越多权限越大，请自行提高积分，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 （股票和时间参数至少输入一个） |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| trade_date | str | Y | 交易日期 |
| buy_sm_vol | int | Y | 小单买入量（手） |
| buy_sm_amount | float | Y | 小单买入金额（万元） |
| sell_sm_vol | int | Y | 小单卖出量（手） |
| sell_sm_amount | float | Y | 小单卖出金额（万元） |
| buy_md_vol | int | Y | 中单买入量（手） |
| buy_md_amount | float | Y | 中单买入金额（万元） |
| sell_md_vol | int | Y | 中单卖出量（手） |
| sell_md_amount | float | Y | 中单卖出金额（万元） |
| buy_lg_vol | int | Y | 大单买入量（手） |
| buy_lg_amount | float | Y | 大单买入金额（万元） |
| sell_lg_vol | int | Y | 大单卖出量（手） |
| sell_lg_amount | float | Y | 大单卖出金额（万元） |
| buy_elg_vol | int | Y | 特大单买入量（手） |
| buy_elg_amount | float | Y | 特大单买入金额（万元） |
| sell_elg_vol | int | Y | 特大单卖出量（手） |
| sell_elg_amount | float | Y | 特大单卖出金额（万元） |
| net_mf_vol | int | Y | 净流入量（手） |
| net_mf_amount | float | Y | 净流入额（万元） |

## 调用示例

```python
pro = ts.pro_api('your token')

#获取单日全部股票数据
df = pro.moneyflow(trade_date='20190315')

#获取单个股票数据
df = pro.moneyflow(ts_code='002149.SZ', start_date='20190115', end_date='20190315')
```
# 指数周线行情

**路径**: 指数专题
**接口**: `index_weekly`
**积分**: 600
**描述**: 获取指数周线行情限量：单次最大1000行记录，可分批获取，总量不限制积分：用户需要至少600积分才可以调取，积分越多频次越高，具体请参阅积分获取办法
**限量**: 单次最大1000行记录，可分批获取，总量不限制积分：用户需要至少600积分才可以调取，积分越多频次越高，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码 |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS指数代码 |
| trade_date | str | Y | 交易日 |
| close | float | Y | 收盘点位 |
| open | float | Y | 开盘点位 |
| high | float | Y | 最高点位 |
| low | float | Y | 最低点位 |
| pre_close | float | Y | 昨日收盘点 |
| change | float | Y | 涨跌点位 |
| pct_chg | float | Y | 涨跌幅 |
| vol | float | Y | 成交量（手） |
| amount | float | Y | 成交额（千元） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.index_weekly(ts_code='000001.SH', start_date='20180101', end_date='20190329', fields='ts_code,trade_date,open,high,low,close,vol,amount')
```

```python
df = pro.index_weekly(trade_date='20190329', fields='ts_code,trade_date,open,high,low,close,vol,amount')
```
# 指数月线行情

**路径**: 指数专题
**接口**: `index_monthly`
**积分**: 600
**描述**: 获取指数月线行情,每月更新一次限量：单次最大1000行记录,可多次获取,总量不限制积分：用户需要至少600积分才可以调取，积分越多频次越高，具体请参阅积分获取办法
**限量**: 单次最大1000行记录,可多次获取,总量不限制积分：用户需要至少600积分才可以调取，积分越多频次越高，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码 |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS指数代码 |
| trade_date | str | Y | 交易日 |
| close | float | Y | 收盘点位 |
| open | float | Y | 开盘点位 |
| high | float | Y | 最高点位 |
| low | float | Y | 最低点位 |
| pre_close | float | Y | 昨日收盘点 |
| change | float | Y | 涨跌点位 |
| pct_chg | float | Y | 涨跌幅 |
| vol | float | 成交量（手） |  |
| amount | float | 成交额（千元） |  |

## 调用示例

```python
pro = ts.pro_api()

df = pro.index_monthly(ts_code='000001.SH', start_date='20180101', end_date='20190330', fields='ts_code,trade_date,open,high,low,close,vol,amount')
```

```python
df = pro.index_monthly(trade_date='20190329', fields='ts_code,trade_date,open,high,low,close,vol,amount')
```
# 温州民间借贷利率

**路径**: 宏观经济/国内宏观/利率数据
**接口**: `wz_index`
**积分**: 2000
**描述**: 温州民间借贷利率，即温州指数限量：不限量，一次可取全部指标全部历史数据积分：用户需要积攒2000积分可调取，具体请参阅积分获取办法数据来源：温州指数网注：温州指数 ，即温州民间融资综合利率指数，该指数及时反映民间金融交易活跃度和交易价格。该指数样板数据主要采集于四个方面：由温州市设立的几百家企业测报点，把各自借入的民间资本利率通过各地方金融办不记名申报收集起来；对各小额贷款公司借出的利率进行加权平均；融资性担保公司如典当行在融资过程中的利率，由温州经信委和商务局负责测报；民间借贷服务中心的实时利率。这些利率进行加权平均，就得出了“温州指数”。它是温州民间融资利率的风向标。2012年12月7日，温州指数正式对外发布。
**限量**: 不限量，一次可取全部指标全部历史数据积分：用户需要积攒2000积分可调取，具体请参阅积分获取办法数据来源：温州指数网注：温州指数 ，即温州民间融资综合利率指数，该指数及时反映民间金融交易活跃度和交易价格。该指数样板数据主要采集于四个方面：由温州市设立的几百家企业测报点，把各自借入的民间资本利率通过各地方金融办不记名申报收集起来；对各小额贷款公司借出的利率进行加权平均；融资性担保公司如典当行在融资过程中的利率，由温州经信委和商务局负责测报；民间借贷服务中心的实时利率。这些利率进行加权平均，就得出了“温州指数”。它是温州民间融资利率的风向标。2012年12月7日，温州指数正式对外发布。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| comp_rate | float | Y | 温州民间融资综合利率指数 (%，下同) |
| center_rate | float | Y | 民间借贷服务中心利率 |
| micro_rate | float | Y | 小额贷款公司放款利率 |
| cm_rate | float | Y | 民间资本管理公司融资价格 |
| sdb_rate | float | Y | 社会直接借贷利率 |
| om_rate | float | Y | 其他市场主体利率 |
| aa_rate | float | Y | 农村互助会互助金费率 |
| m1_rate | float | Y | 温州地区民间借贷分期限利率（一月期） |
| m3_rate | float | Y | 温州地区民间借贷分期限利率（三月期） |
| m6_rate | float | Y | 温州地区民间借贷分期限利率（六月期） |
| m12_rate | float | Y | 温州地区民间借贷分期限利率（一年期） |
| long_rate | float | Y | 温州地区民间借贷分期限利率（长期） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.wz_index(start_date='20180101', end_date='20190401')
```
# 广州民间借贷利率

**路径**: 宏观经济/国内宏观/利率数据
**接口**: `gz_index`
**积分**: 2000
**描述**: 广州民间借贷利率限量：不限量，一次可取全部指标全部历史数据积分：用户需要积攒2000积分可调取，具体请参阅积分获取办法数据来源：广州民间金融街
**限量**: 不限量，一次可取全部指标全部历史数据积分：用户需要积攒2000积分可调取，具体请参阅积分获取办法数据来源：广州民间金融街

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| d10_rate | float | Y | 小额贷市场平均利率（十天） （单位：%，下同） |
| m1_rate | float | Y | 小额贷市场平均利率（一月期） |
| m3_rate | float | Y | 小额贷市场平均利率（三月期） |
| m6_rate | float | Y | 小额贷市场平均利率（六月期） |
| m12_rate | float | Y | 小额贷市场平均利率（一年期） |
| long_rate | float | Y | 小额贷市场平均利率（长期） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.gz_index(start_date='20180101', end_date='20190401')
```
# 股东增减持

**路径**: 股票数据/参考数据
**接口**: `stk_holdertrade`
**积分**: 2000
**描述**: 获取上市公司增减持数据，了解重要股东近期及历史上的股份增减变化限量：单次最大提取3000行记录，总量不限制积分：用户需要至少2000积分才可以调取。基础积分有流量控制，积分越多权限越大，5000积分以上无明显限制，请自行提高积分，具体请参阅积分获取办法
**限量**: 单次最大提取3000行记录，总量不限制积分：用户需要至少2000积分才可以调取。基础积分有流量控制，积分越多权限越大，5000积分以上无明显限制，请自行提高积分，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS股票代码 |
| ann_date | str | N | 公告日期 |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |
| trade_type | str | N | 交易类型IN增持DE减持 |
| holder_type | str | N | 股东类型C公司P个人G高管 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| ann_date | str | Y | 公告日期 |
| holder_name | str | Y | 股东名称 |
| holder_type | str | Y | 股东类型G高管P个人C公司 |
| in_de | str | Y | 类型IN增持DE减持 |
| change_vol | float | Y | 变动数量 |
| change_ratio | float | Y | 占流通比例（%） |
| after_share | float | Y | 变动后持股 |
| after_ratio | float | Y | 变动后占流通比例（%） |
| avg_price | float | Y | 平均价格 |
| total_share | float | Y | 持股总数 |
| begin_date | str | N | 增减持开始日期 |
| close_date | str | N | 增减持结束日期 |

## 调用示例

```python
#获取单日全部增减持数据
df = pro.stk_holdertrade(ann_date='20190426')

#获取单个股票数据
df = pro.stk_holdertrade(ts_code='002149.SZ')

#获取当日增持数据
df = pro.stk_holdertrade(ann_date='20190426', trade_type='IN')
```
# 上市公司全量公告

**路径**: 大模型语料专题数据
**接口**: `anns_d`
**描述**: 获取全量公告数据，提供pdf下载URL限量：单次最大2000条数，可以跟进日期循环获取全量权限：本接口为单独权限，请参考权限说明
**限量**: 单次最大2000条数，可以跟进日期循环获取全量权限：本接口为单独权限，请参考权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| ann_date | str | N | 公告日期（yyyymmdd格式，下同） |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ann_date | str | Y | 公告日期 |
| ts_code | str | Y | 股票代码 |
| name | str | Y | 股票名称 |
| title | str | Y | 标题 |
| url | str | Y | URL，原文下载链接 |
| rec_time | datetime | N | 发布时间 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.anns_d(ann_date='20230621')
```
# Tushare外汇数据

# 外汇基础信息（海外）

**路径**: 外汇数据
**接口**: `fx_obasic`
**积分**: 2000
**描述**: 获取海外外汇基础信息，目前只有FXCM交易商的数据数量：单次可提取全部数据积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| exchange | str | N | 交易商 |
| classify | str | N | 分类 |
| ts_code | str | N | TS代码 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 外汇代码 |
| name | str | Y | 名称 |
| classify | str | Y | 分类 |
| exchange | str | Y | 交易商 |
| min_unit | float | Y | 最小交易单位 |
| max_unit | float | Y | 最大交易单位 |
| pip | float | Y | 点 |
| pip_cost | float | Y | 点值 |
| traget_spread | float | Y | 目标差价 |
| min_stop_distance | float | Y | 最小止损距离（点子） |
| trading_hours | str | Y | 交易时间 |
| break_time | str | Y | 休市时间 |

## 调用示例

```python
pro = ts.pro_api()

#获取差价合约(CFD)中指数产的基础信息
df = pro.fx_obasic(exchange='FXCM', classify='INDEX', fields='ts_code,name,min_unit,max_unit,pip,pip_cost')
```
# 外汇日线行情

**路径**: 外汇数据
**接口**: `fx_daily`
**积分**: 2000
**描述**: 获取外汇日线行情限量：单次最大提取1000行记录，可多次提取，总量不限制积分：用户需要至少2000积分才可以调取，但有流量控制，5000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法
**限量**: 单次最大提取1000行记录，可多次提取，总量不限制积分：用户需要至少2000积分才可以调取，但有流量控制，5000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码 |
| trade_date | str | N | 交易日期（GMT，日期是格林尼治时间，比北京时间晚一天） |
| start_date | str | N | 开始日期（GMT） |
| end_date | str | N | 结束日期（GMT） |
| exchange | str | N | 交易商，目前只有FXCM |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 外汇代码 |
| trade_date | str | Y | 交易日期 |
| bid_open | float | Y | 买入开盘价 |
| bid_close | float | Y | 买入收盘价 |
| bid_high | float | Y | 买入最高价 |
| bid_low | float | Y | 买入最低价 |
| ask_open | float | Y | 卖出开盘价 |
| ask_close | float | Y | 卖出收盘价 |
| ask_high | float | Y | 卖出最高价 |
| ask_low | float | Y | 卖出最低价 |
| tick_qty | int | Y | 报价笔数 |
| exchange | str | N | 交易商 |

## 调用示例

```python
pro = ts.pro_api()


#获取美元人民币交易对的日线行情
df = pro.fx_daily(ts_code='USDCNH.FXCM', start_date='20190101', end_date='20190524')
```
# 基金数据

# 全国拍摄制作电视剧备案公示数据

**路径**: 行业经济/TMT行业
**接口**: `teleplay_record`
**描述**: 获取2009年以来全国拍摄制作电视剧备案公示数据限量：单次最大1000，总量不限制数据权限：用户需要至少积分600才可以调取，积分越多调取频次越高，具体请参阅积分获取办法
**限量**: 单次最大1000，总量不限制数据权限：用户需要至少积分600才可以调取，积分越多调取频次越高，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| report_date | str | N | 备案月份（YYYYMM） |
| start_date | str | N | 备案开始月份（YYYYMM） |
| end_date | str | N | 备案结束月份（YYYYMM） |
| org | str | N | 备案机构 |
| name | str | N | 电视剧名称 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| name | str | Y | 电视剧名称 |
| classify | str | Y | 题材 |
| types | str | Y | 体裁 |
| org | str | Y | 报备机构 |
| report_date | str | Y | 报备时间 |
| license_key | str | Y | 许可证号 |
| episodes | str | Y | 集数 |
| shooting_date | str | Y | 拍摄时间 |
| prod_cycle | str | Y | 制作周期 |
| content | str | Y | 内容提要 |
| pro_opi | str | Y | 省级管理部门备案意见 |
| dept_opi | str | Y | 相关部门意见 |
| remarks | str | Y | 备注 |

## 调用示例

```python
pro = ts.pro_api()

#按备案月份查询
df = pro.teleplay_record(report_date='201905')

df = pro.teleplay_record(start_date='201905', end_date='201906')

#按备案机构查询
df = pro.teleplay_record(org='上海新文化传媒集团股份有限公司')

#按电视剧名称查询
df = pro.teleplay_record(name='三体')
```
# 申万行业分类

**路径**: 指数专题
**接口**: `index_classify`
**积分**: 2000
**描述**: 获取申万行业分类，可以获取申万2014年版本（28个一级分类，104个二级分类，227个三级分类）和2021年本版（31个一级分类，134个二级分类，346个三级分类）列表信息权限：用户需2000积分可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| index_code | str | N | 指数代码 |
| level | str | N | 行业分级（L1/L2/L3） |
| parent_code | str | N | 父级代码（一级为0） |
| src | str | N | 指数来源（SW2014：申万2014年版本，SW2021：申万2021年版本） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| index_code | str | Y | 指数代码 |
| industry_name | str | Y | 行业名称 |
| parent_code | str | Y | 父级代码 |
| level | str | Y | 行业名称 |
| industry_code | str | Y | 行业代码 |
| is_pub | str | Y | 是否发布了指数 |
| src | str | N | 行业分类（SW申万） |

## 调用示例

```python
#获取申万一级行业列表
df = pro.index_classify(level='L1', src='SW2021')

#获取申万二级行业列表
df = pro.index_classify(level='L2', src='SW2021')

#获取申万三级级行业列表
df = pro.index_classify(level='L3', src='SW2021')
```
# 每日涨跌停价格

**路径**: 股票数据/行情数据
**接口**: `stk_limit`
**积分**: 2000
**描述**: 获取全市场（包含A/B股和基金）每日涨跌停价格，包括涨停价格，跌停价格等，每个交易日8点40左右更新当日股票涨跌停价格。限量：单次最多提取5800条记录，可循环调取，总量不限制积分：用户积2000积分可调取，单位分钟有流控，积分越高流量越大，请自行提高积分，具体请参阅积分获取办法
**限量**: 单次最多提取5800条记录，可循环调取，总量不限制积分：用户积2000积分可调取，单位分钟有流控，积分越高流量越大，请自行提高积分，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | TS股票代码 |
| pre_close | float | N | 昨日收盘价 |
| up_limit | float | Y | 涨停价 |
| down_limit | float | Y | 跌停价 |

## 调用示例

```python
pro = ts.pro_api()

#获取单日全部股票数据涨跌停价格
df = pro.stk_limit(trade_date='20190625')

#获取单个股票数据
df = pro.stk_limit(ts_code='002149.SZ', start_date='20190115', end_date='20190615')
```
# Tushare债券数据

# 可转债基本信息

**路径**: 债券专题
**接口**: `cb_basic`
**积分**: 2000
**描述**: 获取可转债基本信息限量：单次最大2000，总量不限制权限：用户需要至少2000积分才可以调取，但有流量控制，5000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法
**限量**: 单次最大2000，总量不限制权限：用户需要至少2000积分才可以调取，但有流量控制，5000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 转债代码 |
| list_date | str | N | 上市日期 |
| exchange | str | N | 上市地点 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 转债代码 |
| bond_full_name | str | Y | 转债名称 |
| bond_short_name | str | Y | 转债简称 |
| cb_code | str | Y | 转股申报代码 |
| stk_code | str | Y | 正股代码 |
| stk_short_name | str | Y | 正股简称 |
| maturity | float | Y | 发行期限（年） |
| par | float | Y | 面值 |
| issue_price | float | Y | 发行价格 |
| issue_size | float | Y | 发行总额（元） |
| remain_size | float | Y | 债券余额（元） |
| value_date | str | Y | 起息日期 |
| maturity_date | str | Y | 到期日期 |
| rate_type | str | Y | 利率类型 |
| coupon_rate | float | Y | 票面利率（%） |
| add_rate | float | Y | 补偿利率（%） |
| pay_per_year | int | Y | 年付息次数 |
| list_date | str | Y | 上市日期 |
| delist_date | str | Y | 摘牌日 |
| exchange | str | Y | 上市地点 |
| conv_start_date | str | Y | 转股起始日 |
| conv_end_date | str | Y | 转股截止日 |
| conv_stop_date | str | Y | 停止转股日(提前到期) |
| first_conv_price | float | Y | 初始转股价 |
| conv_price | float | Y | 最新转股价 |
| rate_clause | str | Y | 利率说明 |
| put_clause | str | N | 赎回条款 |
| maturity_put_price | str | N | 到期赎回价格(含税) |
| call_clause | str | N | 回售条款 |
| reset_clause | str | N | 特别向下修正条款 |
| conv_clause | str | N | 转股条款 |
| guarantor | str | N | 担保人 |
| guarantee_type | str | N | 担保方式 |
| issue_rating | str | N | 发行信用等级 |
| newest_rating | str | N | 最新信用等级 |
| rating_comp | str | N | 最新评级机构 |

## 调用示例

```python
pro = ts.pro_api(your token)
#获取可转债基础信息列表
df = pro.cb_basic(fields="ts_code,bond_short_name,stk_code,stk_short_name,list_date,delist_date")
```
# 可转债发行

**路径**: 债券专题
**接口**: `cb_issue`
**积分**: 2000
**描述**: 获取可转债发行数据限量：单次最大2000，可多次提取，总量不限制积分：用户需要至少2000积分才可以调取，5000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法
**限量**: 单次最大2000，可多次提取，总量不限制积分：用户需要至少2000积分才可以调取，5000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码 |
| ann_date | str | N | 发行公告日 |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 转债代码 |
| ann_date | str | Y | 发行公告日 |
| res_ann_date | str | Y | 发行结果公告日 |
| plan_issue_size | float | Y | 计划发行总额（元） |
| issue_size | float | Y | 发行总额（元） |
| issue_price | float | Y | 发行价格 |
| issue_type | str | Y | 发行方式 |
| issue_cost | float | N | 发行费用（元） |
| onl_code | str | Y | 网上申购代码 |
| onl_name | str | Y | 网上申购简称 |
| onl_date | str | Y | 网上发行日期 |
| onl_size | float | Y | 网上发行总额（张） |
| onl_pch_vol | float | Y | 网上发行有效申购数量（张） |
| onl_pch_num | int | Y | 网上发行有效申购户数 |
| onl_pch_excess | float | Y | 网上发行超额认购倍数 |
| onl_winning_rate | float | N | 网上发行中签率（%） |
| shd_ration_code | str | Y | 老股东配售代码 |
| shd_ration_name | str | Y | 老股东配售简称 |
| shd_ration_date | str | Y | 老股东配售日 |
| shd_ration_record_date | str | Y | 老股东配售股权登记日 |
| shd_ration_pay_date | str | Y | 老股东配售缴款日 |
| shd_ration_price | float | Y | 老股东配售价格 |
| shd_ration_ratio | float | Y | 老股东配售比例 |
| shd_ration_size | float | Y | 老股东配售数量（张） |
| shd_ration_vol | float | N | 老股东配售有效申购数量（张） |
| shd_ration_num | int | N | 老股东配售有效申购户数 |
| shd_ration_excess | float | N | 老股东配售超额认购倍数 |
| offl_size | float | Y | 网下发行总额（张） |
| offl_deposit | float | N | 网下发行定金比例（%） |
| offl_pch_vol | float | N | 网下发行有效申购数量（张） |
| offl_pch_num | int | N | 网下发行有效申购户数 |
| offl_pch_excess | float | N | 网下发行超额认购倍数 |
| offl_winning_rate | float | N | 网下发行中签率 |
| lead_underwriter | str | N | 主承销商 |
| lead_underwriter_vol | float | N | 主承销商包销数量（张） |

## 调用示例

```python
pro = ts.pro_api()


#获取可转债发行数据
df = pro.cb_issue(ann_date='20190612')


#获取可转债发行数据，自定义字段
df = pro.cb_issue(fields='ts_code,ann_date,issue_size')
```
# 可转债行情

**路径**: 债券专题
**接口**: `cb_daily`
**积分**: 2000
**描述**: 获取可转债行情限量：单次最大2000条，可多次提取，总量不限制积分：用户需要至少2000积分才可以调取，5000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法
**限量**: 单次最大2000条，可多次提取，总量不限制积分：用户需要至少2000积分才可以调取，5000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码 |
| trade_date | str | N | 交易日期(YYYYMMDD格式，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 转债代码 |
| trade_date | str | Y | 交易日期 |
| pre_close | float | Y | 昨收盘价(元) |
| open | float | Y | 开盘价(元) |
| high | float | Y | 最高价(元) |
| low | float | Y | 最低价(元) |
| close | float | Y | 收盘价(元) |
| change | float | Y | 涨跌(元) |
| pct_chg | float | Y | 涨跌幅(%) |
| vol | float | Y | 成交量(手) |
| amount | float | Y | 成交金额(万元) |
| bond_value | float | N | 纯债价值 |
| bond_over_rate | float | N | 纯债溢价率(%) |
| cb_value | float | N | 转股价值 |
| cb_over_rate | float | N | 转股溢价率(%) |

## 调用示例

```python
pro = ts.pro_api()


#获取可转债行情
df = pro.cb_daily(trade_date='20190719', fields='ts_code,trade_date, pre_close,open,high,low,close')
```
# 沪深港股通持股明细

**路径**: 股票数据/特色数据
**接口**: `hk_hold`
**积分**: 120
**描述**: 获取沪深港股通持股明细，数据来源港交所。限量：单次最多提取3800条记录，可循环调取，总量不限制积分：用户积120积分可调取试用，2000积分可正常使用，单位分钟有流控，积分越高流量越大，请自行提高积分，具体请参阅积分获取办法
**限量**: 单次最多提取3800条记录，可循环调取，总量不限制积分：用户积120积分可调取试用，2000积分可正常使用，单位分钟有流控，积分越高流量越大，请自行提高积分，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| code | str | N | 交易所代码 |
| ts_code | str | N | TS股票代码 |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| exchange | str | N | 类型：SH沪股通（北向）SZ深股通（北向）HK港股通（南向持股） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| code | str | Y | 原始代码 |
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | TS代码 |
| name | str | Y | 股票名称 |
| vol | int | Y | 持股数量(股) |
| ratio | float | Y | 持股占比（%），占已发行股份百分比 |
| exchange | str | Y | 类型：SH沪股通SZ深股通HK港股通 |

## 调用示例

```python
pro = ts.pro_api()

#获取单日全部持股
df = pro.hk_hold(trade_date='20190625')

#获取单日交易所所有持股
df = pro.hk_hold(trade_date='20190625', exchange='SH')
```
# 期货主力与连续合约

**路径**: 期货数据
**接口**: `fut_mapping`
**积分**: 2000
**描述**: 获取期货主力（或连续）合约与月合约映射数据限量：单次最大2000条，总量不限制积分：用户需要至少2000积分才可以调取，未来可能调整积分，请尽可能多积累积分。具体请参阅积分获取办法
**限量**: 单次最大2000条，总量不限制积分：用户需要至少2000积分才可以调取，未来可能调整积分，请尽可能多积累积分。具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 合约代码 |
| trade_date | str | N | 交易日期(YYYYMMDD格式，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 连续合约代码 |
| trade_date | str | Y | 起始日期 |
| mapping_ts_code | str | Y | 期货合约代码 |

## 调用示例

```python
pro = ts.pro_api()

#获取主力合约TF.CFX每日对应的月合约
df = pro.fut_mapping(ts_code='TF.CFX')
```
# 公募基金列表

**路径**: 公募基金
**接口**: `fund_basic`
**积分**: 2000
**描述**: 获取公募基金数据列表，包括场内和场外基金积分：用户需要2000积分才可以调取，单次最大可以提取15000条数据，5000积分以上权限更高，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 基金代码 |
| market | str | N | 交易市场: E场内 O场外（默认E） |
| status | str | N | 存续状态 D摘牌 I发行 L上市中 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 基金代码 |
| name | str | Y | 简称 |
| management | str | Y | 管理人 |
| custodian | str | Y | 托管人 |
| fund_type | str | Y | 投资类型 |
| found_date | str | Y | 成立日期 |
| due_date | str | Y | 到期日期 |
| list_date | str | Y | 上市时间 |
| issue_date | str | Y | 发行日期 |
| delist_date | str | Y | 退市日期 |
| issue_amount | float | Y | 发行份额(亿) |
| m_fee | float | Y | 管理费 |
| c_fee | float | Y | 托管费 |
| duration_year | float | Y | 存续期 |
| p_value | float | Y | 面值 |
| min_amount | float | Y | 起点金额(万元) |
| exp_return | float | Y | 预期收益率 |
| benchmark | str | Y | 业绩比较基准 |
| status | str | Y | 存续状态D摘牌 I发行 L已上市 |
| invest_type | str | Y | 投资风格 |
| type | str | Y | 基金类型 |
| trustee | str | Y | 受托人 |
| purc_startdate | str | Y | 日常申购起始日 |
| redm_startdate | str | Y | 日常赎回起始日 |
| market | str | Y | E场内O场外 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.fund_basic(market='E')
```
# Tushare港股数据

# 港股列表

**路径**: 港股数据
**接口**: `hk_basic`
**积分**: 2000
**描述**: 获取港股列表信息数量：单次可提取全部在交易的港股列表数据积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码 |
| list_status | str | N | 上市状态 L上市 D退市 P暂停上市 ，默认L |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y |  |
| name | str | Y | 股票简称 |
| fullname | str | Y | 公司全称 |
| enname | str | Y | 英文名称 |
| cn_spell | str | Y | 拼音 |
| market | str | Y | 市场类别 |
| list_status | str | Y | 上市状态 |
| list_date | str | Y | 上市日期 |
| delist_date | str | Y | 退市日期 |
| trade_unit | float | Y | 交易单位 |
| isin | str | Y | ISIN代码 |
| curr_type | str | Y | 货币代码 |

## 调用示例

```python
pro = ts.pro_api()

#获取全部可交易股票基础信息
df = pro.hk_basic()

#获取全部退市股票基础信息
df = pro.hk_basic(list_status='D')
```
# 港股行情

**路径**: 港股数据
**接口**: `hk_daily`
**描述**: 获取港股每日增量和历史行情，每日18点左右更新当日数据限量：单次最大提取5000行记录，可多次提取，总量不限制积分：本接口单独开权限，具体请参阅权限说明
**限量**: 单次最大提取5000行记录，可多次提取，总量不限制积分：本接口单独开权限，具体请参阅权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| open | float | Y | 开盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| close | float | Y | 收盘价 |
| pre_close | float | Y | 昨收价 |
| change | float | Y | 涨跌额 |
| pct_chg | float | Y | 涨跌幅(%) |
| vol | float | Y | 成交量(股) |
| amount | float | Y | 成交额(元) |

## 调用示例

```python
pro = ts.pro_api()

#获取单一股票行情
df = pro.hk_daily(ts_code='00001.HK', start_date='20190101', end_date='20190904')

#获取某一日所有股票
df = pro.hk_daily(trade_date='20190904')
```
# 上市公司管理层

**路径**: 股票数据/基础数据
**接口**: `stk_managers`
**积分**: 2000
**描述**: 获取上市公司管理层积分：用户需要2000积分才可以调取，5000积分以上频次相对较高，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码，支持单个或多个股票输入 |
| ann_date | str | N | 公告日期（YYYYMMDD格式，下同） |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS股票代码 |
| ann_date | str | Y | 公告日期 |
| name | str | Y | 姓名 |
| gender | str | Y | 性别 |
| lev | str | Y | 岗位类别 |
| title | str | Y | 岗位 |
| edu | str | Y | 学历 |
| national | str | Y | 国籍 |
| birthday | str | Y | 出生年月 |
| begin_date | str | Y | 上任日期 |
| end_date | str | Y | 离任日期 |
| resume | str | N | 个人简历 |

## 调用示例

```python
pro = ts.pro_api()

#获取单个公司高管全部数据
df = pro.stk_managers(ts_code='000001.SZ')

#获取多个公司高管全部数据
df = pro.stk_managers(ts_code='000001.SZ,600000.SH')
```
# 管理层薪酬和持股

**路径**: 股票数据/基础数据
**接口**: `stk_rewards`
**积分**: 2000
**描述**: 获取上市公司管理层薪酬和持股积分：用户需要2000积分才可以调取，5000积分以上频次相对较高，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | TS股票代码，支持单个或多个代码输入 |
| end_date | str | N | 报告期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS股票代码 |
| ann_date | str | Y | 公告日期 |
| end_date | str | Y | 截止日期 |
| name | str | Y | 姓名 |
| title | str | Y | 职务 |
| reward | float | Y | 报酬 |
| hold_vol | float | Y | 持股数 |

## 调用示例

```python
pro = ts.pro_api()

#获取单个公司高管全部数据
df = pro.stk_rewards(ts_code='000001.SZ')

#获取多个公司高管全部数据
df = pro.stk_rewards(ts_code='000001.SZ,600000.SH')
```
# 新闻通讯

**路径**: 大模型语料专题数据
**接口**: `major_news`
**描述**: 获取长篇通讯信息，覆盖主要新闻资讯网站，提供超过8年历史新闻。
**限量**: 单次最大400行记录，可循环提取保存到本地。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| src | str | N | 新闻来源（新华网、凤凰财经、同花顺、新浪财经、华尔街见闻、中证网、财新网、第一财经、财联社） |
| start_date | str | N | 新闻发布开始时间，e.g. 2018-11-21 00:00:00 |
| end_date | str | N | 新闻发布结束时间，e.g. 2018-11-22 00:00:00 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| title | str | Y | 标题 |
| content | str | N | 内容 (默认不显示，需要在fields里指定) |
| pub_time | str | Y | 发布时间 |
| src | str | Y | 来源网站 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.major_news(src='新浪财经', start_date='2018-11-21 00:00:00', end_date='2018-11-22 00:00:00')

#提取新闻内容
df = pro.major_news(src='新浪财经', start_date='2018-11-21 00:00:00', end_date='2018-11-22 00:00:00', fields='title,content')
```
# 港股通每日成交统计

**路径**: 股票数据/行情数据
**接口**: `ggt_daily`
**积分**: 2000
**描述**: 获取港股通每日成交信息，数据从2014年开始限量：单次最大1000，总量数据不限制积分：用户积2000积分可调取，5000积分以上频次相对较高，请自行提高积分，具体请参阅积分获取办法
**限量**: 单次最大1000，总量数据不限制积分：用户积2000积分可调取，5000积分以上频次相对较高，请自行提高积分，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期 （格式YYYYMMDD，下同。支持单日和多日输入） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| buy_amount | float | Y | 买入成交金额（亿元） |
| buy_volume | float | Y | 买入成交笔数（万笔） |
| sell_amount | float | Y | 卖出成交金额（亿元） |
| sell_volume | float | Y | 卖出成交笔数（万笔） |

## 调用示例

```python
pro = ts.pro_api()

#获取单日全部统计
df = pro.ggt_daily(trade_date='20190625')

#获取多日统计信息
df = pro.ggt_daily(trade_date='20190925,20180924,20170925')

#获取时间段统计信息
df = pro.ggt_daily(start_date='20180925', end_date='20190925)
```
# 港股通每月成交统计

**路径**: 股票数据/行情数据
**接口**: `ggt_monthly`
**积分**: 1000
**描述**: 港股通每月成交信息，数据从2014年开始限量：单次最大1000积分：用户积5000积分可调取，请自行提高积分，具体请参阅积分获取办法
**限量**: 单次最大1000积分：用户积5000积分可调取，请自行提高积分，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| month | str | N | 月度（格式YYYYMM，下同，支持多个输入） |
| start_month | str | N | 开始月度 |
| end_month | str | N | 结束月度 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| month | str | Y | 交易日期 |
| day_buy_amt | float | Y | 当月日均买入成交金额（亿元） |
| day_buy_vol | float | Y | 当月日均买入成交笔数（万笔） |
| day_sell_amt | float | Y | 当月日均卖出成交金额（亿元） |
| day_sell_vol | float | Y | 当月日均卖出成交笔数（万笔） |
| total_buy_amt | float | Y | 总买入成交金额（亿元） |
| total_buy_vol | float | Y | 总买入成交笔数（万笔） |
| total_sell_amt | float | Y | 总卖出成交金额（亿元） |
| total_sell_vol | float | Y | 总卖出成交笔数（万笔） |

## 调用示例

```python
pro = ts.pro_api()

#获取单月全部统计
df = pro.ggt_monthly(trade_date='201906')

#获取多月统计信息
df = pro.ggt_monthly(trade_date='201906,201907,201709')

#获取时间段统计信息
df = pro.ggt_monthly(start_date='201809', end_date='201908')
```
# 基金复权因子

**路径**: ETF专题
**接口**: `fund_adj`
**积分**: 600
**描述**: 获取基金复权因子，用于计算基金复权行情限量：单次最大提取2000行记录，可循环提取，数据总量不限制积分：用户积600积分可调取，超过5000积分以上频次相对较高。具体请参阅积分获取办法
**限量**: 单次最大提取2000行记录，可循环提取，数据总量不限制积分：用户积600积分可调取，超过5000积分以上频次相对较高。具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS基金代码（支持多只基金输入） |
| trade_date | str | N | 交易日期（格式：yyyymmdd，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| offset | str | N | 开始行数 |
| limit | str | N | 最大行数 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | ts基金代码 |
| trade_date | str | Y | 交易日期 |
| adj_factor | float | Y | 复权因子 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.fund_adj(ts_code='513100.SH', start_date='20190101', end_date='20190926')
```
# 国债收益率曲线

**路径**: 债券专题
**接口**: `yc_cb`
**描述**: 获取中债收益率曲线，目前可获取中债国债收益率曲线即期和到期收益率曲线数据限量：单次最大2000，总量不限制，可循环提取权限：属于单独的权限接口，请在群里联系群主或管理员
**限量**: 单次最大2000，总量不限制，可循环提取权限：属于单独的权限接口，请在群里联系群主或管理员

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 收益率曲线编码：1001.CB-国债收益率曲线 |
| curve_type | str | N | 曲线类型：0-到期，1-即期 |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 查询起始日期 |
| end_date | str | N | 查询结束日期 |
| curve_term | float | N | 期限 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 曲线编码 |
| curve_name | str | Y | 曲线名称 |
| curve_type | str | Y | 曲线类型：0-到期，1-即期 |
| curve_term | float | Y | 期限(年) |
| yield | float | Y | 收益率(%) |

## 调用示例

```python
pro = ts.pro_api(your token)
#获取中债收益率曲线
df = pro.yc_cb(ts_code='1001.CB',curve_type='0',trade_date='20200203')
```
# 基金规模数据

**路径**: 公募基金
**接口**: `fund_share`
**积分**: 2000
**描述**: 获取基金规模数据，包含上海和深圳ETF基金限量：单次最大提取2000行数据积分：用户需要至少2000积分可以调取，5000积分以上频次较高，具体请参阅积分获取办法
**限量**: 单次最大提取2000行数据积分：用户需要至少2000积分可以调取，5000积分以上频次较高，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS基金代码 |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| market | str | N | 市场代码（SH上交所 ，SZ深交所） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 基金代码，支持多只基金同时提取，用逗号分隔 |
| trade_date | str | Y | 交易（变动）日期，格式YYYYMMDD |
| fd_share | float | Y | 基金份额（万） |

## 调用示例

```python
#初始接口
pro = ts.pro_api()

#单只基金
df = pro.fund_share(ts_code='150018.SZ')

#多只基金
df = pro.fund_share(ts_code='150018.SZ,150008.SZ')
```
# 基金经理

**路径**: 公募基金
**接口**: `fund_manager`
**积分**: 500
**描述**: 获取公募基金经理数据，包括基金经理简历等数据限量：单次最大5000，支持分页提取数据积分：用户有500积分可获取数据，2000积分以上可以提高访问频次
**限量**: 单次最大5000，支持分页提取数据积分：用户有500积分可获取数据，2000积分以上可以提高访问频次

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 基金代码，支持多只基金，逗号分隔 |
| ann_date | str | N | 公告日期，格式：YYYYMMDD |
| name | str | N | 基金经理姓名 |
| offset | intint | N | 开始行数 |
| limit | int | N | 每页行数 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 基金代码 |
| ann_date | str | Y | 公告日期 |
| name | str | Y | 基金经理姓名 |
| gender | str | Y | 性别 |
| birth_year | str | Y | 出生年份 |
| edu | str | Y | 学历 |
| nationality | str | Y | 国籍 |
| begin_date | str | Y | 任职日期 |
| end_date | str | Y | 离任日期 |
| resume | str | Y | 简历 |

## 调用示例

```python
#初始接口
pro = ts.pro_api()

#单只基金
df = pro.fund_manager(ts_code='150018.SZ')

#多只基金
df = pro.fund_manager(ts_code='150018.SZ,150008.SZ')
```
# Tushare数据索引

# 国际指数

**路径**: 指数专题
**接口**: `index_global`
**积分**: 6000
**描述**: 获取国际主要指数日线行情限量：单次最大提取4000行情数据，可循环获取，总量不限制积分：用户积6000积分可调取，积分越高频次越高，请自行提高积分，具体请参阅积分获取办法
**限量**: 单次最大提取4000行情数据，可循环获取，总量不限制积分：用户积6000积分可调取，积分越高频次越高，请自行提高积分，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS指数代码 |
| trade_date | str | Y | 交易日 |
| open | float | Y | 开盘点位 |
| close | float | Y | 收盘点位 |
| high | float | Y | 最高点位 |
| low | float | Y | 最低点位 |
| pre_close | float | Y | 昨日收盘点 |
| change | float | Y | 涨跌点位 |
| pct_chg | float | Y | 涨跌幅 |
| swing | float | Y | 振幅 |
| vol | float | Y | 成交量 （大部分无此项数据） |
| amount | float | N | 成交额 （大部分无此项数据） |

## 调用示例

```python
pro = ts.pro_api()

#获取富时中国50指数
df = pro.index_global(ts_code='XIN9', start_date='20200201', end_date='20200220')
```
# 每日停复牌信息

**路径**: 股票数据/行情数据
**接口**: `suspend_d更新时间`
**描述**: 按日期方式获取股票每日停复牌信息

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码(可输入多值) |
| trade_date | str | N | 交易日日期 |
| start_date | str | N | 停复牌查询开始日期 |
| end_date | str | N | 停复牌查询结束日期 |
| suspend_type | str | N | 停复牌类型：S-停牌,R-复牌 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| trade_date | str | Y | 停复牌日期 |
| suspend_timing | str | Y | 日内停牌时间段 |
| suspend_type | str | Y | 停复牌类型：S-停牌，R-复牌 |

## 调用示例

```python
pro = ts.pro_api()

#提取2020-03-12的停牌股票
df = pro.suspend_d(suspend_type='S', trade_date='20200312')
```
# 市场交易统计

**路径**: 指数专题
**接口**: `daily_info`
**积分**: 600
**描述**: 获取交易所股票交易统计，包括各板块明细限量：单次最大4000，可循环获取，总量不限制权限：用户积600积分可调取， 频次有限制，积分越高每分钟调取频次越高，5000积分以上频次相对较高，积分获取方法请参阅积分获取办法
**限量**: 单次最大4000，可循环获取，总量不限制权限：用户积600积分可调取， 频次有限制，积分越高每分钟调取频次越高，5000积分以上频次相对较高，积分获取方法请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 市场代码 |
| ts_name | str | Y | 市场名称 |
| com_count | int | Y | 挂牌数 |
| total_share | float | Y | 总股本（亿股） |
| float_share | float | Y | 流通股本（亿股） |
| total_mv | float | Y | 总市值（亿元） |
| float_mv | float | Y | 流通市值（亿元） |
| amount | float | Y | 交易金额（亿元） |
| vol | float | Y | 成交量（亿股） |
| trans_count | int | Y | 成交笔数（万笔） |
| pe | float | Y | 平均市盈率 |
| tr | float | Y | 换手率（％），注：深交所暂无此列 |
| exchange | str | Y | 交易所（SH上交所 SZ深交所） |

## 调用示例

```python
#获取深圳市场20200320各板块交易数据
df = pro.daily_info(trade_date='20200320', exchange='SZ')

#获取深圳和上海市场20200320各板块交易指定字段的数据
df = pro.daily_info(trade_date='20200320', exchange='SZ,SH', fields='trade_date,ts_name,pe')
```
# 期货主要品种交易周报

**路径**: 期货数据
**接口**: `fut_weekly_detail`
**积分**: 600
**描述**: 获取期货交易所主要品种每周交易统计信息，数据从2010年3月开始权限：600积分可调取，单次最大获取4000行数据，积分越高频次越高，5000积分以上正常调取不受限制数据来源：中国证监会，本数据由Tushare社区成员CE完成规划和采集

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| week | str | N | 周期（每年第几周，e.g. 202001 表示2020第1周） |
| prd | str | N | 期货品种（支持多品种输入，逗号分隔） |
| start_week | str | N | 开始周期 |
| end_week | str | N | 结束周期 |
| exchange | str | N | 交易所（请参考交易所说明） |
| fields | str | N | 提取的字段，e.g. fields='prd,name,vol' |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| exchange | str | Y | 交易所代码 |
| prd | str | Y | 期货品种代码 |
| name | str | Y | 品种名称 |
| vol | int | Y | 成交量（手） |
| vol_yoy | float | Y | 同比增减（%） |
| amount | float | Y | 成交金额（亿元） |
| amout_yoy | float | Y | 同比增减（%） |
| cumvol | int | Y | 年累计成交总量（手） |
| cumvol_yoy | float | Y | 同比增减（%） |
| cumamt | float | Y | 年累计成交金额（亿元） |
| cumamt_yoy | float | Y | 同比增减（%） |
| open_interest | int | Y | 持仓量（手） |
| interest_wow | float | Y | 环比增减（%） |
| mc_close | float | Y | 本周主力合约收盘价 |
| close_wow | float | Y | 环比涨跌（%） |
| week | str | Y | 周期 |
| week_date | str | Y | 周日期 |

## 调用示例

```python
#获取期货铜每周交易统计信息
df = pro.fut_weekly_detail(prd='CU')

#获取期货铜每周交易统计信息
df = pro.fut_weekly_detail(prd='CU', start_week='202001', end_week='202003', fields='prd,name,vol,amount')
```
# 未知接口

**路径**: 宏观经济
# 未知接口

**路径**: 宏观经济/国际宏观
# 国债收益率曲线利率（日频）

**路径**: 宏观经济/国际宏观/美国利率
**接口**: `us_tycr`
**积分**: 120
**描述**: 获取美国每日国债收益率曲线利率限量：单次最大可获取2000条数据权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法
**限量**: 单次最大可获取2000条数据权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期 （YYYYMMDD格式，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| fields | str | N | 指定输出字段（e.g. fields='m1,y1'） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| m1 | float | Y | 1月期 |
| m2 | float | Y | 2月期 |
| m3 | float | Y | 3月期 |
| m4 | float | Y | 4月期（数据从20221019开始） |
| m6 | float | Y | 6月期 |
| y1 | float | Y | 1年期 |
| y2 | float | Y | 2年期 |
| y3 | float | Y | 3年期 |
| y5 | float | Y | 5年期 |
| y7 | float | Y | 7年期 |
| y10 | float | Y | 10年期 |
| y20 | float | Y | 20年期 |
| y30 | float | Y | 30年期 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.us_tycr(start_date='20180101', end_date='20200327')


#获取1月期和1年期数据
df = pro.us_tycr(start_date='20180101', end_date='20200327', fields='m1,y1')
```
# 国债实际收益率曲线利率

**路径**: 宏观经济/国际宏观/美国利率
**接口**: `us_trycr`
**积分**: 120
**描述**: 国债实际收益率曲线利率限量：单次最大可获取2000行数据，可循环获取权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法
**限量**: 单次最大可获取2000行数据，可循环获取权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期 （YYYYMMDD格式，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| fields | str | N | 指定输出字段 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| y5 | float | Y | 5年期 |
| y7 | float | Y | 7年期 |
| y10 | float | Y | 10年期 |
| y20 | float | Y | 20年期 |
| y30 | float | Y | 30年期 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.us_trycr(start_date='20180101', end_date='20200327')


#获取5年期和20年期数据
df = pro.us_trycr(start_date='20180101', end_date='20200327', fields='y5,y20')
```
# 短期国债利率

**路径**: 宏观经济/国际宏观/美国利率
**接口**: `us_tbr`
**积分**: 120
**描述**: 获取美国短期国债利率数据限量：单次最大可获取2000行数据，可循环获取权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法
**限量**: 单次最大可获取2000行数据，可循环获取权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期 |
| start_date | str | N | 开始日期(YYYYMMDD格式) |
| end_date | str | N | 结束日期 |
| fields | str | N | 指定输出字段(e.g. fields='w4_bd,w52_ce') |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| w4_bd | float | Y | 4周银行折现收益率 |
| w4_ce | float | Y | 4周票面利率 |
| w8_bd | float | Y | 8周银行折现收益率 |
| w8_ce | float | Y | 8周票面利率 |
| w13_bd | float | Y | 13周银行折现收益率 |
| w13_ce | float | Y | 13周票面利率 |
| w17_bd | float | Y | 17周银行折现收益率（数据从20221019开始） |
| w17_ce | float | Y | 17周票面利率（数据从20221019开始） |
| w26_bd | float | Y | 26周银行折现收益率 |
| w26_ce | float | Y | 26周票面利率 |
| w52_bd | float | Y | 52周银行折现收益率 |
| w52_ce | float | Y | 52周票面利率 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.us_tbr(start_date='20180101', end_date='20200327')


#获取指定字段数据
df = pro.us_tbr(start_date='20180101', end_date='20200327', fields='w4_bd,w52_ce')
```
# 国债长期利率

**路径**: 宏观经济/国际宏观/美国利率
**接口**: `us_tltr`
**积分**: 120
**描述**: 国债长期利率限量：单次最大可获取2000行数据，可循环获取权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法
**限量**: 单次最大可获取2000行数据，可循环获取权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| fields | str | N | 指定字段 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| ltc | float | Y | 收益率 LT COMPOSITE (>10 Yrs) |
| cmt | float | Y | 20年期CMT利率(TREASURY 20-Yr CMT) |
| e_factor | float | Y | 外推因子EXTRAPOLATION FACTOR |

## 调用示例

```python
pro = ts.pro_api()

df = pro.us_tltr(start_date='20180101', end_date='20200327')


#获取5年期和20年期数据
df = pro.us_tltr(start_date='20180101', end_date='20200327', fields='ltc,cmt')
```
# 国债实际长期利率平均值

**路径**: 宏观经济/国际宏观/美国利率
**接口**: `us_trltr`
**积分**: 120
**描述**: 国债实际长期利率平均值限量：单次最大可获取2000行数据，可循环获取权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法
**限量**: 单次最大可获取2000行数据，可循环获取权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| fields | str | N | 指定字段 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| ltr_avg | float | Y | 实际平均利率LT Real Average (10> Yrs) |

## 调用示例

```python
pro = ts.pro_api()

df = pro.us_trltr(start_date='20180101', end_date='20200327')


#获取指定字段
df = pro.us_trltr(start_date='20180101', end_date='20200327', fields='ltr_avg')
```
# 未知接口

**路径**: 宏观经济
# 未知接口

**路径**: 宏观经济/国内宏观
# 未知接口

**路径**: 宏观经济/国内宏观
# GDP数据

**路径**: 宏观经济/国内宏观/国民经济
**接口**: `cn_gdp`
**积分**: 600
**描述**: 获取国民经济之GDP数据限量：单次最大10000，一次可以提取全部数据权限：用户积累600积分可以使用，具体请参阅积分获取办法
**限量**: 单次最大10000，一次可以提取全部数据权限：用户积累600积分可以使用，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| q | str | N | 季度（2019Q1表示，2019年第一季度） |
| start_q | str | N | 开始季度 |
| end_q | str | N | 结束季度 |
| fields | str | N | 指定输出字段（e.g. fields='quarter,gdp,gdp_yoy'） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| quarter | str | Y | 季度 |
| gdp | float | Y | GDP累计值（亿元） |
| gdp_yoy | float | Y | 当季同比增速（%） |
| pi | float | Y | 第一产业累计值（亿元） |
| pi_yoy | float | Y | 第一产业同比增速（%） |
| si | float | Y | 第二产业累计值（亿元） |
| si_yoy | float | Y | 第二产业同比增速（%） |
| ti | float | Y | 第三产业累计值（亿元） |
| ti_yoy | float | Y | 第三产业同比增速（%） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.cn_gdp(start_q='2018Q1', end_q='2019Q3')


#获取指定字段
df = pro.cn_gdp(start_q='2018Q1', end_q='2019Q3', fields='quarter,gdp,gdp_yoy')
```
# 居民消费价格指数

**路径**: 宏观经济/国内宏观/价格指数
**接口**: `cn_cpi`
**积分**: 600
**描述**: 获取CPI居民消费价格数据，包括全国、城市和农村的数据限量：单次最大5000行，一次可以提取全部数据权限：用户积累600积分可以使用，具体请参阅积分获取办法
**限量**: 单次最大5000行，一次可以提取全部数据权限：用户积累600积分可以使用，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| m | str | N | 月份（YYYYMM，下同），支持多个月份同时输入，逗号分隔 |
| start_m | str | N | 开始月份 |
| end_m | str | N | 结束月份 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| month | str | Y | 月份YYYYMM |
| nt_val | float | Y | 全国当月值 |
| nt_yoy | float | Y | 全国同比（%） |
| nt_mom | float | Y | 全国环比（%） |
| nt_accu | float | Y | 全国累计值 |
| town_val | float | Y | 城市当月值 |
| town_yoy | float | Y | 城市同比（%） |
| town_mom | float | Y | 城市环比（%） |
| town_accu | float | Y | 城市累计值 |
| cnt_val | float | Y | 农村当月值 |
| cnt_yoy | float | Y | 农村同比（%） |
| cnt_mom | float | Y | 农村环比（%） |
| cnt_accu | float | Y | 农村累计值 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.cn_cpi(start_m='201801', end_m='201903')


#获取指定字段
df = pro.cn_cpi(start_q='201801', end_q='201903', fields='month,nt_val,nt_yoy')
```
# 财经日历

**路径**: 债券专题
**接口**: `eco_cal`
**积分**: 2000
**描述**: 获取全球财经日历、包括经济事件数据更新限量：单次最大获取100行数据积分：2000积分可调取
**限量**: 单次最大获取100行数据积分：2000积分可调取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 日期（YYYYMMDD格式） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| currency | str | N | 货币代码 |
| country | str | N | 国家（比如：中国、美国） |
| event | str | N | 事件 （支持模糊匹配： *非农*） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| date | str | Y | 日期 |
| time | str | Y | 时间 |
| currency | str | Y | 货币代码 |
| country | str | Y | 国家 |
| event | str | Y | 经济事件 |
| value | str | Y | 今值 |
| pre_value | str | Y | 前值 |
| fore_value | str | Y | 预测值 |

## 调用示例

```python
pro = ts.pro_api()


#获取指定日期全球经济日历
df = pro.eco_cal(date='20200403')


#获取中国经济事件
df = pro.eco_cal(country='中国')

#获取美国非农数据
df = pro.eco_cal(event='美国季调后非农*', fields='date,time,country,event,value,pre_value,fore_value')
```
# 基础数据

**路径**: 股票数据
# 未知接口

**路径**: 宏观经济/国内宏观
# 未知接口

**路径**: 宏观经济/国内宏观/金融
# 货币供应量

**路径**: 宏观经济/国内宏观/金融/货币供应量
**接口**: `cn_m`
**积分**: 600
**描述**: 获取货币供应量之月度数据限量：单次最大5000，一次可以提取全部数据权限：用户积累600积分可以使用，具体请参阅积分获取办法
**限量**: 单次最大5000，一次可以提取全部数据权限：用户积累600积分可以使用，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| m | str | N | 月度（202001表示，2020年1月） |
| start_m | str | N | 开始月度 |
| end_m | str | N | 结束月度 |
| fields | str | N | 指定输出字段（e.g. fields='month,m0,m1,m2'） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| month | str | Y | 月份YYYYMM |
| m0 | float | Y | M0（亿元） |
| m0_yoy | float | Y | M0同比（%） |
| m0_mom | float | Y | M0环比（%） |
| m1 | float | Y | M1（亿元） |
| m1_yoy | float | Y | M1同比（%） |
| m1_mom | float | Y | M1环比（%） |
| m2 | float | Y | M2（亿元） |
| m2_yoy | float | Y | M2同比（%） |
| m2_mom | float | Y | M2环比（%） |

## 调用示例

```python
pro = ts.pro_api()
df = pro.cn_m(start_m='201901', end_m='202003')
#获取指定字段
df = pro.cn_m(start_m='201901', end_m='202003', fields='month,m0,m1,m2')
```
# 未知接口

**积分**: 1000
# 工业生产者出厂价格指数

**路径**: 宏观经济/国内宏观/价格指数
**接口**: `cn_ppi`
**积分**: 600
**描述**: 获取PPI工业生产者出厂价格指数数据限量：单次最大5000，一次可以提取全部数据权限：用户600积分可以使用，具体请参阅积分获取办法
**限量**: 单次最大5000，一次可以提取全部数据权限：用户600积分可以使用，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| m | str | N | 月份（YYYYMM，下同），支持多个月份同时输入，逗号分隔 |
| start_m | str | N | 开始月份 |
| end_m | str | N | 结束月份 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| month | str | Y | 月份YYYYMM |
| ppi_yoy | float | Y | PPI：全部工业品：当月同比 |
| ppi_mp_yoy | float | Y | PPI：生产资料：当月同比 |
| ppi_mp_qm_yoy | float | Y | PPI：生产资料：采掘业：当月同比 |
| ppi_mp_rm_yoy | float | Y | PPI：生产资料：原料业：当月同比 |
| ppi_mp_p_yoy | float | Y | PPI：生产资料：加工业：当月同比 |
| ppi_cg_yoy | float | Y | PPI：生活资料：当月同比 |
| ppi_cg_f_yoy | float | Y | PPI：生活资料：食品类：当月同比 |
| ppi_cg_c_yoy | float | Y | PPI：生活资料：衣着类：当月同比 |
| ppi_cg_adu_yoy | float | Y | PPI：生活资料：一般日用品类：当月同比 |
| ppi_cg_dcg_yoy | float | Y | PPI：生活资料：耐用消费品类：当月同比 |
| ppi_mom | float | Y | PPI：全部工业品：环比 |
| ppi_mp_mom | float | Y | PPI：生产资料：环比 |
| ppi_mp_qm_mom | float | Y | PPI：生产资料：采掘业：环比 |
| ppi_mp_rm_mom | float | Y | PPI：生产资料：原料业：环比 |
| ppi_mp_p_mom | float | Y | PPI：生产资料：加工业：环比 |
| ppi_cg_mom | float | Y | PPI：生活资料：环比 |
| ppi_cg_f_mom | float | Y | PPI：生活资料：食品类：环比 |
| ppi_cg_c_mom | float | Y | PPI：生活资料：衣着类：环比 |
| ppi_cg_adu_mom | float | Y | PPI：生活资料：一般日用品类：环比 |
| ppi_cg_dcg_mom | float | Y | PPI：生活资料：耐用消费品类：环比 |
| ppi_accu | float | Y | PPI：全部工业品：累计同比 |
| ppi_mp_accu | float | Y | PPI：生产资料：累计同比 |
| ppi_mp_qm_accu | float | Y | PPI：生产资料：采掘业：累计同比 |
| ppi_mp_rm_accu | float | Y | PPI：生产资料：原料业：累计同比 |
| ppi_mp_p_accu | float | Y | PPI：生产资料：加工业：累计同比 |
| ppi_cg_accu | float | Y | PPI：生活资料：累计同比 |
| ppi_cg_f_accu | float | Y | PPI：生活资料：食品类：累计同比 |
| ppi_cg_c_accu | float | Y | PPI：生活资料：衣着类：累计同比 |
| ppi_cg_adu_accu | float | Y | PPI：生活资料：一般日用品类：累计同比 |
| ppi_cg_dcg_accu | float | Y | PPI：生活资料：耐用消费品类：累计同比 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.cn_ppi(start_m='201905', end_m='202005')


#获取指定字段
df = pro.cn_ppi(start_m='201905', end_m='202005', fields='month,ppi_yoy,ppi_mom,ppi_accu')
```
# 可转债转股价变动

**路径**: 债券专题
**接口**: `cb_price_chg`
**描述**: 获取可转债转股价变动限量：单次最大2000，总量不限制权限：本接口需单独开权限（跟积分没关系），具体请参阅积分获取办法
**限量**: 单次最大2000，总量不限制权限：本接口需单独开权限（跟积分没关系），具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 转债代码，支持多值输入 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 转债代码 |
| bond_short_name | str | Y | 转债简称 |
| publish_date | str | Y | 公告日期 |
| change_date | str | Y | 变动日期 |
| convert_price_initial | float | Y | 初始转股价格 |
| convertprice_bef | float | Y | 修正前转股价格 |
| convertprice_aft | float | Y | 修正后转股价格 |

## 调用示例

```python
pro = ts.pro_api(your token)
#获取可转债转股价变动
df = pro.cb_price_chg(ts_code="113556.SH,128114.SZ,128110.SZ",fields="ts_code,bond_short_name,change_date,convert_price_initial,convertprice_bef,convertprice_aft")
```
# 可转债转股结果

**路径**: 债券专题
**接口**: `cb_share`
**积分**: 2000
**描述**: 获取可转债转股结果限量：单次最大2000，总量不限制权限：用户需要至少2000积分才可以调取，但有流量控制，5000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法
**限量**: 单次最大2000，总量不限制权限：用户需要至少2000积分才可以调取，但有流量控制，5000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 转债代码，支持多值输入 |
| ann_date | str | Y | 公告日期（YYYYMMDD格式，下同） |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 债券代码 |
| bond_short_name | str | Y | 债券简称 |
| publish_date | str | Y | 公告日期 |
| end_date | str | Y | 统计截止日期 |
| issue_size | float | Y | 可转债发行总额 |
| convert_price_initial | float | Y | 初始转换价格 |
| convert_price | float | Y | 本次转换价格 |
| convert_val | float | Y | 本次转股金额 |
| convert_vol | float | Y | 本次转股数量 |
| convert_ratio | float | Y | 本次转股比例 |
| acc_convert_val | float | Y | 累计转股金额 |
| acc_convert_vol | float | Y | 累计转股数量 |
| acc_convert_ratio | float | Y | 累计转股比例 |
| remain_size | float | Y | 可转债剩余金额 |
| total_shares | float | Y | 转股后总股本 |

## 调用示例

```python
pro = ts.pro_api(your token)
#获取可转债转股结果
df = pro.cb_share(ts_code="113001.SH,110027.SH",fields="ts_code,end_date,convert_price,convert_val,convert_ratio,acc_convert_ratio")
```
# 基础信息

**路径**: 股票数据/基础数据
**接口**: `stock_basic`
**积分**: 2000
**描述**: 获取基础信息数据，包括股票代码、名称、上市日期、退市日期等权限：2000积分起。此接口是基础信息，调取一次就可以拉取完，建议保存倒本地存储后使用

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS股票代码 |
| name | str | N | 名称 |
| market | str | N | 市场类别 （主板/创业板/科创板/CDR/北交所） |
| list_status | str | N | 上市状态 L上市 D退市 P暂停上市，默认是L |
| exchange | str | N | 交易所 SSE上交所 SZSE深交所 BSE北交所 |
| is_hs | str | N | 是否沪深港通标的，N否 H沪股通 S深股通 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| symbol | str | Y | 股票代码 |
| name | str | Y | 股票名称 |
| area | str | Y | 地域 |
| industry | str | Y | 所属行业 |
| fullname | str | N | 股票全称 |
| enname | str | N | 英文全称 |
| cnspell | str | Y | 拼音缩写 |
| market | str | Y | 市场类型（主板/创业板/科创板/CDR） |
| exchange | str | N | 交易所代码 |
| curr_type | str | N | 交易货币 |
| list_status | str | N | 上市状态 L上市 D退市 P暂停上市 |
| list_date | str | Y | 上市日期 |
| delist_date | str | N | 退市日期 |
| is_hs | str | N | 是否沪深港通标的，N否 H沪股通 S深股通 |
| act_name | str | Y | 实控人名称 |
| act_ent_type | str | Y | 实控人企业性质 |

## 调用示例

```python
pro = ts.pro_api()

#查询当前所有正常上市交易的股票列表

data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
```

```python
#查询当前所有正常上市交易的股票列表

data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
```
# 港股交易日历

**路径**: 港股数据
**接口**: `hk_tradecal`
**积分**: 2000
**描述**: 获取交易日历限量：单次最大2000权限：用户积累2000积分才可调取
**限量**: 单次最大2000权限：用户积累2000积分才可调取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| is_open | str | N | 是否交易 '0'休市 '1'交易 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| cal_date | str | Y | 日历日期 |
| is_open | int | Y | 是否交易 '0'休市 '1'交易 |
| pretrade_date | str | Y | 上一个交易日 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.hk_tradecal(start_date='20200101', end_date='20200708')
```
# 未知接口

# 美股列表

**路径**: 美股数据
**接口**: `us_basic`
**积分**: 120
**描述**: 获取美股列表信息限量：单次最大6000，可分页提取积分：120积分可以试用，5000积分有正式权限
**限量**: 单次最大6000，可分页提取积分：120积分可以试用，5000积分有正式权限

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| classify | str | N | 股票分类 |
| offset | str | N | 开始行数 |
| limit | str | N | 每页最大行数 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 美股代码 |
| name | str | Y | 中文名称 |
| enname | str | N | 英文名称 |
| classify | str | Y | 分类ADR/GDR/EQ |
| list_date | str | Y | 上市日期 |
| delist_date | str | Y | 退市日期 |

## 调用示例

```python
pro = ts.pro_api()

#获取默认美国股票基础信息，单次6000行
df = pro.us_basic()
```
# 美股交易日历

**路径**: 美股数据
**接口**: `us_tradecal`
**描述**: 获取美股交易日历信息限量：单次最大6000，可根据日期阶段获取
**限量**: 单次最大6000，可根据日期阶段获取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| is_open | str | N | 是否交易 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| cal_date | str | Y | 日历日期 |
| is_open | int | Y | 是否交易 '0'休市 '1'交易 |
| pretrade_date | str | Y | 上一个交易日 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.us_tradecal(start_date='20200101', end_date='20200701')
```
# 美股行情

**路径**: 美股数据
**接口**: `us_daily`
**积分**: 120
**描述**: 获取美股行情（未复权），包括全部股票全历史行情，以及重要的市场和估值指标限量：单次最大6000行数据，可根据日期参数循环提取，开通正式权限后也可支持分页提取全部历史要求：120积分可以试用查看数据，开通正式权限请参考权限说明文档。
**限量**: 单次最大6000行数据，可根据日期参数循环提取，开通正式权限后也可支持分页提取全部历史要求：120积分可以试用查看数据，开通正式权限请参考权限说明文档。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码（e.g. AAPL） |
| trade_date | str | N | 交易日期（YYYYMMDD） |
| start_date | str | N | 开始日期（YYYYMMDD） |
| end_date | str | N | 结束日期（YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| close | float | Y | 收盘价 |
| open | float | Y | 开盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| pre_close | float | Y | 昨收价 |
| change | float | N | 涨跌额 |
| pct_change | float | Y | 涨跌幅 |
| vol | float | Y | 成交量 |
| amount | float | Y | 成交额 |
| vwap | float | Y | 平均价 |
| turnover_ratio | float | N | 换手率 |
| total_mv | float | N | 总市值 |
| pe | float | N | PE |
| pb | float | N | PB |

## 调用示例

```python
pro = ts.pro_api()

#获取单一股票行情
df = pro.us_daily(ts_code='AAPL', start_date='20190101', end_date='20190904')

#获取某一日所有股票
df = pro.us_daily(trade_date='20190904')
```
# 备用行情

**路径**: 股票数据/行情数据
**接口**: `bak_daily`
**积分**: 5000
**描述**: 获取备用行情，包括特定的行情指标(数据从2017年中左右开始，早期有几天数据缺失，近期正常)限量：单次最大7000行数据，可以根据日期参数循环获取，正式权限需要5000积分。
**限量**: 单次最大7000行数据，可以根据日期参数循环获取，正式权限需要5000积分。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| offset | str | N | 开始行数 |
| limit | str | N | 最大行数 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| name | str | Y | 股票名称 |
| pct_change | float | Y | 涨跌幅 |
| close | float | Y | 收盘价 |
| change | float | Y | 涨跌额 |
| open | float | Y | 开盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| pre_close | float | Y | 昨收价 |
| vol_ratio | float | Y | 量比 |
| turn_over | float | Y | 换手率 |
| swing | float | Y | 振幅 |
| vol | float | Y | 成交量 |
| amount | float | Y | 成交额 |
| selling | float | Y | 内盘（主动卖，手） |
| buying | float | Y | 外盘（主动买， 手） |
| total_share | float | Y | 总股本(亿) |
| float_share | float | Y | 流通股本(亿) |
| pe | float | Y | 市盈(动) |
| industry | str | Y | 所属行业 |
| area | str | Y | 所属地域 |
| float_mv | float | Y | 流通市值 |
| total_mv | float | Y | 总市值 |
| avg_price | float | Y | 平均价 |
| strength | float | Y | 强弱度(%) |
| activity | float | Y | 活跃度(%) |
| avg_turnover | float | Y | 笔换手 |
| attack | float | Y | 攻击波(%) |
| interval_3 | float | Y | 近3月涨幅 |
| interval_6 | float | Y | 近6月涨幅 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.bak_daily(trade_date='20211012', fields='trade_date,ts_code,name,close,open')
```
# 债券回购日行情

**路径**: 债券专题
**接口**: `repo_daily`
**积分**: 2000
**描述**: 债券回购日行情限量：单次最大2000条，可多次提取，总量不限制权限：用户需要累积2000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大2000条，可多次提取，总量不限制权限：用户需要累积2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码 |
| trade_date | str | N | 交易日期(YYYYMMDD格式，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| trade_date | str | Y | 交易日期 |
| repo_maturity | str | Y | 期限品种 |
| pre_close | float | Y | 前收盘(%) |
| open | float | Y | 开盘价(%) |
| high | float | Y | 最高价(%) |
| low | float | Y | 最低价(%) |
| close | float | Y | 收盘价(%) |
| weight | float | Y | 加权价(%) |
| weight_r | float | Y | 加权价(利率债)(%) |
| amount | float | Y | 成交金额(万元) |
| num | int | Y | 成交笔数(笔) |

## 调用示例

```python
pro = ts.pro_api()

#获取2020年8月4日债券回购日行情
df = pro.repo_daily(trade_date='20200804')
```
# 同花顺概念和行业指数

**路径**: 股票数据/打板专题数据
**接口**: `ths_index`
**积分**: 6000
**描述**: 获取同花顺板块指数。注：数据版权归属同花顺，如做商业用途，请主动联系同花顺，如需帮助请联系微信：waditu_a权限：本接口需有6000积分，单次最大返回5000行数据，一次可提取全部数据，请勿循环提取。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 指数代码 |
| exchange | str | N | 市场类型A-a股 HK-港股 US-美股 |
| type | str | N | 指数类型 N-概念指数 I-行业指数 R-地域指数 S-同花顺特色指数 ST-同花顺风格指数 TH-同花顺主题指数 BB-同花顺宽基指数 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 代码 |
| name | str | Y | 名称 |
| count | int | Y | 成分个数 |
| exchange | str | Y | 交易所 |
| list_date | str | Y | 上市日期 |
| type | str | Y | N概念指数S特色指数 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.ths_index()
```
# 交易日历

**路径**: 股票数据/基础数据
**接口**: `trade_cal`
**积分**: 2000
**描述**: 获取各大交易所交易日历数据,默认提取的是上交所积分：需2000积分

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| exchange | str | N | 交易所 SSE上交所,SZSE深交所,CFFEX 中金所,SHFE 上期所,CZCE 郑商所,DCE 大商所,INE 上能源 |
| start_date | str | N | 开始日期 （格式：YYYYMMDD 下同） |
| end_date | str | N | 结束日期 |
| is_open | str | N | 是否交易 '0'休市 '1'交易 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| exchange | str | Y | 交易所 SSE上交所 SZSE深交所 |
| cal_date | str | Y | 日历日期 |
| is_open | str | Y | 是否交易 0休市 1交易 |
| pretrade_date | str | Y | 上一个交易日 |

## 调用示例

```python
pro = ts.pro_api()


df = pro.trade_cal(exchange='', start_date='20180101', end_date='20181231')
```

```python
df = pro.query('trade_cal', start_date='20180101', end_date='20181231')
```
# 同花顺板块指数行情

**路径**: 股票数据/打板专题数据
**接口**: `ths_daily`
**积分**: 6000
**描述**: 获取同花顺板块指数行情。注：数据版权归属同花顺，如做商业用途，请主动联系同花顺，如需帮助请联系微信：waditu_a限量：单次最大3000行数据（需6000积分），可根据指数代码、日期参数循环提取。
**限量**: 单次最大3000行数据（需6000积分），可根据指数代码、日期参数循环提取。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 指数代码 |
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS指数代码 |
| trade_date | str | Y | 交易日 |
| close | float | Y | 收盘点位 |
| open | float | Y | 开盘点位 |
| high | float | Y | 最高点位 |
| low | float | Y | 最低点位 |
| pre_close | float | Y | 昨日收盘点 |
| avg_price | float | Y | 平均价 |
| change | float | Y | 涨跌点位 |
| pct_change | float | Y | 涨跌幅 |
| vol | float | Y | 成交量 |
| turnover_rate | float | Y | 换手率 |
| total_mv | float | N | 总市值 |
| float_mv | float | N | 流通市值 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.ths_daily(ts_code='865001.TI', start_date='20200101', end_date='20210101', fields='ts_code,trade_date,open,close,high,low,pct_change')
```
# 同花顺概念板块成分

**路径**: 股票数据/打板专题数据
**接口**: `ths_member`
**积分**: 5000
**描述**: 获取同花顺概念板块成分列表注：数据版权归属同花顺，如做商业用途，请主动联系同花顺。限量：用户积累5000积分可调取，每分钟可调取200次，可按概念板块代码循环提取所有成分
**限量**: 用户积累5000积分可调取，每分钟可调取200次，可按概念板块代码循环提取所有成分

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 板块指数代码 |
| con_code | str | N | 股票代码 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 指数代码 |
| con_code | str | Y | 股票代码 |
| con_name | str | Y | 股票名称 |
| weight | float | N | 权重(暂无) |
| in_date | str | N | 纳入日期(暂无) |
| out_date | str | N | 剔除日期(暂无) |
| is_new | str | N | 是否最新Y是N否 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.ths_member(ts_code='885800.TI')
```
# 股票历史列表（历史每天股票列表）

**路径**: 股票数据/基础数据
**接口**: `bak_basic`
**积分**: 5000
**描述**: 获取备用基础列表，数据从2016年开始限量：单次最大7000条，可以根据日期参数循环获取历史，正式权限需要5000积分。
**限量**: 单次最大7000条，可以根据日期参数循环获取历史，正式权限需要5000积分。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期 |
| ts_code | str | N | 股票代码 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | TS股票代码 |
| name | str | Y | 股票名称 |
| industry | str | Y | 行业 |
| area | str | Y | 地域 |
| pe | float | Y | 市盈率（动） |
| float_share | float | Y | 流通股本（亿） |
| total_share | float | Y | 总股本（亿） |
| total_assets | float | Y | 总资产（亿） |
| liquid_assets | float | Y | 流动资产（亿） |
| fixed_assets | float | Y | 固定资产（亿） |
| reserved | float | Y | 公积金 |
| reserved_pershare | float | Y | 每股公积金 |
| eps | float | Y | 每股收益 |
| bvps | float | Y | 每股净资产 |
| pb | float | Y | 市净率 |
| list_date | str | Y | 上市日期 |
| undp | float | Y | 未分配利润 |
| per_undp | float | Y | 每股未分配利润 |
| rev_yoy | float | Y | 收入同比（%） |
| profit_yoy | float | Y | 利润同比（%） |
| gpr | float | Y | 毛利率（%） |
| npr | float | Y | 净利润率（%） |
| holder_num | int | Y | 股东人数 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.bak_basic(trade_date='20211012', fields='trade_date,ts_code,name,industry,pe')
```
# 财务管理类数据

# 基金销售行业数据

**路径**: 财富管理
# 各渠道公募基金销售保有规模占比

**路径**: 财富管理/基金销售行业数据
**接口**: `fund_sales_ratio`
**描述**: 获取各渠道公募基金销售保有规模占比数据，年度更新限量：单次最大100行数据，数据从2015年开始公布，当前数据量很小
**限量**: 单次最大100行数据，数据从2015年开始公布，当前数据量很小

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| 年份 | str | N | 年度 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| year | int | Y | 年度 |
| bank | float | Y | 商业银行（%） |
| sec_comp | float | Y | 证券公司（%） |
| fund_comp | float | Y | 基金公司直销（%） |
| indep_comp | float | Y | 独立基金销售机构（%） |
| rests | float | Y | 其他（%） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.fund_sales_ratio()
```
# 销售机构公募基金销售保有规模

**路径**: 财富管理/基金销售行业数据
**接口**: `fund_sales_vol`
**描述**: 获取销售机构公募基金销售保有规模数据，本数据从2021年Q1开始公布，季度更新限量：单次最大500行数据，目前总量只有100行，未来随着数据量增加会提高上限
**限量**: 单次最大500行数据，目前总量只有100行，未来随着数据量增加会提高上限

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| year | str | N | 年度 |
| quarter | str | N | 季度 |
| name | str | N | 机构名称 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| year | int | Y | 年度 |
| quarter | str | Y | 季度 |
| inst_name | str | Y | 销售机构 |
| fund_scale | float | Y | 股票+混合公募基金保有规模（亿元） |
| scale | float | Y | 非货币市场公募基金保有规模（亿元） |
| rank | int | Y | 排名 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.fund_sales_vol()
```
# 券商每月荐股

**路径**: 股票数据/特色数据
**接口**: `broker_recommend`
**描述**: 获取券商月度金股，一般1日~3日内更新当月数据限量：单次最大1000行数据，可循环提取积分：积分达到6000即可调用，具体请参阅积分获取办法
**限量**: 单次最大1000行数据，可循环提取积分：积分达到6000即可调用，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| month | str | Y | 月度（YYYYMM） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| month | str | Y | 月度 |
| broker | str | Y | 券商 |
| ts_code | str | Y | 股票代码 |
| name | str | Y | 股票简称 |

## 调用示例

```python
#获取查询月份券商金股
df = pro.broker_recommend(month='202106')
```
# 深圳市场每日交易概况

**路径**: 指数专题
**接口**: `sz_daily_info`
**积分**: 2000
**描述**: 获取深圳市场每日交易概况限量：单次最大2000，可循环获取，总量不限制权限：用户积2000积分可调取， 频次有限制，积分越高每分钟调取频次越高，5000积分以上频次相对较高，积分获取方法请参阅积分获取办法
**限量**: 单次最大2000，可循环获取，总量不限制权限：用户积2000积分可调取， 频次有限制，积分越高每分钟调取频次越高，5000积分以上频次相对较高，积分获取方法请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同） |
| ts_code | str | N | 板块代码 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y |  |
| ts_code | str | Y | 市场类型 |
| count | int | Y | 股票个数 |
| amount | float | Y | 成交金额 |
| vol | None | Y | 成交量 |
| total_share | float | Y | 总股本 |
| total_mv | float | Y | 总市值 |
| float_share | float | Y | 流通股票 |
| float_mv | float | Y | 流通市值 |

## 调用示例

```python
#获取深圳市场20200320交易数据
df = pro.sz_daily_info(trade_date='20200320')

#获取深圳市场交易情况
df = pro.sz_daily_info(trade_date='20200320', ts_code='股票')
```
# 可转债赎回信息

**路径**: 债券专题
**接口**: `cb_call`
**积分**: 5000
**描述**: 获取可转债到期赎回、强制赎回等信息。数据来源于公开披露渠道，供个人和机构研究使用，请不要用于数据商业目的。限量：单次最大2000条数据，可以根据日期循环提取，本接口需5000积分。
**限量**: 单次最大2000条数据，可以根据日期循环提取，本接口需5000积分。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 转债代码，支持多值输入 |
| ann_date | str | N | 公告日期(YYYYMMDD格式，下同) |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 转债代码 |
| call_type | str | Y | 赎回类型：到赎、强赎 |
| is_call | str | Y | 是否赎回：已满足强赎条件、公告提示强赎、公告实施强赎、公告到期赎回、公告不强赎 |
| ann_date | str | Y | 公告/提示日期 |
| call_date | str | Y | 赎回日期 |
| call_price | float | Y | 赎回价格(含税，元/张) |
| call_price_tax | float | Y | 赎回价格(扣税，元/张) |
| call_vol | float | Y | 赎回债券数量(张) |
| call_amount | float | Y | 赎回金额(万元) |
| payment_date | str | Y | 行权后款项到账日 |
| call_reg_date | str | Y | 赎回登记日 |

## 调用示例

```python
pro = ts.pro_api('your token')

#获取可转债行情
df = pro.cb_call(fields='ts_code,call_type,is_call,ann_date,call_date,call_price')
```
# A股日线行情

**路径**: 股票数据/行情数据
**接口**: `daily`
**描述**: 获取股票行情数据，或通过通用行情接口获取数据，包含了前后复权数据

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码（支持多个股票同时提取，逗号分隔） |
| trade_date | str | N | 交易日期（YYYYMMDD） |
| start_date | str | N | 开始日期(YYYYMMDD) |
| end_date | str | N | 结束日期(YYYYMMDD) |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | 股票代码 |
| trade_date | str | 交易日期 |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 收盘价 |
| pre_close | float | 昨收价【除权价，前复权】 |
| change | float | 涨跌额 |
| pct_chg | float | 涨跌幅 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收 】 |
| vol | float | 成交量 （手） |
| amount | float | 成交额 （千元） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.daily(ts_code='000001.SZ', start_date='20180701', end_date='20180718')

#多个股票
df = pro.daily(ts_code='000001.SZ,600000.SH', start_date='20180701', end_date='20180718')
```

```python
df = pro.query('daily', ts_code='000001.SZ', start_date='20180701', end_date='20180718')
```

```python
df = pro.daily(trade_date='20180810')
```
# 未知接口

# 债券大宗交易

**路径**: 债券专题
**接口**: `bond_blk`
**积分**: 5000
**描述**: 获取沪深交易所债券大宗交易数据，可以通过数据工具调试和查看数据。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 债券代码 |
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 债券代码 |
| name | str | Y | 债券名称 |
| price | float | Y | 成交价（元） |
| vol | float | Y | 累计成交数量（万股/万份/万张/万手） |
| amount | float | Y | 累计成交金额（万元） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.bond_blk(start_date='20210701', end_date='20210930')
```
# 大宗交易明细

**路径**: 债券专题
**接口**: `bond_blk_detail`
**积分**: 5000
**描述**: 获取沪深交易所债券大宗交易数据，可以通过数据工具调试和查看数据。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 债券代码 |
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 债券代码 |
| name | str | Y | 债券名称 |
| price | float | Y | 成交价（元） |
| vol | float | Y | 成交数量（万股/万份/万张/万手） |
| amount | float | Y | 成交金额（万元） |
| buy_dp | str | Y | 买方营业部 |
| sell_dp | str | Y | 卖方营业部 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.bond_blk_detail(start_date='20210701', end_date='20210930')
```
# 中央结算系统持股明细

**路径**: 股票数据/特色数据
**接口**: `ccass_hold_detail`
**积分**: 8000
**描述**: 获取中央结算系统机构席位持股明细，数据覆盖全历史，根据交易所披露时间，当日数据在下一交易日早上9点前完成限量：单次最大返回6000条数据，可以循环或分页提取积分：用户积8000积分可调取，每分钟可以请求300次
**限量**: 单次最大返回6000条数据，可以循环或分页提取积分：用户积8000积分可调取，每分钟可以请求300次

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 (e.g. 605009.SH) |
| hk_code | str | N | 港交所代码 （e.g. 95009） |
| trade_date | str | N | 交易日期(YYYYMMDD格式，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 股票代号 |
| name | str | Y | 股票名称 |
| col_participant_id | str | Y | 参与者编号 |
| col_participant_name | str | Y | 机构名称 |
| col_shareholding | str | Y | 持股量(股) |
| col_shareholding_percent | str | Y | 占已发行股份/权证/单位百分比(%) |

## 调用示例

```python
pro = ts.pro_api()

df = pro.ccass_hold_detail(ts_code='00960.HK', trade_date='20211101', fields='trade_date,ts_code,col_participant_id,col_participant_name,col_shareholding')
```
# 机构调研表

**路径**: 股票数据/特色数据
**接口**: `stk_surv`
**积分**: 5000
**描述**: 获取上市公司机构调研记录数据限量：单次最大获取100条数据，可循环或分页提取积分：用户积5000积分可使用
**限量**: 单次最大获取100条数据，可循环或分页提取积分：用户积5000积分可使用

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 调研日期 |
| start_date | str | N | 调研开始日期 |
| end_date | str | N | 调研结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| name | str | Y | 股票名称 |
| surv_date | str | Y | 调研日期 |
| fund_visitors | str | Y | 机构参与人员 |
| rece_place | str | Y | 接待地点 |
| rece_mode | str | Y | 接待方式 |
| rece_org | str | Y | 接待的公司 |
| org_type | str | Y | 接待公司类型 |
| comp_rece | str | Y | 上市公司接待人员 |
| content | None | N | 调研内容 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.stk_surv(ts_code='002223.SZ', trade_date='20211024', fields='ts_code,name,surv_date,fund_visitors,rece_place,rece_mode,rece_org')
```
# 复权因子

**路径**: 股票数据/行情数据
**接口**: `adj_factor`
**积分**: 2000
**描述**: 本接口由Tushare自行生产，获取股票复权因子，可提取单只股票全部历史复权因子，也可以提取单日全部股票的复权因子。积分要求：2000积分起，5000以上可高频调取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期(YYYYMMDD，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | 股票代码 |
| trade_date | str | 交易日期 |
| adj_factor | float | 复权因子 |

## 调用示例

```python
pro = ts.pro_api()

#提取000001全部复权因子
df = pro.adj_factor(ts_code='000001.SZ', trade_date='')


#提取2018年7月18日复权因子
df = pro.adj_factor(ts_code='', trade_date='20180718')
```

```python
df = pro.query('adj_factor',  trade_date='20180718')
```
# 现货数据

# 黄金现货基础信息

**路径**: 现货数据
**接口**: `sge_basic`
**积分**: 5000
**描述**: 获取上海黄金交易所现货合约基础信息限量：单次最大100条，当前现货合约数不足20个，可以一次提取全部，不需要循环提取积分：用户积5000积分可以调取，具体请参阅积分获取办法
**限量**: 单次最大100条，当前现货合约数不足20个，可以一次提取全部，不需要循环提取积分：用户积5000积分可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 合约代码 （支持多个，逗号分隔，不输入为获取全部） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 品种代码 |
| ts_name | str | Y | 品种名称 |
| trade_type | str | Y | 交易类型 |
| t_unit | float | Y | 交易单位(克/手) |
| p_unit | float | Y | 报价单位 |
| min_change | float | Y | 最小变动价位 |
| price_limit | float | Y | 每日价格最大波动限制 |
| min_vol | int | Y | 最小单笔报价量(手) |
| max_vol | int | Y | 最大单笔报价量(手) |
| trade_mode | str | Y | 交易期限 |
| margin_rate | float | Y | 保证金比例 |
| liq_rate | float | Y | 违约金比例(%) |
| trade_time | str | Y | 交易时间 |
| list_date | str | Y | 上市日期 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.sge_basic()
```

```python
df = pro.sge_basic(ts_code='Au99.95')
```
# 现货黄金日行情

**路径**: 现货数据
**接口**: `sge_daily`
**积分**: 2000
**描述**: 获取上海黄金交易所现货合约日线行情限量：单次最大2000，可循环或者分页提取积分：用户积2000积分可调取，具体请参阅积分获取办法
**限量**: 单次最大2000，可循环或者分页提取积分：用户积2000积分可调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 合约代码，可通过基础信息获得 |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 现货合约代码 |
| trade_date | str | Y | 交易日 |
| close | float | Y | 收盘点(元/克) |
| open | float | Y | 开盘点(元/克) |
| high | float | Y | 最高点(元/克) |
| low | float | Y | 最低点(元/克) |
| price_avg | float | Y | 加权平均价(元/克) |
| change | float | Y | 涨跌点位(元/克) |
| pct_change | float | Y | 涨跌幅 |
| vol | float | Y | 成交量(千克) |
| amount | float | Y | 成交金额(元) |
| oi | float | Y | 市场持仓 |
| settle_vol | float | Y | 交收量 |
| settle_dire | str | Y | 持仓方向 |

## 调用示例

```python
pro = ts.pro_api()

#获取单日统计数据
df = pro.sge_daily(trade_date='20220311')

#获取某合约指定日期，指定字段输出的数据
df = pro.sge_daily(ts_code='', start_date='20220301', end_date='20220311', fields='ts_code,close,open,vol')
```
# 未知接口

**路径**: 股票数据
**积分**: 2000
# 卖方盈利预测数据

**路径**: 股票数据/特色数据
**接口**: `report_rc`
**积分**: 120
**描述**: 获取券商（卖方）每天研报的盈利预测数据，数据从2010年开始，每晚19~22点更新当日数据限量：单次最大3000条，可分页和循环提取所有数据权限：本接口120积分可以试用，每天10次请求，正式权限需8000积分，每天可请求100000次，10000积分以上无总量限制。
**限量**: 单次最大3000条，可分页和循环提取所有数据权限：本接口120积分可以试用，每天10次请求，正式权限需8000积分，每天可请求100000次，10000积分以上无总量限制。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| report_date | str | N | 报告日期 |
| start_date | str | N | 报告开始日期 |
| end_date | str | N | 报告结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| name | str | Y | 股票名称 |
| report_date | str | Y | 研报日期 |
| report_title | str | Y | 报告标题 |
| report_type | str | Y | 报告类型 |
| classify | str | Y | 报告分类 |
| org_name | str | Y | 机构名称 |
| author_name | str | Y | 作者 |
| quarter | str | Y | 预测报告期 |
| op_rt | float | Y | 预测营业收入（万元） |
| op_pr | float | Y | 预测营业利润（万元） |
| tp | float | Y | 预测利润总额（万元） |
| np | float | Y | 预测净利润（万元） |
| eps | float | Y | 预测每股收益（元） |
| pe | float | Y | 预测市盈率 |
| rd | float | Y | 预测股息率 |
| roe | float | Y | 预测净资产收益率 |
| ev_ebitda | float | Y | 预测EV/EBITDA |
| rating | str | Y | 卖方评级 |
| max_price | float | Y | 预测最高目标价 |
| min_price | float | Y | 预测最低目标价 |
| imp_dg | str | N | 机构关注度 |
| create_time | datetime | N | TS数据更新时间 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.report_rc(ts_code='', report_date='20220429')
```
# 每日筹码及胜率

**路径**: 股票数据/特色数据
**接口**: `cyq_perf`
**积分**: 5000
**描述**: 获取A股每日筹码平均成本和胜率情况，每天17~18点左右更新，数据从2018年开始
**限量**: 单次最大5000条，可以分页或者循环提取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | N | 交易日期（YYYYMMDD） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| his_low | float | Y | 历史最低价 |
| his_high | float | Y | 历史最高价 |
| cost_5pct | float | Y | 5分位成本 |
| cost_15pct | float | Y | 15分位成本 |
| cost_50pct | float | Y | 50分位成本 |
| cost_85pct | float | Y | 85分位成本 |
| cost_95pct | float | Y | 95分位成本 |
| weight_avg | float | Y | 加权平均成本 |
| winner_rate | float | Y | 胜率 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.cyq_perf(ts_code='600000.SH', start_date='20220101', end_date='20220429')
```
# 每日筹码分布

**路径**: 股票数据/特色数据
**接口**: `cyq_chips`
**积分**: 5000
**描述**: 获取A股每日的筹码分布情况，提供各价位占比，数据从2018年开始，每天17~18点之间更新当日数据
**限量**: 单次最大2000条，可以按股票代码和日期循环提取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | N | 交易日期（YYYYMMDD） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| price | float | Y | 成本价格 |
| percent | float | Y | 价格占比（%） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.cyq_chips(ts_code='600000.SH', start_date='20220101', end_date='20220429')
```
# 中央结算系统持股汇总

**路径**: 股票数据/特色数据
**接口**: `ccass_hold`
**积分**: 120
**描述**: 获取中央结算系统持股汇总数据，覆盖全部历史数据，根据交易所披露时间，当日数据在下一交易日早上9点前完成入库限量：单次最大5000条数据，可循环或分页提供全部积分：用户120积分可以试用看数据，5000积分每分钟可以请求300次，8000积分以上可以请求500次每分钟，具体请参阅积分获取办法
**限量**: 单次最大5000条数据，可循环或分页提供全部积分：用户120积分可以试用看数据，5000积分每分钟可以请求300次，8000积分以上可以请求500次每分钟，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 (e.g. 605009.SH) |
| hk_code | str | N | 港交所代码 （e.g. 95009） |
| trade_date | str | N | 交易日期(YYYYMMDD格式，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 股票代号 |
| name | str | Y | 股票名称 |
| shareholding | str | Y | 于中央结算系统的持股量(股)Shareholding in CCASS |
| hold_nums | str | Y | 参与者数目（个） |
| hold_ratio | str | Y | 占于上交所上市及交易的A股总数的百分比（%）% of the total number of A shares listed and traded on the SSE |

## 调用示例

```python
pro = ts.pro_api()

df = pro.ccass_hold(ts_code='00960.HK')
```
# 股票技术因子（量化因子）

**路径**: 股票数据/特色数据
**接口**: `stk_factor`
**积分**: 5000
**描述**: 获取股票每日技术面因子数据，用于跟踪股票当前走势情况，数据由Tushare社区自产，覆盖全历史限量：单次最大10000条，可以循环或者分页提取积分：5000积分每分钟可以请求100次，8000积分以上每分钟500次，具体请参阅积分获取办法
**限量**: 单次最大10000条，可以循环或者分页提取积分：5000积分每分钟可以请求100次，8000积分以上每分钟500次，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期 （yyyymmdd，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| close | float | Y | 收盘价 |
| open | float | Y | 开盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| pre_close | float | Y | 昨收价 |
| change | float | Y | 涨跌额 |
| pct_change | float | Y | 涨跌幅 |
| vol | float | Y | 成交量 （手） |
| amount | float | Y | 成交额 （千元） |
| adj_factor | float | Y | 复权因子 |
| open_hfq | float | Y | 开盘价后复权 |
| open_qfq | float | Y | 开盘价前复权 |
| close_hfq | float | Y | 收盘价后复权 |
| close_qfq | float | Y | 收盘价前复权 |
| high_hfq | float | Y | 最高价后复权 |
| high_qfq | float | Y | 最高价前复权 |
| low_hfq | float | Y | 最低价后复权 |
| low_qfq | float | Y | 最低价前复权 |
| pre_close_hfq | float | Y | 昨收价后复权 |
| pre_close_qfq | float | Y | 昨收价前复权 |
| macd_dif | float | Y | MCAD_DIF (基于前复权价格计算，下同) |
| macd_dea | float | Y | MCAD_DEA |
| macd | float | Y | MCAD |
| kdj_k | float | Y | KDJ_K |
| kdj_d | float | Y | KDJ_D |
| kdj_j | float | Y | KDJ_J |
| rsi_6 | float | Y | RSI_6 |
| rsi_12 | float | Y | RSI_12 |
| rsi_24 | float | Y | RSI_24 |
| boll_upper | float | Y | BOLL_UPPER |
| boll_mid | float | Y | BOLL_MID |
| boll_lower | float | Y | BOLL_LOWER |
| cci | float | Y | CCI |

## 调用示例

```python
pro = ts.pro_api()

df = pro.stk_factor(ts_code='600000.SH', start_date='20220501', end_date='20220520', fields='ts_code,trade_date,macd,kdj_k,kdj_d,kdj_j')
```
# 涨跌停列表（新）

**路径**: 股票数据/打板专题数据
**接口**: `limit_list_d`
**积分**: 5000
**描述**: 获取A股每日涨跌停、炸板数据情况，数据从2020年开始（不提供ST股票的统计）限量：单次最大可以获取2500条数据，可通过日期或者股票循环提取积分：5000积分每分钟可以请求200次每天总量1万次，8000积分以上每分钟500次每天总量不限制，具体请参阅积分获取办法
**限量**: 单次最大可以获取2500条数据，可通过日期或者股票循环提取积分：5000积分每分钟可以请求200次每天总量1万次，8000积分以上每分钟500次每天总量不限制，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期 |
| ts_code | str | N | 股票代码 |
| limit_type | str | N | 涨跌停类型（U涨停D跌停Z炸板） |
| exchange | str | N | 交易所（SH上交所SZ深交所BJ北交所） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 股票代码 |
| industry | str | Y | 所属行业 |
| name | str | Y | 股票名称 |
| close | float | Y | 收盘价 |
| pct_chg | float | Y | 涨跌幅 |
| amount | float | Y | 成交额 |
| limit_amount | float | Y | 板上成交金额(成交价格为该股票跌停价的所有成交额的总和，涨停无此数据) |
| float_mv | float | Y | 流通市值 |
| total_mv | float | Y | 总市值 |
| turnover_ratio | float | Y | 换手率 |
| fd_amount | float | Y | 封单金额（以涨停价买入挂单的资金总量） |
| first_time | str | Y | 首次封板时间（跌停无此数据） |
| last_time | str | Y | 最后封板时间 |
| open_times | int | Y | 炸板次数(跌停为开板次数) |
| up_stat | str | Y | 涨停统计（N/T T天有N次涨停） |
| limit_times | int | Y | 连板数（个股连续封板数量） |
| limit | str | Y | D跌停U涨停Z炸板 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.limit_list_d(trade_date='20220615', limit_type='U', fields='ts_code,trade_date,industry,name,close,pct_chg,open_times,up_stat,limit_times')
```
# 港股分钟行情

**路径**: 港股数据
**接口**: `hk_mins`
**积分**: 120
**描述**: 港股分钟数据，支持1min/5min/15min/30min/60min行情，提供Python SDK和 http Restful API两种方式限量：单次最大8000行数据，可以通过股票代码和日期循环获取权限：120积分可以调取2次接口查看数据，正式权限请参阅 权限说明  。
**限量**: 单次最大8000行数据，可以通过股票代码和日期循环获取权限：120积分可以调取2次接口查看数据，正式权限请参阅 权限说明  。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码，e.g.00001.HK |
| freq | str | Y | 分钟频度（1min/5min/15min/30min/60min） |
| start_date | datetime | N | 开始日期 格式：2023-03-13 09:00:00 |
| end_date | datetime | N | 结束时间 格式：2023-03-13 19:00:00 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_time | str | Y | 交易时间 |
| open | float | Y | 开盘价 |
| close | float | Y | 收盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| vol | int | Y | 成交量 |
| amount | float | Y | 成交金额 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.hk_mins(ts_code='00001.HK', freq='1min', start_date='2023-03-13 09:00:00', end_date='2023-03-13 19:00:00')
```
# 可转债票面利率

**路径**: 债券专题
**接口**: `cb_rate`
**积分**: 5000
**描述**: 获取可转债票面利率限量：单次最大2000，总量不限制权限：用户需要至少5000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大2000，总量不限制权限：用户需要至少5000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 转债代码，支持多值输入 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 转债代码 |
| rate_freq | int | N | 付息频率(次/年) |
| rate_start_date | str | N | 付息开始日期 |
| rate_end_date | str | N | 付息结束日期 |
| coupon_rate | float | N | 票面利率(%) |

## 调用示例

```python
pro = ts.pro_api(your token)
#获取可转债基础信息列表
df = pro.cb_rate(ts_code='123046.SZ,127064.SZ',fields="ts_code,rate_freq,rate_start_date,rate_end_date,coupon_rate")
```
# 中信行业指数行情

**路径**: 指数专题
**接口**: `ci_daily`
**积分**: 5000
**描述**: 获取中信行业指数日线行情限量：单次最大4000条，可循环提取积分：5000积分可调取，可通过指数代码和日期参数循环获取所有数据
**限量**: 单次最大4000条，可循环提取积分：5000积分可调取，可通过指数代码和日期参数循环获取所有数据

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 行业代码 |
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 指数代码 |
| trade_date | str | Y | 交易日期 |
| open | float | Y | 开盘点位 |
| low | float | Y | 最低点位 |
| high | float | Y | 最高点位 |
| close | float | Y | 收盘点位 |
| pre_close | float | Y | 昨日收盘点位 |
| change | float | Y | 涨跌点位 |
| pct_change | float | Y | 涨跌幅 |
| vol | float | Y | 成交量（万股） |
| amount | float | Y | 成交额（万元） |

## 调用示例

```python
pro = ts.pro_api('your token')

df = pro.ci_daily(trade_date='20230705', fields='ts_code,trade_date,open,low,high,close')
```
# 未知接口

**路径**: 宏观经济/国内宏观/金融
# 社融数据（月度）

**路径**: 宏观经济/国内宏观/金融/社会融资
**接口**: `sf_month`
**积分**: 2000
**描述**: 获取月度社会融资数据限量：单次最大2000条数据，可循环提取积分：需2000积分
**限量**: 单次最大2000条数据，可循环提取积分：需2000积分

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| m | str | N | 月份（YYYYMM，下同），支持多个月份同时输入，逗号分隔 |
| start_m | str | N | 开始月份 |
| end_m | str | N | 结束月份 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| month | str | Y | 月度 |
| inc_month | float | Y | 社融增量当月值（亿元） |
| inc_cumval | float | Y | 社融增量累计值（亿元） |
| stk_endval | float | Y | 社融存量期末值（万亿元） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.sf_month(start_m='201901', end_m='202307')
```
# 游资名录

**路径**: 股票数据/打板专题数据
**接口**: `hm_list`
**积分**: 500
**描述**: 获取游资分类名录信息限量：单次最大1000条数据，目前总量未超过500积分：5000积分可以调取，积分获取办法请参阅积分获取办法
**限量**: 单次最大1000条数据，目前总量未超过500积分：5000积分可以调取，积分获取办法请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| name | str | N | 游资名称 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| name | str | Y | 游资名称 |
| desc | str | Y | 说明 |
| orgs | None | Y | 关联机构 |

## 调用示例

```python
#代码示例
pro = ts.pro_api()

df = pro.hm_list()
```
# 游资每日明细

**路径**: 股票数据/打板专题数据
**接口**: `hm_detail`
**积分**: 10000
**描述**: 获取每日游资交易明细，数据开始于2022年8。游资分类名录，请点击游资名录限量：单次最多提取2000条记录，可循环调取，总量不限制积分：用户积10000积分可调取使用，积分获取办法请参阅积分获取办法
**限量**: 单次最多提取2000条记录，可循环调取，总量不限制积分：用户积10000积分可调取使用，积分获取办法请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期(YYYYMMDD) |
| ts_code | str | N | 股票代码 |
| hm_name | str | N | 游资名称 |
| start_date | str | N | 开始日期(YYYYMMDD) |
| end_date | str | N | 结束日期(YYYYMMDD) |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 股票代码 |
| ts_name | str | Y | 股票名称 |
| buy_amount | float | Y | 买入金额（元） |
| sell_amount | float | Y | 卖出金额（元） |
| net_amount | float | Y | 净买卖（元） |
| hm_name | str | Y | 游资名称 |
| hm_orgs | str | Y | 关联机构（一般为营业部或机构专用） |
| tag | str | N | 标签 |

## 调用示例

```python
pro = ts.pro_api()

#获取单日全部明细
df = pro.hm_detail(trade_date='20230815')
```
# 期货历史分钟行情

**路径**: 期货数据
**接口**: `ft_mins`
**积分**: 120
**描述**: 获取全市场期货合约分钟数据，支持1min/5min/15min/30min/60min行情，提供Python SDK和 http Restful API两种方式，如果需要主力合约分钟，请先通过主力mapping接口获取对应的合约代码后提取分钟。限量：单次最大8000行数据，可以通过期货合约代码和时间循环获取，本接口可以提供超过10年历史分钟数据。权限：120积分可以调取2次接口查看数据，正式权限请参阅 权限说明  。
**限量**: 单次最大8000行数据，可以通过期货合约代码和时间循环获取，本接口可以提供超过10年历史分钟数据。权限：120积分可以调取2次接口查看数据，正式权限请参阅 权限说明  。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码，e.g.CU2310.SHF |
| freq | str | Y | 分钟频度（1min/5min/15min/30min/60min） |
| start_date | datetime | N | 开始日期 格式：2023-08-25 09:00:00 |
| end_date | datetime | N | 结束时间 格式：2023-08-25 19:00:00 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_time | str | Y | 交易时间 |
| open | float | Y | 开盘价（元） |
| close | float | Y | 收盘价（元） |
| high | float | Y | 最高价（元） |
| low | float | Y | 最低价（元） |
| vol | int | Y | 成交量（手） |
| amount | float | Y | 成交金额（元） |
| oi | float | Y | 持仓量（手） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.df = pro.ft_mins(ts_code='CU2310.SHF', freq='1min', start_date='2023-08-25 09:00:00', end_date='2023-08-25 19:00:00')
```
# 期货Tick行情数据

**路径**: 期货数据
# 实时盘口TICK快照(爬虫版)

**路径**: 股票数据/行情数据
**接口**: `realtime_quote`
**描述**: 本接口是tushare org版实时接口的顺延，数据来自网络，且不进入tushare服务器，属于爬虫接口，请将tushare升级到1.3.3版本以上。权限：0积分完全开放，但需要有tushare账号，如果没有账号请先注册。说明：由于该接口是纯爬虫程序，跟tushare服务器无关，因此tushare不对数据内容和质量负责。数据主要用于研究和学习使用，如做商业目的，请自行解决合规问题。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
|  |  |  | 支持多个多个股票同时输入，举例：ts_code='600000.SH,000001.SZ'），一次最多不能超过50个股票 |
|  |  |  | 只支持单个股票提取 |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| name | str | 股票名称 |
| ts_code | str | 股票代码 |
| date | str | 交易日期 |
| time | str | 交易时间 |
| open | float | 开盘价 |
| pre_close | float | 昨收价 |
| price | float | 现价 |
| high | float | 今日最高价 |
| low | float | 今日最低价 |
| bid | float | 竞买价，即“买一”报价（元） |
| ask | float | 竞卖价，即“卖一”报价（元） |
| volume | int | 成交量（src=sina时是股，src=dc时是手） |
| amount | float | 成交金额（元 CNY） |
| b1_v | float | 委买一（量，单位：手，下同） |
| b1_p | float | 委买一（价，单位：元，下同） |
| b2_v | float | 委买二（量） |
| b2_p | float | 委买二（价） |
| b3_v | float | 委买三（量） |
| b3_p | float | 委买三（价） |
| b4_v | float | 委买四（量） |
| b4_p | float | 委买四（价） |
| b5_v | float | 委买五（量） |
| b5_p | float | 委买五（价） |
| a1_v | float | 委卖一（量，单位：手，下同） |
| a1_p | float | 委卖一（价，单位：元，下同） |
| a2_v | float | 委卖二（量） |
| a2_p | float | 委卖二（价） |
| a3_v | float | 委卖三（量） |
| a3_p | float | 委卖三（价） |
| a4_v | float | 委卖四（量） |
| a4_p | float | 委卖四（价） |
| a5_v | float | 委卖五（量） |
| a5_p | float | 委卖五（价） |
# 实时成交数据(爬虫版)

**路径**: 股票数据/行情数据
**接口**: `realtime_tick`
**描述**: 本接口是tushare org版实时接口的顺延，数据来自网络，且不进入tushare服务器，属于爬虫接口，数据包括该股票当日开盘以来的所有分笔成交数据。权限：0积分完全开放，但需要有tushare账号，如果没有账号请先注册。说明：由于该接口是纯爬虫程序，跟tushare服务器无关，因此tushare不对数据内容和质量负责。数据主要用于研究和学习使用，如做商业目的，请自行解决合规问题。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码，需按tushare股票代码标准输入，比如：000001.SZ表示平安银行，600000.SH表示浦发银行，单次只能输入一个股票 |
| src | str | N | 数据源 （sina-新浪 dc-东方财富，默认sina） |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| time | str | 交易时间 |
| price | float | 现价 |
| change | float | 价格变动 |
| volume | int | 成交量（单位：手） |
| amount | int | 成交金额（元） |
| type | str | 类型：买入/卖出/中性 |
# 实时涨跌幅排名(爬虫版)

**路径**: 股票数据/行情数据
**接口**: `realtime_list`
**描述**: 本接口是tushare org版实时接口的顺延，数据来自网络，且不进入tushare服务器，属于爬虫接口，数据包括该股票当日开盘以来的所有分笔成交数据。权限：0积分完全开放，但需要有tushare账号，如果没有账号请先注册。说明：由于该接口是纯爬虫程序，跟tushare服务器无关，因此tushare不对数据内容和质量负责。数据主要用于研究和学习使用，如做商业目的，请自行解决合规问题。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| src | str | N | 数据源 （sina-新浪 dc-东方财富，默认dc） |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | 股票代码 |
| name | str | 股票名称 |
| price | float | 当前价格 |
| pct_change | float | 涨跌幅 |
| change | float | 涨跌额 |
| buy | float | 买入价 |
| sale | float | 卖出价 |
| close | float | 今日收盘价 |
| open | float | 今日开盘价 |
| high | float | 今日最高价 |
| low | float | 今日最低价 |
| volume | int | 成交量（单位：股） |
| amount | int | 成交金额（元） |
| time | str | 当前时间 |
# 每日指标

**路径**: 股票数据/行情数据
**接口**: `daily_basic`
**积分**: 2000
**描述**: 获取全部股票每日重要的基本面指标，可用于选股分析、报表展示等。单次请求最大返回6000条数据，可按日线循环提取全部历史。积分：至少2000积分才可以调取，5000积分无总量限制，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码（二选一） |
| trade_date | str | N | 交易日期 （二选一） |
| start_date | str | N | 开始日期(YYYYMMDD) |
| end_date | str | N | 结束日期(YYYYMMDD) |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | TS股票代码 |
| trade_date | str | 交易日期 |
| close | float | 当日收盘价 |
| turnover_rate | float | 换手率（%） |
| turnover_rate_f | float | 换手率（自由流通股） |
| volume_ratio | float | 量比 |
| pe | float | 市盈率（总市值/净利润， 亏损的PE为空） |
| pe_ttm | float | 市盈率（TTM，亏损的PE为空） |
| pb | float | 市净率（总市值/净资产） |
| ps | float | 市销率 |
| ps_ttm | float | 市销率（TTM） |
| dv_ratio | float | 股息率 （%） |
| dv_ttm | float | 股息率（TTM）（%） |
| total_share | float | 总股本 （万股） |
| float_share | float | 流通股本 （万股） |
| free_share | float | 自由流通股本 （万） |
| total_mv | float | 总市值 （万元） |
| circ_mv | float | 流通市值（万元） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.daily_basic(ts_code='', trade_date='20180726', fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pb')
```

```python
df = pro.query('daily_basic', ts_code='', trade_date='20180726',fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pb')
```
# 同花顺热榜

**路径**: 股票数据/打板专题数据
**接口**: `ths_hot`
**积分**: 5000
**描述**: 获取同花顺App热榜数据，包括热股、概念板块、ETF、可转债、港美股等等，每日盘中提取4次，收盘后4次，最晚22点提取一次。限量：单次最大2000条，可根据日期等参数循环获取全部数据积分：用户积5000积分可调取使用，积分获取办法请参阅积分获取办法注意：本接口只限个人学习和研究使用，如需商业用途，请自行联系同花顺解决数据采购问题。
**限量**: 单次最大2000条，可根据日期等参数循环获取全部数据积分：用户积5000积分可调取使用，积分获取办法请参阅积分获取办法注意：本接口只限个人学习和研究使用，如需商业用途，请自行联系同花顺解决数据采购问题。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期 |
| ts_code | str | N | TS代码 |
| market | str | N | 热榜类型(热股、ETF、可转债、行业板块、概念板块、期货、港股、热基、美股) |
| is_new | str | N | 是否最新（默认Y，如果为N则为盘中和盘后阶段采集，具体时间可参考rank_time字段，状态N每小时更新一次，状态Y更新时间为22：30） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| data_type | str | Y | 数据类型 |
| ts_code | str | Y | 股票代码 |
| ts_name | str | Y | 股票名称 |
| rank | int | Y | 排行 |
| pct_change | float | Y | 涨跌幅% |
| current_price | float | Y | 当前价格 |
| concept | str | Y | 标签 |
| rank_reason | str | Y | 上榜解读 |
| hot | float | Y | 热度值 |
| rank_time | str | Y | 排行榜获取时间 |

## 调用示例

```python
#获取查询月份券商金股
df = pro.ths_hot(trade_date='20240315', market='热股', fields='ts_code,ts_name,hot,concept')
```
# 东方财富热板

**路径**: 股票数据/打板专题数据
**接口**: `dc_hot`
**积分**: 8000
**描述**: 获取东方财富App热榜数据，包括A股市场、ETF基金、港股市场、美股市场等等，每日盘中提取4次，收盘后4次，最晚22点提取一次。限量：单次最大2000条，可根据日期等参数循环获取全部数据积分：用户积8000积分可调取使用，积分获取办法请参阅积分获取办法注意：本接口只限个人学习和研究使用，如需商业用途，请自行联系东方财富解决数据采购问题。
**限量**: 单次最大2000条，可根据日期等参数循环获取全部数据积分：用户积8000积分可调取使用，积分获取办法请参阅积分获取办法注意：本接口只限个人学习和研究使用，如需商业用途，请自行联系东方财富解决数据采购问题。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期 |
| ts_code | str | N | TS代码 |
| market | str | N | 类型(A股市场、ETF基金、港股市场、美股市场) |
| hot_type | str | N | 热点类型(人气榜、飙升榜) |
| is_new | str | N | 是否最新（默认Y，如果为N则为盘中和盘后阶段采集，具体时间可参考rank_time字段，状态N每小时更新一次，状态Y更新时间为22：30） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| data_type | str | Y | 数据类型 |
| ts_code | str | Y | 股票代码 |
| ts_name | str | Y | 股票名称 |
| rank | int | Y | 排行或者热度 |
| pct_change | float | Y | 涨跌幅% |
| current_price | float | Y | 当前价 |
| rank_time | str | Y | 排行榜获取时间 |

## 调用示例

```python
#获取查询月份券商金股
df = pro.dc_hot(trade_date='20240415', market='A股市场',hot_type='人气榜',  fields='ts_code,ts_name,rank')
```
# 柜台流通式债券报价

**路径**: 债券专题
**接口**: `bc_otcqt`
**积分**: 500
**描述**: 柜台流通式债券报价限量：单次最大2000条，可多次提取，总量不限制积分：用户需要至少500积分可以试用调取，2000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法
**限量**: 单次最大2000条，可多次提取，总量不限制积分：用户需要至少500积分可以试用调取，2000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期(YYYYMMDD格式，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| ts_code | str | N | TS代码 |
| bank | str | N | 报价机构 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | N | 报价日期 |
| qt_time | str | N | 报价时间 |
| bank | str | N | 报价机构 |
| ts_code | str | N | 债券编码 |
| name | str | N | 债券简称 |
| maturity | str | N | 期限 |
| remain_maturity | str | N | 剩余期限 |
| bond_type | str | N | 债券类型 |
| coupon_rate | float | N | 票面利率（%） |
| buy_price | float | N | 投资者买入全价 |
| sell_price | float | N | 投资者卖出全价 |
| buy_yield | float | N | 投资者买入到期收益率（%） |
| sell_yield | float | N | 投资者卖出到期收益率（%） |

## 调用示例

```python
pro = ts.pro_api(your token)
#柜台流通式债券报价
df = pro.bc_otcqt(start_date='20240325',end_date='20240329',ts_code='200013.BC',fields='trade_date,qt_time,bank,ts_code,name,remain_maturity,buy_yield,sell_yield')
```
# 柜台流通式债券最优报价

**路径**: 债券专题
**接口**: `bc_bestotcqt`
**积分**: 500
**描述**: 柜台流通式债券最优报价限量：单次最大2000，可多次提取，总量不限制积分：用户需要至少500积分可以试用调取，2000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法
**限量**: 单次最大2000，可多次提取，总量不限制积分：用户需要至少500积分可以试用调取，2000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 报价日期(YYYYMMDD格式，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| ts_code | str | N | TS代码 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | N | 报价日期 |
| ts_code | str | N | 债券编码 |
| name | str | N | 债券简称 |
| remain_maturity | str | N | 剩余期限 |
| bond_type | str | N | 债券类型 |
| best_buy_bank | str | N | 最优报买价方 |
| best_buy_yield | float | N | 投资者最优买入价到期收益率（%） |
| best_buy_price | float | N | 投资者最优买入全价 |
| best_sell_bank | str | N | 最优卖报价方 |
| best_sell_yield | float | N | 投资者最优卖出价到期收益率（%） |
| best_sell_price | float | N | 投资者最优卖出全价 |

## 调用示例

```python
pro = ts.pro_api(your token)
#获取柜台流通式债券最优报价
df = pro.bc_bestotcqt(ts_code='200013.BC',start_date='20240325',end_date='20240329',fields='trade_date,ts_code,name,remain_maturity,best_buy_bank,best_buy_yield,best_sell_bank,best_sell_yield')
```
# 未知接口

**路径**: 宏观经济/国内宏观
# 采购经理人指数

**路径**: 宏观经济/国内宏观/景气度
**接口**: `cn_pmi`
**积分**: 2000
**描述**: 采购经理人指数限量：单次最大2000，一次可以提取全部数据权限：用户积累2000积分可以使用，具体请参阅积分获取办法
**限量**: 单次最大2000，一次可以提取全部数据权限：用户积累2000积分可以使用，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| m | str | N | 月度（202401表示，2024年1月） |
| start_m | str | N | 开始月度 |
| end_m | str | N | 结束月度（e.g. fields='month,pmi010000,pmi010400'） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| month | str | N | 月份YYYYMM |
| pmi010000 | float | N | 制造业PMI |
| pmi010100 | float | N | 制造业PMI:企业规模/大型企业 |
| pmi010200 | float | N | 制造业PMI:企业规模/中型企业 |
| pmi010300 | float | N | 制造业PMI:企业规模/小型企业 |
| pmi010400 | float | N | 制造业PMI:构成指数/生产指数 |
| pmi010401 | float | N | 制造业PMI:构成指数/生产指数:企业规模/大型企业 |
| pmi010402 | float | N | 制造业PMI:构成指数/生产指数:企业规模/中型企业 |
| pmi010403 | float | N | 制造业PMI:构成指数/生产指数:企业规模/小型企业 |
| pmi010500 | float | N | 制造业PMI:构成指数/新订单指数 |
| pmi010501 | float | N | 制造业PMI:构成指数/新订单指数:企业规模/大型企业 |
| pmi010502 | float | N | 制造业PMI:构成指数/新订单指数:企业规模/中型企业 |
| pmi010503 | float | N | 制造业PMI:构成指数/新订单指数:企业规模/小型企业 |
| pmi010600 | float | N | 制造业PMI:构成指数/供应商配送时间指数 |
| pmi010601 | float | N | 制造业PMI:构成指数/供应商配送时间指数:企业规模/大型企业 |
| pmi010602 | float | N | 制造业PMI:构成指数/供应商配送时间指数:企业规模/中型企业 |
| pmi010603 | float | N | 制造业PMI:构成指数/供应商配送时间指数:企业规模/小型企业 |
| pmi010700 | float | N | 制造业PMI:构成指数/原材料库存指数 |
| pmi010701 | float | N | 制造业PMI:构成指数/原材料库存指数:企业规模/大型企业 |
| pmi010702 | float | N | 制造业PMI:构成指数/原材料库存指数:企业规模/中型企业 |
| pmi010703 | float | N | 制造业PMI:构成指数/原材料库存指数:企业规模/小型企业 |
| pmi010800 | float | N | 制造业PMI:构成指数/从业人员指数 |
| pmi010801 | float | N | 制造业PMI:构成指数/从业人员指数:企业规模/大型企业 |
| pmi010802 | float | N | 制造业PMI:构成指数/从业人员指数:企业规模/中型企业 |
| pmi010803 | float | N | 制造业PMI:构成指数/从业人员指数:企业规模/小型企业 |
| pmi010900 | float | N | 制造业PMI:其他/新出口订单 |
| pmi011000 | float | N | 制造业PMI:其他/进口 |
| pmi011100 | float | N | 制造业PMI:其他/采购量 |
| pmi011200 | float | N | 制造业PMI:其他/主要原材料购进价格 |
| pmi011300 | float | N | 制造业PMI:其他/出厂价格 |
| pmi011400 | float | N | 制造业PMI:其他/产成品库存 |
| pmi011500 | float | N | 制造业PMI:其他/在手订单 |
| pmi011600 | float | N | 制造业PMI:其他/生产经营活动预期 |
| pmi011700 | float | N | 制造业PMI:分行业/装备制造业 |
| pmi011800 | float | N | 制造业PMI:分行业/高技术制造业 |
| pmi011900 | float | N | 制造业PMI:分行业/基础原材料制造业 |
| pmi012000 | float | N | 制造业PMI:分行业/消费品制造业 |
| pmi020100 | float | N | 非制造业PMI:商务活动 |
| pmi020101 | float | N | 非制造业PMI:商务活动:分行业/建筑业 |
| pmi020102 | float | N | 非制造业PMI:商务活动:分行业/服务业业 |
| pmi020200 | float | N | 非制造业PMI:新订单指数 |
| pmi020201 | float | N | 非制造业PMI:新订单指数:分行业/建筑业 |
| pmi020202 | float | N | 非制造业PMI:新订单指数:分行业/服务业 |
| pmi020300 | float | N | 非制造业PMI:投入品价格指数 |
| pmi020301 | float | N | 非制造业PMI:投入品价格指数:分行业/建筑业 |
| pmi020302 | float | N | 非制造业PMI:投入品价格指数:分行业/服务业 |
| pmi020400 | float | N | 非制造业PMI:销售价格指数 |
| pmi020401 | float | N | 非制造业PMI:销售价格指数:分行业/建筑业 |
| pmi020402 | float | N | 非制造业PMI:销售价格指数:分行业/服务业 |
| pmi020500 | float | N | 非制造业PMI:从业人员指数 |
| pmi020501 | float | N | 非制造业PMI:从业人员指数:分行业/建筑业 |
| pmi020502 | float | N | 非制造业PMI:从业人员指数:分行业/服务业 |
| pmi020600 | float | N | 非制造业PMI:业务活动预期指数 |
| pmi020601 | float | N | 非制造业PMI:业务活动预期指数:分行业/建筑业 |
| pmi020602 | float | N | 非制造业PMI:业务活动预期指数:分行业/服务业 |
| pmi020700 | float | N | 非制造业PMI:新出口订单 |
| pmi020800 | float | N | 非制造业PMI:在手订单 |
| pmi020900 | float | N | 非制造业PMI:存货 |
| pmi021000 | float | N | 非制造业PMI:供应商配送时间 |
| pmi030000 | float | N | 中国综合PMI:产出指数 |

## 调用示例

```python
pro = ts.pro_api()

#获取指定字段
df = pro.cn_pmi(start_m='201901', end_m='202003', fields='month,pmi010000,pmi010400')
```
# 融资融券标的（盘前更新）

**路径**: 股票数据/两融及转融通
**接口**: `margin_secs`
**积分**: 2000
**描述**: 获取沪深京三大交易所融资融券标的（包括ETF），每天盘前更新限量：单次最大6000行数据，可根据股票代码、交易日期、交易所代码循环提取积分：2000积分可调取，5000积分无总量限制，积分越高权限越大，具体参考权限说明
**限量**: 单次最大6000行数据，可根据股票代码、交易日期、交易所代码循环提取积分：2000积分可调取，5000积分无总量限制，积分越高权限越大，具体参考权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 标的代码 |
| trade_date | str | N | 交易日 |
| exchange | str | N | 交易所（SSE上交所 SZSE深交所 BSE北交所） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 标的代码 |
| name | str | Y | 标的名称 |
| exchange | str | Y | 交易所 |

## 调用示例

```python
pro = ts.pro_api()

#获取2024年4月17日上交所融资融券标的
df = pro.margin_secs(trade_date='20240417', exchange='SSE')
```
# 申万行业日线行情

**路径**: 指数专题
**接口**: `sw_daily`
**积分**: 5000
**描述**: 获取申万行业日线行情（默认是申万2021版行情）限量：单次最大4000行数据，可通过指数代码和日期参数循环提取，5000积分可调取
**限量**: 单次最大4000行数据，可通过指数代码和日期参数循环提取，5000积分可调取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 行业代码 |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 指数代码 |
| trade_date | str | Y | 交易日期 |
| name | str | Y | 指数名称 |
| open | float | Y | 开盘点位 |
| low | float | Y | 最低点位 |
| high | float | Y | 最高点位 |
| close | float | Y | 收盘点位 |
| change | float | Y | 涨跌点位 |
| pct_change | float | Y | 涨跌幅 |
| vol | float | Y | 成交量（万股） |
| amount | float | Y | 成交额（万元） |
| pe | float | Y | 市盈率 |
| pb | float | Y | 市净率 |
| float_mv | float | Y | 流通市值（万元） |
| total_mv | float | Y | 总市值（万元） |

## 调用示例

```python
pro = ts.pro_api('your token')

#获取20230705当日所有申万行业指数的ts_code,name,open,close,vol,pe,pb数据
df = pro.sw_daily(trade_date='20230705', fields='ts_code,name,open,close,vol,pe,pb')
```
# 股票技术面因子(专业版)

**路径**: 股票数据/特色数据
**接口**: `stk_factor_pro`
**积分**: 5000
**描述**: 获取股票每日技术面因子数据，用于跟踪股票当前走势情况，数据由Tushare社区自产，覆盖全历史；输出参数_bfq表示不复权，_qfq表示前复权 _hfq表示后复权，描述中说明了因子的默认传参，如需要特殊参数或者更多因子可以联系管理员评估限量：单次调取最多返回10000条数据，可以通过日期参数循环积分：5000积分每分钟可以请求30次，8000积分以上每分钟500次，具体请参阅积分获取办法
**限量**: 单次调取最多返回10000条数据，可以通过日期参数循环积分：5000积分每分钟可以请求30次，8000积分以上每分钟500次，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期(格式：yyyymmdd，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| open | float | Y | 开盘价 |
| open_hfq | float | Y | 开盘价（后复权） |
| open_qfq | float | Y | 开盘价（前复权） |
| high | float | Y | 最高价 |
| high_hfq | float | Y | 最高价（后复权） |
| high_qfq | float | Y | 最高价（前复权） |
| low | float | Y | 最低价 |
| low_hfq | float | Y | 最低价（后复权） |
| low_qfq | float | Y | 最低价（前复权） |
| close | float | Y | 收盘价 |
| close_hfq | float | Y | 收盘价（后复权） |
| close_qfq | float | Y | 收盘价（前复权） |
| pre_close | float | Y | 昨收价(前复权)--为daily接口的pre_close,以当时复权因子计算值跟前一日close_qfq对不上，可不用 |
| change | float | Y | 涨跌额 |
| pct_chg | float | Y | 涨跌幅 （未复权，如果是复权请用 通用行情接口 ） |
| vol | float | Y | 成交量 （手） |
| amount | float | Y | 成交额 （千元） |
| turnover_rate | float | Y | 换手率（%） |
| turnover_rate_f | float | Y | 换手率（自由流通股） |
| volume_ratio | float | Y | 量比 |
| pe | float | Y | 市盈率（总市值/净利润， 亏损的PE为空） |
| pe_ttm | float | Y | 市盈率（TTM，亏损的PE为空） |
| pb | float | Y | 市净率（总市值/净资产） |
| ps | float | Y | 市销率 |
| ps_ttm | float | Y | 市销率（TTM） |
| dv_ratio | float | Y | 股息率 （%） |
| dv_ttm | float | Y | 股息率（TTM）（%） |
| total_share | float | Y | 总股本 （万股） |
| float_share | float | Y | 流通股本 （万股） |
| free_share | float | Y | 自由流通股本 （万） |
| total_mv | float | Y | 总市值 （万元） |
| circ_mv | float | Y | 流通市值（万元） |
| adj_factor | float | Y | 复权因子 |
| asi_bfq | float | Y | 振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10 |
| asi_hfq | float | Y | 振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10 |
| asi_qfq | float | Y | 振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10 |
| asit_bfq | float | Y | 振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10 |
| asit_hfq | float | Y | 振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10 |
| asit_qfq | float | Y | 振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10 |
| atr_bfq | float | Y | 真实波动N日平均值-CLOSE, HIGH, LOW, N=20 |
| atr_hfq | float | Y | 真实波动N日平均值-CLOSE, HIGH, LOW, N=20 |
| atr_qfq | float | Y | 真实波动N日平均值-CLOSE, HIGH, LOW, N=20 |
| bbi_bfq | float | Y | BBI多空指标-CLOSE, M1=3, M2=6, M3=12, M4=20 |
| bbi_hfq | float | Y | BBI多空指标-CLOSE, M1=3, M2=6, M3=12, M4=21 |
| bbi_qfq | float | Y | BBI多空指标-CLOSE, M1=3, M2=6, M3=12, M4=22 |
| bias1_bfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias1_hfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias1_qfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias2_bfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias2_hfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias2_qfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias3_bfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias3_hfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias3_qfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| boll_lower_bfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_lower_hfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_lower_qfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_mid_bfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_mid_hfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_mid_qfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_upper_bfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_upper_hfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_upper_qfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| brar_ar_bfq | float | Y | BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26 |
| brar_ar_hfq | float | Y | BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26 |
| brar_ar_qfq | float | Y | BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26 |
| brar_br_bfq | float | Y | BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26 |
| brar_br_hfq | float | Y | BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26 |
| brar_br_qfq | float | Y | BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26 |
| cci_bfq | float | Y | 顺势指标又叫CCI指标-CLOSE, HIGH, LOW, N=14 |
| cci_hfq | float | Y | 顺势指标又叫CCI指标-CLOSE, HIGH, LOW, N=14 |
| cci_qfq | float | Y | 顺势指标又叫CCI指标-CLOSE, HIGH, LOW, N=14 |
| cr_bfq | float | Y | CR价格动量指标-CLOSE, HIGH, LOW, N=20 |
| cr_hfq | float | Y | CR价格动量指标-CLOSE, HIGH, LOW, N=20 |
| cr_qfq | float | Y | CR价格动量指标-CLOSE, HIGH, LOW, N=20 |
| dfma_dif_bfq | float | Y | 平行线差指标-CLOSE, N1=10, N2=50, M=10 |
| dfma_dif_hfq | float | Y | 平行线差指标-CLOSE, N1=10, N2=50, M=10 |
| dfma_dif_qfq | float | Y | 平行线差指标-CLOSE, N1=10, N2=50, M=10 |
| dfma_difma_bfq | float | Y | 平行线差指标-CLOSE, N1=10, N2=50, M=10 |
| dfma_difma_hfq | float | Y | 平行线差指标-CLOSE, N1=10, N2=50, M=10 |
| dfma_difma_qfq | float | Y | 平行线差指标-CLOSE, N1=10, N2=50, M=10 |
| dmi_adx_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_adx_hfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_adx_qfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_adxr_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_adxr_hfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_adxr_qfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_mdi_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_mdi_hfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_mdi_qfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_pdi_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_pdi_hfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_pdi_qfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| downdays | float | Y | 连跌天数 |
| updays | float | Y | 连涨天数 |
| dpo_bfq | float | Y | 区间震荡线-CLOSE, M1=20, M2=10, M3=6 |
| dpo_hfq | float | Y | 区间震荡线-CLOSE, M1=20, M2=10, M3=6 |
| dpo_qfq | float | Y | 区间震荡线-CLOSE, M1=20, M2=10, M3=6 |
| madpo_bfq | float | Y | 区间震荡线-CLOSE, M1=20, M2=10, M3=6 |
| madpo_hfq | float | Y | 区间震荡线-CLOSE, M1=20, M2=10, M3=6 |
| madpo_qfq | float | Y | 区间震荡线-CLOSE, M1=20, M2=10, M3=6 |
| ema_bfq_10 | float | Y | 指数移动平均-N=10 |
| ema_bfq_20 | float | Y | 指数移动平均-N=20 |
| ema_bfq_250 | float | Y | 指数移动平均-N=250 |
| ema_bfq_30 | float | Y | 指数移动平均-N=30 |
| ema_bfq_5 | float | Y | 指数移动平均-N=5 |
| ema_bfq_60 | float | Y | 指数移动平均-N=60 |
| ema_bfq_90 | float | Y | 指数移动平均-N=90 |
| ema_hfq_10 | float | Y | 指数移动平均-N=10 |
| ema_hfq_20 | float | Y | 指数移动平均-N=20 |
| ema_hfq_250 | float | Y | 指数移动平均-N=250 |
| ema_hfq_30 | float | Y | 指数移动平均-N=30 |
| ema_hfq_5 | float | Y | 指数移动平均-N=5 |
| ema_hfq_60 | float | Y | 指数移动平均-N=60 |
| ema_hfq_90 | float | Y | 指数移动平均-N=90 |
| ema_qfq_10 | float | Y | 指数移动平均-N=10 |
| ema_qfq_20 | float | Y | 指数移动平均-N=20 |
| ema_qfq_250 | float | Y | 指数移动平均-N=250 |
| ema_qfq_30 | float | Y | 指数移动平均-N=30 |
| ema_qfq_5 | float | Y | 指数移动平均-N=5 |
| ema_qfq_60 | float | Y | 指数移动平均-N=60 |
| ema_qfq_90 | float | Y | 指数移动平均-N=90 |
| emv_bfq | float | Y | 简易波动指标-HIGH, LOW, VOL, N=14, M=9 |
| emv_hfq | float | Y | 简易波动指标-HIGH, LOW, VOL, N=14, M=9 |
| emv_qfq | float | Y | 简易波动指标-HIGH, LOW, VOL, N=14, M=9 |
| maemv_bfq | float | Y | 简易波动指标-HIGH, LOW, VOL, N=14, M=9 |
| maemv_hfq | float | Y | 简易波动指标-HIGH, LOW, VOL, N=14, M=9 |
| maemv_qfq | float | Y | 简易波动指标-HIGH, LOW, VOL, N=14, M=9 |
| expma_12_bfq | float | Y | EMA指数平均数指标-CLOSE, N1=12, N2=50 |
| expma_12_hfq | float | Y | EMA指数平均数指标-CLOSE, N1=12, N2=50 |
| expma_12_qfq | float | Y | EMA指数平均数指标-CLOSE, N1=12, N2=50 |
| expma_50_bfq | float | Y | EMA指数平均数指标-CLOSE, N1=12, N2=50 |
| expma_50_hfq | float | Y | EMA指数平均数指标-CLOSE, N1=12, N2=50 |
| expma_50_qfq | float | Y | EMA指数平均数指标-CLOSE, N1=12, N2=50 |
| kdj_bfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_hfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_qfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_d_bfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_d_hfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_d_qfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_k_bfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_k_hfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_k_qfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| ktn_down_bfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_down_hfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_down_qfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_mid_bfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_mid_hfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_mid_qfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_upper_bfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_upper_hfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_upper_qfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| lowdays | float | Y | LOWRANGE(LOW)表示当前最低价是近多少周期内最低价的最小值 |
| topdays | float | Y | TOPRANGE(HIGH)表示当前最高价是近多少周期内最高价的最大值 |
| ma_bfq_10 | float | Y | 简单移动平均-N=10 |
| ma_bfq_20 | float | Y | 简单移动平均-N=20 |
| ma_bfq_250 | float | Y | 简单移动平均-N=250 |
| ma_bfq_30 | float | Y | 简单移动平均-N=30 |
| ma_bfq_5 | float | Y | 简单移动平均-N=5 |
| ma_bfq_60 | float | Y | 简单移动平均-N=60 |
| ma_bfq_90 | float | Y | 简单移动平均-N=90 |
| ma_hfq_10 | float | Y | 简单移动平均-N=10 |
| ma_hfq_20 | float | Y | 简单移动平均-N=20 |
| ma_hfq_250 | float | Y | 简单移动平均-N=250 |
| ma_hfq_30 | float | Y | 简单移动平均-N=30 |
| ma_hfq_5 | float | Y | 简单移动平均-N=5 |
| ma_hfq_60 | float | Y | 简单移动平均-N=60 |
| ma_hfq_90 | float | Y | 简单移动平均-N=90 |
| ma_qfq_10 | float | Y | 简单移动平均-N=10 |
| ma_qfq_20 | float | Y | 简单移动平均-N=20 |
| ma_qfq_250 | float | Y | 简单移动平均-N=250 |
| ma_qfq_30 | float | Y | 简单移动平均-N=30 |
| ma_qfq_5 | float | Y | 简单移动平均-N=5 |
| ma_qfq_60 | float | Y | 简单移动平均-N=60 |
| ma_qfq_90 | float | Y | 简单移动平均-N=90 |
| macd_bfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_hfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_qfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_dea_bfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_dea_hfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_dea_qfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_dif_bfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_dif_hfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_dif_qfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| mass_bfq | float | Y | 梅斯线-HIGH, LOW, N1=9, N2=25, M=6 |
| mass_hfq | float | Y | 梅斯线-HIGH, LOW, N1=9, N2=25, M=6 |
| mass_qfq | float | Y | 梅斯线-HIGH, LOW, N1=9, N2=25, M=6 |
| ma_mass_bfq | float | Y | 梅斯线-HIGH, LOW, N1=9, N2=25, M=6 |
| ma_mass_hfq | float | Y | 梅斯线-HIGH, LOW, N1=9, N2=25, M=6 |
| ma_mass_qfq | float | Y | 梅斯线-HIGH, LOW, N1=9, N2=25, M=6 |
| mfi_bfq | float | Y | MFI指标是成交量的RSI指标-CLOSE, HIGH, LOW, VOL, N=14 |
| mfi_hfq | float | Y | MFI指标是成交量的RSI指标-CLOSE, HIGH, LOW, VOL, N=14 |
| mfi_qfq | float | Y | MFI指标是成交量的RSI指标-CLOSE, HIGH, LOW, VOL, N=14 |
| mtm_bfq | float | Y | 动量指标-CLOSE, N=12, M=6 |
| mtm_hfq | float | Y | 动量指标-CLOSE, N=12, M=6 |
| mtm_qfq | float | Y | 动量指标-CLOSE, N=12, M=6 |
| mtmma_bfq | float | Y | 动量指标-CLOSE, N=12, M=6 |
| mtmma_hfq | float | Y | 动量指标-CLOSE, N=12, M=6 |
| mtmma_qfq | float | Y | 动量指标-CLOSE, N=12, M=6 |
| obv_bfq | float | Y | 能量潮指标-CLOSE, VOL |
| obv_hfq | float | Y | 能量潮指标-CLOSE, VOL |
| obv_qfq | float | Y | 能量潮指标-CLOSE, VOL |
| psy_bfq | float | Y | 投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6 |
| psy_hfq | float | Y | 投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6 |
| psy_qfq | float | Y | 投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6 |
| psyma_bfq | float | Y | 投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6 |
| psyma_hfq | float | Y | 投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6 |
| psyma_qfq | float | Y | 投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6 |
| roc_bfq | float | Y | 变动率指标-CLOSE, N=12, M=6 |
| roc_hfq | float | Y | 变动率指标-CLOSE, N=12, M=6 |
| roc_qfq | float | Y | 变动率指标-CLOSE, N=12, M=6 |
| maroc_bfq | float | Y | 变动率指标-CLOSE, N=12, M=6 |
| maroc_hfq | float | Y | 变动率指标-CLOSE, N=12, M=6 |
| maroc_qfq | float | Y | 变动率指标-CLOSE, N=12, M=6 |
| rsi_bfq_12 | float | Y | RSI指标-CLOSE, N=12 |
| rsi_bfq_24 | float | Y | RSI指标-CLOSE, N=24 |
| rsi_bfq_6 | float | Y | RSI指标-CLOSE, N=6 |
| rsi_hfq_12 | float | Y | RSI指标-CLOSE, N=12 |
| rsi_hfq_24 | float | Y | RSI指标-CLOSE, N=24 |
| rsi_hfq_6 | float | Y | RSI指标-CLOSE, N=6 |
| rsi_qfq_12 | float | Y | RSI指标-CLOSE, N=12 |
| rsi_qfq_24 | float | Y | RSI指标-CLOSE, N=24 |
| rsi_qfq_6 | float | Y | RSI指标-CLOSE, N=6 |
| taq_down_bfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_down_hfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_down_qfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_mid_bfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_mid_hfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_mid_qfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_up_bfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_up_hfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_up_qfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| trix_bfq | float | Y | 三重指数平滑平均线-CLOSE, M1=12, M2=20 |
| trix_hfq | float | Y | 三重指数平滑平均线-CLOSE, M1=12, M2=20 |
| trix_qfq | float | Y | 三重指数平滑平均线-CLOSE, M1=12, M2=20 |
| trma_bfq | float | Y | 三重指数平滑平均线-CLOSE, M1=12, M2=20 |
| trma_hfq | float | Y | 三重指数平滑平均线-CLOSE, M1=12, M2=20 |
| trma_qfq | float | Y | 三重指数平滑平均线-CLOSE, M1=12, M2=20 |
| vr_bfq | float | Y | VR容量比率-CLOSE, VOL, M1=26 |
| vr_hfq | float | Y | VR容量比率-CLOSE, VOL, M1=26 |
| vr_qfq | float | Y | VR容量比率-CLOSE, VOL, M1=26 |
| wr_bfq | float | Y | W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6 |
| wr_hfq | float | Y | W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6 |
| wr_qfq | float | Y | W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6 |
| wr1_bfq | float | Y | W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6 |
| wr1_hfq | float | Y | W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6 |
| wr1_qfq | float | Y | W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6 |
| xsii_td1_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td1_hfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td1_qfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td2_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td2_hfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td2_qfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td3_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td3_hfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td3_qfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td4_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td4_hfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td4_qfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
# 股本情况（盘前）

**路径**: 股票数据/基础数据
**接口**: `stk_premarket`
**描述**: 每日开盘前获取当日股票的股本情况，包括总股本和流通股本，涨跌停价格等。限量：单次最大8000条数据，可循环提取权限：与积分无关，需单独开权限
**限量**: 单次最大8000条数据，可循环提取权限：与积分无关，需单独开权限

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期(YYYYMMDD格式，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | TS股票代码 |
| total_share | float | Y | 总股本（万股） |
| float_share | float | Y | 流通股本（万股） |
| pre_close | float | Y | 昨日收盘价 |
| up_limit | float | Y | 今日涨停价 |
| down_limit | float | Y | 今日跌停价 |

## 调用示例

```python
pro = ts.pro_api()

#获取某一日盘前所有股票当日的最新股本
df = pro.stk_premarket(trade_date='20240603')
```
# 利润表

**路径**: 股票数据/财务数据
**接口**: `income`
**积分**: 2000
**描述**: 获取上市公司财务利润表数据积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用income_vip接口（参数一致），需积攒5000积分。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| ann_date | str | N | 公告日期（YYYYMMDD格式，下同） |
| f_ann_date | str | N | 实际公告日期 |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |
| period | str | N | 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报) |
| report_type | str | N | 报告类型，参考文档最下方说明 |
| comp_type | str | N | 公司类型（1一般工商业2银行3保险4证券） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| ann_date | str | Y | 公告日期 |
| f_ann_date | str | Y | 实际公告日期 |
| end_date | str | Y | 报告期 |
| report_type | str | Y | 报告类型 见底部表 |
| comp_type | str | Y | 公司类型(1一般工商业2银行3保险4证券) |
| end_type | str | Y | 报告期类型 |
| basic_eps | float | Y | 基本每股收益 |
| diluted_eps | float | Y | 稀释每股收益 |
| total_revenue | float | Y | 营业总收入 |
| revenue | float | Y | 营业收入 |
| int_income | float | Y | 利息收入 |
| prem_earned | float | Y | 已赚保费 |
| comm_income | float | Y | 手续费及佣金收入 |
| n_commis_income | float | Y | 手续费及佣金净收入 |
| n_oth_income | float | Y | 其他经营净收益 |
| n_oth_b_income | float | Y | 加:其他业务净收益 |
| prem_income | float | Y | 保险业务收入 |
| out_prem | float | Y | 减:分出保费 |
| une_prem_reser | float | Y | 提取未到期责任准备金 |
| reins_income | float | Y | 其中:分保费收入 |
| n_sec_tb_income | float | Y | 代理买卖证券业务净收入 |
| n_sec_uw_income | float | Y | 证券承销业务净收入 |
| n_asset_mg_income | float | Y | 受托客户资产管理业务净收入 |
| oth_b_income | float | Y | 其他业务收入 |
| fv_value_chg_gain | float | Y | 加:公允价值变动净收益 |
| invest_income | float | Y | 加:投资净收益 |
| ass_invest_income | float | Y | 其中:对联营企业和合营企业的投资收益 |
| forex_gain | float | Y | 加:汇兑净收益 |
| total_cogs | float | Y | 营业总成本 |
| oper_cost | float | Y | 减:营业成本 |
| int_exp | float | Y | 减:利息支出 |
| comm_exp | float | Y | 减:手续费及佣金支出 |
| biz_tax_surchg | float | Y | 减:营业税金及附加 |
| sell_exp | float | Y | 减:销售费用 |
| admin_exp | float | Y | 减:管理费用 |
| fin_exp | float | Y | 减:财务费用 |
| assets_impair_loss | float | Y | 减:资产减值损失 |
| prem_refund | float | Y | 退保金 |
| compens_payout | float | Y | 赔付总支出 |
| reser_insur_liab | float | Y | 提取保险责任准备金 |
| div_payt | float | Y | 保户红利支出 |
| reins_exp | float | Y | 分保费用 |
| oper_exp | float | Y | 营业支出 |
| compens_payout_refu | float | Y | 减:摊回赔付支出 |
| insur_reser_refu | float | Y | 减:摊回保险责任准备金 |
| reins_cost_refund | float | Y | 减:摊回分保费用 |
| other_bus_cost | float | Y | 其他业务成本 |
| operate_profit | float | Y | 营业利润 |
| non_oper_income | float | Y | 加:营业外收入 |
| non_oper_exp | float | Y | 减:营业外支出 |
| nca_disploss | float | Y | 其中:减:非流动资产处置净损失 |
| total_profit | float | Y | 利润总额 |
| income_tax | float | Y | 所得税费用 |
| n_income | float | Y | 净利润(含少数股东损益) |
| n_income_attr_p | float | Y | 净利润(不含少数股东损益) |
| minority_gain | float | Y | 少数股东损益 |
| oth_compr_income | float | Y | 其他综合收益 |
| t_compr_income | float | Y | 综合收益总额 |
| compr_inc_attr_p | float | Y | 归属于母公司(或股东)的综合收益总额 |
| compr_inc_attr_m_s | float | Y | 归属于少数股东的综合收益总额 |
| ebit | float | Y | 息税前利润 |
| ebitda | float | Y | 息税折旧摊销前利润 |
| insurance_exp | float | Y | 保险业务支出 |
| undist_profit | float | Y | 年初未分配利润 |
| distable_profit | float | Y | 可分配利润 |
| rd_exp | float | Y | 研发费用 |
| fin_exp_int_exp | float | Y | 财务费用:利息费用 |
| fin_exp_int_inc | float | Y | 财务费用:利息收入 |
| transfer_surplus_rese | float | Y | 盈余公积转入 |
| transfer_housing_imprest | float | Y | 住房周转金转入 |
| transfer_oth | float | Y | 其他转入 |
| adj_lossgain | float | Y | 调整以前年度损益 |
| withdra_legal_surplus | float | Y | 提取法定盈余公积 |
| withdra_legal_pubfund | float | Y | 提取法定公益金 |
| withdra_biz_devfund | float | Y | 提取企业发展基金 |
| withdra_rese_fund | float | Y | 提取储备基金 |
| withdra_oth_ersu | float | Y | 提取任意盈余公积金 |
| workers_welfare | float | Y | 职工奖金福利 |
| distr_profit_shrhder | float | Y | 可供股东分配的利润 |
| prfshare_payable_dvd | float | Y | 应付优先股股利 |
| comshare_payable_dvd | float | Y | 应付普通股股利 |
| capit_comstock_div | float | Y | 转作股本的普通股股利 |
| net_after_nr_lp_correct | float | N | 扣除非经常性损益后的净利润（更正前） |
| credit_impa_loss | float | N | 信用减值损失 |
| net_expo_hedging_benefits | float | N | 净敞口套期收益 |
| oth_impair_loss_assets | float | N | 其他资产减值损失 |
| total_opcost | float | N | 营业总成本（二） |
| amodcost_fin_assets | float | N | 以摊余成本计量的金融资产终止确认收益 |
| oth_income | float | N | 其他收益 |
| asset_disp_income | float | N | 资产处置收益 |
| continued_net_profit | float | N | 持续经营净利润 |
| end_net_profit | float | N | 终止经营净利润 |
| update_flag | str | Y | 更新标识 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.income(ts_code='600000.SH', start_date='20180101', end_date='20180730', fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,basic_eps,diluted_eps')
```

```python
df = pro.income_vip(period='20181231',fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,basic_eps,diluted_eps')
```
# 未知接口

**路径**: 股票数据
# 转融资交易汇总

**路径**: 股票数据/两融及转融通
**接口**: `slb_len`
**积分**: 2000
**描述**: 转融通融资汇总限量：单次最大可以提取5000行数据，可循环获取所有历史积分：2000积分每分钟请求200次，5000积分500次请求
**限量**: 单次最大可以提取5000行数据，可循环获取所有历史积分：2000积分每分钟请求200次，5000积分500次请求

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ob | float | Y | 期初余额(亿元) |
| auc_amount | float | Y | 竞价成交金额(亿元) |
| repo_amount | float | Y | 再借成交金额(亿元) |
| repay_amount | float | Y | 偿还金额(亿元) |
| cb | float | Y | 期末余额(亿元) |

## 调用示例

```python
pro = ts.pro_api()

df = pro.slb_len(start_date='20240601', end_date='20240620')
```
# 转融券交易汇总

**路径**: 股票数据/两融及转融通
**接口**: `slb_sec`
**积分**: 2000
**描述**: 转融通转融券交易汇总限量：单次最大可以提取5000行数据，可循环获取所有历史积分：2000积分每分钟请求200次，5000积分500次请求
**限量**: 单次最大可以提取5000行数据，可循环获取所有历史积分：2000积分每分钟请求200次，5000积分500次请求

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同） |
| ts_code | str | N | 股票代码 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期（YYYYMMDD） |
| ts_code | str | Y | 股票代码 |
| name | str | Y | 股票名称 |
| ope_inv | float | Y | 期初余量(万股) |
| lent_qnt | float | Y | 转融券融出数量(万股) |
| cls_inv | float | Y | 期末余量(万股) |
| end_bal | float | Y | 期末余额(万元) |

## 调用示例

```python
pro = ts.pro_api()

df = pro.slb_sec(trade_date='20240620')
```
# 转融券交易明细

**路径**: 股票数据/两融及转融通
**接口**: `slb_sec_detail`
**积分**: 2000
**描述**: 转融券交易明细限量：单次最大可以提取5000行数据，可循环获取所有历史积分：2000积分每分钟请求200次，5000积分500次请求
**限量**: 单次最大可以提取5000行数据，可循环获取所有历史积分：2000积分每分钟请求200次，5000积分500次请求

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同） |
| ts_code | str | N | 股票代码 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期（YYYYMMDD） |
| ts_code | str | Y | 股票代码 |
| name | str | Y | 股票名称 |
| tenor | str | Y | 期 限(天) |
| fee_rate | float | Y | 融出费率(%) |
| lent_qnt | float | Y | 转融券融出数量(万股) |

## 调用示例

```python
pro = ts.pro_api()

df = pro.slb_sec_detail(trade_date='20240620')
```
# 做市借券交易汇总

**路径**: 股票数据/两融及转融通
**接口**: `slb_len_mm`
**积分**: 2000
**描述**: 做市借券交易汇总限量：单次最大可以提取5000行数据，可循环获取所有历史积分：2000积分每分钟请求200次，5000积分500次请求
**限量**: 单次最大可以提取5000行数据，可循环获取所有历史积分：2000积分每分钟请求200次，5000积分500次请求

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同） |
| ts_code | str | N | 股票代码 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期（YYYYMMDD） |
| ts_code | str | Y | 股票代码 |
| name | str | Y | 股票名称 |
| ope_inv | float | Y | 期初余量(万股) |
| lent_qnt | float | Y | 融出数量(万股) |
| cls_inv | float | Y | 期末余量(万股) |
| end_bal | float | Y | 期末余额(万元) |

## 调用示例

```python
pro = ts.pro_api()

df = pro.slb_len_mm(trade_date='20240620')
```
# 申万行业成分构成(分级)

**路径**: 指数专题
**接口**: `index_member_all`
**积分**: 2000
**描述**: 按三级分类提取申万行业成分，可提供某个分类的所有成分，也可按股票代码提取所属分类，参数灵活限量：单次最大2000行，总量不限制权限：用户需2000积分可调取，积分获取方法请参阅积分获取办法
**限量**: 单次最大2000行，总量不限制权限：用户需2000积分可调取，积分获取方法请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| l1_code | str | N | 一级行业代码 |
| l2_code | str | N | 二级行业代码 |
| l3_code | str | N | 三级行业代码 |
| ts_code | str | N | 股票代码 |
| is_new | str | N | 是否最新（默认为“Y是”） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| l1_code | str | Y | 一级行业代码 |
| l1_name | str | Y | 一级行业名称 |
| l2_code | str | Y | 二级行业代码 |
| l2_name | str | Y | 二级行业名称 |
| l3_code | str | Y | 三级行业代码 |
| l3_name | str | Y | 三级行业名称 |
| ts_code | str | Y | 成分股票代码 |
| name | str | Y | 成分股票名称 |
| in_date | str | Y | 纳入日期 |
| out_date | str | Y | 剔除日期 |
| is_new | str | Y | 是否最新Y是N否 |

## 调用示例

```python
#获取黄金分类的成份股
df = pro.index_member_all(l3_code='850531.SI')

#获取000001.SZ所属行业
df = pro.index_member_all(ts_code='000001.SZ')
```
# 股票周/月线行情(每日更新)

**路径**: 股票数据/行情数据
**接口**: `stk_weekly_monthly`
**积分**: 2000
**描述**: 股票周/月线行情(每日更新)限量：单次最大6000,可使用交易日期循环提取，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大6000,可使用交易日期循环提取，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码 |
| trade_date | str | N | 交易日期(格式：YYYYMMDD，每周或每月最后一天的日期） |
| start_date | str | N | 开始交易日期 |
| end_date | str | N | 结束交易日期 |
| freq | str | Y | 频率week周，month月 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| end_date | str | Y | 计算截至日期 |
| freq | str | Y | 频率(周week,月month) |
| open | float | Y | (周/月)开盘价 |
| high | float | Y | (周/月)最高价 |
| low | float | Y | (周/月)最低价 |
| close | float | Y | (周/月)收盘价 |
| pre_close | float | Y | 上一(周/月)收盘价 |
| vol | float | Y | (周/月)成交量 |
| amount | float | Y | (周/月)成交额 |
| change | float | Y | (周/月)涨跌额 |
| pct_chg | float | Y | (周/月)涨跌幅(未复权,如果是复权请用 通用行情接口) |

## 调用示例

```python
pro = ts.pro_api()

#获取20251024这周周线数据
df=pro.stk_weekly_monthly(trade_date='20251024',freq='week')

#获取202510月月线数据
df=pro.stk_weekly_monthly(trade_date='20251031',freq='month')
```
# 期货周/月线行情(每日更新)

**路径**: 期货数据
**接口**: `fut_weekly_monthly`
**描述**: 期货周/月线行情(每日更新)限量：单次最大6000
**限量**: 单次最大6000

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | TS代码 |
| trade_date | str | N | 交易日期 |
| start_date | str | N | 开始交易日期 |
| end_date | str | N | 结束交易日期 |
| freq | str | Y | 频率week周，month月 |
| exchange | str | N | 交易所 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 期货代码 |
| trade_date | str | Y | 交易日期（每周五或者月末日期） |
| end_date | str | Y | 计算截至日期 |
| freq | str | Y | 频率(周week,月month) |
| open | float | Y | (周/月)开盘价 |
| high | float | Y | (周/月)最高价 |
| low | float | Y | (周/月)最低价 |
| close | float | Y | (周/月)收盘价 |
| pre_close | float | Y | 前一(周/月)收盘价 |
| settle | float | Y | (周/月)结算价 |
| pre_settle | float | Y | 前一(周/月)结算价 |
| vol | float | Y | (周/月)成交量(手) |
| amount | float | Y | (周/月)成交金额(万元) |
| oi | float | Y | (周/月)持仓量(手) |
| oi_chg | float | Y | (周/月)持仓量变化 |
| exchange | str | Y | 交易所 |
| change1 | float | Y | (周/月)涨跌1 收盘价-昨结算价 |
| change2 | float | Y | (周/月)涨跌2 结算价-昨结算价 |
# 美股复权行情

**路径**: 美股数据
**接口**: `us_daily_adj`
**积分**: 120
**描述**: 获取美股复权行情，支持美股全市场股票，提供股本、市值、复权因子和成交信息等多个数据指标限量：单次最大可以提取8000条数据，可循环获取全部，支持分页提取要求：120积分可以试用查看数据，开通正式权限请参考权限说明文档
**限量**: 单次最大可以提取8000条数据，可循环获取全部，支持分页提取要求：120积分可以试用查看数据，开通正式权限请参考权限说明文档

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码（e.g. AAPL） |
| trade_date | str | N | 交易日期（YYYYMMDD） |
| start_date | str | N | 开始日期（YYYYMMDD） |
| end_date | str | N | 结束日期（YYYYMMDD） |
| exchange | str | N | 交易所（NAS/NYS/OTC) |
| offset | int | N | 开始行数 |
| limit | int | N | 每页行数行数 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| close | float | Y | 收盘价 |
| open | float | Y | 开盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| pre_close | float | Y | 昨收价 |
| change | float | Y | 涨跌额 |
| pct_change | float | Y | 涨跌幅 |
| vol | int | Y | 成交量 |
| amount | float | Y | 成交额 |
| vwap | float | Y | 平均价 |
| adj_factor | float | Y | 复权因子 |
| turnover_ratio | float | Y | 换手率 |
| free_share | int | Y | 流通股本 |
| total_share | int | Y | 总股本 |
| free_mv | float | Y | 流通市值 |
| total_mv | float | Y | 总市值 |
| exchange | str | Y | 交易所代码 |

## 调用示例

```python
pro = ts.pro_api()

#获取单一股票行情
df = pro.us_daily_adj(ts_code='AAPL', start_date='20240101', end_date='20240722')

#获取某一日某个交易所的全部股票
df = pro.us_daily_adj(trade_date='20240722', exhange='NAS')
```
# 港股复权行情

**路径**: 港股数据
**接口**: `hk_daily_adj`
**积分**: 120
**描述**: 获取港股复权行情，提供股票股本、市值和成交及换手多个数据指标限量：单次最大可以提取6000条数据，可循环获取全部，支持分页提取要求：120积分可以试用查看数据，开通正式权限请参考权限说明文档
**限量**: 单次最大可以提取6000条数据，可循环获取全部，支持分页提取要求：120积分可以试用查看数据，开通正式权限请参考权限说明文档

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码（e.g. 00001.HK） |
| trade_date | str | N | 交易日期（YYYYMMDD） |
| start_date | str | N | 开始日期（YYYYMMDD） |
| end_date | str | N | 结束日期（YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| close | float | Y | 收盘价 |
| open | float | Y | 开盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| pre_close | float | Y | 昨收价 |
| change | float | Y | 涨跌额 |
| pct_change | float | Y | 涨跌幅 |
| vol | None | Y | 成交量 |
| amount | float | Y | 成交额 |
| vwap | float | Y | 平均价 |
| adj_factor | float | Y | 复权因子 |
| turnover_ratio | float | Y | 换手率(基于总股本) |
| free_share | None | Y | 流通股本 |
| total_share | None | Y | 总股本 |
| free_mv | float | Y | 流通市值 |
| total_mv | float | Y | 总市值 |

## 调用示例

```python
pro = ts.pro_api()

#获取单一股票行情
df = pro.hk_daily_adj(ts_code='00001.HK', start_date='20240101', end_date='20240722')

#获取某一日某个交易所的全部股票
df = pro.hk_daily_adj(trade_date='20240722')
```
# 期货实时分钟行情

**路径**: 期货数据
**接口**: `rt_fut_min`
**描述**: 获取全市场期货合约实时分钟数据，支持1min/5min/15min/30min/60min行情，提供Python SDK、 http Restful API和websocket三种方式，如果需要主力合约分钟，请先通过主力mapping接口获取对应的合约代码后提取分钟。限量：每分钟可以请求500次，支持多个合约同时提取权限：需单独开权限，正式权限请参阅 权限说明  。
**限量**: 每分钟可以请求500次，支持多个合约同时提取权限：需单独开权限，正式权限请参阅 权限说明  。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码，e.g.CU2310.SHF，仅支持一次一个合约的回放 |
| freq | str | Y | 分钟频度（1MIN/5MIN/15MIN/30MIN/60MIN） |
| date_str | str | N | 回放日期（格式：YYYY-MM-DD，默认为交易当日，支持回溯一天） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| code | str | Y | 股票代码 |
| freq | str | Y | 频度 |
| time | str | Y | 交易时间 |
| open | float | Y | 开盘价 |
| close | float | Y | 收盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| vol | int | Y | 成交量 |
| amount | float | Y | 成交金额 |
| oi | float | Y | 持仓量 |

## 调用示例

```python
pro = ts.pro_api()

#单个合约
df = pro.df = pro.rt_fut_min(ts_code='CU2501.SHF', freq='1MIN')

#多个合约
df = pro.df = pro.rt_fut_min(ts_code='CU2501.SHF,CU2502.SHF', freq='1MIN')
```
# 期权历史分钟行情

**路径**: 期权数据
**接口**: `opt_mins`
**积分**: 120
**描述**: 获取全市场期权合约分钟数据，支持1min/5min/15min/30min/60min行情，提供Python SDK和 http Restful API两种方式。限量：单次最大8000行数据，可以通过合约代码和时间循环获取。权限：120积分可以调取2次接口查看数据，正式权限请参阅 权限说明  。
**限量**: 单次最大8000行数据，可以通过合约代码和时间循环获取。权限：120积分可以调取2次接口查看数据，正式权限请参阅 权限说明  。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码，e.g：10007976.SH |
| freq | str | Y | 分钟频度（1min/5min/15min/30min/60min） |
| start_date | datetime | N | 开始日期 格式：2024-08-25 09:00:00 |
| end_date | datetime | N | 结束时间 格式：2024-08-25 19:00:00 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_time | str | Y | 交易时间 |
| open | float | Y | 开盘价 |
| close | float | Y | 收盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| vol | int | Y | 成交量 |
| amount | float | Y | 成交金额 |
| oi | float | Y | 持仓量 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.df = pro.opt_mins(ts_code='10007976.SH', freq='1min', start_date='2024-09-27 09:00:00', end_date='2024-09-27 19:00:00')
```
# 未知接口

**路径**: 股票数据
# 同花顺行业资金流向（THS）

**路径**: 股票数据/资金流向数据
**接口**: `moneyflow_ind_ths`
**积分**: 5000
**描述**: 获取同花顺行业资金流向，每日盘后更新限量：单次最大可调取5000条数据，可以根据日期和代码循环提取全部数据积分：5000积分可以调取，具体请参阅积分获取办法
**限量**: 单次最大可调取5000条数据，可以根据日期和代码循环提取全部数据积分：5000积分可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 代码 |
| trade_date | str | N | 交易日期(YYYYMMDD格式，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 板块代码 |
| industry | str | Y | 板块名称 |
| lead_stock | str | Y | 领涨股票名称 |
| close | float | Y | 收盘指数 |
| pct_change | float | Y | 指数涨跌幅 |
| company_num | int | Y | 公司数量 |
| pct_change_stock | float | Y | 领涨股涨跌幅 |
| close_price | float | Y | 领涨股最新价 |
| net_buy_amount | float | Y | 流入资金(亿元) |
| net_sell_amount | float | Y | 流出资金(亿元) |
| net_amount | float | Y | 净额(亿元) |

## 调用示例

```python
#获取当日所有同花顺行业资金流向
df = pro.moneyflow_ind_ths(trade_date='20240927')
```
# 东财概念及行业板块资金流向（DC）

**路径**: 股票数据/资金流向数据
**接口**: `moneyflow_ind_dc`
**积分**: 5000
**描述**: 获取东方财富板块资金流向，每天盘后更新限量：单次最大可调取5000条数据，可以根据日期和代码循环提取全部数据积分：5000积分可以调取，具体请参阅积分获取办法
**限量**: 单次最大可调取5000条数据，可以根据日期和代码循环提取全部数据积分：5000积分可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 代码 |
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| content_type | str | N | 资金类型(行业、概念、地域) |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| content_type | str | Y | 数据类型 |
| ts_code | str | Y | DC板块代码（行业、概念、地域） |
| name | str | Y | 板块名称 |
| pct_change | float | Y | 板块涨跌幅（%） |
| close | float | Y | 板块最新指数 |
| net_amount | float | Y | 今日主力净流入 净额（元） |
| net_amount_rate | float | Y | 今日主力净流入净占比% |
| buy_elg_amount | float | Y | 今日超大单净流入 净额（元） |
| buy_elg_amount_rate | float | Y | 今日超大单净流入 净占比% |
| buy_lg_amount | float | Y | 今日大单净流入 净额（元） |
| buy_lg_amount_rate | float | Y | 今日大单净流入 净占比% |
| buy_md_amount | float | Y | 今日中单净流入 净额（元） |
| buy_md_amount_rate | float | Y | 今日中单净流入 净占比% |
| buy_sm_amount | float | Y | 今日小单净流入 净额（元） |
| buy_sm_amount_rate | float | Y | 今日小单净流入 净占比% |
| buy_sm_amount_stock | str | Y | 今日主力净流入最大股 |
| rank | int | Y | 序号 |

## 调用示例

```python
#获取当日所有板块资金流向
df = pro.moneyflow_ind_dc(trade_date='20240927', fields='trade_date,name,pct_change, close, net_amount,net_amount_rate,rank')
```
# 大盘资金流向（DC）

**路径**: 股票数据/资金流向数据
**接口**: `moneyflow_mkt_dc`
**积分**: 120
**描述**: 获取东方财富大盘资金流向数据，每日盘后更新限量：单次最大3000条，可根据日期或日期区间循环获取积分：120积分可试用，5000积分可正式调取，具体请参阅积分获取办法
**限量**: 单次最大3000条，可根据日期或日期区间循环获取积分：120积分可试用，5000积分可正式调取，具体请参阅积分获取办法

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| close_sh | float | Y | 上证收盘价（点） |
| pct_change_sh | float | Y | 上证涨跌幅(%) |
| close_sz | float | Y | 深证收盘价（点） |
| pct_change_sz | float | Y | 深证涨跌幅(%) |
| net_amount | float | Y | 今日主力净流入 净额（元） |
| net_amount_rate | float | Y | 今日主力净流入净占比% |
| buy_elg_amount | float | Y | 今日超大单净流入 净额（元） |
| buy_elg_amount_rate | float | Y | 今日超大单净流入 净占比% |
| buy_lg_amount | float | Y | 今日大单净流入 净额（元） |
| buy_lg_amount_rate | float | Y | 今日大单净流入 净占比% |
| buy_md_amount | float | Y | 今日中单净流入 净额（元） |
| buy_md_amount_rate | float | Y | 今日中单净流入 净占比% |
| buy_sm_amount | float | Y | 今日小单净流入 净额（元） |
| buy_sm_amount_rate | float | Y | 今日小单净流入 净占比% |

## 调用示例

```python
#获取当日所有板块资金流向
df = pro.moneyflow_mkt_dc(start_date='20240901', end_date='20240930')
```
# 未知接口

**路径**: 股票数据
# 开盘啦榜单数据

**路径**: 股票数据/打板专题数据
**接口**: `kpl_list`
**积分**: 5000
**描述**: 获取开盘啦涨停、跌停、炸板等榜单数据限量：单次最大8000条数据，可根据日期循环获取历史数据积分：5000积分每分钟可以请求200次每天总量1万次，8000积分以上每分钟500次每天总量不限制，具体请参阅积分获取办法
**限量**: 单次最大8000条数据，可根据日期循环获取历史数据积分：5000积分每分钟可以请求200次每天总量1万次，8000积分以上每分钟500次每天总量不限制，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期 |
| tag | str | N | 板单类型（涨停/炸板/跌停/自然涨停/竞价，默认为涨停) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 代码 |
| name | str | Y | 名称 |
| trade_date | str | Y | 交易时间 |
| lu_time | str | Y | 涨停时间 |
| ld_time | str | Y | 跌停时间 |
| open_time | str | Y | 开板时间 |
| last_time | str | Y | 最后涨停时间 |
| lu_desc | str | Y | 涨停原因 |
| tag | str | Y | 标签 |
| theme | str | Y | 板块 |
| net_change | float | Y | 主力净额(元) |
| bid_amount | float | Y | 竞价成交额(元) |
| status | str | Y | 状态（N连板） |
| bid_change | float | Y | 竞价净额 |
| bid_turnover | float | Y | 竞价换手% |
| lu_bid_vol | float | Y | 涨停委买额 |
| pct_chg | float | Y | 涨跌幅% |
| bid_pct_chg | float | Y | 竞价涨幅% |
| rt_pct_chg | float | Y | 实时涨幅% |
| limit_order | float | Y | 封单 |
| amount | float | Y | 成交额 |
| turnover_rate | float | Y | 换手率% |
| free_float | float | Y | 实际流通 |
| lu_limit_order | float | Y | 最大封单 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.kpl_list(trade_date='20240927', tag='涨停', fields='ts_code,name,trade_date,tag,theme,status')
```
# 个股资金流向（THS）

**路径**: 股票数据/资金流向数据
**接口**: `moneyflow_ths`
**积分**: 5000
**描述**: 获取同花顺个股资金流向数据，每日盘后更新限量：单次最大6000，可根据日期或股票代码循环提取数据积分：用户需要至少5000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大6000，可根据日期或股票代码循环提取数据积分：用户需要至少5000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 股票代码 |
| name | str | Y | 股票名称 |
| pct_change | float | Y | 涨跌幅 |
| latest | float | Y | 最新价 |
| net_amount | float | Y | 资金净流入(万元) |
| net_d5_amount | float | Y | 5日主力净额(万元) |
| buy_lg_amount | float | Y | 今日大单净流入额(万元) |
| buy_lg_amount_rate | float | Y | 今日大单净流入占比(%) |
| buy_md_amount | float | Y | 今日中单净流入额(万元) |
| buy_md_amount_rate | float | Y | 今日中单净流入占比(%) |
| buy_sm_amount | float | Y | 今日小单净流入额(万元) |
| buy_sm_amount_rate | float | Y | 今日小单净流入占比(%) |

## 调用示例

```python
pro = ts.pro_api()

#获取单日全部股票数据
df = pro.moneyflow_ths(trade_date='20241011')

#获取单个股票数据
df = pro.moneyflow_ths(ts_code='002149.SZ', start_date='20241001', end_date='20241011')
```
# 个股资金流向（DC）

**路径**: 股票数据/资金流向数据
**接口**: `moneyflow_dc`
**积分**: 5000
**描述**: 获取东方财富个股资金流向数据，每日盘后更新，数据开始于20230911限量：单次最大获取6000条数据，可根据日期或股票代码循环提取数据积分：用户需要至少5000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大获取6000条数据，可根据日期或股票代码循环提取数据积分：用户需要至少5000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 股票代码 |
| name | str | Y | 股票名称 |
| pct_change | float | Y | 涨跌幅 |
| close | float | Y | 最新价 |
| net_amount | float | Y | 今日主力净流入额（万元） |
| net_amount_rate | float | Y | 今日主力净流入净占比（%） |
| buy_elg_amount | float | Y | 今日超大单净流入额（万元） |
| buy_elg_amount_rate | float | Y | 今日超大单净流入占比（%） |
| buy_lg_amount | float | Y | 今日大单净流入额（万元） |
| buy_lg_amount_rate | float | Y | 今日大单净流入占比（%） |
| buy_md_amount | float | Y | 今日中单净流入额（万元） |
| buy_md_amount_rate | float | Y | 今日中单净流入占比（%） |
| buy_sm_amount | float | Y | 今日小单净流入额（万元） |
| buy_sm_amount_rate | float | Y | 今日小单净流入占比（%） |

## 调用示例

```python
pro = ts.pro_api()

#获取单日全部股票数据
df = pro.moneyflow_dc(trade_date='20241011')

#获取单个股票数据
df = pro.moneyflow_dc(ts_code='002149.SZ', start_date='20240901', end_date='20240913')
```
# 开盘啦题材库

**路径**: 股票数据/打板专题数据
**接口**: `kpl_concept`
**积分**: 5000
**描述**: 获取开盘啦概念题材列表，每天盘后更新限量：单次最大5000条，可根据日期循环获取历史数据积分：5000积分可提取数据，具体请参阅积分获取办法
**限量**: 单次最大5000条，可根据日期循环获取历史数据积分：5000积分可提取数据，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期（YYYYMMDD格式） |
| ts_code | str | N | 题材代码（xxxxxx.KP格式） |
| name | str | N | 题材名称 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 题材代码 |
| name | str | Y | 题材名称 |
| z_t_num | None | Y | 涨停数量 |
| up_num | str | Y | 排名上升位数 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.kpl_concept(trade_date='20241014')
```
# 开盘啦题材成分

**路径**: 股票数据/打板专题数据
**接口**: `kpl_concept_cons`
**积分**: 5000
**描述**: 获取开盘啦概念题材的成分股限量：单次最大3000条，可根据代码和日期循环获取全部数据积分：5000积分可提取数据，具体请参阅积分获取办法
**限量**: 单次最大3000条，可根据代码和日期循环获取全部数据积分：5000积分可提取数据，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期（YYYYMMDD格式） |
| ts_code | str | N | 题材代码（xxxxxx.KP格式） |
| con_code | str | N | 成分代码（xxxxxx.SH格式） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 题材ID |
| name | str | Y | 题材名称 |
| con_name | str | Y | 股票名称 |
| con_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| desc | str | Y | 描述 |
| hot_num | None | Y | 人气值 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.kpl_concept_cons(trade_date='20241014')
```
# 股票开盘集合竞价数据

**路径**: 股票数据/特色数据
**接口**: `stk_auction_o`
**描述**: 股票开盘9:30集合竞价数据，每天盘后更新限量：单次请求最大返回10000行数据，可根据日期循环权限：开通了股票分钟权限后可获得本接口权限，具体参考权限说明
**限量**: 单次请求最大返回10000行数据，可根据日期循环权限：开通了股票分钟权限后可获得本接口权限，具体参考权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期(YYYYMMDD) |
| start_date | str | N | 开始日期(YYYYMMDD) |
| end_date | str | N | 结束日期(YYYYMMDD) |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| close | float | Y | 开盘集合竞价收盘价 |
| open | float | Y | 开盘集合竞价开盘价 |
| high | float | Y | 开盘集合竞价最高价 |
| low | float | Y | 开盘集合竞价最低价 |
| vol | float | Y | 开盘集合竞价成交量 |
| amount | float | Y | 开盘集合竞价成交额 |
| vwap | float | Y | 开盘集合竞价均价 |

## 调用示例

```python
pro = ts.pro_api()

df=pro.stk_auction_o(trade_date='20241122')
```
# 股票收盘集合竞价数据

**路径**: 股票数据/特色数据
**接口**: `stk_auction_c`
**描述**: 股票收盘15:00集合竞价数据，每天盘后更新限量：单次请求最大返回10000行数据，可根据日期循环权限：开通了股票分钟权限后可获得本接口权限，具体参考权限说明
**限量**: 单次请求最大返回10000行数据，可根据日期循环权限：开通了股票分钟权限后可获得本接口权限，具体参考权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期(YYYYMMDD) |
| start_date | str | N | 开始日期(YYYYMMDD) |
| end_date | str | N | 结束日期(YYYYMMDD) |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| close | float | Y | 收盘集合竞价收盘价 |
| open | float | Y | 收盘集合竞价开盘价 |
| high | float | Y | 收盘集合竞价最高价 |
| low | float | Y | 收盘集合竞价最低价 |
| vol | float | Y | 收盘集合竞价成交量 |
| amount | float | Y | 收盘集合竞价成交额 |
| vwap | float | Y | 收盘集合竞价均价 |

## 调用示例

```python
pro = ts.pro_api()

df=pro.stk_auction_c(trade_date='20241122')
```
# 涨跌停榜单（同花顺）

**路径**: 股票数据/打板专题数据
**接口**: `limit_list_ths`
**积分**: 8000
**描述**: 获取同花顺每日涨跌停榜单数据，历史数据从20231101开始提供，增量每天16点左右更新限量：单次最大4000条，可根据日期或股票代码循环提取积分：8000积分以上每分钟500次，每天总量不限制，具体请参阅积分获取办法注意：本接口只限个人学习和研究使用，如需商业用途，请自行联系同花顺解决数据采购问题。
**限量**: 单次最大4000条，可根据日期或股票代码循环提取积分：8000积分以上每分钟500次，每天总量不限制，具体请参阅积分获取办法注意：本接口只限个人学习和研究使用，如需商业用途，请自行联系同花顺解决数据采购问题。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期 |
| ts_code | str | N | 股票代码 |
| limit_type | str | N | 涨停池、连扳池、冲刺涨停、炸板池、跌停池，默认：涨停池 |
| market | str | N | HS-沪深主板 GEM-创业板 STAR-科创板 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 股票代码 |
| name | str | Y | 股票名称 |
| price | float | Y | 收盘价(元) |
| pct_chg | float | Y | 涨跌幅% |
| open_num | int | Y | 打开次数 |
| lu_desc | str | Y | 涨停原因 |
| limit_type | str | Y | 板单类别 |
| tag | str | Y | 涨停标签 |
| status | str | Y | 涨停状态（N连板、一字板） |
| first_lu_time | str | N | 首次涨停时间 |
| last_lu_time | str | N | 最后涨停时间 |
| first_ld_time | str | N | 首次跌停时间 |
| last_ld_time | str | N | 最后跌停时间 |
| limit_order | float | Y | 封单量(元 |
| limit_amount | float | Y | 封单额(元 |
| turnover_rate | float | Y | 换手率% |
| free_float | float | Y | 实际流通(元 |
| lu_limit_order | float | Y | 最大封单(元 |
| limit_up_suc_rate | float | Y | 近一年涨停封板率 |
| turnover | float | Y | 成交额 |
| rise_rate | float | N | 涨速 |
| sum_float | float | N | 总市值（亿元） |
| market_type | str | Y | 股票类型：HS沪深主板、GEM创业板、STAR科创板 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.limit_list_ths(trade_date='20241125', limit_type='涨停池', fields='ts_code,trade_date,tag,status,lu_desc')
```
# 连板天梯

**路径**: 股票数据/打板专题数据
**接口**: `limit_step`
**积分**: 8000
**描述**: 获取每天连板个数晋级的股票，可以分析出每天连续涨停进阶个数，判断强势热度限量：单次最大2000行数据，可根据股票代码或者日期循环提取全部积分：8000积分以上每分钟500次，每天总量不限制，具体请参阅积分获取办法
**限量**: 单次最大2000行数据，可根据股票代码或者日期循环提取全部积分：8000积分以上每分钟500次，每天总量不限制，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期（格式：YYYYMMDD，下同） |
| ts_code | str | N | 股票代码 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| nums | str | N | 连板次数，支持多个输入，例如nums='2,3' |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 代码 |
| name | str | Y | 名称 |
| trade_date | str | Y | 交易日期 |
| nums | str | Y | 连板次数 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.limit_step(trade_date='20241125')
```
# 最强板块统计

**路径**: 股票数据/打板专题数据
**接口**: `limit_cpt_list`
**积分**: 8000
**描述**: 获取每天涨停股票最多最强的概念板块，可以分析强势板块的轮动，判断资金动向限量：单次最大2000行数据，可根据股票代码或者日期循环提取全部积分：8000积分以上每分钟500次，每天总量不限制，具体请参阅积分获取办法
**限量**: 单次最大2000行数据，可根据股票代码或者日期循环提取全部积分：8000积分以上每分钟500次，每天总量不限制，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期（格式：YYYYMMDD，下同） |
| ts_code | str | N | 板块代码 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 板块代码 |
| name | str | Y | 板块名称 |
| trade_date | str | Y | 交易日期 |
| days | int | Y | 上榜天数 |
| up_stat | str | Y | 连板高度 |
| cons_nums | int | Y | 连板家数 |
| up_nums | str | Y | 涨停家数 |
| pct_chg | float | Y | 涨跌幅% |
| rank | str | Y | 板块热点排名 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.limit_cpt_list(trade_date='20241127')
```
# 指数技术因子(专业版)

**路径**: 指数专题
**接口**: `idx_factor_pro`
**积分**: 8000
**描述**: 获取指数每日技术面因子数据，用于跟踪指数当前走势情况，数据由Tushare社区自产，覆盖全历史；输出参数_bfq表示不复权描述中说明了因子的默认传参，如需要特殊参数或者更多因子可以联系管理员评估，指数包括大盘指数 申万行业指数 中信指数限量：单次最大8000积分：5000积分每分钟可以请求30次，8000积分以上每分钟500次
**限量**: 单次最大8000积分：5000积分每分钟可以请求30次，8000积分以上每分钟500次

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 指数代码(大盘指数 申万指数 中信指数) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| trade_date | str | N | 交易日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 指数代码 |
| trade_date | str | Y | 交易日期 |
| open | float | Y | 开盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| close | float | Y | 收盘价 |
| pre_close | float | Y | 昨收价 |
| change | float | Y | 涨跌额 |
| pct_change | float | Y | 涨跌幅 （未复权，如果是复权请用 通用行情接口 ） |
| vol | float | Y | 成交量 （手） |
| amount | float | Y | 成交额 （千元） |
| asi_bfq | float | Y | 振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10 |
| asit_bfq | float | Y | 振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10 |
| atr_bfq | float | Y | 真实波动N日平均值-CLOSE, HIGH, LOW, N=20 |
| bbi_bfq | float | Y | BBI多空指标-CLOSE, M1=3, M2=6, M3=12, M4=20 |
| bias1_bfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias2_bfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias3_bfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| boll_lower_bfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_mid_bfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_upper_bfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| brar_ar_bfq | float | Y | BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26 |
| brar_br_bfq | float | Y | BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26 |
| cci_bfq | float | Y | 顺势指标又叫CCI指标-CLOSE, HIGH, LOW, N=14 |
| cr_bfq | float | Y | CR价格动量指标-CLOSE, HIGH, LOW, N=20 |
| dfma_dif_bfq | float | Y | 平行线差指标-CLOSE, N1=10, N2=50, M=10 |
| dfma_difma_bfq | float | Y | 平行线差指标-CLOSE, N1=10, N2=50, M=10 |
| dmi_adx_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_adxr_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_mdi_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_pdi_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| downdays | float | Y | 连跌天数 |
| updays | float | Y | 连涨天数 |
| dpo_bfq | float | Y | 区间震荡线-CLOSE, M1=20, M2=10, M3=6 |
| madpo_bfq | float | Y | 区间震荡线-CLOSE, M1=20, M2=10, M3=6 |
| ema_bfq_10 | float | Y | 指数移动平均-N=10 |
| ema_bfq_20 | float | Y | 指数移动平均-N=20 |
| ema_bfq_250 | float | Y | 指数移动平均-N=250 |
| ema_bfq_30 | float | Y | 指数移动平均-N=30 |
| ema_bfq_5 | float | Y | 指数移动平均-N=5 |
| ema_bfq_60 | float | Y | 指数移动平均-N=60 |
| ema_bfq_90 | float | Y | 指数移动平均-N=90 |
| emv_bfq | float | Y | 简易波动指标-HIGH, LOW, VOL, N=14, M=9 |
| maemv_bfq | float | Y | 简易波动指标-HIGH, LOW, VOL, N=14, M=9 |
| expma_12_bfq | float | Y | EMA指数平均数指标-CLOSE, N1=12, N2=50 |
| expma_50_bfq | float | Y | EMA指数平均数指标-CLOSE, N1=12, N2=50 |
| kdj_bfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_d_bfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_k_bfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| ktn_down_bfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_mid_bfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_upper_bfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| lowdays | float | Y | LOWRANGE(LOW)表示当前最低价是近多少周期内最低价的最小值 |
| topdays | float | Y | TOPRANGE(HIGH)表示当前最高价是近多少周期内最高价的最大值 |
| ma_bfq_10 | float | Y | 简单移动平均-N=10 |
| ma_bfq_20 | float | Y | 简单移动平均-N=20 |
| ma_bfq_250 | float | Y | 简单移动平均-N=250 |
| ma_bfq_30 | float | Y | 简单移动平均-N=30 |
| ma_bfq_5 | float | Y | 简单移动平均-N=5 |
| ma_bfq_60 | float | Y | 简单移动平均-N=60 |
| ma_bfq_90 | float | Y | 简单移动平均-N=90 |
| macd_bfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_dea_bfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_dif_bfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| mass_bfq | float | Y | 梅斯线-HIGH, LOW, N1=9, N2=25, M=6 |
| ma_mass_bfq | float | Y | 梅斯线-HIGH, LOW, N1=9, N2=25, M=6 |
| mfi_bfq | float | Y | MFI指标是成交量的RSI指标-CLOSE, HIGH, LOW, VOL, N=14 |
| mtm_bfq | float | Y | 动量指标-CLOSE, N=12, M=6 |
| mtmma_bfq | float | Y | 动量指标-CLOSE, N=12, M=6 |
| obv_bfq | float | Y | 能量潮指标-CLOSE, VOL |
| psy_bfq | float | Y | 投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6 |
| psyma_bfq | float | Y | 投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6 |
| roc_bfq | float | Y | 变动率指标-CLOSE, N=12, M=6 |
| maroc_bfq | float | Y | 变动率指标-CLOSE, N=12, M=6 |
| rsi_bfq_12 | float | Y | RSI指标-CLOSE, N=12 |
| rsi_bfq_24 | float | Y | RSI指标-CLOSE, N=24 |
| rsi_bfq_6 | float | Y | RSI指标-CLOSE, N=6 |
| taq_down_bfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_mid_bfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_up_bfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| trix_bfq | float | Y | 三重指数平滑平均线-CLOSE, M1=12, M2=20 |
| trma_bfq | float | Y | 三重指数平滑平均线-CLOSE, M1=12, M2=20 |
| vr_bfq | float | Y | VR容量比率-CLOSE, VOL, M1=26 |
| wr_bfq | float | Y | W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6 |
| wr1_bfq | float | Y | W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6 |
| xsii_td1_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td2_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td3_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td4_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
# 场内基金技术因子(专业版)

**路径**: 公募基金
**接口**: `fund_factor_pro`
**积分**: 8000
**描述**: 获取场内基金每日技术面因子数据，用于跟踪场内基金当前走势情况，数据由Tushare社区自产，覆盖全历史；输出参数_bfq表示不复权，描述中说明了因子的默认传参，如需要特殊参数或者更多因子可以联系管理员评估限量：单次最大8000积分：5000积分每分钟可以请求30次，8000积分以上每分钟500次
**限量**: 单次最大8000积分：5000积分每分钟可以请求30次，8000积分以上每分钟500次

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 基金代码 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| trade_date | str | N | 交易日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 基金代码 |
| trade_date | str | Y | 交易日期 |
| trade_date_doris | None | Y | 日期 |
| open | float | Y | 开盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| close | float | Y | 收盘价 |
| pre_close | float | Y | 昨收价 |
| change | float | Y | 涨跌额 |
| pct_change | float | Y | 涨跌幅 （未复权，如果是复权请用 通用行情接口 ） |
| vol | float | Y | 成交量 （手） |
| amount | float | Y | 成交额 （千元） |
| asi_bfq | float | Y | 振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10 |
| asit_bfq | float | Y | 振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10 |
| atr_bfq | float | Y | 真实波动N日平均值-CLOSE, HIGH, LOW, N=20 |
| bbi_bfq | float | Y | BBI多空指标-CLOSE, M1=3, M2=6, M3=12, M4=20 |
| bias1_bfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias2_bfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias3_bfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| boll_lower_bfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_mid_bfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_upper_bfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| brar_ar_bfq | float | Y | BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26 |
| brar_br_bfq | float | Y | BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26 |
| cci_bfq | float | Y | 顺势指标又叫CCI指标-CLOSE, HIGH, LOW, N=14 |
| cr_bfq | float | Y | CR价格动量指标-CLOSE, HIGH, LOW, N=20 |
| dfma_dif_bfq | float | Y | 平行线差指标-CLOSE, N1=10, N2=50, M=10 |
| dfma_difma_bfq | float | Y | 平行线差指标-CLOSE, N1=10, N2=50, M=10 |
| dmi_adx_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_adxr_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_mdi_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_pdi_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| downdays | float | Y | 连跌天数 |
| updays | float | Y | 连涨天数 |
| dpo_bfq | float | Y | 区间震荡线-CLOSE, M1=20, M2=10, M3=6 |
| madpo_bfq | float | Y | 区间震荡线-CLOSE, M1=20, M2=10, M3=6 |
| ema_bfq_10 | float | Y | 指数移动平均-N=10 |
| ema_bfq_20 | float | Y | 指数移动平均-N=20 |
| ema_bfq_250 | float | Y | 指数移动平均-N=250 |
| ema_bfq_30 | float | Y | 指数移动平均-N=30 |
| ema_bfq_5 | float | Y | 指数移动平均-N=5 |
| ema_bfq_60 | float | Y | 指数移动平均-N=60 |
| ema_bfq_90 | float | Y | 指数移动平均-N=90 |
| emv_bfq | float | Y | 简易波动指标-HIGH, LOW, VOL, N=14, M=9 |
| maemv_bfq | float | Y | 简易波动指标-HIGH, LOW, VOL, N=14, M=9 |
| expma_12_bfq | float | Y | EMA指数平均数指标-CLOSE, N1=12, N2=50 |
| expma_50_bfq | float | Y | EMA指数平均数指标-CLOSE, N1=12, N2=50 |
| kdj_bfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_d_bfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_k_bfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| ktn_down_bfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_mid_bfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_upper_bfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| lowdays | float | Y | LOWRANGE(LOW)表示当前最低价是近多少周期内最低价的最小值 |
| topdays | float | Y | TOPRANGE(HIGH)表示当前最高价是近多少周期内最高价的最大值 |
| ma_bfq_10 | float | Y | 简单移动平均-N=10 |
| ma_bfq_20 | float | Y | 简单移动平均-N=20 |
| ma_bfq_250 | float | Y | 简单移动平均-N=250 |
| ma_bfq_30 | float | Y | 简单移动平均-N=30 |
| ma_bfq_5 | float | Y | 简单移动平均-N=5 |
| ma_bfq_60 | float | Y | 简单移动平均-N=60 |
| ma_bfq_90 | float | Y | 简单移动平均-N=90 |
| macd_bfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_dea_bfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_dif_bfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| mass_bfq | float | Y | 梅斯线-HIGH, LOW, N1=9, N2=25, M=6 |
| ma_mass_bfq | float | Y | 梅斯线-HIGH, LOW, N1=9, N2=25, M=6 |
| mfi_bfq | float | Y | MFI指标是成交量的RSI指标-CLOSE, HIGH, LOW, VOL, N=14 |
| mtm_bfq | float | Y | 动量指标-CLOSE, N=12, M=6 |
| mtmma_bfq | float | Y | 动量指标-CLOSE, N=12, M=6 |
| obv_bfq | float | Y | 能量潮指标-CLOSE, VOL |
| psy_bfq | float | Y | 投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6 |
| psyma_bfq | float | Y | 投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6 |
| roc_bfq | float | Y | 变动率指标-CLOSE, N=12, M=6 |
| maroc_bfq | float | Y | 变动率指标-CLOSE, N=12, M=6 |
| rsi_bfq_12 | float | Y | RSI指标-CLOSE, N=12 |
| rsi_bfq_24 | float | Y | RSI指标-CLOSE, N=24 |
| rsi_bfq_6 | float | Y | RSI指标-CLOSE, N=6 |
| taq_down_bfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_mid_bfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_up_bfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| trix_bfq | float | Y | 三重指数平滑平均线-CLOSE, M1=12, M2=20 |
| trma_bfq | float | Y | 三重指数平滑平均线-CLOSE, M1=12, M2=20 |
| vr_bfq | float | Y | VR容量比率-CLOSE, VOL, M1=26 |
| wr_bfq | float | Y | W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6 |
| wr1_bfq | float | Y | W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6 |
| xsii_td1_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td2_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td3_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td4_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
# 资产负债表

**路径**: 股票数据/财务数据
**接口**: `balancesheet`
**积分**: 2000
**描述**: 获取上市公司资产负债表积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用balancesheet_vip接口（参数一致），需积攒5000积分。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| ann_date | str | N | 公告日期(YYYYMMDD格式，下同) |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |
| period | str | N | 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报) |
| report_type | str | N | 报告类型：见下方详细说明 |
| comp_type | str | N | 公司类型：1一般工商业 2银行 3保险 4证券 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS股票代码 |
| ann_date | str | Y | 公告日期 |
| f_ann_date | str | Y | 实际公告日期 |
| end_date | str | Y | 报告期 |
| report_type | str | Y | 报表类型 |
| comp_type | str | Y | 公司类型(1一般工商业2银行3保险4证券) |
| end_type | str | Y | 报告期类型 |
| total_share | float | Y | 期末总股本 |
| cap_rese | float | Y | 资本公积金 |
| undistr_porfit | float | Y | 未分配利润 |
| surplus_rese | float | Y | 盈余公积金 |
| special_rese | float | Y | 专项储备 |
| money_cap | float | Y | 货币资金 |
| trad_asset | float | Y | 交易性金融资产 |
| notes_receiv | float | Y | 应收票据 |
| accounts_receiv | float | Y | 应收账款 |
| oth_receiv | float | Y | 其他应收款 |
| prepayment | float | Y | 预付款项 |
| div_receiv | float | Y | 应收股利 |
| int_receiv | float | Y | 应收利息 |
| inventories | float | Y | 存货 |
| amor_exp | float | Y | 待摊费用 |
| nca_within_1y | float | Y | 一年内到期的非流动资产 |
| sett_rsrv | float | Y | 结算备付金 |
| loanto_oth_bank_fi | float | Y | 拆出资金 |
| premium_receiv | float | Y | 应收保费 |
| reinsur_receiv | float | Y | 应收分保账款 |
| reinsur_res_receiv | float | Y | 应收分保合同准备金 |
| pur_resale_fa | float | Y | 买入返售金融资产 |
| oth_cur_assets | float | Y | 其他流动资产 |
| total_cur_assets | float | Y | 流动资产合计 |
| fa_avail_for_sale | float | Y | 可供出售金融资产 |
| htm_invest | float | Y | 持有至到期投资 |
| lt_eqt_invest | float | Y | 长期股权投资 |
| invest_real_estate | float | Y | 投资性房地产 |
| time_deposits | float | Y | 定期存款 |
| oth_assets | float | Y | 其他资产 |
| lt_rec | float | Y | 长期应收款 |
| fix_assets | float | Y | 固定资产 |
| cip | float | Y | 在建工程 |
| const_materials | float | Y | 工程物资 |
| fixed_assets_disp | float | Y | 固定资产清理 |
| produc_bio_assets | float | Y | 生产性生物资产 |
| oil_and_gas_assets | float | Y | 油气资产 |
| intan_assets | float | Y | 无形资产 |
| r_and_d | float | Y | 研发支出 |
| goodwill | float | Y | 商誉 |
| lt_amor_exp | float | Y | 长期待摊费用 |
| defer_tax_assets | float | Y | 递延所得税资产 |
| decr_in_disbur | float | Y | 发放贷款及垫款 |
| oth_nca | float | Y | 其他非流动资产 |
| total_nca | float | Y | 非流动资产合计 |
| cash_reser_cb | float | Y | 现金及存放中央银行款项 |
| depos_in_oth_bfi | float | Y | 存放同业和其它金融机构款项 |
| prec_metals | float | Y | 贵金属 |
| deriv_assets | float | Y | 衍生金融资产 |
| rr_reins_une_prem | float | Y | 应收分保未到期责任准备金 |
| rr_reins_outstd_cla | float | Y | 应收分保未决赔款准备金 |
| rr_reins_lins_liab | float | Y | 应收分保寿险责任准备金 |
| rr_reins_lthins_liab | float | Y | 应收分保长期健康险责任准备金 |
| refund_depos | float | Y | 存出保证金 |
| ph_pledge_loans | float | Y | 保户质押贷款 |
| refund_cap_depos | float | Y | 存出资本保证金 |
| indep_acct_assets | float | Y | 独立账户资产 |
| client_depos | float | Y | 其中：客户资金存款 |
| client_prov | float | Y | 其中：客户备付金 |
| transac_seat_fee | float | Y | 其中:交易席位费 |
| invest_as_receiv | float | Y | 应收款项类投资 |
| total_assets | float | Y | 资产总计 |
| lt_borr | float | Y | 长期借款 |
| st_borr | float | Y | 短期借款 |
| cb_borr | float | Y | 向中央银行借款 |
| depos_ib_deposits | float | Y | 吸收存款及同业存放 |
| loan_oth_bank | float | Y | 拆入资金 |
| trading_fl | float | Y | 交易性金融负债 |
| notes_payable | float | Y | 应付票据 |
| acct_payable | float | Y | 应付账款 |
| adv_receipts | float | Y | 预收款项 |
| sold_for_repur_fa | float | Y | 卖出回购金融资产款 |
| comm_payable | float | Y | 应付手续费及佣金 |
| payroll_payable | float | Y | 应付职工薪酬 |
| taxes_payable | float | Y | 应交税费 |
| int_payable | float | Y | 应付利息 |
| div_payable | float | Y | 应付股利 |
| oth_payable | float | Y | 其他应付款 |
| acc_exp | float | Y | 预提费用 |
| deferred_inc | float | Y | 递延收益 |
| st_bonds_payable | float | Y | 应付短期债券 |
| payable_to_reinsurer | float | Y | 应付分保账款 |
| rsrv_insur_cont | float | Y | 保险合同准备金 |
| acting_trading_sec | float | Y | 代理买卖证券款 |
| acting_uw_sec | float | Y | 代理承销证券款 |
| non_cur_liab_due_1y | float | Y | 一年内到期的非流动负债 |
| oth_cur_liab | float | Y | 其他流动负债 |
| total_cur_liab | float | Y | 流动负债合计 |
| bond_payable | float | Y | 应付债券 |
| lt_payable | float | Y | 长期应付款 |
| specific_payables | float | Y | 专项应付款 |
| estimated_liab | float | Y | 预计负债 |
| defer_tax_liab | float | Y | 递延所得税负债 |
| defer_inc_non_cur_liab | float | Y | 递延收益-非流动负债 |
| oth_ncl | float | Y | 其他非流动负债 |
| total_ncl | float | Y | 非流动负债合计 |
| depos_oth_bfi | float | Y | 同业和其它金融机构存放款项 |
| deriv_liab | float | Y | 衍生金融负债 |
| depos | float | Y | 吸收存款 |
| agency_bus_liab | float | Y | 代理业务负债 |
| oth_liab | float | Y | 其他负债 |
| prem_receiv_adva | float | Y | 预收保费 |
| depos_received | float | Y | 存入保证金 |
| ph_invest | float | Y | 保户储金及投资款 |
| reser_une_prem | float | Y | 未到期责任准备金 |
| reser_outstd_claims | float | Y | 未决赔款准备金 |
| reser_lins_liab | float | Y | 寿险责任准备金 |
| reser_lthins_liab | float | Y | 长期健康险责任准备金 |
| indept_acc_liab | float | Y | 独立账户负债 |
| pledge_borr | float | Y | 其中:质押借款 |
| indem_payable | float | Y | 应付赔付款 |
| policy_div_payable | float | Y | 应付保单红利 |
| total_liab | float | Y | 负债合计 |
| treasury_share | float | Y | 减:库存股 |
| ordin_risk_reser | float | Y | 一般风险准备 |
| forex_differ | float | Y | 外币报表折算差额 |
| invest_loss_unconf | float | Y | 未确认的投资损失 |
| minority_int | float | Y | 少数股东权益 |
| total_hldr_eqy_exc_min_int | float | Y | 股东权益合计(不含少数股东权益) |
| total_hldr_eqy_inc_min_int | float | Y | 股东权益合计(含少数股东权益) |
| total_liab_hldr_eqy | float | Y | 负债及股东权益总计 |
| lt_payroll_payable | float | Y | 长期应付职工薪酬 |
| oth_comp_income | float | Y | 其他综合收益 |
| oth_eqt_tools | float | Y | 其他权益工具 |
| oth_eqt_tools_p_shr | float | Y | 其他权益工具(优先股) |
| lending_funds | float | Y | 融出资金 |
| acc_receivable | float | Y | 应收款项 |
| st_fin_payable | float | Y | 应付短期融资款 |
| payables | float | Y | 应付款项 |
| hfs_assets | float | Y | 持有待售的资产 |
| hfs_sales | float | Y | 持有待售的负债 |
| cost_fin_assets | float | Y | 以摊余成本计量的金融资产 |
| fair_value_fin_assets | float | Y | 以公允价值计量且其变动计入其他综合收益的金融资产 |
| cip_total | float | Y | 在建工程(合计)(元) |
| oth_pay_total | float | Y | 其他应付款(合计)(元) |
| long_pay_total | float | Y | 长期应付款(合计)(元) |
| debt_invest | float | Y | 债权投资(元) |
| oth_debt_invest | float | Y | 其他债权投资(元) |
| oth_eq_invest | float | N | 其他权益工具投资(元) |
| oth_illiq_fin_assets | float | N | 其他非流动金融资产(元) |
| oth_eq_ppbond | float | N | 其他权益工具:永续债(元) |
| receiv_financing | float | N | 应收款项融资 |
| use_right_assets | float | N | 使用权资产 |
| lease_liab | float | N | 租赁负债 |
| contract_assets | float | Y | 合同资产 |
| contract_liab | float | Y | 合同负债 |
| accounts_receiv_bill | float | Y | 应收票据及应收账款 |
| accounts_pay | float | Y | 应付票据及应付账款 |
| oth_rcv_total | float | Y | 其他应收款(合计)（元） |
| fix_assets_total | float | Y | 固定资产(合计)(元) |
| update_flag | str | Y | 更新标识 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.balancesheet(ts_code='600000.SH', start_date='20180101', end_date='20180730', fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,cap_rese')
```

```python
df2 = pro.balancesheet_vip(period='20181231',fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,cap_rese')
```
# 东方财富概念板块

**路径**: 股票数据/打板专题数据
**接口**: `dc_index`
**积分**: 6000
**描述**: 获取东方财富每个交易日的概念板块数据，支持按日期查询限量：单次最大可获取5000条数据，历史数据可根据日期循环获取权限：用户积累6000积分可调取，具体请参阅积分获取办法
**限量**: 单次最大可获取5000条数据，历史数据可根据日期循环获取权限：用户积累6000积分可调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 指数代码（支持多个代码同时输入，用逗号分隔） |
| name | str | N | 板块名称（例如：人形机器人） |
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 概念代码 |
| trade_date | str | Y | 交易日期 |
| name | str | Y | 概念名称 |
| leading | str | Y | 领涨股票名称 |
| leading_code | str | Y | 领涨股票代码 |
| pct_change | float | Y | 涨跌幅 |
| leading_pct | float | Y | 领涨股票涨跌幅 |
| total_mv | float | Y | 总市值（万元） |
| turnover_rate | float | Y | 换手率 |
| up_num | int | Y | 上涨家数 |
| down_num | int | Y | 下降家数 |

## 调用示例

```python
#获取东方财富2025年1月3日的概念板块列表
df = pro.dc_index(trade_date='20250103', fields='ts_code,name,turnover_rate,up_num,down_num')
```
# 东方财富板块成分

**路径**: 股票数据/打板专题数据
**接口**: `dc_member`
**积分**: 6000
**描述**: 获取东方财富板块每日成分数据，可以根据概念板块代码和交易日期，获取历史成分限量：单次最大获取5000条数据，可以通过日期和代码循环获取权限：用户积累6000积分可调取，具体请参阅积分获取办法注意：本接口只限个人学习和研究使用，如需商业用途，请自行联系东方财富解决数据采购问题。
**限量**: 单次最大获取5000条数据，可以通过日期和代码循环获取权限：用户积累6000积分可调取，具体请参阅积分获取办法注意：本接口只限个人学习和研究使用，如需商业用途，请自行联系东方财富解决数据采购问题。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 板块指数代码 |
| con_code | str | N | 成分股票代码 |
| trade_date | str | N | 交易日期（YYYYMMDD格式） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 概念代码 |
| con_code | str | Y | 成分代码 |
| name | str | Y | 成分股名称 |

## 调用示例

```python
#获取东方财富2025年1月2日的人形机器人概念板块成分列表
df = pro.dc_member(trade_date='20250102', ts_code='BK1184.DC')
```
# 神奇九转指标

**路径**: 股票数据/特色数据
**接口**: `stk_nineturn`
**积分**: 6000
**描述**: 神奇九转（又称“九转序列”）是一种基于技术分析的股票趋势反转指标，其思想来源于技术分析大师汤姆·迪马克（Tom DeMark）的TD序列。该指标的核心功能是通过识别股价在上涨或下跌过程中连续9天的特定走势，来判断股价的潜在反转点，从而帮助投资者提高抄底和逃顶的成功率，日线级别配合60min的九转效果更好，数据从20230101开始。限量：单次提取最大返回10000行数据，可通过股票代码和日期循环获取全部数据权限：达到6000积分可以调用
**限量**: 单次提取最大返回10000行数据，可通过股票代码和日期循环获取全部数据权限：达到6000积分可以调用

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期 （格式：YYYY-MM-DD HH:MM:SS) |
| freq | str | N | 频率(日daily) |
| start_date | str | N | 开始时间 |
| end_date | str | N | 结束时间 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | datetime | Y | 交易日期 |
| freq | str | Y | 频率(日daily) |
| open | float | Y | 开盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| close | float | Y | 收盘价 |
| vol | float | Y | 成交量 |
| amount | float | Y | 成交额 |
| up_count | float | Y | 上九转计数 |
| down_count | float | Y | 下九转计数 |
| nine_up_turn | str | Y | 是否上九转)+9表示上九转 |
| nine_down_turn | str | Y | 是否下九转-9表示下九转 |

## 调用示例

```python
pro = ts.pro_api()

df=pro.stk_nineturn(ts_code='000001.SZ',freq='daily',fields='ts_code,trade_date,freq,up_count,down_count,nine_up_turn,nine_down_turn')
```
# 股票周/月线行情(复权--每日更新)

**路径**: 股票数据/行情数据
**接口**: `stk_week_month_adj`
**积分**: 2000
**描述**: 股票周/月线行情(复权--每日更新)限量：单次最大6000,可使用交易日期循环提取，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法
**限量**: 单次最大6000,可使用交易日期循环提取，总量不限制积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str |  | 股票代码 |
| trade_date | str |  | 交易日期（每周五或者月末日期） |
| end_date | str |  | 计算截至日期 |
| freq | str |  | 频率(周week,月month) |
| open | float |  | (周/月)开盘价 |
| high | float |  | (周/月)最高价 |
| low | float |  | (周/月)最低价 |
| close | float |  | (周/月)收盘价 |
| pre_close | float |  | 上一(周/月)收盘价【除权价，前复权】 |
| open_qfq | float |  | 前复权(周/月)开盘价 |
| high_qfq | float |  | 前复权(周/月)最高价 |
| low_qfq | float |  | 前复权(周/月)最低价 |
| close_qfq | float |  | 前复权(周/月)收盘价 |
| open_hfq | float |  | 后复权(周/月)开盘价 |
| high_hfq | float |  | 后复权(周/月)最高价 |
| low_hfq | float |  | 后复权(周/月)最低价 |
| close_hfq | float |  | 后复权(周/月)收盘价 |
| vol | float |  | (周/月)成交量 |
| amount | float |  | (周/月)成交额 |
| change | float |  | (周/月)涨跌额 |
| pct_chg | float |  | (周/月)涨跌幅 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收 】 |

## 调用示例

```python
pro = ts.pro_api()

df=pro.stk_week_month_adj(ts_code='000001.SZ',freq='week')
```
# 上证E互动

**路径**: 大模型语料专题数据
**接口**: `irm_qa_sh`
**积分**: 120
**描述**: 获取上交所e互动董秘问答文本数据。上证e互动是由上海证券交易所建立、上海证券市场所有参与主体无偿使用的沟通平台,旨在引导和促进上市公司、投资者等各市场参与主体之间的信息沟通,构建集中、便捷的互动渠道。本接口数据记录了以上沟通问答的文本数据。限量：单次请求最大返回3000行数据，可根据股票代码，日期等参数循环提取全部数据权限：用户后120积分可以试用，正式权限为10000积分，或申请单独开权限，请参考权限说明
**限量**: 单次请求最大返回3000行数据，可根据股票代码，日期等参数循环提取全部数据权限：用户后120积分可以试用，正式权限为10000积分，或申请单独开权限，请参考权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期（格式YYYYMMDD，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| pub_date | str | N | 发布开始日期(格式：2025-06-03 16:43:03) |
| pub_date | str | N | 发布结束日期(格式：2025-06-03 18:43:23) |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| name | str | Y | 公司名称 |
| trade_date | str | Y | 日期 |
| q | str | Y | 问题 |
| a | str | Y | 回复 |
| pub_time | datetime | Y | 回复时间 |

## 调用示例

```python
pro = ts.pro_api()

#获取2025年2月12日上证e互动的问答文本
df = pro.irm_qa_sh(ann_date='20250212')
```
# 深证互动易

**路径**: 大模型语料专题数据
**接口**: `irm_qa_sz`
**积分**: 120
**描述**: 互动易是由深交所官方推出,供投资者与上市公司直接沟通的平台,一站式公司资讯汇集,提供第一手的互动问答、投资者关系信息、公司声音等内容。限量：单次请求最大返回3000行数据，可根据股票代码，日期等参数循环提取全部数据权限：用户后120积分可以试用，正式权限为10000积分，或申请单独开权限，请参考权限说明
**限量**: 单次请求最大返回3000行数据，可根据股票代码，日期等参数循环提取全部数据权限：用户后120积分可以试用，正式权限为10000积分，或申请单独开权限，请参考权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期（格式YYYYMMDD，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| pub_date | str | N | 发布开始日期(格式：2025-06-03 16:43:03) |
| pub_date | str | N | 发布结束日期(格式：2025-06-03 18:43:23) |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| name | str | Y | 公司名称 |
| trade_date | str | Y | 发布时间 |
| q | str | Y | 问题 |
| a | str | Y | 回复 |
| pub_time | str | Y | 答复时间 |
| industry | str | Y | 涉及行业 |

## 调用示例

```python
pro = ts.pro_api()

#获取2025年2月12日深证互动易的问答文本
df = pro.irm_qa_sz(ann_date='20250212')
```
# 期货合约涨跌停价格（盘前）

**路径**: 期货数据
**接口**: `ft_limit`
**积分**: 5000
**描述**: 获取所有期货合约每天的涨跌停价格及最低保证金率，数据开始于2005年。限量：单次最大获取4000行数据，可以通过日期、合约代码等参数循环获取所有历史积分：用户积5000积分可调取，积分获取方法具体请参阅积分获取办法
**限量**: 单次最大获取4000行数据，可以通过日期、合约代码等参数循环获取所有历史积分：用户积5000积分可调取，积分获取方法具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 合约代码 |
| trade_date | str | N | 交易日期（格式：YYYYMMDD） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| cont | str | N | 合约代码（例如：cont='CU') |
| exchange | str | N | 交易所代码 （例如：exchange='DCE') |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | TS股票代码 |
| name | str | Y | 合约名称 |
| up_limit | float | Y | 涨停价 |
| down_limit | float | Y | 跌停价 |
| m_ratio | float | Y | 最低交易保证金率（%） |
| cont | str | Y | 合约代码 |
| exchange | str | Y | 交易所代码 |

## 调用示例

```python
pro = ts.pro_api()

#获取单日全部期货合约涨跌停价格
df = pro.ft_limit(trade_date='20250213')

#获取单个品种所有合约涨跌停价格
df = pro.ft_limit(cont='CU')
```
# 当日集合竞价

**路径**: 股票数据/打板专题数据
**接口**: `stk_auction`
**描述**: 获取当日个股和ETF的集合竞价成交情况，每天9点25~29分之间可以获取当日的集合竞价成交数据限量：单次最大返回8000行数据，可根据日期或代码循环获取历史积分：本接口是单独开权限的数据，已经开通了股票分钟权限的用户可自动获得本接口权限，单独申请权限请参考权限列表。
**限量**: 单次最大返回8000行数据，可根据日期或代码循环获取历史积分：本接口是单独开权限的数据，已经开通了股票分钟权限的用户可自动获得本接口权限，单独申请权限请参考权限列表。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期（YYYYMMDD格式，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 数据日期 |
| vol | int | Y | 成交量（股） |
| price | int | Y | 成交均价（元） |
| amount | float | Y | 成交金额（元） |
| pre_close | float | Y | 昨收价（元） |
| turnover_rate | float | Y | 换手率（%） |
| volume_ratio | float | Y | 量比 |
| float_share | float | Y | 流通股本（万股） |

## 调用示例

```python
#获取2025年2月18日开盘集合竞价成交情况
df = pro.stk_auction(trade_date='20250218',fields='ts_code, trade_date,vol,price,amount,turnover_rate,volume_ratio')
```
# 股票历史分钟行情

**路径**: 股票数据/行情数据
**接口**: `stk_mins`
**描述**: 获取A股分钟数据，支持1min/5min/15min/30min/60min行情，提供Python SDK和 http Restful API两种方式限量：单次最大8000行数据，可以通过股票代码和时间循环获取，本接口可以提供超过10年历史分钟数据权限：需单独开权限，正式权限请参阅 权限说明
**限量**: 单次最大8000行数据，可以通过股票代码和时间循环获取，本接口可以提供超过10年历史分钟数据权限：需单独开权限，正式权限请参阅 权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码，e.g. 600000.SH |
| freq | str | Y | 分钟频度（1min/5min/15min/30min/60min） |
| start_date | datetime | N | 开始日期 格式：2023-08-25 09:00:00 |
| end_date | datetime | N | 结束时间 格式：2023-08-25 19:00:00 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_time | str | Y | 交易时间 |
| open | float | Y | 开盘价 |
| close | float | Y | 收盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| vol | int | Y | 成交量 |
| amount | float | Y | 成交金额 |

## 调用示例

```python
pro = ts.pro_api()

#获取浦发银行60000.SH的历史分钟数据
df = pro.stk_mins(ts_code='600000.SH', freq='1min', start_date='2023-08-25 09:00:00', end_date='2023-08-25 19:00:00')
```
# 同花顺概念板块资金流向（THS）

**路径**: 股票数据/资金流向数据
**接口**: `moneyflow_cnt_ths`
**积分**: 5000
**描述**: 获取同花顺概念板块每日资金流向限量：单次最大可调取5000条数据，可以根据日期和代码循环提取全部数据积分：5000积分可以调取，具体请参阅积分获取办法
**限量**: 单次最大可调取5000条数据，可以根据日期和代码循环提取全部数据积分：5000积分可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 代码 |
| trade_date | str | N | 交易日期(格式：YYYYMMDD，下同) |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| trade_date | str | Y | 交易日期 |
| ts_code | str | Y | 板块代码 |
| name | str | Y | 板块名称 |
| lead_stock | str | Y | 领涨股票名称 |
| close_price | float | Y | 最新价 |
| pct_change | float | Y | 行业涨跌幅 |
| industry_index | float | Y | 板块指数 |
| company_num | int | Y | 公司数量 |
| pct_change_stock | float | Y | 领涨股涨跌幅 |
| net_buy_amount | float | Y | 流入资金(亿元) |
| net_sell_amount | float | Y | 流出资金(亿元) |
| net_amount | float | Y | 净额(亿元) |

## 调用示例

```python
#获取当日同花顺板块资金流向
df = pro.moneyflow_cnt_ths(trade_date='20250320')
```
# 沪深京实时日线

**路径**: 股票数据/行情数据
**接口**: `rt_k`
**描述**: 获取实时日k线行情，支持按股票代码及股票代码通配符一次性提取全部股票实时日k线行情
**限量**: 单次最大可提取6000条数据，等同于一次提取全市场

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 支持通配符方式，e.g. 6*.SH、301*.SZ、600000.SH |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| name | None | Y | 股票名称 |
| pre_close | float | Y | 昨收价 |
| high | float | Y | 最高价 |
| open | float | Y | 开盘价 |
| low | float | Y | 最低价 |
| close | float | Y | 收盘价（最新价） |
| vol | int | Y | 成交量（股） |
| amount | int | Y | 成交金额（元） |
| num | int | Y | 开盘以来成交笔数 |
| ask_price1 | float | N | 委托卖盘（元） |
| ask_volume1 | int | N | 委托卖盘（股） |
| bid_price1 | float | N | 委托买盘（元） |
| bid_volume1 | int | N | 委托买盘（股） |
| trade_time | str | N | 交易时间 |

## 调用示例

```python
#获取今日开盘以来所有创业板实时日线和成交笔数
df = pro.rt_k(ts_code='3*.SZ')

#获取今日开盘以来全市场所有股票实时日线和成交笔数（不建议一次提取全市场，可分批提取性能更好）
df = pro.rt_k(ts_code='3*.SZ,6*.SH,0*.SZ,9*.BJ')

#获取当日开盘以来单个股票实时日线和成交笔数
df = pro.rt_k(ts_code='600000.SH,000001.SZ')
```
# 中信行业成分

**路径**: 指数专题
**接口**: `ci_index_member`
**积分**: 5000
**描述**: 按三级分类提取中信行业成分，可提供某个分类的所有成分，也可按股票代码提取所属分类，参数灵活限量：单次最大5000行，总量不限制权限：用户需5000积分可调取，积分获取方法请参阅积分获取办法
**限量**: 单次最大5000行，总量不限制权限：用户需5000积分可调取，积分获取方法请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| l1_code | str | N | 一级行业代码 |
| l2_code | str | N | 二级行业代码 |
| l3_code | str | N | 三级行业代码 |
| ts_code | str | N | 股票代码 |
| is_new | str | N | 是否最新（默认为“Y是”） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| l1_code | str | Y | 一级行业代码 |
| l1_name | str | Y | 一级行业名称 |
| l2_code | str | Y | 二级行业代码 |
| l2_name | str | Y | 二级行业名称 |
| l3_code | str | Y | 三级行业代码 |
| l3_name | str | Y | 三级行业名称 |
| ts_code | str | Y | 成分股票代码 |
| name | str | Y | 成分股票名称 |
| in_date | str | Y | 纳入日期 |
| out_date | str | Y | 剔除日期 |
| is_new | str | Y | 是否最新Y是N否 |

## 调用示例

```python
#获取二级分类元器件的成份股
df = pro.ci_index_member(l2_code='CI005835.CI', fields='l2_code,l1_name,ts_code,name')

#获取000001.SZ所属行业
df = pro.ci_index_member(ts_code='000001.SZ')
```
# A股实时分钟

**路径**: 股票数据/行情数据
**接口**: `rt_min`
**描述**: 获取全A股票实时分钟数据，包括1~60min限量：单次最大1000行数据，可以通过股票代码提取数据，支持逗号分隔的多个代码同时提取权限：正式权限请参阅 权限说明
**限量**: 单次最大1000行数据，可以通过股票代码提取数据，支持逗号分隔的多个代码同时提取权限：正式权限请参阅 权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| freq | str | Y | 1MIN,5MIN,15MIN,30MIN,60MIN （大写） |
| ts_code | str | Y | 支持单个和多个：600000.SH 或者 600000.SH,000001.SZ |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| time | None | Y | 交易时间 |
| open | float | Y | 开盘价 |
| close | float | Y | 收盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| vol | float | Y | 成交量(股） |
| amount | float | Y | 成交额（元） |

## 调用示例

```python
pro = ts.pro_api()

#获取浦发银行60000.SH的实时分钟数据
df = pro.rt_min(ts_code='600000.SH', freq='1MIN')
```
# 北交所新旧代码对照表

**路径**: 股票数据/基础数据
**接口**: `bse_mapping`
**积分**: 120
**描述**: 获取北交所股票代码变更后新旧代码映射表数据限量：单次最大1000条（本接口总数据量300以内）积分：120积分即可调取
**限量**: 单次最大1000条（本接口总数据量300以内）积分：120积分即可调取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| o_code | str | N | 旧代码 |
| n_code | str | N | 新代码 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| name | str | Y | 股票名称 |
| o_code | str | Y | 原代码 |
| n_code | str | Y | 新代码 |
| list_date | str | Y | 上市日期 |

## 调用示例

```python
#获取方大新材新旧代码对照数据
df = pro.bse_mapping(o_code='838163.BJ')


#获取全部变更的股票代码对照表
df = pro.bse_mapping()
```
# 通达信板块信息

**路径**: 股票数据/打板专题数据
**接口**: `tdx_index`
**积分**: 6000
**描述**: 获取通达信板块基础信息，包括概念板块、行业、风格、地域等限量：单次最大1000条数据，可根据日期参数循环提取权限：用户积累6000积分可调取，具体请参阅积分获取办法
**限量**: 单次最大1000条数据，可根据日期参数循环提取权限：用户积累6000积分可调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 板块代码：xxxxxx.TDX |
| trade_date | str | N | 交易日期(格式：YYYYMMDD） |
| idx_type | str | N | 板块类型：概念板块、行业板块、风格板块、地区板块 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 板块代码 |
| trade_date | str | Y | 交易日期 |
| name | str | Y | 板块名称 |
| idx_type | str | Y | 板块类型 |
| idx_count | int | Y | 成分个数 |
| total_share | float | Y | 总股本(亿) |
| float_share | float | Y | 流通股(亿) |
| total_mv | float | Y | 总市值(亿) |
| float_mv | float | Y | 流通市值(亿) |

## 调用示例

```python
#获取通达信2025年5月13日的概念板块列表
df = pro.tdx_index(trade_date='20250513', fields='ts_code,name,idx_type,idx_count')
```
# 通达信板块成分

**路径**: 股票数据/打板专题数据
**接口**: `tdx_member`
**积分**: 6000
**描述**: 获取通达信各板块成分股信息限量：单次最大3000条数据，可以根据日期和板块代码循环提取权限：用户积累6000积分可调取，具体请参阅积分获取办法
**限量**: 单次最大3000条数据，可以根据日期和板块代码循环提取权限：用户积累6000积分可调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 板块代码：xxxxxx.TDX |
| trade_date | str | N | 交易日期：格式YYYYMMDD |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 板块代码 |
| trade_date | str | Y | 交易日期 |
| con_code | str | Y | 成分股票代码 |
| con_name | str | Y | 成分股票名称 |

## 调用示例

```python
#获取通达信板块2025年5月13日的航运概念板块成分股
df = pro.tdx_member(trade_date='20250513', ts_code='880728.TDX')
```
# 通达信板块行情

**路径**: 股票数据/打板专题数据
**接口**: `tdx_daily`
**积分**: 6000
**描述**: 获取通达信各板块行情，包括成交和估值等数据
**限量**: 单次提取最大3000条数据，可根据板块代码和日期参数循环提取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 板块代码：xxxxxx.TDX |
| trade_date | str | N | 交易日期，格式YYYYMMDD,下同 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 板块代码 |
| trade_date | str | Y | 交易日期 |
| close | float | Y | 收盘点位 |
| open | float | Y | 开盘点位 |
| high | float | Y | 最高点位 |
| low | float | Y | 最低点位 |
| pre_close | float | Y | 昨日收盘点 |
| change | float | Y | 涨跌点位 |
| pct_change | float | Y | 涨跌幅% |
| vol | float | Y | 成交量（手） |
| amount | float | Y | 成交额（万元）, 对于期货指数，该字段存储持仓量 |
| rise | str | Y | 收盘涨速% |
| vol_ratio | float | Y | 量比 |
| turnover_rate | float | Y | 换手% |
| swing | float | Y | 振幅% |
| up_num | int | Y | 上涨家数 |
| down_num | int | Y | 下跌家数 |
| limit_up_num | int | Y | 涨停家数 |
| limit_down_num | int | Y | 跌停家数 |
| lu_days | int | Y | 连涨天数 |
| 3day | float | Y | 3日涨幅% |
| 5day | float | Y | 5日涨幅% |
| 10day | float | Y | 10日涨幅% |
| 20day | float | Y | 20日涨幅% |
| 60day | float | Y | 60日涨幅% |
| mtd | float | Y | 月初至今% |
| ytd | float | Y | 年初至今% |
| 1year | float | Y | 一年涨幅% |
| pe | str | Y | 市盈率 |
| pb | str | Y | 市净率 |
| float_mv | float | Y | 流通市值(亿) |
| ab_total_mv | float | Y | AB股总市值（亿） |
| float_share | float | Y | 流通股(亿) |
| total_share | float | Y | 总股本(亿) |
| bm_buy_net | float | Y | 主买净额(元) |
| bm_buy_ratio | float | Y | 主买占比% |
| bm_net | float | Y | 主力净额 |
| bm_ratio | float | Y | 主力占比% |

## 调用示例

```python
#获取通达信2025年5月13日概念板块行情
df = pro.tdx_daily(trade_date='20250513')
```
# 东财概念板块行情

**路径**: 股票数据/打板专题数据
**接口**: `dc_daily`
**积分**: 6000
**描述**: 获取东财概念板块、行业指数板块、地域板块行情数据，历史数据开始于2020年限量：单次最大2000条数据，可根据日期参数循环获取权限：用户积累6000积分可调取，具体请参阅积分获取办法注意：本接口只限个人学习和研究使用，如需商业用途，请自行联系东方财富解决数据采购问题。
**限量**: 单次最大2000条数据，可根据日期参数循环获取权限：用户积累6000积分可调取，具体请参阅积分获取办法注意：本接口只限个人学习和研究使用，如需商业用途，请自行联系东方财富解决数据采购问题。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 板块代码（格式：xxxxx.DC) |
| trade_date | str | N | 交易日期(格式：YYYYMMDD下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| idx_type | str | N | 板块类型： 概念板块、行业板块、地域板块 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 板块代码 |
| trade_date | str | Y | 交易日 |
| close | float | Y | 收盘点位 |
| open | float | Y | 开盘点位 |
| high | float | Y | 最高点位 |
| low | float | Y | 最低点位 |
| change | float | Y | 涨跌点位 |
| pct_change | float | Y | 涨跌幅 |
| vol | float | Y | 成交量 |
| amount | float | Y | 成交额 |
| swing | float | Y | 振幅 |
| turnover_rate | float | Y | 换手率 |

## 调用示例

```python
#获取东方财富2025年5月13日概念板块行情
df = pro.dc_daily(trade_date='20250513')
```
# 港股实时日线

**路径**: 港股数据
**接口**: `rt_hk_k`
**描述**: 获取港股实时日k线行情，支持按股票代码及股票代码通配符一次性提取全部股票实时日k线行情限量：单次最大可提取5000条数据积分：本接口是单独开权限的数据，单独申请权限请参考权限列表
**限量**: 单次最大可提取5000条数据积分：本接口是单独开权限的数据，单独申请权限请参考权限列表

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 支持通配符方式，e.g. 00001.HK、02*.HK |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| pre_close | float | Y | 昨收价 |
| close | float | Y | 收盘价 |
| high | float | Y | 最高价 |
| open | float | Y | 开盘价 |
| low | float | Y | 最低价 |
| vol | float | Y | 成交量（股） |
| amount | float | Y | 成交额(元) |

## 调用示例

```python
#获取特定股票实时日线
df = pro.rt_hk_k(ts_code='00001.HK')

#获取今日开盘以来部分港股实时日线
df = pro.rt_hk_k(ts_code='01*.HK')
```
# 未知接口

# ETF基础信息

**路径**: ETF专题
**接口**: `etf_basic`
**积分**: 8000
**描述**: 获取国内ETF基础信息，包括了QDII。数据来源与沪深交易所公开披露信息。限量：单次请求最大放回5000条数据（当前ETF总数未超过2000）权限：用户积8000积分可调取，具体请参阅积分获取办法
**限量**: 单次请求最大放回5000条数据（当前ETF总数未超过2000）权限：用户积8000积分可调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | ETF代码（带.SZ/.SH后缀的6位数字，如：159526.SZ） |
| index_code | str | N | 跟踪指数代码 |
| list_date | str | N | 上市日期（格式：YYYYMMDD） |
| list_status | str | N | 上市状态（L上市 D退市 P待上市） |
| exchange | str | N | 交易所（SH上交所 SZ深交所） |
| mgr | str | N | 管理人（简称，e.g.华夏基金) |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 基金交易代码 |
| csname | str | Y | ETF中文简称 |
| extname | str | Y | ETF扩位简称(对应交易所简称) |
| cname | str | Y | 基金中文全称 |
| index_code | str | Y | ETF基准指数代码 |
| index_name | str | Y | ETF基准指数中文全称 |
| setup_date | str | Y | 设立日期（格式：YYYYMMDD） |
| list_date | str | Y | 上市日期（格式：YYYYMMDD） |
| list_status | str | Y | 存续状态（L上市 D退市 P待上市） |
| exchange | str | Y | 交易所（上交所SH 深交所SZ） |
| mgr_name | str | Y | 基金管理人简称 |
| custod_name | str | Y | 基金托管人名称 |
| mgt_fee | float | Y | 基金管理人收取的费用 |
| etf_type | str | Y | 基金投资通道类型（境内、QDII） |

## 调用示例

```python
#获取当前所有上市的ETF列表
df = pro.etf_basic(list_status='L', fields='ts_code,extname,index_code,index_name,exchange,mgr_name')


#获取“嘉实基金”所有上市的ETF列表
df = pro.etf_basic(mgr='嘉实基金'， list_status='L', fields='ts_code,extname,index_code,index_name,exchange,etf_type')


#获取“嘉实基金”在深交所上市的所有ETF列表
df = pro.etf_basic(mgr='嘉实基金'， list_status='L', exchange='SZ', fields='ts_code,extname,index_code,index_name,exchange,etf_type')


#获取以沪深300指数为跟踪指数的所有上市的ETF列表
df = pro.etf_basic(index_code='000300.SH', fields='ts_code,extname,index_code,index_name,exchange,mgr_name')
```
# ETF基准指数列表

**路径**: ETF专题
**接口**: `etf_index`
**积分**: 8000
**描述**: 获取ETF基准指数列表信息限量：单次请求最大返回5000行数据（当前未超过2000个）权限：用户积累8000积分可调取，具体请参阅积分获取办法
**限量**: 单次请求最大返回5000行数据（当前未超过2000个）权限：用户积累8000积分可调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 指数代码 |
| pub_date | str | N | 发布日期（格式：YYYYMMDD） |
| base_date | str | N | 指数基期（格式：YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 指数代码 |
| indx_name | str | Y | 指数全称 |
| indx_csname | str | Y | 指数简称 |
| pub_party_name | str | Y | 指数发布机构 |
| pub_date | str | Y | 指数发布日期 |
| base_date | str | Y | 指数基日 |
| bp | float | Y | 指数基点(点) |
| adj_circle | str | Y | 指数成份证券调整周期 |

## 调用示例

```python
#获取当前ETF跟踪的基准指数列表
df = pro.etf_index(fields='ts_code,indx_name,pub_date,bp')
```
# ETF历史分钟行情

**路径**: ETF专题
**接口**: `stk_mins`
**描述**: 获取ETF分钟数据，支持1min/5min/15min/30min/60min行情，提供Python SDK和 http Restful API两种方式限量：单次最大8000行数据，可以通过股票代码和时间循环获取，本接口可以提供超过10年ETF历史分钟数据权限：正式权限请参阅 权限说明
**限量**: 单次最大8000行数据，可以通过股票代码和时间循环获取，本接口可以提供超过10年ETF历史分钟数据权限：正式权限请参阅 权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | ETF代码，e.g. 159001.SZ |
| freq | str | Y | 分钟频度（1min/5min/15min/30min/60min） |
| start_date | datetime | N | 开始日期 格式：2025-06-01 09:00:00 |
| end_date | datetime | N | 结束时间 格式：2025-06-20 19:00:00 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | ETF代码 |
| trade_time | str | Y | 交易时间 |
| open | float | Y | 开盘价 |
| close | float | Y | 收盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| vol | int | Y | 成交量 |
| amount | float | Y | 成交金额 |

## 调用示例

```python
pro = ts.pro_api()

#获取沪深300ETF华夏510330.SH的历史分钟数据
df = pro.stk_mins(ts_code='510330.SH', freq='1min', start_date='2025-06-20 09:00:00', end_date='2025-06-20 19:00:00')
```
# 港股财务指标数据

**路径**: 港股数据
**接口**: `hk_fina_indicator`
**积分**: 15000
**描述**: 获取港股上市公司财务指标数据，为避免服务器压力，现阶段每次请求最多返回200条记录，可通过设置日期多次请求获取更多数据。权限：需单独开权限或有15000积分，具体权限信息请参考权限列表提示：当前接口按单只股票获取其历史数据，单次请求最大返回10000行数据，可循环提取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| period | str | N | 报告期(格式：YYYYMMDD） |
| report_type | str | N | 报告期类型（Q1一季报Q2半年报Q3三季报Q4年报） |
| start_date | str | N | 报告期开始日期(格式：YYYYMMDD） |
| end_date | str | N | 报告结束日期(格式：YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| name | str | Y | 股票名称 |
| end_date | str | Y | 报告期 |
| ind_type | str | Y | 报告类型,Q-按报告期(季度),Y-按年度 |
| report_type | str | Y | 报告期类型 |
| std_report_date | str | Y | 标准报告期 |
| per_netcash_operate | float | Y | 每股经营现金流(元) |
| per_oi | float | Y | 每股营业收入(元) |
| bps | float | Y | 每股净资产(元) |
| basic_eps | float | Y | 基本每股收益(元) |
| diluted_eps | float | Y | 稀释每股收益(元) |
| operate_income | float | Y | 营业总收入(元) |
| operate_income_yoy | float | Y | 营业总收入同比增长(%) |
| gross_profit | float | Y | 毛利润(元) |
| gross_profit_yoy | float | Y | 毛利润同比增长(%) |
| holder_profit | float | Y | 归母净利润(元) |
| holder_profit_yoy | float | Y | 归母净利润同比增长(%) |
| gross_profit_ratio | float | Y | 毛利率(%) |
| eps_ttm | float | Y | ttm每股收益(元) |
| operate_income_qoq | float | Y | 营业总收入滚动环比增长(%) |
| net_profit_ratio | float | Y | 净利率(%) |
| roe_avg | float | Y | 平均净资产收益率(%) |
| gross_profit_qoq | float | Y | 毛利润滚动环比增长(%) |
| roa | float | Y | 总资产净利率(%) |
| holder_profit_qoq | float | Y | 归母净利润滚动环比增长(%) |
| roe_yearly | float | Y | 年化净资产收益率(%) |
| roic_yearly | float | Y | 年化投资回报率(%) |
| total_assets | float | Y | 资产总额 |
| total_liabilities | float | Y | 负债总额 |
| tax_ebt | float | Y | 所得税/利润总额(%) |
| ocf_sales | float | Y | 经营现金流/营业收入(%) |
| total_parent_equity | float | Y | 本公司权益持有人应占权益 |
| debt_asset_ratio | float | Y | 资产负债率(%) |
| operate_profit | float | Y | 经营盈利 |
| pretax_profit | float | Y | 除税前盈利 |
| netcash_operate | float | Y | 经营活动所得现金流量净额 |
| netcash_invest | float | Y | 投资活动耗用现金流量净额 |
| netcash_finance | float | Y | 融资活动耗用现金流量净额 |
| end_cash | float | Y | 期末的现金及现金等价物 |
| divi_ratio | float | Y | 分红比例 |
| dividend_rate | float | Y | 股息率 |
| current_ratio | float | Y | 流动比率(倍) |
| common_acs | float | Y | 普通股应计股息 |
| currentdebt_debt | float | Y | 流动负债/总负债(%) |
| issued_common_shares | float | Y | 已发行普通股 |
| hk_common_shares | float | Y | 港股本 |
| per_shares | float | Y | 每手股数 |
| total_market_cap | float | Y | 总市值 |
| hksk_market_cap | float | Y | 港股市值 |
| pe_ttm | float | Y | 滚动市盈率 |
| pb_ttm | float | Y | 滚动市净率 |
| report_date_sq | str | Y | 季报日期 |
| report_type_sq | str | Y | 报告类型 |
| operate_income_sq | float | Y | 营业收入 |
| dps_hkd | float | Y | 每股股息（港元） |
| operate_income_qoq_sq | float | Y | 营业收入环比 |
| net_profit_ratio_sq | float | Y | 净利润率 |
| holder_profit_sq | float | Y | 归属于股东净利润 |
| holder_profit_qoq_sq | float | Y | 归母净利润环比 |
| roe_avg_sq | float | Y | 平均净资产收益率 |
| pe_ttm_sq | float | Y | 季报滚动市盈率 |
| pb_ttm_sq | float | Y | 季报滚动市净率 |
| roa_sq | float | Y | 总资产收益率 |
| start_date | float | Y | 会计年度起始日 |
| fiscal_year | float | Y | 会计年度截止日 |
| currency | str | Y | 币种 港元（hkd） |
| is_cny_code | float | Y | 是否人民币代码 |
| dps_hkd_ly | float | Y | 上一年每股股息 |
| org_type | str | Y | 企业类型 |
| premium_income | float | Y | 保费收入 |
| premium_income_yoy | float | Y | 保费收入同比 |
| net_interest_income | float | Y | 净利息收入 |
| net_interest_income_yoy | float | Y | 净利息收入同比 |
| fee_commission_income | float | Y | 手续费及佣金收入 |
| fee_commission_income_yoy | float | Y | 手续费及佣金收入同比 |
| accounts_rece_tdays | float | Y | 应收账款周转率(次) |
| inventory_tdays | float | Y | 存货周转率(次) |
| current_assets_tdays | float | Y | 流动资产周转率(次) |
| total_assets_tdays | float | Y | 总资产周转率(次) |
| premium_expense | float | Y | 保险赔付支出 |
| loan_deposit | float | Y | 贷款/存款 |
| loan_equity | float | Y | 贷款/股东权益 |
| loan_assets | float | Y | 贷款/总资产 |
| deposit_equity | float | Y | 存款/股东权益 |
| deposit_assets | float | Y | 存款/总资产 |
| equity_multiplier | float | Y | 权益乘数 |
| equity_ratio | float | Y | 产权比率 |

## 调用示例

```python
pro = ts.pro_api()

#获取港股腾讯控股00700.HK股票2014年度的财务指标数据
df = pro.hk_fina_indicator(ts_code='00700.HK', period='20241231')

#获取港股腾讯控股00700.HK股票历年年报财务指标数据
df = pro.hk_fina_indicator(ts_code='00700.HK', report_type='Q4')
```
# 港股利润表

**路径**: 港股数据
**接口**: `hk_income`
**积分**: 15000
**描述**: 获取港股上市公司财务利润表数据权限：需单独开权限或有15000积分，具体权限信息请参考权限列表提示：当前接口按单只股票获取其历史数据，单次请求最大返回10000行数据，可循环提取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| period | str | N | 报告期(格式：YYYYMMDD） |
| ind_name | str | N | 指标名（如：营业额） |
| start_date | str | N | 报告期开始日期（格式：YYYYMMDD） |
| end_date | str | N | 报告结束始日期（格式：YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| end_date | str | Y | 报告期 |
| name | str | Y | 股票名称 |
| ind_name | str | Y | 财务科目名称 |
| ind_value | float | Y | 财务科目值 |

## 调用示例

```python
pro = ts.pro_api()

#获取腾讯控股00700.HK股票的2024年度利润表数据
df = pro.hk_income(ts_code='00700.HK', period='20241231')

#获取腾讯控股00700.HK股票利润表历年营业额数据
df = pro.hk_income(ts_code='00700.HK', ind_name='营业额')
```
# 港股资产负债表

**路径**: 港股数据
**接口**: `hk_balancesheet`
**积分**: 15000
**描述**: 获取港股上市公司资产负债表权限：需单独开权限或有15000积分，具体权限信息请参考权限列表提示：当前接口按单只股票获取其历史数据，单次请求最大返回10000行数据，可循环提取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| period | str | N | 报告期(格式：YYYYMMDD） |
| ind_name | str | N | 指标名（如：应收帐款） |
| start_date | str | N | 报告期开始日期（格式：YYYYMMDD） |
| end_date | str | N | 报告结束始日期（格式：YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| name | str | Y | 股票名称 |
| end_date | str | Y | 报告期 |
| ind_name | str | Y | 财务科目名称 |
| ind_value | float | Y | 财务科目值 |

## 调用示例

```python
pro = ts.pro_api()

#获取港股腾讯控股00700.HK股票2014年度的资产负债表数据
df = pro.hk_balancesheet(ts_code='00700.HK', period='20241231')

#获取港股腾讯控股00700.HK股票历年应收帐款指标数据
df = pro.hk_balancesheet(ts_code='00700.HK', ind_name='应收帐款')
```
# 港股现金流量表

**路径**: 港股数据
**接口**: `hk_cashflow`
**积分**: 15000
**描述**: 获取港股上市公司现金流量表数据权限：需单独开权限或有15000积分，具体权限信息请参考权限列表提示：当前接口按单只股票获取其历史数据，单次请求最大返回10000行数据，可循环提取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| period | str | N | 报告期(格式：YYYYMMDD） |
| ind_name | str | N | 指标名（如：新增贷款） |
| start_date | str | N | 报告期开始日期（格式：YYYYMMDD） |
| end_date | str | N | 报告结束始日期（格式：YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| end_date | str | Y | 报告期 |
| name | str | Y | 股票名称 |
| ind_name | str | Y | 财务科目名称 |
| ind_value | float | Y | 财务科目值 |

## 调用示例

```python
pro = ts.pro_api()


#获取腾讯控股00700.HK股票的2024年度资产负债表数据
df = pro.hk_cashflow(ts_code='00700.HK', period='20241231')

#获取腾讯控股00700.HK股票资产负债表历年新增借款数据
df = pro.hk_cashflow(ts_code='00700.HK', ind_name='新增借款')
```
# 可转债技术因子(专业版)

**路径**: 债券专题
**接口**: `cb_factor_pro`
**积分**: 5000
**描述**: 获取可转债每日技术面因子数据，用于跟踪可转债当前走势情况，数据由Tushare社区自产，覆盖全历史；输出参数_bfq表示不复权，_qfq表示前复权 _hfq表示后复权，描述中说明了因子的默认传参，如需要特殊参数或者更多因子可以联系管理员评估限量：单次调取最多返回10000条数据，可以通过日期参数循环积分：5000积分每分钟可以请求30次，8000积分以上每分钟500次，具体请参阅积分获取办法
**限量**: 单次调取最多返回10000条数据，可以通过日期参数循环积分：5000积分每分钟可以请求30次，8000积分以上每分钟500次，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 可转债代码 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| trade_date | str | N | 交易日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 转债代码 |
| trade_date | str | Y | 交易日期 |
| open | float | Y | 开盘价 |
| high | float | Y | 最高价 |
| low | float | Y | 最低价 |
| close | float | Y | 收盘价 |
| pre_close | float | Y | 昨收价 |
| change | float | Y | 涨跌额 |
| pct_change | float | Y | 涨跌幅 （未复权，如果是复权请用 通用行情接口 ） |
| vol | float | Y | 成交量 （手） |
| amount | float | Y | 成交金额(万元) |
| asi_bfq | float | Y | 振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10 |
| asit_bfq | float | Y | 振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10 |
| atr_bfq | float | Y | 真实波动N日平均值-CLOSE, HIGH, LOW, N=20 |
| bbi_bfq | float | Y | BBI多空指标-CLOSE, M1=3, M2=6, M3=12, M4=20 |
| bias1_bfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias2_bfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| bias3_bfq | float | Y | BIAS乖离率-CLOSE, L1=6, L2=12, L3=24 |
| boll_lower_bfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_mid_bfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| boll_upper_bfq | float | Y | BOLL指标，布林带-CLOSE, N=20, P=2 |
| brar_ar_bfq | float | Y | BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26 |
| brar_br_bfq | float | Y | BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26 |
| cci_bfq | float | Y | 顺势指标又叫CCI指标-CLOSE, HIGH, LOW, N=14 |
| cr_bfq | float | Y | CR价格动量指标-CLOSE, HIGH, LOW, N=20 |
| dfma_dif_bfq | float | Y | 平行线差指标-CLOSE, N1=10, N2=50, M=10 |
| dfma_difma_bfq | float | Y | 平行线差指标-CLOSE, N1=10, N2=50, M=10 |
| dmi_adx_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_adxr_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_mdi_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| dmi_pdi_bfq | float | Y | 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6 |
| downdays | float | Y | 连跌天数 |
| updays | float | Y | 连涨天数 |
| dpo_bfq | float | Y | 区间震荡线-CLOSE, M1=20, M2=10, M3=6 |
| madpo_bfq | float | Y | 区间震荡线-CLOSE, M1=20, M2=10, M3=6 |
| ema_bfq_10 | float | Y | 指数移动平均-N=10 |
| ema_bfq_20 | float | Y | 指数移动平均-N=20 |
| ema_bfq_250 | float | Y | 指数移动平均-N=250 |
| ema_bfq_30 | float | Y | 指数移动平均-N=30 |
| ema_bfq_5 | float | Y | 指数移动平均-N=5 |
| ema_bfq_60 | float | Y | 指数移动平均-N=60 |
| ema_bfq_90 | float | Y | 指数移动平均-N=90 |
| emv_bfq | float | Y | 简易波动指标-HIGH, LOW, VOL, N=14, M=9 |
| maemv_bfq | float | Y | 简易波动指标-HIGH, LOW, VOL, N=14, M=9 |
| expma_12_bfq | float | Y | EMA指数平均数指标-CLOSE, N1=12, N2=50 |
| expma_50_bfq | float | Y | EMA指数平均数指标-CLOSE, N1=12, N2=50 |
| kdj_bfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_d_bfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| kdj_k_bfq | float | Y | KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3 |
| ktn_down_bfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_mid_bfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| ktn_upper_bfq | float | Y | 肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10 |
| lowdays | float | Y | LOWRANGE(LOW)表示当前最低价是近多少周期内最低价的最小值 |
| topdays | float | Y | TOPRANGE(HIGH)表示当前最高价是近多少周期内最高价的最大值 |
| ma_bfq_10 | float | Y | 简单移动平均-N=10 |
| ma_bfq_20 | float | Y | 简单移动平均-N=20 |
| ma_bfq_250 | float | Y | 简单移动平均-N=250 |
| ma_bfq_30 | float | Y | 简单移动平均-N=30 |
| ma_bfq_5 | float | Y | 简单移动平均-N=5 |
| ma_bfq_60 | float | Y | 简单移动平均-N=60 |
| ma_bfq_90 | float | Y | 简单移动平均-N=90 |
| macd_bfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_dea_bfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| macd_dif_bfq | float | Y | MACD指标-CLOSE, SHORT=12, LONG=26, M=9 |
| mass_bfq | float | Y | 梅斯线-HIGH, LOW, N1=9, N2=25, M=6 |
| ma_mass_bfq | float | Y | 梅斯线-HIGH, LOW, N1=9, N2=25, M=6 |
| mfi_bfq | float | Y | MFI指标是成交量的RSI指标-CLOSE, HIGH, LOW, VOL, N=14 |
| mtm_bfq | float | Y | 动量指标-CLOSE, N=12, M=6 |
| mtmma_bfq | float | Y | 动量指标-CLOSE, N=12, M=6 |
| obv_bfq | float | Y | 能量潮指标-CLOSE, VOL |
| psy_bfq | float | Y | 投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6 |
| psyma_bfq | float | Y | 投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6 |
| roc_bfq | float | Y | 变动率指标-CLOSE, N=12, M=6 |
| maroc_bfq | float | Y | 变动率指标-CLOSE, N=12, M=6 |
| rsi_bfq_12 | float | Y | RSI指标-CLOSE, N=12 |
| rsi_bfq_24 | float | Y | RSI指标-CLOSE, N=24 |
| rsi_bfq_6 | float | Y | RSI指标-CLOSE, N=6 |
| taq_down_bfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_mid_bfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| taq_up_bfq | float | Y | 唐安奇通道(海龟)交易指标-HIGH, LOW, 20 |
| trix_bfq | float | Y | 三重指数平滑平均线-CLOSE, M1=12, M2=20 |
| trma_bfq | float | Y | 三重指数平滑平均线-CLOSE, M1=12, M2=20 |
| vr_bfq | float | Y | VR容量比率-CLOSE, VOL, M1=26 |
| wr_bfq | float | Y | W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6 |
| wr1_bfq | float | Y | W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6 |
| xsii_td1_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td2_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td3_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |
| xsii_td4_bfq | float | Y | 薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7 |

## 调用示例

```python
pro = ts.pro_api()

#获取鹤21转债113632.SH所以有历史因子数据
df = pro.cb_factor_pro(ts_code=113632.SH')

#获取交易日期为20250724当天所有可转债的因子数据
df = pro.hk_income(trade_date='20250724')
```
# 美股财务指标数据

**路径**: 美股数据
**接口**: `us_fina_indicator`
**积分**: 15000
**描述**: 获取美股上市公司财务指标数据，目前只覆盖主要美股和中概股。为避免服务器压力，现阶段每次请求最多返回200条记录，可通过设置日期多次请求获取更多数据。权限：需单独开权限或有15000积分，具体权限信息请参考权限列表提示：当前接口按单只股票获取其历史数据，单次请求最大返回10000行数据，可循环提取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| period | str | N | 报告期（格式：YYYYMMDD，每个季度最后一天的日期，如20241231) |
| report_type | str | N | 报告期类型(Q1一季报Q2半年报Q3三季报Q4年报) |
| start_date | str | N | 报告期开始时间（格式：YYYYMMDD） |
| end_date | str | N | 报告结束始时间（格式：YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| end_date | str | Y | 报告期 |
| ind_type | str | Y | 报告类型,Q1一季报,Q2中报,Q3三季报,Q4年报 |
| security_name_abbr | str | Y | 股票名称 |
| accounting_standards | str | Y | 会计准则 |
| notice_date | str | Y | 公告日期 |
| start_date | str | Y | 报告期开始时间 |
| std_report_date | str | Y | 标准报告期 |
| financial_date | str | Y | 年结日 |
| currency | str | Y | 币种 |
| date_type | str | Y | 报告期类型 |
| report_type | str | Y | 报告类型 |
| operate_income | float | Y | 收入 |
| operate_income_yoy | float | Y | 收入增长 |
| gross_profit | float | Y | 毛利 |
| gross_profit_yoy | float | Y | 毛利增长 |
| parent_holder_netprofit | float | Y | 归母净利润 |
| parent_holder_netprofit_yoy | float | Y | 归母净利润增长 |
| basic_eps | float | Y | 基本每股收益 |
| diluted_eps | float | Y | 稀释每股收益 |
| gross_profit_ratio | float | Y | 销售毛利率 |
| net_profit_ratio | float | Y | 销售净利率 |
| accounts_rece_tr | float | Y | 应收账款周转率(次) |
| inventory_tr | float | Y | 存货周转率(次) |
| total_assets_tr | float | Y | 总资产周转率(次) |
| accounts_rece_tdays | float | Y | 应收账款周转天数 |
| inventory_tdays | float | Y | 存货周转天数 |
| total_assets_tdays | float | Y | 总资产周转天数 |
| roe_avg | float | Y | 净资产收益率 |
| roa | float | Y | 总资产净利率 |
| current_ratio | float | Y | 流动比率(倍) |
| speed_ratio | float | Y | 速动比率(倍) |
| ocf_liqdebt | float | Y | 经营业务现金净额/流动负债 |
| debt_asset_ratio | float | Y | 资产负债率 |
| equity_ratio | float | Y | 产权比率 |
| basic_eps_yoy | float | Y | 基本每股收益同比增长 |
| gross_profit_ratio_yoy | float | Y | 毛利率同比增长(%) |
| net_profit_ratio_yoy | float | Y | 净利率同比增长(%) |
| roe_avg_yoy | float | Y | 平均净资产收益率同比增长(%) |
| roa_yoy | float | Y | 净资产收益率同比增长(%) |
| debt_asset_ratio_yoy | float | Y | 资产负债率同比增长(%) |
| current_ratio_yoy | float | Y | 流动比率同比增长(%) |
| speed_ratio_yoy | float | Y | 速动比率同比增长(%) |
| currency_abbr | str | Y | 币种 |
| total_income | float | Y | 收入总额 |
| total_income_yoy | float | Y | 收入总额同比增长 |
| premium_income | float | Y | 保费收入 |
| premium_income_yoy | float | Y | 保费收入同比 |
| basic_eps_cs | float | Y | 基本每股收益 |
| basic_eps_cs_yoy | float | Y | 基本每股收益同比增长 |
| diluted_eps_cs | float | Y | 稀释每股收益 |
| payout_ratio | float | Y | 保费收入/赔付支出 |
| capitial_ratio | float | Y | 总资产周转率 |
| roe | float | Y | 净资产收益率 |
| roe_yoy | float | Y | 净资产收益率同比增长 |
| debt_ratio | float | Y | 资产负债率 |
| debt_ratio_yoy | float | Y | 资产负债率同比增长 |
| net_interest_income | float | Y | 净利息收入 |
| net_interest_income_yoy | float | Y | 净利息收入增长 |
| diluted_eps_cs_yoy | float | Y | 稀释每股收益增长 |
| loan_loss_provision | float | Y | 贷款损失准备 |
| loan_loss_provision_yoy | float | Y | 贷款损失准备增长 |
| loan_deposit | float | Y | 贷款/存款 |
| loan_equity | float | Y | 贷款/股东权益(倍) |
| loan_assets | float | Y | 贷款/总资产 |
| deposit_equity | float | Y | 存款/股东权益(倍) |
| deposit_assets | float | Y | 存款/总资产 |
| rol | float | Y | 贷款回报率 |
| rod | float | Y | 存款回报率 |

## 调用示例

```python
pro = ts.pro_api()

#获取美股英伟达NVDA股票2024年度的财务指标数据
df = pro.us_fina_indicator(ts_code='NVDA', period='20241231')

#获取美股英伟达NVDA股票历年年报财务指标数据
df = pro.us_fina_indicator(ts_code='NVDA', report_type='Q4')
```
# 美股利润表

**路径**: 美股数据
**接口**: `us_income`
**积分**: 15000
**描述**: 获取美股上市公司财务利润表数据（目前只覆盖主要美股和中概股）权限：需单独开权限或有15000积分，具体权限信息请参考权限列表提示：当前接口按单只股票获取其历史数据，单次请求最大返回10000行数据，可循环提取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| period | str | N | 报告期（格式：YYYYMMDD，每个季度最后一天的日期，如20241231) |
| ind_name | str | N | 指标名(如：新增借款） |
| report_type | str | N | 报告期类型(Q1一季报Q2半年报Q3三季报Q4年报) |
| start_date | str | N | 报告期开始时间（格式：YYYYMMDD） |
| end_date | str | N | 报告结束始时间（格式：YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| end_date | str | Y | 报告期 |
| ind_type | str | Y | 报告期类型(Q1一季报Q2半年报Q3三季报Q4年报) |
| name | str | Y | 股票名称 |
| ind_name | str | Y | 财务科目名称 |
| ind_value | float | Y | 财务科目值 |
| report_type | str | Y | 报告类型 |

## 调用示例

```python
pro = ts.pro_api()

#获取美股英伟达NVDA股票的2024年度利润表数据
df = pro.us_income(ts_code='NVDA', period='20241231')

#获取美股英伟达NVDA股票利润表历年营业额数据
df = pro.us_income(ts_code='NVDA', ind_name='营业额')
```
# 美股资产负债表

**路径**: 美股数据
**接口**: `us_balancesheet`
**积分**: 15000
**描述**: 获取美股上市公司资产负债表（目前只覆盖主要美股和中概股）权限：需单独开权限或有15000积分，具体权限信息请参考权限列表提示：当前接口按单只股票获取其历史数据，单次请求最大返回10000行数据，可循环提取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| period | str | N | 报告期（格式：YYYYMMDD，每个季度最后一天的日期，如20241231) |
| ind_name | str | N | 指标名(如：新增借款） |
| report_type | str | N | 报告期类型(Q1一季报Q2半年报Q3三季报Q4年报) |
| start_date | str | N | 报告期开始时间（格式：YYYYMMDD） |
| end_date | str | N | 报告结束始时间（格式：YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| end_date | str | Y | 报告期 |
| ind_type | str | Y | 报告期类型(Q1一季报Q2半年报Q3三季报Q4年报) |
| name | str | Y | 股票名称 |
| ind_name | str | Y | 财务科目名称 |
| ind_value | float | Y | 财务科目值 |
| report_type | str | Y | 报告类型 |

## 调用示例

```python
pro = ts.pro_api()

#获取美股英伟达NVDA股票2014年度的资产负债表数据
df = pro.us_balancesheet(ts_code='NVDA', period='20241231')

#获取美股英伟达NVDA股票历年应收帐款指标数据
df = pro.us_balancesheet(ts_code='NVDA', ind_name='应收帐款')
```
# 美股现金流量表

**路径**: 美股数据
**接口**: `us_cashflow`
**积分**: 15000
**描述**: 获取美股上市公司现金流量表数据（目前只覆盖主要美股和中概股）权限：需单独开权限或有15000积分，具体权限信息请参考权限列表提示：当前接口按单只股票获取其历史数据，单次请求最大返回10000行数据，可循环提取

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| period | str | N | 报告期（格式：YYYYMMDD，每个季度最后一天的日期，如20241231) |
| ind_name | str | N | 指标名(如：新增借款） |
| report_type | str | N | 报告期类型(Q1一季报Q2半年报Q3三季报Q4年报) |
| start_date | str | N | 报告期开始时间（格式：YYYYMMDD） |
| end_date | str | N | 报告结束始时间（格式：YYYYMMDD） |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| end_date | str | Y | 报告期 |
| ind_type | str | Y | 报告期类型(Q1一季报Q2半年报Q3三季报Q4年报) |
| name | str | Y | 股票名称 |
| ind_name | str | Y | 财务科目名称 |
| ind_value | float | Y | 财务科目值 |
| report_type | str | Y | 报告类型 |

## 调用示例

```python
pro = ts.pro_api()


#获取美股英伟达NVDA股票的2024年度现金流量表数据
df = pro.us_cashflow(ts_code='NVDA', period='20241231')

#获取美股英伟达NVDA股票现金流量表历年新增借款数据
df = pro.us_cashflow(ts_code='NVDA', ind_name='新增借款')
```
# ST股票列表

**路径**: 股票数据/基础数据
**接口**: `stock_st`
**积分**: 3000
**描述**: 获取ST股票列表，可根据交易日期获取历史上每天的ST列表权限：3000积分起提示：每天上午9:20更新，单次请求最大返回1000行数据，可循环提取,本接口数据从20160101开始,太早历史无法补齐

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期（格式：YYYYMMDD下同） |
| start_date | str | N | 开始时间 |
| end_date | str | N | 结束时间 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| name | str | Y | 股票名称 |
| trade_date | str | Y | 交易日期 |
| type | str | Y | 类型 |
| type_name | str | Y | 类型名称 |

## 调用示例

```python
pro = ts.pro_api()

#获取20250813日所有的ST股票
df = pro.stock_st(trade_date='20250813')
```
# 沪深港通股票列表

**路径**: 股票数据/基础数据
**接口**: `stock_hsgt`
**积分**: 3000
**描述**: 获取沪深港通股票列表权限：3000积分起提示：每天上午9:20更新，单次请求最大返回2000行数据，可根据类型循环提取,本接口数据从20250812开始

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期（格式：YYYYMMDD） |
| type | str | Y | 类型（参考下表） |
| start_date | str | N | 开始时间 |
| end_date | str | N | 结束时间 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| type | str | Y | 类型 |
| name | str | Y | 股票名称 |
| type_name | str | Y | 类型名称 |

## 调用示例

```python
pro = ts.pro_api()

#获取20250813日深股通的股票列表
df = pro.stock_hsgt(trade_date='20250813',type='HK_SZ')
```
# AH股比价

**路径**: 股票数据/特色数据
**接口**: `stk_ah_comparison`
**积分**: 5000
**描述**: AH股比价数据，可根据交易日期获取历史权限：5000积分起提示：每天盘后17:00更新，单次请求最大返回1000行数据，可循环提取,本接口数据从20250812开始，由于历史不好补充，只能累积

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| hk_code | str | N | 港股股票代码（xxxxx.HK) |
| ts_code | str | N | A股票代码(xxxxxx.SH/SZ/BJ) |
| trade_date | str | N | 交易日期（格式：YYYYMMDD下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| hk_code | str | Y | 港股股票代码 |
| ts_code | str | Y | A股股票代码 |
| trade_date | str | Y | 交易日期 |
| hk_name | str | Y | 港股股票名称 |
| hk_pct_chg | float | Y | 港股股票涨跌幅 |
| hk_close | float | Y | 港股股票收盘价 |
| name | str | Y | A股股票名称 |
| close | float | Y | A股股票收盘价 |
| pct_chg | float | Y | A股股票涨跌幅 |
| ah_comparison | float | Y | 比价(A/H) |
| ah_premium | float | Y | 溢价(A/H)% |

## 调用示例

```python
pro = ts.pro_api()

#获取20250812日所有的AH股比价数据
df = pro.stk_ah_comparison(trade_date='20250812')
```
# ETF实时日线

**路径**: ETF专题
**接口**: `rt_etf_k`
**描述**: 获取ETF实时日k线行情，支持按ETF代码或代码通配符一次性提取全部ETF实时日k线行情

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 支持通配符方式，e.g. 5*.SH、15*.SZ、159101.SZ |
| topic | str | Y | 分类参数，取上海ETF时，需要输入'HQ_FND_TICK'，参考下面例子 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | ETF代码 |
| name | None | Y | ETF名称 |
| pre_close | float | Y | 昨收价 |
| high | float | Y | 最高价 |
| open | float | Y | 开盘价 |
| low | float | Y | 最低价 |
| close | float | Y | 收盘价（最新价） |
| vol | int | Y | 成交量（股） |
| amount | int | Y | 成交金额（元） |
| num | int | Y | 开盘以来成交笔数 |
| ask_volume1 | int | N | 委托卖盘（股） |
| bid_volume1 | int | N | 委托买盘（股） |
| trade_time | str | N | 交易时间 |

## 调用示例

```python
#获取今日所有深市ETF实时日线和成交笔数
df = pro.rt_etf_k(ts_code='1*.SZ')

#获取今日沪市所有ETF实时日线和成交笔数
df = pro.rt_etf_k(ts_code='5*.SH', topic='HQ_FND_TICK')
```
# 港股复权因子

**路径**: 港股数据
**接口**: `hk_adjfactor`
**描述**: 获取港股每日复权因子数据，每天滚动刷新限量：单次最大6000行数据，可以根据日期循环权限：本接口是在开通港股日线权限后自动获取权限，权限请参考权限说明文档
**限量**: 单次最大6000行数据，可以根据日期循环权限：本接口是在开通港股日线权限后自动获取权限，权限请参考权限说明文档

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期（格式：YYYYMMDD，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| cum_adjfactor | float | Y | 累计复权因子 |
| close_price | float | Y | 收盘价 |

## 调用示例

```python
pro = ts.pro_api()

#获取港股单一股票复权因子
df = pro.hk_adjfactor(ts_code='00001.HK', start_date='20240101', end_date='20251022')

#获取港股某一日全部股票的复权因子
df = pro.hk_adjfactor(trade_date='20251031')
```
# 美股复权因子

**路径**: 美股数据
**接口**: `us_adjfactor`
**描述**: 获取美股每日复权因子数据，在每天美股收盘后滚动刷新限量：单次最大15000行数据，可以根据日期循环权限：本接口是在开通美股日线权限后自动获取权限，权限请参考权限说明文档
**限量**: 单次最大15000行数据，可以根据日期循环权限：本接口是在开通美股日线权限后自动获取权限，权限请参考权限说明文档

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码 |
| trade_date | str | N | 交易日期（格式：YYYYMMDD，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 股票代码 |
| trade_date | str | Y | 交易日期 |
| exchange | str | Y | 交易所 |
| cum_adjfactor | float | Y | 累计复权因子 |
| close_price | float | Y | 收盘价 |

## 调用示例

```python
pro = ts.pro_api()

#获取美股单一股票复权因子
df = pro.us_adjfactor(ts_code='AAPL', start_date='20240101', end_date='20251022')

#获取美股某一日全部股票的复权因子
df = pro.us_adjfactor(trade_date='20251031')
```
# rt_idx_k

**路径**: 指数专题
**接口**: `rt_idx_k`
**描述**: 获取交易所指数实时日线行情，支持按代码或代码通配符一次性提取全部交易所指数实时日k线行情

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 指数代码，支持通配符方式，e.g. 0*.SH、3*.SZ、000001.SH |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | 指数代码 |
| name | str | Y | 指数名称 |
| trade_time | str | Y | 交易时间 |
| close | float | Y | 现价 |
| pre_close | float | Y | 昨收 |
| high | float | Y | 最高价 |
| open | float | Y | 开盘价 |
| low | float | Y | 最低价 |
| vol | float | Y | 成交量 |
| amount | float | Y | 成交金额（元） |

## 调用示例

```python
#获取单个指数实时行情
df = pro.rt_idx_k(ts_code='000001.SH')

#获取多个指数实时行情,以上证综指和深证A指为例
df = pro.rt_idx_k(ts_code='000001.SH,399107.SZ')

#获取上交所所有指数实时行情，同时指定输出字段
df = pro.rt_idx_k(ts_code='0*.SH', fields='ts_code,name,close,vol')
```
# 现金流量表

**路径**: 股票数据/财务数据
**接口**: `cashflow`
**积分**: 2000
**描述**: 获取上市公司现金流量表积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用cashflow_vip接口（参数一致），需积攒5000积分。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| ann_date | str | N | 公告日期（YYYYMMDD格式，下同） |
| f_ann_date | str | N | 实际公告日期 |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |
| period | str | N | 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报) |
| report_type | str | N | 报告类型：见下方详细说明 |
| comp_type | str | N | 公司类型：1一般工商业 2银行 3保险 4证券 |
| is_calc | int | N | 是否计算报表 |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS股票代码 |
| ann_date | str | Y | 公告日期 |
| f_ann_date | str | Y | 实际公告日期 |
| end_date | str | Y | 报告期 |
| comp_type | str | Y | 公司类型(1一般工商业2银行3保险4证券) |
| report_type | str | Y | 报表类型 |
| end_type | str | Y | 报告期类型 |
| net_profit | float | Y | 净利润 |
| finan_exp | float | Y | 财务费用 |
| c_fr_sale_sg | float | Y | 销售商品、提供劳务收到的现金 |
| recp_tax_rends | float | Y | 收到的税费返还 |
| n_depos_incr_fi | float | Y | 客户存款和同业存放款项净增加额 |
| n_incr_loans_cb | float | Y | 向中央银行借款净增加额 |
| n_inc_borr_oth_fi | float | Y | 向其他金融机构拆入资金净增加额 |
| prem_fr_orig_contr | float | Y | 收到原保险合同保费取得的现金 |
| n_incr_insured_dep | float | Y | 保户储金净增加额 |
| n_reinsur_prem | float | Y | 收到再保业务现金净额 |
| n_incr_disp_tfa | float | Y | 处置交易性金融资产净增加额 |
| ifc_cash_incr | float | Y | 收取利息和手续费净增加额 |
| n_incr_disp_faas | float | Y | 处置可供出售金融资产净增加额 |
| n_incr_loans_oth_bank | float | Y | 拆入资金净增加额 |
| n_cap_incr_repur | float | Y | 回购业务资金净增加额 |
| c_fr_oth_operate_a | float | Y | 收到其他与经营活动有关的现金 |
| c_inf_fr_operate_a | float | Y | 经营活动现金流入小计 |
| c_paid_goods_s | float | Y | 购买商品、接受劳务支付的现金 |
| c_paid_to_for_empl | float | Y | 支付给职工以及为职工支付的现金 |
| c_paid_for_taxes | float | Y | 支付的各项税费 |
| n_incr_clt_loan_adv | float | Y | 客户贷款及垫款净增加额 |
| n_incr_dep_cbob | float | Y | 存放央行和同业款项净增加额 |
| c_pay_claims_orig_inco | float | Y | 支付原保险合同赔付款项的现金 |
| pay_handling_chrg | float | Y | 支付手续费的现金 |
| pay_comm_insur_plcy | float | Y | 支付保单红利的现金 |
| oth_cash_pay_oper_act | float | Y | 支付其他与经营活动有关的现金 |
| st_cash_out_act | float | Y | 经营活动现金流出小计 |
| n_cashflow_act | float | Y | 经营活动产生的现金流量净额 |
| oth_recp_ral_inv_act | float | Y | 收到其他与投资活动有关的现金 |
| c_disp_withdrwl_invest | float | Y | 收回投资收到的现金 |
| c_recp_return_invest | float | Y | 取得投资收益收到的现金 |
| n_recp_disp_fiolta | float | Y | 处置固定资产、无形资产和其他长期资产收回的现金净额 |
| n_recp_disp_sobu | float | Y | 处置子公司及其他营业单位收到的现金净额 |
| stot_inflows_inv_act | float | Y | 投资活动现金流入小计 |
| c_pay_acq_const_fiolta | float | Y | 购建固定资产、无形资产和其他长期资产支付的现金 |
| c_paid_invest | float | Y | 投资支付的现金 |
| n_disp_subs_oth_biz | float | Y | 取得子公司及其他营业单位支付的现金净额 |
| oth_pay_ral_inv_act | float | Y | 支付其他与投资活动有关的现金 |
| n_incr_pledge_loan | float | Y | 质押贷款净增加额 |
| stot_out_inv_act | float | Y | 投资活动现金流出小计 |
| n_cashflow_inv_act | float | Y | 投资活动产生的现金流量净额 |
| c_recp_borrow | float | Y | 取得借款收到的现金 |
| proc_issue_bonds | float | Y | 发行债券收到的现金 |
| oth_cash_recp_ral_fnc_act | float | Y | 收到其他与筹资活动有关的现金 |
| stot_cash_in_fnc_act | float | Y | 筹资活动现金流入小计 |
| free_cashflow | float | Y | 企业自由现金流量 |
| c_prepay_amt_borr | float | Y | 偿还债务支付的现金 |
| c_pay_dist_dpcp_int_exp | float | Y | 分配股利、利润或偿付利息支付的现金 |
| incl_dvd_profit_paid_sc_ms | float | Y | 其中:子公司支付给少数股东的股利、利润 |
| oth_cashpay_ral_fnc_act | float | Y | 支付其他与筹资活动有关的现金 |
| stot_cashout_fnc_act | float | Y | 筹资活动现金流出小计 |
| n_cash_flows_fnc_act | float | Y | 筹资活动产生的现金流量净额 |
| eff_fx_flu_cash | float | Y | 汇率变动对现金的影响 |
| n_incr_cash_cash_equ | float | Y | 现金及现金等价物净增加额 |
| c_cash_equ_beg_period | float | Y | 期初现金及现金等价物余额 |
| c_cash_equ_end_period | float | Y | 期末现金及现金等价物余额 |
| c_recp_cap_contrib | float | Y | 吸收投资收到的现金 |
| incl_cash_rec_saims | float | Y | 其中:子公司吸收少数股东投资收到的现金 |
| uncon_invest_loss | float | Y | 未确认投资损失 |
| prov_depr_assets | float | Y | 加:资产减值准备 |
| depr_fa_coga_dpba | float | Y | 固定资产折旧、油气资产折耗、生产性生物资产折旧 |
| amort_intang_assets | float | Y | 无形资产摊销 |
| lt_amort_deferred_exp | float | Y | 长期待摊费用摊销 |
| decr_deferred_exp | float | Y | 待摊费用减少 |
| incr_acc_exp | float | Y | 预提费用增加 |
| loss_disp_fiolta | float | Y | 处置固定、无形资产和其他长期资产的损失 |
| loss_scr_fa | float | Y | 固定资产报废损失 |
| loss_fv_chg | float | Y | 公允价值变动损失 |
| invest_loss | float | Y | 投资损失 |
| decr_def_inc_tax_assets | float | Y | 递延所得税资产减少 |
| incr_def_inc_tax_liab | float | Y | 递延所得税负债增加 |
| decr_inventories | float | Y | 存货的减少 |
| decr_oper_payable | float | Y | 经营性应收项目的减少 |
| incr_oper_payable | float | Y | 经营性应付项目的增加 |
| others | float | Y | 其他 |
| im_net_cashflow_oper_act | float | Y | 经营活动产生的现金流量净额(间接法) |
| conv_debt_into_cap | float | Y | 债务转为资本 |
| conv_copbonds_due_within_1y | float | Y | 一年内到期的可转换公司债券 |
| fa_fnc_leases | float | Y | 融资租入固定资产 |
| im_n_incr_cash_equ | float | Y | 现金及现金等价物净增加额(间接法) |
| net_dism_capital_add | float | Y | 拆出资金净增加额 |
| net_cash_rece_sec | float | Y | 代理买卖证券收到的现金净额(元) |
| credit_impa_loss | float | Y | 信用减值损失 |
| use_right_asset_dep | float | Y | 使用权资产折旧 |
| oth_loss_asset | float | Y | 其他资产减值损失 |
| end_bal_cash | float | Y | 现金的期末余额 |
| beg_bal_cash | float | Y | 减:现金的期初余额 |
| end_bal_cash_equ | float | Y | 加:现金等价物的期末余额 |
| beg_bal_cash_equ | float | Y | 减:现金等价物的期初余额 |
| update_flag | str | Y | 更新标志(1最新） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.cashflow(ts_code='600000.SH', start_date='20180101', end_date='20180730')
```

```python
df2 = pro.cashflow_vip(period='20181231',fields='')
```
# 业绩预告

**路径**: 股票数据/财务数据
**接口**: `forecast`
**积分**: 2000
**描述**: 获取业绩预告数据权限：用户需要至少2000积分才可以调取，具体请参阅积分获取办法提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用forecast_vip接口（参数一致），需积攒5000积分。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码(二选一) |
| ann_date | str | N | 公告日期 (二选一) |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |
| period | str | N | 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报) |
| type | str | N | 预告类型(预增/预减/扭亏/首亏/续亏/续盈/略增/略减) |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | TS股票代码 |
| ann_date | str | 公告日期 |
| end_date | str | 报告期 |
| type | str | 业绩预告类型(预增/预减/扭亏/首亏/续亏/续盈/略增/略减) |
| p_change_min | float | 预告净利润变动幅度下限（%） |
| p_change_max | float | 预告净利润变动幅度上限（%） |
| net_profit_min | float | 预告净利润下限（万元） |
| net_profit_max | float | 预告净利润上限（万元） |
| last_parent_net | float | 上年同期归属母公司净利润 |
| first_ann_date | str | 首次公告日 |
| summary | str | 业绩预告摘要 |
| change_reason | str | 业绩变动原因 |

## 调用示例

```python
pro = ts.pro_api()

pro.forecast(ann_date='20190131', fields='ts_code,ann_date,end_date,type,p_change_min,p_change_max,net_profit_min')
```

```python
df = pro.forecast_vip(period='20181231',fields='ts_code,ann_date,end_date,type,p_change_min,p_change_max,net_profit_min')
```
# 业绩快报

**路径**: 股票数据/财务数据
**接口**: `express`
**积分**: 2000
**描述**: 获取上市公司业绩快报权限：用户需要至少2000积分才可以调取，具体请参阅积分获取办法提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用express_vip接口（参数一致），需积攒5000积分。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| ann_date | str | N | 公告日期 |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |
| period | str | N | 报告期(每个季度最后一天的日期,比如20171231表示年报，20170630半年报，20170930三季报) |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | TS股票代码 |
| ann_date | str | 公告日期 |
| end_date | str | 报告期 |
| revenue | float | 营业收入(元) |
| operate_profit | float | 营业利润(元) |
| total_profit | float | 利润总额(元) |
| n_income | float | 净利润(元) |
| total_assets | float | 总资产(元) |
| total_hldr_eqy_exc_min_int | float | 股东权益合计(不含少数股东权益)(元) |
| diluted_eps | float | 每股收益(摊薄)(元) |
| diluted_roe | float | 净资产收益率(摊薄)(%) |
| yoy_net_profit | float | 去年同期修正后净利润 |
| bps | float | 每股净资产 |
| yoy_sales | float | 同比增长率:营业收入 |
| yoy_op | float | 同比增长率:营业利润 |
| yoy_tp | float | 同比增长率:利润总额 |
| yoy_dedu_np | float | 同比增长率:归属母公司股东的净利润 |
| yoy_eps | float | 同比增长率:基本每股收益 |
| yoy_roe | float | 同比增减:加权平均净资产收益率 |
| growth_assets | float | 比年初增长率:总资产 |
| yoy_equity | float | 比年初增长率:归属母公司的股东权益 |
| growth_bps | float | 比年初增长率:归属于母公司股东的每股净资产 |
| or_last_year | float | 去年同期营业收入 |
| op_last_year | float | 去年同期营业利润 |
| tp_last_year | float | 去年同期利润总额 |
| np_last_year | float | 去年同期净利润 |
| eps_last_year | float | 去年同期每股收益 |
| open_net_assets | float | 期初净资产 |
| open_bps | float | 期初每股净资产 |
| perf_summary | str | 业绩简要说明 |
| is_audit | int | 是否审计： 1是 0否 |
| remark | str | 备注 |

## 调用示例

```python
pro = ts.pro_api()

pro.express(ts_code='600000.SH', start_date='20180101', end_date='20180701', fields='ts_code,ann_date,end_date,revenue,operate_profit,total_profit,n_income,total_assets')
```

```python
df = pro.express_vip(period='20181231',fields='ts_code,ann_date,end_date,revenue,operate_profit,total_profit,n_income,total_assets')
```
# 沪深港通资金流向

**路径**: 股票数据/资金流向数据
**接口**: `moneyflow_hsgt`
**积分**: 2000
**描述**: 获取沪股通、深股通、港股通每日资金流向数据，每次最多返回300条记录，总量不限制。每天18~20点之间完成当日更新积分要求：2000积分起，5000积分每分钟可提取500次

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期 (二选一) |
| start_date | str | N | 开始日期 (二选一) |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| trade_date | str | 交易日期 |
| ggt_ss | float | 港股通（上海） |
| ggt_sz | float | 港股通（深圳） |
| hgt | float | 沪股通（百万元） |
| sgt | float | 深股通（百万元） |
| north_money | float | 北向资金（百万元） |
| south_money | float | 南向资金（百万元） |

## 调用示例

```python
pro = ts.pro_api()

pro.moneyflow_hsgt(start_date='20180125', end_date='20180808')
```

```python
pro.query('moneyflow_hsgt', trade_date='20180725')
```
# 沪深股通十大成交股

**路径**: 股票数据/行情数据
**接口**: `hsgt_top10`
**描述**: 获取沪股通、深股通每日前十大成交详细数据，每天18~20点之间完成当日更新

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码（二选一） |
| trade_date | str | N | 交易日期（二选一） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| market_type | str | N | 市场类型（1：沪市 3：深市） |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| trade_date | str | 交易日期 |
| ts_code | str | 股票代码 |
| name | str | 股票名称 |
| close | float | 收盘价 |
| change | float | 涨跌额 |
| rank | int | 资金排名 |
| market_type | str | 市场类型（1：沪市 3：深市） |
| amount | float | 成交金额（元） |
| net_amount | float | 净成交金额（元） |
| buy | float | 买入金额（元） |
| sell | float | 卖出金额（元） |

## 调用示例

```python
pro = ts.pro_api()

pro.hsgt_top10(trade_date='20180725', market_type='1')
```

```python
pro.query('hsgt_top10', ts_code='600519.SH', start_date='20180701', end_date='20180725')
```
# 港股通十大成交股

**路径**: 股票数据/行情数据
**接口**: `ggt_top10`
**描述**: 获取港股通每日成交数据，其中包括沪市、深市详细数据，每天18~20点之间完成当日更新

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 股票代码（二选一） |
| trade_date | str | N | 交易日期（二选一） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| market_type | str | N | 市场类型 2：港股通（沪） 4：港股通（深） |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| trade_date | str | 交易日期 |
| ts_code | str | 股票代码 |
| name | str | 股票名称 |
| close | float | 收盘价 |
| p_change | float | 涨跌幅 |
| rank | str | 资金排名 |
| market_type | str | 市场类型 2：港股通（沪） 4：港股通（深） |
| amount | float | 累计成交金额（元） |
| net_amount | float | 净买入金额（元） |
| sh_amount | float | 沪市成交金额（元） |
| sh_net_amount | float | 沪市净买入金额（元） |
| sh_buy | float | 沪市买入金额（元） |
| sh_sell | float | 沪市卖出金额 |
| sz_amount | float | 深市成交金额（元） |
| sz_net_amount | float | 深市净买入金额（元） |
| sz_buy | float | 深市买入金额（元） |
| sz_sell | float | 深市卖出金额（元） |

## 调用示例

```python
pro = ts.pro_api()

pro.ggt_top10(trade_date='20180727')
```

```python
pro.query('ggt_top10', ts_code='00700', start_date='20180701', end_date='20180727')
```
# 融资融券交易汇总

**路径**: 股票数据/两融及转融通
**接口**: `margin`
**积分**: 2000
**描述**: 获取融资融券每日交易汇总数据限量：单次请求最大返回4000行数据，可根据日期循环权限：2000积分可获得本接口权限，积分越高权限越大，具体参考权限说明
**限量**: 单次请求最大返回4000行数据，可根据日期循环权限：2000积分可获得本接口权限，积分越高权限越大，具体参考权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期（格式：YYYYMMDD，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |
| exchange_id | str | N | 交易所代码（SSE上交所SZSE深交所BSE北交所） |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| trade_date | str | 交易日期 |
| exchange_id | str | 交易所代码（SSE上交所SZSE深交所BSE北交所） |
| rzye | float | 融资余额(元) |
| rzmre | float | 融资买入额(元) |
| rzche | float | 融资偿还额(元) |
| rqye | float | 融券余额(元) |
| rqmcl | float | 融券卖出量(股,份,手) |
| rzrqye | float | 融资融券余额(元) |
| rqyl | float | 融券余量(股,份,手) |

## 调用示例

```python
pro = ts.pro_api()

df = pro.margin(trade_date='20180802')
```

```python
df = pro.query('margin', trade_date='20180802', exchange_id='SSE')
```
# 融资融券交易明细

**路径**: 股票数据/两融及转融通
**接口**: `margin_detail`
**积分**: 2000
**描述**: 获取沪深两市每日融资融券明细限量：单次请求最大返回6000行数据，可根据日期循环权限：2000积分可获得本接口权限，积分越高权限越大，具体参考权限说明
**限量**: 单次请求最大返回6000行数据，可根据日期循环权限：2000积分可获得本接口权限，积分越高权限越大，具体参考权限说明

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| trade_date | str | N | 交易日期（格式：YYYYMMDD，下同） |
| ts_code | str | N | TS代码 |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| trade_date | str | 交易日期 |
| ts_code | str | TS股票代码 |
| name | str | 股票名称 （20190910后有数据） |
| rzye | float | 融资余额(元) |
| rqye | float | 融券余额(元) |
| rzmre | float | 融资买入额(元) |
| rqyl | float | 融券余量（股） |
| rzche | float | 融资偿还额(元) |
| rqchl | float | 融券偿还量(股) |
| rqmcl | float | 融券卖出量(股,份,手) |
| rzrqye | float | 融资融券余额(元) |

## 调用示例

```python
pro = ts.pro_api()

df = pro.margin_detail(trade_date='20180802')
```

```python
df = pro.query('margin_detail', trade_date='20180802')
```
# 前十大股东

**路径**: 股票数据/参考数据
**接口**: `top10_holders`
**积分**: 2000
**描述**: 获取上市公司前十大股东数据，包括持有数量和比例等信息积分：需2000积分以上才可以调取本接口，5000积分以上频次会更高

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | TS代码 |
| period | str | N | 报告期（YYYYMMDD格式，一般为每个季度最后一天） |
| ann_date | str | N | 公告日期 |
| start_date | str | N | 报告期开始日期 |
| end_date | str | N | 报告期结束日期 |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | TS股票代码 |
| ann_date | str | 公告日期 |
| end_date | str | 报告期 |
| holder_name | str | 股东名称 |
| hold_amount | float | 持有数量（股） |
| hold_ratio | float | 占总股本比例(%) |
| hold_float_ratio | float | 占流通股本比例(%) |
| hold_change | float | 持股变动 |
| holder_type | str | 股东类型 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.top10_holders(ts_code='600000.SH', start_date='20170101', end_date='20171231')
```

```python
df = pro.query('top10_holders', ts_code='600000.SH', start_date='20170101', end_date='20171231')
```
# 前十大流通股东

**路径**: 股票数据/参考数据
**接口**: `top10_floatholders`
**积分**: 2000
**描述**: 获取上市公司前十大流通股东数据积分：需2000积分以上才可以调取本接口，5000积分以上频次会更高

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | TS代码 |
| period | str | N | 报告期（YYYYMMDD格式，一般为每个季度最后一天） |
| ann_date | str | N | 公告日期 |
| start_date | str | N | 报告期开始日期 |
| end_date | str | N | 报告期结束日期 |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | TS股票代码 |
| ann_date | str | 公告日期 |
| end_date | str | 报告期 |
| holder_name | str | 股东名称 |
| hold_amount | float | 持有数量（股） |
| hold_ratio | float | 占总股本比例(%) |
| hold_float_ratio | float | 占流通股本比例(%) |
| hold_change | float | 持股变动 |
| holder_type | str | 股东类型 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.top10_floatholders(ts_code='600000.SH', start_date='20170101', end_date='20171231')
```

```python
df = pro.query('top10_floatholders', ts_code='600000.SH', start_date='20170101', end_date='20171231')
```
# 财务指标数据

**路径**: 股票数据/财务数据
**接口**: `fina_indicator`
**积分**: 2000
**描述**: 获取上市公司财务指标数据，为避免服务器压力，现阶段每次请求最多返回100条记录，可通过设置日期多次请求获取更多数据。权限：用户需要至少2000积分才可以调取，具体请参阅积分获取办法提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用fina_indicator_vip接口（参数一致），需积攒5000积分。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | TS股票代码,e.g. 600001.SH/000001.SZ |
| ann_date | str | N | 公告日期 |
| start_date | str | N | 报告期开始日期 |
| end_date | str | N | 报告期结束日期 |
| period | str | N | 报告期(每个季度最后一天的日期,比如20171231表示年报) |

## 输出参数

| 名称 | 类型 | 默认显示 | 描述 |
|------|------|----------|------|
| ts_code | str | Y | TS代码 |
| ann_date | str | Y | 公告日期 |
| end_date | str | Y | 报告期 |
| eps | float | Y | 基本每股收益 |
| dt_eps | float | Y | 稀释每股收益 |
| total_revenue_ps | float | Y | 每股营业总收入 |
| revenue_ps | float | Y | 每股营业收入 |
| capital_rese_ps | float | Y | 每股资本公积 |
| surplus_rese_ps | float | Y | 每股盈余公积 |
| undist_profit_ps | float | Y | 每股未分配利润 |
| extra_item | float | Y | 非经常性损益 |
| profit_dedt | float | Y | 扣除非经常性损益后的净利润（扣非净利润） |
| gross_margin | float | Y | 毛利 |
| current_ratio | float | Y | 流动比率 |
| quick_ratio | float | Y | 速动比率 |
| cash_ratio | float | Y | 保守速动比率 |
| invturn_days | float | N | 存货周转天数 |
| arturn_days | float | N | 应收账款周转天数 |
| inv_turn | float | N | 存货周转率 |
| ar_turn | float | Y | 应收账款周转率 |
| ca_turn | float | Y | 流动资产周转率 |
| fa_turn | float | Y | 固定资产周转率 |
| assets_turn | float | Y | 总资产周转率 |
| op_income | float | Y | 经营活动净收益 |
| valuechange_income | float | N | 价值变动净收益 |
| interst_income | float | N | 利息费用 |
| daa | float | N | 折旧与摊销 |
| ebit | float | Y | 息税前利润 |
| ebitda | float | Y | 息税折旧摊销前利润 |
| fcff | float | Y | 企业自由现金流量 |
| fcfe | float | Y | 股权自由现金流量 |
| current_exint | float | Y | 无息流动负债 |
| noncurrent_exint | float | Y | 无息非流动负债 |
| interestdebt | float | Y | 带息债务 |
| netdebt | float | Y | 净债务 |
| tangible_asset | float | Y | 有形资产 |
| working_capital | float | Y | 营运资金 |
| networking_capital | float | Y | 营运流动资本 |
| invest_capital | float | Y | 全部投入资本 |
| retained_earnings | float | Y | 留存收益 |
| diluted2_eps | float | Y | 期末摊薄每股收益 |
| bps | float | Y | 每股净资产 |
| ocfps | float | Y | 每股经营活动产生的现金流量净额 |
| retainedps | float | Y | 每股留存收益 |
| cfps | float | Y | 每股现金流量净额 |
| ebit_ps | float | Y | 每股息税前利润 |
| fcff_ps | float | Y | 每股企业自由现金流量 |
| fcfe_ps | float | Y | 每股股东自由现金流量 |
| netprofit_margin | float | Y | 销售净利率 |
| grossprofit_margin | float | Y | 销售毛利率 |
| cogs_of_sales | float | Y | 销售成本率 |
| expense_of_sales | float | Y | 销售期间费用率 |
| profit_to_gr | float | Y | 净利润/营业总收入 |
| saleexp_to_gr | float | Y | 销售费用/营业总收入 |
| adminexp_of_gr | float | Y | 管理费用/营业总收入 |
| finaexp_of_gr | float | Y | 财务费用/营业总收入 |
| impai_ttm | float | Y | 资产减值损失/营业总收入 |
| gc_of_gr | float | Y | 营业总成本/营业总收入 |
| op_of_gr | float | Y | 营业利润/营业总收入 |
| ebit_of_gr | float | Y | 息税前利润/营业总收入 |
| roe | float | Y | 净资产收益率 |
| roe_waa | float | Y | 加权平均净资产收益率 |
| roe_dt | float | Y | 净资产收益率(扣除非经常损益) |
| roa | float | Y | 总资产报酬率 |
| npta | float | Y | 总资产净利润 |
| roic | float | Y | 投入资本回报率 |
| roe_yearly | float | Y | 年化净资产收益率 |
| roa2_yearly | float | Y | 年化总资产报酬率 |
| roe_avg | float | N | 平均净资产收益率(增发条件) |
| opincome_of_ebt | float | N | 经营活动净收益/利润总额 |
| investincome_of_ebt | float | N | 价值变动净收益/利润总额 |
| n_op_profit_of_ebt | float | N | 营业外收支净额/利润总额 |
| tax_to_ebt | float | N | 所得税/利润总额 |
| dtprofit_to_profit | float | N | 扣除非经常损益后的净利润/净利润 |
| salescash_to_or | float | N | 销售商品提供劳务收到的现金/营业收入 |
| ocf_to_or | float | N | 经营活动产生的现金流量净额/营业收入 |
| ocf_to_opincome | float | N | 经营活动产生的现金流量净额/经营活动净收益 |
| capitalized_to_da | float | N | 资本支出/折旧和摊销 |
| debt_to_assets | float | Y | 资产负债率 |
| assets_to_eqt | float | Y | 权益乘数 |
| dp_assets_to_eqt | float | Y | 权益乘数(杜邦分析) |
| ca_to_assets | float | Y | 流动资产/总资产 |
| nca_to_assets | float | Y | 非流动资产/总资产 |
| tbassets_to_totalassets | float | Y | 有形资产/总资产 |
| int_to_talcap | float | Y | 带息债务/全部投入资本 |
| eqt_to_talcapital | float | Y | 归属于母公司的股东权益/全部投入资本 |
| currentdebt_to_debt | float | Y | 流动负债/负债合计 |
| longdeb_to_debt | float | Y | 非流动负债/负债合计 |
| ocf_to_shortdebt | float | Y | 经营活动产生的现金流量净额/流动负债 |
| debt_to_eqt | float | Y | 产权比率 |
| eqt_to_debt | float | Y | 归属于母公司的股东权益/负债合计 |
| eqt_to_interestdebt | float | Y | 归属于母公司的股东权益/带息债务 |
| tangibleasset_to_debt | float | Y | 有形资产/负债合计 |
| tangasset_to_intdebt | float | Y | 有形资产/带息债务 |
| tangibleasset_to_netdebt | float | Y | 有形资产/净债务 |
| ocf_to_debt | float | Y | 经营活动产生的现金流量净额/负债合计 |
| ocf_to_interestdebt | float | N | 经营活动产生的现金流量净额/带息债务 |
| ocf_to_netdebt | float | N | 经营活动产生的现金流量净额/净债务 |
| ebit_to_interest | float | N | 已获利息倍数(EBIT/利息费用) |
| longdebt_to_workingcapital | float | N | 长期债务与营运资金比率 |
| ebitda_to_debt | float | N | 息税折旧摊销前利润/负债合计 |
| turn_days | float | Y | 营业周期 |
| roa_yearly | float | Y | 年化总资产净利率 |
| roa_dp | float | Y | 总资产净利率(杜邦分析) |
| fixed_assets | float | Y | 固定资产合计 |
| profit_prefin_exp | float | N | 扣除财务费用前营业利润 |
| non_op_profit | float | N | 非营业利润 |
| op_to_ebt | float | N | 营业利润／利润总额 |
| nop_to_ebt | float | N | 非营业利润／利润总额 |
| ocf_to_profit | float | N | 经营活动产生的现金流量净额／营业利润 |
| cash_to_liqdebt | float | N | 货币资金／流动负债 |
| cash_to_liqdebt_withinterest | float | N | 货币资金／带息流动负债 |
| op_to_liqdebt | float | N | 营业利润／流动负债 |
| op_to_debt | float | N | 营业利润／负债合计 |
| roic_yearly | float | N | 年化投入资本回报率 |
| total_fa_trun | float | N | 固定资产合计周转率 |
| profit_to_op | float | Y | 利润总额／营业收入 |
| q_opincome | float | N | 经营活动单季度净收益 |
| q_investincome | float | N | 价值变动单季度净收益 |
| q_dtprofit | float | N | 扣除非经常损益后的单季度净利润 |
| q_eps | float | N | 每股收益(单季度) |
| q_netprofit_margin | float | N | 销售净利率(单季度) |
| q_gsprofit_margin | float | N | 销售毛利率(单季度) |
| q_exp_to_sales | float | N | 销售期间费用率(单季度) |
| q_profit_to_gr | float | N | 净利润／营业总收入(单季度) |
| q_saleexp_to_gr | float | Y | 销售费用／营业总收入 (单季度) |
| q_adminexp_to_gr | float | N | 管理费用／营业总收入 (单季度) |
| q_finaexp_to_gr | float | N | 财务费用／营业总收入 (单季度) |
| q_impair_to_gr_ttm | float | N | 资产减值损失／营业总收入(单季度) |
| q_gc_to_gr | float | Y | 营业总成本／营业总收入 (单季度) |
| q_op_to_gr | float | N | 营业利润／营业总收入(单季度) |
| q_roe | float | Y | 净资产收益率(单季度) |
| q_dt_roe | float | Y | 净资产单季度收益率(扣除非经常损益) |
| q_npta | float | Y | 总资产净利润(单季度) |
| q_opincome_to_ebt | float | N | 经营活动净收益／利润总额(单季度) |
| q_investincome_to_ebt | float | N | 价值变动净收益／利润总额(单季度) |
| q_dtprofit_to_profit | float | N | 扣除非经常损益后的净利润／净利润(单季度) |
| q_salescash_to_or | float | N | 销售商品提供劳务收到的现金／营业收入(单季度) |
| q_ocf_to_sales | float | Y | 经营活动产生的现金流量净额／营业收入(单季度) |
| q_ocf_to_or | float | N | 经营活动产生的现金流量净额／经营活动净收益(单季度) |
| basic_eps_yoy | float | Y | 基本每股收益同比增长率(%) |
| dt_eps_yoy | float | Y | 稀释每股收益同比增长率(%) |
| cfps_yoy | float | Y | 每股经营活动产生的现金流量净额同比增长率(%) |
| op_yoy | float | Y | 营业利润同比增长率(%) |
| ebt_yoy | float | Y | 利润总额同比增长率(%) |
| netprofit_yoy | float | Y | 归属母公司股东的净利润同比增长率(%) |
| dt_netprofit_yoy | float | Y | 归属母公司股东的净利润-扣除非经常损益同比增长率(%) |
| ocf_yoy | float | Y | 经营活动产生的现金流量净额同比增长率(%) |
| roe_yoy | float | Y | 净资产收益率(摊薄)同比增长率(%) |
| bps_yoy | float | Y | 每股净资产相对年初增长率(%) |
| assets_yoy | float | Y | 资产总计相对年初增长率(%) |
| eqt_yoy | float | Y | 归属母公司的股东权益相对年初增长率(%) |
| tr_yoy | float | Y | 营业总收入同比增长率(%) |
| or_yoy | float | Y | 营业收入同比增长率(%) |
| q_gr_yoy | float | N | 营业总收入同比增长率(%)(单季度) |
| q_gr_qoq | float | N | 营业总收入环比增长率(%)(单季度) |
| q_sales_yoy | float | Y | 营业收入同比增长率(%)(单季度) |
| q_sales_qoq | float | N | 营业收入环比增长率(%)(单季度) |
| q_op_yoy | float | N | 营业利润同比增长率(%)(单季度) |
| q_op_qoq | float | Y | 营业利润环比增长率(%)(单季度) |
| q_profit_yoy | float | N | 净利润同比增长率(%)(单季度) |
| q_profit_qoq | float | N | 净利润环比增长率(%)(单季度) |
| q_netprofit_yoy | float | N | 归属母公司股东的净利润同比增长率(%)(单季度) |
| q_netprofit_qoq | float | N | 归属母公司股东的净利润环比增长率(%)(单季度) |
| equity_yoy | float | Y | 净资产同比增长率 |
| rd_exp | float | N | 研发费用 |
| update_flag | str | N | 更新标识 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.fina_indicator(ts_code='600000.SH')
```

```python
df = pro.query('fina_indicator', ts_code='600000.SH', start_date='20170101', end_date='20180801')
```
# 财务审计意见

**路径**: 股票数据/财务数据
**接口**: `fina_audit`
**积分**: 500
**描述**: 获取上市公司定期财务审计意见数据权限：用户需要至少500积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| ann_date | str | N | 公告日期 |
| start_date | str | N | 公告开始日期 |
| end_date | str | N | 公告结束日期 |
| period | str | N | 报告期(每个季度最后一天的日期,比如20171231表示年报) |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | TS股票代码 |
| ann_date | str | 公告日期 |
| end_date | str | 报告期 |
| audit_result | str | 审计结果 |
| audit_fees | float | 审计总费用（元） |
| audit_agency | str | 会计事务所 |
| audit_sign | str | 签字会计师 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.fina_audit(ts_code='600000.SH', start_date='20100101', end_date='20180808')
```
# 主营业务构成

**路径**: 股票数据/财务数据
**接口**: `fina_mainbz`
**积分**: 2000
**描述**: 获得上市公司主营业务构成，分地区和产品两种方式权限：用户需要至少2000积分才可以调取，具体请参阅积分获取办法  ，单次最大提取100行，总量不限制，可循环获取。提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用fina_mainbz_vip接口（参数一致），需积攒5000积分。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 股票代码 |
| period | str | N | 报告期(每个季度最后一天的日期,比如20171231表示年报) |
| type | str | N | 类型：P按产品 D按地区 I按行业（请输入大写字母P或者D） |
| start_date | str | N | 报告期开始日期 |
| end_date | str | N | 报告期结束日期 |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | TS代码 |
| end_date | str | 报告期 |
| bz_item | str | 主营业务来源 |
| bz_sales | float | 主营业务收入(元) |
| bz_profit | float | 主营业务利润(元) |
| bz_cost | float | 主营业务成本(元) |
| curr_type | str | 货币代码 |
| update_flag | str | 是否更新 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.fina_mainbz(ts_code='000627.SZ', type='P')
```

```python
df = pro.fina_mainbz_vip(period='20181231', type='P' ,fields='ts_code,end_date,bz_item,bz_sales')
```
# 行业经济数据

# TMT行业数据

**路径**: 行业经济
# 台湾电子产业月营收明细

**路径**: 行业经济/TMT行业
**接口**: `tmt_twincomedetail`
**描述**: 获取台湾TMT行业上市公司各类产品月度营收情况。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 报告期 |
| item | str | N | 产品代码 |
| symbol | str | N | 公司代码 |
| start_date | str | N | 报告期开始日期 |
| end_date | str | N | 报告期结束日期 |
| source | str | N | None |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| date | str | 报告期 |
| item | str | 产品代码 |
| symbol | str | 公司代码 |
| op_income | str | 月度营收 |
| consop_income | str | 合并月度营收（默认不展示） |

## 调用示例

```python
pro = ts.pro_api()

#获取台湾松上电子PCB的月度营收数据
df = pro.tmt_twincomedetail(item='8', symbol='6156')
```
# 台湾电子产业月营收

**路径**: 行业经济/TMT行业
**接口**: `tmt_twincome`
**描述**: 获取台湾TMT电子产业领域各类产品月度营收数据。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| date | str | N | 报告期 |
| item | str | Y | 产品代码 |
| start_date | str | N | 报告期开始日期 |
| end_date | str | N | 报告期结束日期 |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| date | str | 报告期 |
| item | str | 产品代码 |
| op_income | str | 月度收入 |

## 调用示例

```python
pro = ts.pro_api()

#获取PCB月度营收
df = pro.tmt_twincome(item='8')

#获取PCB月度营收（20120101-20181010）
df = pro.tmt_twincome(item='8', start_date='20120101', end_date='20181010')
```
# 指数数据

# 指数基本信息

**路径**: 指数专题
**接口**: `index_basic`
**描述**: 获取指数基础信息。

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | N | 指数代码 |
| name | str | N | 指数简称 |
| market | str | N | 交易所或服务商(默认SSE) |
| publisher | str | N | 发布商 |
| category | str | N | 指数类别 |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | TS代码 |
| name | str | 简称 |
| fullname | str | 指数全称 |
| market | str | 市场 |
| publisher | str | 发布方 |
| index_type | str | 指数风格 |
| category | str | 指数类别 |
| base_date | str | 基期 |
| base_point | float | 基点 |
| list_date | str | 发布日期 |
| weight_rule | str | 加权方式 |
| desc | str | 描述 |
| exp_date | str | 终止日期 |

## 调用示例

```python
pro = ts.pro_api()

df = pro.index_basic(market='SW')
```
# 指数日线行情

**路径**: 指数专题
**接口**: `index_daily`
**积分**: 2000
**描述**: 获取指数每日行情，还可以通过bar接口获取。由于服务器压力，目前规则是单次调取最多取8000行记录，可以设置start和end日期补全。指数行情也可以通过通用行情接口获取数据．权限：用户累积2000积分可调取，5000积分以上频次相对较高。本接口不包括申万行情数据，申万等行业指数行情需5000积分以上，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| ts_code | str | Y | 指数代码，来源指数基础信息接口 |
| trade_date | str | N | 交易日期 （日期格式：YYYYMMDD，下同） |
| start_date | str | N | 开始日期 |
| end_date | str | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| ts_code | str | TS指数代码 |
| trade_date | str | 交易日 |
| close | float | 收盘点位 |
| open | float | 开盘点位 |
| high | float | 最高点位 |
| low | float | 最低点位 |
| pre_close | float | 昨日收盘点 |
| change | float | 涨跌点 |
| pct_chg | float | 涨跌幅（%） |
| vol | float | 成交量（手） |
| amount | float | 成交额（千元） |

## 调用示例

```python
pro = ts.pro_api()

df = pro.index_daily(ts_code='399300.SZ')

#或者按日期取

df = pro.index_daily(ts_code='399300.SZ', start_date='20180101', end_date='20181010')
```
# 指数成分和权重

**路径**: 指数专题
**接口**: `index_weight`
**积分**: 2000
**描述**: 获取各类指数成分和权重，月度数据 ，建议输入参数里开始日期和结束日分别输入当月第一天和最后一天的日期。来源：指数公司网站公开数据积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
|------|------|------|------|
| index_code | str | Y | 指数代码，来源指数基础信息接口 |
| trade_date | str | N | 交易日期（格式YYYYMMDD，下同） |
| start_date | str | N | 开始日期 |
| end_date | None | N | 结束日期 |

## 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| index_code | str | 指数代码 |
| con_code | str | 成分代码 |
| trade_date | str | 交易日期 |
| weight | float | 权重 |

## 调用示例

```python
pro = ts.pro_api()

#提取沪深300指数2018年9月成分和权重
df = pro.index_weight(index_code='399300.SZ', start_date='20180901', end_date='20180930')
```
