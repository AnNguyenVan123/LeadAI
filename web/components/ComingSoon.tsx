const ITEMS = [
  { title: "Tracking & Follow-ups", body: "Who replied, who ghosted, who needs a bump in 3 days. States follow the lead instead of living in your head." },
  { title: "Intent Radar Alerts", body: "Someone just posted your exact problem — get notified immediately without opening the dashboard." },
  { title: "Conversation Memory", body: "Everything known about a person: past posts, your messages, their replies, tools they use." },
  { title: "More Sources", body: "X, Hacker News, IndieHackers, Facebook groups — using the same scoring engine." },
];

export default function ComingSoon() {
  return (
    <section className="mt-14">
      <div className="flex items-baseline gap-3">
        <h2 className="font-cond font-semibold text-[15px]">Coming up</h2>
        <span className="font-mono text-[11px] text-muted">not enabled in this demo</span>
      </div>
      <div className="mt-3 grid sm:grid-cols-2 gap-3">
        {ITEMS.map((it) => (
          <div key={it.title} className="rounded border border-dashed border-line bg-surface-2/60 p-4">
            <div className="flex items-center gap-2">
              <h3 className="font-cond font-semibold text-[14px] text-muted">{it.title}</h3>
              <span className="font-mono text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-full border border-line text-muted">soon</span>
            </div>
            <p className="mt-1.5 text-[13px] text-muted leading-relaxed">{it.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
