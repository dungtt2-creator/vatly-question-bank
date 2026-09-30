# -*- coding: utf-8 -*-
"""
Exporter Word (python-docx).

Xuất:
  A. Ngân hàng câu hỏi (chọn nhiều câu)
  B. Đề thi hoàn chỉnh (câu hỏi + phương án; tùy chọn đáp án/lời giải/taxonomy)
  C. Đáp án riêng
  D. Câu hỏi + lời giải

Hỗ trợ:
- Hình ảnh (image_path trỏ tới file PNG/JPG) được chèn giữ nguyên.
- Công thức: lưu dạng text Unicode (vd "F = ma", "Δp = ρgΔh") — giữ nguyên nội dung.
- Bảng Đúng/Sai: tạo bảng 2 cột (Phát biểu | Đ/S) nếu câu có 4 ý a) b) c) d).
- Ô trả lời ngắn: dòng chấm chỗ trả lời.
"""
import os
import re
import json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT


def _add_question_para(doc, q, index=None, with_answer=False, with_solution=False, with_taxonomy=False):
    """Thêm 1 câu hỏi vào doc."""
    text = q.get("question_text", "")
    if index is not None:
        p = doc.add_paragraph()
        r = p.add_run(f"Câu {index}. "); r.bold = True
        # Loại bỏ số câu đã lặp trong text nếu có
        t = re.sub(r"^\s*Câu\s+\d+\s*[\.\:\)]\s*", "", text, flags=re.IGNORECASE)
        _add_text_with_formulas(doc, p, t, q)
    else:
        p = doc.add_paragraph()
        _add_text_with_formulas(doc, p, text, q)

    # Hình ảnh minh họa (image_path)
    imgs = q.get("image_path") or []
    if isinstance(imgs, str):
        imgs = [imgs]
    for im in imgs:
        if im and os.path.exists(str(im)):
            try:
                doc.add_picture(str(im), width=Cm(10))
            except Exception:
                pass

    # Phương án MCQ
    opts = q.get("options") or []
    if isinstance(opts, str):
        opts = json.loads(opts)
    letters = "ABCD"
    for i, o in enumerate(opts):
        o = re.sub(r"^\s*[A-Da-d]\s*[\.\:\)]\s*", "", str(o)).strip()
        if i < 4:
            p = doc.add_paragraph(f"{letters[i]}. ", style="List Bullet")
            # Xóa prefix vừa thêm ở run đầu (style List Bullet) rồi add text:
            # cách đơn giản: thêm text vào run sau
            p.runs[0].text = f"{letters[i]}. "
            _add_text_with_formulas(doc, p, "", q, append_run=True, opt_text=o)

    # Bảng Đúng/Sai nếu có a) b) c) d)
    qtype = q.get("question_type", "")
    if qtype == "Đúng/Sai" or re.search(r"^\s*[a-d]\s*[\.\:\)]", text, flags=re.M):
        subs = re.findall(r"(?m)^\s*([a-d])\s*[\.\:\)]\s*(.+)$", text)
        if subs:
            tbl = doc.add_table(rows=1, cols=3)
            tbl.style = "Table Grid"
            hdr = tbl.rows[0].cells
            hdr[0].text = "Ý"; hdr[1].text = "Nội dung"; hdr[2].text = "Đúng / Sai"
            for i, (letter, content) in enumerate(subs):
                row = tbl.add_row().cells
                row[0].text = letter.upper()
                row[1].text = content.strip()
                row[2].text = ""
            doc.add_paragraph()

    # Ô trả lời cho trả lời ngắn
    if q.get("question_type") == "Trả lời ngắn":
        doc.add_paragraph("Trả lời: " + "." * 40)

    if with_answer and q.get("answer"):
        p = doc.add_paragraph()
        r = p.add_run(f"Đáp án: {q['answer']}"); r.bold = True
    if with_solution and q.get("solution"):
        doc.add_paragraph(f"Hướng dẫn giải: {q['solution']}")
    if with_taxonomy:
        meta = []
        if q.get("strand_name"): meta.append(f"Mạch: {q['strand_name']}")
        if q.get("content_name"): meta.append(f"Nội dung: {q['content_name']}")
        if q.get("unit_name"): meta.append(f"ĐVKT: {q['unit_name']}")
        if q.get("outcome_name"): meta.append(f"YCCĐ: {q['outcome_name']}")
        if q.get("cognitive_level"): meta.append(f"Mức độ: {q['cognitive_level']}")
        if q.get("difficulty"): meta.append(f"Độ khó: {q['difficulty']}")
        if meta:
            p = doc.add_paragraph("[Taxonomy: " + "; ".join(meta) + "]")
            for r in p.runs:
                r.font.size = Pt(9); r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)


def _add_text_with_formulas(doc, paragraph, text, q, append_run=False, opt_text=None):
    """
    Thêm text vào paragraph; nếu trong text có [[FORMULA:n]] thì chèn ảnh công
    thức (render từ Word) tại đúng vị trí. Nếu append_run=True, thêm run mới
    (dùng cho option); opt_text là text option đã strip label.
    """
    # map công thức từ q
    fm = q.get("formulas") or {}
    if isinstance(fm, str):
        try:
            fm = json.loads(fm)
        except Exception:
            fm = {}
    if not isinstance(fm, dict):
        fm = {}

    parts = re.split(r"(\[\[FORMULA:\d+\]\])", text)
    for part in parts:
        if not part:
            continue
        mformula = re.match(r"\[\[FORMULA:(\d+)\]\]", part)
        if mformula:
            n = mformula.group(1)
            p = fm.get(str(n))
            if p and os.path.exists(str(p)):
                try:
                    run = paragraph.add_run()
                    run.add_picture(str(p), width=Cm(4))
                except Exception:
                    paragraph.add_run("[công thức]")
            else:
                paragraph.add_run("[công thức]")
        else:
            paragraph.add_run(part)

    # nếu option text rời (append_run mode) thì thêm sau
    if append_run and opt_text:
        parts2 = re.split(r"(\[\[FORMULA:\d+\]\])", opt_text)
        for part in parts2:
            if not part:
                continue
            mformula = re.match(r"\[\[FORMULA:(\d+)\]\]", part)
            if mformula:
                n = mformula.group(1)
                p = fm.get(str(n))
                if p and os.path.exists(str(p)):
                    try:
                        run = paragraph.add_run()
                        run.add_picture(str(p), width=Cm(4))
                    except Exception:
                        paragraph.add_run("[công thức]")
                else:
                    paragraph.add_run("[công thức]")
            else:
                paragraph.add_run(part)


def export_bank(questions, out_path, with_answer=False, with_solution=False, with_taxonomy=False):
    """A. Xuất ngân hàng câu hỏi đã chọn."""
    doc = Document()
    _setup_doc(doc)
    h = doc.add_heading("NGÂN HÀNG CÂU HỎI VẬT LÍ – TN THPT", level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Tổng số câu: {len(questions)}").alignment = WD_ALIGN_PARAGRAPH.CENTER

    for i, q in enumerate(questions, 1):
        _add_question_para(doc, q, index=i, with_answer=with_answer,
                           with_solution=with_solution, with_taxonomy=with_taxonomy)
        if i < len(questions):
            doc.add_paragraph()
    doc.save(out_path)
    return out_path


def export_exam(questions, out_path, exam_name="", subject="Vật lí", duration="",
                with_answer=False, with_solution=False, with_taxonomy=False, shuffle=False):
    """B. Xuất đề thi hoàn chỉnh."""
    doc = Document()
    _setup_doc(doc)
    h = doc.add_heading((exam_name or "ĐỀ THI VẬT LÍ").upper(), level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info = [f"Môn: {subject}"]
    if duration:
        info.append(f"Thời gian: {duration}")
    info.append(f"Số câu: {len(questions)}")
    doc.add_paragraph(" – ".join(info)).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()

    items = list(enumerate(questions, 1))
    if shuffle:
        import random
        random.shuffle(items)
        for new_i, (_, q) in enumerate(items, 1):
            _add_question_para(doc, q, index=new_i, with_answer=with_answer,
                               with_solution=with_solution, with_taxonomy=with_taxonomy)
    else:
        for i, q in items:
            _add_question_para(doc, q, index=i, with_answer=with_answer,
                               with_solution=with_solution, with_taxonomy=with_taxonomy)

    doc.save(out_path)
    return out_path


def export_answers(questions, out_path, exam_name="", with_solution=False):
    """C. Xuất đáp án riêng."""
    doc = Document()
    _setup_doc(doc)
    h = doc.add_heading((exam_name or "ĐỀ THI VẬT LÍ") + " – ĐÁP ÁN", level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()

    if all(q.get("answer") for q in questions):
        tbl = doc.add_table(rows=1, cols=2)
        tbl.style = "Table Grid"
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr = tbl.rows[0].cells
        hdr[0].text = "Câu"; hdr[1].text = "Đáp án"
        for i, q in enumerate(questions, 1):
            row = tbl.add_row().cells
            row[0].text = str(i)
            row[1].text = str(q.get("answer", ""))
    else:
        for i, q in enumerate(questions, 1):
            doc.add_paragraph(f"Câu {i}: {q.get('answer', '—')}")
    if with_solution:
        doc.add_page_break()
        doc.add_heading("HƯỚNG DẪN GIẢI", level=1)
        for i, q in enumerate(questions, 1):
            doc.add_paragraph(f"Câu {i}")
            doc.add_paragraph(q.get("solution") or "—")
    doc.save(out_path)
    return out_path


def _setup_doc(doc):
    for section in doc.sections:
        section.left_margin = Cm(2.2)
        section.right_margin = Cm(2.2)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(13)
    try:
        from docx.oxml.ns import qn
        style.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    except Exception:
        pass


def export_questions_json(questions, out_path):
    """Xuất JSON (dữ liệu có cấu trúc để trao đổi / tích hợp AI)."""
    import json as _json
    with open(out_path, "w", encoding="utf-8") as f:
        _json.dump(questions, f, ensure_ascii=False, indent=2)
    return out_path