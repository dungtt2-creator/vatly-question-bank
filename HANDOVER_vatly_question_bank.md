# HANDOVER – NGÂN HÀNG CÂU HỎI VẬT LÍ – TN THPT (WEB MVP)
*Bàn giao phiên làm việc 30/09/2026 — file này là nguồn thông tin đầy đủ nhất cho phiên tiếp theo.*

---

## 1. TÌNH TRẠNG TỔNG QUAN

- **Web MVP HOÀN CHỈNH, đang chạy local** tại `http://localhost:8607` (Streamlit).
- **Repo GitHub public:** https://github.com/dungtt2-creator/vatly-question-bank
  (4 commit, working tree sạch, đã push hết — commit cuối `d2711a1`)
- **Deploy cloud:** CHƯA bấm Deploy trên share.streamlit.io (người dùng phải tự
  đăng nhập GitHub/Streamlit; trình duyệt sandbox không có session — xem mục 9).
- **DB demo:** 83 câu từ 3 đề thật + 306 node taxonomy. Server đang chạy (PID 16712, port 8607).

## 2. ĐƯỜNG DẪN QUAN TRỌNG

| Thứ | Đường dẫn |
|---|---|
| Dự án | `G:\Other computers\My Laptop\THIỀU DUNG\7. TÀI LIỆU ĐỊNH HƯỚNG CÁC KÌ THI\TN THPT\vatly_question_bank\` |
| App chính | `app.py` (Streamlit, 8 trang) |
| Core | `core\` (db, parser, classifier, duplicate, exporter, service, ai_engine, formula_extract, taxo_match, seed_taxonomy) |
| DB | `data\bank.db` (SQLite) |
| Ảnh công thức render | `data\formulas\<hash>\formula_*.png` (304 PNG, 6.9MB) |
| File đặc tả Word | `data\exports\Đặc_tả_Web_MVP_Ngân_hàng_câu_hỏi_Vật_lí.docx` (39 blocks) |
| Test | `tests\test_suite.py` (21 assertions), `test_formulas.py`, `test_e2e.py`, `test_ui_smoke.py`, `test_real_exams.py` |
| Demo data | `scripts\populate_demo.py` |
| Đề gốc | `TN THPT\1. Đề tham khảo 2025\`, `2. Đề chính thức 2025\`, `3. Đề chính thức 2026\` (cạnh dự án) |

## 3. CÁCH CHẠY

```bash
cd "...\TN THPT\vatly_question_bank"
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8607
```
- Venv đã có sẵn: `.\.venv\` (Python 3.11; streamlit 1.64, python-docx 1.2, pdfplumber, pypdfium2, pywin32, Pillow, rapidfuzz, openpyxl, pandas).
- Deploy cloud: Streamlit Cloud (`app.py`) hoặc Render (`render.yaml`). **Lưu ý:** cloud không có Word COM → công thức MathType không render được thành ảnh (hiện "[công thức]").

## 4. CHỨC NĂNG ĐÃ HOÀN THÀNH (Phase 1 — toàn bộ)

- Dashboard, Nguồn chuẩn, Taxonomy (cây 4 cấp CRUD), Nạp đề (tách câu 3 dạng), Thẩm định (6 trạng thái + so sánh song song), Ngân hàng (lọc đa tiêu chí + từ khóa), Tạo đề (Word 4 chế độ), Thống kê.
- **Phát hiện trùng 4 mức** (Mức 1 ≥0.95 chặn duyệt), **CẦN THẨM ĐỊNH** khi thiếu YCCĐ, **mức độ ≠ độ khó** (2 trường riêng), AI layer contract (`ai_engine.py`, heuristic local, không API trả phí).
- **Taxonomy** 306 node seed từ Thông tư 32/2018/TT-BGDĐT (10 mạch / 23 nội dung / 70 ĐVKT / 203 YCCĐ nguyên văn) — KHÔNG bịa.
- **Xuất Word** giữ ảnh, công thức (PNG nhúng), bảng Đúng-Sai, ô trả lời ngắn; xuất JSON.

## 5. TÍNH NĂNG MỚI 30/09 (bản vá 2 lỗi lớn — commit 0afd6cf + d2711a1)

1. **Công thức MathType hiển thị được** — `core/formula_extract.py`:
   - Đề dùng OLE objects (MathType) + ảnh WMF; python-docx bỏ qua w:object → công thức mất.
   - Giải pháp: lxml thay `w:object`→`[[FORMULA:n]]`, `w:drawing`→`[[IMG:n]]`; **Word COM (pywin32)** `CopyAsPicture()` từng OLE → doc tạm (mỗi cái 1 trang, có page break) → ExportAsFixedFormat PDF → **pypdfium2** render scale 3x → `_autocrop()` → PNG; cache theo hash path trong `data/formulas\<hash>\`.
   - Parser giữ placeholder trong text + map `formulas {n: path}` lưu DB (JSON); UI dùng `show_assets()` hiển thị ảnh (màn Nạp đề preview, Thẩm định, Chi tiết), exporter dùng `_add_text_with_formulas()` chèn ảnh đúng vị trí (width Cm(4)).
   - **Điều kiện:** cần Word cài trên máy + pywin32. Tham khảo render: CT2025 38 OLE → 38 PNG OK.
2. **Lời giải tách khỏi phương án** — parser `_split_block()`:
   - Marker "Hướng dẫn / Hướng dẫn giải / Lời giải / Giải / Đáp án:" → phần sau vào `solution` riêng; options sạch (0 dính).
   - Đáp án bắt từ "Đáp án: B" hoặc dòng "Chọn B" cuối → answer.
3. **Bug bắt kèm:** (a) cắt text tại "HẾT"/"ĐÁP ÁN" (đáp án lọt vào câu cuối gây nhận nhầm Đ/S); (b) đề 3 PHẦN (I MCQ / II Đ/S / III TL ngắn) đánh số lại → thêm cột `part` (1/2/3) phân biệt; (c) ảnh đứng trước "Câu N." làm mất câu → pattern `[[IMG:n]]Câu N.`; (d) `qrow_to_dict` parse `image_path` JSON.

## 6. TRẠNG THÁI DỮ LIỆU (lúc bàn giao)

- **83 câu:** Đề tham khảo 2025 (28: P1-MCQ 18, P2-Đ/S 4, P3-TL 6 — file DOCX kèm ma trận+lời giải, 17 câu có solution) + CT 2025 (28: chính xác 18/4/6, 11 câu công thức) + CT 2026 (28: 18/4/6, có 2 câu dùng chung đề mô tả "Nội dung câu 1 và 2").
- Tất cả 83 câu có `review_status='Chờ duyệt'`, mạch nội dung gắn tự động (1 câu trống mạch), 37 câu có formulas ảnh, 10 câu có ảnh minh họa image_path.
- Taxonomy: 306 node; sources: 3 (mỗi đề 1 source); exams: 3.

## 7. KIỂM THỬ (tất cả PASS lúc bàn giao)

- `tests/test_suite.py` → 21/21 (Test 1-8 đặc tả)
- `tests/test_formulas.py` → ALL PASS (công thức + lời giải + DB + export)
- `tests/test_e2e.py` → PASS (pipeline đề thật, trùng Mức 1 score 1.0, chặn duyệt trùng)
- `tests/test_ui_smoke.py` → 8/8 trang render OK
- Chạy lại nhanh: `.\.venv\Scripts\python.exe tests\test_suite.py`

## 8. CHƯA LÀM / VIỆC TIẾP THEO ĐỀ XUẤT

- [ ] **Deploy Streamlit Cloud**: user tự đăng nhập https://share.streamlit.io/deploy → repo `dungtt2-creator/vatly-question-bank` → branch main → app.py → Deploy. (Trình duyệt sandbox không có session GitHub/Streamlit; không đoán mật khẩu.)
- [ ] Cloud không có Word → công thức sẽ thành "[công thức]". Hướng: commit sẵn PNG render vào repo (thêm `data/formulas` vào git) hoặc chuyển sang MathML/OMML (Phase 2).
- [ ] Nút "duyệt nhanh" hàng loạt 83 câu demo (hiện tất cả Chờ duyệt).
- [ ] Supabase free tier nếu muốn dữ liệu bền trên cloud (interface `core/db.py` đã chừa).
- [ ] Phase 2: AI provider API, OCR PDF (03_VatLi.pdf đề TK 2025 là scan → 0 câu), embedding near-duplicate.

## 9. LƯU Ý KỸ THUẬT / CẠM BẪY

- **Windows shell = git-bash (MSYS):** luôn dùng `./.venv/Scripts/python.exe`; path native cho tool Windows dùng dạng `C:/...`.
- **browser_exec lỗi Unicode:** stdout bị lỗi `UnicodeEncodeError` khi in tiếng Việt → phải dùng `escape()`/base64 trong JS khi trả text về.
- **WMF/EMF không mở bằng Pillow:** `register_wmf` đã bị gỡ khỏi Pillow 12 → bắt buộc Word COM.
- **MathType render cần page break mỗi ảnh** (`InsertBreak(7)`) nếu không các công thức dồn 1 trang → chỉ map được 2-3 PNG.
- **lxml vs regex:** thay `w:object` PHẢI dùng `_replace_with_text(el, text)` đặt run mới ở cấp `w:p` (không lồng trong w:r cũ) nếu không python-docx đọc text mất placeholder.
- Parser phần đề: cắt đuôi "HẾT"/"ĐÁP ÁN" TRƯỚC khi tách câu, nếu không câu cuối nuốt cả đáp án (nhận nhầm Đúng/Sai vì chữ "đúng hoặc sai" trong phần II mô tả).
- `data/formulas/` đã thêm vào .gitignore (6.9MB, không đẩy lên git).
- Server hiện đang chạy (PID 16712). Nếu cần khởi động lại: xem mục 3.

## 10. THÔNG TIN NGƯỜI DÙNG (context phiên)

- User làm nội dung giáo dục Vật lí (ôn thi TN THPT 2025/2026), thích sản phẩm chạy được + tài liệu Word đầy đủ, giao tiếp tiếng Việt.
- Git: user `dungtt2-creator`, push dùng token từ `git credential fill`.
- Nói tiếng Việt, deliver gọn, ưu tiên "đơn giản, ổn định, mở rộng được".