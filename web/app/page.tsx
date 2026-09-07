"use client";
import { useEffect, useState } from "react";
import InputCard from "@/components/InputCard";
import Stages from "@/components/Stages";
import Results from "@/components/Results";
import ComingSoon from "@/components/ComingSoon";
import { getHealth, getRun, startRun, streamRun, type Health, type RunResult, type StageEvent } from "@/lib/api";

export default function Home() {
  const [events, setEvents] = useState<StageEvent[]>([]);
  const [run, setRun] = useState<RunResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [health, setHealth] = useState<Health | null>(null);

  useEffect(() => { getHealth().then(setHealth).catch(() => {}); }, []);

  // A finished run keeps its own URL, so results can be reopened or shared.
  useEffect(() => {
    const id = new URLSearchParams(window.location.search).get("run");
    if (!id) return;
    getRun(id).then(setRun).catch(() => setError("Không mở được kết quả của run này"));
  }, []);

  async function go(kind: "url" | "text", value: string, live: boolean) {
    setBusy(true); setError(""); setRun(null); setEvents([]);
    try {
      const { run_id } = await startRun(kind, value, live);
      const { done } = streamRun(run_id, (e) => setEvents((prev) => [...prev, e]));
      await done;
      setRun(await getRun(run_id));
      window.history.replaceState(null, "", `?run=${run_id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Có lỗi xảy ra");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-3xl px-5 py-10 sm:py-16">
      <header className="mb-8">
        <div className="font-cond text-[11px] uppercase tracking-[.16em] text-muted">Reddit · bản demo</div>
        <h1 className="font-cond font-bold text-[34px] leading-[1.1] tracking-tight mt-1">Intent Radar</h1>
        <p className="mt-2 text-[15px] text-muted max-w-[54ch] leading-relaxed">
          Nói cho mình biết bạn đang bán gì. Mình đi tìm những người vừa mới viết ra
          đúng vấn đề đó trên Reddit, chấm điểm từng người kèm câu trích làm bằng chứng,
          và viết sẵn câu trả lời để bạn duyệt.
        </p>
      </header>

      <InputCard onRun={go} busy={busy} liveEnabled={health?.live_enabled ?? false}
        perIp={health?.limits.per_ip ?? 0} />

      {error && (
        <div className="mt-4 rounded border border-line bg-hot-soft px-4 py-3 text-[13.5px] text-hot">{error}</div>
      )}

      {(busy || events.length > 0) && !run && (
        <div className="mt-6"><Stages events={events} /></div>
      )}

      {run && <div className="mt-8"><Results run={run} onUpdate={setRun} /></div>}

      <ComingSoon />

      <footer className="mt-14 pt-6 border-t border-line text-[12.5px] text-muted leading-relaxed">
        Post, tác giả và link đều là dữ liệu thật trên Reddit. Điểm số do Claude bóc bằng
        chứng rồi code chấm — mọi câu trích đều được đối chiếu lại với post gốc, câu nào
        không khớp sẽ bị loại trước khi tính điểm.
      </footer>
    </main>
  );
}
