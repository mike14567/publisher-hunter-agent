"""Best-effort contact email discovery: checks a domain's homepage and common
contact/about pages for a publicly listed email address. This only reads
public HTML — no login, no contact forms submitted, no guessing/brute force."""
from __future__ import annotations

import re
import logging

import httpx

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (compatible; PublisherHunterBot/1.0; +mailto:you@example.com)"

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Emails that show up constantly but are useless for outreach (image CDNs,
# placeholder addresses, etc.)
JUNK_PATTERNS = ("example.com", "sentry.io", "wixpress.com", ".png", ".jpg", ".gif")

CANDIDATE_PATHS = ("/", "/contact", "/contact-us", "/about", "/about-us")


def _clean_emails(text: str) -> set[str]:
    found = set(EMAIL_RE.findall(text))
    return {e for e in found if not any(j in e.lower() for j in JUNK_PATTERNS)}


def find_contact_email(domain: str) -> str | None:
    """Tries a few common pages on the domain and returns the first email found, if any."""
    for path in CANDIDATE_PATHS:
        url = f"https://{domain}{path}"
        try:
            resp = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=10, follow_redirects=True)
            if resp.status_code != 200:
                continue
            emails = _clean_emails(resp.text)
            if emails:
                return sorted(emails)[0]
        except httpx.HTTPError as e:
            logger.debug("Contact lookup failed for %s%s: %s", domain, path, e)
            continue
    return None
