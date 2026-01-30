"""
Formatting utilities for InvestorMate.
Pretty printing for financial data, tables, and reports.
"""

from typing import Dict, Any, Optional, List
import pandas as pd


def format_number(value: Any, decimals: int = 2, prefix: str = "", suffix: str = "") -> str:
    """
    Format a number for display.
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        prefix: Prefix string (e.g., "$")
        suffix: Suffix string (e.g., "%")
        
    Returns:
        Formatted string
    """
    if value is None:
        return "N/A"
    
    # Handle pandas NA/NaN
    try:
        if pd.isna(value):
            return "N/A"
    except (TypeError, ValueError):
        pass
    
    try:
        num_value = float(value)
        formatted = f"{num_value:,.{decimals}f}"
        return f"{prefix}{formatted}{suffix}"
    except (ValueError, TypeError):
        return str(value)


def format_large_number(value: Any, decimals: int = 2) -> str:
    """
    Format large numbers with K/M/B/T suffixes.
    
    Args:
        value: Number to format
        decimals: Decimal places
        
    Returns:
        Formatted string (e.g., "1.5B", "234.5M")
    """
    if value is None:
        return "N/A"
    
    try:
        if pd.isna(value):
            return "N/A"
    except (TypeError, ValueError):
        pass
    
    try:
        num_value = float(value)
        
        if abs(num_value) >= 1_000_000_000_000:
            return f"{num_value / 1_000_000_000_000:.{decimals}f}T"
        elif abs(num_value) >= 1_000_000_000:
            return f"{num_value / 1_000_000_000:.{decimals}f}B"
        elif abs(num_value) >= 1_000_000:
            return f"{num_value / 1_000_000:.{decimals}f}M"
        elif abs(num_value) >= 1_000:
            return f"{num_value / 1_000:.{decimals}f}K"
        else:
            return f"{num_value:.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def format_percentage(value: Any, decimals: int = 2) -> str:
    """
    Format percentage value.
    
    Args:
        value: Decimal value (e.g., 0.15 for 15%)
        decimals: Decimal places
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"
    
    try:
        if pd.isna(value):
            return "N/A"
    except (TypeError, ValueError):
        pass
    
    try:
        num_value = float(value)
        percentage = num_value * 100
        return f"{percentage:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)


def format_currency(value: Any, decimals: int = 2, currency: str = "$") -> str:
    """
    Format currency value.
    
    Args:
        value: Numeric value
        decimals: Decimal places
        currency: Currency symbol
        
    Returns:
        Formatted currency string
    """
    return format_number(value, decimals=decimals, prefix=currency)


def print_financial_statement(
    data: Dict,
    title: str = "Financial Statement",
    value_formatter: Optional[callable] = None
) -> None:
    """
    Print a financial statement in a pretty table format.
    
    Args:
        data: Dictionary with date keys and metric dictionaries
        title: Title for the statement
        value_formatter: Optional function to format values
    """
    if not data:
        print(f"\n{title}: No data available\n")
        return
    
    if value_formatter is None:
        value_formatter = format_large_number
    
    # Convert to DataFrame for easier handling
    df = pd.DataFrame(data)
    
    # Get all unique metrics across all periods
    all_metrics = set()
    for period_data in data.values():
        all_metrics.update(period_data.keys())
    
    all_metrics = sorted(all_metrics)
    
    # Calculate column widths
    metric_width = max(len(str(m)) for m in all_metrics) + 2
    date_width = max(len(str(d)) for d in data.keys()) + 2
    value_width = 15
    
    # Print header
    print(f"\n{'=' * (metric_width + len(data) * value_width + 4)}")
    print(f"{title.center(metric_width + len(data) * value_width + 4)}")
    print(f"{'=' * (metric_width + len(data) * value_width + 4)}\n")
    
    # Print column headers
    header = f"{'Metric'.ljust(metric_width)}"
    for date in sorted(data.keys(), reverse=True):
        header += f"{str(date)[:10].rjust(value_width)}"
    print(header)
    print("-" * (metric_width + len(data) * value_width))
    
    # Print rows
    for metric in all_metrics:
        row = f"{str(metric).ljust(metric_width)}"
        for date in sorted(data.keys(), reverse=True):
            value = data[date].get(metric)
            formatted_value = value_formatter(value) if value is not None else "N/A"
            row += f"{formatted_value.rjust(value_width)}"
        print(row)
    
    print()


def print_ratios_table(ratios: Dict[str, Any], title: str = "Financial Ratios") -> None:
    """
    Print financial ratios in a formatted table.
    
    Args:
        ratios: Dictionary of ratio name -> value
        title: Table title
    """
    if not ratios:
        print(f"\n{title}: No data available\n")
        return
    
    print(f"\n{'=' * 60}")
    print(f"{title.center(60)}")
    print(f"{'=' * 60}\n")
    
    # Group ratios by category
    categories = {
        'Valuation': ['pe', 'peg', 'pb', 'ps', 'ev_ebitda', 'ev_revenue', 'ttm_pe'],
        'Profitability': ['roe', 'roa', 'roic', 'profit_margin', 'operating_margin', 'gross_margin', 'ebitda_margin'],
        'Liquidity': ['current_ratio', 'quick_ratio', 'cash_ratio'],
        'Leverage': ['debt_to_equity', 'debt_to_assets', 'equity_ratio', 'equity_multiplier', 'interest_coverage', 'wacc'],
        'Efficiency': ['asset_turnover', 'inventory_turnover', 'receivables_turnover'],
        'Growth': ['revenue_growth', 'earnings_growth', 'eps_growth'],
        'Dividend': ['dividend_yield', 'payout_ratio'],
        'TTM Metrics': ['ttm_eps', 'ttm_revenue', 'ttm_net_income', 'ttm_ebitda']
    }
    
    for category, ratio_keys in categories.items():
        category_ratios = {k: v for k, v in ratios.items() if k in ratio_keys and v is not None}
        
        if category_ratios:
            print(f"\n{category}:")
            print("-" * 60)
            
            for ratio_name, ratio_value in category_ratios.items():
                # Format ratio name
                display_name = ratio_name.replace('_', ' ').title()
                
                # Format value based on ratio type
                if any(x in ratio_name for x in ['margin', 'yield', 'growth', 'roe', 'roa', 'roic', 'wacc']):
                    formatted_value = format_percentage(ratio_value)
                elif 'ttm_' in ratio_name and ratio_name not in ['ttm_eps', 'ttm_pe']:
                    formatted_value = format_large_number(ratio_value)
                else:
                    formatted_value = format_number(ratio_value)
                
                print(f"  {display_name.ljust(30)}: {formatted_value.rjust(20)}")
    
    print()


def print_comparison_table(
    stocks: List[str],
    metrics: Dict[str, Dict[str, Any]],
    title: str = "Stock Comparison"
) -> None:
    """
    Print a comparison table for multiple stocks.
    
    Args:
        stocks: List of stock tickers
        metrics: Dictionary mapping metric_name -> {ticker: value}
        title: Table title
    """
    if not stocks or not metrics:
        print(f"\n{title}: No data available\n")
        return
    
    # Calculate column widths
    metric_width = max(len(str(m)) for m in metrics.keys()) + 2
    stock_width = 15
    
    print(f"\n{'=' * (metric_width + len(stocks) * stock_width + 4)}")
    print(f"{title.center(metric_width + len(stocks) * stock_width + 4)}")
    print(f"{'=' * (metric_width + len(stocks) * stock_width + 4)}\n")
    
    # Print header
    header = f"{'Metric'.ljust(metric_width)}"
    for stock in stocks:
        header += f"{stock.rjust(stock_width)}"
    print(header)
    print("-" * (metric_width + len(stocks) * stock_width))
    
    # Print rows
    for metric_name, values in metrics.items():
        row = f"{metric_name.ljust(metric_width)}"
        for stock in stocks:
            value = values.get(stock)
            formatted = format_number(value) if value is not None else "N/A"
            row += f"{formatted.rjust(stock_width)}"
        print(row)
    
    print()


def print_dataframe_pretty(
    df: pd.DataFrame,
    title: Optional[str] = None,
    max_rows: int = 50,
    max_cols: int = 10
) -> None:
    """
    Print a DataFrame in a pretty format.
    
    Args:
        df: DataFrame to print
        title: Optional title
        max_rows: Maximum rows to display
        max_cols: Maximum columns to display
    """
    if df is None or df.empty:
        print("\nNo data available\n")
        return
    
    if title:
        print(f"\n{'=' * 80}")
        print(f"{title.center(80)}")
        print(f"{'=' * 80}\n")
    
    # Set pandas display options temporarily
    with pd.option_context(
        'display.max_rows', max_rows,
        'display.max_columns', max_cols,
        'display.width', 120,
        'display.precision', 2,
        'display.float_format', '{:,.2f}'.format
    ):
        print(df)
    
    print()
