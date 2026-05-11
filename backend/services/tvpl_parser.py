"""
TVPL Parser — parse thuvienphapluat.vn document pages to HTML content.
Used as fallback when CrawlKit API is unavailable/slow.
"""
import re
import logging
from typing import Optional, Dict
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}

SO_HIEU_PATTERN = re.compile(
    r"(?:Luật|Nghị định|Thông tư|Quyết định|Nghị quyết|Pháp lệnh)\s+[\d/\-]+(?:/\w+)*",
    re.IGNORECASE
)


def _extract_so_hieu(title: str) -> str:
    """Extract document number from title string."""
    m = re.search(r"(\d+[\d/\-]+(?:/\w+)+)", title)
    return m.group(1) if m else ""


def _extract_loai(title: str, url: str = "") -> str:
    """Detect document type from title."""
    title_l = title.lower()
    if "thông tư" in title_l: return "Thông tư"
    if "nghị định" in title_l: return "Nghị định"
    if "luật" in title_l: return "Luật"
    if "quyết định" in title_l: return "Quyết định"
    if "nghị quyết" in title_l: return "Nghị quyết"
    if "pháp lệnh" in title_l: return "Pháp lệnh"
    if "công văn" in title_l: return "Công văn"
    if "thông báo" in title_l: return "Thông báo"
    return "Văn bản khác"


def parse_tvpl_html(html: str, url: str = "") -> Dict:
    """
    Parse raw HTML from thuvienphapluat.vn.
    Returns dict with: title, so_hieu, loai, co_quan_ban_hanh, ngay_ban_hanh,
                       content_html, content_text
    """
    soup = BeautifulSoup(html, "html.parser")

    # Extract title
    title = ""
    for sel in ["h1.doc-title", ".doc-title", "h1.title", ".fulltext-doc h1", "h1", "title"]:
        el = soup.select_one(sel)
        if el:
            title = el.get_text(strip=True)
            break

    # Extract main content HTML
    content_html = ""
    for sel in [
        "#toanvan", ".fulltext-doc", ".content1", "#content_vanban",
        ".doc-content", ".article-content", "article", ".entry-content"
    ]:
        el = soup.select_one(sel)
        if el:
            # Remove scripts, styles, nav elements
            for tag in el.select("script, style, nav, .nav, .toolbar, .share, .ads"):
                tag.decompose()
            content_html = str(el)
            break

    if not content_html:
        # Fallback: use body
        body = soup.find("body")
        if body:
            content_html = str(body)[:200000]

    # Strip HTML for content_text
    content_text = re.sub(r"<[^>]+>", " ", content_html)
    content_text = re.sub(r"\s+", " ", content_text).strip()

    # Extract metadata from common TVPL meta blocks
    so_hieu = _extract_so_hieu(title)
    loai = _extract_loai(title, url)
    co_quan = ""
    ngay_ban_hanh = None

    # Try structured metadata tables
    for row in soup.select("table.tttd tr, .doc-info tr, .van-ban-info tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True).lower()
            value = cells[1].get_text(strip=True)
            if "số ký hiệu" in label or "số hiệu" in label:
                so_hieu = so_hieu or value
            elif "cơ quan" in label or "ban hành" in label:
                co_quan = co_quan or value
            elif "ngày ban hành" in label or "ngày ký" in label:
                ngay_ban_hanh = ngay_ban_hanh or value

    return {
        "title": title,
        "so_hieu": so_hieu,
        "loai": loai,
        "co_quan_ban_hanh": co_quan,
        "ngay_ban_hanh": ngay_ban_hanh,
        "content_html": content_html,
        "content_text": content_text,
        "source_url": url,
    }


async def fetch_and_parse_tvpl(url: str, timeout: int = 30) -> Dict:
    """Fetch a TVPL URL and parse it. Returns parsed dict or error dict."""
    try:
        async with httpx.AsyncClient(
            headers=HEADERS, timeout=timeout, follow_redirects=True
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return parse_tvpl_html(resp.text, url)
    except Exception as e:
        logger.error(f"fetch_and_parse_tvpl failed for {url}: {e}")
        return {"error": str(e), "url": url, "title": "", "content_html": "", "content_text": ""}


async def crawl_via_crawlkit(url: str, api_key: str, base_url: str = "https://crawlkit.gpt4vn.com") -> Dict:
    """
    Crawl via CrawlKit API. Correct endpoint: POST /v1/scrape
    Falls back to direct fetch if CrawlKit fails.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(
                f"{base_url}/v1/scrape",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "url": url,
                    "formats": ["html", "markdown"],
                    "onlyMainContent": True,
                },
            )
            r.raise_for_status()
            data = r.json()
            html_content = data.get("html") or ""
            markdown = data.get("markdown") or data.get("content") or ""

            if html_content:
                result = parse_tvpl_html(html_content, url)
                return result
            elif markdown:
                return {
                    "title": data.get("metadata", {}).get("title", ""),
                    "so_hieu": "",
                    "loai": "",
                    "co_quan_ban_hanh": "",
                    "ngay_ban_hanh": None,
                    "content_html": f"<div class='markdown-content'>{markdown}</div>",
                    "content_text": markdown,
                    "source_url": url,
                }
    except Exception as e:
        logger.warning(f"CrawlKit failed for {url}: {e} — falling back to direct fetch")

    # Fallback to direct fetch
    return await fetch_and_parse_tvpl(url)
