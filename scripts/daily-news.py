#!/usr/bin/env python3
"""
Daily News Digest — Top 10 for AI Product Development Managers
Fetches Google News RSS + Hacker News, saves to outputs/news/YYYY-MM-DD.md
"""

import json
import html
import re
import ssl
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

# Use certifi certs if available (fixes macOS Python SSL issue)
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX = ssl.create_default_context()

# Load ANTHROPIC_API_KEY from .env if not already in environment
import os
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
if not os.environ.get("ANTHROPIC_API_KEY") and _ENV_FILE.exists():
    for line in _ENV_FILE.read_text().splitlines():
        if line.startswith("ANTHROPIC_API_KEY="):
            os.environ["ANTHROPIC_API_KEY"] = line.split("=", 1)[1].strip()
            break

# ── Configuration ──────────────────────────────────────────────────────────────

WORKSPACE_DIR  = Path(__file__).resolve().parent.parent
OUTPUT_DIR     = WORKSPACE_DIR / "outputs" / "news"
LINKEDIN_DIR   = WORKSPACE_DIR / "outputs" / "linkedin"

# Google News queries — focused on AI product development
NEWS_QUERIES = [
    "AI model release 2026",
    "LLM product launch 2026",
    "Anthropic Claude update",
    "OpenAI product update",
    "Google Gemini AI product",
    "AI agent framework product",
    "enterprise AI product strategy",
    "AI product roadmap 2026",
]
MAX_PER_QUERY = 3   # items to fetch per query
GOOGLE_SHOW   = 6   # top Google News items in final digest

# Hacker News — keywords relevant to AI PD managers
HN_FETCH    = 100
HN_SHOW     = 4
HN_KEYWORDS = [
    "ai", "llm", "gpt", "claude", "gemini", "agent",
    "product", "launch", "model", "framework", "api",
    "anthropic", "openai", "deepmind", "mistral",
]

# ── Helpers ────────────────────────────────────────────────────────────────────

def fetch(url: str, timeout: int = 12) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 DailyNewsBot/1.0"}
    )
    with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as r:
        return r.read()


def strip_tags(text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


def parse_rss_datetime(raw: str) -> datetime.datetime:
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
        try:
            dt = datetime.datetime.strptime(raw, fmt)
            return dt.replace(tzinfo=None)
        except ValueError:
            continue
    return datetime.datetime.min


def fmt_date(dt: datetime.datetime) -> str:
    return dt.strftime("%b %d") if dt != datetime.datetime.min else ""

# ── Fetchers ───────────────────────────────────────────────────────────────────

def fetch_google_news(queries: list, max_per_query: int = 3, show: int = 6) -> list:
    """Fetch from multiple queries, deduplicate, return most recent `show` items."""
    pool = {}  # title -> item dict (dedup by title)

    for query in queries:
        q   = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
        try:
            root = ET.fromstring(fetch(url))
            for item in root.findall(".//item")[:max_per_query]:
                title = strip_tags(item.findtext("title", ""))
                link  = item.findtext("link", "")
                src   = strip_tags(item.findtext("source", ""))
                dt    = parse_rss_datetime(item.findtext("pubDate", ""))
                if title and link and title not in pool:
                    pool[title] = {"title": title, "link": link, "source": src, "dt": dt}
        except Exception as e:
            print(f"  [warn] google_news({query!r}): {e}")

    sorted_items = sorted(pool.values(), key=lambda x: x["dt"], reverse=True)
    return sorted_items[:show]


def fetch_hacker_news(fetch_n: int = 100, show_n: int = 4, keywords: list = None) -> list:
    """Fetch HN top stories, filter by keywords, return top `show_n` by points."""
    try:
        ids = json.loads(fetch("https://hacker-news.firebaseio.com/v0/topstories.json"))[:fetch_n]
    except Exception as e:
        print(f"  [warn] hacker_news: {e}")
        return []

    stories = []
    for sid in ids:
        try:
            s = json.loads(fetch(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"))
            if s.get("type") != "story":
                continue
            title = s.get("title", "")
            if keywords and not any(k in title.lower() for k in keywords):
                continue
            stories.append({
                "title":    title,
                "url":      s.get("url") or f"https://news.ycombinator.com/item?id={sid}",
                "points":   s.get("score", 0),
                "comments": s.get("descendants", 0),
                "id":       sid,
            })
            if len(stories) >= show_n * 3:  # collect extras, sort by points
                break
        except Exception:
            continue

    return sorted(stories, key=lambda x: x["points"], reverse=True)[:show_n]

# ── Builder ────────────────────────────────────────────────────────────────────

def build_digest_from(gn_items: list, hn_items: list, today: str) -> str:
    now = datetime.datetime.now().strftime("%H:%M")

    lines = [
        f"# Daily News — {today}",
        f"",
        f"*Top 10 for AI Product Development Managers · Generated at {now}*",
        f"",
        f"---",
        f"",
    ]

    n = 1

    # Google News items
    for item in gn_items:
        date_str = fmt_date(item["dt"])
        meta = f"*{item['source']} · {date_str}*" if item["source"] else f"*{date_str}*"
        lines += [
            f"**{n}. [{item['title']}]({item['link']})**",
            meta,
            "",
        ]
        n += 1

    # Hacker News items
    if hn_items:
        lines += ["---", "", "**From Hacker News**", ""]
        for s in hn_items:
            hn_link = f"https://news.ycombinator.com/item?id={s['id']}"
            lines += [
                f"**{n}. [{s['title']}]({s['url']})**",
                f"*HN · {s['points']} pts · [{s['comments']} comments]({hn_link})*",
                "",
            ]
            n += 1

    lines += ["---", f"*Sources: Google News RSS · Hacker News API*"]
    return "\n".join(lines)

# ── LinkedIn post builder ──────────────────────────────────────────────────────

def _normalize_stories(gn_items: list, hn_items: list) -> list:
    """Return a flat list of story dicts with unified fields for Claude to evaluate."""
    stories = []
    for s in gn_items:
        stories.append({
            "title":  s["title"],
            "link":   s["link"],
            "source": s.get("source", ""),
            "meta":   f"{s['source']} · {fmt_date(s['dt'])}" if s.get("source") else fmt_date(s["dt"]),
            "signal": "",
        })
    for s in hn_items:
        hn_link = f"https://news.ycombinator.com/item?id={s['id']}"
        stories.append({
            "title":  s["title"],
            "link":   s["url"],
            "source": "Hacker News",
            "meta":   f"Hacker News · {s['points']} pts · [{s['comments']} comments]({hn_link})",
            "signal": f"{s['points']} HN points",
        })
    return stories


def generate_linkedin_post(gn_items: list, hn_items: list) -> tuple[dict, str]:
    """Use Claude to pick the best story and write the post in one call.
    Returns (story_dict, post_content_string). Falls back to blank template on error."""
    stories = _normalize_stories(gn_items, hn_items)
    if not stories:
        return {}, (
            "<!-- HOOK — grab attention in the first line -->\n\n\n\n"
            "<!-- INSIGHT — what does this mean for AI product teams? -->\n\n\n\n"
            "<!-- YOUR TAKE — personal angle or experience -->\n\n\n\n"
            "<!-- CLOSE — question or call to action -->"
        )

    story_list = "\n".join(
        f"{i+1}. {s['title']} ({s['source']}{' · ' + s['signal'] if s['signal'] else ''})\n   URL: {s['link']}"
        for i, s in enumerate(stories)
    )

    prompt = (
        "You are helping an AI Product Development Manager build their personal brand on LinkedIn.\n\n"
        "Their audience: product managers, tech leads, and founders building AI products.\n"
        "Their voice: direct, confident, practitioner — no fluff, no corporate speak.\n\n"
        f"Today's top stories:\n{story_list}\n\n"
        "Task:\n"
        "1. Pick the single most compelling story for a LinkedIn post. "
        "Prioritise genuine AI product/engineering/strategy relevance over raw engagement numbers. "
        "Ignore stories that only match on name coincidence (e.g. a math paper called 'Claude's Cycles' is NOT about the AI model).\n"
        "2. Write the post based on that story.\n\n"
        "Post format (output ONLY the post — no preamble, no story number, no explanation):\n"
        "- Line 1: SELECTED_STORY_NUMBER=<number>\n"
        "- Then the post:\n"
        "  - 1 punchy hook line (no emoji, no fluff)\n"
        "  - 2-3 short paragraphs with sharp insight for AI product teams\n"
        "  - 1 closing question to drive engagement\n\n"
        "Tone: direct, confident, practitioner. No hashtags, no URL. Max 220 words."
    )

    try:
        import anthropic
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()

        # Parse story number from first line
        lines = raw.splitlines()
        idx = 0
        if lines and lines[0].startswith("SELECTED_STORY_NUMBER="):
            try:
                idx = int(lines[0].split("=", 1)[1].strip()) - 1
            except ValueError:
                idx = 0
            content = "\n".join(lines[1:]).strip()
        else:
            content = raw

        idx = max(0, min(idx, len(stories) - 1))
        return stories[idx], content

    except Exception as e:
        import anthropic as _a
        if isinstance(e, _a.AuthenticationError):
            print(f"  [error] Invalid ANTHROPIC_API_KEY — update .env and retry.")
        else:
            print(f"  [warn] Claude API: {e}")
        fallback = stories[0] if stories else {}
        return fallback, (
            "<!-- HOOK — grab attention in the first line -->\n\n\n\n"
            "<!-- INSIGHT — what does this mean for AI product teams? -->\n\n\n\n"
            "<!-- YOUR TAKE — personal angle or experience -->\n\n\n\n"
            "<!-- CLOSE — question or call to action -->"
        )


def build_linkedin_post(gn_items: list, hn_items: list, today: str) -> str:
    story, content = generate_linkedin_post(gn_items, hn_items)
    if not story:
        return ""

    title = story["title"]
    link  = story["link"]
    meta  = story["meta"]

    return "\n".join([
        f"# LinkedIn Post Draft — {today}",
        f"",
        f"*Based on: [{title}]({link})*  ",
        f"*{meta}*",
        f"",
        f"---",
        f"",
        content,
        f"",
        f"🔗 {link}",
        f"",
        f"#AI #ProductManagement #AIProduct #LLM #ArtificialIntelligence",
        f"",
        f"---",
        f"*Draft generated from today's digest. Edit before posting.*",
    ])

# ── Entry ──────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LINKEDIN_DIR.mkdir(parents=True, exist_ok=True)
    today    = datetime.date.today().strftime("%Y-%m-%d")

    print(f"Fetching news for {today}...")
    gn_items = fetch_google_news(NEWS_QUERIES, MAX_PER_QUERY, GOOGLE_SHOW)
    hn_items = fetch_hacker_news(HN_FETCH, HN_SHOW, HN_KEYWORDS)

    # News digest
    digest   = build_digest_from(gn_items, hn_items, today)
    out_path = OUTPUT_DIR / f"{today}.md"
    out_path.write_text(digest, encoding="utf-8")
    print(f"News:     {out_path}")

    # LinkedIn post — Claude picks best story and writes the post
    li_post = build_linkedin_post(gn_items, hn_items, today)
    if li_post:
        li_path = LINKEDIN_DIR / f"{today}.md"
        li_path.write_text(li_post, encoding="utf-8")
        print(f"LinkedIn: {li_path}")


if __name__ == "__main__":
    main()
