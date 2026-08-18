# Publisher Hunter Agent

Daily agent that scrapes "best sites" listicle pages for streaming, APK/mod,
converter, and file-sharing niches, and emails you only the domains it
**hasn't seen before** — so your inbox doesn't repeat the same 40 sites daily.

## How it works
1. `config.yaml` lists source pages to re-scan per category.
2. Each run, it pulls every outbound link from those pages and extracts domains.
3. Domains already in `data/seen_domains.json` are skipped; new ones are emailed and recorded.
4. GitHub Actions runs this daily and commits the updated state file back to the repo.

## Setup (15 min)

1. **Create a new GitHub repo** and push this folder to it.

2. **Get a Gmail App Password** (don't use your real password):
   - Google Account → Security → 2-Step Verification → App Passwords
   - Generate one for "Mail" — copy the 16-character code.

3. **Add repo secrets** (Settings → Secrets and variables → Actions → New repository secret):
   - `EMAIL_FROM` — the Gmail address sending the report
   - `EMAIL_TO` — your inbox (can be the same address)
   - `EMAIL_APP_PASSWORD` — the app password from step 2

4. **Enable Actions** if prompted (Actions tab → "I understand, enable").

5. Done — it runs daily at 07:00 UTC. To test immediately: Actions tab →
   "Daily Publisher Hunt" → "Run workflow".

## Tuning
- Add/remove listicle URLs in `config.yaml` under `sources:` any time.
- Add noisy domains (ad networks, social platforms, etc.) to `exclude_domains:`.
- Change the cron schedule in `.github/workflows/daily.yml` (it's UTC).

## What this does NOT do
- Does not verify traffic, ad stack, or brand-safety — it's a raw discovery
  feed. Cross-check flagged domains against SimilarWeb/Ahrefs before outreach.
- Does not send outreach emails to publishers — only sends *you* the daily
  digest. Any contact with publishers stays a manual, human step.
- Scrapes only public listicle pages via normal HTTP GET — no login bypass,
  no CAPTCHA solving, respects each site's public HTML as rendered.

## Local test run
```bash
pip install -r requirements.txt
export EMAIL_FROM="you@gmail.com"
export EMAIL_TO="you@gmail.com"
export EMAIL_APP_PASSWORD="xxxxxxxxxxxxxxxx"
python main.py
```
