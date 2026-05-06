"""
Gamma API client for slide generation from writing content.
Uses GAMMA_API_KEY env var.
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

GAMMA_API_KEY = os.getenv("GAMMA_API_KEY", "")
GAMMA_API_BASE = "https://api.gamma.app/v1"


async def create_gamma_slides(title: str, content: str, language: str = "vi") -> Optional[str]:
    """
    Send content to Gamma API to create a slide deck.
    Returns the Gamma presentation URL or None on failure.

    NOTE: Gamma's API endpoint for programmatic creation.
    If GAMMA_API_KEY is not set, returns None gracefully.
    """
    if not GAMMA_API_KEY:
        logger.warning("GAMMA_API_KEY not set — skipping Gamma slide creation")
        return None

    try:
        import httpx

        # Gamma API — create presentation from markdown
        payload = {
            "title": title,
            "content": content,
            "language": language,
            "theme": "professional",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{GAMMA_API_BASE}/presentations",
                json=payload,
                headers={
                    "Authorization": f"Bearer {GAMMA_API_KEY}",
                    "Content-Type": "application/json",
                }
            )

            if response.status_code in (200, 201):
                data = response.json()
                url = data.get("url") or data.get("share_url") or data.get("id")
                if url and not url.startswith("http"):
                    url = f"https://gamma.app/docs/{url}"
                logger.info(f"Gamma presentation created: {url}")
                return url
            else:
                logger.warning(f"Gamma API error {response.status_code}: {response.text}")
                return None

    except Exception as e:
        logger.warning(f"Gamma API call failed: {e}")
        return None
