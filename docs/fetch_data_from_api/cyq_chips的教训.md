【教训：cyq_chips 不适合作为“全市场日频截面”接口】

现象：
- 按 “trade_date + 全市场截面” 方式批量调用 cyq_chips
- Tushare 返回错误：必填参数 ts_code
- 重试多次后依然失败，37 个交易日全部 failed

原因：
- cyq_chips 的设计是“单只股票 + 一段时间”的筹码接口，参数要求必须带 ts_code
- 它不是像 daily/daily_basic 那种“给一个 trade_date 就能返回全市场截面”的 API
- 因此无法用当前的 “fetch_api_cross_section(api_name, trade_date)” 这种全市场截面模式来调用

决策：
- 从 `SUPPORTED_STOCK_DAILY_APIS` 中临时移除 `cyq_chips`
- 日频截面批量任务（全市场 + 按交易日循环）只覆盖真正支持“按 trade_date 拉全市场截面”的接口：
  - daily, daily_basic, adj_factor, stk_limit, moneyflow,
    stk_factor, stk_factor_pro, stk_nineturn, stk_auction
- 如果以后要接入 cyq_chips，需要单独设计：
  - 以 ts_code 为主循环（或 ts_code + 日期区间），而不是 trade_date 截面模式

结论：
- cyq_chips 属于“按股票维度调取、时间维度为次”的筹码接口，不属于当前这层“按交易日维度拉全市场截面”的 stock-daily 面板范畴。
