"""Fetches source listicle pages and extracts outbound domains as lead candidates."""
from __future__ import annotations

import re
import logging
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (compatible; PublisherHunterBot/1.0; +mailto:you@example.com)"


@dataclass(frozen=True)
class Candidate:
    domain: str
    source_url: str
    category: str


def _extract_domains(html: str, base_url: str) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    domains: set[str] = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.startswith("http"):
            continue
        netloc = urlparse(href).netloc.lower()
        netloc = re.sub(r"^www\.", "", netloc)
        if netloc:
            domains.add(netloc)

    base_domain = re.sub(r"^www\.", "", urlparse(base_url).netloc.lower())
    domains.discard(base_domain)
    return domains


def fetch_candidates(category: str, source_url: str, exclude: set[str]) -> list[Candidate]:
    try:
        resp = httpx.get(source_url, headers={"User-Agent": USER_AGENT}, timeout=20, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.warning("Failed to fetch %s: %s", source_url, e)
        return []

    domains = _extract_domains(resp.text, source_url)
    domains = {d for d in domains if not any(d.endswith(ex) for ex in exclude)}

    return [Candidate(domain=d, source_url=source_url, category=category) for d in sorted(domains)]
