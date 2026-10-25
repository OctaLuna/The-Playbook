"""Parsers and small HTTP clients for News API and RSS article sources."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

from rag.ingestion.sanitizer import sanitize_text

NEWS_API_URL = "https://newsapi.org/v2/everything"


@dataclass(frozen=True)
class NewsArticle:
    title: str
    url: str
    published_at: datetime
    source: str
    content: str


def parse_published_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(UTC)


def article_from_news_api(raw: dict[str, object]) -> NewsArticle | None:
    published = parse_published_at(_string(raw.get("publishedAt")))
    url = _string(raw.get("url"))
    title = _string(raw.get("title"))
    content = _string(raw.get("content"))
    if not published or not _is_http_url(url) or not title or not content:
        return None
    source_data = raw.get("source")
    source = _string(source_data.get("name")) if isinstance(source_data, dict) else "News API"
    sanitized = sanitize_text(content).sanitized_text
    if not sanitized:
        return None
    return NewsArticle(title[:512], url[:2048], published, source[:128] or "News API", sanitized)


def parse_rss_items(xml_text: str, *, source: str) -> list[NewsArticle]:
    # Reject declarations before parsing: RSS feeds are untrusted network input.
    if "<!DOCTYPE" in xml_text.upper() or "<!ENTITY" in xml_text.upper():
        return []
    try:
        root = ET.fromstring(xml_text)  # noqa: S314 - DTD and entity declarations are rejected above.
    except ET.ParseError:
        return []
    articles: list[NewsArticle] = []
    for item in root.iter():
        if _local_name(item.tag) not in {"item", "entry"}:
            continue
        fields = {_local_name(child.tag): child for child in item}
        link = fields.get("link")
        url = (link.attrib.get("href", "") if link is not None else "") or _text(link)
        published = parse_published_at(
            _text(fields.get("pubdate"))
            or _text(fields.get("published"))
            or _text(fields.get("updated"))
        )
        title = _text(fields.get("title"))
        content = _text(fields.get("description")) or _text(fields.get("summary"))
        if not (published and _is_http_url(url) and title and content):
            continue
        sanitized = sanitize_text(content).sanitized_text
        if sanitized:
            articles.append(
                NewsArticle(title[:512], url[:2048], published, source[:128], sanitized)
            )
    return articles


def fetch_news_api(query: str, api_key: str, *, timeout: float = 15) -> list[NewsArticle]:
    params = urllib.parse.urlencode({"q": query, "language": "en", "sortBy": "publishedAt"})
    request = urllib.request.Request(  # noqa: S310 - endpoint is a fixed HTTPS constant
        f"{NEWS_API_URL}?{params}", headers={"X-Api-Key": api_key, "User-Agent": "ThePlaybook/1.0"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed HTTPS host
        payload = json.loads(response.read())
    return [
        article
        for raw in payload.get("articles", [])
        if isinstance(raw, dict) and (article := article_from_news_api(raw)) is not None
    ]


def fetch_rss(url: str, *, timeout: float = 15) -> list[NewsArticle]:
    if urllib.parse.urlparse(url).scheme not in {"http", "https"}:
        raise ValueError("RSS feed URLs must use HTTP or HTTPS")
    request = urllib.request.Request(  # noqa: S310 - URL scheme is validated above
        url, headers={"User-Agent": "ThePlaybook/1.0"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - scheme validated
        xml_text = response.read().decode("utf-8", errors="replace")
    return parse_rss_items(xml_text, source=_host(url))


def _string(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _text(element: ET.Element | None) -> str:
    return " ".join(element.itertext()).strip() if element is not None else ""


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _host(url: str) -> str:
    return urllib.parse.urlparse(url).hostname or "RSS"


def _is_http_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
