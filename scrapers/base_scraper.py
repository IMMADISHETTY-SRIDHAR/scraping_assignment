from abc import ABC, abstractmethod
import logging
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    def __init__(self, start_url, source_name, delay=0.5, timeout=15):
        self.start_url = start_url
        self.source_name = source_name
        self.delay = delay
        self.timeout = timeout
        self.session = self._create_session()

    @staticmethod
    def _create_session():
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; ETL-Scraper/1.0)"
        })
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(["GET"]),
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def fetch(self, url):
        logger.info("[%s] Requesting: %s", self.source_name, url)
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response
        except requests.RequestException as exc:
            logger.error("[%s] Request failed: %s | %s", self.source_name, url, exc)
            return None

    def scrape(self):
        records = []
        current_url = self.start_url
        page_number = 1
        pages_scraped = 0

        while current_url:
            logger.info("[%s] Page %d: %s", self.source_name, page_number, current_url)
            response = self.fetch(current_url)
            if response is None:
                logger.error("[%s] Stopping after failed page %d.", self.source_name, page_number)
                break

            pages_scraped += 1
            soup = BeautifulSoup(response.text, "lxml")

            try:
                records.extend(self.parse_page(soup, current_url))
            except Exception:
                logger.exception("[%s] Page %d parsing failed; continuing.", self.source_name, page_number)

            next_link = soup.select_one("li.next > a[href]")
            if not next_link:
                break

            current_url = urljoin(current_url, next_link["href"])
            page_number += 1
            time.sleep(self.delay)

        return records, pages_scraped

    def close(self):
        self.session.close()

    @abstractmethod
    def parse_page(self, soup, page_url):
        raise NotImplementedError
