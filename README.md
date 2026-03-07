# Junipr Python SDK

Official Python SDK for the [Junipr API](https://junipr.io) — capture screenshots, generate PDFs, and extract metadata from any URL.

[![PyPI](https://img.shields.io/pypi/v/junipr)](https://pypi.org/project/junipr/)
[![Python](https://img.shields.io/pypi/pyversions/junipr)](https://pypi.org/project/junipr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install junipr
```

## Quick Start

```python
from junipr import Junipr

client = Junipr("your-api-key")

# Take a screenshot
image = client.screenshot("https://example.com")
with open("screenshot.png", "wb") as f:
    f.write(image)
```

## Usage

### Screenshots

Capture pixel-perfect screenshots of any URL.

```python
from junipr import Junipr

client = Junipr("your-api-key")

# Basic screenshot
image = client.screenshot("https://example.com")

# Full-page screenshot with options
image = client.screenshot(
    "https://example.com",
    width=1920,
    height=1080,
    format="webp",
    quality=90,
    full_page=True,
    block_banners=True,
    device="desktop",
)

with open("screenshot.webp", "wb") as f:
    f.write(image)
```

### PDFs

Generate PDFs from URLs or raw HTML.

```python
from junipr import Junipr

client = Junipr("your-api-key")

# PDF from URL
pdf = client.pdf(url="https://example.com")

# PDF from HTML with options
pdf = client.pdf(
    html="<h1>Invoice #1234</h1><p>Amount: $99.00</p>",
    format="Letter",
    margin={"top": "1in", "bottom": "1in", "left": "0.5in", "right": "0.5in"},
    print_background=True,
)

with open("output.pdf", "wb") as f:
    f.write(pdf)
```

### Metadata

Extract title, description, Open Graph, Twitter Card, structured data, and more.

```python
from junipr import Junipr

client = Junipr("your-api-key")

meta = client.metadata("https://example.com")
print(meta.title)          # "Example Domain"
print(meta.description)    # "This domain is for use in illustrative examples..."
print(meta.og.image)       # "https://example.com/og-image.png"
print(meta.language)       # "en"
```

### Error Handling

All API errors raise `JuniprError` with structured error details.

```python
from junipr import Junipr, JuniprError

client = Junipr("your-api-key")

try:
    image = client.screenshot("https://example.com")
except JuniprError as e:
    print(e.code)        # "RATE_LIMITED"
    print(e.message)     # "Too many requests"
    print(e.request_id)  # "req_abc123"
    print(e.status_code) # 429
```

### Request a Free API Key

```python
from junipr import Junipr

client = Junipr("")  # No key needed for this endpoint
result = client.request_free_key("you@example.com")
print(result.message)  # "API key sent to you@example.com"
```

### Self-Hosted / Custom Base URL

```python
from junipr import Junipr

client = Junipr("your-api-key", base_url="https://junipr.internal.company.com")
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `api_key` | required | Your Junipr API key |
| `base_url` | `https://api.junipr.io` | API base URL |
| `timeout` | `60.0` | Request timeout in seconds |
| `httpx_client` | `None` | Bring your own `httpx.Client` or `httpx.AsyncClient` |

## License

MIT
