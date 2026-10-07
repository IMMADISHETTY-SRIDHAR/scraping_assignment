from urllib.parse import urlparse

VALID_SOURCES = {"Books to Scrape", "Quotes to Scrape"}


def validate_record(record):
    errors = []

    if record.get("source") not in VALID_SOURCES:
        errors.append("invalid_source")

    if not record.get("name_or_title"):
        errors.append("missing_name_or_title")

    url = record.get("source_url")
    parsed = urlparse(url) if isinstance(url, str) else None
    if not parsed or parsed.scheme not in {"http", "https"} or not parsed.netloc:
        errors.append("invalid_source_url")

    price = record.get("price")
    if price is not None and (
        isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0
    ):
        errors.append("invalid_price")

    rating = record.get("rating")
    if rating is not None and (
        isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 5
    ):
        errors.append("invalid_rating")

    return errors
