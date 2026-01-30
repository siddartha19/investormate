"""
Example: Advanced Financial Ratios and TTM Metrics

This example demonstrates the new advanced financial ratios and
Trailing Twelve Months (TTM) metrics added to InvestorMate.
"""

from investormate import Stock
from investormate.utils import print_ratios_table, format_percentage, format_number

def main():
    # Initialize stock
    ticker = "AAPL"
    print(f"\n{'='*80}")
    print(f"Advanced Financial Ratios Analysis for {ticker}")
    print(f"{'='*80}\n")
    
    stock = Stock(ticker)
    
    # 1. TTM (Trailing Twelve Months) Metrics
    print("\n1. TTM (Trailing Twelve Months) Metrics")
    print("-" * 80)
    
    ttm_metrics = stock.ratios.ttm_metrics()
    for metric, value in ttm_metrics.items():
        display_name = metric.replace('_', ' ').upper()
        if value is not None:
            if 'eps' in metric.lower() or 'pe' in metric.lower():
                formatted = format_number(value, decimals=2)
            else:
                formatted = format_number(value, decimals=0)
            print(f"{display_name.ljust(25)}: {formatted.rjust(20)}")
        else:
            print(f"{display_name.ljust(25)}: {'N/A'.rjust(20)}")
    
    # 2. Advanced Profitability Ratios
    print("\n\n2. Advanced Profitability Ratios")
    print("-" * 80)
    
    print(f"{'ROIC (Return on Invested Capital)'.ljust(40)}: {format_percentage(stock.ratios.roic).rjust(15)}")
    print(f"{'ROE (Return on Equity)'.ljust(40)}: {format_percentage(stock.ratios.roe).rjust(15)}")
    print(f"{'ROA (Return on Assets)'.ljust(40)}: {format_percentage(stock.ratios.roa).rjust(15)}")
    
    # 3. Capital Structure Metrics
    print("\n\n3. Capital Structure Metrics")
    print("-" * 80)
    
    print(f"{'WACC (Weighted Avg Cost of Capital)'.ljust(40)}: {format_percentage(stock.ratios.wacc).rjust(15)}")
    print(f"{'Equity Multiplier (Financial Leverage)'.ljust(40)}: {format_number(stock.ratios.equity_multiplier, decimals=2).rjust(15)}")
    print(f"{'Debt to Equity'.ljust(40)}: {format_number(stock.ratios.debt_to_equity, decimals=2).rjust(15)}")
    print(f"{'Debt to Assets'.ljust(40)}: {format_percentage(stock.ratios.debt_to_assets).rjust(15)}")
    
    # 4. DuPont Analysis
    print("\n\n4. DuPont Analysis (ROE Breakdown)")
    print("-" * 80)
    
    dupont = stock.ratios.dupont_roe
    if dupont:
        print("\nROE = Profit Margin × Asset Turnover × Equity Multiplier\n")
        print(f"{'Reported ROE'.ljust(30)}: {format_percentage(dupont.get('roe')).rjust(15)}")
        print(f"{'Profit Margin'.ljust(30)}: {format_percentage(dupont.get('profit_margin')).rjust(15)}")
        print(f"{'Asset Turnover'.ljust(30)}: {format_number(dupont.get('asset_turnover'), decimals=3).rjust(15)}")
        print(f"{'Equity Multiplier'.ljust(30)}: {format_number(dupont.get('equity_multiplier'), decimals=2).rjust(15)}")
        print(f"{'Calculated ROE'.ljust(30)}: {format_percentage(dupont.get('calculated_roe')).rjust(15)}")
    
    # 5. Complete Ratios Summary
    print("\n\n5. Complete Financial Ratios Summary")
    print("=" * 80)
    
    all_ratios = stock.ratios.all()
    print_ratios_table(all_ratios, title=f"{ticker} - Complete Financial Ratios")
    
    # 6. Compare Multiple Stocks
    print("\n\n6. Multi-Stock Comparison")
    print("=" * 80)
    
    tickers = ["AAPL", "MSFT", "GOOGL"]
    print(f"\nComparing: {', '.join(tickers)}\n")
    
    # Create comparison table
    metrics_to_compare = ['roic', 'roe', 'wacc', 'equity_multiplier', 'ttm_pe']
    
    print(f"{'Metric'.ljust(30)}", end='')
    for t in tickers:
        print(f"{t.rjust(15)}", end='')
    print()
    print("-" * (30 + 15 * len(tickers)))
    
    for metric in metrics_to_compare:
        display_name = metric.replace('_', ' ').upper()
        print(f"{display_name.ljust(30)}", end='')
        
        for t in tickers:
            try:
                s = Stock(t)
                value = getattr(s.ratios, metric, None)
                
                if value is not None:
                    if metric in ['roic', 'roe', 'wacc']:
                        formatted = format_percentage(value)
                    else:
                        formatted = format_number(value, decimals=2)
                else:
                    formatted = "N/A"
                
                print(f"{formatted.rjust(15)}", end='')
            except Exception as e:
                print(f"{'Error'.rjust(15)}", end='')
        
        print()
    
    print("\n" + "=" * 80)
    print("Analysis Complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
