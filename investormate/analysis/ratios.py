"""
Financial ratios calculator for InvestorMate.
Auto-calculates various financial ratios from stock data.
"""

from typing import Dict, Optional
from ..utils.helpers import safe_divide


class RatiosCalculator:
    """Calculator for financial ratios."""
    
    def __init__(self, stock_info: Dict, balance_sheet: Optional[Dict] = None,
                 income_stmt: Optional[Dict] = None, cash_flow: Optional[Dict] = None):
        """
        Initialize ratios calculator.
        
        Args:
            stock_info: Stock info dictionary from yfinance
            balance_sheet: Balance sheet data (optional)
            income_stmt: Income statement data (optional)
            cash_flow: Cash flow data (optional)
        """
        self.info = stock_info
        self.balance_sheet = balance_sheet or {}
        self.income_stmt = income_stmt or {}
        self.cash_flow = cash_flow or {}
    
    # Valuation Ratios
    
    @property
    def pe(self) -> Optional[float]:
        """P/E Ratio (Price-to-Earnings)."""
        return self.info.get('trailingPE') or self.info.get('forwardPE')
    
    @property
    def peg(self) -> Optional[float]:
        """PEG Ratio (P/E to Growth)."""
        return self.info.get('pegRatio')
    
    @property
    def pb(self) -> Optional[float]:
        """P/B Ratio (Price-to-Book)."""
        return self.info.get('priceToBook')
    
    @property
    def ps(self) -> Optional[float]:
        """P/S Ratio (Price-to-Sales)."""
        return self.info.get('priceToSalesTrailing12Months')
    
    @property
    def ev_ebitda(self) -> Optional[float]:
        """EV/EBITDA Ratio."""
        return self.info.get('enterpriseToEbitda')
    
    @property
    def ev_revenue(self) -> Optional[float]:
        """EV/Revenue Ratio."""
        return self.info.get('enterpriseToRevenue')
    
    # Profitability Ratios
    
    @property
    def roe(self) -> Optional[float]:
        """ROE (Return on Equity)."""
        return self.info.get('returnOnEquity')
    
    @property
    def roa(self) -> Optional[float]:
        """ROA (Return on Assets)."""
        return self.info.get('returnOnAssets')
    
    @property
    def profit_margin(self) -> Optional[float]:
        """Net Profit Margin."""
        return self.info.get('profitMargins')
    
    @property
    def operating_margin(self) -> Optional[float]:
        """Operating Margin."""
        return self.info.get('operatingMargins')
    
    @property
    def gross_margin(self) -> Optional[float]:
        """Gross Margin."""
        return self.info.get('grossMargins')
    
    @property
    def ebitda_margin(self) -> Optional[float]:
        """EBITDA Margin."""
        ebitda = self.info.get('ebitda')
        revenue = self.info.get('totalRevenue')
        return safe_divide(ebitda, revenue)
    
    # Liquidity Ratios
    
    @property
    def current_ratio(self) -> Optional[float]:
        """Current Ratio."""
        return self.info.get('currentRatio')
    
    @property
    def quick_ratio(self) -> Optional[float]:
        """Quick Ratio."""
        return self.info.get('quickRatio')
    
    @property
    def cash_ratio(self) -> Optional[float]:
        """Cash Ratio."""
        cash = self.info.get('totalCash')
        current_liabilities = self.info.get('totalCurrentLiabilities')
        return safe_divide(cash, current_liabilities)
    
    # Leverage Ratios
    
    @property
    def debt_to_equity(self) -> Optional[float]:
        """Debt-to-Equity Ratio."""
        return self.info.get('debtToEquity')
    
    @property
    def debt_to_assets(self) -> Optional[float]:
        """Debt-to-Assets Ratio."""
        total_debt = self.info.get('totalDebt')
        total_assets = self.info.get('totalAssets')
        return safe_divide(total_debt, total_assets)
    
    @property
    def equity_ratio(self) -> Optional[float]:
        """Equity Ratio."""
        equity = self.info.get('totalStockholderEquity')
        total_assets = self.info.get('totalAssets')
        return safe_divide(equity, total_assets)
    
    @property
    def interest_coverage(self) -> Optional[float]:
        """Interest Coverage Ratio."""
        ebit = self.info.get('ebit')
        interest_expense = self.info.get('interestExpense')
        return safe_divide(ebit, interest_expense)
    
    # Efficiency Ratios
    
    @property
    def asset_turnover(self) -> Optional[float]:
        """Asset Turnover Ratio."""
        revenue = self.info.get('totalRevenue')
        total_assets = self.info.get('totalAssets')
        return safe_divide(revenue, total_assets)
    
    @property
    def inventory_turnover(self) -> Optional[float]:
        """Inventory Turnover Ratio."""
        cogs = self.info.get('costOfRevenue')
        inventory = self.info.get('inventory')
        return safe_divide(cogs, inventory)
    
    @property
    def receivables_turnover(self) -> Optional[float]:
        """Receivables Turnover Ratio."""
        revenue = self.info.get('totalRevenue')
        receivables = self.info.get('accountsReceivable')
        return safe_divide(revenue, receivables)
    
    # Growth Ratios
    
    @property
    def revenue_growth(self) -> Optional[float]:
        """Revenue Growth (YoY)."""
        return self.info.get('revenueGrowth')
    
    @property
    def earnings_growth(self) -> Optional[float]:
        """Earnings Growth (YoY)."""
        return self.info.get('earningsGrowth')
    
    @property
    def eps_growth(self) -> Optional[float]:
        """EPS Growth."""
        return self.info.get('earningsQuarterlyGrowth')
    
    # Dividend Ratios
    
    @property
    def dividend_yield(self) -> Optional[float]:
        """Dividend Yield."""
        return self.info.get('dividendYield')
    
    @property
    def payout_ratio(self) -> Optional[float]:
        """Payout Ratio."""
        return self.info.get('payoutRatio')
    
    # Utility Methods
    
    def all(self) -> Dict[str, Optional[float]]:
        """
        Get all ratios as a dictionary.
        
        Returns:
            Dictionary of ratio name -> value
        """
        return {
            # Valuation
            'pe': self.pe,
            'peg': self.peg,
            'pb': self.pb,
            'ps': self.ps,
            'ev_ebitda': self.ev_ebitda,
            'ev_revenue': self.ev_revenue,
            
            # Profitability
            'roe': self.roe,
            'roa': self.roa,
            'profit_margin': self.profit_margin,
            'operating_margin': self.operating_margin,
            'gross_margin': self.gross_margin,
            'ebitda_margin': self.ebitda_margin,
            
            # Liquidity
            'current_ratio': self.current_ratio,
            'quick_ratio': self.quick_ratio,
            'cash_ratio': self.cash_ratio,
            
            # Leverage
            'debt_to_equity': self.debt_to_equity,
            'debt_to_assets': self.debt_to_assets,
            'equity_ratio': self.equity_ratio,
            'interest_coverage': self.interest_coverage,
            
            # Efficiency
            'asset_turnover': self.asset_turnover,
            'inventory_turnover': self.inventory_turnover,
            'receivables_turnover': self.receivables_turnover,
            
            # Growth
            'revenue_growth': self.revenue_growth,
            'earnings_growth': self.earnings_growth,
            'eps_growth': self.eps_growth,
            
            # Dividend
            'dividend_yield': self.dividend_yield,
            'payout_ratio': self.payout_ratio,
        }
    
    def valuation_ratios(self) -> Dict[str, Optional[float]]:
        """Get valuation ratios only."""
        return {
            'pe': self.pe,
            'peg': self.peg,
            'pb': self.pb,
            'ps': self.ps,
            'ev_ebitda': self.ev_ebitda,
            'ev_revenue': self.ev_revenue,
        }
    
    def profitability_ratios(self) -> Dict[str, Optional[float]]:
        """Get profitability ratios only."""
        return {
            'roe': self.roe,
            'roa': self.roa,
            'profit_margin': self.profit_margin,
            'operating_margin': self.operating_margin,
            'gross_margin': self.gross_margin,
            'ebitda_margin': self.ebitda_margin,
        }
    
    def liquidity_ratios(self) -> Dict[str, Optional[float]]:
        """Get liquidity ratios only."""
        return {
            'current_ratio': self.current_ratio,
            'quick_ratio': self.quick_ratio,
            'cash_ratio': self.cash_ratio,
        }
    
    def leverage_ratios(self) -> Dict[str, Optional[float]]:
        """Get leverage ratios only."""
        return {
            'debt_to_equity': self.debt_to_equity,
            'debt_to_assets': self.debt_to_assets,
            'equity_ratio': self.equity_ratio,
            'interest_coverage': self.interest_coverage,
        }
