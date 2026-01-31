"""
Backtest results with performance metrics.
"""

from typing import Dict, List
import pandas as pd
import numpy as np


class BacktestResults:
    """
    Backtest results with comprehensive performance metrics.
    
    Provides:
    - Return metrics (total return, CAGR)
    - Risk metrics (Sharpe ratio, max drawdown, volatility)
    - Trade statistics (win rate, avg win/loss)
    - Equity curve and trade log
    """
    
    def __init__(self, results_dict: Dict):
        """
        Initialize from backtest results dictionary.
        
        Args:
            results_dict: Results from BacktestEngine.run()
        """
        self._results = results_dict
        self._trades_df = None
        self._equity_df = None
        self._metrics = None
    
    @property
    def trades(self) -> pd.DataFrame:
        """Get trades as DataFrame."""
        if self._trades_df is None and self._results['trades']:
            self._trades_df = pd.DataFrame(self._results['trades'])
            if not self._trades_df.empty:
                self._trades_df.set_index('date', inplace=True)
        return self._trades_df
    
    @property
    def equity_curve(self) -> pd.DataFrame:
        """Get equity curve as DataFrame."""
        if self._equity_df is None:
            self._equity_df = pd.DataFrame(self._results['equity_history'])
            if not self._equity_df.empty:
                self._equity_df.set_index('date', inplace=True)
        return self._equity_df
    
    def _calculate_metrics(self) -> Dict:
        """Calculate all performance metrics."""
        if self._metrics is not None:
            return self._metrics
        
        equity_curve = self.equity_curve
        trades_df = self.trades
        
        initial_capital = self._results['initial_capital']
        final_equity = self._results['final_equity']
        
        # Basic return metrics
        total_return = ((final_equity - initial_capital) / initial_capital) * 100
        
        # Calculate daily returns
        returns = equity_curve['equity'].pct_change().dropna()
        
        # Time-based metrics
        days = len(equity_curve)
        years = days / 252  # Trading days
        
        cagr = 0.0
        if years > 0 and final_equity > 0:
            cagr = (((final_equity / initial_capital) ** (1 / years)) - 1) * 100
        
        # Risk metrics
        volatility = returns.std() * np.sqrt(252) * 100 if len(returns) > 1 else 0.0
        
        # Sharpe ratio (assuming 0% risk-free rate)
        sharpe_ratio = 0.0
        if volatility > 0 and len(returns) > 1:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
        
        # Max drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100 if len(drawdown) > 0 else 0.0
        
        # Trade statistics
        total_trades = 0
        winning_trades = 0
        losing_trades = 0
        total_pnl = 0.0
        total_wins = 0.0
        total_losses = 0.0
        
        if trades_df is not None and not trades_df.empty:
            sell_trades = trades_df[trades_df['type'] == 'SELL']
            total_trades = len(sell_trades)
            
            if total_trades > 0:
                for _, trade in sell_trades.iterrows():
                    pnl = trade.get('pnl', 0)
                    total_pnl += pnl
                    
                    if pnl > 0:
                        winning_trades += 1
                        total_wins += pnl
                    elif pnl < 0:
                        losing_trades += 1
                        total_losses += abs(pnl)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        avg_win = total_wins / winning_trades if winning_trades > 0 else 0.0
        avg_loss = total_losses / losing_trades if losing_trades > 0 else 0.0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0.0
        
        self._metrics = {
            'total_return': round(total_return, 2),
            'cagr': round(cagr, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'volatility': round(volatility, 2),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'initial_capital': initial_capital,
            'final_equity': round(final_equity, 2),
            'total_pnl': round(total_pnl, 2)
        }
        
        return self._metrics
    
    @property
    def total_return(self) -> float:
        """Total return percentage."""
        return self._calculate_metrics()['total_return']
    
    @property
    def cagr(self) -> float:
        """Compound Annual Growth Rate percentage."""
        return self._calculate_metrics()['cagr']
    
    @property
    def sharpe_ratio(self) -> float:
        """Sharpe ratio (risk-adjusted return)."""
        return self._calculate_metrics()['sharpe_ratio']
    
    @property
    def max_drawdown(self) -> float:
        """Maximum drawdown percentage."""
        return self._calculate_metrics()['max_drawdown']
    
    @property
    def volatility(self) -> float:
        """Annual volatility percentage."""
        return self._calculate_metrics()['volatility']
    
    @property
    def total_trades(self) -> int:
        """Total number of completed trades."""
        return self._calculate_metrics()['total_trades']
    
    @property
    def win_rate(self) -> float:
        """Winning trades percentage."""
        return self._calculate_metrics()['win_rate']
    
    @property
    def avg_win(self) -> float:
        """Average profit per winning trade."""
        return self._calculate_metrics()['avg_win']
    
    @property
    def avg_loss(self) -> float:
        """Average loss per losing trade."""
        return self._calculate_metrics()['avg_loss']
    
    @property
    def profit_factor(self) -> float:
        """Profit factor (total wins / total losses)."""
        return self._calculate_metrics()['profit_factor']
    
    def summary(self) -> str:
        """
        Get formatted summary of backtest results.
        
        Returns:
            Formatted string with key metrics
        """
        metrics = self._calculate_metrics()
        
        summary = f"""
Backtest Results Summary
{'=' * 60}

Performance Metrics:
  Total Return:        {metrics['total_return']:>10.2f}%
  CAGR:                {metrics['cagr']:>10.2f}%
  Sharpe Ratio:        {metrics['sharpe_ratio']:>10.2f}
  Max Drawdown:        {metrics['max_drawdown']:>10.2f}%
  Volatility:          {metrics['volatility']:>10.2f}%

Capital:
  Initial Capital:     ${metrics['initial_capital']:>10,.2f}
  Final Equity:        ${metrics['final_equity']:>10,.2f}
  Total P&L:           ${metrics['total_pnl']:>10,.2f}

Trade Statistics:
  Total Trades:        {metrics['total_trades']:>10}
  Winning Trades:      {metrics['winning_trades']:>10}
  Losing Trades:       {metrics['losing_trades']:>10}
  Win Rate:            {metrics['win_rate']:>10.2f}%
  Avg Win:             ${metrics['avg_win']:>10,.2f}
  Avg Loss:            ${metrics['avg_loss']:>10,.2f}
  Profit Factor:       {metrics['profit_factor']:>10.2f}

{'=' * 60}
"""
        return summary
    
    def __repr__(self) -> str:
        """String representation."""
        metrics = self._calculate_metrics()
        return (f"BacktestResults(return={metrics['total_return']:.2f}%, "
                f"sharpe={metrics['sharpe_ratio']:.2f}, "
                f"trades={metrics['total_trades']})")
