# -*- coding: utf-8 -*-
"""
Tầng dữ liệu – SQLite.
Schema bám sát §15 của đặc tả: Question_ID ... Updated_Date, mở rộng được
cho Phase 2/3 (ma trận đề, AI, thống kê chất lượng).
"""
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "bank.db")

# ---- Hằng số (danh sách chỉnh sửa được trên giao diện ở Phase 2; MVP dùng hằng) ----
QUESTION_TYPES = ["MCQ 4 lựa chọn", "Đúng/Sai", "Trả lời ngắn"]
COGNITIVE_LEVELS = ["Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"]
DIFFICULTIES = ["Dễ", "Trung bình", "Khó", "Rất khó"]
REVIEW_STATUSES = ["Chờ duyệt", "Đã duyệt", "Trùng 100%", "Gần trùng", "Cần thẩm định", "Lỗi câu hỏi"]
DUPLICATE_LEVELS = ["Mức 1 – Trùng 100%", "Mức 2 – Gần trùng", "Mức 3 – Tương đồng", "Mức 4 – Không trùng"]
SOURCE_GROUPS = [
    "CTGDPT 2018 môn Vật lí",
    "Đề tham khảo TN THPT",
    "Đề chính thức 2025",
    "Đề chính thức 2026",
    "Hướng dẫn xây dựng đề thi",
    "Các tài liệu chuẩn khác",
]
CLASS_LEVELS = ["Không gắn lớp", "Lớp 10", "Lớp 11", "Lớp 12"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  group_name TEXT NOT NULL,
  year INTEGER,
  description TEXT DEFAULT '',
  file_path TEXT DEFAULT '',
  file_name TEXT DEFAULT '',
  status TEXT DEFAULT 'Đang sử dụng',
  created_at TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS taxonomy_nodes(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  level INTEGER NOT NULL,            -- 1= Mạch nội dung, 2= Nội dung, 3= Đơn vị kiến thức, 4= YCCĐ
  name TEXT NOT NULL,
  grade TEXT DEFAULT '',             -- Lớp 10/11/12 hoặc rỗng
  parent_id INTEGER REFERENCES taxonomy_nodes(id),
  source TEXT DEFAULT '',            -- căn cứ (vd: TT 32/2018/TT-BGDĐT)
  code TEXT DEFAULT '',
  note TEXT DEFAULT '',
  sort_order INTEGER DEFAULT 0,
  UNIQUE(level, name, parent_id)
);
CREATE INDEX IF NOT EXISTS idx_tax_parent ON taxonomy_nodes(parent_id);

CREATE TABLE IF NOT EXISTS exams(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  organization TEXT DEFAULT '',
  year INTEGER,
  subject TEXT DEFAULT 'Vật lí',
  exam_code TEXT DEFAULT '',
  source_id INTEGER REFERENCES sources(id),
  note TEXT DEFAULT '',
  file_path TEXT DEFAULT '',
  file_name TEXT DEFAULT '',
  created_at TEXT, updated_at TEXT
);

CREATE TABLE IF NOT EXISTS questions(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER REFERENCES sources(id),
  source_name TEXT DEFAULT '',
  year INTEGER,
  organization TEXT DEFAULT '',
  exam_name TEXT DEFAULT '',
  exam_code TEXT DEFAULT '',
  exam_id INTEGER REFERENCES exams(id),
  question_number INTEGER,
  question_type TEXT DEFAULT '',        -- QUESTION_TYPES
  question_text TEXT NOT NULL,
  options TEXT DEFAULT '',              -- JSON list ["A. ...", ...]
  answer TEXT DEFAULT '',
  solution TEXT DEFAULT '',
  image_path TEXT DEFAULT '',           -- đường dẫn ảnh/đồ thị (PNG) hoặc '' (JSON list nếu nhiều)
  formulas TEXT DEFAULT '',             -- JSON list công thức dạng text rút từ nguồn
  table_data TEXT DEFAULT '',           -- JSON (bảng) nếu có
  
  -- Taxonomy (id tham chiếu taxonomy_nodes, lưu cả tên để query nhanh)
  strand_id INTEGER, strand_name TEXT DEFAULT '',        -- Mạch nội dung
  content_id INTEGER, content_name TEXT DEFAULT '',      -- Nội dung
  unit_id INTEGER, unit_name TEXT DEFAULT '',            -- Đơn vị kiến thức
  outcome_id INTEGER, outcome_name TEXT DEFAULT '',      -- Yêu cầu cần đạt
  
  cognitive_level TEXT DEFAULT '',      -- COGNITIVE_LEVELS
  difficulty TEXT DEFAULT '',           -- DIFFICULTIES
  
  -- Trùng lặp
  duplicate_status TEXT DEFAULT '',     -- DUPLICATE_LEVELS
  similarity_score REAL DEFAULT 0,
  related_question_ids TEXT DEFAULT '[]',   -- JSON list
  
  -- Phân loại
  classification_confidence REAL DEFAULT 0,
  classification_basis TEXT DEFAULT '',
  
  -- Duyệt
  review_status TEXT DEFAULT 'Chờ duyệt',
  reviewer TEXT DEFAULT '',
  review_note TEXT DEFAULT '',
  created_at TEXT, updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_q_review ON questions(review_status);
CREATE INDEX IF NOT EXISTS idx_q_strand ON questions(strand_id);
CREATE INDEX IF NOT EXISTS idx_q_type ON questions(question_type);
CREATE INDEX IF NOT EXISTS idx_q_dup ON questions(duplicate_status);

CREATE TABLE IF NOT EXISTS settings(
  key TEXT PRIMARY KEY,
  value TEXT
);
"""


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_conn(db_path=DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path=DB_PATH):
    conn = get_conn(db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


# ------------------------- helpers -------------------------
def rows_to_dicts(rows):
    return [dict(r) for r in rows]


def qrow_to_dict(r):
    d = dict(r)
    for k in ("options", "related_question_ids", "formulas"):
        if k in d and isinstance(d.get(k), str) and d[k]:
            try:
                d[k] = json.loads(d[k])
            except Exception:
                pass
    return d