# Your whole pipeline. One sheet.

Google Sheets CRM/transaction template for individual commission-based residential real estate agents.

**Buy:** https://lachieverse20.gumroad.com/l/ngskw

Landing page is `index.html` (GitHub Pages, deploy from root).

The sold `.xlsx` and the private Control Hub are **not** in this repo.

## Weekly Content Ideas (GitHub Actions)

Workflow: `.github/workflows/weekly-content-ideas.yml`

Repo secrets (Settings → Secrets and variables → Actions):

- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `CONTROL_HUB_SHEET_ID`

Leave the workflow unused until those four secrets exist. Do not scrape Zillow, Realtor.com, or MLS data.
