"""
Custom strategy framework for user-defined stock screening logic.
"""

from typing import List, Dict, Callable, Optional, Any
from ..core.stock import Stock


class CustomStrategy:
    """
    Framework for creating custom stock screening strategies.
    
    Supports two modes:
    1. Function-based: Pass filter and ranking functions
    2. Builder pattern: Chain filters and ranking criteria
    
    Example (Function-based):
        >>> def my_filter(stock):
        ...     return (
        ...         10 < stock.ratios.pe < 25 and
        ...         stock.ratios.roe > 0.15
        ...     )
        ...
        >>> def my_ranking(stock):
        ...     return stock.ratios.roe * stock.ratios.revenue_growth
        ...
        >>> strategy = CustomStrategy(
        ...     filter_func=my_filter,
        ...     rank_func=my_ranking,
        ...     universe=["AAPL", "GOOGL", "MSFT"]
        ... )
        >>> results = strategy.run()
    
    Example (Builder pattern):
        >>> strategy = (
        ...     CustomStrategy()
        ...     .add_filter("pe", min=10, max=25)
        ...     .add_filter("roe", min=0.15)
        ...     .rank_by("roe")
        ...     .apply(universe=["AAPL", "GOOGL", "MSFT"])
        ... )
    """
    
    def __init__(
        self,
        filter_func: Optional[Callable[[Stock], bool]] = None,
        rank_func: Optional[Callable[[Stock], float]] = None,
        universe: Optional[List[str]] = None
    ):
        """
        Initialize custom strategy.
        
        Args:
            filter_func: Function that takes Stock and returns bool
            rank_func: Function that takes Stock and returns float (higher = better)
            universe: List of ticker symbols to screen
        """
        self.filter_func = filter_func
        self.rank_func = rank_func
        self.universe = universe or []
        
        # Builder pattern state
        self._filters = []
        self._rank_criteria = []
    
    def add_filter(self, attribute: str, min: Optional[float] = None, max: Optional[float] = None) -> 'CustomStrategy':
        """
        Add a filter criterion (builder pattern).
        
        Args:
            attribute: Attribute path (e.g., "ratios.pe", "price")
            min: Minimum value (inclusive)
            max: Maximum value (inclusive)
        
        Returns:
            Self for chaining
        
        Example:
            >>> strategy.add_filter("ratios.pe", min=10, max=25)
        """
        self._filters.append({
            'attribute': attribute,
            'min': min,
            'max': max
        })
        return self
    
    def rank_by(self, criteria: str, ascending: bool = False) -> 'CustomStrategy':
        """
        Add ranking criterion (builder pattern).
        
        Args:
            criteria: Attribute path or expression (e.g., "ratios.roe", "ratios.roe * ratios.revenue_growth")
            ascending: If True, lower values rank higher
        
        Returns:
            Self for chaining
        
        Example:
            >>> strategy.rank_by("ratios.roe", ascending=False)
        """
        self._rank_criteria.append({
            'criteria': criteria,
            'ascending': ascending
        })
        return self
    
    def apply(self, universe: List[str]) -> 'CustomStrategy':
        """
        Set universe and prepare for execution (builder pattern).
        
        Args:
            universe: List of ticker symbols
        
        Returns:
            Self for chaining
        """
        self.universe = universe
        return self
    
    def _get_attribute_value(self, stock: Stock, attribute: str) -> Any:
        """
        Get attribute value from stock using dot notation.
        
        Args:
            stock: Stock object
            attribute: Attribute path (e.g., "ratios.pe")
        
        Returns:
            Attribute value
        """
        parts = attribute.split('.')
        value = stock
        
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                return None
        
        return value
    
    def _eval_expression(self, stock: Stock, expression: str) -> float:
        """
        Evaluate expression on stock.
        
        Args:
            stock: Stock object
            expression: Expression to evaluate
        
        Returns:
            Evaluated value
        """
        # Simple evaluation for basic expressions
        # For safety, we only allow specific patterns
        
        # Check if it's a simple attribute
        if '*' not in expression and '+' not in expression and '-' not in expression and '/' not in expression:
            return self._get_attribute_value(stock, expression)
        
        # Handle simple multiplication (e.g., "ratios.roe * ratios.revenue_growth")
        if '*' in expression:
            parts = [p.strip() for p in expression.split('*')]
            result = 1.0
            for part in parts:
                val = self._get_attribute_value(stock, part)
                if val is None:
                    return None
                result *= float(val)
            return result
        
        # Add more operators as needed
        return None
    
    def _passes_filters(self, stock: Stock) -> bool:
        """
        Check if stock passes all filters.
        
        Args:
            stock: Stock object
        
        Returns:
            True if passes all filters
        """
        # Function-based filter
        if self.filter_func:
            try:
                return self.filter_func(stock)
            except Exception:
                return False
        
        # Builder pattern filters
        for filter_def in self._filters:
            attribute = filter_def['attribute']
            min_val = filter_def['min']
            max_val = filter_def['max']
            
            value = self._get_attribute_value(stock, attribute)
            
            if value is None:
                return False
            
            try:
                value = float(value)
            except (TypeError, ValueError):
                return False
            
            if min_val is not None and value < min_val:
                return False
            
            if max_val is not None and value > max_val:
                return False
        
        return True
    
    def _calculate_rank(self, stock: Stock) -> float:
        """
        Calculate ranking score for stock.
        
        Args:
            stock: Stock object
        
        Returns:
            Rank score (higher = better)
        """
        # Function-based ranking
        if self.rank_func:
            try:
                return self.rank_func(stock)
            except Exception:
                return 0.0
        
        # Builder pattern ranking
        if self._rank_criteria:
            # Use first criterion for now (can be extended to multi-criteria)
            criterion = self._rank_criteria[0]
            score = self._eval_expression(stock, criterion['criteria'])
            
            if score is None:
                return 0.0
            
            # Invert if ascending
            if criterion['ascending']:
                return -score
            
            return score
        
        return 0.0
    
    def run(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Run the strategy on the universe.
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of dicts with ticker and rank score, sorted by rank
        
        Example:
            >>> results = strategy.run(limit=10)
            >>> for result in results:
            ...     print(f"{result['ticker']}: {result['rank']}")
        """
        if not self.universe:
            return []
        
        results = []
        
        for ticker in self.universe:
            try:
                stock = Stock(ticker)
                
                # Check if passes filters
                if not self._passes_filters(stock):
                    continue
                
                # Calculate rank
                rank = self._calculate_rank(stock)
                
                results.append({
                    'ticker': ticker,
                    'rank': rank,
                    'name': stock.name,
                    'price': stock.price
                })
            
            except Exception as e:
                # Skip stocks that fail (e.g., bad ticker, data unavailable)
                print(f"Skipping {ticker}: {e}")
                continue
        
        # Sort by rank (highest first)
        results.sort(key=lambda x: x['rank'], reverse=True)
        
        # Apply limit
        if limit:
            results = results[:limit]
        
        return results
    
    def __repr__(self) -> str:
        """String representation."""
        return f"CustomStrategy(universe_size={len(self.universe)})"
