"""
Multi-Provider AI Example for InvestorMate

This example demonstrates using different AI providers.
"""

import os
from investormate import Investor

# Initialize with multiple providers
investor = Investor(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    # gemini_api_key=os.getenv("GEMINI_API_KEY"),
    default_provider="openai"
)

print(f"Available providers: {investor.available_providers}")

# Use OpenAI
print("\n" + "="*50)
print("Using OpenAI GPT-4...")
result_openai = investor.ask(
    "AAPL",
    "What's the current valuation?",
    provider="openai"
)
print(f"OpenAI Answer: {result_openai['answer'][:200]}...")

# Use Anthropic Claude (if available)
if "anthropic" in investor.available_providers:
    print("\n" + "="*50)
    print("Using Anthropic Claude...")
    result_anthropic = investor.ask(
        "AAPL",
        "What's the current valuation?",
        provider="anthropic"
    )
    print(f"Anthropic Answer: {result_anthropic['answer'][:200]}...")

# Use Gemini (if available)
if "gemini" in investor.available_providers:
    print("\n" + "="*50)
    print("Using Google Gemini...")
    result_gemini = investor.ask(
        "AAPL",
        "What's the current valuation?",
        provider="gemini"
    )
    print(f"Gemini Answer: {result_gemini['answer'][:200]}...")

# Default provider is used when not specified
result_default = investor.ask("MSFT", "Analyze growth prospects")
print(f"\nDefault provider ({investor.default_provider}) answer:")
print(result_default['answer'][:200] + "...")
