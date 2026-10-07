import csv
import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
CSV_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary_report.json"
LOG_PATH = LOG_DIR / "scraper.log"

FIELDNAMES = [
    "source", "source_url", "name_or_title", "category", "price",
    "rating", "author", "tags", "description", "scraped_at"
]


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def write_csv(records):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=FIELDNAMES, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(records)


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    started = datetime.now(timezone.utc)
    timer = time.perf_counter()

    scrapers = [BooksScraper(), QuotesScraper()]
    raw_by_source = {}
    source_stats = {}

    for scraper in scrapers:
        source = scraper.source_name
        try:
            records, pages = scraper.scrape()
        except Exception:
            logger.exception("[%s] Unexpected scraper failure.", source)
            records, pages = [], 0
        finally:
            scraper.close()

        raw_by_source[source] = records
        source_stats[source] = {
            "pages_scraped": pages,
            "raw_records": len(records),
            "records_after_cleaning": 0,
            "rejected_records": 0,
            "rejected_by_reason": {},
            "duplicates_detected": 0,
        }

    valid_records = []

    for source, raw_records in raw_by_source.items():
        stats = source_stats[source]

        for raw in raw_records:
            try:
                cleaned = clean_record(raw)
                stats["records_after_cleaning"] += 1
            except Exception:
                logger.exception("[%s] Cleaning failed.", source)
                stats["rejected_records"] += 1
                stats["rejected_by_reason"]["cleaning_error"] = (
                    stats["rejected_by_reason"].get("cleaning_error", 0) + 1
                )
                continue

            errors = validate_record(cleaned)

            if errors:
                stats["rejected_records"] += 1
                for reason in errors:
                    stats["rejected_by_reason"][reason] = (
                        stats["rejected_by_reason"].get(reason, 0) + 1
                    )
                logger.warning(
                    "[%s] Rejected record: %s | %s",
                    source,
                    cleaned.get("name_or_title"),
                    ", ".join(errors),
                )
            else:
                valid_records.append(cleaned)

    unique_records, duplicate_records = find_duplicates(valid_records)

    for source, count in Counter(r["source"] for r in duplicate_records).items():
        source_stats[source]["duplicates_detected"] = count

    write_csv(unique_records)

    finished = datetime.now(timezone.utc)
    total_raw = sum(s["raw_records"] for s in source_stats.values())
    total_cleaned = sum(s["records_after_cleaning"] for s in source_stats.values())
    total_rejected = sum(s["rejected_records"] for s in source_stats.values())

    summary = {
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "duration_seconds": round(time.perf_counter() - timer, 3),
        "sources": source_stats,
        "collected_per_source": {
            source: stats["raw_records"] for source, stats in source_stats.items()
        },
        "cleaned_per_source": {
            source: stats["records_after_cleaning"]
            for source, stats in source_stats.items()
        },
        "rejected_total": total_rejected,
        "duplicates_detected": len(duplicate_records),
        "final_record_count": len(unique_records),
        "reconciliation": {
            "raw_records": total_raw,
            "rejected_records": total_rejected,
            "duplicates": len(duplicate_records),
            "expected_final": total_raw - total_rejected - len(duplicate_records),
            "actual_final": len(unique_records),
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with SUMMARY_PATH.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    logger.info("Pipeline completed. Final records: %d", len(unique_records))
    logger.info("CSV: %s", CSV_PATH)
    logger.info("Summary: %s", SUMMARY_PATH)


if __name__ == "__main__":
    main()
