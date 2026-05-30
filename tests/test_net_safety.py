"""Tests for SSRF URL-safety guards."""

import pytest

from investormate.utils.net import is_safe_public_url, assert_safe_url
from investormate.utils.exceptions import DocumentProcessingError


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/secret",
        "http://localhost/admin",
        "http://10.0.0.5/internal",
        "http://192.168.1.1/router",
        "http://169.254.169.254/latest/meta-data/",  # cloud metadata
        "http://[::1]/loopback",
        "ftp://example.com/file",
        "file:///etc/passwd",
        "not-a-url",
        "",
    ],
)
def test_unsafe_urls_rejected(url):
    assert is_safe_public_url(url) is False


def test_numeric_public_ip_allowed():
    # Numeric IP avoids DNS; 8.8.8.8 is a public address
    assert is_safe_public_url("https://8.8.8.8/") is True


def test_allow_private_bypass_keeps_scheme_check():
    assert is_safe_public_url("http://127.0.0.1/", allow_private=True) is True
    # Scheme check still applies even with allow_private
    assert is_safe_public_url("file:///etc/passwd", allow_private=True) is False


def test_assert_safe_url_raises_on_unsafe():
    with pytest.raises(DocumentProcessingError):
        assert_safe_url("http://169.254.169.254/latest/meta-data/")


def test_assert_safe_url_returns_url_when_safe():
    assert assert_safe_url("https://8.8.8.8/") == "https://8.8.8.8/"
