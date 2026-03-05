"""Type definitions for Junipr SDK request/response objects."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict
else:
    from typing_extensions import NotRequired, TypedDict

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


class ScreenshotOptions(TypedDict, total=False):
    """Options for the screenshot endpoint."""

    url: str  # required — enforced at call site
    width: int
    height: int
    format: Literal["png", "jpeg", "webp"]
    quality: int
    full_page: bool
    block_banners: bool
    wait_for: Optional[str]
    delay: int
    device: Literal["desktop", "mobile", "tablet"]
    cache: bool


class MarginOptions(TypedDict, total=False):
    """PDF margin options."""

    top: str
    right: str
    bottom: str
    left: str


class PDFOptions(TypedDict, total=False):
    """Options for the PDF endpoint."""

    url: Optional[str]
    html: Optional[str]
    format: Literal["A4", "Letter", "Legal", "Tabloid", "A3", "A5"]
    margin: Optional[MarginOptions]
    landscape: bool
    print_background: bool
    header: Optional[str]
    footer: Optional[str]
    cache: bool


@dataclass
class OpenGraphData:
    """Open Graph metadata."""

    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    url: Optional[str] = None
    type: Optional[str] = None
    site_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OpenGraphData:
        return cls(
            title=data.get("title"),
            description=data.get("description"),
            image=data.get("image"),
            url=data.get("url"),
            type=data.get("type"),
            site_name=data.get("site_name"),
        )


@dataclass
class TwitterCardData:
    """Twitter Card metadata."""

    card: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    site: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TwitterCardData:
        return cls(
            card=data.get("card"),
            title=data.get("title"),
            description=data.get("description"),
            image=data.get("image"),
            site=data.get("site"),
        )


@dataclass
class MetadataResponse:
    """Parsed metadata response."""

    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    og: Optional[OpenGraphData] = None
    twitter: Optional[TwitterCardData] = None
    favicon: Optional[str] = None
    canonical: Optional[str] = None
    language: Optional[str] = None
    structured_data: List[Dict[str, Any]] = field(default_factory=list)
    response_time_ms: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MetadataResponse:
        og_raw = data.get("og")
        twitter_raw = data.get("twitter")
        return cls(
            url=data["url"],
            title=data.get("title"),
            description=data.get("description"),
            og=OpenGraphData.from_dict(og_raw) if og_raw else None,
            twitter=TwitterCardData.from_dict(twitter_raw) if twitter_raw else None,
            favicon=data.get("favicon"),
            canonical=data.get("canonical"),
            language=data.get("language"),
            structured_data=data.get("structured_data", []),
            response_time_ms=data.get("response_time_ms"),
        )


@dataclass
class KeyResponse:
    """Response from the free key endpoint."""

    success: bool
    message: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> KeyResponse:
        return cls(success=data["success"], message=data["message"])
