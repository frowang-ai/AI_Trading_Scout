import argparse
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.data_loader import load_dataset
from src.feature_eng import process_tushare_features
from src.model_engine import ScorePredictor


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Tushare-only proxy model for Demo1.")
    parser.add_argument("--start-date", type=str, default="20251101")
    parser.add_argument("--end-date", type=str, default="20251130")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(PROJECT_ROOT / "output"),
        help="模型与报告输出目录",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    model_path = output_dir / "tushare_model.pkl"

    print("Starting Tushare Model Training Pipeline...")

    # 1. Load Data (Merged: Excel Target + Tushare Features)
    df = load_dataset(
        source_type="tushare_only",
        start_date=args.start_date,
        end_date=args.end_date,
    )
    if df.empty:
        print("No data loaded. Exiting.")
        return
    print(f"Loaded {len(df)} rows of data.")

    # 2. Feature Engineering
    X, y, _ = process_tushare_features(df)
    print(f"Features processed: {X.shape[1]} features.")

    # 简单划分训练/验证：80/20
    split_idx = int(len(X) * 0.8)
    X_train, X_valid = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_valid = y.iloc[:split_idx], y.iloc[split_idx:]

    # 3. Train Model
    predictor = ScorePredictor(model_path=model_path)
    predictor.set_metadata(
        source_type="tushare_only",
        start_date=args.start_date,
        end_date=args.end_date,
    )
    predictor.fit(X_train, y_train, X_valid=X_valid, y_valid=y_valid)

    # 4. Evaluate
    metrics_train = predictor.evaluate(X_train, y_train, dataset_name="Train", verbose=True)
    metrics_valid = predictor.evaluate(X_valid, y_valid, dataset_name="Valid", verbose=True)

    print("\nModel Performance Summary:")
    for name, metrics in [("Train", metrics_train), ("Valid", metrics_valid)]:
        print(f"  [{name}] r2={metrics['r2']:.4f}, mae={metrics['mae']:.4f}, rmse={metrics['rmse']:.4f}")

    # 5. Save model + metadata
    predictor.save(model_path=model_path)

    # 6. 输出特征列表与全量 SHAP 报告
    shap_output_dir = output_dir / "shap_tushare"
    predictor.export_shap_report(
        X_sample=X_valid if not X_valid.empty else X_train,
        output_dir=shap_output_dir,
        prefix="tushare_model",
        max_samples=5000,
    )


if __name__ == "__main__":
    main()

