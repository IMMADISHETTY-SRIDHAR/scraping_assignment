import logging
from datetime import datetime, timezone

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class QuotesScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://quotes.toscrape.com/", "Quotes to Scrape")

    def parse_page(self, soup, page_url):
        records = []

        for quote in soup.select("div.quote"):
            try:
                quote_element = quote.select_one("span.text")
                author_element = quote.select_one("small.author")

                records.append({
                    "source": self.source_name,
                    "source_url": page_url,
                    "name_or_title": quote_element.get_text(" ", strip=True) if quote_element else None,
                    "category": None,
                    "price_raw": None,
                    "rating_raw": None,
                    "author": author_element.get_text(" ", strip=True) if author_element else None,
                    "tags": [tag.get_text(" ", strip=True) for tag in quote.select("a.tag")],
                    "description": None,
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                })
            except Exception:
                logger.exception("[%s] Failed to parse one quote.", self.source_name)

        return records
