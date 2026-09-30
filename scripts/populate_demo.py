# -*- coding: utf-8 -*-
"""
Nạp dữ liệu demo: Đề tham khảo 2025 + Đề chính thức 2025 + Đề chính thức 2026
vào ngân hàng (từ thư mục TN THPT). Gắn taxonomy tự động + chạy kiểm tra trùng.

Chạy: python scripts/populate_demo.py
"""
import os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
ROOT = os.path.dirname(BASE)  # thư mục TN THPT

from core import db as dbm
from core import service as svc
from core import parser as psr
from core.taxo_match import auto_taxonomy
from core.seed_taxonomy import seed_taxonomy

dbm.init_db()
seed_taxonomy()

DEMOS = [
    {
        "dir": "1. Đề tham khảo 2025",
        "files": ["DE VAT LI THAM KHAO BGD 2025-MA TRAN-GIAI CHI TIET.docx"],
        "name": "Đề tham khảo TN THPT 2025 – Vật lí (kèm ma trận – lời giải)",
        "org": "Bộ GD&ĐT", "year": 2025,
        "src_group": "Đề tham khảo TN THPT",
    },
    {
        "dir": "2. Đề chính thức 2025",
        "files": ["Vật lí_Đề thi chính thức 2025.docx"],
        "name": "Đề chính thức TN THPT 2025 – Vật lí",
        "org": "Bộ GD&ĐT", "year": 2025,
        "src_group": "Đề chính thức 2025",
    },
    {
        "dir": "3. Đề chính thức 2026",
        "files": ["thuvienhoclieu.com-De-thi-TN-THPT-2026-mon-Vat-Li-Li-Bo-GD-ma-de-0211.docx"],
        "name": "Đề chính thức TN THPT 2026 – Vật lí",
        "org": "Bộ GD&ĐT", "year": 2026,
        "src_group": "Đề chính thức 2026",
    },
]

tree = svc.get_taxonomy_tree()

for demo in DEMOS:
    fpath = os.path.join(ROOT, demo["dir"], demo["files"][0])
    if not os.path.exists(fpath):
        print(f"SKIP {demo['files'][0]} (không tồn tại)")
        continue
    try:
        qs = psr.parse_exam_file(fpath)
    except Exception as e:
        print(f"LỖI parse {demo['files'][0]}: {e}")
        continue
    if not qs:
        print(f"SKIP {demo['files'][0]} — 0 câu (có thể file scan, cần OCR)")
        continue

    # tạo source + exam
    sid = svc.add_source(demo["name"], demo["src_group"], demo["year"],
                         f"Tự động nạp khi tạo bộ dữ liệu demo", fpath,
                         os.path.basename(fpath))
    eid = svc.add_exam(demo["name"], demo["org"], demo["year"], "—", sid, "", fpath,
                       os.path.basename(fpath))

    ok, flagged, errs = svc.import_exam_pipeline(eid, qs)
    # sau import: gắn taxonomy tự động cho từng câu của exam này
    conn = dbm.get_conn()
    rows = conn.execute("SELECT id, question_text FROM questions WHERE exam_id=? ORDER BY question_number", (eid,)).fetchall()
    conn.close()
    n_tax = 0
    for r in rows:
        strand, content, unit, outcome = auto_taxonomy(r["question_text"], tree)
        upd = {}
        if strand: upd["strand_id"] = strand["id"]; upd["strand_name"] = strand["name"]
        if content: upd["content_id"] = content["id"]; upd["content_name"] = content["name"]
        if unit: upd["unit_id"] = unit["id"]; upd["unit_name"] = unit["name"]
        if outcome: upd["outcome_id"] = outcome["id"]; upd["outcome_name"] = outcome["name"]
        if upd:
            svc.update_question(r["id"], **upd)
            n_tax += 1
    print(f"✔ {demo['name']}: parsed={len(qs)} imported_ok={ok} flagged_dup={flagged} errors={len(errs)} taxo_gán={n_tax}")

print("\nXONG. Tổng kết ngân hàng:")
st = svc.stats_overview()
print(f"  Tổng câu: {st['total']} | Đã duyệt: {st['reviewed']} | Trùng M1: {st['dups']} | Cần thẩm định: {st['need_review']}")
for row in st["by_strand"]:
    print(f"   - {row['name']}: {row['c']}")