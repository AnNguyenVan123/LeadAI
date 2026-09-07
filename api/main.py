"""FastAPI backend.

    uvicorn api.main:app --reload --port 8000

POST /api/analyze        start a run, returns {run_id}
GET  /api/runs/{id}/events   SSE: one event per pipeline stage, then `result`
GET  /api/runs/{id}      the finished run (3 leads unless unlocked)
POST /api/unlock         email -> the rest of the leads
GET  /api/stats          demo counters
"""
from __future__ import annotations
import json, os, queue, threading, traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from . import analyze, limits, store
from .schemas import AnalyzeRequest, UnlockRequest, SaveLeadRequest, UpdateLeadRequest, SavedLead

FREE_LEADS = 3

app = FastAPI(title="LeadAI demo")
ORIGINS = [o.strip() for o in os.environ.get(
    "LEADAI_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=ORIGINS,
                   allow_methods=["*"], allow_headers=["*"])

_streams: dict[str, queue.Queue] = {}


def _work(run_id: str, req: AnalyzeRequest) -> None:
    q = _streams[run_id]

    def emit(stage: str, message: str, data: dict) -> None:
        q.put({"stage": stage, "message": message, **data})

    try:
        out = analyze.run(req.kind, req.value, req.live, emit)
        store.save_result(run_id, out["icp"], out["leads"], out["scanned"], out["funnel"])
        q.put({"stage": "result", "message": "xong", "run_id": run_id})
    except Exception as e:
        traceback.print_exc()
        q.put({"stage": "error", "message": f"{type(e).__name__}: {e}"})
    finally:
        q.put(None)


@app.post("/api/analyze")
def start(req: AnalyzeRequest, request: Request):
    ip = limits.check(request, req.live)
    run_id = store.new_run(req.kind, req.value, req.live, ip)
    _streams[run_id] = queue.Queue()
    threading.Thread(target=_work, args=(run_id, req), daemon=True).start()
    return {"run_id": run_id}


@app.get("/api/runs/{run_id}/events")
def events(run_id: str):
    q = _streams.get(run_id)
    if q is None:
        raise HTTPException(404, "run không tồn tại hoặc đã kết thúc")

    def gen():
        while True:
            try:
                item = q.get(timeout=15)
                if item is None:
                    break
                yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
            except queue.Empty:
                yield ": keepalive\n\n"
        _streams.pop(run_id, None)

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def _payload(run: dict) -> dict:
    leads = run["leads"] if run["unlocked"] else run["leads"][:FREE_LEADS]
    return {"run_id": run["id"], "icp": run["icp"], "scanned": run["scanned"],
            "funnel": run["funnel"], "leads": leads,
            "locked_count": max(0, len(run["leads"]) - len(leads)),
            "unlocked": run["unlocked"]}


@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(404, "chưa có kết quả cho run này")
    return _payload(run)


@app.post("/api/unlock")
def unlock(req: UnlockRequest):
    run = store.unlock(req.run_id, req.email)
    if not run:
        raise HTTPException(404, "chưa có kết quả cho run này")
    run["id"] = req.run_id
    return _payload(run)


@app.get("/api/stats")
def stats():
    return store.stats()


@app.get("/api/health")
def health():
    return {"ok": True, "engine": analyze.llm.provider_name(),
            "corpus": len(analyze.cached_corpus()), "live_enabled": limits.ALLOW_LIVE,
            "limits": {"per_ip": limits.PER_IP, "per_day": limits.PER_DAY}}


@app.post("/api/leads")
def save_lead(req: SaveLeadRequest):
    lead_id = store.save_lead(req.model_dump())
    return {"id": lead_id}


@app.get("/api/leads", response_model=list[SavedLead])
def list_leads():
    return store.list_leads()


@app.patch("/api/leads/{lead_id}")
def update_lead(lead_id: str, req: UpdateLeadRequest):
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    store.update_lead(lead_id, updates)
    return {"ok": True}


@app.delete("/api/leads/{lead_id}")
def delete_lead(lead_id: str):
    store.delete_lead(lead_id)
    return {"ok": True}
