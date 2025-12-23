import pandas as pd
from .base import StrategyConfig

class SignalGenerator:
    def __init__(self, wide_table: pd.DataFrame):
        self.df = wide_table

    def generate(self, config: StrategyConfig) -> pd.DataFrame:
        """
        Generate signals based on the strategy configuration.
        Returns a DataFrame with ['trade_date', 'ts_code', 'total_score']
        """
        df = self.df.copy()
        
        # Filter out rows with no score
        df = df.dropna(subset=['total_score'])
        
        signals = []
        
        # Group by date
        grouped = df.groupby('trade_date')
        
        for date, group in grouped:
            if config.method == "top_n":
                # Sort by score
                sorted_group = group.sort_values('total_score', ascending=config.ascending)
                # Take top N
                selected = sorted_group.head(config.n)
                signals.append(selected)
                
            elif config.method == "percentile":
                # TODO: Implement percentile
                pass
                
        if not signals:
            return pd.DataFrame(columns=['trade_date', 'ts_code', 'total_score'])
            
        return pd.concat(signals)[['trade_date', 'ts_code', 'total_score']]
