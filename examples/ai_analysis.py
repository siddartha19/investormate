"""
AI Analysis Example for InvestorMate

This example demonstrates AI-powered stock analysis.
"""

import os
from investormate import Investor

# Initialize with OpenAI (or use anthropic_api_key, gemini_api_key)
investor = Investor(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Ask a question about a stock
print("Analyzing Apple...")
result = investor.ask(
    "AAPL",
    "What are the key revenue drivers and is the stock currently undervalued?"
)

print("\nAnswer:")
print(result['answer'])

if result.get('graph_data'):
    print("\nChart Data Available:")
    print(result['graph_data'])

# Compare multiple stocks
print("\n" + "="*50)
print("Comparing tech giants...")

comparison = investor.compare(
    ["AAPL", "GOOGL", "MSFT"],
    "Which company has the best growth prospects for the next 2 years?"
)

print("\nComparison Answer:")
print(comparison['answer'])

# Batch analysis
print("\n" + "="*50)
print("Batch analysis...")

queries = [
    ("TSLA", "What's the debt situation?"),
    ("NVDA", "Is the P/E ratio justified?"),
]

results = investor.batch_analyze(queries)

for item in results:
    print(f"\n{item['ticker']}: {item['question']}")
    if 'result' in item:
        print(f"Answer: {item['result']['answer'][:200]}...")
    else:
        print(f"Error: {item.get('error')}")
