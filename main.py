"""Daily entrypoint: scrape sources, diff against seen state, look up contact
emails for new domains, and email a CSV report."""
from __future__ import annotations

import logging
from pathlib import Path

import yaml

from src.scraper import fetch_candidates
from src.state import SeenStore
from src.contact_finder import find_contact_email
from src.reporter import send_email

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent / "config.yaml"
STATE_PATH = Path(__file__).parent / "data" / "seen_domains.json"


def main() -> None:
    config = yaml.safe_load(CONFIG_PATH.read_text())
    exclude = set(config.get("exclude_domains", []))
    store = SeenStore(STATE_PATH)

    new_rows: list[dict] = []
    for category, urls in config["sources"].items():
        for source_url in urls:
            for candidate in fetch_candidates(category, source_url, exclude):
                if not store.is_new(candidate.domain):
                    continue
                store.mark_seen(candidate.domain)

                contact = find_contact_email(candidate.domain)
                new_rows.append({
                    "domain": candidate.domain,
                    "category": candidate.category,
                    "source_url": candidate.source_url,
                    "contact_email": contact,
                })
                logger.info("New: %s (contact: %s)", candidate.domain, contact or "none found")

    logger.info("Found %d new candidate domains", len(new_rows))
    send_email(new_rows)
    store.save()


if __name__ == "__main__":
    main()
