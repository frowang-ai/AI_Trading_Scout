from pathlib import Path

import pandas as pd

from backtest.visualization.report import ReportBuilder


def test_generate_multi_html_creates_file() -> None:
    """
    轻量验证多策略报告：
    - 能正常生成 report_multi_strategies.html
    - HTML 中包含两个策略名称和多策略标题
    """
    current_dir = Path(__file__).parent.resolve()
    tmp_dir = current_dir / "_tmp_test_multi_reports"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    builder = ReportBuilder(tmp_dir)

    index = pd.date_range("2025-01-01", periods=3, freq="D")
    columns = pd.MultiIndex.from_product(
        [["ret_1d"], ["mean", "win_rate"]], names=["metric", "stat"]
    )
    cohort_summary = pd.DataFrame(
        [[0.01, 0.6], [0.0, 0.5], [-0.005, 0.4]],
        index=index,
        columns=columns,
    )

    ic_df = pd.DataFrame(
        {"ic_1d": [0.1, 0.2, 0.0]},
        index=index,
    )

    results = {
        "Top_5_Score": {
            "cohort_summary": cohort_summary,
            "ic_df": ic_df,
        },
        "Top_10_Score": {
            "cohort_summary": cohort_summary,
            "ic_df": ic_df,
        },
    }

    builder.generate_multi_html(results)

    output_file = tmp_dir / "report_multi_strategies.html"
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert "Backtest Multi-Strategy Report" in content
    assert "Top_5_Score" in content
    assert "Top_10_Score" in content

