import pandas as pd
import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backtest import config
from backtest.strategy.base import StrategyConfig
from backtest.strategy.generator import SignalGenerator
from backtest.engine.cohort import CohortAnalyzer
from backtest.analysis.metrics import MetricsCalculator
from backtest.visualization.report import ReportBuilder

def main():
    parser = argparse.ArgumentParser(description="Run Backtest")
    parser.add_argument(
        "--top_n",
        type=int,
        default=5,
        help="Number of stocks to select (single-strategy mode)",
    )
    parser.add_argument(
        "--top_n_list",
        type=str,
        default="",
        help="Multiple Top N strategies, comma separated (e.g. '5,10,20'). "
             "If provided, overrides --top_n and generates a multi-strategy report.",
    )
    parser.add_argument(
        "--days",
        type=str,
        default=",".join(str(d) for d in config.DEFAULT_HOLD_DAYS),
        help="Holding periods (comma separated)",
    )
    args = parser.parse_args()

    hold_days = [int(d.strip()) for d in args.days.split(",") if d.strip()]

    # 1. Load Data
    print(f"Holding Days: {hold_days}")
    print("Loading wide table...")
    if not config.WIDE_TABLE_PATH.exists():
        print("Wide table not found. Please run backtest/data/builder.py first.")
        return

    wide_table = pd.read_parquet(config.WIDE_TABLE_PATH)
    print(f"Loaded {len(wide_table)} records.")

    # 2. Analysis (IC) - can be shared across strategies
    ic_df = MetricsCalculator.calculate_ic(wide_table, hold_days)
    if 'ic_1d' in ic_df.columns:
        print(f"Avg IC (1D): {ic_df['ic_1d'].mean():.4f}")
    else:
        print("IC calc failed")

    # Multi-strategy mode
    if args.top_n_list:
        top_n_values = [int(x.strip()) for x in args.top_n_list.split(",") if x.strip()]
        print(f"Running multi-strategy backtest for Top N: {top_n_values}")

        results_by_strategy = {}
        analyzer = CohortAnalyzer(wide_table)

        for n in top_n_values:
            strategy_name = f"Top_{n}_Score"
            print(f"\n=== Strategy {strategy_name} ===")

            strategy_config = StrategyConfig(
                name=strategy_name,
                method="top_n",
                n=n,
                ascending=False,
            )

            generator = SignalGenerator(wide_table)
            signals = generator.generate(strategy_config)
            print(f"Generated {len(signals)} signals.")

            if signals.empty:
                print("No signals generated for this strategy, skip.")
                continue

            detailed_results = analyzer.run(signals, hold_days)
            cohort_summary = analyzer.aggregate(detailed_results, hold_days)

            print("Cohort Analysis Complete.")
            print(cohort_summary.head())

            results_by_strategy[strategy_name] = {
                "cohort_summary": cohort_summary,
                "ic_df": ic_df,
                "detailed_results": detailed_results,
            }

        if not results_by_strategy:
            print("No valid strategies to report, exiting.")
            return

        report_builder = ReportBuilder(config.OUTPUT_DIR)
        report_builder.generate_multi_html(results_by_strategy)
        print("Multi-strategy backtest done.")
        return

    # Single-strategy mode (default)
    print(f"Running single-strategy backtest for Top {args.top_n}")

    strategy_config = StrategyConfig(
        name=f"Top_{args.top_n}_Score",
        method="top_n",
        n=args.top_n,
        ascending=False,  # Higher score is better
    )

    generator = SignalGenerator(wide_table)
    signals = generator.generate(strategy_config)
    print(f"Generated {len(signals)} signals.")

    if signals.empty:
        print("No signals generated.")
        return

    analyzer = CohortAnalyzer(wide_table)
    detailed_results = analyzer.run(signals, hold_days)
    cohort_summary = analyzer.aggregate(detailed_results, hold_days)

    print("Cohort Analysis Complete.")
    print(cohort_summary.head())

    report_builder = ReportBuilder(config.OUTPUT_DIR)
    report_builder.generate_html(cohort_summary, ic_df, strategy_config.name, detailed_results)

    print("Done.")

if __name__ == "__main__":
    main()
