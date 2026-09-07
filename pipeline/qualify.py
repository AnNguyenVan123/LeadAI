"""Two model passes.

Pass 1 (Haiku, batched): recall filter. Cheap, generous, one word per post.
Pass 2 (Opus, one post per call): evidence extraction, NOT scoring.

The second pass is the important design decision. We never ask the model for a
number — models are poorly calibrated at "rate this 0-100" and the score drifts
between runs and between prompts. We ask it for facts it can point at, each one
carrying a verbatim quote. scoring.py turns those facts into a number in Python,
where the weights are visible, versionable and tunable without re-running anything.

Every quote is then checked against the post body. A quote that is not literally
present means the model paraphrased or invented it, and that piece of evidence is
dropped before it can move the score.
"""
from __future__ import annotations
import json, re
from . import llm
from .icp import ICP

TRIAGE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["verdicts"],
    "properties": {"verdicts": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["id", "keep", "reason"],
        "properties": {
            "id": {"type": "string"},
            "keep": {"type": "boolean"},
            "reason": {"type": "string", "maxLength": 120},
        }}}}}

EVIDENCE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["is_lead", "disqualifier", "problem_statement", "stage", "sells_to",
                 "audience_reachable_online", "icp_fit", "evidence", "why", "risk", "draft_reply"],
    "properties": {
        "is_lead": {"type": "boolean"},
        "disqualifier": {"type": ["string", "null"],
                         "enum": ["vendor", "content_marketing", "no_product_yet",
                                  "off_topic", "cannot_afford", None]},
        "problem_statement": {"type": "string", "maxLength": 300},
        "stage": {"type": "string",
                  "enum": ["idea", "building", "launched_no_users", "has_users", "has_revenue"]},
        "sells_to": {"type": "string", "maxLength": 160},
        # Can WE find this person's customers in public conversations? If not, the
        # product cannot deliver for them however good a fit the person seems.
        "audience_reachable_online": {"type": "boolean"},
        "icp_fit": {"type": "string", "enum": ["strong", "partial", "weak"]},
        "evidence": {
            "type": "object", "additionalProperties": False,
            "required": ["states_problem", "seeking_solution", "tried_tools",
                         "budget_signal", "urgency"],
            "properties": {k: {
                "type": "object", "additionalProperties": False,
                "required": ["present", "quote"],
                "properties": {"present": {"type": "boolean"},
                               "quote": {"type": "string", "maxLength": 400}},
            } for k in ["states_problem", "seeking_solution", "tried_tools",
                        "budget_signal", "urgency"]},
        },
        "why": {"type": "string", "maxLength": 700},
        "risk": {"type": "string", "maxLength": 400},
        "draft_reply": {"type": "string", "maxLength": 1400},
    }}


def _icp_block(icp: ICP) -> str:
    return (f"PRODUCT WE SELL\n{icp.product}\n\n"
            f"THE PROBLEM OUR BUYER FEELS (in their words)\n{icp.problem}\n\n"
            f"WHO BUYS\n{icp.buyer}\n\n"
            f"WHO LOOKS LIKE A BUYER BUT IS NOT\n- " + "\n- ".join(icp.not_buyer) + "\n\n"
            f"KNOWN DISQUALIFIERS\n- " + "\n- ".join(icp.disqualifiers))


TRIAGE_SYS = """You screen Reddit posts for a sales team. Be generous: this is a recall
filter, a later pass does the careful work. Keep a post if a real person is describing a
situation our product could plausibly help with. Drop it only when you are confident:
someone broadcasting advice or results, someone selling something, or a topic mismatch."""


def triage(posts: list[dict], icp: ICP, *, batch: int = 12) -> list[dict]:
    jobs, groups = [], []
    for i in range(0, len(posts), batch):
        chunk = posts[i:i + batch]
        listing = "\n\n".join(
            f"[{p['id']}] r/{p['subreddit']} · {p['age_days']:.0f}d\n"
            f"TITLE: {p['title']}\nBODY: {p['body'][:900]}" for p in chunk)
        jobs.append((TRIAGE_SYS,
                     f"{_icp_block(icp)}\n\n---\nPOSTS\n\n{listing}\n\n"
                     f"Return one verdict per post id.", TRIAGE_SCHEMA))
        groups.append(chunk)

    results = llm.map_json(jobs, model=llm.HAIKU, max_tokens=2000, workers=6)
    keep_ids: set[str] = set()
    for chunk, res in zip(groups, results):
        if res is None:                       # a failed batch keeps everything
            keep_ids |= {p["id"] for p in chunk}
            continue
        keep_ids |= {v["id"] for v in res.get("verdicts", []) if v.get("keep")}
    return [p for p in posts if p["id"] in keep_ids]


QUALIFY_SYS = """You qualify one Reddit post as a sales lead. You are careful and you
never flatter the post.

Rules:
- Every `quote` must be copied VERBATIM from the post body or its comments. Never paraphrase, never
  invent, never quote the title. If there is no supporting sentence, set present=false
  and leave quote empty.
- `audience_reachable_online` asks whether THIS PERSON'S OWN customers discuss their
  problems in public forums. A founder selling to barbershops or local salons is not
  reachable this way even if the founder themselves is a perfect fit. Answer for their
  customers, not for them.
- `draft_reply` is a comment the founder will read and send by hand. Lead with something
  genuinely useful and specific to this post. Mention our product at most once, at the
  end, only if it fits naturally; if the person cannot afford it or we cannot help them,
  do not mention it at all. No greetings, no hype, no emoji.
- `why` and `risk` are for the founder's eyes: what makes this worth their time, and what
  would make contacting them a mistake."""


def qualify(posts: list[dict], icp: ICP, *, workers: int = 6) -> list[dict]:
    from .sources import fetch_comments
    
    jobs = []
    for p in posts:
        comments_text = fetch_comments(p["url"])
        if comments_text:
            p["body"] += comments_text
            
        jobs.append((QUALIFY_SYS,
             f"{_icp_block(icp)}\n\n---\nPOST\nr/{p['subreddit']} · posted {p['age_days']:.0f} "
             f"days ago · u/{p['author']}\nTITLE: {p['title']}\n\n{p['body']}",
             EVIDENCE_SCHEMA))

    out = []
    for p, res in zip(posts, llm.map_json(jobs, model=llm.OPUS, max_tokens=4000, workers=workers)):
        if res is None:
            continue
        res["evidence"] = _verify_quotes(res.get("evidence", {}), p["body"])
        out.append({**p, "judgement": res})
    return out


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _verify_quotes(evidence: dict, body: str) -> dict:
    """Drop any claim whose quote is not literally in the post."""
    hay = _norm(body)
    for key, e in evidence.items():
        quote = (e or {}).get("quote", "")
        if not e.get("present"):
            continue
        if len(quote) < 12 or _norm(quote) not in hay:
            e["present"] = False
            e["unverified_quote"] = quote
            e["quote"] = ""
    return evidence
