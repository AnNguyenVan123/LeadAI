"""Evidence -> number, in code.

Doc §12 lists six factors. Each one here is computed from facts the model extracted
and we verified, so a score can always be traced back to a sentence in the post.
Change a weight, re-run this file, and every historical lead re-scores for free —
no model calls involved. That is the whole reason scoring lives outside the prompt.

The weights are a starting hypothesis (§12 says as much). Once the founder has
marked ~50 leads good/bad, fit them instead of guessing: the inputs are already
a clean feature vector.
"""
from __future__ import annotations
import math

WEIGHTS = {"problem": 0.22, "icp": 0.18, "pain": 0.16, "intent": 0.26,
           "recency": 0.10, "engagement": 0.08}

STAGE_PAIN = {"idea": 20, "building": 45, "launched_no_users": 95,
              "has_users": 70, "has_revenue": 45}
ICP_FIT = {"strong": 95, "partial": 65, "weak": 30}


def _recency(age_days: float, half_life: float = 21.0) -> int:
    """Reddit threads die fast — a 60-day-old post is a cold call, not a lead."""
    return round(100 * math.exp(-age_days * math.log(2) / half_life))


def _engagement(score, comments) -> int:
    if score is None and comments is None:
        return 55                       # RSS gives us nothing; stay neutral
    s, c = score or 0, comments or 0
    # A busy thread means our reply gets buried; a dead one means nobody is listening.
    return round(max(20, min(95, 40 + 12 * math.log1p(c) - 6 * math.log1p(max(0, c - 40)))))


def score(lead: dict) -> dict:
    j, ev = lead["judgement"], lead["judgement"]["evidence"]
    p = lambda k: ev.get(k, {}).get("present", False)

    problem = (55 if p("states_problem") else 15) + (25 if j["is_lead"] else 0) \
              + (20 if j["stage"] in ("launched_no_users", "has_users") else 0)
    icp = ICP_FIT[j["icp_fit"]]
    pain = STAGE_PAIN[j["stage"]] + (10 if p("urgency") else 0)
    intent = (20 + 45 * p("seeking_solution") + 20 * p("tried_tools") + 25 * p("budget_signal"))
    recency = _recency(lead["age_days"])
    engagement = _engagement(lead.get("score"), lead.get("num_comments"))

    factors = {k: max(0, min(100, round(v))) for k, v in
               [("problem", problem), ("icp", icp), ("pain", pain),
                ("intent", intent), ("recency", recency), ("engagement", engagement)]}
    total = round(sum(factors[k] * w for k, w in WEIGHTS.items()))

    # Hard gates. These are not weights — they are things that make a lead wrong
    # no matter how well it scores, and they must not be averaged away.
    tier, gate = None, None
    if j["disqualifier"] or not j["is_lead"]:
        tier, gate = "drop", j["disqualifier"] or "not_a_lead"
    elif not j["audience_reachable_online"]:
        tier, gate = "cool", "we cannot reach their customers from public forums"
        total = min(total, 65)
    elif not p("states_problem"):
        tier, gate = "cool", "no verbatim evidence they have the problem"
        total = min(total, 60)

    if tier is None:
        tier = "hot" if total >= 78 and p("seeking_solution") else "warm" if total >= 60 else "cool"

    return {**lead, "factors": factors, "score": total, "tier": tier, "gate": gate}


def rank(leads: list[dict]) -> list[dict]:
    scored = [score(l) for l in leads]
    keep = [l for l in scored if l["tier"] != "drop"]
    keep.sort(key=lambda l: -l["score"])
    return keep
