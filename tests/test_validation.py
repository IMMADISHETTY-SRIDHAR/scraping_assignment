from processing.validation import validate_record


def test_valid_record():
    record = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/test",
        "name_or_title": "Test Book",
        "price": 10.5,
        "rating": 4,
    }
    assert validate_record(record) == []


def test_invalid_record():
    record = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/test",
        "name_or_title": None,
        "price": 10.5,
        "rating": 6,
    }
    errors = validate_record(record)
    assert "missing_name_or_title" in errors
    assert "invalid_rating" in errors
