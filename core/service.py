# -*- coding: utf-8 -*-
"""
Service layer – các thao tác nghiệp vụ trên DB (dùng cho UI Streamlit và CLI).
"""
import json
import os
import shutil
from datetime import datetime

from . import db as dbm
from .db import now, get_conn, rows_to_dicts, qrow_to_dict
from . import duplicate as dup
from . import classifier as clf

# ------------------------------------------------------------------ NGUỒN
def add_source(name, group_name, year=None, description="", file_path="", file_name="", status="Đang sử dụng"):
    conn = get_conn()
    cur = conn.cursor()
    t = now()
    cur.execute(
        "INSERT INTO sources(name, group_name, year, description, file_path, file_name, status, created_at, updated_at)"
        " VALUES(?,?,?,?,?,?,?,?,?)",
        (name, group_name, year, description, file_path, file_name, status, t, t),
    )
    conn.commit()
    sid = cur.lastrowid
    conn.close()
    return sid


def list_sources():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM sources ORDER BY group_name, year DESC, id DESC").fetchall()
    conn.close()
    return rows_to_dicts(rows)


def update_source(sid, **fields):
    conn = get_conn()
    cur = conn.cursor()
    allowed = {"name", "group_name", "year", "description", "file_path", "file_name", "status"}
    sets = {k: v for k, v in fields.items() if k in allowed}
    sets["updated_at"] = now()
    cur.execute(
        f"UPDATE sources SET {', '.join(f'{k}=?' for k in sets)} WHERE id=?",
        (*sets.values(), sid),
    )
    conn.commit()
    conn.close()


def delete_source(sid):
    conn = get_conn()
    conn.execute("DELETE FROM sources WHERE id=?", (sid,))
    conn.commit()
    conn.close()


# ------------------------------------------------------------------ TAXONOMY
def add_taxonomy_node(level, name, parent_id=None, grade="", source="", note="", code=""):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO taxonomy_nodes(level, name, grade, parent_id, source, note, code) VALUES(?,?,?,?,?,?,?)",
        (level, name, grade, parent_id, source, note, code),
    )
    conn.commit()
    nid = cur.lastrowid
    conn.close()
    return nid


def update_taxonomy_node(nid, name=None, grade=None, note=None):
    conn = get_conn()
    cur = conn.cursor()
    sets, vals = [], []
    if name is not None:
        sets.append("name=?"); vals.append(name)
    if grade is not None:
        sets.append("grade=?"); vals.append(grade)
    if note is not None:
        sets.append("note=?"); vals.append(note)
    if sets:
        cur.execute(f"UPDATE taxonomy_nodes SET {', '.join(sets)} WHERE id=?", (*vals, nid))
        conn.commit()
    conn.close()


def delete_taxonomy_node(nid):
    """Xóa node + subtree (câu hỏi tham chiếu sẽ có taxonomy rỗng)."""
    conn = get_conn()
    conn.execute("PRAGMA recursive_triggers=ON")
    # xóa con trước
    conn.execute("DELETE FROM taxonomy_nodes WHERE id IN (WITH RECURSIVE sub(id) AS "
                 "(SELECT ? UNION ALL SELECT t.id FROM taxonomy_nodes t JOIN sub ON t.parent_id=sub.id) SELECT id FROM sub)", (nid,))
    conn.commit()
    conn.close()


def get_taxonomy_tree():
    """Trả cây: list [ {id, name, grade, level, children:[...]} ] (cấp 1..4)."""
    conn = get_conn()
    rows = conn.execute("SELECT * FROM taxonomy_nodes ORDER BY level, sort_order, id").fetchall()
    conn.close()
    nodes = rows_to_dicts(rows)
    by_parent = {}
    for n in nodes:
        by_parent.setdefault(n["parent_id"], []).append(n)
    def build(pid):
        out = []
        for n in by_parent.get(pid, []):
            out.append({**n, "children": build(n["id"])})
        return out
    return build(None)


def taxonomy_lookup(text, topn=5):
    """Gợi ý node taxonomy theo từ khóa (tìm trong name)."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, level, name, grade, parent_id FROM taxonomy_nodes WHERE name LIKE ? ORDER BY level LIMIT ?",
        (f"%{text}%", topn),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


# ------------------------------------------------------------------ ĐỀ THI
def add_exam(name, organization="", year=None, exam_code="", source_id=None, note="", file_path="", file_name=""):
    conn = get_conn()
    cur = conn.cursor()
    t = now()
    cur.execute(
        "INSERT INTO exams(name, organization, year, exam_code, source_id, note, file_path, file_name, created_at, updated_at)"
        " VALUES(?,?,?,?,?,?,?,?,?,?)",
        (name, organization, year, exam_code, source_id, note, file_path, file_name, t, t),
    )
    conn.commit()
    eid = cur.lastrowid
    conn.close()
    return eid


def list_exams():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM exams ORDER BY id DESC").fetchall()
    conn.close()
    return rows_to_dicts(rows)


def delete_exam(eid):
    conn = get_conn()
    conn.execute("DELETE FROM exams WHERE id=?", (eid,))
    conn.commit()
    conn.close()


# ------------------------------------------------------------------ CÂU HỎI
def add_question(q, check_duplicates=True):
    """
    Thêm câu hỏi. Nếu check_duplicates, tự chạy phát hiện trùng với ngân hàng
    (chỉ so với câu Đã duyệt hoặc đang chờ — tất cả đã có trong bảng).
    Trả (qid, duplicate_flag)
    """
    conn = get_conn()
    cur = conn.cursor()

    dup_status, sim_score, related, cands = "", 0.0, [], []
    if check_duplicates:
        bank = conn.execute(
            "SELECT id, question_text, options, answer FROM questions WHERE review_status IN ('Đã duyệt','Chờ duyệt')"
        ).fetchall()
        bank_rows = rows_to_dicts(bank)
        dup_status, sim_score, related, cands = dup.flag_question(q, bank_rows)

    t = now()
    cur.execute(
        """INSERT INTO questions(
          source_id, source_name, year, organization, exam_name, exam_code, exam_id, question_number,
          question_type, question_text, options, answer, solution, image_path, formulas, table_data,
          strand_id, strand_name, content_id, content_name, unit_id, unit_name, outcome_id, outcome_name,
          cognitive_level, difficulty, duplicate_status, similarity_score, related_question_ids,
          classification_confidence, classification_basis, review_status, reviewer, review_note,
          created_at, updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            q.get("source_id"), q.get("source_name", ""), q.get("year"), q.get("organization", ""),
            q.get("exam_name", ""), q.get("exam_code", ""), q.get("exam_id"),
            q.get("question_number"),
            q.get("question_type", ""), q.get("question_text", ""),
            json.dumps(q.get("options", []), ensure_ascii=False),
            q.get("answer", ""), q.get("solution", ""), q.get("image_path", ""),
            json.dumps(q.get("formulas", []), ensure_ascii=False),
            json.dumps(q.get("table_data", ""), ensure_ascii=False),
            q.get("strand_id"), q.get("strand_name", ""),
            q.get("content_id"), q.get("content_name", ""),
            q.get("unit_id"), q.get("unit_name", ""),
            q.get("outcome_id"), q.get("outcome_name", ""),
            q.get("cognitive_level", ""), q.get("difficulty", ""),
            dup_status, sim_score, json.dumps(related, ensure_ascii=False),
            q.get("classification_confidence", 0), q.get("classification_basis", ""),
            q.get("review_status", "Chờ duyệt"), q.get("reviewer", ""), q.get("review_note", ""),
            t, t,
        ),
    )
    conn.commit()
    qid = cur.lastrowid
    conn.close()
    return qid, {"duplicate_status": dup_status, "similarity_score": sim_score,
                 "related": related, "candidates": cands}


def update_question(qid, **fields):
    conn = get_conn()
    cur = conn.cursor()
    allowed = {
        "source_id", "source_name", "year", "organization", "exam_name", "exam_code", "exam_id",
        "question_number", "question_type", "question_text", "options", "answer", "solution",
        "image_path", "strand_id", "strand_name", "content_id", "content_name", "unit_id", "unit_name",
        "outcome_id", "outcome_name", "cognitive_level", "difficulty", "duplicate_status",
        "similarity_score", "related_question_ids", "classification_confidence", "classification_basis",
        "review_status", "reviewer", "review_note",
    }
    sets, vals = {}, []
    for k, v in fields.items():
        if k not in allowed:
            continue
        if k in ("options", "related_question_ids", "formulas") and not isinstance(v, str):
            v = json.dumps(v, ensure_ascii=False)
        sets[k] = v
    if "updated_at" not in sets:
        sets["updated_at"] = now()
    if sets:
        cur.execute(f"UPDATE questions SET {', '.join(f'{k}=?' for k in sets)} WHERE id=?", (*sets.values(), qid))
        conn.commit()
    conn.close()


def get_question(qid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()
    conn.close()
    return qrow_to_dict(row) if row else None


def list_questions(filters=None, limit=5000):
    """filters: dict gồm review_status, strand_name, content_name, unit_name, question_type,
    cognitive_level, difficulty, year, organization, source_name, duplicate_status, q (keyword)"""
    conn = get_conn()
    sql = "SELECT * FROM questions WHERE 1=1"
    params = []
    f = filters or {}
    if f.get("review_status"):
        sql += " AND review_status=?"; params.append(f["review_status"])
    if f.get("strand_name"):
        sql += " AND strand_name=?"; params.append(f["strand_name"])
    if f.get("content_name"):
        sql += " AND content_name=?"; params.append(f["content_name"])
    if f.get("unit_name"):
        sql += " AND unit_name=?"; params.append(f["unit_name"])
    if f.get("question_type"):
        sql += " AND question_type=?"; params.append(f["question_type"])
    if f.get("cognitive_level"):
        sql += " AND cognitive_level=?"; params.append(f["cognitive_level"])
    if f.get("difficulty"):
        sql += " AND difficulty=?"; params.append(f["difficulty"])
    if f.get("year"):
        sql += " AND year=?"; params.append(f["year"])
    if f.get("organization"):
        sql += " AND organization LIKE ?"; params.append(f"%{f['organization']}%")
    if f.get("source_name"):
        sql += " AND source_name=?"; params.append(f["source_name"])
    if f.get("duplicate_status"):
        sql += " AND duplicate_status=?"; params.append(f["duplicate_status"])
    if f.get("q"):
        sql += " AND (question_text LIKE ? OR question_text LIKE ? OR answer LIKE ?)"
        kw = f"%{f['q']}%"
        params += [kw, kw, kw]
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [qrow_to_dict(r) for r in rows]


def review_question(qid, review_status, reviewer="", review_note="", **extra):
    """Duyệt câu: đạt -> Đã duyệt; trùng -> Trùng 100%/Gần trùng; ..."""
    upd = {"review_status": review_status, "reviewer": reviewer}
    if review_note:
        upd["review_note"] = review_note
    upd.update(extra)
    update_question(qid, **upd)


def approve_to_bank(qid, reviewer="", review_note=""):
    """Duyệt đạt: gỡ trạng thái trùng (nếu câu vẫn trùng level 1 thì không cho)."""
    q = get_question(qid)
    if q and q.get("duplicate_status", "").startswith("Mức 1"):
        return False, "Câu đang là TRÙNG 100% — không được duyệt vào ngân hàng."
    review_question(qid, "Đã duyệt", reviewer, review_note)
    return True, "OK"


def stats_overview():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) c FROM questions").fetchone()["c"]
    reviewed = conn.execute("SELECT COUNT(*) c FROM questions WHERE review_status='Đã duyệt'").fetchone()["c"]
    dups = conn.execute("SELECT COUNT(*) c FROM questions WHERE duplicate_status LIKE 'Mức 1%'").fetchone()["c"]
    need_review = conn.execute(
        "SELECT COUNT(*) c FROM questions WHERE review_status IN ('Chờ duyệt','Cần thẩm định','Gần trùng')"
    ).fetchone()["c"]
    by_strand = rows_to_dicts(conn.execute(
        "SELECT COALESCE(strand_name,'(chưa gắn)') name, COUNT(*) c FROM questions GROUP BY strand_name ORDER BY c DESC"
    ).fetchall())
    by_type = rows_to_dicts(conn.execute(
        "SELECT COALESCE(question_type,'(chưa gắn)') name, COUNT(*) c FROM questions GROUP BY question_type ORDER BY c DESC"
    ).fetchall())
    by_level = rows_to_dicts(conn.execute(
        "SELECT COALESCE(cognitive_level,'(chưa gắn)') name, COUNT(*) c FROM questions GROUP BY cognitive_level ORDER BY c DESC"
    ).fetchall())
    conn.close()
    return {
        "total": total, "reviewed": reviewed, "dups": dups, "need_review": need_review,
        "by_strand": by_strand, "by_type": by_type, "by_level": by_level,
    }


def import_exam_pipeline(exam_id, questions, taxonomy_pairs=None, reviewer=""):
    """
    Pipeline nạp đề: với mỗi câu -> phân loại heuristic -> kiểm tra trùng -> thêm vào DB.
    taxonomy_pairs: list (strand_name, content_name, unit_name, outcome_name) theo câu (optional).
    Trả (ok_count, flagged_count, errors).
    """
    exam = None
    conn = get_conn()
    row = conn.execute("SELECT * FROM exams WHERE id=?", (exam_id,)).fetchone()
    conn.close()
    if row:
        exam = rows_to_dicts([row])[0]

    ok, flagged, errors = 0, 0, []
    for idx, q in enumerate(questions):
        try:
            cl = clf.heuristic_classify(q)
            q["question_type"] = q.get("question_type") or cl["question_type"]
            if cl.get("content_strand"):
                q["strand_name"] = cl["content_strand"]          # ghi mạch → giao diện hiển thị ngay
            q["cognitive_level"] = cl["cognitive_level"]
            q["difficulty"] = cl["difficulty"]
            q["classification_confidence"] = cl["confidence"]
            q["classification_basis"] = cl["classification_basis"]
            if exam:
                q.setdefault("source_id", exam.get("source_id"))
                q.setdefault("year", exam.get("year"))
                q.setdefault("organization", exam.get("organization"))
                q.setdefault("exam_name", exam.get("name"))
                q.setdefault("exam_code", exam.get("exam_code"))
                q["exam_id"] = exam["id"]
            qid, dup_info = add_question(q, check_duplicates=True)
            if dup_info["duplicate_status"]:
                flagged += 1
            else:
                ok += 1
        except Exception as e:  # pragma: no cover
            errors.append(f"Câu {q.get('question_number')}: {e}")
    return ok, flagged, errors


def bulk_update_taxonomy(qids, strand_id=None, strand_name=None, content_id=None, content_name=None,
                         unit_id=None, unit_name=None, outcome_id=None, outcome_name=None):
    for qid in qids:
        q = get_question(qid)
        if not q:
            continue
        upd = {}
        if strand_id: upd["strand_id"] = strand_id; upd["strand_name"] = strand_name
        if content_id: upd["content_id"] = content_id; upd["content_name"] = content_name
        if unit_id: upd["unit_id"] = unit_id; upd["unit_name"] = unit_name
        if outcome_id: upd["outcome_id"] = outcome_id; upd["outcome_name"] = outcome_name
        if upd:
            update_question(qid, **upd)


def save_upload(uploaded_file, subdir="uploads"):
    """Lưu file upload vào data/uploads, trả đường dẫn + tên."""
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", subdir)
    os.makedirs(base, exist_ok=True)
    safe = os.path.basename(uploaded_file.name).replace(" ", "_")
    dst = os.path.join(base, f"{int(datetime.now().timestamp())}_{safe}")
    with open(dst, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return dst, safe