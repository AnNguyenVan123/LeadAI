"use client";
import { useState } from "react";
import type { Lead } from "@/lib/api";

const TIER = {
  hot: { label: "Liên hệ ngay", stripe: "border-l-hot", text: "text-hot", chip: "bg-hot-soft text-hot" },
  warm: { label: "Trả lời trong tuần", stripe: "border-l-warm", text: "text-warm", chip: "bg-warm-soft text-warm" },
  cool: { label: "Theo dõi", stripe: "border-l-cool", text: "text-cool", chip: "bg-cool-soft text-cool" },
} as const;

const FACTORS: [string, string][] = [
  ["problem", "Khớp vấn đề"], ["icp", "Khớp chân dung"], ["pain", "Mức đau"],
  ["intent", "Ý định mua"], ["recency", "Độ mới"], ["engagement", "Tương tác"],
];

export default function LeadCard({ lead, blurred }: { lead: Lead; blurred?: boolean }) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const t = TIER[lead.tier];

  return (
    <article className={`rounded border border-line border-l-[3px] ${t.stripe} bg-surface ${blurred ? "pointer-events-none select-none blur-[5px]" : ""}`}>
      <button onClick={() => setOpen(!open)} aria-expanded={open}
        className="w-full text-left grid grid-cols-[1fr_auto] gap-x-5 gap-y-1 p-4 sm:p-5 cursor-pointer">
        <div>
          <h3 className="font-cond font-semibold text-[17px] leading-snug">{lead.title}</h3>
          <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px] text-muted">
            <span className="font-mono px-1.5 py-0.5 rounded-sm bg-surface-2 border border-line-soft">r/{lead.subreddit}</span>
            {lead.author_url ? (
              <a href={lead.author_url} target="_blank" rel="noopener"
                onClick={(e) => e.stopPropagation()}
                className="font-mono underline decoration-line underline-offset-2 hover:text-accent">u/{lead.author}</a>
            ) : (
              <span className="font-mono">u/{lead.author}</span>
            )}
            <span className="font-mono">{lead.age}</span>
            <span>{lead.one_line}</span>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1.5">
          <span className={`font-cond text-[11px] font-semibold uppercase tracking-[.09em] px-2 py-1 rounded-sm ${t.chip}`}>{t.label}</span>
          <span className={`font-mono text-[22px] tabnum ${t.text}`}>{lead.score}</span>
        </div>
      </button>

      {open && (
        <div className="border-t border-line-soft p-4 sm:p-5 flex flex-col gap-5">
          <p className="text-[14px] text-muted border-l-2 border-line pl-3">{lead.problem}</p>

          <div className="grid md:grid-cols-2 gap-5">
            <div className="flex flex-col gap-2">
              <div className="font-cond text-[11px] uppercase tracking-[.14em] text-muted">Điểm thành phần</div>
              {FACTORS.map(([k, label]) => (
                <div key={k} className="grid grid-cols-[104px_1fr_30px] gap-2.5 items-center text-[12px]">
                  <span>{label}</span>
                  <span className="h-[5px] rounded-full bg-line-soft overflow-hidden">
                    <span className="block h-full rounded-full bg-accent" style={{ width: `${lead.factors[k] ?? 0}%` }} />
                  </span>
                  <span className="font-mono text-[12px] tabnum text-right text-muted">{lead.factors[k] ?? 0}</span>
                </div>
              ))}
            </div>

            <div>
              <div className="font-cond text-[11px] uppercase tracking-[.14em] text-muted">Bằng chứng đã đối chiếu với post gốc</div>
              <div className="mt-2 flex flex-col gap-2">
                {lead.evidence.map((e) => (
                  <div key={e.label} className={`grid grid-cols-[16px_1fr] gap-2 text-[13px] ${e.present ? "" : "text-muted/70"}`}>
                    <span className={`font-mono text-xs ${e.present ? "text-accent" : "text-line"}`}>{e.present ? "✓" : "—"}</span>
                    <span>
                      {e.label}
                      {e.quote && <q className="block not-italic text-[12.5px] text-muted border-l-2 border-line-soft pl-2 mt-1">{e.quote}</q>}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="text-[14px]">
            <div className="font-cond text-[11px] uppercase tracking-[.14em] text-muted">Vì sao là lead</div>
            <p className="mt-1">{lead.why}</p>
            {lead.risk && (<>
              <div className="font-cond text-[11px] uppercase tracking-[.14em] text-muted mt-3">Rủi ro</div>
              <p className="mt-1">{lead.risk}</p>
            </>)}
          </div>

          {lead.gate && (
            <div className="flex gap-2 items-baseline text-[13px] text-muted bg-warm-soft border border-line-soft rounded-sm px-3 py-2.5">
              <b className="font-cond text-[11px] uppercase tracking-[.08em] text-warm whitespace-nowrap">Trần điểm</b>
              <span>{lead.gate}</span>
            </div>
          )}

          <div className="bg-surface-2 border border-line-soft rounded-sm p-4">
            <div className="flex items-center justify-between gap-3">
              <div className="font-cond text-[11px] uppercase tracking-[.14em] text-muted">Nháp trả lời — bạn duyệt trước khi gửi</div>
              <button onClick={() => { navigator.clipboard.writeText(lead.draft); setCopied(true); setTimeout(() => setCopied(false), 1600); }}
                className="font-mono text-[11px] px-2 py-1 rounded-sm border border-line text-muted hover:border-accent hover:text-accent">
                {copied ? "đã chép" : "chép"}
              </button>
            </div>
            <p className="mt-2 whitespace-pre-wrap text-[14px] leading-relaxed">{lead.draft}</p>
          </div>

          <div className="flex flex-wrap gap-2">
            <a href={lead.url} target="_blank" rel="noopener"
              className="font-mono text-[12px] px-3 py-2 rounded-sm border border-accent text-accent hover:bg-accent-soft">
              Mở post gốc ↗
            </a>
            {lead.author_url && (
              <a href={lead.author_url} target="_blank" rel="noopener"
                className="font-mono text-[12px] px-3 py-2 rounded-sm border border-line text-muted hover:border-accent hover:text-accent">
                Profile u/{lead.author} ↗
              </a>
            )}
          </div>
        </div>
      )}
    </article>
  );
}
