"use client";
import { useState } from "react";
import type { RunResult } from "@/lib/api";
import { unlock } from "@/lib/api";
import LeadCard from "./LeadCard";

const CONF = { high: "confident", medium: "fairly sure", low: "vague" } as const;

export default function Results({ run, onUpdate }: { run: RunResult; onUpdate: (r: RunResult) => void }) {
  const [email, setEmail] = useState("");
  const [sending, setSending] = useState(false);
  const [err, setErr] = useState("");
  const counts = { hot: 0, warm: 0, cool: 0 };
  run.leads.forEach((l) => counts[l.tier]++);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSending(true); setErr("");
    try { onUpdate(await unlock(run.run_id, email)); }
    catch (e) { setErr(e instanceof Error ? e.message : "Có lỗi xảy ra"); }
    finally { setSending(false); }
  }

  return (
    <div className="flex flex-col gap-6">
      <section className="rounded border border-line bg-surface p-5">
        <div className="flex items-baseline justify-between gap-3 flex-wrap">
          <h2 className="font-cond font-semibold text-[15px]">I understand you're selling</h2>
          <span className="font-mono text-[11px] text-muted">confidence: {CONF[run.icp.confidence]}</span>
        </div>
        <dl className="mt-3 grid sm:grid-cols-3 gap-4 text-[13.5px]">
          {([["Product", run.icp.product], ["Customer's pain", run.icp.problem], ["Buyer", run.icp.buyer]] as const).map(([k, v]) => (
            <div key={k}>
              <dt className="font-cond text-[11px] uppercase tracking-[.14em] text-muted">{k}</dt>
              <dd className="mt-1 leading-relaxed">{v}</dd>
            </div>
          ))}
        </dl>
        {run.icp.note && <p className="mt-3 text-[13px] text-muted border-t border-line-soft pt-3">{run.icp.note}</p>}
      </section>

      <section className="rounded border border-line overflow-hidden bg-line grid grid-cols-2 sm:grid-cols-5 gap-px">
        {run.funnel.map((f) => (
          <div key={f.label} className="bg-surface px-4 py-3 flex flex-col gap-0.5">
            <span className="font-mono text-[19px] tabnum">{f.n}</span>
            <span className="text-[11px] text-muted">{f.label}</span>
            {f.drop > 0 && <span className="font-mono text-[11px] text-hot">-{f.drop}</span>}
          </div>
        ))}
      </section>

      <div className="flex flex-wrap gap-2 items-center font-mono text-[11px] text-muted">
        <span className="text-hot">{counts.hot} contact now</span>·
        <span className="text-warm">{counts.warm} reply this week</span>·
        <span className="text-cool">{counts.cool} monitor</span>
        {run.locked_count > 0 && <span>· {run.locked_count} locked leads</span>}
      </div>

      {run.leads.length === 0 ? (
        <div className="rounded border border-line bg-surface p-5">
          <h3 className="font-cond font-semibold text-[16px]">No leads found for this product</h3>
          <p className="mt-2 text-[14px] text-muted leading-relaxed">
            I scanned {run.scanned} posts and nobody is actually facing the problem you solve.
            I chose to return 0 instead of giving you a few almost-right names — a wrong lead
            wastes half your day, and makes you lose trust in the right ones.
          </p>
          {run.icp.note && (
            <p className="mt-3 text-[13.5px] border-l-2 border-warm pl-3 leading-relaxed">{run.icp.note}</p>
          )}
          <ul className="mt-4 flex flex-col gap-1.5 text-[13.5px] text-muted">
            <li>· Try checking <b className="text-ink font-medium">"Scan live Reddit"</b> to search using a custom query for your product.</li>
            <li>· Or describe it better: who is your customer, where do they complain, what do they use.</li>
          </ul>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {run.leads.map((l) => <LeadCard key={l.url} lead={l} runId={run.run_id} />)}
        </div>
      )}

      {run.locked_count > 0 && (
        <div className="relative">
          <div className="flex flex-col gap-3" aria-hidden>
            {run.leads.slice(0, Math.min(2, run.locked_count)).map((l) => <LeadCard key={"ghost" + l.url} lead={l} blurred />)}
          </div>
          <div className="absolute inset-0 flex items-start justify-center pt-8">
            <form onSubmit={submit} className="w-full max-w-md rounded border border-line bg-surface p-5 shadow-[0_20px_50px_-30px_rgba(20,24,26,.7)]">
              <h3 className="font-cond font-semibold text-[16px]">{run.locked_count} more leads for this product</h3>
              <p className="mt-1 text-[13px] text-muted">Leave your email to view them all, along with suggested replies. No spam, no newsletters.</p>
              <div className="mt-3 flex gap-2">
                <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@email.com"
                  className="flex-1 rounded-sm border border-line bg-surface-2 px-3 py-2.5 text-[14px] outline-none focus:border-accent focus:bg-surface" />
                <button disabled={sending}
                  className="font-cond font-semibold px-4 py-2.5 rounded-sm bg-accent text-white disabled:opacity-50">
                  {sending ? "…" : "Unlock"}
                </button>
              </div>
              {err && <p className="mt-2 text-[12.5px] text-hot">{err}</p>}
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
