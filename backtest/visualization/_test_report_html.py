from pathlib import Path

import pandas as pd

from backtest.visualization.report import ReportBuilder


def test_report_html_basic_structure() -> None:
    """
    轻量验证 ReportBuilder 生成的 HTML：
    - 使用 container 的 max-width 样式
    - 能正常输出到指定目录
    """
    current_dir = Path(__file__).parent.resolve()
    tmp_dir = current_dir / "_tmp_test_reports"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    builder = ReportBuilder(tmp_dir)

    # 构造最小化的 cohort_summary 与 ic_df
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

    strategy_name = "Test_Strategy"
    builder.generate_html(cohort_summary, ic_df, strategy_name, detailed_results=None)

    output_file = tmp_dir / f"report_{strategy_name}.html"
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert "max-width" in content
    assert "Backtest Report" in content

