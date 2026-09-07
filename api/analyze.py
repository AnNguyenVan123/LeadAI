"""One demo run: whatever the visitor typed -> scored leads.

Two paths share every stage after the ICP:

  fast  — score against a corpus of Reddit posts already pulled and pre-filtered.
          Nothing is faked; the posts are real and so is the judgement. What is
          skipped is the fetch, which is the slow, rate-limited part.
  live  — expand queries and hit Reddit now. Minutes, and Reddit throttles hard.
"""
from __future__ import annotations
import json, os, re, urllib.request, functools
from typing import Callable, Iterator

from pipeline import expand, prefilter, qualify, scoring, sources, llm
from pipeline.icp import ICP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "out", "posts.json")
QUALIFY_TOP = int(os.environ.get("LEADAI_QUALIFY_TOP", "8"))

STAGE = {"idea": "just an idea", "building": "building",
         "launched_no_users": "launched, no users", "has_users": "has users",
         "has_revenue": "has revenue"}
EV_LABELS = [("states_problem", "Explicitly states the problem"),
             ("seeking_solution", "Actively seeking a solution"),
             ("tried_tools", "Has tried other tools/methods"),
             ("budget_signal", "Shows willingness to pay"),
             ("urgency", "Has an urgency factor")]
GATE_VI = {"we cannot reach their customers from public forums":
           "Their customers are not on public forums — we cannot find them",
           "no verbatim evidence they have the problem":
           "No verbatim quote proving they have the problem"}

ICP_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["product", "problem", "buyer", "not_buyer", "subreddits", "confidence", "note"],
    "properties": {
        "product": {"type": "string", "maxLength": 600},
        "problem": {"type": "string", "maxLength": 600},
        "buyer": {"type": "string", "maxLength": 400},
        "not_buyer": {"type": "array", "maxItems": 5, "items": {"type": "string", "maxLength": 160}},
        "subreddits": {"type": "array", "minItems": 3, "maxItems": 10,
                       "items": {"type": "string", "maxLength": 30}},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "note": {"type": "string", "maxLength": 300},
    }}

ICP_SYS = """You turn a scrap of product information into a search brief.

`problem` is the hardest and most important field: write the sentence the buyer would
type on Reddit at the moment the problem bites — their words, their frustration, no
marketing vocabulary. Never reuse the product's own tagline for it.

`buyer` is one specific role, not a market. `not_buyer` lists look-alikes that would
waste the founder's time. `subreddits` are places that specific buyer actually posts in.

Set confidence to "low" and say what is missing in `note` when the input is too thin to
be sure — a vague description is a normal thing for a visitor to give us."""


def fetch_url(url: str) -> str:
    if not re.match(r"^https?://", url):
        url = "https://" + url
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; leadai/0.1)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read(600_000).decode("utf-8", "replace")
    html = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", html)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&[a-z]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()[:8000]


def extract_icp(kind: str, value: str) -> dict:
    source = fetch_url(value) if kind == "url" else value.strip()[:8000]
    if len(source) < 40:
        raise ValueError("Content is too short to understand the product")
    return llm.json_call(ICP_SYS, f"INPUT ({kind})\n\n{source}", ICP_SCHEMA,
                         model=llm.OPUS, max_tokens=2000)


@functools.lru_cache(maxsize=1)
def cached_corpus() -> list[dict]:
    posts = json.load(open(CORPUS))
    kept, _ = prefilter.apply(posts, max_age_days=180)
    return kept


def to_wire(lead: dict) -> dict:
    j = lead["judgement"]
    # Nothing reaches the UI without a real, openable source. A lead we cannot point
    # at is worthless to the founder and indistinguishable from an invented one.
    if not re.match(r"^https://www\.reddit\.com/r/[^/]+/comments/", lead["url"] or ""):
        raise ValueError(f"lead has no verifiable permalink: {lead.get('url')!r}")
    author = (lead.get("author") or "").strip()
    return {
        "title": lead["title"], "subreddit": lead["subreddit"], "author": author,
        "url": lead["url"],
        "author_url": f"https://www.reddit.com/user/{author}" if author and author != "[deleted]" else "",
        "age": f"{round(lead['age_days'])} days ago" if lead["age_days"] >= 1 else "today",
        "tier": lead["tier"], "score": lead["score"], "factors": lead["factors"],
        "problem": j["problem_statement"],
        "one_line": f"{STAGE.get(j['stage'], j['stage'])} · sells to {j['sells_to']}",
        "evidence": [{"label": lab, "present": j["evidence"].get(k, {}).get("present", False),
                      "quote": j["evidence"].get(k, {}).get("quote", "")} for k, lab in EV_LABELS],
        "why": j["why"], "risk": j.get("risk", ""),
        "gate": GATE_VI.get(lead.get("gate") or "", lead.get("gate") or ""),
        "draft": j["draft_reply"],
    }


def run(kind: str, value: str, live: bool, emit: Callable[[str, str, dict], None]) -> dict:
    emit("icp", "Reading your product...", {})
    icp_raw = extract_icp(kind, value)
    icp = ICP(product=icp_raw["product"], problem=icp_raw["problem"], buyer=icp_raw["buyer"],
              not_buyer=icp_raw["not_buyer"] or ["People selling services to this exact same audience"],
              subreddits=icp_raw["subreddits"],
              disqualifiers=["Their customers don't discuss publicly on forums"])
    emit("icp_done", f"Looking for: {icp_raw['buyer']}", {"icp": icp_raw})

    if live:
        emit("plan", "Finding relevant Subreddits...", {})
        plan = expand.plan(icp)
        emit("plan_done", f"Found {len(plan['subreddits'])} subreddits",
             {"queries": plan["subreddits"][:8]})
        emit("fetch", "Collecting new posts from the last 24h...", {})
        posts = sources.collect(plan, per_query=100, pause=2.0)
        scanned = len(posts)
        pool, dropped = prefilter.apply(posts)
    else:
        pool = cached_corpus()
        scanned = len(json.load(open(CORPUS)))
        dropped = {"pre-filter": scanned - len(pool)}
    emit("prefilter", f"{scanned} posts → {len(pool)} after static filter",
         {"scanned": scanned, "kept": len(pool), "dropped": dropped})

    emit("triage", "Haiku 4.5 is filtering irrelevant posts...", {})
    kept = qualify.triage(pool, icp)
    emit("triage_done", f"remaining {len(kept)} posts for deep analysis", {"kept": len(kept)})

    kept.sort(key=lambda p: p["age_days"])
    kept = kept[:QUALIFY_TOP]
    emit("qualify", f"Opus 5 is extracting evidence from {len(kept)} posts...", {})
    judged = qualify.qualify(kept, icp, workers=6)

    leads = scoring.rank(judged)
    emit("score", f"{len(leads)} leads after scoring and hard gates", {})

    funnel = [
        {"label": "Reddit posts", "n": scanned, "drop": scanned - len(pool)},
        {"label": "static filter", "n": len(pool), "drop": len(pool) - len(kept)},
        {"label": "Haiku triage", "n": len(kept), "drop": len(kept) - len(judged)},
        {"label": "Opus evidence", "n": len(judged), "drop": len(judged) - len(leads)},
        {"label": "real leads", "n": len(leads), "drop": 0},
    ]
    return {"icp": icp_raw, "leads": [to_wire(l) for l in leads], "scanned": scanned, "funnel": funnel}
