import argparse
import sys
from pathlib import Path

import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.data_loader import load_excel_data
from src.feature_eng import process_excel_features
from src.model_engine import ScorePredictor
from src.monitor import alert_if_drift_detected, calculate_daily_drift


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily Model Monitor & Inference")
    parser.add_argument("--date", type=str, required=True, help="Date to process (YYYYMMDD)")
    parser.add_argument("--model", type=str, default="excel_model.pkl", help="Model filename in output/")
    args = parser.parse_args()

    date_str = args.date
    model_path = PROJECT_ROOT / "output" / args.model

    print(f"Running Daily Monitor for {date_str} using {args.model}...")

    # 1. Load Data（这里仍使用 Excel-only，方便做漂移校验）
    df = load_excel_data(date_str)
    if df.empty:
        print(f"No data found for {date_str}")
        return

    print(f"Loaded {len(df)} rows.")

    # 2. Load Model
    predictor = ScorePredictor(model_path=model_path)
    if not predictor.load(model_path=model_path):
        print("Failed to load model. Please train it first.")
        return

    # 3. Prepare Features
    try:
        X, y_actual, _ = process_excel_features(df)

        # 4. Predict（内部会自动按 feature_names 对齐列）
        y_pred = predictor.predict(X)

        # 5. Monitor Drift
        df_pred = pd.DataFrame(
            {
                "ts_code": df["ts_code"],
                "pred_score": y_pred,
            }
        )

        df_actual = pd.DataFrame(
            {
                "ts_code": df["ts_code"],
                "total_score": y_actual,
            }
        )

        metrics = calculate_daily_drift(df_pred, df_actual)
        alert_if_drift_detected(metrics)

        # 6. Save Predictions
        output_file = PROJECT_ROOT / "output" / f"pred_{date_str}.csv"
        df_pred.to_csv(output_file, index=False, encoding="utf-8")
        print(f"Predictions saved to {output_file}")

    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

