# -*- coding: utf-8 -*-
"""Test sửa hiển thị: công thức MathType (ảnh) + tách lời giải khỏi phương án."""
import os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from core import parser as psr
from core import service as svc
from core import db as dbm

f = r"G:\Other computers\My Laptop\THIỀU DUNG\7. TÀI LIỆU ĐỊNH HƯỚNG CÁC KÌ THI\TN THPT\2. Đề chính thức 2025\Vật lí_Đề thi chính thức 2025.docx"
qs = psr.parse_exam_file(f)
assert qs, "không parse được"
print(f"[1] Parse Đề chính thức 2025: {len(qs)} câu")

# Kiểm tra: câu có công thức nằm trong options
with_formula = [q for q in qs if q.get("formulas")]
print(f"[2] Số câu có công thức MathType: {len(with_formula)}")
assert with_formula, "KHÔNG có câu nào có công thức!"
q0 = with_formula[0]
print(f"    Q{q0['question_number']} formulas keys: {list(q0['formulas'].keys())[:6]}")
print(f"    lead: {q0['question_text'][:120]}")
assert any("[[FORMULA:" in (o or "") for o in q0["options"]), "placeholder không nằm trong options"

# Kiểm tra ảnh công thức tồn tại
all_paths = [p for q in qs for p in q["formulas"].values() if isinstance(p, str) and p != "UNCONVERTED"]
print(f"[3] Ảnh công thức PNG tồn tại: {sum(os.path.exists(p) for p in all_paths)}/{len(all_paths)}")

# Tách lời giải khỏi options (file tham khảo có lời giải)
f2 = r"G:\Other computers\My Laptop\THIỀU DUNG\7. TÀI LIỆU ĐỊNH HƯỚNG CÁC KÌ THI\TN THPT\1. Đề tham khảo 2025\DE VAT LI THAM KHAO BGD 2025-MA TRAN-GIAI CHI TIET.docx"
qs2 = psr.parse_exam_file(f2)
dinh = sum(1 for q in qs2 for o in q["options"] if "Hướng dẫn" in o or "Chọn" in o or "Giải" in o)
print(f"[4] Đề tham khảo 2025: {len(qs2)} câu | options dính lời giải: {dinh}")
assert dinh == 0, f"còn {dinh} options dính lời giải"
n_sol = sum(1 for q in qs2 if q.get("solution"))
print(f"    Số câu có lời giải đã tách: {n_sol}")

# Lưu vào DB với formulas
conn = dbm.get_conn()
conn.execute("DELETE FROM questions"); conn.execute("DELETE FROM exams"); conn.execute("DELETE FROM sources")
conn.commit(); conn.close()
eid = svc.add_exam("Test CT 2025 formulas", "Bộ GD&ĐT", 2025, "M021", None)
for q in qs[:6]:
    svc.add_question({**q, "exam_id": eid, "exam_name": "Test CT 2025 formulas",
                      "year": 2025, "organization": "Bộ GD&ĐT"}, check_duplicates=False)
got = svc.list_questions({"q": ""}, limit=10) if False else svc.list_questions({}, limit=10)
with_form = [q for q in got if q.get("formulas")]
print(f"[5] DB lưu: {len(got)} câu | {len(with_form)} có formulas")
assert with_form, "formulas không được lưu vào DB"
fm = with_form[0]["formulas"]
print(f"    Q{with_form[0]['id']} formulas type={type(fm).__name__}, keys={list(fm.keys())[:4] if isinstance(fm,dict) else fm}")
assert isinstance(fm, dict) and len(fm) > 0

# Export Word có ảnh công thức
from core import exporter as exp
out = os.path.join(BASE, "data", "exports", "test_formula_export.docx")
exp.export_exam(with_form[:2], out, "ĐỀ KIỂM TRA CÔNG THỨC", with_answer=True)
import zipfile
z = zipfile.ZipFile(out)
media = [n for n in z.namelist() if "media" in n and n.endswith(".png")]
print(f"[6] Export Word: {os.path.getsize(out)} bytes | {len(media)} ảnh PNG nhúng")
assert len(media) >= 2, "Ảnh công thức không được nhúng vào Word"
print("\nALL PASS ✔")