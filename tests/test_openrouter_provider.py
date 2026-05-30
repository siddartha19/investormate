"""Tests for the OpenRouter AI provider and Investor wiring."""

from unittest.mock import patch, MagicMock

import pytest

# OpenRouter reuses the openai SDK; skip cleanly if it isn't installed.
pytest.importorskip("openai")

from investormate.ai.openrouter_provider import (  # noqa: E402
    OpenRouterProvider,
    OPENROUTER_BASE_URL,
    DEFAULT_OPENROUTER_MODEL,
)

FAKE_KEY = "sk-or-v1-test-key-1234567890"


def _mock_chat_response(content: str) -> MagicMock:
    resp = MagicMock()
    choice = MagicMock()
    choice.message.content = content
    resp.choices = [choice]
    return resp


@patch("investormate.ai.openrouter_provider.openai.OpenAI")
def test_client_uses_openrouter_base_url(mock_openai_cls):
    OpenRouterProvider(FAKE_KEY)
    mock_openai_cls.assert_called_once()
    kwargs = mock_openai_cls.call_args.kwargs
    assert kwargs["base_url"] == OPENROUTER_BASE_URL
    assert kwargs["api_key"] == FAKE_KEY


@patch("investormate.ai.openrouter_provider.openai.OpenAI")
def test_default_model_and_name(mock_openai_cls):
    provider = OpenRouterProvider(FAKE_KEY)
    assert provider.model == DEFAULT_OPENROUTER_MODEL
    assert provider.provider_name == "OpenRouter"


@patch("investormate.ai.openrouter_provider.openai.OpenAI")
def test_custom_model_passthrough(mock_openai_cls):
    provider = OpenRouterProvider(FAKE_KEY, model="anthropic/claude-3.5-sonnet")
    assert provider.model == "anthropic/claude-3.5-sonnet"


@patch("investormate.ai.openrouter_provider.openai.OpenAI")
def test_ranking_headers_forwarded(mock_openai_cls):
    OpenRouterProvider(FAKE_KEY, site_url="https://example.com", site_name="MyApp")
    headers = mock_openai_cls.call_args.kwargs["default_headers"]
    assert headers["HTTP-Referer"] == "https://example.com"
    assert headers["X-Title"] == "MyApp"


@patch("investormate.ai.openrouter_provider.openai.OpenAI")
def test_no_headers_when_unset(mock_openai_cls):
    OpenRouterProvider(FAKE_KEY)
    assert mock_openai_cls.call_args.kwargs["default_headers"] is None


@patch("investormate.ai.openrouter_provider.openai.OpenAI")
def test_analyze_parses_response(mock_openai_cls):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _mock_chat_response(
        '{"answer": "Apple looks fairly valued"}'
    )
    mock_openai_cls.return_value = mock_client

    provider = OpenRouterProvider(FAKE_KEY, model="openai/gpt-4o-mini")
    result = provider.analyze(data="{...}", prompt="Is AAPL cheap?")

    assert isinstance(result, dict)
    assert result["answer"] == "Apple looks fairly valued"
    # Model slug forwarded to the API call
    called_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert called_kwargs["model"] == "openai/gpt-4o-mini"


@patch("investormate.ai.openrouter_provider.openai.OpenAI")
def test_investor_wires_openrouter(mock_openai_cls):
    from investormate import Investor

    investor = Investor(openrouter_api_key=FAKE_KEY)
    assert "openrouter" in investor.available_providers
    # Falls back to the only available provider as default
    assert investor.default_provider == "openrouter"
