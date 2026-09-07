# Intent Radar

Dán link landing page hoặc mô tả sản phẩm bằng lời → nhận về những người trên Reddit
đang thật sự gặp vấn đề đó, kèm điểm số, câu trích làm bằng chứng, và nháp trả lời.

    web/  →  Next.js 16 (App Router, TypeScript, Tailwind 4)
    api/  →  FastAPI: REST + SSE
    pipeline/  →  ICP → truy vấn → Reddit → lọc → Haiku triage → Opus bóc bằng chứng → chấm điểm

## Chạy

    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    export ANTHROPIC_API_KEY=...        # bắt buộc cho production
    export REDDIT_CLIENT_ID=...         # tạo script app ở reddit.com/prefs/apps
    export REDDIT_CLIENT_SECRET=...
    .venv/bin/uvicorn api.main:app --port 8000

    cd web && npm install && npm run dev      # http://localhost:3000

Không có `ANTHROPIC_API_KEY` thì `pipeline/llm.py` tự chuyển sang gọi `claude` CLI —
chạy được nhưng chậm và dính session limit. Không có credential Reddit thì `sources.py`
rơi về RSS công khai: vẫn là post thật nhưng Reddit bóp tốc độ và không trả về upvote.

## API

| | |
|---|---|
| `POST /api/analyze` | `{kind: "url"\|"text", value, live}` → `{run_id}` |
| `GET /api/runs/{id}/events` | SSE, mỗi chặng một event, kết thúc bằng `result` |
| `GET /api/runs/{id}` | kết quả (3 lead đầu, phần còn lại khoá) |
| `POST /api/unlock` | `{run_id, email}` → toàn bộ lead |
| `GET /api/stats` | số run và số email đã thu |

Kết quả có URL riêng: `/?run=<id>` mở lại được và chia sẻ được.

## Ba chốt chặn chống bịa

1. **Câu trích phải có thật.** `qualify._verify_quotes()` đối chiếu từng câu trích với
   nội dung post; câu nào không khớp bị xoá và mất luôn phần đóng góp vào điểm.
2. **Không lead nào không có link.** `analyze.to_wire()` từ chối bất kỳ lead nào không
   có permalink Reddit hợp lệ; mỗi lead hiện cả link post và link profile tác giả.
3. **Điểm do code tính, không do model.** Model chỉ trả về sự kiện có trích dẫn;
   `pipeline/scoring.py` mới quy ra số. Đổi trọng số → chấm lại toàn bộ lead cũ,
   không cần gọi model.

Không tìm được ai thì trả về 0 và nói rõ vì sao — đã kiểm chứng: một web app quản lý
phòng gym cho thị trường Việt Nam chạy qua kho 348 post founder SaaS cho ra đúng 0 lead.

## Coming soon (hiện trong UI, chưa bật)

Theo dõi & nhắc follow-up · Cảnh báo Intent Radar · Bộ nhớ hội thoại · Nguồn ngoài Reddit
