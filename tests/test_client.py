"""Tests for Junipr sync and async clients."""

from __future__ import annotations

import json
from typing import Any, Dict

import httpx
import pytest

from junipr import AsyncJunipr, Junipr, JuniprError, MetadataResponse


def _mock_transport(
    status_code: int = 200,
    content: bytes = b"",
    json_body: Dict[str, Any] | None = None,
    content_type: str = "application/octet-stream",
) -> httpx.MockTransport:
    """Create a mock transport that returns a fixed response."""

    def handler(request: httpx.Request) -> httpx.Response:
        headers = {"content-type": content_type}
        if json_body is not None:
            return httpx.Response(
                status_code,
                content=json.dumps(json_body).encode(),
                headers={**headers, "content-type": "application/json"},
            )
        return httpx.Response(status_code, content=content, headers=headers)

    return httpx.MockTransport(handler)


# --- Sync client tests ---


class TestJuniprScreenshot:
    def test_returns_bytes(self) -> None:
        transport = _mock_transport(content=b"\x89PNG fake image data")
        client = httpx.Client(transport=transport, base_url="https://api.junipr.io")
        j = Junipr("test-key", httpx_client=client)
        result = j.screenshot("https://example.com")
        assert result == b"\x89PNG fake image data"

    def test_passes_options(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["url"] == "https://example.com"
            assert body["width"] == 1920
            assert body["full_page"] is True
            assert "wait_for" not in body  # None values stripped
            return httpx.Response(200, content=b"ok")

        transport = httpx.MockTransport(handler)
        client = httpx.Client(transport=transport, base_url="https://api.junipr.io")
        j = Junipr("test-key", httpx_client=client)
        j.screenshot("https://example.com", width=1920, full_page=True)

    def test_raises_on_error(self) -> None:
        transport = _mock_transport(
            status_code=429,
            json_body={
                "error": True,
                "code": "RATE_LIMITED",
                "message": "Too many requests",
                "request_id": "req_123",
            },
        )
        client = httpx.Client(transport=transport, base_url="https://api.junipr.io")
        j = Junipr("test-key", httpx_client=client)
        with pytest.raises(JuniprError) as exc_info:
            j.screenshot("https://example.com")
        assert exc_info.value.code == "RATE_LIMITED"
        assert exc_info.value.request_id == "req_123"
        assert exc_info.value.status_code == 429


class TestJuniprPDF:
    def test_returns_bytes(self) -> None:
        transport = _mock_transport(content=b"%PDF-1.4 fake pdf")
        client = httpx.Client(transport=transport, base_url="https://api.junipr.io")
        j = Junipr("test-key", httpx_client=client)
        result = j.pdf(url="https://example.com")
        assert result == b"%PDF-1.4 fake pdf"

    def test_html_input(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["html"] == "<h1>Hello</h1>"
            assert "url" not in body
            return httpx.Response(200, content=b"%PDF")

        transport = httpx.MockTransport(handler)
        client = httpx.Client(transport=transport, base_url="https://api.junipr.io")
        j = Junipr("test-key", httpx_client=client)
        j.pdf(html="<h1>Hello</h1>")


class TestJuniprMetadata:
    def test_parses_response(self) -> None:
        transport = _mock_transport(
            json_body={
                "url": "https://example.com",
                "title": "Example",
                "description": "An example page",
                "og": {"title": "OG Title", "image": "https://example.com/og.png"},
                "twitter": {"card": "summary_large_image"},
                "favicon": "https://example.com/favicon.ico",
                "canonical": "https://example.com",
                "language": "en",
                "structured_data": [],
                "response_time_ms": 150,
            },
        )
        client = httpx.Client(transport=transport, base_url="https://api.junipr.io")
        j = Junipr("test-key", httpx_client=client)
        meta = j.metadata("https://example.com")
        assert isinstance(meta, MetadataResponse)
        assert meta.title == "Example"
        assert meta.og is not None
        assert meta.og.title == "OG Title"
        assert meta.twitter is not None
        assert meta.twitter.card == "summary_large_image"
        assert meta.response_time_ms == 150


class TestJuniprFreeKey:
    def test_returns_key_response(self) -> None:
        transport = _mock_transport(
            json_body={"success": True, "message": "Key sent to test@example.com"},
        )
        client = httpx.Client(transport=transport, base_url="https://api.junipr.io")
        j = Junipr("test-key", httpx_client=client)
        result = j.request_free_key("test@example.com")
        assert result.success is True
        assert "test@example.com" in result.message


class TestJuniprContextManager:
    def test_sync_context_manager(self) -> None:
        transport = _mock_transport(content=b"ok")
        client = httpx.Client(transport=transport, base_url="https://api.junipr.io")
        with Junipr("test-key", httpx_client=client) as j:
            result = j.screenshot("https://example.com")
            assert result == b"ok"


# --- Async client tests ---


class TestAsyncJuniprScreenshot:
    @pytest.mark.anyio
    async def test_returns_bytes(self) -> None:
        transport = _mock_transport(content=b"\x89PNG async image")
        client = httpx.AsyncClient(
            transport=transport, base_url="https://api.junipr.io"
        )
        j = AsyncJunipr("test-key", httpx_client=client)
        result = await j.screenshot("https://example.com")
        assert result == b"\x89PNG async image"

    @pytest.mark.anyio
    async def test_raises_on_error(self) -> None:
        transport = _mock_transport(
            status_code=401,
            json_body={
                "error": True,
                "code": "UNAUTHORIZED",
                "message": "Invalid API key",
                "request_id": "req_456",
            },
        )
        client = httpx.AsyncClient(
            transport=transport, base_url="https://api.junipr.io"
        )
        j = AsyncJunipr("test-key", httpx_client=client)
        with pytest.raises(JuniprError) as exc_info:
            await j.screenshot("https://example.com")
        assert exc_info.value.code == "UNAUTHORIZED"
        assert exc_info.value.status_code == 401


class TestAsyncJuniprContextManager:
    @pytest.mark.anyio
    async def test_async_context_manager(self) -> None:
        transport = _mock_transport(content=b"ok")
        client = httpx.AsyncClient(
            transport=transport, base_url="https://api.junipr.io"
        )
        async with AsyncJunipr("test-key", httpx_client=client) as j:
            result = await j.screenshot("https://example.com")
            assert result == b"ok"


class TestHeaders:
    def test_api_key_header_sent(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["X-API-Key"] == "my-secret-key"
            assert "junipr-python/" in request.headers["User-Agent"]
            return httpx.Response(200, content=b"ok")

        transport = httpx.MockTransport(handler)
        client = httpx.Client(
            transport=transport,
            base_url="https://api.junipr.io",
            headers={
                "X-API-Key": "my-secret-key",
                "User-Agent": "junipr-python/0.1.0",
            },
        )
        j = Junipr("my-secret-key", httpx_client=client)
        j.screenshot("https://example.com")
