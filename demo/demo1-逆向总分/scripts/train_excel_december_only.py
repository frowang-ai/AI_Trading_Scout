import argparse
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.data_loader import load_dataset
from src.feature_eng import process_excel_features
from src.model_engine import ScorePredictor


def main() -> None:
    parser = argparse.ArgumentParser(description="Train & evaluate Excel-only model using December data only.")
    parser.add_argument(
        "--start-date",
        type=str,
        default="20251201",
        help="12 月起始日期（YYYYMMDD），默认为 20251201",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default="20251231",
        help="12 月结束日期（YYYYMMDD），默认为 20251231",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(PROJECT_ROOT / "output"),
        help="模型与评估结果输出目录",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    model_path = output_dir / "excel_model_december_only.pkl"

    print("Starting December-only Excel Model Training Pipeline...")

    # 1. 只加载 12 月数据
    df = load_dataset(
        source_type="excel_only",
        start_date=args.start_date,
        end_date=args.end_date,
    )
    print(f"[December-only] Loaded {len(df)} rows of data.")

    if df.empty:
        print("No December data loaded. Exit.")
        return

    # 2. 特征工程
    X, y, _ = process_excel_features(df)
    print(f"[December-only] Features processed: {X.shape[1]} features.")

    # 3. 在 12 月内部做 80/20 划分（不再跨月）
    split_idx = int(len(X) * 0.8)
    X_train, X_valid = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_valid = y.iloc[:split_idx], y.iloc[split_idx:]

    # 4. 训练模型
    predictor = ScorePredictor(model_path=model_path)
    predictor.set_metadata(
        source_type="excel_only_december_only",
        start_date=args.start_date,
        end_date=args.end_date,
    )
    predictor.fit(X_train, y_train, X_valid=X_valid, y_valid=y_valid)

    # 5. 评估：只看 12 月内部的拟合 & 排序能力
    metrics_train = predictor.evaluate(X_train, y_train, dataset_name="December-Train", verbose=True)
    metrics_valid = predictor.evaluate(X_valid, y_valid, dataset_name="December-Valid", verbose=True)

    print("\n[December-only] Model Performance Summary:")
    for name, metrics in [("Train", metrics_train), ("Valid", metrics_valid)]:
        print(f"  [{name}] r2={metrics['r2']:.4f}, mae={metrics['mae']:.4f}, rmse={metrics['rmse']:.4f}")

    # 6. 保存模型
    predictor.save(model_path=model_path)

    # 7. 输出特征列表与 SHAP 报告，单独放一个子目录，方便和 11 月版本对比
    shap_output_dir = output_dir / "shap_excel_december_only"
    predictor.export_shap_report(
        X_sample=X_valid if not X_valid.empty else X_train,
        output_dir=shap_output_dir,
        prefix="excel_model_december_only",
        max_samples=5000,
    )


if __name__ == "__main__":
    main()

