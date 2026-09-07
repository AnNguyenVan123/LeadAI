"""Free filtering, before any token is spent.

Everything here is a rule we can state out loud and a founder can argue with.
The point is not precision — it is throwing away the obvious noise so the model
only reads posts where its judgement actually changes the answer.
"""
from __future__ import annotations
import re, time

# A post shaped like content marketing: the author is broadcasting a result,
# not asking for help. These flooded the top of the keyword-only baseline.
BROADCAST = re.compile(
    r"here'?s (what|how|why)|lessons (learned|from)|what nobody tells|"
    r"\d+\s*(hacks|tips|lessons|mistakes|ways|things)|"
    r"(hit|crossed|reached|made|did)\s*\$?\s*[\d.,]+\s*(k|m)?\s*(mrr|arr|revenue|in sales)|"
    r"my journey|the mistakes that|i (built|made|launched) (this|my)|"
    r"roast my|feedback on my|check (out|this) my|introducing ", re.I)

# Somebody selling the same thing we sell, or selling to our buyer.
VENDOR = re.compile(
    r"\bwe (help|offer|provide|build) (founders|startups|saas)|our agency|dm me if you|"
    r"i run a (gtm|growth|marketing|lead gen) (agency|business)|book a call|"
    r"limited spots|hiring|looking for (a )?(co-?founder|developer|designer)", re.I)

ASK = re.compile(
    r"\bhow (do|did|would) (i|you)|what (should|would) i|any (advice|tips|tools|ideas)|"
    r"anyone (know|else)|is there (a|any) (tool|way)|recommend|help|struggling|stuck|"
    r"no idea|not sure|\?", re.I)


def apply(posts: list[dict], *, max_age_days: int = 120, min_chars: int = 200) -> tuple[list[dict], dict]:
    now = time.time()
    kept, dropped = [], {"too_old": 0, "too_short": 0, "broadcast": 0, "vendor": 0, "no_ask": 0}
    for p in posts:
        text = f"{p['title']}\n{p['body']}"
        age_days = (now - (p.get("created_utc") or 0)) / 86400
        p["age_days"] = round(age_days, 1)

        if age_days > max_age_days:
            dropped["too_old"] += 1; continue
        if len(p["body"]) < min_chars:
            dropped["too_short"] += 1; continue
        if VENDOR.search(text):
            dropped["vendor"] += 1; continue
        # A broadcast post survives only if it also contains a real question.
        if BROADCAST.search(p["title"]) and not ASK.search(p["title"]):
            dropped["broadcast"] += 1; continue
        if not ASK.search(text):
            dropped["no_ask"] += 1; continue
        kept.append(p)
    return kept, dropped
