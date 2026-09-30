# -*- coding: utf-8 -*-
"""E2E test với đề thật: pipeline nạp -> trùng -> duyệt -> export."""
import os, sys, shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from core import db as dbm
from core import service as svc
from core import parser as psr
from core import duplicate as dup
from core.seed_taxonomy import seed_taxonomy

dbm.init_db()
seed_taxonomy()

# dọn DB test
conn = dbm.get_conn()
conn.execute("DELETE FROM questions"); conn.execute("DELETE FROM exams"); conn.execute("DELETE FROM sources")
conn.commit(); conn.close()

exam_file = os.path.join(os.path.dirname(BASE), "2. Đề chính thức 2025", "Vật lí_Đề thi chính thức 2025.docx")
assert os.path.exists(exam_file), exam_file

qs = psr.parse_exam_file(exam_file)
print(f"Parse: {len(qs)} câu")

# 1) Pipeline import (trống ngân hàng -> không flag)
exam_id = svc.add_exam("Đề chính thức 2025", "Bộ GD&ĐT", 2025, "Đề chính thức", source_id=None)
ok, flagged, errs = svc.import_exam_pipeline(exam_id, qs)
print(f"Import: ok={ok} flagged={flagged} errs={len(errs)}")
assert ok + flagged == len(qs), "mất câu khi import"

# 2) Thêm lại câu 1 (giống 100%) -> phải flag Mức 1
q1 = svc.list_questions({"q": "đẳng áp"})[0]
new_q = dict(q1); new_q.pop("id", None)
qid, dupinfo = svc.add_question(new_q, check_duplicates=True)
print(f"Câu trùng: {dupinfo['duplicate_status']} score={dupinfo['similarity_score']}")
assert dupinfo["duplicate_status"].startswith("Mức 1"), dupinfo

# 3) Duyệt 1 câu OK -> vào ngân hàng (chọn câu KHÔNG flag trùng)
clean = [q for q in svc.list_questions({"review_status": "Chờ duyệt"}, limit=100)
         if not (q.get("duplicate_status") or "").startswith("Mức 1")]
ok_q = clean[0]
ok, msg = svc.approve_to_bank(ok_q["id"], reviewer="E2E")
print(f"Approve: {ok} {msg}")
assert ok

# 4) Export toàn bộ 29 câu thành Word
from core import exporter as exp
sel = svc.list_questions(limit=100)
out = os.path.join(BASE, "data", "exports", "e2e_de.docx")
exp.export_exam(sel, out, "ĐỀ E2E", with_answer=True, with_solution=False)
assert os.path.getsize(out) > 5000
print(f"Export Word OK: {out} ({os.path.getsize(out)} bytes)")

print("E2E PASS ✔")