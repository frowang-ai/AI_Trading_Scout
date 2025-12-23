import pandas as pd

from production.utils import llm_analyst


def _make_current_top() -> pd.DataFrame:
    data = {
        "ts_code": ["000001.SZ", "000002.SZ"],
        "name": ["平安银行", "万 科A"],
        "industry": ["银行", "房地产"],
        "concepts": ["大金融;银行", "地产;深圳国资"],
        "open": [10.0, 19.5],
        "high": [10.8, 21.0],
        "low": [9.9, 19.0],
        "close": [10.5, 20.3],
        "pre_close": [10.2, 20.0],
        "pct_chg": [2.3, -1.2],
        "volume": [1_000_000.0, 2_000_000.0],
        "amount": [1.05e7, 4.06e7],
        "vol_ratio": [1.5, 2.0],
        "pe": [10.0, 15.0],
        "pb": [1.2, 2.3],
        "ps": [0.8, 1.5],
        "dv_ratio": [2.0, 1.5],
        "circ_mv": [5e10, 8e10],
        "macd_signal": [1.0, -1.0],
        "days_to_high": [0, 15],
        "predicted_score": [98.5, 95.2],
        "rank": [1, 2],
    }
    return pd.DataFrame(data)


def _make_history_day1() -> pd.DataFrame:
    # 昨天：只有 000002.SZ 在榜
    data = {
        "ts_code": ["000002.SZ"],
        "trade_date": ["20251217"],
        "predicted_score": [94.0],
        "rank": [1],
    }
    return pd.DataFrame(data)


def _make_history_day2() -> pd.DataFrame:
    # 前天：000002.SZ 仍在榜，模拟连续 3 天
    data = {
        "ts_code": ["000002.SZ"],
        "trade_date": ["20251216"],
        "predicted_score": [93.0],
        "rank": [2],
    }
    return pd.DataFrame(data)


def test_build_llm_top_table_with_days_on_top() -> None:
    """验证 LLM 输入表包含预期字段、榜单状态以及 days_on_top。"""
    current_top = _make_current_top()
    history = [_make_history_day1(), _make_history_day2()]

    table = llm_analyst.build_llm_top_table(current_top, history_tops=history)

    expected_columns = [
        "ts_code",
        "name",
        "industry",
        "concepts",
        "open",
        "high",
        "low",
        "close",
        "pre_close",
        "pct_chg",
        "volume",
        "amount",
        "vol_ratio",
        "pe",
        "pb",
        "ps",
        "dv",
        "circ_mv",
        "macd_status",
        "days_to_high",
        "score",
        "status",
        "days_on_top",
    ]
    for col in expected_columns:
        assert col in table.columns

    # 000001.SZ 昨天不在榜，应为新进且 days_on_top 为 1
    row_new = table[table["ts_code"] == "000001.SZ"].iloc[0]
    assert row_new["status"] == "新进"
    assert row_new["days_on_top"] == 1

    # 000002.SZ 连续 3 天在榜（今天 + 昨天 + 前天）
    row_stay = table[table["ts_code"] == "000002.SZ"].iloc[0]
    assert row_stay["status"] == "维持"
    assert row_stay["days_on_top"] == 3

    # macd_signal > 0 -> 金叉, < 0 -> 死叉
    assert row_new["macd_status"] == "金叉"
    assert row_stay["macd_status"] == "死叉"


def test_build_prompts_and_history_summary() -> None:
    """验证生成的 Prompt 至少包含关键小节标题和历史摘要信息。"""
    current_top = _make_current_top()
    history = [_make_history_day1(), _make_history_day2()]
    table = llm_analyst.build_llm_top_table(current_top, history_tops=history)

    summary = llm_analyst.summarize_recent_top_history(table)
    assert "连续2天在榜" in summary
    assert "连续3天及以上在榜" in summary

    system_prompt, user_prompt = llm_analyst.build_daily_prompts(
        current_date="2025-12-18",
        top_table=table,
        history_summary=summary,
    )

    assert "Role" in system_prompt
    assert "市场风格与板块协同" in system_prompt
    assert "今日日期" in user_prompt
    # 表头中应包含 ts_code / name / open / high / low / industry 等
    assert "| ts_code | name | open | high | low | industry" in user_prompt
