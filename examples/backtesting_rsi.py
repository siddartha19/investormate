"""
Example: Simple RSI Backtesting Strategy

This example demonstrates how to backtest a basic RSI trading strategy:
- Buy when RSI < 30 (oversold)
- Sell when RSI > 70 (overbought)
"""

from investormate import Backtest, Strategy


class RSIStrategy(Strategy):
    """
    Simple RSI mean-reversion strategy.
    
    Buy signals: RSI falls below 30 (oversold)
    Sell signals: RSI rises above 70 (overbought)
    """
    
    def initialize(self):
        """Initialize strategy parameters."""
        self.rsi_period = 14
        self.buy_threshold = 30
        self.sell_threshold = 70
        print(f"RSI Strategy initialized:")
        print(f"  RSI Period: {self.rsi_period}")
        print(f"  Buy when RSI < {self.buy_threshold}")
        print(f"  Sell when RSI > {self.sell_threshold}")
    
    def on_data(self, data):
        """
        Called for each bar of historical data.
        
        Args:
            data: Stock object with historical data
        """
        try:
            # Calculate RSI
            rsi_series = data.indicators.rsi(length=self.rsi_period)
            
            if rsi_series is None or len(rsi_series) == 0:
                return
            
            current_rsi = rsi_series.iloc[-1]
            
            # Trading logic
            if current_rsi < self.buy_threshold and not self.has_position:
                # Oversold - buy signal
                self.buy(percent=1.0)  # Use 100% of available cash
            
            elif current_rsi > self.sell_threshold and self.has_position:
                # Overbought - sell signal
                self.sell_all()
        
        except Exception as e:
            # Silently skip if indicators can't be calculated
            pass


def run_simple_backtest():
    """Run a simple backtest."""
    print("=" * 70)
    print("RSI STRATEGY BACKTEST")
    print("=" * 70)
    print()
    
    # Create backtest
    bt = Backtest(
        strategy=RSIStrategy,
        ticker="AAPL",
        start_date="2022-01-01",
        end_date="2024-01-01",
        initial_capital=10000,
        commission=0.001  # 0.1% commission per trade
    )
    
    print("Running backtest...")
    print()
    
    # Run backtest
    results = bt.run()
    
    # Print results
    print(results.summary())
    
    # Show some trades
    if results.trades is not None and not results.trades.empty:
        print("\nFirst 5 Trades:")
        print("-" * 70)
        print(results.trades.head())
    
    # Show equity curve sample
    if results.equity_curve is not None and not results.equity_curve.empty:
        print("\nEquity Curve (first 5 days):")
        print("-" * 70)
        print(results.equity_curve.head())


def run_comparison():
    """Compare different RSI parameters."""
    print("\n" + "=" * 70)
    print("RSI PARAMETER COMPARISON")
    print("=" * 70)
    print()
    
    parameters = [
        (20, 80),  # More conservative
        (30, 70),  # Standard
        (40, 60),  # More aggressive
    ]
    
    print(f"{'Parameters':<20} {'Total Return':>15} {'Sharpe':>10} {'Max DD':>10} {'Trades':>10}")
    print("-" * 70)
    
    for buy_thresh, sell_thresh in parameters:
        # Create custom strategy with these parameters
        class CustomRSI(Strategy):
            def initialize(self):
                self.rsi_period = 14
                self.buy_threshold = buy_thresh
                self.sell_threshold = sell_thresh
            
            def on_data(self, data):
                try:
                    rsi_series = data.indicators.rsi(length=self.rsi_period)
                    if rsi_series is None or len(rsi_series) == 0:
                        return
                    current_rsi = rsi_series.iloc[-1]
                    
                    if current_rsi < self.buy_threshold and not self.has_position:
                        self.buy(percent=1.0)
                    elif current_rsi > self.sell_threshold and self.has_position:
                        self.sell_all()
                except:
                    pass
        
        bt = Backtest(
            strategy=CustomRSI,
            ticker="AAPL",
            start_date="2022-01-01",
            end_date="2024-01-01",
            initial_capital=10000
        )
        
        results = bt.run()
        
        print(f"RSI({buy_thresh}/{sell_thresh})  {results.total_return:>14.2f}% "
              f"{results.sharpe_ratio:>10.2f} {results.max_drawdown:>9.2f}% "
              f"{results.total_trades:>10}")


def main():
    """Run all examples."""
    try:
        run_simple_backtest()
        run_comparison()
        
        print("\n" + "=" * 70)
        print("Backtest completed successfully!")
        print("=" * 70)
        print("\nKey Insights:")
        print("  1. RSI strategies work best in range-bound markets")
        print("  2. Parameter selection significantly affects performance")
        print("  3. Consider combining RSI with other indicators")
        print("  4. Always test on out-of-sample data")
        print()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have internet connection for historical data.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
