# AI Providers Guide

InvestorMate supports multiple AI providers for stock analysis. Choose the one that best fits your needs.

## Supported Providers

- **OpenAI** (GPT-4, GPT-4o)
- **Anthropic** (Claude 3.5 Sonnet)
- **Google Gemini** (Gemini 1.5 Pro)

## Getting API Keys

### OpenAI

1. Visit https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `sk-`)

**Pricing**: Pay-as-you-go, ~$0.01-0.03 per analysis

### Anthropic Claude

1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Generate an API key
4. Copy the key (starts with `sk-ant-`)

**Pricing**: Pay-as-you-go, similar to OpenAI

### Google Gemini

1. Visit https://ai.google.dev/
2. Sign up for Google AI Studio
3. Create an API key
4. Copy the key

**Pricing**: Free tier available, then pay-as-you-go

## Usage

### Single Provider

```python
from investormate import Investor

# OpenAI only
investor = Investor(openai_api_key="sk-...")

# Anthropic only
investor = Investor(anthropic_api_key="sk-ant-...")

# Gemini only
investor = Investor(gemini_api_key="...")
```

### Multiple Providers

```python
from investormate import Investor

investor = Investor(
    openai_api_key="sk-...",
    anthropic_api_key="sk-ant-...",
    gemini_api_key="...",
    default_provider="openai"
)

# Use default provider
result1 = investor.ask("AAPL", "Analyze valuation")

# Specify provider explicitly
result2 = investor.ask("AAPL", "Analyze valuation", provider="anthropic")
result3 = investor.ask("AAPL", "Analyze valuation", provider="gemini")

# Check available providers
print(investor.available_providers)
```

## Provider Comparison

| Feature | OpenAI | Anthropic | Gemini |
|---------|--------|-----------|--------|
| **Model** | GPT-4o | Claude 3.5 Sonnet | Gemini 1.5 Pro |
| **Speed** | Fast | Fast | Very Fast |
| **Quality** | Excellent | Excellent | Very Good |
| **Cost** | $$$ | $$$ | $ (Free tier) |
| **Context Window** | 128K | 200K | 2M |

## Best Practices

### Cost Optimization

1. **Use caching**: Store results for repeated queries
2. **Batch queries**: Use `batch_analyze()` for multiple stocks
3. **Choose wisely**: Gemini has a free tier for experimentation

```python
# Cache results
results_cache = {}

ticker = "AAPL"
if ticker not in results_cache:
    results_cache[ticker] = investor.ask(ticker, question)
```

### Rate Limiting

All providers have rate limits. Handle them gracefully:

```python
from investormate.utils.exceptions import AIProviderError

try:
    result = investor.ask("AAPL", "Analyze stock")
except AIProviderError as e:
    if "rate limit" in str(e).lower():
        # Wait and retry
        time.sleep(60)
        result = investor.ask("AAPL", "Analyze stock")
    else:
        raise
```

### Environment Variables

Store API keys securely:

```bash
# .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
```

```python
import os
from dotenv import load_dotenv

load_dotenv()

investor = Investor(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
)
```

## Features by Provider

### All Providers Support

- Stock analysis
- Document analysis
- Multi-stock comparison
- Batch processing
- Custom prompts

### Provider-Specific Notes

**OpenAI**:
- Most tested
- Excellent at financial analysis
- Good at generating structured responses (JSON)

**Anthropic**:
- Great at reasoning
- More conservative/balanced analysis
- Excellent context understanding

**Gemini**:
- Very fast responses
- Free tier available
- Large context window for complex analyses

## Troubleshooting

### Invalid API Key

```python
from investormate.utils.exceptions import APIKeyError

try:
    investor = Investor(openai_api_key="invalid")
except APIKeyError as e:
    print(f"Error: {e}")
```

### No Provider Available

```python
# At least one provider required
investor = Investor()  # ❌ Raises APIKeyError

# Correct usage
investor = Investor(openai_api_key="sk-...")  # ✅
```

### Provider Not Initialized

```python
investor = Investor(openai_api_key="sk-...")

# This will fail - anthropic not initialized
result = investor.ask("AAPL", "question", provider="anthropic")  # ❌

# Check available providers first
if "anthropic" in investor.available_providers:
    result = investor.ask("AAPL", "question", provider="anthropic")  # ✅
```

## Example: Fallback Pattern

```python
def analyze_with_fallback(ticker, question):
    """Try multiple providers in order."""
    providers = ["openai", "anthropic", "gemini"]
    
    for provider in providers:
        if provider in investor.available_providers:
            try:
                return investor.ask(ticker, question, provider=provider)
            except Exception as e:
                print(f"{provider} failed: {e}")
                continue
    
    raise Exception("All providers failed")
```

## Security Best Practices

1. **Never commit API keys**: Use environment variables
2. **Rotate keys regularly**: Generate new keys periodically
3. **Monitor usage**: Check your provider dashboards for unusual activity
4. **Set spending limits**: Configure budget alerts in provider dashboards
5. **Use read-only keys**: If available, use keys with limited permissions

## Support

For provider-specific issues:
- OpenAI: https://help.openai.com
- Anthropic: https://support.anthropic.com
- Gemini: https://ai.google.dev/docs

For InvestorMate issues:
- GitHub: https://github.com/investormate/investormate/issues
