# 外部CSV因子与官方API字段对照

| 外部列 | 匹配类型 | API | 官方字段 | 备注 |
|--------|----------|-----|----------|------|
| Unnamed: 0 | not_found |  |  |  |
| 代码 | not_found |  |  |  |
| 名称 | not_found |  |  |  |
| 日期 | not_found |  |  |  |
| 总分 | not_found |  |  |  |
| 开盘 | not_found |  |  |  |
| 最高 | not_found |  |  |  |
| 最低 | not_found |  |  |  |
| close | exact | daily | close |  |
| jump | family | daily |  | 跳空为衍生逻辑，不是官方字段 |
| 涨跌幅 | family | daily | pct_chg | 中文同义：涨跌幅→pct_chg |
| 换手率% | family | daily_basic | turnover_rate | 中文同义：换手率→turnover_rate |
| 放量天数 | not_found |  |  |  |
| 平均量比_50天 | family | daily_basic | volume_ratio | 中文同义：量比→volume_ratio |
| 成交量 | family | daily | vol | 中文同义：成交量→vol；consec为衍生 |
| 放量天数_volume | not_found |  |  |  |
| 平均量比_50天_volume | family | daily_basic | volume_ratio | 中文同义：量比→volume_ratio |
| 波动率 | not_found |  |  |  |
| volatile_consec | not_found |  |  |  |
| BETA | not_found |  |  |  |
| BETA_consec | not_found |  |  |  |
| 相关性 | not_found |  |  |  |
| 总市值(亿) | family | daily_basic | total_mv | 中文同义：总市值→total_mv |
| 长期 | not_found |  |  |  |
| 短期 | not_found |  |  |  |
| 行业 | not_found |  |  |  |
| 超买 | not_found |  |  |  |
| 超卖 | not_found |  |  |  |
| macd_signal | family | stk_factor | macd | MACD主值；signal/consec为衍生 |
| slowkdj_signal | family | stk_factor | kdj_k, kdj_d, kdj_j | KDJ信号/连日由k/d/j衍生 |
| lon_lonma | not_found |  |  |  |
| lon_consec | not_found |  |  |  |
| lon_0 | not_found |  |  |  |
| loncons_consec | not_found |  |  |  |
| lonma_0 | not_found |  |  |  |
| lonmacons_consec | not_found |  |  |  |
| dma | family | stk_factor_pro |  | DMA不在官方字段列表（可能为自定义） |
| dma_consec | family | stk_factor_pro |  | DMA不在官方字段列表（可能为自定义） |
| dif_dem | family | stk_factor | macd_dif | MACD分量：dif→macd_dif |
| macd_consec | family | stk_factor | macd | MACD主值；signal/consec为衍生 |
| dif_0 | not_found |  |  |  |
| macdcons_consec | family | stk_factor | macd | MACD主值；signal/consec为衍生 |
| dem_0 | not_found |  |  |  |
| demcons_consec | not_found |  |  |  |
| pdi_adx | family | stk_factor_pro | dmi_adx_bfq, dmi_adx_qfq, dmi_adx_hfq | ADX族在stk_factor_pro |
| dmiadx_consec | family | stk_factor_pro | dmi_adx_bfq, dmi_adx_qfq, dmi_adx_hfq | ADX族在stk_factor_pro |
| pdi_ndi | family | stk_factor_pro | dmi_pdi_bfq, dmi_mdi_bfq | DI族在stk_factor_pro（PDI/MDI） |
| dmi_consec | not_found |  |  |  |
| obv | family | stk_factor_pro | obv_bfq, obv_qfq, obv_hfq | OBV族在stk_factor_pro |
| obv_consec | family | stk_factor_pro | obv_bfq, obv_qfq, obv_hfq | OBV族在stk_factor_pro |
| k_kdj | family | stk_factor | kdj_k | KDJ：k_kdj/slowk→kdj_k |
| slowkdj_consec | family | stk_factor | kdj_k, kdj_d, kdj_j | KDJ信号/连日由k/d/j衍生 |
| rsi | family | stk_factor | rsi_6, rsi_12, rsi_24 | RSI族：rsi为聚合；*_consec为衍生 |
| rsi_consec | family | stk_factor | rsi_6, rsi_12, rsi_24 | RSI族：rsi为聚合；*_consec为衍生 |
| cci_-90 | family | stk_factor | cci | CCI阈值衍生；原始字段 cci |
| cci_lower_consec | family | stk_factor | cci | CCI阈值衍生；原始字段 cci |
| cci_90 | family | stk_factor | cci | CCI阈值衍生；原始字段 cci |
| cci_upper_consec | family | stk_factor | cci | CCI阈值衍生；原始字段 cci |
| bands_lower | family | stk_factor | boll_lower | BOLL→bands_lower 对应 boll_lower |
| bands_lower_consec | family | stk_factor | boll_lower, boll_mid, boll_upper | BOLL连日为衍生 |
| bands_middle | family | stk_factor | boll_mid | BOLL→bands_middle 对应 boll_mid |
| bands_middle_consec | family | stk_factor | boll_lower, boll_mid, boll_upper | BOLL连日为衍生 |
| bands_upper | family | stk_factor | boll_upper | BOLL→bands_upper 对应 boll_upper |
| bands_upper_consec | family | stk_factor | boll_lower, boll_mid, boll_upper | BOLL连日为衍生 |
| lon_lonma_diff | not_found |  |  |  |
| lon | not_found |  |  |  |
| lonma | not_found |  |  |  |
| histgram | family | stk_factor | macd | MACD主值；signal/consec为衍生 |
| dif | family | stk_factor | macd_dif | MACD分量：dif→macd_dif |
| dem | family | stk_factor | macd_dea | MACD分量：dem(DEA)→macd_dea |
| ADX | family | stk_factor_pro | dmi_adx_bfq, dmi_adx_qfq, dmi_adx_hfq | ADX族在stk_factor_pro |
| PLUS_DI | family | stk_factor_pro | dmi_pdi_bfq, dmi_mdi_bfq | DI族在stk_factor_pro（PDI/MDI） |
| OBV | family | stk_factor_pro | obv_bfq, obv_qfq, obv_hfq | OBV族在stk_factor_pro |
| slowk | family | stk_factor | kdj_k | KDJ：k_kdj/slowk→kdj_k |
| RSI | family | stk_factor | rsi_6, rsi_12, rsi_24 | RSI族：rsi为聚合；*_consec为衍生 |
| CCI_-90 | family | stk_factor | cci | CCI阈值衍生；原始字段 cci |
| CCI_90 | family | stk_factor | cci | CCI阈值衍生；原始字段 cci |
| lower | family | stk_factor | boll_lower | BOLL→bands_lower 对应 boll_lower |
| middle | family | stk_factor | boll_mid | BOLL→bands_middle 对应 boll_mid |
| upper | family | stk_factor | boll_upper | BOLL→bands_upper 对应 boll_upper |
| lst_close | family | daily | close | 收盘价 |
| code2 | family | daily | ts_code | 代码同义：code→ts_code |
| name2 | family | daily |  | 名称非API字段 |
| zhangdiefu2 | family | daily | pct_chg | 中文同义：涨跌幅→pct_chg |
| volume_consec2 | family | daily | vol | 中文同义：成交量→vol；consec为衍生 |
| volume_50_consec2 | not_found |  |  |  |