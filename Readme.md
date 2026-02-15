# Table Extractor

A CLI tool that extracts HTML tables from any URL (or local file) and saves them to an Excel workbook — one sheet per table. It uses **Playwright** with a real Chrome browser to handle JavaScript-heavy pages and **automatic Cloudflare bypass**.

## Features

- **URL & local file support** — scrape a live webpage or parse a local `.html` file
- **Cloudflare handling** — auto-detects challenges; retries in visible mode for manual solve if needed
- **Smart caching** — fetched pages are cached locally to avoid redundant requests
- **Multi-table export** — all tables are saved as separate sheets in a single `.xlsx` file
- **Stealth mode** — optional `playwright-stealth` integration to reduce bot detection

## Quick Start

```bash
# 1. Clone
git clone https://github.com/swrno/table_extractactor && cd table_extractactor

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Run
python3 main.py --url "https://example.com/page-with-tables"
```

## Usage

```
python3 main.py [OPTIONS]
```

| Flag | Description |
|---|---|
| `--url URL` | URL to scrape tables from |
| `--file PATH` | Local HTML file to extract tables from |
| `--no-headless` | Run the browser in visible mode (useful for Cloudflare challenges) |
| `--force-refresh` | Ignore cached content and fetch fresh HTML |

### Examples

```bash
# Extract tables from a URL
python3 main.py --url "https://fbref.com/en/squads/5bb5024a/2022/Netherlands-Men-Stats"

# Use visible browser to handle Cloudflare
python3 main.py --no-headless --url "https://fbref.com/en/squads/5bb5024a/2022/Netherlands-Men-Stats"

# Extract from a local HTML file
python3 main.py --file page.html

# Force a fresh fetch (skip cache)
python3 main.py --force-refresh --url "https://example.com"
```

## Project Structure

```
├── main.py          # CLI entry point & orchestration
├── fetcher.py       # Playwright-based page fetcher with Cloudflare handling
├── extractor.py     # Table extraction & Excel export via pandas
├── utils.py         # Caching & filename utilities
├── cache/           # Cached HTML pages
└── outputs/         # Generated .xlsx files
```

## Dependencies

- [Playwright](https://playwright.dev/python/) — browser automation
- [pandas](https://pandas.pydata.org/) — table parsing (`pd.read_html`) & Excel export
- [openpyxl](https://openpyxl.readthedocs.io/) — Excel file writing
- [playwright-stealth](https://pypi.org/project/playwright-stealth/) *(optional)* — anti-detection patches# table_extractactor
