# -*- coding: utf-8 -*-
"""Tách câu hỏi từ đề thi (PDF / DOCX / TXT)."""
import re
import os
import json
import hashlib

try:
    import pdfplumber
    HAS_PDF = True
except Exception:  # pragma: no cover
    HAS_PDF = False

try:
    from docx import Document as DocxDocument
    HAS_DOCX = True
except Exception:
    HAS_DOCX = False

FORMULA_RE = re.compile(r"\[\[FORMULA:(\d+)\]\]")
IMG_RE = re.compile(r"\[\[IMG:(\d+)\]\]")


def read_docx(path):
    """
    Đọc DOCX có công thức MathType/OLE và ảnh minh họa.
    - Thay w:object (MathType) bằng [[FORMULA:n]], w:drawing bằng [[IMG:n]].
    - Render công thức thành PNG (Word COM + pypdfium2, cache theo hash file).
    Trả (text, formulas {n: path}, images {n: path}).
    """
    from . import formula_extract as fe

    prepared, formulas, images = fe.prepare_exam_assets(path)
    doc = DocxDocument(prepared)
    lines = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            lines.append(t)
    for tbl in doc.tables:
        for row in tbl.rows:
            cells = [c.text.strip() for c in row.cells if c.text.strip()]
            if cells:
                lines.append(" | ".join(cells))
    text = "\n".join(lines)
    return text, formulas, images


def read_pdf(path):
    if not HAS_PDF:
        raise RuntimeError("pdfplumber chưa cài — không đọc được PDF")
    out = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text(x_tolerance=1.5, y_tolerance=3)
            if t:
                out.append(t)
    return "\n".join(out)


def read_txt(path):
    for enc in ("utf-8", "utf-16", "windows-1258"):
        try:
            with open(path, encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def read_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return read_pdf(path)
    if ext == ".docx":
        return read_docx(path)
    if ext == ".txt":
        return read_txt(path)
    if ext in (".xlsx", ".xls"):
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.worksheets[0]
        rows = []
        for row in ws.iter_rows(values_only=True):
            v = str(row[0]).strip() if row and row[0] is not None else ""
            if v:
                rows.append(v)
        return "\n".join(rows)
    raise ValueError(f"Định dạng không hỗ trợ: {ext}")


# ---- Định nghĩa câu hỏi ----
QUESTION_PATTERNS = [
    # ưu tiên: câu có placeholder ảnh/công thức phía trước ([[IMG:0]]Câu 3.)
    re.compile(r"(?m)^\s*(?:\[\[(?:IMG|FORMULA):\d+\]\]\s*)+Câu\s+(\d{1,3})\s*[\.\:\)]\s*"),
    # Câu 1. / Câu 1: / Câu 1)  — phổ biến trong đề VN
    re.compile(r"(?m)^\s*Câu\s+(\d{1,3})\s*[\.\:\)]\s*"),
    # Question 1.
    re.compile(r"(?m)^\s*Question\s+(\d{1,3})\s*[\.\:\)]\s*"),
    # 1. / 1) / 1.5 gạch đầu dòng "1. " đứng đầu dòng, KHÔNG phải trong câu
    re.compile(r"(?m)^\s*(\d{1,3})\s*[\.\:\)]\s+(?=[A-ZĐẠ×])"),
]
OPTION_RE = re.compile(r"^\s*[A-D][\.\:\)]\s*")
SUB_OPTION_RE = re.compile(r"^\s*[a-d][\.\:\)]\s*")
# Marker bắt đầu phần lời giải
SOLUTION_START_RE = re.compile(
    r"^\s*(?:Hướng dẫn giải|Hướng dẫn|Lời giải|HDG|Giải\s*:?)\s*[:：]?\s*$|^\s*Đáp án\s*:?\s*$",
    re.IGNORECASE,
)
ANSWER_RE = re.compile(
    r"(?i)(?:đáp\s*án|Đ\s*[: =])\s*[:=\s]*([A-D]{1})\s*(?:$|[.,;)\s])"
)


def _clean_question_text(block):
    """Làm sạch block câu hỏi: bỏ header, chuẩn hóa khoảng trắng."""
    block = re.sub(r"[ \t]+", " ", block)
    block = re.sub(r"\n\s*\n+", "\n", block)
    return block.strip()


def _split_block(block):
    """
    Tách block câu thành (lead, options, solution).
    - Options: từ dòng A. đầu tiên cho tới khi gặp marker lời giải
      ("Hướng dẫn", "Hướng dẫn giải", "Lời giải", "Đáp án:") hoặc hết.
    - Solution: phần sau marker (gồm cả các dòng "Chọn B" cuối).
    """
    lines = block.split("\n")
    lead_lines, opts, sol = [], [], []
    state = "lead"  # lead -> opts -> sol
    for ln in lines:
        s = ln.strip()
        if state == "lead":
            if OPTION_RE.match(s):
                state = "opts"
            else:
                lead_lines.append(s)
                continue
        if state == "opts":
            if SOLUTION_START_RE.match(s):
                state = "sol"
                sol.append(s)
                continue
            if OPTION_RE.match(s):
                # có thể nhiều option trên 1 dòng: "A. .. B. .."
                parts = re.split(r"(?=\s?[B-D][\.\:\)]\s)", s)
                for p in parts:
                    p = p.strip()
                    if p:
                        opts.append(p)
            elif re.match(r"^\s*Câu\s+\d+", s):
                # đầu câu tiếp theo lọt vào block cũ (safety) — dừng
                break
            else:
                # dòng không phải option giữa options (vd chú thích ảnh) -> coi là lời giải tạm
                sol.append(s)
                state = "sol"
            continue
        # sol
        sol.append(s)

    lead = "\n".join(lead_lines).strip()
    return lead, opts, sol


def parse_exam_text(text, default_year=None, default_exam=None, formulas=None, images=None):
    """
    Tách text đề thi -> list dict câu hỏi:
      {question_number, part, question_text, options, answer, solution, question_type,
       formulas (map n->path), image_path (list)}
    - Cắt phần đáp án ngay khi gặp dòng "HẾT" / "ĐÁP ÁN" / "---- HẾT ----".
    - Đề có 3 phần (I: MCQ, II: Đ/S, III: TL ngắn) mỗi phần đánh số lại từ 1;
      gắn part (1/2/3) để phân biệt, question_number giữ số gốc trong phần.
    """
    # 1) cắt đuôi: chỉ lấy phần đề thi
    cut = re.search(r"(?im)^\s*[-–—\s]*HẾT[-–—\s]*$|^\s*[-–—]*ĐÁP ÁN\s*$|^\s*ĐÁP ÁN\b", text)
    if cut:
        text = text[: cut.start()]

    # 2) phát hiện phần hiện tại: [(start, part_no), ...]
    part_starts = [(m.start(), i + 1)
                   for i, m in enumerate(re.finditer(r"(?im)^\s*PHẦN\s+(I{1,3}|IV)\b[^\n]*", text))]

    def part_at(pos):
        p = 0
        for st, pi in part_starts:
            if st <= pos:
                p = pi
            else:
                break
        return p

    bounds = []
    for pat in QUESTION_PATTERNS:
        for m in pat.finditer(text):
            bounds.append((m.start(), int(m.group(1))))
    bounds.sort()

    if bounds:
        unique = [bounds[0]]
        for b in bounds[1:]:
            if b[0] != unique[-1][0]:
                unique.append(b)
        bounds = unique

    formulas = formulas or {}
    images = images or {}
    questions = []
    for i, (pos, num) in enumerate(bounds):
        end = bounds[i + 1][0] if i + 1 < len(bounds) else len(text)
        part = part_at(pos)
        block = text[pos:end]
        block = re.sub(r"^\s*(?:Câu|Question)\s+\d+\s*[\.\:\)]\s*", "", block, count=1, flags=re.IGNORECASE)
        block = re.sub(r"^\s*\d+\s*[\.\:\)]\s*", "", block, count=1)
        block = _clean_question_text(block)
        if not block:
            continue

        # Đáp án dạng "Đáp án: B" / "Đáp án B" xuất hiện trong block (đề có đáp án kèm)
        answer = ""
        m = ANSWER_RE.search(block)
        if m:
            answer = m.group(1).upper()

        # Tách option + lời giải
        lead, opts, sol = _split_block(block)

        # Đáp án "Chọn B" nằm cuối lời giải — nếu chưa có đáp án, lấy từ dòng "Chọn X"
        if not answer:
            m2 = re.search(r"(?im)^\s*Chọn\s+([A-D])\s*$", "\n".join(sol))
            if m2:
                answer = m2.group(1).upper()
        elif answer:
            # nếu bắt được "Đáp án: B" trong text thì bỏ dòng đó khỏi solution
            pass

        # Tách clean solution: bỏ dòng "Chọn X" trùng, bỏ dòng marker
        clean_sol = []
        for ln in sol:
            ls = ln.strip()
            if not ls:
                continue
            if re.match(r"(?i)^\s*Hướng dẫn( giải)?\s*$", ls):
                continue
            if re.match(r"(?i)^\s*(Giải)\s*:?\s*$", ls):
                continue
            if re.match(r"(?i)^\s*Đáp án\s*:?\s*(?:[A-D])?\s*$", ls):
                continue
            if re.match(r"(?i)^\s*Chọn\s+[A-D]\s*$", ls) and answer and len(clean_sol) > 0:
                continue
            clean_sol.append(ls)
        solution = "\n".join(clean_sol).strip()

        # Câu hỏi lead: giữ placeholder công thức (để render sau); bỏ [[IMG:n]]
        # (ảnh minh họa đã được lưu riêng vào image_path, tránh hiển thị chuỗi thô)
        lead = IMG_RE.sub("", lead)
        # Bỏ bound giả: sau khi strip ảnh mà lead rỗng (vd dòng mô tả chung
        # "Nội dung câu 1 và 2: ..." bị ngắt bởi ảnh đầu dòng) thì bỏ qua
        if not lead.strip():
            continue
        lower_lead = lead.lower()
        qtype = "MCQ 4 lựa chọn"
        if not opts:
            # Đúng/Sai chỉ khi có 4 ý a) b) c) d) hoặc cụm "đúng/sai" trong THÂN câu (phần I không có)
            has_sub = bool(re.search(r"(?m)^\s*[a-d]\s*[\.\:\)]", lead))
            has_ds_text = bool(re.search(r"đúng\s*/\s*sai|đúng hay sai|đúng hoặc sai", lower_lead))
            if has_sub or has_ds_text:
                qtype = "Đúng/Sai"
            else:
                qtype = "Trả lời ngắn"
        # Đúng/Sai: câu có lead + 4 ý a) b) c) d) — options rỗng nhưng có sub-options trong lead
        if not opts and re.search(r"(?m)^\s*[a-d]\s*[\.\:\)]", lead):
            qtype = "Đúng/Sai"

        # Gắn ảnh công thức + minh họa thuộc câu này (giữ placeholder trong text
        # để UI/export chèn ảnh đúng vị trí; lưu map n -> path)
        q_formulas = {}
        q_images = []
        for mf in FORMULA_RE.finditer(block):
            k = int(mf.group(1))
            if k in formulas and formulas[k] != "UNCONVERTED":
                q_formulas[k] = formulas[k]
        for mi in IMG_RE.finditer(block):
            k = int(mi.group(1))
            if k in images:
                q_images.append(images[k])

        questions.append({
            "question_number": num,
            "part": part,
            "question_text": lead,
            "options": opts,
            "answer": answer,
            "solution": solution,
            "question_type": qtype,
            "formulas": q_formulas,
            "image_path": q_images,
        })
    return questions


def parse_exam_file(path, default_year=None, default_exam=None):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        text, formulas, images = read_docx(path)
        return parse_exam_text(text, default_year, default_exam, formulas, images)
    text = read_file(path)
    return parse_exam_text(text, default_year, default_exam)