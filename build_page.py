"""out/leads.json -> the published Intent Radar page."""
import json, re, os, datetime as dt
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
TPL = "/private/tmp/claude-501/-Users-nguyenvanan-Projects-LeadAI/0d7d1e38-a0d2-4895-98df-f608fa89bed4/scratchpad/radar.template.html"

STAGE = {"idea": "mới có ý tưởng", "building": "đang build",
         "launched_no_users": "đã launch, chưa có user", "has_users": "đã có user",
         "has_revenue": "đã có doanh thu"}
EV = [("states_problem", "Nói rõ đang gặp đúng vấn đề"),
      ("seeking_solution", "Đang chủ động đi tìm cách giải quyết"),
      ("tried_tools", "Đã thử công cụ hoặc cách khác"),
      ("budget_signal", "Có tín hiệu sẵn sàng chi tiền"),
      ("urgency", "Có yếu tố gấp")]
GATE_VI = {"we cannot reach their customers from public forums":
           "Khách hàng của họ không xuất hiện trên forum công khai — mình không tìm hộ được",
           "no verbatim evidence they have the problem":
           "Không trích được câu nào chứng minh họ đang gặp vấn đề"}


def age_vi(days):
    d = round(days)
    return "hôm nay" if d == 0 else f"{d} ngày trước"


def main():
    src = json.load(open(f"{ROOT}/out/leads.json"))
    log = open(f"{ROOT}/out/run.log").read()
    g = lambda pat, d=0: int(m.group(1)) if (m := re.search(pat, log)) else d

    leads = []
    for l in src["leads"]:
        j = l["judgement"]
        leads.append(dict(
            title=l["title"], subreddit=l["subreddit"], author=l["author"], url=l["url"],
            age=age_vi(l["age_days"]), found_via=l["found_via"],
            tier=l["tier"], score=l["score"], factors=l["factors"],
            one_line=f"{STAGE.get(j['stage'], j['stage'])} · bán cho {j['sells_to']}",
            problem=j["problem_statement"],
            evidence=[dict(label=lab, present=j["evidence"].get(k, {}).get("present", False),
                           quote=j["evidence"].get(k, {}).get("quote", "")) for k, lab in EV],
            why=j["why"], risk=j.get("risk", ""),
            gate=GATE_VI.get(l.get("gate") or "", l.get("gate") or ""),
            draft=j["draft_reply"]))

    scanned = src["posts_scanned"]
    pre = g(r"prefilter\s+\d+ -> (\d+)")
    tri = g(r"triage \(haiku\)\s+-> (\d+)")
    qua = g(r"qualify \(opus\)\s+-> (\d+)")
    funnel = [
        dict(label="post kéo về từ Reddit", n=scanned, drop=scanned - pre),
        dict(label="qua bộ lọc tĩnh (0 token)", n=pre, drop=pre - tri),
        dict(label="qua triage Haiku 4.5", n=tri, drop=max(0, tri - qua)),
        dict(label="Opus 5 bóc bằng chứng", n=qua, drop=qua - len(leads)),
        dict(label="lead còn lại sau hard gate", n=len(leads), drop=0),
    ]

    data = dict(
        run_at=dt.datetime.fromisoformat(src["run_at"]).strftime("%d/%m/%Y %H:%M"),
        posts_scanned=scanned,
        icp="Founder / dev solo đã build xong sản phẩm nhưng chưa có khách trả tiền.",
        method=(f"{scanned} post thật kéo từ Reddit. Mỗi lead đi qua 4 chặng: lọc tĩnh, "
                f"triage bằng Haiku 4.5, bóc bằng chứng bằng Opus 5, rồi chấm điểm bằng code. "
                f"Mô hình không bao giờ được hỏi \"cho điểm 0-100\" — nó chỉ trả về sự kiện kèm "
                f"câu trích, và mọi câu trích đều được đối chiếu lại với post gốc trước khi tính điểm."),
        feeds=[dict(sub=k.split(" · ")[0].replace("r/", ""), query=k.split(" · ")[1], n=v)
               for k, v in Counter(l["found_via"] for l in src["leads"]).items()],
        funnel=funnel, leads=leads)

    out = open(TPL).read().replace("__DATA__", json.dumps(data, ensure_ascii=False))
    open(f"{ROOT}/intent-radar-demo.html", "w").write(out)
    print(f"built {len(out)} bytes · {len(leads)} leads · funnel {[f['n'] for f in funnel]}")


if __name__ == "__main__":
    main()
