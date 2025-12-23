import pandas as pd
import numpy as np
from typing import List, Dict

class CohortAnalyzer:
    def __init__(self, wide_table: pd.DataFrame):
        # Index wide table by (trade_date, ts_code) for fast lookup
        self.wide_table = wide_table.set_index(['trade_date', 'ts_code'])

    def run(self, signals: pd.DataFrame, hold_days: List[int] = [1, 3, 5, 10]) -> pd.DataFrame:
        """
        Calculate returns for each signal for different holding periods.
        """
        results = []
        
        # Iterate through signals
        # It's faster to join than to iterate rows
        # Join signals with wide_table to get returns
        
        # signals has ['trade_date', 'ts_code']
        # wide_table has ['ret_1d', 'ret_3d', ...]
        
        # Perform inner join to get returns for selected stocks
        merged = pd.merge(
            signals, 
            self.wide_table.reset_index(), 
            on=['trade_date', 'ts_code'], 
            how='inner'
        )
        
        return merged
        
    def aggregate(self, detailed_results: pd.DataFrame, hold_days: List[int] = [1, 3, 5, 10]) -> pd.DataFrame:
        """
        Aggregate detailed results by date to get daily performance.
        """
        agg_dict = {}
        for d in hold_days:
            col = f'ret_{d}d'
            if col in detailed_results.columns:
                agg_dict[col] = ['mean', 'median', 'count', lambda x: (x > 0).mean()]
        
        # Rename lambda to win_rate
        # Pandas naming is tricky with lambda, let's do it manually or use named aggregation
        
        summary = detailed_results.groupby('trade_date').agg({
            f'ret_{d}d': ['mean', 'median', 'count'] for d in hold_days if f'ret_{d}d' in detailed_results.columns
        })
        
        # Calculate win rate separately
        for d in hold_days:
            col = f'ret_{d}d'
            if col in detailed_results.columns:
                win_rate = detailed_results.groupby('trade_date')[col].apply(lambda x: (x > 0).mean())
                summary[(col, 'win_rate')] = win_rate
                
        return summary
