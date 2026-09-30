# -*- coding: utf-8 -*-
"""
Phân loại câu hỏi (Classification Engine).
MVP: phân loại heuristic dựa trên nội dung — KHÔNG gọi AI trả phí.
Kiến trúc tách lớp: `classify_all` trả schema chuẩn (content_strand, content,
knowledge_unit, learning_outcome, question_type, cognitive_level, difficulty,
confidence, classification_basis, duplicate_candidates) giống hệt AI layer §18,
để sau này thay engine nội bộ bằng API mà không đổi giao diện.
"""
import json
import re

# Từ khóa → Mạch nội dung (theo CTGDPT 2018)
STRAND_KEYWORDS = [
    ("Cơ học", ["động học", "động lực", "chuyển động", "vận tốc", "gia tốc", "quãng đường", "lực", "khối lượng",
                "công cơ", "động năng", "thế năng", "cơ năng", "động lượng", "va chạm", "moment", "dao động",
                "con lắc", "chu kì", "tần số", "biên độ", "cộng hưởng", "lò xo", "rơi tự do", "ném"]),
    ("Nhiệt học", ["nhiệt", "nội năng", "nhiệt dung", "nóng chảy", "hoá hơi", "nhiệt độ", "kelvin", "celsius",
                   "khí lí tưởng", "khí lý tưởng", "boyle", "charles", "boltzmann", "phân tử", "chuyển thể",
                   "động năng phân tử", "áp suất khí", "nhiệt động"]),
    ("Điện học", ["điện tích", "điện trường", "coulomb", "điện thế", "hiệu điện thế", "điện dung", "tụ điện",
                  "dòng điện", "cường độ dòng điện", "điện trở", "ohm", "suất điện động", "mạch điện",
                  "công suất điện", "năng lượng điện", "dòng điện xoay chiều", "xoay chiều", "máy biến áp",
                  "điện năng", "ampe", "vôn", "oát"]),
    ("Từ học", ["từ trường", "cảm ứng từ", "lực từ", "từ thông", "cảm ứng điện từ", "faraday", "lenz",
                "tesla", "weber", "nam châm", "đường sức từ", "sóng điện từ", "dòng điện xoay chiều"]),
    ("Quang học", ["quang", "ánh sáng", "gương", "thấu kính", "khúc xạ", "phản xạ", "lăng kính", "sóng ánh sáng",
                   "giao thoa ánh sáng", "quang phổ", "nhiễu xạ", "photon", "quang điện", "lưỡng tính"]),
    ("Vật lí hạt nhân và phóng xạ", ["hạt nhân", "phóng xạ", "nucleon", "proton", "neutron", "bán rã", "độ phóng xạ",
                                     "phân hạch", "tổng hợp hạt nhân", "năng lượng liên kết", "độ hụt khối",
                                     "alpha", "beta", "gamma", "đồng vị"]),
    ("Vật lí hiện đại", ["lượng tử", "de broglie", "vùng năng lượng", "chất rắn", "bán dẫn", "hiệu ứng quang điện",
                         "electron", "nguyên tử", "mức năng lượng"]),
    ("Trái Đất và bầu trời", ["thiên văn", "sao bắc cực", "nhật thực", "nguyệt thực", "thuỷ triều", "vệ tinh",
                              "mặt trăng", "mặt trời", "chòm sao", "thiên thể"]),
]

# Danh sách "Dao động và Sóng" được bỏ (trùng với Cơ học). Thực tế theo CTGDPT:
# Dao động & Sóng thuộc Lớp 11; map về Cơ học hoặc tạo mạch riêng — đặt trong 'Cơ học' để
# đơn giản MVP, GV có thể sửa trên giao diện. Đầy đủ hơn ở seed dưới.

STRANDS = [
    "Mở đầu", "Cơ học", "Nhiệt học", "Điện học", "Từ học", "Quang học",
    "Vật lí hạt nhân và phóng xạ", "Vật lí hiện đại", "Trái Đất và bầu trời",
]

# Từ khóa → Mức độ tư duy (chỉ heuristic — KHÔNG dùng làm căn cứ chính thức)
LEVEL_KEYWORDS = {
    "Nhận biết": ["nêu được", "định nghĩa", "phát biểu", "kể tên", "nhận biết", "liệt kê", "mô tả được"],
    "Thông hiểu": ["giải thích", "so sánh", "phân tích", "trình bày", "mô tả", "vận dụng công thức", "tính", "xác định"],
    "Vận dụng": ["vận dụng", "áp dụng", "tính toán", "thiết kế", "đề xuất", "chứng minh", "đánh giá"],
}


def detect_question_type(text, options):
    """Phát hiện dạng câu hỏi từ nội dung + phương án."""
    opts = options if isinstance(options, list) else json.loads(options or "[]")
    n_opts = len([o for o in opts if str(o).strip()])

    # Đúng/Sai: có câu lệnh "Xét ... " + 4 phát biểu a) b) c) d) HOẶC "Đúng/Sai" trong đề
    t = text.lower()
    if re.search(r"(đúng\s*/\s*sai|đúng hay sai|nhận định.*đúng)", t) and n_opts <= 4:
        return "Đúng/Sai"
    if re.search(r"\ba\)\s", t, flags=re.IGNORECASE) and re.search(r"\bb\)\s", t, flags=re.IGNORECASE):
        return "Đúng/Sai"
    if n_opts >= 4:
        return "MCQ 4 lựa chọn"
    if n_opts == 0:
        return "Trả lời ngắn"
    return "Trả lời ngắn"


def heuristic_classify(q, taxonomy_tree=None):
    """
    Phân loại heuristic. Trả dict theo schema AI layer §18.
    taxonomy_tree: dict {strand: {content: [units]}} — để gợi ý sâu hơn (optional).
    """
    text = (q.get("question_text") or "") + " " + " ".join(q.get("options") or [])
    t = text.lower()

    strand = ""
    for s, kws in STRAND_KEYWORDS:
        if s is None:
            continue
        if any(k in t for k in kws):
            strand = s
            break

    qtype = detect_question_type(q.get("question_text", ""), q.get("options", []))

    # Mức độ: keyword → Nhận biết/Thông hiểu/Vận dụng; còn lại "Cần thẩm định"
    cognitive = ""
    for lvl, kws in LEVEL_KEYWORDS.items():
        if any(k in t for k in kws):
            cognitive = lvl
            break

    # Độ khó heuristic: số phép tính/số đề nghị + từ khóa "tính", "phức tạp", "nâng cao"
    n_digits = len(re.findall(r"\d", q.get("question_text", "")))
    has_tinh = "tính" in t or "xác định" in t or "tìm" in t
    if n_digits >= 8 and (re.search(r"nâng cao|phức tạp|kết hợp", t)):
        difficulty = "Rất khó"
    elif n_digits >= 6 or "vận dụng cao" in t:
        difficulty = "Khó"
    elif "trung bình" in t or "đơn giản" in t:
        difficulty = "Trung bình"
    elif n_digits >= 3 and has_tinh:
        difficulty = "Trung bình"
    else:
        difficulty = "Dễ"

    confidence = 0.0
    basis = []
    if strand:
        confidence += 0.4
        basis.append(f"Phát hiện từ khóa mạch: {strand}")
    if qtype:
        confidence += 0.3
        basis.append(f"Dạng câu: {qtype}")
    if cognitive:
        confidence += 0.2
        basis.append(f"Từ khóa mức độ: {cognitive}")
    if difficulty:
        confidence += 0.1
        basis.append(f"Độ khó ước lượng: {difficulty}")

    return {
        "content_strand": strand,
        "content": "",
        "knowledge_unit": "",
        "learning_outcome": "",
        "question_type": qtype,
        "cognitive_level": cognitive,
        "difficulty": difficulty,
        "confidence": round(min(confidence, 0.92), 2),
        "classification_basis": "; ".join(basis),
        "duplicate_candidates": [],
    }


def classify_all(questions, taxonomy=None):
    """Phân loại hàng loạt — dùng cho luồng nạp đề."""
    return [heuristic_classify(q, taxonomy) for q in questions]