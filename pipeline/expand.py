"""Turn one ICP into a search plan.

The biggest recall mistake is searching for the words you use to describe your
product. Buyers do not know those words — they write "I have no users", not
"customer acquisition tooling". This pass asks Claude for the buyer's vocabulary
at the moment of pain, plus the subreddits where that sentence gets typed.
"""
from __future__ import annotations
from . import llm
from .icp import ICP

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["queries", "subreddits", "negative_terms"],
    "properties": {
        "queries": {"type": "array", "minItems": 12, "maxItems": 24,
                    "items": {"type": "string", "maxLength": 80}},
        "subreddits": {"type": "array", "minItems": 4, "maxItems": 14,
                       "items": {"type": "string", "maxLength": 30}},
        "negative_terms": {"type": "array", "maxItems": 20,
                           "items": {"type": "string", "maxLength": 40}},
    }}

SYS = """You write Reddit search queries that find people in the middle of a problem.

- Write what a frustrated person types, not what a marketer types. "no one signed up"
  beats "user acquisition challenges".
- Prefer exact phrases in quotes; Reddit search is literal.
- Cover the different ways the same pain gets phrased: as a question, as a complaint,
  as a request for a tool, as a description of a failed attempt.
- Include a few queries that catch people naming competing tools.
- negative_terms are phrases that mark a post as broadcast content or a vendor pitch."""


def plan(icp: ICP) -> dict:
    out = llm.json_call(
        SYS,
        f"PRODUCT\n{icp.product}\n\nBUYER\n{icp.buyer}\n\n"
        f"THE PAIN, IN THEIR WORDS\n{icp.problem}\n\n"
        f"SEED SUBREDDITS\n{', '.join(icp.subreddits)}\n\n"
        f"NOT OUR BUYER\n- " + "\n- ".join(icp.not_buyer),
        SCHEMA, model=llm.OPUS, max_tokens=3000)
    out["subreddits"] = list(dict.fromkeys(icp.subreddits + out["subreddits"]))
    return out
