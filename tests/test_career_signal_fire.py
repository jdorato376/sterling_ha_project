import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sterling.career_signal_fire import (
    CAREER_KEYWORDS,
    dispatch_alert,
    fetch_articles,
    score_article,
)


def test_score_article():
    article = {"raw_text": "AI in healthcare and Medicaid"}

    def fake_summary(text):
        return text

    def fake_keywords(text):
        return ["AI in healthcare", "Medicaid"]

    score, summary, keywords = score_article(
        article,
        summarize_article=fake_summary,
        extract_keywords=fake_keywords,
    )
    assert score == 2
    assert summary == article["raw_text"]
    assert "Medicaid" in keywords


def test_fetch_articles(monkeypatch):
    def fake_parse(url):
        return SimpleNamespace(
            entries=[
                {
                    "title": "Medicaid news",
                    "summary": "AI in healthcare advances",
                    "link": "http://example.com",
                    "published": "today",
                }
            ]
        )

    monkeypatch.setitem(sys.modules, "feedparser", SimpleNamespace(parse=fake_parse))
    articles = fetch_articles()
    assert articles
    assert any(
        k.lower() in articles[0]["raw_text"].lower() for k in CAREER_KEYWORDS
    )


def test_dispatch_alert(capsys):
    logs = []

    def log_event(_src, msg):
        logs.append(msg)

    alert = {"title": "t", "link": "l", "summary": "s", "published": "p"}
    dispatch_alert(
        alert,
        score=3,
        summary="s",
        keywords=["Medicaid"],
        route_to_briefing=lambda *_args, **_kw: logs.append('brief'),
        escalate_to_exec=lambda *_: logs.append("exec"),
        log_event=log_event,
    )

    assert "exec" in logs
    assert any("High-impact" in m for m in logs)
