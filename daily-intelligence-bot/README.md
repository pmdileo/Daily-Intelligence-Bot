# Daily Intelligence Briefing

A personal scheduled email, designed for **06:00 America/Chicago**. Runs on a computer or in GitHub Actions. It gathers your editable task list, upcoming events from a Google Calendar ICS feed, unread Gmail inbox *headers only*, neuroscience research from Europe PMC, news RSS, an indicative natural-gas futures quote, local weather, and optional AI recommendations. Links to primary or reported sources are included.

## Quick start on Windows / Mac / Linux

1. Install Python 3.12+ and Git.
2. Download/unzip this project. From the folder, run:
   ```sh
   python -m venv .venv
   ```
   Activate on Windows PowerShell: `.venv\\Scripts\\Activate.ps1`; on Mac/Linux: `source .venv/bin/activate`.
3. Run `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`. **Keep `.env` private and do not commit it.**
5. Edit `tasks.yaml` and `config.yaml`. Then run `python briefing.py`.
6. Open `preview.html` in a browser. In preview mode no email is sent, even if credentials are configured.

## Connect Gmail (MVP method)

The MVP uses Gmail SMTP to send and Gmail IMAP to check unread **subject/from/date** headers. It does not read message bodies, label messages, or mark them read. For personal Gmail accounts, you may use a Google **app password** if 2-Step Verification is enabled and Google offers app passwords for your account: https://support.google.com/mail/answer/185833 . Google recommends OAuth/"Sign in with Google" where possible; use OAuth for a longer-term production version. Some Workspace and Advanced Protection accounts cannot use app passwords. Never enter your ordinary Google password.

1. Set `GMAIL_USER=youraddress@gmail.com` in `.env`.
2. Set `GMAIL_APP_PASSWORD=` to your **app password**, not your normal password.
3. Set `EMAIL_TO=` to the inbox where you want the digest.
4. Confirm Gmail IMAP is available on your account. This bot uses `imap.gmail.com:993` and `smtp.gmail.com:465` (SSL).
5. To send a test locally, change `DRY_RUN=0`, then run `python briefing.py`. **This actually sends an email.** To go back to preview mode, set `DRY_RUN=1`.

## Connect Google Calendar

In Google Calendar on desktop, go to **Settings → [your calendar] → Integrate calendar → Secret address in iCal format**. Set `CALENDAR_ICS_URL` to that URL. Treat this address as a password: anyone with it may view calendar data. If your account doesn't offer it, calendar will simply say unavailable until an alternative OAuth approach is added. The bot expands recurring events using `recurring-ical-events`. Only the next 48 hours are included by default. Calendars containing sensitive information should use OAuth rather than distributing an ICS URL.

## Optional AI recommendations

Set `OPENAI_API_KEY` in `.env` to enable short AI suggestions. API usage may incur charges separate from your ChatGPT subscription. The bot sends **news headlines, research titles, and task titles** to the model, but **does not send inbox subjects or calendar events**. Avoid sensitive info in task titles if this is enabled. If no key is set, it still generates the full digest without AI recommendations. AI text is advisory, never a confirmed deadline.

## Automate with GitHub Actions

1. Create a **private** GitHub repository and upload the contents of this project (including `.github/workflows/daily.yml`). Do not upload `.env` or `preview.html`.
2. In the repository, go to **Settings → Secrets and variables → Actions → New repository secret**. Add `GMAIL_USER`, `GMAIL_APP_PASSWORD`, and `EMAIL_TO`. Optionally add `CALENDAR_ICS_URL` and `OPENAI_API_KEY`.
3. Open **Actions → Daily intelligence email → Run workflow** for a manual live test. This sends an email if the credentials are valid.
4. The workflow schedules at `0 6 * * *` with timezone `America/Chicago`. GitHub scheduled jobs can start late, fail, or be disabled after prolonged inactivity; this is **not a precision alarm clock**. Monitor Actions runs and notifications.
5. Important: a schedule runs from the default branch. GitHub Actions in private repositories may use billable minutes beyond plan allowances. Review GitHub's current pricing and policies.

## Data quality and limitations

- Headlines come from Google News RSS; publication timestamps may be missing, syndicated, or delayed. Sources are linked. This is discovery, **not** verified change detection.
- Research uses Europe PMC and a past-30-day search. Results depend on indexing coverage; no result does not imply no new paper exists.
- Official residency/AGFC links are **reference pages only**. This MVP does **not** verify that an application requirement or hunting rule has changed. Do not rely on it as a sole deadline monitor.
- The natural-gas ticker `NG=F` is an **indicative**, possibly delayed **futures** quote from an unofficial Yahoo chart endpoint; it may not resolve. It is not a confirmed live price or necessarily the contract you intend.
- Weather uses approximate Nimrod-area coordinates; adjust them in `config.yaml`. It is not specific to your precise hunting location.
- USGS link is a dashboard link, **not** a gauge-reading integration yet. Pick a verified station before adding quantitative river alerts. The new API is at https://api.waterdata.usgs.gov/ (old WaterServices is being retired in 2027).
- Pending email is only an unread-inbox shortlist; it does not reliably determine which messages require a reply.
- This build has no persistent deduplication or completed-task database. For version 2, add SQLite/cloud storage, confirmed-delta monitoring, OAuth credentials, and smart reply classification.
- All external sources and API keys can fail; sections degrade to clear unavailable messages rather than fabricated values.

## Customize

- `tasks.yaml`: priorities, categories, optional **confirmed** due dates. Remove tasks when done or set `done: true`.
- `config.yaml`: sources, PubMed-adjacent Europe PMC research queries, news topics, location, and official links.
- `briefing.py`: extend with sports scores, Google Tasks API, a real financial-market data provider, and USGS gauge readings.

## Privacy

Use a **private** GitHub repo. Store secrets only in GitHub Actions Secrets (or local `.env`, excluded from Git). A private ICS URL is sensitive. Don't paste credentials in ChatGPT. If a secret ever leaks, revoke it. The project does not persist your emails or event history.


## Sleeper fantasy football + basketball integration (v1.1)

The Sleeper official public API is **read-only**, needs **no Sleeper password or token**, and documents automatic discovery of NFL leagues and rosters: https://docs.sleeper.com/ . The current documentation does **not guarantee NBA league discovery**; the bot therefore imports basketball names via `fantasy_rosters.yaml` until an appropriate supported integration is validated.

### Football: connect your Sleeper username

1. In the Sleeper mobile app, open your profile and find your **username** (not your display nickname). Do not provide a password.
2. In a local `.env`, set `SLEEPER_USERNAME=your_username_here` and `SLEEPER_NFL_SEASON=2026`. Leave `SLEEPER_NFL_LEAGUE_IDS` empty to import all NFL leagues in that season. To restrict it, supply comma-separated league IDs such as `SLEEPER_NFL_LEAGUE_IDS=123456789012345678,987654321098765432` (these are fake examples, not real league IDs).
3. Run `python briefing.py`. It will discover your NFL leagues, identify the rosters you own using your user ID, map player IDs to names, and add your roster players plus a selection of player-specific news headlines to the briefing. If you do not see rosters, verify the username and season, or set specific league IDs.
4. In the **private GitHub repo**, configure **Settings → Secrets and variables → Actions → Variables**: add `SLEEPER_USERNAME` and optionally `SLEEPER_NFL_LEAGUE_IDS`. The schedule already specifies NFL season 2026. Update that yearly. If you want your username private from repository collaborators, move it to GitHub Secrets and change the workflow expression to `secrets.SLEEPER_USERNAME`.
5. Run the GitHub workflow manually to test after Gmail delivery credentials have been configured. Keep `DRY_RUN=1` locally until ready to send.

**Optional league link:** In Sleeper, open a league and use its share/invite feature to copy the league URL. The numerical `league_id` can often be found in its URL; alternatively, the public API's league lookup can be used. Only use your own leagues or information you're authorized to access.

### Basketball: import your actual roster

Open `fantasy_rosters.yaml` and replace its empty basketball list with your real current roster, e.g.:

```yaml
basketball:
  - league: "My dynasty basketball league"
    players:
      - name: "Actual Player Name"
        team: "WAS"
      - name: "Another Actual Player"
```

This example intentionally contains placeholders rather than assuming the user's roster. Roster news is searched for both NFL and NBA players (up to 5 names per sport per morning), and the news section adds Kansas City Chiefs, Razorbacks, college football, NFL, Washington Wizards, and NBA feeds independently. If you have more than five players, expand `max_players` in `fetch_fantasy_player_news` cautiously to avoid slow or throttled RSS requests.

**Limitations:** This is headline discovery rather than verified injury reports, advice, real-time player projections, or lineup optimization. It does not change your Sleeper lineup or fetch private account details. If it can't connect, it labels the data unavailable rather than showing fabricated roster information. Sleeper recommends not downloading the entire NFL player dictionary more than once per day; this bot retrieves it once per run. The scheduled workflow is once daily.

## Configured import for `phil64` (v1.2)

The daily workflow now uses `SLEEPER_USERNAME=phil64` as its nonsecret default, and continues to sync 2026 NFL rosters each morning when Sleeper is reachable. To inspect **actual league names and complete rosters** before enabling Gmail, run from the extracted project folder:

```powershell
python -m pip install -r requirements.txt
python import_sleeper.py --username phil64 --season 2026
```

This writes `roster-import/sleeper_rosters.md` (human-readable league/player roster) and `roster-import/sleeper_rosters.json` (machine-readable data). Both are excluded from git by default since they reflect your interests. You can re-run it whenever you want a fresh snapshot. The bot's normal `briefing.py` reads Sleeper live each run; it does not require this export to work.

If you would rather import from GitHub without installing Python, open **Actions → Import Sleeper rosters → Run workflow**. After the run, download the **sleeper-rosters-2026** artifact from the workflow's run summary to see the league report and JSON. This action does not send email or modify Sleeper.

**Account data not yet verified:** The live Sleeper API was inaccessible from the assistant's development environment, so neither the actual league names nor the player lists have been verified here. The first successful import will populate them automatically. The basketball roster is still manual via `fantasy_rosters.yaml` because officially documented league discovery currently supports NFL only.
