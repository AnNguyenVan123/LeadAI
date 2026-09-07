"""Chặn lạm dụng cho bản demo công khai.

Mỗi lượt chạy tốn tiền thật (~$1 với cấu hình hiện tại), nên trang này không thể
mở trần. Ba lớp, tất cả đọc từ biến môi trường để chỉnh mà không phải deploy lại:

  LEADAI_MAX_RUNS_PER_IP    số lượt một IP được chạy trong 24h   (mặc định 2)
  LEADAI_MAX_RUNS_PER_DAY   trần toàn hệ thống mỗi ngày          (mặc định 60)
  LEADAI_ALLOW_LIVE         cho phép quét Reddit trực tiếp       (mặc định tắt)
"""
from __future__ import annotations
import os, time
from fastapi import HTTPException, Request

from .store import _conn

PER_IP = int(os.environ.get("LEADAI_MAX_RUNS_PER_IP", "2"))
PER_DAY = int(os.environ.get("LEADAI_MAX_RUNS_PER_DAY", "60"))
ALLOW_LIVE = os.environ.get("LEADAI_ALLOW_LIVE", "0") == "1"


def client_ip(request: Request) -> str:
    # Railway và Vercel đều đứng sau proxy, nên IP thật nằm ở X-Forwarded-For.
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "?")


def check(request: Request, live: bool) -> str:
    ip = client_ip(request)
    day_ago = time.time() - 86400
    with _conn() as c:
        mine = c.execute("SELECT COUNT(*) n FROM runs WHERE ip=? AND created_at>?",
                         (ip, day_ago)).fetchone()["n"]
        total = c.execute("SELECT COUNT(*) n FROM runs WHERE created_at>?",
                          (day_ago,)).fetchone()["n"]
    if total >= PER_DAY:
        raise HTTPException(429, "Bản demo đã chạm trần lượt chạy hôm nay. "
                                 "Quay lại ngày mai, hoặc nhắn cho mình để mở thêm.")
    if mine >= PER_IP:
        raise HTTPException(429, f"Bạn đã dùng {PER_IP} lượt trong 24h qua. "
                                 f"Mỗi lượt tốn chi phí thật nên mình phải giới hạn — "
                                 f"để lại email nếu muốn chạy nhiều hơn.")
    if live and not ALLOW_LIVE:
        raise HTTPException(400, "Quét Reddit trực tiếp đang tắt ở bản công khai "
                                 "(chậm và hay bị Reddit chặn). Bản demo chấm trên kho post đã tải sẵn.")
    return ip
