# Lead pipeline

    pip install anthropic          # production path
    export ANTHROPIC_API_KEY=...   # or: ant auth login
    export REDDIT_CLIENT_ID=...    # script app at reddit.com/prefs/apps
    export REDDIT_CLIENT_SECRET=...
    python -m pipeline.run

Without an API key the modules shell out to the `claude` CLI instead (slower, no
batching). Without Reddit credentials `sources.py` falls back to public RSS, which
Reddit throttles aggressively and which carries no upvote or comment counts.

| Stage | File | Model | Cost driver |
|---|---|---|---|
| Search plan | `expand.py` | Opus 5 | once per ICP |
| Fetch | `sources.py` | — | Reddit rate limit |
| Prefilter | `prefilter.py` | — | free |
| Triage | `qualify.py` | Haiku 4.5, batched | ~$0.001 / 10 posts |
| Qualify | `qualify.py` | Opus 5, one call each | the real cost |
| Score | `scoring.py` | — | free, re-runnable |

Production should send the qualify pass through the Batch API (50% cheaper, no
concurrency ceiling) and cache the ICP block, which is identical across every call
in a run.
