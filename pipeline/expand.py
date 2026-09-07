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
    "required": ["subreddits", "negative_terms"],
    "properties": {
        "subreddits": {"type": "array", "minItems": 4, "maxItems": 14,
                       "items": {"type": "string", "maxLength": 30}},
        "negative_terms": {"type": "array", "maxItems": 20,
                           "items": {"type": "string", "maxLength": 40}},
    }}

SYS = """You identify the exact Reddit communities (subreddits) where a specific buyer persona hangs out or complains about their problems.

- Focus on niche, highly relevant subreddits where the pain point is actively discussed.
- Avoid overly broad subreddits unless absolutely necessary (e.g., prefer r/SaaS over r/Entrepreneur if the product is SaaS-specific).
- `negative_terms` are phrases that mark a post as broadcast content, a vendor pitch, or a spammer (these will be used to filter out noise)."""


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
