# -*- coding: utf-8 -*-
"""
Gắn taxonomy tự động (heuristic) cho câu hỏi dựa trên cây taxonomy đã seed.
Đối chiếu câu hỏi với tên node (Mạch/Nội dung/ĐVKT) bằng từ khóa;
YCCĐ chỉ gán khi đủ từ khóa trùng — nếu không, để trống → CẦN THẨM ĐỊNH (đúng quy tắc).
"""
import re
import unicodedata

STOPWORDS = set("""
được của và với cho theo trong không các một khi thì là ở có từ qua trên dưới vào ra lên tại đến về hay hoặc
nêu tính xác định vận dụng sử thực hiện thảo luận thiết kế lựa chọn phương án thí nghiệm vật lí học tập môn
của là các những đã đang sẽ vì nên nhưng mà này đó với giữa bằng theo sau trước đây đó năm giờ phút giây
ngày người vật làm cho dùng tìm hiểu đơn giản số liệu cho trước dụng cụ thực hành tiến hành quan sát hình ảnh
phân tích đánh giá kết quả thu được trường hợp một số ví dụ thực tế thảo luận đề xuất phù hợp
""".split())


def normalize(s):
    s = str(s).replace("đ", "d").replace("Đ", "D")  # đ không có NFD-mark
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower()


def sig_tokens(text):
    """Từ khóa có nghĩa (bỏ stopword, dài >= 3 ký tự)."""
    out = set()
    for tok in re.findall(r"[a-z0-9]+", normalize(text)):
        if tok not in STOPWORDS and len(tok) >= 3:
            out.add(tok)
    return out


def _best_match(question_text, nodes, min_hits=1):
    """Chọn node có nhiều từ khóa trùng nhất với câu hỏi."""
    qtoks = sig_tokens(question_text)
    if not qtoks:
        return None, 0
    best, best_hits = None, 0
    for n in nodes:
        ntoks = sig_tokens(n["name"])
        hits = len(ntoks & qtoks)
        if hits > best_hits:
            best, best_hits = n, hits
    if best and best_hits >= min_hits:
        return best, best_hits
    return None, 0


def auto_taxonomy(question_text, tree):
    """
    tree: danh sách node cấp 1 với children (như get_taxonomy_tree).
    Trả (strand, content, unit, outcome) — mỗi phần là dict node hoặc None.
    """
    strand, _ = _best_match(question_text, [n for n in tree])
    if not strand:
        return (None, None, None, None)
    content, _ = _best_match(question_text, strand["children"], min_hits=1)
    unit, outcome = None, None
    if content:
        unit, _ = _best_match(question_text, content["children"], min_hits=1)
    if unit:
        outcome, hits = _best_match(question_text, unit["children"], min_hits=2)
    return strand, content, unit, outcome