# -*- coding: utf-8 -*-
"""
Phát hiện câu hỏi trùng – 4 mức theo §10 đặc tả.
Thuật toán: chuẩn hóa nội dung (bỏ số câu, khoảng trắng, dấu) + SequenceMatcher
trên nội dung và phương án. Không tự kết luận trùng 100% chỉ vì cùng kiến thức.
"""
import re
import unicodedata
from difflib import SequenceMatcher

# Ký hiệu toán học thường xuất hiện dưới dạng ký tự đặc biệt (m2, omega...) – giữ nguyên
def normalize_text(s):
    """Chuẩn hóa để so sánh: bỏ số câu, xuống dòng, khoảng trắng thừa, dấu câu đuôi."""
    if not s:
        return ""
    s = str(s)
    # Bỏ tiền tố số câu "Câu 1." / "1." / "Câu 1:" ở đầu
    s = re.sub(r"^\s*(câu\s*)?(\d+)\s*[\.\:\)]?\s*", "", s, flags=re.IGNORECASE)
    # Bỏ ký tự khoảng trắng, tab, xuống dòng
    s = re.sub(r"\s+", " ", s)
    # Bỏ dấu chấm/hỏi/chấm than cuối
    s = re.sub(r"[\.\?\!]+$", "", s.strip())
    # Bỏ dấu thanh tiếng Việt + lowercase để so sánh lỏng
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.lower()
    return s


def _norm_options(opts, answer=None):
    """Chuẩn hóa phương án (loại prefix A./ B. và khoảng trắng)."""
    if isinstance(opts, str):
        try:
            import json
            opts = json.loads(opts)
        except Exception:
            opts = [opts]
    out = []
    for o in (opts or []):
        o = re.sub(r"^\s*[A-Da-d]\s*[\.\:\)]\s*", "", str(o)).strip()
        out.append(normalize_text(o))
    return out


def similarity(a, b):
    """0..1 – độ tương đồng giữa hai chuỗi."""
    return SequenceMatcher(None, a, b).ratio()


def compare_questions(q1, q2):
    """
    So sánh 2 câu hỏi -> dict:
      score, level (Mức 1..4), reason, matched_parts (để highlight)
    """
    t1 = normalize_text(q1.get("question_text", ""))
    t2 = normalize_text(q2.get("question_text", ""))
    if not t1 and not t2:
        return {"score": 0.0, "level": "Mức 4 – Không trùng", "reason": "Không có nội dung để so sánh"}

    text_score = similarity(t1, t2)
    o1 = _norm_options(q1.get("options"))
    o2 = _norm_options(q2.get("options"))
    opt_scores = []
    if o1 and o2:
        n = min(len(o1), len(o2))
        opt_scores = [similarity(a, b) for a, b in zip(o1[:n], o2[:n])]
    opt_score = sum(opt_scores) / len(opt_scores) if opt_scores else 0.0

    # Trọng số: nội dung 70%, phương án 30%
    score = 0.7 * text_score + 0.3 * opt_score

    # Mức độ
    if score >= 0.95 and (text_score >= 0.95):
        level = "Mức 1 – Trùng 100%"
    elif score >= 0.75:
        level = "Mức 2 – Gần trùng"
    elif score >= 0.45:
        level = "Mức 3 – Tương đồng"
    else:
        level = "Mức 4 – Không trùng"

    return {
        "score": round(score, 3),
        "level": level,
        "text_score": round(text_score, 3),
        "opt_score": round(opt_score, 3),
        "reason": f"Nội dung tương đồng {text_score:.0%}, phương án {opt_score:.0%}",
    }


def find_duplicates(new_question, bank_questions, threshold=0.45):
    """
    So câu mới với toàn bộ ngân hàng.
    Trả về list dict: {question_id, score, level, ...} sắp theo score giảm dần.
    """
    results = []
    for q in bank_questions:
        if q["id"] == new_question.get("id"):
            continue
        cmp = compare_questions(new_question, q)
        if cmp["score"] >= threshold:
            results.append({"question_id": q["id"], **cmp})
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def flag_question(new_question, bank_questions):
    """
    Gắn trạng thái cho câu mới dựa vào kết quả duy nhất (cao nhất).
    Trả (duplicate_status, similarity_score, related_ids, candidates)
    """
    cands = find_duplicates(new_question, bank_questions)
    if not cands:
        return "", 0.0, [], []
    top = cands[0]
    return top["level"], top["score"], [c["question_id"] for c in cands if c["level"].startswith(("Mức 1", "Mức 2"))], cands