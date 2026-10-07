import logging
from datetime import datetime, timezone
from urllib.parse import urljoin

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BooksScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://books.toscrape.com/", "Books to Scrape")

    def parse_page(self, soup, page_url):
        records = []

        for book in soup.select("article.product_pod"):
            try:
                title_link = book.select_one("h3 > a[href]")
                price_element = book.select_one("p.price_color")
                rating_element = book.select_one("p.star-rating")

                records.append({
                    "source": self.source_name,
                    "source_url": (
                        urljoin(page_url, title_link["href"])
                        if title_link and title_link.get("href")
                        else page_url
                    ),
                    "name_or_title": title_link.get("title") if title_link else None,
                    "category": None,
                    "price_raw": price_element.get_text(" ", strip=True) if price_element else None,
                    "rating_raw": " ".join(rating_element.get("class", [])) if rating_element else None,
                    "author": None,
                    "tags": None,
                    "description": None,
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                })
            except Exception:
                logger.exception("[%s] Failed to parse one book.", self.source_name)

        return records
