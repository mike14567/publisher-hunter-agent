"""Daily entrypoint: scrape sources, diff against seen state, email new leads."""
from __future__ import annotations

import logging
from pathlib import Path

import yaml

from src.scraper import fetch_candidates
from src.state import SeenStore
from src.reporter import build_html, send_email

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent / "config.yaml"
STATE_PATH = Path(__file__).parent / "data" / "seen_domains.json"


def main() -> None:
    config = yaml.safe_load(CONFIG_PATH.read_text())
    exclude = set(config.get("exclude_domains", []))
    store = SeenStore(STATE_PATH)

    new_candidates = []
    for category, urls in config["sources"].items():
        for source_url in urls:
            for candidate in fetch_candidates(category, source_url, exclude):
                if store.is_new(candidate.domain):
                    new_candidates.append(candidate)
                    store.mark_seen(candidate.domain)

    logger.info("Found %d new candidate domains", len(new_candidates))

    html = build_html(new_candidates)
    subject = f"Publisher Hunter: {len(new_candidates)} new leads" if new_candidates else "Publisher Hunter: no new leads today"
    send_email(html, subject)

    store.save()


if __name__ == "__main__":
    main()
