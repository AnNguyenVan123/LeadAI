"use client";
import type { StageEvent } from "@/lib/api";

const ORDER = [
  ["icp", "Đọc sản phẩm của bạn"],
  ["prefilter", "Lọc tĩnh (không tốn token)"],
  ["triage", "Haiku 4.5 loại post không liên quan"],
  ["qualify", "Opus 5 bóc bằng chứng từ post"],
  ["score", "Chấm điểm bằng code"],
] as const;

const REACHED: Record<string, number> = {
  icp: 0, icp_done: 0, plan: 0, plan_done: 0, fetch: 0,
  prefilter: 1, triage: 2, triage_done: 2, qualify: 3, score: 4, result: 5,
};

export default function Stages({ events }: { events: StageEvent[] }) {
  const last = events[events.length - 1];
  const at = last ? REACHED[last.stage] ?? 0 : 0;
  const detail = events.filter((e) => ["icp_done", "prefilter", "triage_done", "plan_done"].includes(e.stage));

  return (
    <div className="rounded border border-line bg-surface p-5 sm:p-6">
      <ol className="flex flex-col gap-3">
        {ORDER.map(([key, label], i) => {
          const state = i < at ? "done" : i === at ? "now" : "todo";
          return (
            <li key={key} className="flex items-start gap-3 text-[14px]">
              <span className={`font-mono text-xs mt-0.5 ${
                state === "done" ? "text-accent" : state === "now" ? "text-ink" : "text-line"}`}>
                {state === "done" ? "✓" : state === "now" ? "▸" : "·"}
              </span>
              <span className={state === "todo" ? "text-muted/60" : state === "now" ? "font-medium" : "text-muted"}>
                {label}
                {state === "now" && last && <span className="block text-[13px] text-muted mt-0.5">{last.message}</span>}
              </span>
            </li>
          );
        })}
      </ol>
      {detail.length > 0 && (
        <div className="mt-4 pt-4 border-t border-line-soft flex flex-col gap-1.5">
          {detail.map((e, i) => (
            <div key={i} className="font-mono text-[11.5px] text-muted">{e.message}</div>
          ))}
        </div>
      )}
    </div>
  );
}
