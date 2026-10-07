import hashlib
import re


def _normalize_identity(value):
    text = "" if value is None else str(value).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def make_fingerprint(record):
    source = _normalize_identity(record.get("source"))

    if source == "books to scrape":
        identity = _normalize_identity(record.get("name_or_title"))
    else:
        author = _normalize_identity(record.get("author"))
        quote = _normalize_identity(record.get("name_or_title"))[:50]
        identity = f"{author}|{quote}"

    key = f"{source}|{identity}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def find_duplicates(records):
    seen = set()
    unique = []
    duplicates = []

    for record in records:
        fingerprint = make_fingerprint(record)
        if fingerprint in seen:
            duplicates.append(record)
        else:
            seen.add(fingerprint)
            unique.append(record)

    return unique, duplicates
