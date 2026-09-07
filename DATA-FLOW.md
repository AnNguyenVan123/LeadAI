# Landing Page — Data Flow

Trang: `landing.html` → https://claude.ai/code/artifact/ef770ba3-35ed-42c9-8403-3a5e4a1d246f
Funnel dashboard: thêm `?metrics=1` vào cuối URL.

Bám theo doc §26 (Landing Page Funnel) và §28 (Core Validation Metrics).

## 1. Funnel

```
Visitor mở trang
      │  → tạo doc  sessions/{sid}
      ▼
Click CTA (hero / nav / final)
      │  → sessions/{sid}.cta_clicks++, opened_form = true
      ▼
Step 1 — Email                    ← LEAD ĐƯỢC LƯU TỪ ĐÂY
      │  → tạo doc  signups/{leadId}, furthest_step = 1
      ▼
Step 2 — "What are you building?"
      │  → signups/{leadId}.building, furthest_step = 2
      ▼
Step 3 — ICP + kênh đang dùng
      │  → signups/{leadId}.icp + .channels, furthest_step = 3
      ▼
Step 4 — Beta interest
         → .beta_interest, completed = true, furthest_step = 4
```

Điểm thiết kế quan trọng: **mỗi step ghi ngay khi submit**, không đợi tới cuối.
Người bỏ giữa chừng vẫn được lưu, và `furthest_step` cho biết họ rớt ở đâu.
Nút "I'll send this later" ở step 2/3 giữ lại email thay vì mất trắng lead.

## 2. Schema

### `signups/{leadId}` — một doc / một lead
```json
{
  "created_at": "2026-09-07T…", "updated_at": "2026-09-07T…",
  "email": "…",
  "building": "…",          // step 2 — input cho Concierge MVP (§27)
  "icp": "…",               // step 3
  "channels": ["Reddit", "X / Twitter"],
  "beta_interest": "now" | "later" | "watching",
  "furthest_step": 1-4,
  "completed": true,
  "session_id": "…", "referrer": "…",
  "utm": { "utm_source": "…", "utm_campaign": "…", "ref": "…" }
}
```

### `sessions/{sid}` — một doc / một visitor
```json
{
  "created_at": "…", "last_seen": "…",
  "cta_clicks": 2, "cta_from": "hero",
  "opened_form": true, "reached_step": 3, "converted": false,
  "lead_id": "…", "referrer": "…", "utm": { … }
}
```

`sid` nằm trong `localStorage` nên visitor quay lại không bị đếm hai lần.
Mỗi doc chỉ có **một writer duy nhất** (chính tab đó) → không có race, không cần counter cộng dồn.

## 3. Đọc số liệu

**Cách 1 — dashboard trong trang:** mở URL + `?metrics=1`.
Có funnel đầy đủ với % chuyển đổi từng bước, và danh sách founder kèm
startup idea + ICP của họ — chính là hàng đợi để chạy Concierge MVP (§27).

**Cách 2 — hỏi Claude:** "đọc signups từ landing page" — mình query trực tiếp
qua `read_db` và trả về số hoặc export ra file.

## 4. Metric ánh xạ sang §28

| Doc | Đọc ở đâu |
|---|---|
| Signup rate | `Email submitted / Visitors` |
| Intent thật (§26) | `ICP submitted / Email submitted` — người chịu mô tả ICP mới là tín hiệu mạnh |
| Ưu tiên concierge | `beta_interest == "now"` |
| Kênh đang dùng | `channels` — nếu ít ai chọn Reddit thì nguồn đầu tiên cần xem lại (§35 PIVOT) |

Các metric còn lại của §28 (acceptance rate, action rate, reply rate) **không đo được ở
landing page** — chúng chỉ xuất hiện sau khi bạn giao lead report thật. Trang này chỉ
chịu trách nhiệm tới `Beta interest`.

## 5. Ngưỡng quyết định gợi ý

Sau ~200 visitor có định hướng (không phải traffic rác):

- `ICP submitted / Visitors` ≥ 4% → tín hiệu tốt, chạy Concierge MVP ngay
- 1–4% → có nhu cầu nhưng messaging chưa trúng, sửa headline/hero trước
- < 1% và không ai chọn `"now"` → xem lại §35 (PIVOT / STOP)

Bản thân `beta_interest == "now"` ≥ 5 người là đủ để chạy trọn §27.

## 6. Giới hạn cần biết

- Artifact có khai báo `db` nên **không share public được** — chỉ người đã đăng nhập
  trong workspace của bạn và được share mới mở được. Dùng để test luồng và demo nội bộ.
  Muốn chạy validation thật với founder ngoài (Reddit, X, IndieHackers) thì deploy
  `landing.html` lên host công khai và thay hai hàm `saveSession()` / `saveLead()`
  bằng `fetch()` tới endpoint của bạn — schema ở mục 2 giữ nguyên.
- Store tối đa 5.000 doc. Sessions ăn nhiều nhất; khi tới ~4.000 thì export rồi xóa
  bớt `sessions` cũ (`signups` giữ lại).
- Counter social proof chỉ hiện khi ≥ 10 signup, để không hiện "0 founders".
