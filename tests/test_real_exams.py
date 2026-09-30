# -*- coding: utf-8 -*-
"""Kiểm thử với file đề thật (2025/2026) + verify seed taxonomy."""
import os, sys, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from core import db as dbm
from core.seed_taxonomy import seed_taxonomy
from core import parser as psr

dbm.init_db()
cnt = seed_taxonomy()
print("Seed taxonomy:", cnt)

conn = dbm.get_conn()
for lvl, name in [(1, "Mạch nội dung"), (2, "Nội dung"), (3, "ĐVKT"), (4, "YCCĐ")]:
    n = conn.execute("SELECT COUNT(*) c FROM taxonomy_nodes WHERE level=?", (lvl,)).fetchone()["c"]
    print(f"  Cấp {lvl} ({name}): {n} nodes")
conn.close()

# --- Parse đề thật ---
base_dir = os.path.dirname(BASE)  # TN THPT/
files = [
    os.path.join(base_dir, "1. Đề tham khảo 2025", "03_VatLi.pdf"),
    os.path.join(base_dir, "2. Đề chính thức 2025", "Vật lí_Đề thi chính thức 2025.docx"),
    os.path.join(base_dir, "3. Đề chính thức 2026", "thuvienhoclieu.com-De-thi-TN-THPT-2026-mon-Vat-Li-Li-Bo-GD-ma-de-0211.docx"),
]
for f in files:
    if not os.path.exists(f):
        print(f"\nSKIP (không tồn tại): {os.path.basename(f)}")
        continue
    try:
        qs = psr.parse_exam_file(f)
        types = {}
        for q in qs:
            types[q["question_type"]] = types.get(q["question_type"], 0) + 1
        print(f"\n[{os.path.basename(f)}] => {len(qs)} câu | {types}")
        # in mẫu 2 câu đầu (rút gọn)
        for q in qs[:2]:
            print("   -", q["question_type"], "|", q["question_text"][:90].replace("\n", " "))
            if q["options"]:
                print("     opts:", [o[:40] for o in q["options"]][:4])
    except Exception as e:
        print(f"\n[{os.path.basename(f)}] LỖI: {e}")