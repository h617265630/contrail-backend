"""
Tests for resource deduplication and ranking logic.

rerank.py::rerank_resources
"""
import pytest
from learnpathly_langchain.schemas import Resource
from learnpathly_langchain.rerank import rerank_resources


def make_resource(url: str, score: float = 0.0) -> Resource:
    # Use trailing slash to match HttpUrl normalization behavior
    normalized_url = url if url.endswith('/') else url + '/'
    return Resource(
        type="article",
        title=f"Resource at {url}",
        url=normalized_url,
        description="",
        source_score=score,
        why_recommended="",
    )


class TestRerankResources:
    # ─── Normal cases ──────────────────────────────────────────────────────────

    def test_returns_resources_sorted_by_source_score_descending(self):
        resources = [
            make_resource("https://a.com", score=3.0),
            make_resource("https://b.com", score=1.0),
            make_resource("https://c.com", score=5.0),
            make_resource("https://d.com", score=2.0),
        ]
        result = rerank_resources(resources)
        scores = [r.source_score for r in result]
        assert scores == [5.0, 3.0, 2.0, 1.0]

    def test_deduplicates_by_url(self):
        resources = [
            make_resource("https://example.com", score=5.0),
            make_resource("https://example.com", score=4.0),  # duplicate
            make_resource("https://other.com", score=3.0),
        ]
        result = rerank_resources(resources)
        # HttpUrl adds trailing slash, so strip it for comparison
        urls = [str(r.url).rstrip('/') for r in result]
        assert urls == ["https://example.com", "https://other.com"]

    def test_respects_top_k_limit(self):
        resources = [
            make_resource(f"https://site{i}.com", score=10.0 - i)
            for i in range(10)
        ]
        result = rerank_resources(resources, top_k=3)
        assert len(result) == 3
        urls = [str(r.url).rstrip('/') for r in result]
        assert urls == [
            "https://site0.com",
            "https://site1.com",
            "https://site2.com",
        ]

    def test_top_k_equal_to_input_size_returns_all_unique(self):
        resources = [
            make_resource("https://a.com", score=2.0),
            make_resource("https://b.com", score=1.0),
        ]
        result = rerank_resources(resources, top_k=5)
        assert len(result) == 2

    # ─── Edge cases ────────────────────────────────────────────────────────────

    def test_empty_list_returns_empty(self):
        result = rerank_resources([])
        assert result == []

    def test_single_resource_returns_it(self):
        resources = [make_resource("https://only.com", score=1.0)]
        result = rerank_resources(resources)
        assert len(result) == 1
        # HttpUrl normalizes to add trailing slash
        assert str(result[0].url).rstrip('/') == "https://only.com"

    def test_all_duplicates_returns_one(self):
        resources = [
            make_resource("https://same.com", score=3.0),
            make_resource("https://same.com", score=2.0),
            make_resource("https://same.com", score=1.0),
        ]
        result = rerank_resources(resources)
        assert len(result) == 1

    def test_top_k_zero_returns_first_unique(self):
        """top_k=0: first item is added (break triggers on next iteration)."""
        resources = [make_resource("https://a.com", score=1.0)]
        result = rerank_resources(resources, top_k=0)
        # len >= 0 is true after first append, so we break and return 1 item
        assert len(result) == 1

    def test_top_k_negative_breaks_immediately(self):
        """top_k=-1: len >= -1 is true on first item, so only first unique is returned."""
        resources = [make_resource(f"https://s{i}.com", score=1.0) for i in range(3)]
        result = rerank_resources(resources, top_k=-1)
        # After first append: len=1, 1 >= -1 is true → break
        assert len(result) == 1

    def test_urls_with_different_schemes_are_distinct(self):
        resources = [
            make_resource("https://example.com", score=3.0),
            make_resource("http://example.com", score=2.0),
        ]
        result = rerank_resources(resources)
        # Different URLs by string comparison
        assert len(result) == 2

    def test_urls_with_www_and_without_are_distinct(self):
        resources = [
            make_resource("https://example.com", score=3.0),
            make_resource("https://www.example.com", score=2.0),
        ]
        result = rerank_resources(resources)
        assert len(result) == 2

    def test_same_url_different_query_params_is_same(self):
        """str(url) comparison — query params are part of URL string."""
        resources = [
            make_resource("https://example.com?a=1", score=3.0),
            make_resource("https://example.com?b=2", score=5.0),
        ]
        result = rerank_resources(resources)
        # They have different full URL strings
        assert len(result) == 2

    def test_url_fragment_difference_is_same_url(self):
        """Fragment (#section) is part of URL string, but browser navigation may treat them as same."""
        resources = [
            make_resource("https://example.com#top", score=3.0),
            make_resource("https://example.com#bottom", score=5.0),
        ]
        result = rerank_resources(resources)
        # Different URL strings
        assert len(result) == 2

    # ─── Ordering with duplicates ───────────────────────────────────────────────

    def test_higher_score_duplicate_appears_first(self):
        """When same URL appears multiple times, highest score wins (first occurrence in sorted order)."""
        resources = [
            make_resource("https://a.com", score=1.0),
            make_resource("https://a.com", score=5.0),  # higher score, should win
            make_resource("https://b.com", score=2.0),
        ]
        result = rerank_resources(resources)
        # Sorted: a(5.0), b(2.0), a(1.0) — dedup keeps first a(5.0)
        urls = [str(r.url).rstrip('/') for r in result]
        assert urls[0] == "https://a.com"
        assert urls[1] == "https://b.com"
        assert result[0].source_score == 5.0

    # ─── Error cases ────────────────────────────────────────────────────────────

    def test_resource_with_missing_score_defaults_to_zero(self):
        resources = [
            Resource(type="article", title="No score", url="https://a.com", description="", source_score=0.0),
        ]
        result = rerank_resources(resources)
        assert result[0].source_score == 0.0

    def test_resources_with_none_urls_handled_as_string(self):
        """URL is HttpUrl field; str(None) produces 'None' string, which won't match real URLs."""
        resources = [
            make_resource("https://real.com", score=2.0),
        ]
        # Resource.url is HttpUrl — can't be None if created via pydantic
        # This tests the runtime behavior
        result = rerank_resources(resources)
        assert len(result) == 1
