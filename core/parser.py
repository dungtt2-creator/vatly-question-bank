# -*- coding: utf-8 -*-
"""
Tách câu hỏi từ đề thi (PDF / DOCX / TXT).

MVP hỗ trợ:
- TXT / DOCX: đọc text layer, tách theo mẫu số câu (Câu 1., Câu 2., 1., 1) ... )
- PDF: dùng pdfplumber đọc text layer (đề scan cần OCR – nằm ở Phase 2).
Nhận diện dạng câu:
  - MCQ: có 4 phương án A. B. C. D.
  - Đúng/Sai: có 4 phát biểu a) b) c) d) hoặc từ khóa "đúng/sai"
  - Trả lời ngắn: không có phương án
"""
import re
import os
import json

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


def read_docx(path):
    doc = DocxDocument(path)
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
    return "\n".join(lines)


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
    # .xlsx: đọc cột đầu tiên của Sheet1 (mỗi ô là 1 câu) — MVP
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
    # Câu 1. / Câu 1: / Câu 1)  — phổ biến trong đề VN
    re.compile(r"(?m)^\s*Câu\s+(\d{1,3})\s*[\.\:\)]\s*"),
    # Question 1.
    re.compile(r"(?m)^\s*Question\s+(\d{1,3})\s*[\.\:\)]\s*"),
    # 1. / 1) / 1.5 gạch đầu dòng "1. " đứng đầu dòng, KHÔNG phải trong câu
    re.compile(r"(?m)^\s*(\d{1,3})\s*[\.\:\)]\s+(?=[A-ZĐẠ×])"),
]
OPTION_RE = re.compile(r"^\s*[A-D][\.\:\)]\s*")
SUB_OPTION_RE = re.compile(r"^\s*[a-d][\.\:\)]\s*")
ANSWER_RE = re.compile(
    r"(?i)(?:đáp\s*án|Đ\s*[: =]|Đáp án\s*:?)\s*[:\s]*([A-D]{1})\s*(?:$|[.,;)\s])"
    r"|(?<=\n)\s*([A-D])\s*$"
)


def _clean_question_text(block):
    """Làm sạch block câu hỏi: bỏ header, chuẩn hóa khoảng trắng."""
    block = re.sub(r"[ \t]+", " ", block)
    block = re.sub(r"\n\s*\n+", "\n", block)
    return block.strip()


def _split_options(block):
    """Tách phương án A. B. C. D. khỏi phần lời dẫn. Trả (lead, [options]) hoặc (block, [])."""
    lines = block.split("\n")
    lead_lines, opts = [], []
    in_opts = False
    for ln in lines:
        s = ln.strip()
        if OPTION_RE.match(s):
            in_opts = True
        if in_opts:
            # Một dòng có thể chứa nhiều phương án: "A. 2 m.        B. 5 m."
            s = re.sub(r"\s{2,}", " ", s)
            parts = re.split(r"(?=\s?[B-D][\.\:\)]\s)", s)
            for p in parts:
                p = p.strip()
                if p and OPTION_RE.match(p):
                    opts.append(p)
                elif p:
                    opts.append(p)
        else:
            lead_lines.append(s)
    if opts:
        return "\n".join(lead_lines).strip(), opts
    return block.strip(), []


def parse_exam_text(text, default_year=None, default_exam=None):
    """
    Tách text đề thi -> list dict câu hỏi:
      {question_number, question_text, options, answer, solution, question_type}
    """
    # Xác định vị trí bắt đầu các câu
    bounds = []  # (pos, number)
    for pat in QUESTION_PATTERNS:
        for m in pat.finditer(text):
            bounds.append((m.start(), int(m.group(1))))
    bounds.sort()

    # Bỏ trùng vị trí, giữ pattern đầu tiên (ưu tiên "Câu N.")
    if bounds:
        unique = [bounds[0]]
        for b in bounds[1:]:
            if b[0] != unique[-1][0]:
                unique.append(b)
        bounds = unique

    questions = []
    for i, (pos, num) in enumerate(bounds):
        end = bounds[i + 1][0] if i + 1 < len(bounds) else len(text)
        block = text[pos:end]
        # Bỏ phần "Câu N." tiền tố
        block = re.sub(r"^\s*(?:Câu|Question)\s+\d+\s*[\.\:\)]\s*", "", block, count=1, flags=re.IGNORECASE)
        block = re.sub(r"^\s*\d+\s*[\.\:\)]\s*", "", block, count=1)
        block = _clean_question_text(block)
        if not block:
            continue

        # Tách đáp án (nếu có) — ở dòng cuối "A." hoặc "Đáp án: B"
        answer = ""
        m = ANSWER_RE.search(block)
        if m:
            answer = (m.group(1) or m.group(2) or "").upper()
            if m.group(1):
                block = block[:m.start()] + block[m.end():]

        lead, opts = _split_options(block)
        # Bỏ phần "Hướng dẫn giải" nếu có trong block (MVP: giữ nguyên, GV tự cắt)
        qtype = "MCQ 4 lựa chọn"
        if not opts:
            qtype = "Trả lời ngắn"
            # Nhận biết Đúng/Sai: có a) b) c) d) hoặc chữ "Đúng" / "Sai"
            if SUB_OPTION_RE.match(lead.split("\n")[-1] if lead else ""):
                qtype = "Đúng/Sai"
            elif re.search(r"đúng\s*/\s*sai|đúng hay sai", lead, flags=re.IGNORECASE):
                qtype = "Đúng/Sai"
            # Điền dấu "X" vào ô Đúng/Sai (dạng bảng)
            elif "Đúng" in lead and "Sai" in lead:
                qtype = "Đúng/Sai"

        questions.append({
            "question_number": num,
            "question_text": lead,
            "options": opts,
            "answer": answer,
            "solution": "",
            "question_type": qtype,
        })
    return questions


def parse_exam_file(path, default_year=None, default_exam=None):
    text = read_file(path)
    return parse_exam_text(text, default_year, default_exam)