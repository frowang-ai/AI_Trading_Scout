import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path

class ReportBuilder:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def _build_figures(
        self,
        cohort_summary: pd.DataFrame,
        ic_df: pd.DataFrame,
        strategy_name: str,
    ):
        """
        为单个策略构建三张核心图表：
        - 持仓天数 vs 平均收益 & 胜率
        - 各持仓天数的“累计平均收益”曲线
        - IC Decay 柱状图
        """
        periods = []
        means = []
        win_rates = []

        # Identify holding periods from columns
        # Columns are MultiIndex: ('ret_1d', 'mean'), ...
        levels = cohort_summary.columns
        # 先抽取 (天数, 列名前缀)，再按天数数值排序，避免 'ret_10d' 排在 'ret_1d' 前面
        ret_key_pairs = sorted(
            {
                (int(c[0].replace("ret_", "").replace("d", "")), c[0])
                for c in levels
                if isinstance(c[0], str) and c[0].startswith("ret_")
            },
            key=lambda x: x[0],
        )
        ret_keys = [name for _, name in ret_key_pairs]

        for key in ret_keys:
            period = key.replace('ret_', '').replace('d', '')
            periods.append(f"{period} Days")
            means.append(cohort_summary[(key, 'mean')].mean() * 100)  # %
            win_rates.append(cohort_summary[(key, 'win_rate')].mean() * 100)  # %

        # 1. 持仓天数 vs 平均收益 & 胜率
        fig_perf = make_subplots(specs=[[{"secondary_y": True}]])

        fig_perf.add_trace(
            go.Bar(x=periods, y=means, name="Avg Return (%)", marker_color='indianred'),
            secondary_y=False,
        )

        fig_perf.add_trace(
            go.Scatter(
                x=periods,
                y=win_rates,
                name="Win Rate (%)",
                mode='lines+markers',
                marker_color='royalblue',
            ),
            secondary_y=True,
        )

        fig_perf.update_layout(title_text=f"Strategy Performance by Holding Period ({strategy_name})")
        fig_perf.update_yaxes(title_text="Avg Return (%)", secondary_y=False)
        fig_perf.update_yaxes(title_text="Win Rate (%)", secondary_y=True)

        # 2. Cumulative Return (by holding period)
        # 注意：这是信号层面的累计平均收益，不是完整账户资金曲线。
        fig_equity = go.Figure()
        for key in ret_keys:
            col = (key, "mean")
            if col not in cohort_summary.columns:
                continue
            cum_ret = (1 + cohort_summary[col]).cumprod()
            period = key.replace("ret_", "").replace("d", "")
            fig_equity.add_trace(
                go.Scatter(
                    x=cohort_summary.index,
                    y=cum_ret,
                    name=f"{period}D Hold",
                )
            )

        fig_equity.update_layout(
            title_text="Cumulative Average Return by Holding Period",
            xaxis_title="Date",
            yaxis_title="Cumulative Return (Signal Level)",
        )

        # 3. IC Decay
        ic_means = ic_df.mean()
        fig_ic = go.Bar(
            x=[c.replace('ic_', '').replace('d', ' Days') for c in ic_means.index],
            y=ic_means.values,
            marker_color='teal',
        )
        fig_ic_layout = go.Layout(title_text="Information Coefficient (IC) Decay")
        fig_ic_obj = go.Figure(data=[fig_ic], layout=fig_ic_layout)

        return fig_perf, fig_equity, fig_ic_obj, ic_means

    def generate_html(self, 
                      cohort_summary: pd.DataFrame, 
                      ic_df: pd.DataFrame, 
                      strategy_name: str,
                      detailed_results: pd.DataFrame = None):
        """
        Generate an HTML report with Plotly charts.
        """
        fig_perf, fig_equity, fig_ic_obj, ic_means = self._build_figures(
            cohort_summary, ic_df, strategy_name
        )

        # Generate HTML
        html_content = f"""
        <html>
        <head>
            <title>Backtest Report - {strategy_name}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                h1, h2 {{ color: #333; }}
                .chart {{ margin-bottom: 40px; }}
                .strategy-grid {{ display: flex; gap: 20px; flex-wrap: wrap; }}
                .strategy-column {{ flex: 1 1 300px; min-width: 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Backtest Report: {strategy_name}</h1>
                <p>Generated on: {pd.Timestamp.now()}</p>
                
                <div class="chart">
                    {fig_perf.to_html(full_html=False, include_plotlyjs=False)}
                </div>
                
                <div class="chart">
                    {fig_equity.to_html(full_html=False, include_plotlyjs=False)}
                </div>
                
                <div class="chart">
                    {fig_ic_obj.to_html(full_html=False, include_plotlyjs=False)}
                </div>
                
                <h2>Detailed Metrics</h2>
                <p>Average IC: {ic_means.mean():.4f}</p>
            </div>
        </body>
        </html>
        """
            
        output_file = self.output_dir / f"report_{strategy_name}.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"Report saved to {output_file}")

    def generate_multi_html(
        self,
        results_by_strategy: dict,
    ) -> None:
        """
        生成多策略“合并图”报告：
        - 图1：不同策略在各持仓天数上的平均收益曲线
        - 图2：不同策略在各持仓天数上的胜率曲线
        - 图3：固定持仓天数（优先 1D）的累计平均收益曲线（按策略对比）
        - 图4：整体 IC Decay（与策略无关，但一起展示在多策略报告中）
        """
        if not results_by_strategy:
            print("No strategies provided for multi-strategy report.")
            return

        strategy_names = list(results_by_strategy.keys())

        # 假定所有策略使用相同的持仓天数配置，取第一个策略的列结构作为基准
        first_strategy = strategy_names[0]
        first_cohort = results_by_strategy[first_strategy]["cohort_summary"]
        levels = first_cohort.columns
        ret_key_pairs = sorted(
            {
                (int(c[0].replace("ret_", "").replace("d", "")), c[0])
                for c in levels
                if isinstance(c[0], str) and c[0].startswith("ret_")
            },
            key=lambda x: x[0],
        )
        ret_keys = [name for _, name in ret_key_pairs]

        # 解析持仓天数（整数）
        holding_days = [int(k.replace("ret_", "").replace("d", "")) for k in ret_keys]

        # 图1：平均收益 vs 持仓天数（多策略对比）
        fig_avg = go.Figure()
        for name in strategy_names:
            cohort_summary = results_by_strategy[name]["cohort_summary"]
            avg_returns = []
            for key in ret_keys:
                col = (key, "mean")
                if col in cohort_summary.columns:
                    avg_returns.append(cohort_summary[col].mean() * 100)
                else:
                    avg_returns.append(None)
            fig_avg.add_trace(
                go.Scatter(
                    x=holding_days,
                    y=avg_returns,
                    name=name,
                    mode="lines+markers",
                )
            )

        fig_avg.update_layout(
            title_text="Average Return by Holding Period (Multi-Strategy)",
            xaxis_title="Holding Days",
            yaxis_title="Avg Return (%)",
        )
        fig_avg.update_xaxes(dtick=1)

        # 图2：胜率 vs 持仓天数（多策略对比）
        fig_win = go.Figure()
        for name in strategy_names:
            cohort_summary = results_by_strategy[name]["cohort_summary"]
            win_rates = []
            for key in ret_keys:
                col = (key, "win_rate")
                if col in cohort_summary.columns:
                    win_rates.append(cohort_summary[col].mean() * 100)
                else:
                    win_rates.append(None)
            fig_win.add_trace(
                go.Scatter(
                    x=holding_days,
                    y=win_rates,
                    name=name,
                    mode="lines+markers",
                )
            )

        fig_win.update_layout(
            title_text="Win Rate by Holding Period (Multi-Strategy)",
            xaxis_title="Holding Days",
            yaxis_title="Win Rate (%)",
        )
        fig_win.update_xaxes(dtick=1)
        fig_win.update_xaxes(dtick=1)

        # 图3：固定持仓天数的累计平均收益（按策略对比）
        target_key = "ret_1d" if "ret_1d" in ret_keys else ret_keys[0]
        target_days = target_key.replace("ret_", "").replace("d", "")

        fig_cum = go.Figure()
        for name in strategy_names:
            cohort_summary = results_by_strategy[name]["cohort_summary"]
            col = (target_key, "mean")
            if col not in cohort_summary.columns:
                continue
            cum_ret = (1 + cohort_summary[col]).cumprod()
            fig_cum.add_trace(
                go.Scatter(
                    x=cohort_summary.index,
                    y=cum_ret,
                    name=name,
                )
            )

        fig_cum.update_layout(
            title_text=f"Cumulative Average Return ({target_days}D Hold, Multi-Strategy)",
            xaxis_title="Date",
            yaxis_title="Cumulative Return (Signal Level)",
        )

        # 图4：IC Decay（所有策略共用一份 IC）
        any_ic_df = results_by_strategy[first_strategy]["ic_df"]
        ic_means = any_ic_df.mean()
        fig_ic = go.Figure(
            data=[
                go.Bar(
                    x=[c.replace("ic_", "").replace("d", " Days") for c in ic_means.index],
                    y=ic_means.values,
                    marker_color="teal",
                    name="IC",
                )
            ]
        )
        fig_ic.update_layout(title_text="Information Coefficient (IC) Decay")

        strategies_desc = ", ".join(strategy_names)

        # 计算整体回测区间（所有策略的 trade_date 并集）
        all_dates = None
        for name in strategy_names:
            idx = results_by_strategy[name]["cohort_summary"].index
            all_dates = idx if all_dates is None else all_dates.union(idx)
        start_date = all_dates.min() if all_dates is not None else None
        end_date = all_dates.max() if all_dates is not None else None
        start_str = start_date.strftime("%Y-%m-%d") if start_date is not None else "N/A"
        end_str = end_date.strftime("%Y-%m-%d") if end_date is not None else "N/A"

        holding_days_str = ", ".join(str(d) for d in holding_days)

        html_content = f"""
        <html>
        <head>
            <title>Backtest Multi-Strategy Report</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                h1, h2 {{ color: #333; }}
                .chart {{ margin-bottom: 40px; }}
                .summary-table {{ border-collapse: collapse; margin: 10px 0 30px 0; }}
                .summary-table th, .summary-table td {{ border: 1px solid #ddd; padding: 6px 10px; font-size: 14px; }}
                .summary-table th {{ background-color: #f0f2f5; text-align: left; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Backtest Multi-Strategy Report</h1>
                <p>Strategies: {strategies_desc}</p>
                <table class="summary-table">
                    <tr>
                        <th>Backtest Window</th>
                        <td>{start_str} ~ {end_str}</td>
                    </tr>
                    <tr>
                        <th>Holding Days Used</th>
                        <td>{holding_days_str}</td>
                    </tr>
                </table>
                <div class="chart">
                    {fig_avg.to_html(full_html=False, include_plotlyjs=False)}
                </div>
                <div class="chart">
                    {fig_win.to_html(full_html=False, include_plotlyjs=False)}
                </div>
                <div class="chart">
                    {fig_cum.to_html(full_html=False, include_plotlyjs=False)}
                </div>
                <div class="chart">
                    {fig_ic.to_html(full_html=False, include_plotlyjs=False)}
                </div>
            </div>
        </body>
        </html>
        """

        output_file = self.output_dir / "report_multi_strategies.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"Multi-strategy report saved to {output_file}")
