const ITEMS = [
  { title: "Theo dõi & nhắc follow-up", body: "Ai đã trả lời, ai im lặng, ai cần nhắc lại sau 3 ngày. Trạng thái chạy theo từng lead thay vì nằm trong đầu bạn." },
  { title: "Cảnh báo Intent Radar", body: "Có người vừa đăng đúng vấn đề bạn giải — báo ngay, không cần mở dashboard." },
  { title: "Bộ nhớ hội thoại", body: "Mọi thứ đã biết về một người: post cũ, lần bạn nhắn, họ trả lời gì, họ đã dùng tool nào." },
  { title: "Thêm nguồn ngoài Reddit", body: "X, Hacker News, IndieHackers, group Facebook — cùng một cách chấm điểm." },
];

export default function ComingSoon() {
  return (
    <section className="mt-14">
      <div className="flex items-baseline gap-3">
        <h2 className="font-cond font-semibold text-[15px]">Đang làm tiếp</h2>
        <span className="font-mono text-[11px] text-muted">chưa bật trong bản demo này</span>
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
