from processing.deduplication import find_duplicates


def test_duplicate_books():
    records = [
        {"source": "Books to Scrape", "name_or_title": "The Great Book"},
        {"source": "Books to Scrape", "name_or_title": "The Great Book"},
        {"source": "Books to Scrape", "name_or_title": "Another Book"},
    ]
    unique, duplicates = find_duplicates(records)
    assert len(unique) == 2
    assert len(duplicates) == 1


def test_duplicate_quotes():
    records = [
        {"source": "Quotes to Scrape", "author": "Albert Einstein", "name_or_title": "“A famous quote.”"},
        {"source": "Quotes to Scrape", "author": "Albert Einstein", "name_or_title": "A famous quote."},
    ]
    unique, duplicates = find_duplicates(records)
    assert len(unique) == 1
    assert len(duplicates) == 1
