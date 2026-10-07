import re
from urllib.parse import urljoin, urlparse

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def clean_text(value):
    if value is None:
        return None
    text = str(value).replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def strip_quotes(value):
    text = clean_text(value)
    if not text:
        return None
    while len(text) >= 2 and text[0] in '"“”' and text[-1] in '"“”':
        text = text[1:-1].strip()
    return text or None


def clean_price(value):
    text = clean_text(value)
    if not text:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
    return float(match.group()) if match else None


def clean_rating(value):
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = int(value)
        return number if number == value else None
    text = clean_text(value)
    if not text:
        return None
    for word, number in RATING_MAP.items():
        if word in text.lower().split():
            return number
    match = re.search(r"\b([1-5])\b", text)
    return int(match.group(1)) if match else None


def clean_tags(value):
    if value is None:
        return None
    values = value.split(";") if isinstance(value, str) else value
    cleaned = {clean_text(item).lower() for item in values if clean_text(item)}
    return ";".join(sorted(cleaned)) or None


def normalize_url(value, base_url=None):
    text = clean_text(value)
    if not text:
        return None
    if base_url:
        text = urljoin(base_url, text)
    parsed = urlparse(text)
    return text if parsed.scheme in {"http", "https"} and parsed.netloc else None


def clean_record(raw):
    return {
        "source": clean_text(raw.get("source")),
        "source_url": normalize_url(raw.get("source_url")),
        "name_or_title": strip_quotes(raw.get("name_or_title")),
        "category": clean_text(raw.get("category")),
        "price": clean_price(raw.get("price_raw", raw.get("price"))),
        "rating": clean_rating(raw.get("rating_raw", raw.get("rating"))),
        "author": clean_text(raw.get("author")),
        "tags": clean_tags(raw.get("tags")),
        "description": clean_text(raw.get("description")),
        "scraped_at": clean_text(raw.get("scraped_at")),
    }
