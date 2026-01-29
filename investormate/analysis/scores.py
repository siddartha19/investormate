"""
Financial scoring systems for InvestorMate.
Piotroski F-Score, Altman Z-Score, Beneish M-Score.
"""

from typing import Dict, Tuple, Optional
from ..utils.helpers import safe_divide


class FinancialScores:
    """Calculator for financial health scores."""
    
    def __init__(self, stock_info: Dict, balance_sheet: Optional[Dict] = None,
                 income_stmt: Optional[Dict] = None, cash_flow: Optional[Dict] = None):
        """
        Initialize financial scores calculator.
        
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
    
    def piotroski_score(self) -> Tuple[int, Dict[str, int]]:
        """
        Calculate Piotroski F-Score (0-9).
        
        A score of 8-9 indicates a very strong company.
        A score of 0-2 indicates a weak company.
        
        Returns:
            Tuple of (total_score, breakdown_dict)
        """
        breakdown = {}
        
        # Profitability (4 points)
        # 1. Positive net income
        net_income = self.info.get('netIncomeToCommon', 0)
        breakdown['net_income'] = 1 if net_income > 0 else 0
        
        # 2. Positive ROA
        roa = self.info.get('returnOnAssets', 0)
        breakdown['roa'] = 1 if roa and roa > 0 else 0
        
        # 3. Positive operating cash flow
        operating_cf = self.info.get('operatingCashflow', 0)
        breakdown['operating_cf'] = 1 if operating_cf and operating_cf > 0 else 0
        
        # 4. Cash flow from operations > net income (quality of earnings)
        breakdown['cf_quality'] = 1 if operating_cf and net_income and operating_cf > net_income else 0
        
        # Leverage, Liquidity & Source of Funds (3 points)
        # 5. Lower long-term debt ratio this year
        # (simplified: check if debt-to-equity is reasonable)
        debt_to_equity = self.info.get('debtToEquity', 100)
        breakdown['debt'] = 1 if debt_to_equity and debt_to_equity < 80 else 0
        
        # 6. Higher current ratio this year
        current_ratio = self.info.get('currentRatio', 0)
        breakdown['current_ratio'] = 1 if current_ratio and current_ratio > 1.0 else 0
        
        # 7. No new shares issued
        # (simplified: assume yes if shares outstanding is stable)
        breakdown['no_dilution'] = 1  # Default to 1, hard to calculate from single point
        
        # Operating Efficiency (2 points)
        # 8. Higher gross margin this year
        gross_margin = self.info.get('grossMargins', 0)
        breakdown['gross_margin'] = 1 if gross_margin and gross_margin > 0.20 else 0
        
        # 9. Higher asset turnover this year
        revenue = self.info.get('totalRevenue', 0)
        total_assets = self.info.get('totalAssets', 1)
        asset_turnover = safe_divide(revenue, total_assets, 0)
        breakdown['asset_turnover'] = 1 if asset_turnover and asset_turnover > 0.5 else 0
        
        total_score = sum(breakdown.values())
        return total_score, breakdown
    
    def altman_z_score(self) -> Tuple[Optional[float], str]:
        """
        Calculate Altman Z-Score (bankruptcy prediction).
        
        Z > 2.99: Safe zone (low bankruptcy risk)
        1.81 < Z < 2.99: Grey zone
        Z < 1.81: Distress zone (high bankruptcy risk)
        
        Returns:
            Tuple of (z_score, interpretation)
        """
        # Get financial data
        total_assets = self.info.get('totalAssets')
        total_liabilities = self.info.get('totalLiabilities')
        total_equity = self.info.get('totalStockholderEquity')
        current_assets = self.info.get('totalCurrentAssets')
        current_liabilities = self.info.get('totalCurrentLiabilities')
        retained_earnings = self.info.get('retainedEarnings')
        ebit = self.info.get('ebit')
        revenue = self.info.get('totalRevenue')
        market_cap = self.info.get('marketCap')
        
        # Check if we have enough data
        if not all([total_assets, total_liabilities, current_assets, current_liabilities]):
            return None, "Insufficient data for Z-Score calculation"
        
        # Calculate working capital
        working_capital = (current_assets or 0) - (current_liabilities or 0)
        
        # Calculate components
        # X1 = Working Capital / Total Assets
        x1 = safe_divide(working_capital, total_assets, 0) * 1.2
        
        # X2 = Retained Earnings / Total Assets
        x2 = safe_divide(retained_earnings or 0, total_assets, 0) * 1.4
        
        # X3 = EBIT / Total Assets
        x3 = safe_divide(ebit or 0, total_assets, 0) * 3.3
        
        # X4 = Market Cap / Total Liabilities
        x4 = safe_divide(market_cap or 0, total_liabilities, 0) * 0.6
        
        # X5 = Revenue / Total Assets
        x5 = safe_divide(revenue or 0, total_assets, 0) * 1.0
        
        # Calculate Z-Score
        z_score = x1 + x2 + x3 + x4 + x5
        
        # Interpret
        if z_score > 2.99:
            interpretation = "Safe Zone - Low bankruptcy risk"
        elif z_score > 1.81:
            interpretation = "Grey Zone - Moderate risk"
        else:
            interpretation = "Distress Zone - High bankruptcy risk"
        
        return z_score, interpretation
    
    def beneish_m_score(self) -> Tuple[Optional[float], str]:
        """
        Calculate Beneish M-Score (earnings manipulation detection).
        
        M-Score < -2.22: Unlikely to be manipulating earnings
        M-Score > -2.22: Possible earnings manipulation
        
        Returns:
            Tuple of (m_score, interpretation)
        """
        # This is a simplified version as full calculation requires historical data
        # We'll use available ratios as proxies
        
        current_ratio = self.info.get('currentRatio', 1)
        debt_to_equity = self.info.get('debtToEquity', 0)
        gross_margin = self.info.get('grossMargins', 0)
        asset_turnover = safe_divide(
            self.info.get('totalRevenue', 0),
            self.info.get('totalAssets', 1),
            0
        )
        
        # Simplified scoring (not exact Beneish formula)
        # Lower is better
        risk_score = 0
        
        # High leverage is a red flag
        if debt_to_equity and debt_to_equity > 100:
            risk_score += 1
        
        # Declining margins
        if gross_margin and gross_margin < 0.15:
            risk_score += 1
        
        # Poor asset efficiency
        if asset_turnover < 0.5:
            risk_score += 1
        
        # Convert to approximate M-Score scale
        m_score = -3.0 + (risk_score * 0.5)
        
        if m_score < -2.22:
            interpretation = "Low risk of earnings manipulation"
        else:
            interpretation = "Potential earnings manipulation - investigate further"
        
        return m_score, interpretation
    
    def all_scores(self) -> Dict:
        """
        Get all financial scores.
        
        Returns:
            Dictionary with all scores
        """
        piotroski, piotroski_breakdown = self.piotroski_score()
        altman, altman_interp = self.altman_z_score()
        beneish, beneish_interp = self.beneish_m_score()
        
        return {
            'piotroski': {
                'score': piotroski,
                'max': 9,
                'breakdown': piotroski_breakdown,
                'interpretation': self._interpret_piotroski(piotroski)
            },
            'altman_z': {
                'score': altman,
                'interpretation': altman_interp
            },
            'beneish_m': {
                'score': beneish,
                'interpretation': beneish_interp
            }
        }
    
    @staticmethod
    def _interpret_piotroski(score: int) -> str:
        """Interpret Piotroski F-Score."""
        if score >= 8:
            return "Very Strong - Excellent financial health"
        elif score >= 6:
            return "Strong - Good financial health"
        elif score >= 4:
            return "Moderate - Average financial health"
        elif score >= 2:
            return "Weak - Below average financial health"
        else:
            return "Very Weak - Poor financial health"
