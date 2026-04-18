import pytest
from unittest.mock import patch, MagicMock
from sources.reddit import fetch_headlines


def test_fetch_headlines_returns_list_of_strings(requests_mock):
    fake_response = {
        "data": {
            "children": [
                {"data": {"title": "Headline one about politics"}},
                {"data": {"title": "Headline two about crypto"}},
            ]
        }
    }
    # mock all subreddit hot.json endpoints
    import config
    for sub in config.REDDIT_SUBREDDITS:
        requests_mock.get(
            f"https://www.reddit.com/r/{sub}/hot.json",
            json=fake_response,
        )
    headlines = fetch_headlines()
    assert isinstance(headlines, list)
    assert all(isinstance(h, str) for h in headlines)
    assert len(headlines) == len(config.REDDIT_SUBREDDITS) * 2


def test_fetch_headlines_handles_failed_subreddit(requests_mock):
    import config
    for sub in config.REDDIT_SUBREDDITS:
        requests_mock.get(
            f"https://www.reddit.com/r/{sub}/hot.json",
            status_code=429,
        )
    headlines = fetch_headlines()
    assert headlines == []
