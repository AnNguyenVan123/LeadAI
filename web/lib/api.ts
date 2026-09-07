export const API = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export type Evidence = { label: string; present: boolean; quote: string };
export type Lead = {
  title: string; subreddit: string; author: string; url: string; author_url: string; age: string;
  tier: "hot" | "warm" | "cool"; score: number; factors: Record<string, number>;
  problem: string; one_line: string; evidence: Evidence[];
  why: string; risk: string; gate: string; draft: string;
};
export type Icp = {
  product: string; problem: string; buyer: string; not_buyer: string[];
  subreddits: string[]; confidence: "high" | "medium" | "low"; note: string;
};
export type RunResult = {
  run_id: string; icp: Icp; scanned: number;
  funnel: { label: string; n: number; drop: number }[];
  leads: Lead[]; locked_count: number; unlocked: boolean;
};
export type StageEvent = { stage: string; message: string; [k: string]: unknown };

export async function startRun(kind: "url" | "text", value: string, live: boolean) {
  const r = await fetch(`${API}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ kind, value, live }),
  });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail ?? "Failed to send request");
  return (await r.json()) as { run_id: string };
}

/** SSE stream of pipeline stages. Resolves the run id when the backend says `result`. */
export function streamRun(runId: string, onEvent: (e: StageEvent) => void) {
  const es = new EventSource(`${API}/api/runs/${runId}/events`);
  const done = new Promise<void>((resolve, reject) => {
    es.onmessage = (m) => {
      const e = JSON.parse(m.data) as StageEvent;
      onEvent(e);
      if (e.stage === "result") { es.close(); resolve(); }
      if (e.stage === "error") { es.close(); reject(new Error(e.message)); }
    };
    es.onerror = () => { es.close(); reject(new Error("Connection to server lost")); };
  });
  return { done, cancel: () => es.close() };
}

export async function getRun(runId: string) {
  const r = await fetch(`${API}/api/runs/${runId}`);
  if (!r.ok) throw new Error("Failed to fetch result");
  return (await r.json()) as RunResult;
}

export async function unlock(runId: string, email: string) {
  const r = await fetch(`${API}/api/unlock`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ run_id: runId, email }),
  });
  if (!r.ok) throw new Error("Invalid email or result has expired");
  return (await r.json()) as RunResult;
}

export type Health = {
  ok: boolean; engine: string; corpus: number; live_enabled: boolean;
  limits: { per_ip: number; per_day: number };
};

export async function getHealth() {
  const r = await fetch(`${API}/api/health`);
  if (!r.ok) throw new Error("Server is not responding");
  return (await r.json()) as Health;
}

export type SavedLead = {
  id: string; run_id: string; title: string; author: string; url: string;
  problem: string; stage: string; saved_at: number; notes: string; status: string;
};

export async function saveLead(lead: Partial<SavedLead>) {
  const r = await fetch(`${API}/api/leads`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(lead),
  });
  if (!r.ok) throw new Error("Failed to save lead");
  return await r.json();
}

export async function getSavedLeads() {
  const r = await fetch(`${API}/api/leads`);
  if (!r.ok) throw new Error("Failed to load leads list");
  return (await r.json()) as SavedLead[];
}

export async function updateLead(id: string, updates: Partial<SavedLead>) {
  const r = await fetch(`${API}/api/leads/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  if (!r.ok) throw new Error("Failed to update lead");
  return await r.json();
}

export async function deleteLead(id: string) {
  const r = await fetch(`${API}/api/leads/${id}`, {
    method: "DELETE",
  });
  if (!r.ok) throw new Error("Failed to delete lead");
  return await r.json();
}
