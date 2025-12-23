from pathlib import Path
import sys

import pandas as pd

CURRENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from aggregate_feature_importance import aggregate_feature_importance  # type: ignore


def test_aggregate_feature_importance_basic(tmp_path: Path) -> None:
    """
    构造一份简单的 feature_importance CSV，验证：
    - 可以按前缀聚合
    - 生成 group, importance 两列
    """
    input_path = tmp_path / "toy_importance.csv"
    df = pd.DataFrame(
        {
            "feature": ["pe_ttm", "pe_lyr", "macd_dif", "macd_dea", "other1"],
            "mean_abs_shap": [0.5, 0.3, 1.0, 0.7, 0.05],
        }
    )
    df.to_csv(input_path, index=False, encoding="utf-8")

    output_path = tmp_path / "toy_grouped.csv"
    aggregate_feature_importance(
        input_path=input_path,
        output_path=output_path,
        min_share_for_group=0.05,
    )

    assert output_path.exists()
    grouped = pd.read_csv(output_path)
    assert set(grouped.columns) == {"group", "importance"}
    # 前缀 pe / macd 至少应该分别作为一个组存在（或 importance 合理大于 0）
    assert (grouped["group"] == "pe").any()
    assert (grouped["group"] == "macd").any()

