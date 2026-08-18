"""Builds the daily report as a CSV attachment (domain, category, contact email,
source) plus a short email body, and sends it."""
from __future__ import annotations

import os
import csv
import io
import smtplib
import logging
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

logger = logging.getLogger(__name__)

CATEGORY_LABELS = {
    "streaming": "Streaming",
    "apk_mods": "APK / Mods",
    "converters_downloaders": "Converters / Downloaders",
    "file_sharing": "File Sharing",
}


def build_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["domain", "category", "contact_email", "source_url"])
    for r in rows:
        writer.writerow([
            r["domain"],
            CATEGORY_LABELS.get(r["category"], r["category"]),
            r.get("contact_email") or "",
            r["source_url"],
        ])
    return buf.getvalue()


def build_summary_html(rows: list[dict]) -> str:
    if not rows:
        return "<p>No new candidate domains found today.</p>"

    with_contact = sum(1 for r in rows if r.get("contact_email"))
    return (
        f"<h2>Publisher Hunter — New Leads for {date.today().isoformat()}</h2>"
        f"<p>{len(rows)} new domains found, {with_contact} with a contact email located.</p>"
        f"<p>Full list attached as CSV (domain, category, contact_email, source_url).</p>"
        f"<p style='color:#888;font-size:12px'>Contact emails are best-effort, pulled from "
        f"each site's public homepage/contact/about pages — not all sites list one. "
        f"Verify traffic and current ad stack before outreach.</p>"
    )


def send_email(rows: list[dict]) -> None:
    from_addr = os.environ["EMAIL_FROM"]
    to_addr = os.environ["EMAIL_TO"]
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_password = os.environ["EMAIL_APP_PASSWORD"]

    subject = f"Publisher Hunter: {len(rows)} new leads" if rows else "Publisher Hunter: no new leads today"

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(build_summary_html(rows), "html"))

    if rows:
        csv_content = build_csv(rows)
        attachment = MIMEApplication(csv_content.encode("utf-8"), Name="new_leads.csv")
        attachment["Content-Disposition"] = 'attachment; filename="new_leads.csv"'
        msg.attach(attachment)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(from_addr, smtp_password)
        server.sendmail(from_addr, [to_addr], msg.as_string())

    logger.info("Report emailed to %s (%d new leads)", to_addr, len(rows))
