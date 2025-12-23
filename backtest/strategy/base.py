from dataclasses import dataclass
from typing import List, Optional

@dataclass
class StrategyConfig:
    name: str
    method: str = "top_n"  # top_n, percentile, threshold
    n: int = 5
    ascending: bool = False  # False means higher score is better
