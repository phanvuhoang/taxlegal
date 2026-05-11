"""
Tax Legal Document Crawler — CrawlKit powered.
Crawls Vietnamese legal websites for tax laws and indexes them into the legalai DB.
"""
import os
import re
import logging
import uuid
from typing import Optional, List, Dict
from sqlalchemy import text
from .database import LegalAISession
from .embedder import get_embedder

logger = logging.getLogger(__name__)

# Tax-focused legal sources
TAX_SOURCES = {
    "thuvienphapluat_thue": {
        "name": "Thư Viện Pháp Luật — Thuế",
        "urls": [
            "https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/",
            "https://thuvienphapluat.vn/van-ban/Ke-toan-Kiem-toan/",
        ],
        "domains": ["thue"],
    },
    "vbpl_thue": {
        "name": "VBPL — Chính sách thuế",
        "urls": ["https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx"],
        "domains": ["thue"],
    },
}

# Priority tax document URLs
PRIORITY_TAX_URLS = [
    # Thuế TNDN (CIT)
    "https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Luat-thue-thu-nhap-doanh-nghiep-sua-doi-2013-197354.aspx",
    "https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Nghi-dinh-218-2013-ND-CP-Huong-dan-Luat-Thue-thu-nhap-doanh-nghiep-216453.aspx",
    # Thuế GTGT (VAT)
    "https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Luat-Thue-gia-tri-gia-tang-sua-doi-2013-197303.aspx",
    # Thuế TNCN (PIT)
    "https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Luat-thue-thu-nhap-ca-nhan-sua-doi-2012-150307.aspx",
    # Luật Quản lý thuế
    "https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Luat-Quan-ly-thue-38-2019-QH14-381916.aspx",
    # Thuế nhà thầu
    "https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Thong-tu-103-2014-TT-BTC-thue-nha-thau-243111.aspx",
]


class TaxCrawler:
    def __init__(self, crawlkit_api_key: Optional[str] = None):
        self.api_key = crawlkit_api_key or os.getenv("CRAWLKIT_API_KEY", "")
        self.base_url = "https://crawlkit.gpt4vn.com"
        self.enabled = bool(self.api_key)

        if not self.enabled:
            logger.warning("CRAWLKIT_API_KEY not set — crawling disabled")

    async def crawl_url(self, url: str) -> Dict:
        """Crawl a single URL using CrawlKit API."""
        if not self.enabled:
            return {"success": False, "error": "CrawlKit not configured"}

        import httpx

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(
                    f"{self.base_url}/v1/scrape",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
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
                return {
                    "success": True,
                    "content": data.get("html") or data.get("markdown") or data.get("content", ""),
                    "title": data.get("title") or data.get("metadata", {}).get("title", ""),
                    "url": url,
                }
        except Exception as e:
            logger.error(f"CrawlKit error for {url}: {e}")
            return {"success": False, "error": str(e), "url": url}

    def extract_law_metadata(self, title: str, content: str) -> Dict:
        """Extract law_number, issuer, type from title/content heuristics."""
        metadata: Dict = {
            "law_type": "other",
            "issuer": "Quốc hội",
            "domains": ["thue"],
            "law_number": "",
        }

        title_lower = title.lower()

        # Law type detection
        if "luật" in title_lower:
            metadata["law_type"] = "luat"
            metadata["issuer"] = "Quốc hội"
        elif "nghị định" in title_lower or "nghi dinh" in title_lower:
            metadata["law_type"] = "nghi_dinh"
            metadata["issuer"] = "Chính phủ"
        elif "thông tư" in title_lower or "thong tu" in title_lower:
            metadata["law_type"] = "thong_tu"
            metadata["issuer"] = "Bộ Tài chính"
        elif "quyết định" in title_lower:
            metadata["law_type"] = "quyet_dinh"

        # Law number extraction
        patterns = [
            r"(\d+/\d{4}/(?:QH|NĐ-CP|TT-BTC|TT-NHNN|QĐ-TTg|QĐ-BTC)[\w-]*)",
            r"(\d+/\d{4}/\w+)",
            r"số\s+(\d+[\w/.-]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, title + " " + content[:200], re.IGNORECASE)
            if match:
                metadata["law_number"] = match.group(1)
                break

        # Domain detection
        domains = ["thue"]
        if any(k in title_lower for k in ["tndn", "thu nhap doanh nghiep", "cit"]):
            domains.append("cit")
        if any(k in title_lower for k in ["gtgt", "gia tri gia tang", "vat"]):
            domains.append("vat")
        if any(k in title_lower for k in ["tncn", "thu nhap ca nhan", "pit"]):
            domains.append("pit")
        if any(k in title_lower for k in ["nha thau", "fct"]):
            domains.append("fct")
        if any(k in title_lower for k in ["tieu thu dac biet", "sst", "ttdb"]):
            domains.append("sst")
        metadata["domains"] = domains

        return metadata

    def chunk_law_text(self, content: str, law_title: str) -> List[Dict]:
        """Split law text into chunks by article/clause."""
        chunks: List[Dict] = []

        # Split by "Điều X." pattern
        article_pattern = re.compile(
            r"(Điều\s+\d+[a-z]?\..*?)(?=Điều\s+\d+[a-z]?\.|\Z)",
            re.DOTALL | re.IGNORECASE,
        )
        articles = article_pattern.findall(content)

        if not articles:
            # Fallback: split by paragraphs, max ~1000 chars
            paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 50]
            for i, para in enumerate(paragraphs):
                if len(para) > 1500:
                    for j in range(0, len(para), 1000):
                        chunk = para[j : j + 1000]
                        if chunk.strip():
                            chunks.append(
                                {
                                    "content": chunk,
                                    "article": None,
                                    "clause": None,
                                    "parent_context": f"Đoạn {i + 1}",
                                }
                            )
                else:
                    chunks.append(
                        {
                            "content": para,
                            "article": None,
                            "clause": None,
                            "parent_context": None,
                        }
                    )
        else:
            for article_text in articles:
                lines = article_text.strip().split("\n")
                article_header = lines[0] if lines else ""
                article_num_match = re.match(r"(Điều\s+\d+[a-z]?)", article_header, re.IGNORECASE)
                article_num = article_num_match.group(1) if article_num_match else None

                # Split article into clauses (khoản)
                clause_pattern = re.compile(r"(\d+\.\s.*?)(?=\d+\.\s|\Z)", re.DOTALL)
                clauses = clause_pattern.findall(article_text)

                if clauses and len(clauses) > 1:
                    for clause_text in clauses:
                        if len(clause_text.strip()) > 30:
                            clause_num_match = re.match(r"(\d+)\.", clause_text.strip())
                            chunks.append(
                                {
                                    "content": clause_text.strip(),
                                    "article": article_num,
                                    "clause": (
                                        f"Khoản {clause_num_match.group(1)}"
                                        if clause_num_match
                                        else None
                                    ),
                                    "parent_context": article_header[:200],
                                }
                            )
                else:
                    if len(article_text.strip()) > 30:
                        chunks.append(
                            {
                                "content": article_text.strip(),
                                "article": article_num,
                                "clause": None,
                                "parent_context": article_header[:200],
                            }
                        )

        return chunks

    async def crawl_and_index(self, url: str, job_id: Optional[str] = None) -> Dict:
        """Crawl URL, chunk, embed and store in legalai DB."""
        result = await self.crawl_url(url)
        if not result["success"]:
            return result

        content = result["content"]
        title = result["title"] or url
        metadata = self.extract_law_metadata(title, content)

        if not metadata["law_number"]:
            metadata["law_number"] = url.split("/")[-1][:100]

        embedder = get_embedder()

        async with LegalAISession() as session:
            # Skip if already indexed
            existing = await session.execute(
                text("SELECT id FROM law_documents WHERE source_url = :url"),
                {"url": url},
            )
            existing_row = existing.fetchone()

            if existing_row:
                law_id = str(existing_row[0])
                logger.info(f"Law already indexed: {url}")
            else:
                law_id = str(uuid.uuid4())
                await session.execute(
                    text("""
                        INSERT INTO law_documents
                            (id, title, law_number, law_type, issuer, domains,
                             full_text, source_url, crawled_at)
                        VALUES
                            (:id, :title, :law_number, :law_type, :issuer, :domains,
                             :full_text, :source_url, NOW())
                    """),
                    {
                        "id": law_id,
                        "title": title,
                        "law_number": metadata["law_number"],
                        "law_type": metadata["law_type"],
                        "issuer": metadata["issuer"],
                        "domains": metadata["domains"],
                        "full_text": content[:50000],
                        "source_url": url,
                    },
                )

            # Chunk and embed
            chunks = self.chunk_law_text(content, title)
            chunk_texts = [c["content"] for c in chunks]
            embeddings = (
                await embedder.embed_batch(chunk_texts)
                if embedder.available
                else [None] * len(chunks)
            )

            chunk_count = 0
            for chunk, embedding in zip(chunks, embeddings):
                chunk_id = str(uuid.uuid4())
                embedding_val = str(embedding) if embedding else None
                await session.execute(
                    text("""
                        INSERT INTO law_chunks
                            (id, law_id, article, clause, content, parent_context,
                             embedding, domains)
                        VALUES
                            (:id, :law_id, :article, :clause, :content, :parent_context,
                             :embedding::vector, :domains)
                        ON CONFLICT DO NOTHING
                    """),
                    {
                        "id": chunk_id,
                        "law_id": law_id,
                        "article": chunk.get("article"),
                        "clause": chunk.get("clause"),
                        "content": chunk["content"],
                        "parent_context": chunk.get("parent_context"),
                        "embedding": embedding_val,
                        "domains": metadata["domains"],
                    },
                )
                chunk_count += 1

            await session.commit()

        return {
            "success": True,
            "law_id": law_id,
            "title": title,
            "law_number": metadata["law_number"],
            "chunks_indexed": chunk_count,
            "url": url,
        }

    async def crawl_batch(self, urls: List[str]) -> List[Dict]:
        """Crawl a list of URLs sequentially."""
        results = []
        for url in urls:
            result = await self.crawl_and_index(url)
            results.append(result)
        return results
