"""Sync and async Junipr API clients."""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from junipr._exceptions import JuniprError
from junipr._types import (
    KeyResponse,
    MetadataResponse,
    PDFOptions,
    ScreenshotOptions,
)
from junipr._version import __version__

DEFAULT_BASE_URL = "https://api.junipr.io"
DEFAULT_TIMEOUT = 60.0


def _build_headers(api_key: str) -> Dict[str, str]:
    return {
        "X-API-Key": api_key,
        "User-Agent": f"junipr-python/{__version__}",
    }


def _check_error(response: httpx.Response) -> None:
    """Raise JuniprError if the response indicates an API error."""
    if response.status_code >= 400:
        try:
            body = response.json()
        except Exception:
            body = {}

        raise JuniprError(
            message=body.get("message", response.text),
            code=body.get("code", f"HTTP_{response.status_code}"),
            request_id=body.get("request_id", ""),
            status_code=response.status_code,
        )


def _strip_none(d: Dict[str, Any]) -> Dict[str, Any]:
    """Remove keys with None values from a dict."""
    return {k: v for k, v in d.items() if v is not None}


class Junipr:
    """Synchronous Junipr API client.

    Args:
        api_key: Your Junipr API key.
        base_url: Override the API base URL (for self-hosting).
        timeout: Request timeout in seconds.
        httpx_client: Optional pre-configured httpx.Client to use.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        httpx_client: Optional[httpx.Client] = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._owns_client = httpx_client is None
        self._client = httpx_client or httpx.Client(
            base_url=self._base_url,
            headers=_build_headers(api_key),
            timeout=timeout,
        )

    def screenshot(
        self,
        url: str,
        **options: Any,
    ) -> bytes:
        """Capture a screenshot of a URL.

        Args:
            url: The URL to screenshot.
            **options: Additional ScreenshotOptions fields (width, height,
                format, quality, full_page, block_banners, wait_for, delay,
                device, cache).

        Returns:
            Raw image bytes (PNG, JPEG, or WebP).
        """
        payload: Dict[str, Any] = {"url": url, **options}
        response = self._client.post("/v1/screenshot", json=_strip_none(payload))
        _check_error(response)
        return response.content

    def pdf(
        self,
        *,
        url: Optional[str] = None,
        html: Optional[str] = None,
        **options: Any,
    ) -> bytes:
        """Generate a PDF from a URL or raw HTML.

        Args:
            url: The URL to render as PDF.
            html: Raw HTML to render as PDF.
            **options: Additional PDFOptions fields (format, margin,
                landscape, print_background, header, footer, cache).

        Returns:
            Raw PDF bytes.
        """
        payload: Dict[str, Any] = {"url": url, "html": html, **options}
        response = self._client.post("/v1/pdf", json=_strip_none(payload))
        _check_error(response)
        return response.content

    def metadata(self, url: str) -> MetadataResponse:
        """Extract metadata from a URL.

        Args:
            url: The URL to extract metadata from.

        Returns:
            A MetadataResponse with title, description, OG tags, etc.
        """
        response = self._client.get("/v1/metadata", params={"url": url})
        _check_error(response)
        return MetadataResponse.from_dict(response.json())

    def request_free_key(self, email: str) -> KeyResponse:
        """Request a free API key.

        Args:
            email: Email address to send the key to.

        Returns:
            A KeyResponse with success status and message.
        """
        response = self._client.post("/v1/keys/free", json={"email": email})
        _check_error(response)
        return KeyResponse.from_dict(response.json())

    def close(self) -> None:
        """Close the underlying HTTP client (if owned by this instance)."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> Junipr:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncJunipr:
    """Asynchronous Junipr API client.

    Args:
        api_key: Your Junipr API key.
        base_url: Override the API base URL (for self-hosting).
        timeout: Request timeout in seconds.
        httpx_client: Optional pre-configured httpx.AsyncClient to use.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._owns_client = httpx_client is None
        self._client = httpx_client or httpx.AsyncClient(
            base_url=self._base_url,
            headers=_build_headers(api_key),
            timeout=timeout,
        )

    async def screenshot(
        self,
        url: str,
        **options: Any,
    ) -> bytes:
        """Capture a screenshot of a URL.

        Args:
            url: The URL to screenshot.
            **options: Additional ScreenshotOptions fields.

        Returns:
            Raw image bytes (PNG, JPEG, or WebP).
        """
        payload: Dict[str, Any] = {"url": url, **options}
        response = await self._client.post("/v1/screenshot", json=_strip_none(payload))
        _check_error(response)
        return response.content

    async def pdf(
        self,
        *,
        url: Optional[str] = None,
        html: Optional[str] = None,
        **options: Any,
    ) -> bytes:
        """Generate a PDF from a URL or raw HTML.

        Args:
            url: The URL to render as PDF.
            html: Raw HTML to render as PDF.
            **options: Additional PDFOptions fields.

        Returns:
            Raw PDF bytes.
        """
        payload: Dict[str, Any] = {"url": url, "html": html, **options}
        response = await self._client.post("/v1/pdf", json=_strip_none(payload))
        _check_error(response)
        return response.content

    async def metadata(self, url: str) -> MetadataResponse:
        """Extract metadata from a URL.

        Args:
            url: The URL to extract metadata from.

        Returns:
            A MetadataResponse with title, description, OG tags, etc.
        """
        response = await self._client.get("/v1/metadata", params={"url": url})
        _check_error(response)
        return MetadataResponse.from_dict(response.json())

    async def request_free_key(self, email: str) -> KeyResponse:
        """Request a free API key.

        Args:
            email: Email address to send the key to.

        Returns:
            A KeyResponse with success status and message.
        """
        response = await self._client.post("/v1/keys/free", json={"email": email})
        _check_error(response)
        return KeyResponse.from_dict(response.json())

    async def close(self) -> None:
        """Close the underlying HTTP client (if owned by this instance)."""
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncJunipr:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
