"""
Market class for InvestorMate.
Market summaries and indices data.
"""

from typing import Dict

from ..data.fetchers import (
    get_yfinance_market_summary_us,
    get_yfinance_market_summary_asia,
    get_yfinance_market_summary_europe,
    get_yfinance_market_summary_crypto,
    get_yfinance_market_summary_currency,
    get_yfinance_market_summary_commodities,
)
from ..utils.exceptions import DataFetchError


class Market:
    """
    Market data and summaries.
    
    Example:
        >>> market = Market("US")
        >>> print(market.summary)
        
        >>> crypto = Market("CRYPTO")
        >>> print(crypto.summary)
    """
    
    SUPPORTED_MARKETS = ["US", "ASIA", "EUROPE", "CRYPTO", "CURRENCIES", "COMMODITIES"]
    
    def __init__(self, market: str):
        """
        Initialize market.
        
        Args:
            market: Market name ("US", "ASIA", "EUROPE", "CRYPTO", "CURRENCIES", "COMMODITIES")
        """
        market = market.upper()
        if market not in self.SUPPORTED_MARKETS:
            raise ValueError(
                f"Unsupported market: {market}. "
                f"Supported markets: {', '.join(self.SUPPORTED_MARKETS)}"
            )
        
        self.market = market
        self._summary_cache = None
    
    @property
    def summary(self) -> Dict:
        """Get market summary data."""
        if self._summary_cache is not None:
            return self._summary_cache
        
        try:
            if self.market == "US":
                data = get_yfinance_market_summary_us()
            elif self.market == "ASIA":
                data = get_yfinance_market_summary_asia()
            elif self.market == "EUROPE":
                data = get_yfinance_market_summary_europe()
            elif self.market == "CRYPTO":
                data = get_yfinance_market_summary_crypto()
            elif self.market == "CURRENCIES":
                data = get_yfinance_market_summary_currency()
            elif self.market == "COMMODITIES":
                data = get_yfinance_market_summary_commodities()
            else:
                raise ValueError(f"Unknown market: {self.market}")
            
            self._summary_cache = data
            return data
            
        except Exception as e:
            raise DataFetchError(f"Failed to fetch market summary: {str(e)}")
    
    def refresh(self):
        """Clear cached data to force refresh."""
        self._summary_cache = None
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Market(market='{self.market}')"
