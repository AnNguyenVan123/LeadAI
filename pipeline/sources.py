"""Reddit access.

OAuth is the real path: create a 'script' app at reddit.com/prefs/apps, export
REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET / REDDIT_USER_AGENT. You get 100 requests
per minute, full search operators, comment bodies and score/comment counts.

Without credentials we fall back to the public .rss feeds. Those still return real
posts but Reddit throttles them hard (HTTP 429 within a couple of requests), caps
at 100 items, and omits upvotes and comment counts — engagement scoring goes blind.
"""
from __future__ import annotations
import html, json, os, re, time, urllib.parse, urllib.request, urllib.error
import xml.etree.ElementTree as ET

NS = {"a": "http://www.w3.org/2005/Atom"}
UA = os.environ.get("REDDIT_USER_AGENT", "leadai-radar/0.1")


def _clean(h: str) -> str:
    h = html.unescape(h or "")
    for a, b in [("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("—", "-"), ("–", "-")]:
        h = h.replace(a, b)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()


def _token() -> str | None:
    cid, secret = os.environ.get("REDDIT_CLIENT_ID"), os.environ.get("REDDIT_CLIENT_SECRET")
    if not (cid and secret):
        return None
    import base64
    auth = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=b"grant_type=client_credentials",
        headers={"Authorization": f"Basic {auth}", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)["access_token"]


def _get(url: str, headers: dict, tries: int = 5) -> str | None:
    wait = 15
    for _ in range(tries):
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(url, headers=headers), timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503):
                return None
        except Exception:
            pass
        time.sleep(wait)
        wait = min(wait * 1.6, 120)
    return None


def search(subreddit: str, query: str, *, limit: int = 100, window: str = "year") -> list[dict]:
    tok = _token()
    if tok:
        url = (f"https://oauth.reddit.com/r/{subreddit}/search?"
               f"q={urllib.parse.quote(query)}&restrict_sr=1&sort=new&limit={limit}&t={window}")
        body = _get(url, {"Authorization": f"bearer {tok}", "User-Agent": UA})
        if not body:
            return []
        return [{
            "id": c["data"]["id"],
            "title": _clean(c["data"]["title"]),
            "body": _clean(c["data"].get("selftext", ""))[:6000],
            "author": c["data"].get("author", ""),
            "subreddit": c["data"]["subreddit"],
            "created_utc": c["data"]["created_utc"],
            "score": c["data"].get("score", 0),
            "num_comments": c["data"].get("num_comments", 0),
            "url": "https://www.reddit.com" + c["data"]["permalink"],
            "found_via": f"r/{subreddit} · {query}",
        } for c in json.loads(body)["data"]["children"]]

    url = (f"https://www.reddit.com/r/{subreddit}/search.rss?"
           f"q={urllib.parse.quote(query)}&restrict_sr=1&sort=new&limit={limit}&t={window}")
    body = _get(url, {"User-Agent": UA, "Accept": "application/atom+xml"})
    if not body or "<entry" not in body:
        return []
    out = []
    for e in ET.fromstring(body).findall("a:entry", NS):
        link = e.find("a:link", NS)
        content = e.find("a:content", NS)
        author = e.find("a:author/a:name", NS)
        updated = e.find("a:updated", NS)
        if link is None:
            continue
        href = link.get("href")
        out.append({
            "id": href.rstrip("/").split("/")[-2] if "/comments/" in href else href,
            "title": _clean(e.find("a:title", NS).text if e.find("a:title", NS) is not None else ""),
            "body": _clean(content.text if content is not None else "")[:6000],
            "author": (author.text if author is not None else "").replace("/u/", ""),
            "subreddit": subreddit,
            "created_utc": _iso_to_epoch(updated.text if updated is not None else ""),
            "score": None,          # not in RSS
            "num_comments": None,   # not in RSS
            "url": href,
            "found_via": f"r/{subreddit} · {query}",
        })
    return out


def _iso_to_epoch(s: str) -> float:
    import datetime as dt
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0


def collect(plan: dict, *, per_query: int = 100, pause: float = 2.0) -> list[dict]:
    """Run the whole expanded query plan, deduped by post id."""
    seen: dict[str, dict] = {}
    for sub in plan["subreddits"]:
        for q in plan["queries"]:
            hits = search(sub, q, limit=per_query)
            for p in hits:
                seen.setdefault(p["id"], p)
            print(f"  r/{sub} · {q}: +{len(hits)} (total {len(seen)})")
            time.sleep(pause)
    return list(seen.values())
