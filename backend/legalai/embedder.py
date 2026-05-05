"""
Async embedder using OpenAI text-embedding-3-small (1024 dims).
"""
import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = "text-embedding-3-small"
        self.dimensions = 1024
        self.base_url = "https://api.openai.com/v1"

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def embed(self, text: str) -> Optional[list]:
        """Embed a single text string."""
        if not self.available:
            return None
        results = await self.embed_batch([text])
        return results[0]

    async def embed_batch(self, texts: list, batch_size: int = 50) -> list:
        """Embed a batch of texts, returning a list of embedding vectors."""
        if not self.available:
            return [None] * len(texts)

        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{self.base_url}/embeddings",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "input": batch,
                        "dimensions": self.dimensions,
                    },
                    timeout=60.0,
                )
                r.raise_for_status()
                data = r.json()
                results.extend([item["embedding"] for item in data["data"]])
        return results


_embedder: Optional[Embedder] = None


def get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder
