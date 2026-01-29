"""
Technical indicators wrapper for InvestorMate.
Uses pandas-ta for technical analysis.
"""

from typing import Optional, List, Union
import pandas as pd

try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False
    ta = None


class IndicatorsHelper:
    """Helper class for calculating technical indicators."""
    
    def __init__(self, price_data: pd.DataFrame):
        """
        Initialize indicators helper.
        
        Args:
            price_data: DataFrame with OHLCV data (Open, High, Low, Close, Volume)
        """
        if not HAS_PANDAS_TA:
            raise ImportError("pandas-ta is required for technical indicators. Install with: pip install pandas-ta")
        
        self.df = price_data.copy()
        
        # Ensure required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close']
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    
    # Moving Averages
    
    def sma(self, period: int = 20, column: str = 'Close') -> pd.Series:
        """Simple Moving Average."""
        return ta.sma(self.df[column], length=period)
    
    def ema(self, period: int = 12, column: str = 'Close') -> pd.Series:
        """Exponential Moving Average."""
        return ta.ema(self.df[column], length=period)
    
    def wma(self, period: int = 20, column: str = 'Close') -> pd.Series:
        """Weighted Moving Average."""
        return ta.wma(self.df[column], length=period)
    
    # Momentum Indicators
    
    def rsi(self, period: int = 14, column: str = 'Close') -> pd.Series:
        """Relative Strength Index."""
        return ta.rsi(self.df[column], length=period)
    
    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """MACD (Moving Average Convergence Divergence)."""
        return ta.macd(self.df['Close'], fast=fast, slow=slow, signal=signal)
    
    def stoch(self, k: int = 14, d: int = 3, smooth_k: int = 3) -> pd.DataFrame:
        """Stochastic Oscillator."""
        return ta.stoch(self.df['High'], self.df['Low'], self.df['Close'], 
                       k=k, d=d, smooth_k=smooth_k)
    
    def cci(self, period: int = 20) -> pd.Series:
        """Commodity Channel Index."""
        return ta.cci(self.df['High'], self.df['Low'], self.df['Close'], length=period)
    
    def williams_r(self, period: int = 14) -> pd.Series:
        """Williams %R."""
        return ta.willr(self.df['High'], self.df['Low'], self.df['Close'], length=period)
    
    def momentum(self, period: int = 10, column: str = 'Close') -> pd.Series:
        """Momentum."""
        return ta.mom(self.df[column], length=period)
    
    def roc(self, period: int = 10, column: str = 'Close') -> pd.Series:
        """Rate of Change."""
        return ta.roc(self.df[column], length=period)
    
    # Volatility Indicators
    
    def bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """Bollinger Bands."""
        return ta.bbands(self.df['Close'], length=period, std=std_dev)
    
    def atr(self, period: int = 14) -> pd.Series:
        """Average True Range."""
        return ta.atr(self.df['High'], self.df['Low'], self.df['Close'], length=period)
    
    def keltner_channels(self, period: int = 20, scalar: float = 2.0) -> pd.DataFrame:
        """Keltner Channels."""
        return ta.kc(self.df['High'], self.df['Low'], self.df['Close'], 
                    length=period, scalar=scalar)
    
    def donchian_channels(self, period: int = 20) -> pd.DataFrame:
        """Donchian Channels."""
        return ta.donchian(self.df['High'], self.df['Low'], upper_length=period, lower_length=period)
    
    # Volume Indicators
    
    def obv(self) -> pd.Series:
        """On-Balance Volume."""
        if 'Volume' not in self.df.columns:
            raise ValueError("Volume column required for OBV")
        return ta.obv(self.df['Close'], self.df['Volume'])
    
    def ad(self) -> pd.Series:
        """Accumulation/Distribution."""
        if 'Volume' not in self.df.columns:
            raise ValueError("Volume column required for A/D")
        return ta.ad(self.df['High'], self.df['Low'], self.df['Close'], self.df['Volume'])
    
    def adx(self, period: int = 14) -> pd.DataFrame:
        """Average Directional Index."""
        return ta.adx(self.df['High'], self.df['Low'], self.df['Close'], length=period)
    
    def vwap(self) -> pd.Series:
        """Volume Weighted Average Price."""
        if 'Volume' not in self.df.columns:
            raise ValueError("Volume column required for VWAP")
        return ta.vwap(self.df['High'], self.df['Low'], self.df['Close'], self.df['Volume'])
    
    # Trend Indicators
    
    def supertrend(self, period: int = 7, multiplier: float = 3.0) -> pd.DataFrame:
        """SuperTrend."""
        return ta.supertrend(self.df['High'], self.df['Low'], self.df['Close'], 
                            length=period, multiplier=multiplier)
    
    def ichimoku(self) -> pd.DataFrame:
        """Ichimoku Cloud."""
        return ta.ichimoku(self.df['High'], self.df['Low'], self.df['Close'])[0]
    
    # Utility Methods
    
    def add_indicators(self, indicators: List[str]) -> pd.DataFrame:
        """
        Add multiple indicators to the dataframe.
        
        Args:
            indicators: List of indicator names (e.g., ['sma_20', 'rsi_14', 'macd'])
            
        Returns:
            DataFrame with indicators added
        """
        df_with_indicators = self.df.copy()
        
        for indicator in indicators:
            # Parse indicator name and parameters
            parts = indicator.split('_')
            name = parts[0]
            period = int(parts[1]) if len(parts) > 1 else None
            
            if name == 'sma' and period:
                df_with_indicators[indicator] = self.sma(period)
            elif name == 'ema' and period:
                df_with_indicators[indicator] = self.ema(period)
            elif name == 'rsi':
                period = period or 14
                df_with_indicators[f'rsi_{period}'] = self.rsi(period)
            elif name == 'macd':
                macd_df = self.macd()
                for col in macd_df.columns:
                    df_with_indicators[col] = macd_df[col]
            elif name == 'bbands':
                period = period or 20
                bbands_df = self.bollinger_bands(period)
                for col in bbands_df.columns:
                    df_with_indicators[col] = bbands_df[col]
            elif name == 'atr':
                period = period or 14
                df_with_indicators[f'atr_{period}'] = self.atr(period)
            elif name == 'obv':
                df_with_indicators['obv'] = self.obv()
            elif name == 'volume' and 'sma' in indicator:
                # Special case for volume_sma
                period = period or 20
                if 'Volume' in df_with_indicators.columns:
                    df_with_indicators[f'volume_sma_{period}'] = self.sma(period, 'Volume')
        
        return df_with_indicators
    
    @staticmethod
    def available_indicators() -> List[str]:
        """
        Get list of available indicators.
        
        Returns:
            List of indicator names
        """
        return [
            'sma', 'ema', 'wma',  # Moving averages
            'rsi', 'macd', 'stoch', 'cci', 'williams_r', 'momentum', 'roc',  # Momentum
            'bollinger_bands', 'atr', 'keltner_channels', 'donchian_channels',  # Volatility
            'obv', 'ad', 'adx', 'vwap',  # Volume
            'supertrend', 'ichimoku'  # Trend
        ]
