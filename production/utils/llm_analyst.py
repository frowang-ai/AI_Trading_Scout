"""
封装 Stage 3: AI 投顾分析

当前专注于两件事：
1. 把 Python 侧打分结果整理为适合 LLM 理解的“富上下文表格”（含行业 / 概念 / 状态等）
2. 根据统一的 Prompt 模板，构建 System Prompt 与 User Prompt 字符串

真正调用 LLMClient_v2 的逻辑可以在此基础上逐步补充。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import asyncio
from importlib import import_module
import pandas as pd


@dataclass
class LLMReadyRow:
    ts_code: str
    name: str
    industry: str
    concepts: str
    close: float
    pct_chg: float
    vol_ratio: float
    macd_status: str
    days_to_high: int
    score: float
    status: str  # 新进 / 维持
    days_on_top: int


def _select_first_existing_column(
    df: pd.DataFrame, candidates: Sequence[str], default: str = ""
) -> str:
    for col in candidates:
        if col in df.columns:
            return col
    return default


def _infer_macd_status(row: pd.Series) -> str:
    """基于 MACD 相关数值列推断技术形态的简单文字描述."""
    # 优先使用预先计算好的 macd_signal（>0 金叉，<0 死叉）
    if "macd_signal" in row.index:
        val = row["macd_signal"]
        try:
            v = float(val)
        except Exception:
            return "未知"
        if v > 0:
            return "金叉"
        if v < 0:
            return "死叉"
        return "震荡"

    # 退化：根据 macd_dif / macd_dea 粗略判断
    dif = row.get("macd_dif") or row.get("macd_dif_bfq")
    dea = row.get("macd_dea") or row.get("macd_dea_bfq")
    try:
        dif_f = float(dif)
        dea_f = float(dea)
    except Exception:
        return "未知"

    if dif_f >= dea_f and dif_f > 0:
        return "金叉或多头"
    if dif_f <= dea_f and dif_f < 0:
        return "死叉或空头"
    return "震荡"


def build_llm_top_table(
    current_top: pd.DataFrame,
    history_tops: Optional[Sequence[pd.DataFrame]] = None,
) -> pd.DataFrame:
    """
    将当前 TopN DataFrame 转换为适合 LLM 的精简表格，并打上“新进/维持”等标签。

    要求 current_top 至少包含：ts_code, predicted_score, rank；
    若存在 name/industry/concepts/close/pct_chg/vol_ratio/days_to_high 等列会优先使用。
    """
    if current_top.empty:
        return current_top

    df = current_top.copy()

    history_tops = [h for h in (history_tops or []) if h is not None and not h.empty]

    # 榜单状态：新进 / 维持（只看昨天）
    prev_set = set()
    if history_tops:
        first = history_tops[0]
        if "ts_code" in first.columns:
            prev_set = set(first["ts_code"].astype(str).tolist())

    def _status(ts_code: str) -> str:
        return "维持" if ts_code in prev_set else "新进"

    # 常用字段列名推断
    name_col = _select_first_existing_column(df, ["name", "sec_name", "股票名称"])
    industry_col = _select_first_existing_column(
        df,
        [
            "industry",
            "sw_industry_name",
            "sw_l1_name",
            "sw_l1",
            "ci_industry_name",
        ],
    )
    concepts_col = _select_first_existing_column(
        df,
        ["concepts", "concept_name_list", "concepts_joined"],
    )

    # 价格与成交
    open_col = _select_first_existing_column(df, ["open", "open_price"])
    high_col = _select_first_existing_column(df, ["high", "high_price"])
    low_col = _select_first_existing_column(df, ["low", "low_price"])
    close_col = _select_first_existing_column(df, ["close", "close_price"])
    pre_close_col = _select_first_existing_column(
        df, ["pre_close", "prev_close", "pre_close_price"]
    )
    pct_chg_col = _select_first_existing_column(
        df, ["pct_chg", "pct_change", "change_pct"]
    )
    volume_col = _select_first_existing_column(df, ["vol", "volume"])
    amount_col = _select_first_existing_column(df, ["amount"])
    vol_ratio_col = _select_first_existing_column(
        df, ["vol_ratio", "volume_ratio", "量比"]
    )

    # 估值
    pe_col = _select_first_existing_column(df, ["pe", "pe_ttm"])
    pb_col = _select_first_existing_column(df, ["pb"])
    ps_col = _select_first_existing_column(df, ["ps", "ps_ttm"])
    dv_col = _select_first_existing_column(df, ["dv_ratio", "dv_ttm"])
    circ_mv_col = _select_first_existing_column(df, ["circ_mv"])

    days_to_high_col = _select_first_existing_column(
        df,
        ["days_to_high", "n_days_since_high", "recent_high_gap_days", "topdays"],
    )

    rows: List[LLMReadyRow] = []

    # days_on_top：考虑最近 3 个交易日（含今天），超出视为 3+
    history_limit = 3
    effective_history = history_tops[
        : history_limit - 1
    ]  # 例如 3 天窗口 -> 2 个历史 DataFrame
    for _, row in df.iterrows():
        ts_code = str(row["ts_code"])
        if name_col:
            raw_name = str(row[name_col])
            # 给 LLM 的名称直接带上代码，方便在自然语言中引用
            name = f"{raw_name}({ts_code})"
        else:
            name = ts_code
        industry = str(row[industry_col]) if industry_col else ""
        concepts = str(concepts_val) if (concepts_val := row.get(concepts_col)) is not None else ""

        # 价格与成交
        open_val = float(row[open_col]) if open_col else float("nan")
        high_val = float(row[high_col]) if high_col else float("nan")
        low_val = float(row[low_col]) if low_col else float("nan")
        close_val = float(row[close_col]) if close_col else float("nan")
        pre_close_val = float(row[pre_close_col]) if pre_close_col else float("nan")
        pct_chg_val = float(row[pct_chg_col]) if pct_chg_col else float("nan")
        volume_val = float(row[volume_col]) if volume_col else float("nan")
        amount_val = float(row[amount_col]) if amount_col else float("nan")
        vol_ratio_val = float(row[vol_ratio_col]) if vol_ratio_col else float("nan")

        # 估值
        pe_val = float(row[pe_col]) if pe_col else float("nan")
        pb_val = float(row[pb_col]) if pb_col else float("nan")
        ps_val = float(row[ps_col]) if ps_col else float("nan")
        dv_val = float(row[dv_col]) if dv_col else float("nan")
        circ_mv_val = float(row[circ_mv_col]) if circ_mv_col else float("nan")

        macd_status = _infer_macd_status(row)

        if days_to_high_col:
            try:
                days_to_high_val = int(row[days_to_high_col])
            except Exception:
                days_to_high_val = -1
        else:
            days_to_high_val = -1

        score = float(row.get("predicted_score", row.get("score", 0.0)))
        status = _status(ts_code)

        # 连续在榜天数（含今天），最多记录到 3
        days_on_top = 1
        for hist_df in effective_history:
            if "ts_code" not in hist_df.columns:
                break
            hist_set = set(hist_df["ts_code"].astype(str).tolist())
            if ts_code in hist_set:
                days_on_top += 1
            else:
                break
        if days_on_top > history_limit:
            days_on_top = history_limit

        rows.append(
            {
                "ts_code": ts_code,
                "name": name,
                "industry": industry,
                "concepts": concepts,
                "open": open_val,
                "high": high_val,
                "low": low_val,
                "close": close_val,
                "pre_close": pre_close_val,
                "pct_chg": pct_chg_val,
                "volume": volume_val,
                "amount": amount_val,
                "vol_ratio": vol_ratio_val,
                "pe": pe_val,
                "pb": pb_val,
                "ps": ps_val,
                "dv": dv_val,
                "circ_mv": circ_mv_val,
                "macd_status": macd_status,
                "days_to_high": days_to_high_val,
                "score": score,
                "status": status,
                "days_on_top": days_on_top,
            }
        )

    table = pd.DataFrame(rows)
    # 按 score / rank 保持原有排序
    if "rank" in df.columns:
        table = table.merge(df[["ts_code", "rank"]], on="ts_code", how="left")
        table = table.sort_values(["rank", "score"], ascending=[True, False])
        table = table.drop(columns=["rank"], errors="ignore")

    return table


def summarize_recent_top_history(top_table: pd.DataFrame) -> str:
    """
    基于 days_on_top 生成一个适合放入 Prompt 的简短历史摘要。

    约定：days_on_top=1 视为新进；2 为连续两天；3 为连续三天及以上（已到或超过策略持仓窗口）。
    """
    if top_table.empty or "days_on_top" not in top_table.columns:
        return "当前仅有当日 Top 榜单信息，历史连续在榜天数信息暂不可用。"

    total = len(top_table)
    d1 = int((top_table["days_on_top"] == 1).sum())
    d2 = int((top_table["days_on_top"] == 2).sum())
    d3 = int((top_table["days_on_top"] >= 3).sum())

    return (
        f"本次 Top 榜单共 {total} 只股票，其中："
        f"新进(1天在榜) {d1} 只，"
        f"连续2天在榜 {d2} 只，"
        f"连续3天及以上在榜 {d3} 只。"
        "策略假设单票合理持仓周期约为 3 天，"
        "请对连续3天及以上在榜的标的重点关注止盈与回撤风险。"
    )


def _to_markdown_table(df: pd.DataFrame, columns: Iterable[str]) -> str:
    """将 df 的指定列渲染为 Markdown 表格文本."""
    subset = df[list(columns)].copy()

    header = "| " + " | ".join(subset.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(subset.columns)) + "|"

    rows = []
    for _, row in subset.iterrows():
        cells = []
        for col in subset.columns:
            val = row[col]
            cells.append(str(val))
        rows.append("| " + " | ".join(cells) + " |")

    lines = [header, sep] + rows
    return "\n".join(lines)


def build_daily_prompts(
    current_date: str,
    top_table: pd.DataFrame,
    history_summary: str,
) -> Tuple[str, str]:
    """
    根据当前日期 + TopN 精简表 + 昨日榜单摘要，构建 System/User Prompt。

    此处的中文 Prompt 文本可以在后续迭代中微调，但结构基本符合“虚拟投委会”的设定。
    """
    system_prompt = """# Role
你是由 Python 量化策略辅助的资深交易员，兼具量化基金经理和风险控制官双重视角。你的目标是根据量化模型输出的数据，撰写一份《每日收盘交易决策简报》。

# Strategy Context (策略背景)
我们的量化模型是一个“复合动量策略”(Composite Momentum Strategy)，核心逻辑如下：
1. 趋势突破：寻找当日强势突破、价格处于上升通道的股票。
2. 中期确认：使用 MACD 及相关动量指标确认中期趋势向上。
3. 位置优势：优先选择接近历史新高或近期新高的标的。

# Your Task (你的任务)
模型只负责计算分数，你需要负责逻辑解释和风险把控。请基于输入的数据，从以下三个维度进行分析：

## 1. 市场风格与板块协同 (Sector Synergy)
- 核心任务：找出 Top 榜单中是否有集中的“行业”或“概念”。
- 若 Top 榜单中出现明显的行业/概念集群，请指出可能的主线板块，并评估行情的持续性。

## 2. 个股逻辑校验 (Stock Logic Check)
- 新进关注(New Entry)：对于今天新出现在榜单的股票，结合“涨跌幅”“量比”“MACD 状态”“距离新高天数”，分析其爆发力与可持续性。
- 持仓跟踪(Holding)：对于昨天就在榜单的股票，确认其趋势是否延续，是否仍然值得持有或加仓。
- 异常值检测：如果某只股票评分很高，但出现缩量、极端高位 RSI 或远离板块主线，请提示潜在风险。

## 3. 风险提示 (Risk Warning)
- 基于“行业/概念”，指出当前环境下可能波动较大或容易受突发事件影响的板块。
- 检查是否存在类似 ST、长期大幅上涨后有明显回撤风险的标的，并给出防守建议。

# Output Format (输出格式)
请用 Markdown 输出一份结构清晰、条理分明的中文分析，包含：
- 市场风格小结
- 重点板块与龙头股票点评
- 新进和维持个股的操作建议
- 总体风险提示与仓位建议
"""

    table_md = _to_markdown_table(
        top_table,
        [
            "ts_code",
            "name",
            "open",
            "high",
            "low",
            "industry",
            "concepts",
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
        ],
    )

    user_prompt = f"""# 今日日期: {current_date}

# 输入数据 A: 今日 Top 评分表
下表为模型选出的当日高分股票列表，包括基础行情、行业/概念标签与技术形态摘要：

{table_md}

# 输入数据 B: 最近 3 个交易日 Top 榜单摘要
{history_summary}

# 指令
请根据上述数据，重点回答：
1. 今天是否存在明显的板块/概念主线？哪些行业或题材最值得关注？
2. 哪些是“新进”股票，是否具备继续放量上攻的条件？
3. 哪些是“维持”股票，其趋势是否健康，有无减仓或止盈信号？
4. 当前总体风险水平如何，你会给出怎样的仓位与操作节奏建议？
"""

    return system_prompt, user_prompt


def generate_analysis(
    current_top: pd.DataFrame,
    history_tops: Optional[Sequence[pd.DataFrame]],
    current_date: str,
) -> Tuple[str, str]:
    """
    高层接口：构建适合 LLM 输入的 Prompt。

    history_tops: 最近若干个交易日的 Top 列表（按时间从近到远排序，比如 [昨天, 前天, 大前天]），
    内部会聚焦最近 3 天窗口来计算 days_on_top。
    """
    table = build_llm_top_table(current_top=current_top, history_tops=history_tops)
    history_summary = summarize_recent_top_history(table)

    system_prompt, user_prompt = build_daily_prompts(
        current_date=current_date,
        top_table=table,
        history_summary=history_summary,
    )
    return system_prompt, user_prompt


async def _call_single_report_llm(
    system_prompt: str,
    user_prompt: str,
    stage_name: str,
) -> str:
    """
    内部异步封装：针对单一阶段（如 daily_report_gpt）调用一次 LLM。
    """
    # 延迟导入，以避免在无依赖环境下影响其它模块/测试
    llm_client_module = import_module("LLMClient_v2.llm_client")
    LLMClient = getattr(llm_client_module, "LLMClient")

    client = LLMClient.from_stage(stage_name=stage_name)

    full_prompt = system_prompt.strip() + "\n\n---\n\n" + user_prompt.strip()

    response = await client.get_completion(
        prompt=full_prompt,
        stage=stage_name,
    )

    if not response.success:
        return f"[LLM 调用失败 - {stage_name}] {response.error or ''}".strip()

    return response.content


def generate_daily_reports_via_llm(
    current_top: pd.DataFrame,
    history_tops: Optional[Sequence[pd.DataFrame]],
    current_date: str,
    stages: Optional[Sequence[str]] = None,
) -> Dict[str, str]:
    """
    高层同步接口：
    - 基于 current_top + history_tops 构建 Prompt
    - 分别调用多个 LLM 阶段（默认 GPT + Gemini）生成两版报告

    Args:
        current_top: 当日 TopN DataFrame（包含 ts_code / predicted_score / rank 等）
        history_tops: 最近若干交易日 Top 列表（如 [昨天, 前天, 大前天]），可为 None
        current_date: 当前自然日期字符串（如 "2025-12-18"）
        stages: 要调用的阶段名称列表，默认 ["daily_report_gpt", "daily_report_gemini"]

    Returns:
        {stage_name: report_text}
    """
    system_prompt, user_prompt = generate_analysis(
        current_top=current_top,
        history_tops=history_tops,
        current_date=current_date,
    )

    stage_list = list(stages or ["daily_report_gpt", "daily_report_gemini"])

    async def _run_all() -> Dict[str, str]:
        results: Dict[str, str] = {}
        for stage_name in stage_list:
            try:
                content = await _call_single_report_llm(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    stage_name=stage_name,
                )
            except Exception as exc:  # 网络/配置异常时兜底
                content = f"[LLM 调用异常 - {stage_name}] {exc}"
            results[stage_name] = content
        return results

    return asyncio.run(_run_all())
