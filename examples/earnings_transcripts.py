"""
Example: Earnings Call Transcripts

This example demonstrates how to access and work with earnings call transcripts.

Note: Currently yfinance does not provide actual transcript text.
This module provides the infrastructure and will return earnings dates.
For full transcript functionality, integration with services like:
- Alpha Vantage (premium API)
- Seeking Alpha (web scraping)
- SEC Edgar (8-K filings)
- AlphaSense (commercial)
would be required.
"""

from investormate import Stock
from investormate.utils import print_dataframe_pretty

def main():
    # Initialize stock
    ticker = "AAPL"
    print(f"\n{'='*80}")
    print(f"Earnings Call Transcripts Example for {ticker}")
    print(f"{'='*80}\n")
    
    stock = Stock(ticker)
    
    # 1. Get list of available transcripts (earnings dates)
    print("\n1. Available Earnings Dates")
    print("-" * 80)
    
    transcripts_list = stock.earnings_transcripts.get_transcripts_list()
    
    if not transcripts_list.empty:
        print(f"\nFound {len(transcripts_list)} earnings dates:\n")
        print_dataframe_pretty(
            transcripts_list.head(10),
            title="Recent Earnings Dates",
            max_rows=10
        )
    else:
        print("\nNo earnings dates available.")
    
    # 2. Try to get a specific transcript
    print("\n2. Attempting to Fetch Specific Transcript")
    print("-" * 80)
    
    if not transcripts_list.empty:
        # Get the most recent earnings date
        latest = transcripts_list.iloc[0]
        year = latest['fiscal_year']
        quarter = latest['fiscal_quarter']
        
        print(f"\nAttempting to fetch FY{year} Q{quarter} transcript...")
        transcript = stock.earnings_transcripts.get_transcript(year, quarter)
        
        if transcript is not None:
            print(f"\n✓ Transcript found! ({len(transcript)} paragraphs)")
            print_dataframe_pretty(transcript.head(5), title="Transcript Preview")
        else:
            print("\n⚠️  Transcript text not available through yfinance.")
            print("\nTo enable transcript functionality, consider integrating with:")
            print("  • Alpha Vantage API (premium)")
            print("  • Seeking Alpha (web scraping)")
            print("  • SEC Edgar 8-K filings")
            print("  • AlphaSense (commercial service)")
    
    # 3. Print formatted transcript
    print("\n3. Pretty Print Transcript")
    print("-" * 80)
    
    if not transcripts_list.empty:
        latest = transcripts_list.iloc[0]
        year = latest['fiscal_year']
        quarter = latest['fiscal_quarter']
        
        stock.earnings_transcripts.print_pretty_table(year, quarter)
    
    # 4. Search transcript (if available)
    print("\n4. Search Transcript for Keywords")
    print("-" * 80)
    
    if not transcripts_list.empty:
        latest = transcripts_list.iloc[0]
        year = latest['fiscal_year']
        quarter = latest['fiscal_quarter']
        
        keywords = ["revenue", "growth", "AI", "innovation"]
        
        for keyword in keywords:
            matches = stock.earnings_transcripts.search_transcript(year, quarter, keyword)
            print(f"\nSearching for '{keyword}': {len(matches)} matches")
    
    # 5. Example of what the transcript API would look like (with actual data)
    print("\n5. Example Transcript Structure (if data was available)")
    print("-" * 80)
    
    print("""
When integrated with a transcript provider, the data structure would be:

DataFrame columns:
    - paragraph_number: int (sequential numbering)
    - speaker: str (CEO, CFO, Analyst, etc.)
    - content: str (actual text of what was said)

Example usage:
    transcript = stock.earnings_transcripts.get_transcript(2024, 4)
    
    # Filter by speaker
    ceo_comments = transcript[transcript['speaker'].str.contains('CEO')]
    
    # Search for keywords
    ai_mentions = stock.earnings_transcripts.search_transcript(2024, 4, 'artificial intelligence')
    
    # Pretty print
    stock.earnings_transcripts.print_pretty_table(2024, 4)
    """)
    
    print("\n" + "=" * 80)
    print("Example Complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
