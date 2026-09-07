"""Claude access with two backends.

SDK  — production. Needs ANTHROPIC_API_KEY or an `ant auth login` profile.
CLI  — development. Shells out to the `claude` binary, which carries its own auth.
       Slower, no batching, no usage numbers, but it runs with zero setup.

Both return parsed JSON. Structured outputs (output_config.format) do the schema
work on the SDK path; the CLI path asks for JSON and validates on the way out.
"""
from __future__ import annotations
import json, os, re, subprocess, concurrent.futures as cf

OPUS = "claude-opus-5"      # judgement calls: qualification, query expansion
HAIKU = "claude-haiku-4-5"  # bulk triage

_client = None


def _sdk():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic()
    return _client


def have_sdk() -> bool:
    if os.environ.get("LEADAI_FORCE_CLI"):
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
                or os.path.exists(os.path.expanduser("~/.config/anthropic")))


def _extract_json(text: str):
    fence = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    raw = fence.group(1) if fence else text
    start = min((i for i in (raw.find("{"), raw.find("[")) if i >= 0), default=-1)
    if start < 0:
        raise ValueError(f"no JSON in response: {text[:200]}")
    end = max(raw.rfind("}"), raw.rfind("]"))
    return json.loads(raw[start:end + 1])


def json_call(system: str, user: str, schema: dict, *, model: str = OPUS,
              max_tokens: int = 8000, effort: str = "high") -> dict:
    """One request, one JSON object back, validated against `schema`."""
    if have_sdk():
        r = _sdk().messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config={"format": {"type": "json_schema", "schema": schema},
                           "effort": effort},
            **({"thinking": {"type": "adaptive"}} if model != HAIKU else {}),
        )
        return json.loads("".join(b.text for b in r.content if b.type == "text"))

    prompt = (f"{system}\n\n{user}\n\nReturn ONLY a JSON object matching this schema, "
              f"no prose, no markdown fence:\n{json.dumps(schema)}")
    for attempt in range(2):
        out = subprocess.run(
            ["claude", "-p", "--model", "haiku" if model == HAIKU else "opus", prompt],
            capture_output=True, text=True, timeout=600)
        try:
            return _extract_json(out.stdout)
        except Exception:
            if attempt:
                raise
    raise RuntimeError("unreachable")


def map_json(jobs: list[tuple[str, str, dict]], *, model: str = OPUS,
             workers: int = 6, **kw) -> list[dict | None]:
    """Same call over many inputs. Production should use the Batch API (50% cheaper,
    no concurrency ceiling); this keeps the CLI path usable by fanning out threads."""
    def one(job):
        try:
            return json_call(job[0], job[1], job[2], model=model, **kw)
        except Exception as e:
            print(f"  ! {type(e).__name__}: {str(e)[:120]}")
            return None

    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(one, jobs))
