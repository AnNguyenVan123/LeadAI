"""End to end: ICP -> search plan -> posts -> prefilter -> triage -> qualify -> score.

    python -m pipeline.run                     # fetch fresh from Reddit
    python -m pipeline.run --cache posts.json  # re-run judgement on a saved corpus
    python -m pipeline.run --limit 60          # cap the expensive pass
"""
from __future__ import annotations
import argparse, datetime as dt, json, os, sys, time
from . import expand, sources, prefilter, qualify, scoring, llm
from .icp import LEADAI

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", help="JSON file of posts to reuse instead of fetching")
    ap.add_argument("--limit", type=int, default=60, help="max posts through the Opus pass")
    ap.add_argument("--out", default=os.path.join(OUT, "leads.json"))
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    print(f"engine: {'Anthropic SDK' if llm.have_sdk() else 'claude CLI'}")

    if args.cache:
        posts = json.load(open(args.cache))
        print(f"1. corpus          {len(posts)} posts from {args.cache}")
    else:
        print("1. search plan")
        p = expand.plan(LEADAI)
        json.dump(p, open(os.path.join(OUT, "plan.json"), "w"), indent=1)
        print(f"   {len(p['queries'])} queries × {len(p['subreddits'])} subreddits")
        posts = sources.collect(p)
        json.dump(posts, open(os.path.join(OUT, "posts.json"), "w"), indent=1)
        print(f"   {len(posts)} unique posts")

    kept, dropped = prefilter.apply(posts)
    print(f"2. prefilter       {len(posts)} -> {len(kept)}   dropped {dropped}")

    kept = qualify.triage(kept, LEADAI)
    print(f"3. triage (haiku)  -> {len(kept)}")

    kept.sort(key=lambda p: p["age_days"])
    kept = kept[:args.limit]
    judged = qualify.qualify(kept, LEADAI)
    print(f"4. qualify (opus)  -> {len(judged)} judged")

    leads = scoring.rank(judged)
    tiers = {t: sum(1 for l in leads if l["tier"] == t) for t in ("hot", "warm", "cool")}
    unverified = sum(1 for l in leads for e in l["judgement"]["evidence"].values()
                     if e.get("unverified_quote"))
    print(f"5. score           {len(judged)} -> {len(leads)} kept   {tiers}")
    print(f"   quotes rejected as unverifiable: {unverified}")

    json.dump({"run_at": dt.datetime.now().isoformat(timespec="seconds"),
               "posts_scanned": len(posts), "prefilter_dropped": dropped,
               "leads": leads}, open(args.out, "w"), ensure_ascii=False, indent=1)
    print(f"\nwrote {args.out} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
