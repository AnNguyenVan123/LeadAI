"use client";
import { useState } from "react";

const EXAMPLES = [
  { label: "Tool đặt lịch cho phòng gym", text: "Mình làm một web app giúp phòng gym nhỏ quản lý lịch tập cá nhân và nhắc học viên qua Zalo. Khách là chủ phòng gym 1-2 cơ sở, hiện đang ghi lịch bằng Excel và Zalo." },
  { label: "SaaS phân tích review", text: "I built a tool that reads all your app store reviews and tells you which feature complaints are growing week over week. For indie iOS developers with a live app who don't have time to read reviews." },
];

export default function InputCard({ onRun, busy, liveEnabled, perIp }: {
  onRun: (kind: "url" | "text", value: string, live: boolean) => void;
  busy: boolean;
  liveEnabled: boolean;
  perIp: number;
}) {
  const [kind, setKind] = useState<"url" | "text">("text");
  const [value, setValue] = useState("");
  const [live, setLive] = useState(false);
  const ok = kind === "url" ? /\./.test(value) : value.trim().length >= 40;

  return (
    <div className="rounded border border-line bg-surface p-5 sm:p-7 shadow-[0_1px_2px_rgba(20,24,26,.04),0_16px_40px_-32px_rgba(20,24,26,.5)]">
      <div className="flex gap-1 mb-4">
        {([["text", "Mô tả bằng lời"], ["url", "Dán link landing page"]] as const).map(([k, label]) => (
          <button key={k} onClick={() => setKind(k)} disabled={busy}
            className={`font-mono text-xs px-3 py-2 rounded-sm border transition-colors ${
              kind === k ? "bg-ink text-ground border-ink" : "bg-surface text-muted border-line hover:border-muted"}`}>
            {label}
          </button>
        ))}
      </div>

      {kind === "url" ? (
        <input value={value} onChange={(e) => setValue(e.target.value)} disabled={busy}
          placeholder="vd. yourproduct.com"
          className="w-full rounded-sm border border-line bg-surface-2 px-3 py-3 text-[15px] outline-none focus:border-accent focus:bg-surface" />
      ) : (
        <textarea value={value} onChange={(e) => setValue(e.target.value)} disabled={busy} rows={5}
          placeholder="Sản phẩm của bạn giải quyết vấn đề gì, cho ai? Viết như đang kể cho một người bạn — không cần trau chuốt."
          className="w-full rounded-sm border border-line bg-surface-2 px-3 py-3 text-[15px] leading-relaxed outline-none focus:border-accent focus:bg-surface resize-y" />
      )}

      {kind === "text" && (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="font-cond text-[11px] uppercase tracking-[.14em] text-muted">Thử nhanh</span>
          {EXAMPLES.map((ex) => (
            <button key={ex.label} onClick={() => setValue(ex.text)} disabled={busy}
              className="font-mono text-[11px] px-2.5 py-1.5 rounded-full border border-line text-muted hover:border-accent hover:text-accent">
              {ex.label}
            </button>
          ))}
        </div>
      )}

      <div className="mt-5 flex flex-wrap items-center justify-between gap-4">
        {liveEnabled ? (
          <label className="flex items-center gap-2 text-[13px] text-muted cursor-pointer">
            <input type="checkbox" checked={live} onChange={(e) => setLive(e.target.checked)} disabled={busy}
              className="accent-[color:var(--color-accent)]" />
            Quét Reddit mới thay vì kho đã tải sẵn
            <span className="font-mono text-[11px] text-warm">chậm 2-4 phút</span>
          </label>
        ) : (
          <p className="text-[12.5px] text-muted">
            Chấm trên kho post Reddit đã tải sẵn{perIp ? ` · ${perIp} lượt/ngày mỗi người` : ""}
          </p>
        )}
        <button onClick={() => onRun(kind, value.trim(), live)} disabled={!ok || busy}
          className="font-cond font-semibold tracking-wide px-6 py-3 rounded-sm bg-accent text-white disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-110">
          {busy ? "Đang tìm…" : "Tìm người đang cần nó"}
        </button>
      </div>
    </div>
  );
}
