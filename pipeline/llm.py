"""LLM access with two providers and a CLI fallback.

Provider priority:
  1. Gemini  — if GEMINI_API_KEY is set, uses google-genai SDK.
  2. Anthropic SDK — if ANTHROPIC_API_KEY is set.
  3. Claude CLI — shells out to the `claude` binary (dev only).

All three return parsed JSON. The provider is chosen once at startup and stays
for the process lifetime.
"""
from __future__ import annotations
import json, os, re, subprocess, concurrent.futures as cf

# Logical model names used throughout the pipeline
OPUS = "opus"    # judgement calls: qualification, query expansion
HAIKU = "haiku"  # bulk triage

# ── Model mapping ──────────────────────────────────────────────────────────

_GEMINI_MODELS = {"opus": "gemini-2.5-pro", "haiku": "gemini-2.5-flash"}
_ANTHROPIC_MODELS = {"opus": "claude-opus-5", "haiku": "claude-haiku-4-5"}

# ── Provider detection ─────────────────────────────────────────────────────

_provider: str | None = None   # "gemini" | "anthropic" | "cli"
_client = None


def _detect_provider() -> str:
    if os.environ.get("LEADAI_FORCE_CLI"):
        return "cli"
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return "anthropic"
    if os.path.exists(os.path.expanduser("~/.config/anthropic")):
        return "anthropic"
    return "cli"


def _get_provider() -> str:
    global _provider
    if _provider is None:
        _provider = _detect_provider()
    return _provider


def have_sdk() -> bool:
    return _get_provider() in ("gemini", "anthropic")


def provider_name() -> str:
    return _get_provider()


# ── Gemini backend ─────────────────────────────────────────────────────────

_gemini_client = None


def _gemini():
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        _gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _gemini_client


def _gemini_call(system: str, user: str, schema: dict, *, model: str,
                 max_tokens: int, **_kw) -> dict:
    from google.genai import types

    model_id = _GEMINI_MODELS.get(model, model)

    response = _gemini().models.generate_content(
        model=model_id,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
            temperature=0.3,
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )
    return json.loads(response.text)


# ── Anthropic SDK backend ─────────────────────────────────────────────────

_anthropic_client = None


def _anthropic():
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic
        _anthropic_client = anthropic.Anthropic()
    return _anthropic_client


def _anthropic_call(system: str, user: str, schema: dict, *, model: str,
                    max_tokens: int, effort: str = "high", **_kw) -> dict:
    model_id = _ANTHROPIC_MODELS.get(model, model)
    r = _anthropic().messages.create(
        model=model_id,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={"format": {"type": "json_schema", "schema": schema},
                       "effort": effort},
        **({} if model == HAIKU else {"thinking": {"type": "adaptive"}}),
    )
    return json.loads("".join(b.text for b in r.content if b.type == "text"))


# ── CLI fallback ───────────────────────────────────────────────────────────

def _extract_json(text: str):
    fence = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    raw = fence.group(1) if fence else text
    start = min((i for i in (raw.find("{"), raw.find("[")) if i >= 0), default=-1)
    if start < 0:
        raise ValueError(f"no JSON in response: {text[:200]}")
    end = max(raw.rfind("}"), raw.rfind("]"))
    return json.loads(raw[start:end + 1])


def _cli_call(system: str, user: str, schema: dict, *, model: str,
              max_tokens: int, **_kw) -> dict:
    prompt = (f"{system}\n\n{user}\n\nReturn ONLY a JSON object matching this schema, "
              f"no prose, no markdown fence:\n{json.dumps(schema)}")
    cli_model = "haiku" if model == HAIKU else "opus"
    for attempt in range(2):
        out = subprocess.run(
            ["claude", "-p", "--model", cli_model, prompt],
            capture_output=True, text=True, timeout=600)
        try:
            return _extract_json(out.stdout)
        except Exception:
            if attempt:
                raise
    raise RuntimeError("unreachable")


# ── Public API ─────────────────────────────────────────────────────────────

_BACKENDS = {"gemini": _gemini_call, "anthropic": _anthropic_call, "cli": _cli_call}


def json_call(system: str, user: str, schema: dict, *, model: str = OPUS,
              max_tokens: int = 8000, **kw) -> dict:
    """One request, one JSON object back."""
    backend = _BACKENDS[_get_provider()]
    return backend(system, user, schema, model=model, max_tokens=max_tokens, **kw)


def map_json(jobs: list[tuple[str, str, dict]], *, model: str = OPUS,
             workers: int = 6, **kw) -> list[dict | None]:
    """Same call over many inputs, fanned out with threads."""
    def one(job):
        try:
            return json_call(job[0], job[1], job[2], model=model, **kw)
        except Exception as e:
            print(f"  ! {type(e).__name__}: {str(e)[:120]}")
            return None

    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(one, jobs))
