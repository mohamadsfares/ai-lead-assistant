from app.answer import cited_sources

CHUNKS = [
    {"source": "pricing.md", "section": "Roofing"},
    {"source": "warranty.md", "section": "Roofing Warranty"},
    {"source": "pricing.md", "section": "Gutters"},
]


def test_keeps_only_cited_sources_with_their_numbers():
    answer = "A new roof costs $9,500 to $22,000 [1]. Gutter guards cost extra [3]."
    assert cited_sources(answer, CHUNKS) == ["[1] pricing.md > Roofing", "[3] pricing.md > Gutters"]


def test_repeated_citations_are_listed_once_in_order():
    answer = "Free [3]. Within 48 hours [1]. No obligation [3]."
    assert cited_sources(answer, CHUNKS) == ["[1] pricing.md > Roofing", "[3] pricing.md > Gutters"]


def test_no_citations_returns_empty_list():
    answer = "Our sources don't mention that."
    assert cited_sources(answer, CHUNKS) == []


def test_ignores_numbers_outside_the_sources():
    answer = "Something [9]."
    assert cited_sources(answer, CHUNKS) == []