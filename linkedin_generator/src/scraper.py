"""Extração de texto limpo a partir de URLs."""

from __future__ import annotations

from typing import List
import trafilatura
from config import SCRAPE_TIMEOUT, MAX_TEXT_PER_URL


def scrape_url(url: str) -> dict:
    """
    Extrai texto limpo de uma URL.
    Usa trafilatura como primary; newspaper3k como fallback.
    Retorna dict com keys: url, title, text, success, error.
    """
    url = url.strip()
    if not url:
        return {"url": url, "title": "", "text": "", "success": False, "error": "URL vazia"}

    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            result = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
                favor_recall=True,
            )
            if result and len(result.strip()) > 100:
                metadata = trafilatura.extract_metadata(downloaded)
                title = metadata.title if metadata and metadata.title else url
                return {
                    "url": url,
                    "title": title,
                    "text": result[:MAX_TEXT_PER_URL],
                    "success": True,
                    "error": None,
                }
    except Exception:
        pass

    # Fallback: newspaper3k
    try:
        from newspaper import Article
        article = Article(url, request_timeout=SCRAPE_TIMEOUT)
        article.download()
        article.parse()
        text = article.text.strip()
        if text and len(text) > 100:
            return {
                "url": url,
                "title": article.title or url,
                "text": text[:MAX_TEXT_PER_URL],
                "success": True,
                "error": None,
            }
    except Exception as e:
        return {
            "url": url,
            "title": "",
            "text": "",
            "success": False,
            "error": str(e)[:200],
        }

    return {
        "url": url,
        "title": "",
        "text": "",
        "success": False,
        "error": "Não foi possível extrair conteúdo da URL.",
    }


def scrape_urls(urls: List[str]) -> List[dict]:
    """Scraping sequencial de múltiplas URLs. Retorna lista de resultados."""
    return [scrape_url(u) for u in urls if u.strip()]
