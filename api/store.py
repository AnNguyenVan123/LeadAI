"""SQLite. Two tables: what people asked us to analyse, and who left an email.

The signup shape mirrors what landing.html already writes so both funnels land in
one place when this replaces the static page.
"""
from __future__ import annotations
import json, os, sqlite3, time, uuid

DB = os.environ.get("LEADAI_DB",
                    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "leadai.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id TEXT PRIMARY KEY, created_at REAL, kind TEXT, input TEXT,
  icp TEXT, leads TEXT, scanned INTEGER, funnel TEXT, live INTEGER, unlocked INTEGER DEFAULT 0,
  ip TEXT
);
CREATE TABLE IF NOT EXISTS signups (
  email TEXT PRIMARY KEY, created_at REAL, run_id TEXT, product TEXT, buyer TEXT, leads_seen INTEGER
);
"""


def _conn():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    if "ip" not in {r["name"] for r in c.execute("PRAGMA table_info(runs)")}:
        c.execute("ALTER TABLE runs ADD COLUMN ip TEXT")
    return c


def new_run(kind: str, value: str, live: bool, ip: str = "") -> str:
    rid = uuid.uuid4().hex[:12]
    with _conn() as c:
        c.execute("INSERT INTO runs (id, created_at, kind, input, live, ip) VALUES (?,?,?,?,?,?)",
                  (rid, time.time(), kind, value[:20000], int(live), ip))
    return rid


def save_result(run_id: str, icp: dict, leads: list[dict], scanned: int, funnel: list[dict]) -> None:
    with _conn() as c:
        c.execute("UPDATE runs SET icp=?, leads=?, scanned=?, funnel=? WHERE id=?",
                  (json.dumps(icp), json.dumps(leads), scanned, json.dumps(funnel), run_id))


def get_run(run_id: str) -> dict | None:
    with _conn() as c:
        r = c.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
    if not r or not r["leads"]:
        return None
    return {"id": r["id"], "icp": json.loads(r["icp"]), "leads": json.loads(r["leads"]),
            "scanned": r["scanned"], "funnel": json.loads(r["funnel"]),
            "unlocked": bool(r["unlocked"])}


def unlock(run_id: str, email: str) -> dict | None:
    run = get_run(run_id)
    if not run:
        return None
    with _conn() as c:
        c.execute("UPDATE runs SET unlocked=1 WHERE id=?", (run_id,))
        c.execute("INSERT OR REPLACE INTO signups (email, created_at, run_id, product, buyer, leads_seen)"
                  " VALUES (?,?,?,?,?,?)",
                  (email, time.time(), run_id, run["icp"].get("product", "")[:400],
                   run["icp"].get("buyer", "")[:300], len(run["leads"])))
    run["unlocked"] = True
    return run


def stats() -> dict:
    with _conn() as c:
        return {"runs": c.execute("SELECT COUNT(*) n FROM runs").fetchone()["n"],
                "completed": c.execute("SELECT COUNT(*) n FROM runs WHERE leads IS NOT NULL").fetchone()["n"],
                "signups": c.execute("SELECT COUNT(*) n FROM signups").fetchone()["n"]}
