# Python Web Scraping ETL Assignment

Scrapes Books to Scrape and Quotes to Scrape, then cleans, validates, deduplicates, consolidates and saves the results.

## Setup

Recommended Python: 3.10-3.12

```bash
python -m pip install requests beautifulsoup4 lxml pytest
python -m pip freeze > requirements.txt
```

## Run

```bash
python -m pytest -q
python main.py
```

## Output

- output/final_dataset.csv
- output/summary_report.json
- logs/scraper.log

Pagination uses the dynamic `li.next > a` link. Requests include retries for 429, 500, 502, 503 and 504 and approximately 0.5 seconds between pages.

Book category/description are left empty because the listing page does not provide them; this avoids extra detail-page requests.

See AI_USAGE.md for AI-assisted development notes.
