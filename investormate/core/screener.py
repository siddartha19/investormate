"""
Screener class for InvestorMate.
Stock screening based on financial criteria.
"""

from typing import Dict, List, Optional, Tuple

from ..data.constants import MAJOR_US_TICKERS
from ..data.fetchers import get_yfinance_data
from ..utils.helpers import safe_divide


class Screener:
    """
    Stock screener for filtering stocks by criteria.
    
    Example:
        >>> screener = Screener()
        >>> value_stocks = screener.value_stocks(pe_max=15, pb_max=1.5)
    """
    
    def __init__(self, universe: Optional[List[str]] = None):
        """
        Initialize screener.
        
        Args:
            universe: List of tickers to screen (default: major US stocks)
        """
        if universe is None:
            # Default to major US stocks for v0.1.0
            self.universe = MAJOR_US_TICKERS[:50]  # Limit to 50 for performance
        else:
            self.universe = universe
    
    def value_stocks(self, pe_max: float = 15, pb_max: float = 1.5,
                    debt_to_equity_max: float = 0.5) -> List[str]:
        """
        Find value stocks based on valuation metrics.
        
        Args:
            pe_max: Maximum P/E ratio
            pb_max: Maximum P/B ratio
            debt_to_equity_max: Maximum debt-to-equity ratio
            
        Returns:
            List of ticker symbols matching criteria
        """
        def criteria(info: Dict) -> bool:
            pe = info.get('trailingPE') or info.get('forwardPE')
            pb = info.get('priceToBook')
            debt_to_equity = info.get('debtToEquity', 100)
            
            return (
                pe and pe > 0 and pe <= pe_max and
                pb and pb > 0 and pb <= pb_max and
                debt_to_equity <= debt_to_equity_max
            )
        
        return self._filter_by_criteria(criteria)
    
    def growth_stocks(self, revenue_growth_min: float = 20,
                     eps_growth_min: float = 15) -> List[str]:
        """
        Find growth stocks based on growth metrics.
        
        Args:
            revenue_growth_min: Minimum revenue growth % (YoY)
            eps_growth_min: Minimum EPS growth % (YoY)
            
        Returns:
            List of ticker symbols matching criteria
        """
        def criteria(info: Dict) -> bool:
            revenue_growth = (info.get('revenueGrowth') or 0) * 100
            eps_growth = (info.get('earningsQuarterlyGrowth') or 0) * 100
            
            return (
                revenue_growth >= revenue_growth_min and
                eps_growth >= eps_growth_min
            )
        
        return self._filter_by_criteria(criteria)
    
    def dividend_stocks(self, yield_min: float = 3.0,
                       payout_ratio_max: float = 60) -> List[str]:
        """
        Find dividend stocks.
        
        Args:
            yield_min: Minimum dividend yield %
            payout_ratio_max: Maximum payout ratio %
            
        Returns:
            List of ticker symbols matching criteria
        """
        def criteria(info: Dict) -> bool:
            dividend_yield = (info.get('dividendYield') or 0) * 100
            payout_ratio = (info.get('payoutRatio') or 0) * 100
            
            return (
                dividend_yield >= yield_min and
                payout_ratio > 0 and payout_ratio <= payout_ratio_max
            )
        
        return self._filter_by_criteria(criteria)
    
    def filter(self, **criteria) -> List[str]:
        """
        Custom screening with flexible criteria.
        
        Args:
            **criteria: Keyword arguments for filtering
                market_cap_min: Minimum market cap
                market_cap_max: Maximum market cap
                pe_ratio: Tuple of (min, max) for P/E ratio
                pb_ratio: Tuple of (min, max) for P/B ratio
                roe_min: Minimum ROE
                debt_to_equity_max: Maximum debt-to-equity
                sector: Sector name to filter by
                industry: Industry name to filter by
                
        Returns:
            List of ticker symbols matching criteria
        """
        def check_criteria(info: Dict) -> bool:
            # Market cap
            if 'market_cap_min' in criteria:
                market_cap = info.get('marketCap', 0)
                if market_cap < criteria['market_cap_min']:
                    return False
            
            if 'market_cap_max' in criteria:
                market_cap = info.get('marketCap', float('inf'))
                if market_cap > criteria['market_cap_max']:
                    return False
            
            # P/E ratio
            if 'pe_ratio' in criteria:
                pe = info.get('trailingPE') or info.get('forwardPE')
                if not pe:
                    return False
                min_pe, max_pe = criteria['pe_ratio']
                if not (min_pe <= pe <= max_pe):
                    return False
            
            # P/B ratio
            if 'pb_ratio' in criteria:
                pb = info.get('priceToBook')
                if not pb:
                    return False
                min_pb, max_pb = criteria['pb_ratio']
                if not (min_pb <= pb <= max_pb):
                    return False
            
            # ROE
            if 'roe_min' in criteria:
                roe = (info.get('returnOnEquity') or 0) * 100
                if roe < criteria['roe_min']:
                    return False
            
            # Debt to Equity
            if 'debt_to_equity_max' in criteria:
                debt_to_equity = info.get('debtToEquity', 100)
                if debt_to_equity > criteria['debt_to_equity_max']:
                    return False
            
            # Sector
            if 'sector' in criteria:
                sector = info.get('sector', '')
                if sector != criteria['sector']:
                    return False
            
            # Industry
            if 'industry' in criteria:
                industry = info.get('industry', '')
                if industry != criteria['industry']:
                    return False
            
            return True
        
        return self._filter_by_criteria(check_criteria)

    def magic_formula(
        self,
        top_n: int = 30,
        min_market_cap: float = 300_000_000,
    ) -> List[str]:
        """
        Joel Greenblatt Magic Formula screen: high ROIC + high earnings yield (EBIT/EV).

        Ranks all names in the universe by ROIC and by earnings yield separately
        (1 = best), then sorts by the sum of ranks (lowest = best).

        Args:
            top_n: Maximum number of tickers to return.
            min_market_cap: Exclude firms below this market cap (default $300M).

        Returns:
            List of tickers, best combined rank first.
        """
        candidates: List[Tuple[str, float, float]] = []

        for ticker in self.universe:
            try:
                info = get_yfinance_data(ticker)
                if not info:
                    continue
                mc = info.get("marketCap") or 0
                if mc < min_market_cap:
                    continue

                ebit = info.get("ebit")
                ev = info.get("enterpriseValue")
                if ebit is None or ev is None or ev <= 0 or ebit <= 0:
                    continue

                earnings_yield = ebit / ev

                total_assets = info.get("totalAssets")
                current_liab = info.get("totalCurrentLiabilities")
                if total_assets is None or current_liab is None:
                    continue
                invested_capital = total_assets - current_liab
                if invested_capital <= 0:
                    continue

                tax_rate = info.get("effectiveTaxRate")
                if tax_rate is None:
                    tax_rate = 0.21
                nopat = ebit * (1 - float(tax_rate))
                roic = safe_divide(nopat, invested_capital, default=None)
                if roic is None or roic <= 0:
                    continue

                candidates.append((ticker, float(roic), float(earnings_yield)))
            except Exception:
                continue

        if not candidates:
            return []

        tickers = [c[0] for c in candidates]
        roics = [c[1] for c in candidates]
        eys = [c[2] for c in candidates]

        # Rank 1 = best (highest)
        roic_order = sorted(range(len(roics)), key=lambda i: roics[i], reverse=True)
        ey_order = sorted(range(len(eys)), key=lambda i: eys[i], reverse=True)

        roic_rank = [0] * len(tickers)
        ey_rank = [0] * len(tickers)
        for rank, idx in enumerate(roic_order, start=1):
            roic_rank[idx] = rank
        for rank, idx in enumerate(ey_order, start=1):
            ey_rank[idx] = rank

        combined = [(tickers[i], roic_rank[i] + ey_rank[i]) for i in range(len(tickers))]
        combined.sort(key=lambda x: x[1])

        return [t for t, _ in combined[:top_n]]

    def _filter_by_criteria(self, criteria_func) -> List[str]:
        """
        Filter stocks by a criteria function.
        
        Args:
            criteria_func: Function that takes stock info dict and returns bool
            
        Returns:
            List of ticker symbols matching criteria
        """
        matching_tickers = []
        
        for ticker in self.universe:
            try:
                info = get_yfinance_data(ticker)
                if criteria_func(info):
                    matching_tickers.append(ticker)
            except Exception:
                # Skip stocks that error out
                continue
        
        return matching_tickers
