"""
Earnings Call Transcripts module for InvestorMate.
Fetches and processes earnings call transcripts.
"""

from typing import Dict, List, Optional
import pandas as pd
import yfinance as yf
from ..utils.exceptions import DataFetchError


class EarningsCallTranscripts:
    """
    Handler for earnings call transcripts.
    
    Example:
        >>> transcripts = EarningsCallTranscripts("AAPL")
        >>> transcript_list = transcripts.get_transcripts_list()
        >>> q4_2024 = transcripts.get_transcript(2024, 4)
    """
    
    def __init__(self, ticker: str):
        """
        Initialize earnings call transcripts handler.
        
        Args:
            ticker: Stock ticker symbol
        """
        self.ticker = ticker
        self._ticker_obj = None
        self._transcripts_cache = {}
    
    @property
    def _yf_ticker(self):
        """Get yfinance Ticker object (cached)."""
        if self._ticker_obj is None:
            self._ticker_obj = yf.Ticker(self.ticker)
        return self._ticker_obj
    
    def get_transcripts_list(self) -> pd.DataFrame:
        """
        Get list of available earnings call transcripts.
        
        Returns:
            DataFrame with columns: fiscal_year, fiscal_quarter, report_date, has_transcript
            
        Note:
            yfinance does not provide earnings call transcripts directly.
            This is a placeholder that returns earnings dates.
            For actual transcripts, integration with services like AlphaSense,
            Seeking Alpha, or SEC Edgar would be required.
        """
        try:
            # Get earnings dates as a proxy for available transcripts
            earnings_dates = self._yf_ticker.earnings_dates
            
            if earnings_dates is None or earnings_dates.empty:
                return pd.DataFrame(columns=['fiscal_year', 'fiscal_quarter', 'report_date', 'has_transcript'])
            
            # Convert earnings dates to transcript list format
            result = []
            for date, row in earnings_dates.iterrows():
                # Extract year and quarter from date
                year = date.year
                quarter = (date.month - 1) // 3 + 1
                
                result.append({
                    'fiscal_year': year,
                    'fiscal_quarter': quarter,
                    'report_date': date.strftime('%Y-%m-%d'),
                    'has_transcript': False  # yfinance doesn't provide transcripts
                })
            
            df = pd.DataFrame(result)
            # Remove duplicates and sort
            df = df.drop_duplicates(subset=['fiscal_year', 'fiscal_quarter'])
            df = df.sort_values(['fiscal_year', 'fiscal_quarter'], ascending=False)
            
            return df.reset_index(drop=True)
            
        except Exception as e:
            raise DataFetchError(f"Failed to fetch transcripts list: {str(e)}")
    
    def get_transcript(self, year: int, quarter: int) -> Optional[pd.DataFrame]:
        """
        Get earnings call transcript for a specific quarter.
        
        Args:
            year: Fiscal year (e.g., 2024)
            quarter: Fiscal quarter (1-4)
            
        Returns:
            DataFrame with columns: paragraph_number, speaker, content
            or None if transcript not available
            
        Note:
            yfinance does not provide earnings call transcripts.
            This is a placeholder that returns None.
            For actual transcripts, integration with:
            - Alpha Vantage (premium)
            - Seeking Alpha (requires scraping)
            - SEC Edgar (8-K filings may contain transcripts)
            - AlphaSense (commercial)
            would be required.
        """
        cache_key = f"{year}_Q{quarter}"
        
        if cache_key in self._transcripts_cache:
            return self._transcripts_cache[cache_key]
        
        # yfinance doesn't provide transcripts
        # Return None to indicate not available
        return None
    
    def print_pretty_table(self, year: int, quarter: int) -> None:
        """
        Print earnings call transcript in a formatted table.
        
        Args:
            year: Fiscal year
            quarter: Fiscal quarter (1-4)
        """
        transcript = self.get_transcript(year, quarter)
        
        if transcript is None:
            print(f"\n⚠️  Earnings call transcript not available for {self.ticker} FY{year} Q{quarter}")
            print("\nNote: yfinance does not provide earnings call transcripts.")
            print("Consider integrating with:")
            print("  - Alpha Vantage (premium API)")
            print("  - Seeking Alpha (requires web scraping)")
            print("  - SEC Edgar (8-K filings)")
            print("  - AlphaSense (commercial service)")
            return
        
        # Format and print transcript
        print(f"\n{'='*80}")
        print(f"Earnings Call Transcript - {self.ticker} FY{year} Q{quarter}")
        print(f"{'='*80}\n")
        
        for _, row in transcript.iterrows():
            speaker = row['speaker']
            content = row['content']
            
            print(f"\n[{speaker}]")
            print("-" * 80)
            print(content)
            print()
    
    def search_transcript(self, year: int, quarter: int, keyword: str) -> List[Dict]:
        """
        Search for keyword in earnings call transcript.
        
        Args:
            year: Fiscal year
            quarter: Fiscal quarter (1-4)
            keyword: Search term
            
        Returns:
            List of dictionaries with matching paragraphs
        """
        transcript = self.get_transcript(year, quarter)
        
        if transcript is None:
            return []
        
        # Case-insensitive search
        keyword_lower = keyword.lower()
        matches = []
        
        for _, row in transcript.iterrows():
            if keyword_lower in row['content'].lower():
                matches.append({
                    'paragraph_number': row['paragraph_number'],
                    'speaker': row['speaker'],
                    'content': row['content']
                })
        
        return matches
    
    def get_all_transcripts(self) -> Dict[str, pd.DataFrame]:
        """
        Get all available transcripts.
        
        Returns:
            Dictionary mapping "YEAR_QX" -> DataFrame
        """
        transcripts_list = self.get_transcripts_list()
        all_transcripts = {}
        
        for _, row in transcripts_list.iterrows():
            year = row['fiscal_year']
            quarter = row['fiscal_quarter']
            transcript = self.get_transcript(year, quarter)
            
            if transcript is not None:
                key = f"{year}_Q{quarter}"
                all_transcripts[key] = transcript
        
        return all_transcripts
