"""
Tests for the Naive LLM (Phase 0) response quality.
Focuses on verifying that responses are short and direct after the prompt update.

Run with:
    python -m pytest test_naive_llm.py -v
"""

import os
import re
import time
import pytest
from dotenv import load_dotenv
load_dotenv()

from llm_client import GeminiClient

# ---------------------------------------------------------------------------
# Skip all tests if no API key is present
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set — skipping live LLM tests"
)

PREAMBLE_PHRASES = [
    "great question",
    "as a documentation assistant",
    "i'd be happy to",
    "certainly!",
    "of course!",
    "sure!",
    "absolutely!",
]

MAX_SENTENCES = 4    # slight buffer above the 2-3 prompt instruction
MAX_WORDS     = 100  # hard cap — anything over this is clearly too long

QUERIES = [
    "Where is the auth token generated?",
    "What environment variables are required for authentication?",
    "How do I connect to the database?",
    "Which endpoint lists all users?",
    "How does a client refresh an access token?",
]

# ---------------------------------------------------------------------------
# Fetch all responses ONCE per test session to avoid rate limits.
# Each query gets one API call; all tests below reuse the cached result.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def responses():
    """Call the API once per query with a small delay to stay under rate limits."""
    client = GeminiClient()
    results = {}
    for i, query in enumerate(QUERIES):
        if i > 0:
            time.sleep(13)  # free tier = 5 req/min → ~12s between calls
        results[query] = client.naive_answer_over_full_docs(query, "")
    return results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sentence_count(text):
    sentences = re.split(r'[.!?]+', text.strip())
    return len([s for s in sentences if s.strip()])

def word_count(text):
    return len(text.split())


# ---------------------------------------------------------------------------
# Test cases — all reuse cached `responses`, no extra API calls
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("query", QUERIES)
def test_response_is_not_empty(responses, query):
    assert responses[query].strip(), f"Got empty response for: {query!r}"


@pytest.mark.parametrize("query", QUERIES)
def test_response_is_short_enough(responses, query):
    answer = responses[query]
    wc = word_count(answer)
    assert wc <= MAX_WORDS, (
        f"Response too long ({wc} words) for: {query!r}\n"
        f"Response: {answer}"
    )


@pytest.mark.parametrize("query", QUERIES)
def test_response_sentence_count(responses, query):
    answer = responses[query]
    sc = sentence_count(answer)
    assert sc <= MAX_SENTENCES, (
        f"Too many sentences ({sc}) for: {query!r}\n"
        f"Response: {answer}"
    )


@pytest.mark.parametrize("query", QUERIES)
def test_no_filler_preamble(responses, query):
    lower = responses[query].lower()
    for phrase in PREAMBLE_PHRASES:
        assert phrase not in lower, (
            f"Filler phrase {phrase!r} found for: {query!r}\n"
            f"Response: {responses[query]}"
        )
