"""Small safe urllib wrapper adapted from the AWS sample skill."""

from __future__ import annotations

import urllib.request
from urllib.parse import urlparse
from typing import Union

USER_AGENT = "research-idea-lab-literature-search/1.0"


def safe_urlopen(
    url_or_request: Union[urllib.request.Request, str], *, timeout: int = 30
):
    """Open only HTTP(S) URLs."""
    url = (
        url_or_request.full_url
        if isinstance(url_or_request, urllib.request.Request)
        else url_or_request
    )
    scheme = urlparse(url).scheme
    if scheme not in ("https", "http"):
        raise ValueError(f"URL scheme not allowed: {scheme!r}")
    return urllib.request.urlopen(url_or_request, timeout=timeout)  # nosec B310
