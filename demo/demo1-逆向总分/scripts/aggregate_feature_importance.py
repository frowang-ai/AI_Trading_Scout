import argparse
import sys
from pathlib import Path
from typing import Dict

import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


def aggregate_feature_importance(
    input_path: Path,
    output_path: Path,
    min_share_for_group: float = 0.02,
) -> None:
    """
    基于 *_importance.csv 自动按前缀聚合特征重要性。

    - 输入文件需包含列：feature, mean_abs_shap
    - 默认以上划线前缀作为“因子族”名称，例如 pe_ttm -> pe
    - 对于重要性占比低于 min_share_for_group 的前缀，统一归入 'other'
    """
    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在：{input_path}")

    df = pd.read_csv(input_path)
    if "feature" not in df.columns or "mean_abs_shap" not in df.columns:
        raise ValueError("输入 CSV 必须包含列 'feature' 和 'mean_abs_shap'")

    # 1) 先按前缀做初步聚合
    def prefix(name: str) -> str:
        return name.split("_")[0] if "_" in name else name

    df["group"] = df["feature"].astype(str).map(prefix)
    grouped = df.groupby("group", as_index=False)["mean_abs_shap"].sum()

    # 2) 将权重过小的 group 汇总到 'other'
    total_importance = grouped["mean_abs_shap"].sum()
    if total_importance <= 0:
        raise ValueError("mean_abs_shap 总和为 0，无法聚合特征重要性")

    def normalize_group(row: Dict) -> str:
        share = row["mean_abs_shap"] / total_importance
        return row["group"] if share >= min_share_for_group else "other"

    grouped["final_group"] = grouped.apply(normalize_group, axis=1)
    result = (
        grouped.groupby("final_group", as_index=False)["mean_abs_shap"].sum()
        .rename(columns={"final_group": "group", "mean_abs_shap": "importance"})
        .sort_values("importance", ascending=False)
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Aggregated feature importance saved to: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate feature importance by prefix for Demo1."
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="输入 *_importance.csv 路径（包含 feature, mean_abs_shap 列）",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="输出聚合后的 CSV 路径（group, importance）",
    )
    parser.add_argument(
        "--min-share",
        type=float,
        default=0.02,
        help="最小重要性占比阈值，低于该阈值的 group 汇总到 'other'",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    aggregate_feature_importance(
        input_path=input_path,
        output_path=output_path,
        min_share_for_group=args.min_share,
    )


if __name__ == "__main__":
    main()

