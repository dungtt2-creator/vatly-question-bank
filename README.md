# 🎓 Ngân hàng Câu hỏi Vật lí – TN THPT (MVP)

Web MVP quản lý ngân hàng câu hỏi Vật lí theo **CTGDPT 2018** và định hướng
đề thi tốt nghiệp THPT: nạp đề → tách câu → phân loại → phát hiện trùng →
duyệt → lưu ngân hàng → tìm kiếm/lọc → xuất Word.

---

## 1. Chạy nhanh (local)

**Repo GitHub (public): https://github.com/dungtt2-creator/vatly-question-bank**

**Deploy 1-click lên Streamlit Community Cloud (miễn phí):**
https://streamlit.io/cloud → Sign in (GitHub) → New app →
`dungtt2-creator/vatly-question-bank` → Main → `app.py` → Deploy.
*Lưu ý: đĩa ephemeral — dữ liệu `data/bank.db` không bền giữa các lần khởi
động; nên nạp lại đề (màn hình Nạp đề) sau mỗi deploy hoặc dùng hành động
"Reset app". Chi tiết trong README mục 8.*

```bash
# (đã có sẵn môi trường nếu tải bản đóng gói)
pip install -r requirements.txt
streamlit run app.py
# mở http://localhost:8607
```

Nếu dùng `uv`:

```bash
uv venv .venv --python 3.11
VIRTUAL_ENV=.venv uv pip install -r requirements.txt
VIRTUAL_ENV=.venv ./.venv/Scripts/python.exe -m streamlit run app.py --server.port 8607
```

**Yêu cầu:** Python 3.10+ (đã test 3.11). Không cần API key, không cần database
bên ngoài — dữ liệu nằm trong `data/bank.db` (SQLite).

---

## 2. Các màn hình & luồng nghiệp vụ

| Màn hình | Chức năng |
| --- | --- |
| 📊 Dashboard | Thống kê nhanh: tổng câu, đã duyệt, trùng, cần thẩm định, phân bố mạch/dạng/mức độ |
| 📚 Nguồn chuẩn | Quản lý tài liệu căn cứ (CTGDPT 2018, đề TK/chính thức, HD xây dựng đề...) |
| 🌳 Taxonomy | Cây 4 cấp: **Mạch nội dung → Nội dung → Đơn vị kiến thức → Yêu cầu cần đạt** (seed từ Thông tư 32/2018/TT-BGDĐT), thêm/sửa/xóa/tìm |
| 📥 Nạp đề | Upload PDF/DOCX/XLSX/TXT → tách câu tự động → gợi ý phân loại → **lưu kèm kiểm tra trùng** |
| ✅ Thẩm định | Sửa nội dung/đáp án/taxonomy/mức độ/độ khó; xem **so sánh song song câu trùng**; duyệt Đạt/Trùng/Gần trùng/Cần thẩm định/Lỗi |
| 🗄️ Ngân hàng câu hỏi | Bảng + bộ lọc đa tiêu chí + tìm từ khóa + tick chọn câu |
| 📝 Tạo đề | Xuất Word: Đề thi / Ngân hàng / Đáp án / Câu hỏi+lời giải (tùy chọn đáp án, lời giải, taxonomy, xáo trộn) |
| 📈 Thống kê | Biểu đồ phân bố |

**Luồng đầy đủ:** Nạp đề → tách câu → phân loại (heuristic/người duyệt) →
kiểm tra trùng → hàng đợi thẩm định → duyệt → ngân hàng → tìm/lọc → tạo đề Word.

---

## 3. Cấu trúc dự án

```
vatly_question_bank/
├── app.py                 # Streamlit app (UI)
├── requirements.txt
├── core/
│   ├── db.py              # Schema SQLite + hằng số
│   ├── seed_taxonomy.py   # Seed 306 nodes taxonomy từ CTGDPT 2018
│   ├── parser.py          # Tách câu hỏi (PDF/DOCX/TXT/XLSX)
│   ├── classifier.py      # Phân loại heuristic (không AI trả phí)
│   ├── ai_engine.py       # Lớp AI Classification Engine (contract cho Phase 2)
│   ├── duplicate.py       # Phát hiện trùng 4 mức (SequenceMatcher)
│   ├── exporter.py        # Xuất Word (python-docx) + JSON
│   └── service.py         # Nghiệp vụ CRUD + pipeline
├── ui/
│   └── compare.py         # Màn so sánh trùng song song (highlight)
├── data/                  # bank.db + uploads/ + exports/ (tự sinh)
└── tests/
    ├── test_suite.py      # Test 1..8 theo đặc tả (21 assertions)
    ├── test_e2e.py        # E2E với đề thật 2025
    └── test_real_exams.py # Parse đề thật 2025/2026 + kiểm tra seed
```

---

## 4. Phát hiện trùng – 4 mức

So sánh bằng chuẩn hóa nội dung (bỏ số câu, khoảng trắng, dấu) + `SequenceMatcher`,
kết hợp nội dung (70%) và phương án (30%):

| Mức | Điểm | Hành động |
| --- | --- | --- |
| Mức 1 – Trùng 100% | ≥ 0.95 | Cảnh báo **không đưa vào ngân hàng**; chặn duyệt Đạt |
| Mức 2 – Gần trùng | ≥ 0.75 | **CẦN THẨM ĐỊNH** |
| Mức 3 – Tương đồng | ≥ 0.45 | Không loại tự động |
| Mức 4 – Không trùng | < 0.45 | Đưa vào sau khi duyệt |

**Nguyên tắc:** hai câu cùng kiến thức KHÔNG tự động bị coi là trùng; màn hình
so sánh song song hiển thị % tương đồng + highlight đoạn giống + ID/nguồn/đáp án/taxonomy.

---

## 5. Taxonomy (bám CTGDPT 2018 – Thông tư 32/2018/TT-BGDĐT)

Cây 4 cấp, 306 node (seed tự động khi khởi động):

- **Cấp 1 – Mạch nội dung (10):** Mở đầu, Cơ học, Sóng học, Nhiệt học, Điện học,
  Từ học, Quang học, Vật lí hạt nhân và phóng xạ, Vật lí hiện đại, Trái Đất và bầu trời.
- **Cấp 2 – Nội dung (23):** lấy đúng tên nội dung của chương trình theo từng lớp
  (vd "Động học", "Dao động", "Khí lí tưởng", "Trường điện (Điện trường)"...).
- **Cấp 3 – Đơn vị kiến thức (70):** vd "Mô tả chuyển động", "Ba định luật Newton", "Phương trình trạng thái"...
- **Cấp 4 – Yêu cầu cần đạt (203):** trích **nguyên văn** từ chương trình — không suy diễn.

Người dùng có thể thêm/sửa/xóa/di chuyển node; taxonomy lưu độc lập bảng `taxonomy_nodes`.

---

## 6. Database (SQLite – `data/bank.db`)

Bảng chính:

- `sources` – nguồn chuẩn (nhóm, năm, mô tả, file, trạng thái).
- `taxonomy_nodes` – cây 4 cấp (level, name, parent_id, grade, source).
- `exams` – metadata đề thi (tên, đơn vị, năm, mã đề, nguồn, file).
- `questions` – câu hỏi (đủ 30+ trường theo đặc tả §15: text, options JSON, answer,
  solution, image_path, strand/content/unit/outcome id+name, cognitive_level,
  difficulty, duplicate_status, similarity_score, related_question_ids,
  classification_confidence, classification_basis, review_status, reviewer, review_note...).
- `settings` – key/value (dành cho mở rộng).

Schema mở rộng được cho Phase 2/3 (ma trận đề, tạo đề tự động, AI).

---

## 7. AI Layer (`core/ai_engine.py`)

MVP **không gọi AI trả phí**. Lớp `ClassificationEngine` định nghĩa hợp đồng
`Question → Context → Taxonomy → Classification` trả đúng schema §18
(`content_strand, content, knowledge_unit, learning_outcome, question_type,
cognitive_level, difficulty, confidence, classification_basis, duplicate_candidates`).
Provider mặc định là `HeuristicProvider` (chạy cục bộ). Để tích hợp API trả phí
(Phase 2): implement `BaseClassificationProvider` và đặt vào config.
Mọi kết quả phân loại luôn có `confidence` + `classification_basis`; người dùng
luôn **sửa được trước khi lưu**; nếu thiếu căn cứ (không xác định được YCCĐ)
hệ thống đánh dấu **CẦN THẨM ĐỊNH** — không tự bịa.

---

## 8. Deploy miễn phí (3 cách)

### A. Streamlit Community Cloud (khuyến nghị)
1. Push repo lên GitHub.
2. https://streamlit.io/cloud → New app → chọn repo + `app.py`.
3. Xong, app chạy tại `https://<tên>.streamlit.app`.
   *Lưu ý: đĩa ephemeral — dữ liệu `data/bank.db` không bền giữa các lần khởi
   động; nên bật cơ chế export/import (màn hình Tạo đề có nút xuất JSON).*

### B. Render (free web service)
1. `render.yaml` được cung cấp sẵn (gồm `web: streamlit run app.py`).
2. Render → New Web Service → Python → build `pip install -r requirements.txt` → start `streamlit run app.py`.

### C. Local/self-host
```bash
streamlit run app.py --server.port 8607 --server.address 0.0.0.0
```

Không phụ thuộc dịch vụ trả phí nào. Muốn đổi DB sang PostgreSQL/Supabase:
thay `core/db.py` (giữ nguyên interface) — Phase 2.

---

## 9. Chạy kiểm thử

```bash
python tests/test_suite.py        # 21 assertions – Test 1..8 theo đặc tả §22
python tests/test_e2e.py          # E2E với Đề chính thức 2025 (28 câu)
python tests/test_real_exams.py   # Parse đề 2025/2026 + verify seed taxonomy
python tests/test_ui_smoke.py     # Render 8 trang UI qua AppTest
```

Kết quả hiện tại: **21/21 PASS**, E2E PASS, UI smoke 8/8 PASS.

## 10. Dữ liệu demo (101 câu từ 3 đề thật)

Đã nạp sẵn vào `data/bank.db` bằng `scripts/populate_demo.py`:
- Đề tham khảo TN THPT 2025 – Vật lí (27 câu)
- Đề chính thức TN THPT 2025 – Vật lí (28 câu)
- Đề chính thức TN THPT 2026 – Vật lí (46 câu)

Mỗi câu đã có mạch nội dung (heuristic), 20 câu được tự đánh dấu trùng/gần
trùng với câu khác — mở màn hình **Thẩm định** để thấy luồng duyệt có dữ liệu.
Nạp lại từ đầu: `python scripts/populate_demo.py`.

---

## 10. Đã hoàn thành / Chưa hoàn thành

### ✅ Đã hoàn thành (Phase 1)
- Web chạy được (Streamlit, không cần backend trả phí).
- Quản lý taxonomy 4 cấp (seed CTGDPT 2018 + CRUD).
- Nạp đề PDF/DOCX/TXT/XLSX + tách câu tự động (3 dạng câu).
- Phân loại thủ công + heuristic; confidence + căn cứ; CẦN THẨM ĐỊNH khi thiếu căn cứ.
- Phát hiện trùng 4 mức; chặn duyệt câu Trùng 100%; so sánh song song + highlight.
- Hàng đợi thẩm định (6 trạng thái), chỉnh sửa trực tiếp, duyệt Đạt → ngân hàng.
- Tìm kiếm/lọc đa tiêu chí; chọn nhiều câu.
- Xuất Word: đề thi / ngân hàng / đáp án / câu hỏi+lời giải; giữ ảnh, công thức
  Unicode, bảng Đúng-Sai, ô trả lời ngắn; xuất JSON.
- Dashboard + Thống kê.
- Tài liệu: README + file Word đặc tả + hướng dẫn sử dụng.

### ⏳ Chưa hoàn thành (Phase 2 – roadmap)
- OCR cho PDF scan (phase 2).
- AI phân loại / phát hiện trùng nâng cao (semantic embedding) – lớp đã sẵn sàng.
- Chuẩn hóa công thức tự động (MathML/OMML), nhận diện đồ thị/hình.
- Ma trận đề, tạo đề tự động, đánh giá độ phủ (Phase 3).

---

## 11. Roadmap Phase 2-3

- **Phase 2:** AI classification (provider API tùy chọn, heuristic giữ làm fallback),
  AI near-duplicate, OCR, nhận diện ảnh/đồ thị, chuẩn hóa công thức.
- **Phase 3:** Ma trận đề, tự động chọn câu theo ma trận, tạo đề tự động,
  thống kê chất lượng ngân hàng, độ phủ kiến thức, AI biên tập/sinh câu.

Xem chi tiết trong **Đặc_tả_Web_MVP_Ngân_hàng_câu_hỏi_Vật_lí.docx**.