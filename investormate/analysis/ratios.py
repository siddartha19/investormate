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
    
    # TTM (Trailing Twelve Months) Metrics
    
    @property
    def ttm_eps(self) -> Optional[float]:
        """TTM EPS (Trailing Twelve Months Earnings Per Share)."""
        return self.info.get('trailingEps')
    
    @property
    def ttm_pe(self) -> Optional[float]:
        """TTM P/E Ratio (Trailing Twelve Months)."""
        return self.info.get('trailingPE')
    
    @property
    def ttm_revenue(self) -> Optional[float]:
        """TTM Revenue (Trailing Twelve Months)."""
        # Calculate from quarterly income statements if available
        if self.income_stmt:
            try:
                # Get last 4 quarters of revenue
                revenues = []
                for date_key in sorted(self.income_stmt.keys(), reverse=True)[:4]:
                    quarter_data = self.income_stmt[date_key]
                    revenue = quarter_data.get('Total Revenue') or quarter_data.get('TotalRevenue')
                    if revenue:
                        revenues.append(revenue)
                
                if len(revenues) == 4:
                    return sum(revenues)
            except (KeyError, TypeError):
                pass
        
        # Fallback to info
        return self.info.get('totalRevenue')
    
    @property
    def ttm_net_income(self) -> Optional[float]:
        """TTM Net Income (Trailing Twelve Months)."""
        # Calculate from quarterly income statements if available
        if self.income_stmt:
            try:
                # Get last 4 quarters of net income
                net_incomes = []
                for date_key in sorted(self.income_stmt.keys(), reverse=True)[:4]:
                    quarter_data = self.income_stmt[date_key]
                    net_income = quarter_data.get('Net Income') or quarter_data.get('NetIncome')
                    if net_income:
                        net_incomes.append(net_income)
                
                if len(net_incomes) == 4:
                    return sum(net_incomes)
            except (KeyError, TypeError):
                pass
        
        # Fallback to info
        return self.info.get('netIncomeToCommon')
    
    @property
    def ttm_ebitda(self) -> Optional[float]:
        """TTM EBITDA (Trailing Twelve Months)."""
        return self.info.get('ebitda')
    
    # Advanced Profitability Ratios
    
    @property
    def roic(self) -> Optional[float]:
        """
        ROIC (Return on Invested Capital).
        Formula: NOPAT / Invested Capital
        where Invested Capital = Total Assets - Current Liabilities
        """
        # Get NOPAT (Net Operating Profit After Tax)
        ebit = self.info.get('ebit')
        tax_rate = self.info.get('effectiveTaxRate')
        
        if not ebit or tax_rate is None:
            return None
        
        nopat = ebit * (1 - tax_rate)
        
        # Get Invested Capital
        total_assets = self.info.get('totalAssets')
        current_liabilities = self.info.get('totalCurrentLiabilities')
        
        if not total_assets or not current_liabilities:
            return None
        
        invested_capital = total_assets - current_liabilities
        
        return safe_divide(nopat, invested_capital)
    
    @property
    def wacc(self) -> Optional[float]:
        """
        WACC (Weighted Average Cost of Capital).
        Simplified approximation using available data.
        Formula: (E/V * Re) + (D/V * Rd * (1-Tc))
        """
        # This is a simplified calculation
        # Market cap (equity value)
        market_cap = self.info.get('marketCap')
        # Total debt
        total_debt = self.info.get('totalDebt')
        # Cost of equity (using dividend discount model approximation)
        dividend_yield = self.info.get('dividendYield') or 0
        growth_rate = self.info.get('earningsGrowth') or 0
        cost_of_equity = dividend_yield + growth_rate
        
        # Cost of debt
        interest_expense = self.info.get('interestExpense')
        rd = safe_divide(abs(interest_expense) if interest_expense else 0, total_debt)
        
        # Tax rate
        tax_rate = self.info.get('effectiveTaxRate') or 0
        
        if not market_cap or not total_debt or not rd:
            return None
        
        # Total value
        total_value = market_cap + total_debt
        
        # WACC calculation
        equity_weight = market_cap / total_value
        debt_weight = total_debt / total_value
        
        wacc = (equity_weight * cost_of_equity) + (debt_weight * rd * (1 - tax_rate))
        
        return wacc if wacc > 0 else None
    
    @property
    def equity_multiplier(self) -> Optional[float]:
        """
        Equity Multiplier (Financial Leverage).
        Formula: Total Assets / Total Equity
        Higher values indicate more leverage.
        """
        total_assets = self.info.get('totalAssets')
        equity = self.info.get('totalStockholderEquity')
        
        return safe_divide(total_assets, equity)
    
    @property
    def dupont_roe(self) -> Optional[Dict[str, Optional[float]]]:
        """
        DuPont Analysis breakdown of ROE.
        ROE = Profit Margin × Asset Turnover × Equity Multiplier
        """
        return {
            'roe': self.roe,
            'profit_margin': self.profit_margin,
            'asset_turnover': self.asset_turnover,
            'equity_multiplier': self.equity_multiplier,
            'calculated_roe': safe_divide(
                (self.profit_margin or 0) * (self.asset_turnover or 0) * (self.equity_multiplier or 0),
                1
            ) if all([self.profit_margin, self.asset_turnover, self.equity_multiplier]) else None
        }
    
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
            'roic': self.roic,
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
            'equity_multiplier': self.equity_multiplier,
            'interest_coverage': self.interest_coverage,
            'wacc': self.wacc,
            
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
            
            # TTM Metrics
            'ttm_eps': self.ttm_eps,
            'ttm_pe': self.ttm_pe,
            'ttm_revenue': self.ttm_revenue,
            'ttm_net_income': self.ttm_net_income,
            'ttm_ebitda': self.ttm_ebitda,
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
            'roic': self.roic,
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
            'equity_multiplier': self.equity_multiplier,
            'interest_coverage': self.interest_coverage,
            'wacc': self.wacc,
        }
    
    def ttm_metrics(self) -> Dict[str, Optional[float]]:
        """Get TTM (Trailing Twelve Months) metrics only."""
        return {
            'ttm_eps': self.ttm_eps,
            'ttm_pe': self.ttm_pe,
            'ttm_revenue': self.ttm_revenue,
            'ttm_net_income': self.ttm_net_income,
            'ttm_ebitda': self.ttm_ebitda,
        }
