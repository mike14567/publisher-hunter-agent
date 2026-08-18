"""Builds and sends the daily HTML email report of newly discovered domains."""
from __future__ import annotations

import os
import smtplib
import logging
from collections import defaultdict
from datetime import date
from email.mime.text import MIMEText

from .scraper import Candidate

logger = logging.getLogger(__name__)

CATEGORY_LABELS = {
    "streaming": "🎬 Streaming",
    "apk_mods": "📱 APK / Mods",
    "converters_downloaders": "🔄 Converters / Downloaders",
    "file_sharing": "📁 File Sharing",
}


def build_html(new_candidates: list[Candidate]) -> str:
    if not new_candidates:
        return "<p>No new candidate domains found today.</p>"

    by_category: dict[str, list[Candidate]] = defaultdict(list)
    for c in new_candidates:
        by_category[c.category].append(c)

    parts = [f"<h2>Publisher Hunter — New Leads for {date.today().isoformat()}</h2>"]
    for category, items in by_category.items():
        label = CATEGORY_LABELS.get(category, category)
        parts.append(f"<h3>{label} ({len(items)})</h3><ul>")
        for c in items:
            parts.append(
                f'<li><a href="https://{c.domain}">{c.domain}</a> '
                f'<span style="color:#888">(via {c.source_url})</span></li>'
            )
        parts.append("</ul>")

    parts.append(
        "<p style='color:#888;font-size:12px'>Verify traffic and current ad stack "
        "before outreach — this is a raw discovery feed, not a qualified list.</p>"
    )
    return "\n".join(parts)


def send_email(html_body: str, subject: str) -> None:
    from_addr = os.environ["EMAIL_FROM"]
    to_addr = os.environ["EMAIL_TO"]
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_password = os.environ["EMAIL_APP_PASSWORD"]

    msg = MIMEText(html_body, "html")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(from_addr, smtp_password)
        server.sendmail(from_addr, [to_addr], msg.as_string())

    logger.info("Report emailed to %s", to_addr)
