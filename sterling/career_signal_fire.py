"""RSS monitoring and alert dispatcher for career-related news."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List

CAREER_KEYWORDS: List[str] = [
    "home care",
    "healthcare finance",
    "staffing reform",
    "Medicaid",
    "Medicare Advantage",
    "CMS",
    "DOH",
    "OIG",
    "compliance",
    "payment reform",
    "rate cut",
    "reimbursement",
    "AI in healthcare",
    "PTA legislation",
    "New York",
    "nursing",
    "CHHA",
    "LHCSA",
    "value-based care",
]

SOURCE_FEEDS: List[str] = [
    "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml",
    "https://www.fiercehealthcare.com/rss.xml",
    "https://www.fingerlakes1.com/feed",
    "https://khn.org/feed/",
    "https://www.healthcaredive.com/feeds/news/",
]


def fetch_articles() -> List[Dict[str, str]]:
    """Fetch articles from ``SOURCE_FEEDS`` filtering for ``CAREER_KEYWORDS``."""
    from feedparser import parse

    articles: List[Dict[str, str]] = []
    for feed in SOURCE_FEEDS:
        parsed = parse(feed)
        for entry in getattr(parsed, "entries", []):
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            published = entry.get("published", "")
            content = f"{title} {summary}"
            if any(k.lower() in content.lower() for k in CAREER_KEYWORDS):
                articles.append(
                    {
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "published": published,
                        "raw_text": content,
                    }
                )
    return articles


def score_article(article: Dict[str, str], *,
                  summarize_article=lambda x: x,
                  extract_keywords=lambda x: []  # type: ignore
                  ) -> tuple[int, str, List[str]]:
    """Return impact score, summary, and keywords for ``article``."""
    summary = summarize_article(article["raw_text"])
    keywords: List[str] = list(extract_keywords(summary))
    impact_score = sum(1 for k in CAREER_KEYWORDS if k in keywords)
    return impact_score, summary, keywords


def dispatch_alert(
    article: Dict[str, str],
    score: int,
    summary: str,
    keywords: Iterable[str],
    *,
    log_event=lambda *_args, **_kwargs: None,
    route_to_briefing=lambda *_args, **_kwargs: None,
    escalate_to_exec=lambda *_args, **_kwargs: None,
) -> None:
    """Send alerts based on ``score`` and log results."""
    alert = {
        "title": article["title"],
        "summary": summary,
        "link": article["link"],
        "published": article["published"],
        "impact_score": score,
        "keywords": list(keywords),
        "timestamp": datetime.utcnow().isoformat(),
    }

    if score >= 3:
        escalate_to_exec("Career Alert", alert)
        route_to_briefing(alert, briefing_type="professional")
        log_event("CareerSignalFire", f"High-impact alert dispatched: {alert['title']}")
    elif score >= 2:
        route_to_briefing(alert, briefing_type="professional")
        log_event("CareerSignalFire", f"Moderate alert logged: {alert['title']}")
    else:
        log_event("CareerSignalFire", f"Ignored low-signal item: {alert['title']}")


def run_career_signal_fire() -> None:
    """Fetch, score and dispatch career-focused articles."""
    articles = fetch_articles()
    for article in articles:
        score, summary, keywords = score_article(article)
        dispatch_alert(article, score, summary, keywords)


if __name__ == "__main__":  # pragma: no cover - manual trigger
    run_career_signal_fire()
