import pandas as pd
import numpy as np
from scipy.stats import spearmanr

class MetricsCalculator:
    @staticmethod
    def calculate_ic(wide_table: pd.DataFrame, hold_days: list = [1, 3, 5, 10]) -> pd.DataFrame:
        """
        Calculate Rank IC (Information Coefficient) daily.
        Correlation between total_score and future returns.
        """
        ic_data = []
        
        grouped = wide_table.groupby('trade_date')
        
        for date, group in grouped:
            # Drop NaNs
            group = group.dropna(subset=['total_score'])
            
            daily_ic = {'trade_date': date}
            for d in hold_days:
                col = f'ret_{d}d'
                if col in group.columns:
                    # Drop NaNs in return column
                    valid = group.dropna(subset=[col])
                    if len(valid) > 10: # Need enough samples
                        corr, _ = spearmanr(valid['total_score'], valid[col])
                        daily_ic[f'ic_{d}d'] = corr
                    else:
                        daily_ic[f'ic_{d}d'] = np.nan
            
            ic_data.append(daily_ic)
            
        return pd.DataFrame(ic_data).set_index('trade_date')

    @staticmethod
    def calculate_overall_performance(cohort_summary: pd.DataFrame) -> pd.DataFrame:
        """
        Summarize the daily cohort performance into a single table.
        """
        # cohort_summary has MultiIndex columns: (ret_1d, mean), (ret_1d, win_rate)...
        
        stats = []
        
        # Flatten columns if needed, but let's assume we iterate through levels
        # The summary columns are like ('ret_1d', 'mean'), ('ret_1d', 'win_rate')
        
        # Extract holding periods from columns
        cols = cohort_summary.columns
        # Assuming structure from CohortAnalyzer.aggregate
        
        # We want to average the daily means, average the daily win rates
        
        summary = cohort_summary.mean()
        return summary
