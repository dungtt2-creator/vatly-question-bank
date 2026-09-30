# -*- coding: utf-8 -*-
"""
Ngân hàng câu hỏi Vật lí – TN THPT (MVP)
App Streamlit: Dashboard | Nguồn chuẩn | Taxonomy | Nạp đề | Thẩm định | Ngân hàng câu hỏi | Tạo đề | Thống kê

Chạy:  streamlit run app.py
"""
import os
import sys
import json
import io
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import streamlit as st
import pandas as pd

from core import db as dbm
from core import service as svc
from core import parser as psr
from core import exporter as exp
from core import duplicate as dup
from core.seed_taxonomy import seed_taxonomy
from core.ai_engine import ClassificationEngine

st.set_page_config(page_title="Ngân hàng câu hỏi Vật lí – TN THPT", page_icon="⚛️", layout="wide")

# ---------------- init ----------------
dbm.init_db()
seed_taxonomy()
if "selected_qids" not in st.session_state:
    st.session_state.selected_qids = set()
if "last_parsed" not in st.session_state:
    st.session_state.last_parsed = []
if "last_exam_id" not in st.session_state:
    st.session_state.last_exam_id = None


def esc(s):
    return (s or "").replace("\n", "<br>").replace("|", "\\|")


def fmt_short(s, n=110):
    s = (s or "").replace("\n", " ")
    return s if len(s) <= n else s[: n - 3] + "…"


def selectbox_kv(label, options, key=None, format_fn=str, **kw):
    """selectbox với dict options {label: value}."""
    if not options:
        return None
    opts = list(options.keys())
    val = st.selectbox(label, opts, key=key, format_func=format_fn, **kw)
    return options[val]


# ---------------- HEADER ----------------
st.sidebar.title("⚛️ Ngân hàng câu hỏi Vật lí")
st.sidebar.caption("TN THPT – theo CTGDPT 2018")
page = st.sidebar.radio(
    "Điều hướng",
    ["📊 Dashboard", "📚 Nguồn chuẩn", "🌳 Taxonomy", "📥 Nạp đề", "✅ Thẩm định",
     "🗄️ Ngân hàng câu hỏi", "📝 Tạo đề", "📈 Thống kê"],
)
st.sidebar.markdown("---")
st.sidebar.caption("MVP v1.0 — dữ liệu lưu cục bộ SQLite")

# ============================== DASHBOARD ==============================
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.caption("Tổng quan ngân hàng câu hỏi Vật lí TN THPT")
    stats = svc.stats_overview()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tổng số câu", stats["total"])
    c2.metric("Đã duyệt", stats["reviewed"])
    c3.metric("Trùng 100%", stats["dups"])
    c4.metric("Cần thẩm định", stats["need_review"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Phân bố theo mạch nội dung")
        df = pd.DataFrame(stats["by_strand"])
        if not df.empty:
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu")
    with col2:
        st.subheader("Phân bố theo dạng câu")
        df = pd.DataFrame(stats["by_type"])
        if not df.empty:
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu")
    with col3:
        st.subheader("Phân bố theo mức độ tư duy")
        df = pd.DataFrame(stats["by_level"])
        if not df.empty:
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu")

    st.markdown("---")
    st.subheader("Quy trình sử dụng")
    steps = ["1. Nạp tài liệu chuẩn (Nguồn chuẩn)",
             "2. Kiểm tra cây taxonomy (Taxonomy)",
             "3. Upload đề thi (Nạp đề) → tự tách câu + gắn taxonomy sơ bộ",
             "4. Duyệt từng câu ở màn hình Thẩm định",
             "5. Tra cứu/lọc ở Ngân hàng câu hỏi",
             "6. Chọn câu → Tạo đề Word"]
    for s in steps:
        st.write(s)

# ============================== NGUỒN CHUẨN ==============================
elif page == "📚 Nguồn chuẩn":
    st.title("📚 Nguồn chuẩn")
    st.caption("Tài liệu làm căn cứ phân loại: CTGDPT 2018, đề tham khảo, đề chính thức...")

    with st.expander("➕ Thêm nguồn chuẩn", expanded=False):
        with st.form("add_source"):
            name = st.text_input("Tên tài liệu *")
            group = st.selectbox("Nhóm nguồn", dbm.SOURCE_GROUPS)
            year = st.number_input("Năm", min_value=2000, max_value=2035, value=2025, step=1)
            desc = st.text_area("Mô tả")
            status = st.selectbox("Trạng thái", ["Đang sử dụng", "Ngừng sử dụng"])
            f = st.file_uploader("File nguồn (PDF/DOCX/TXT, tùy chọn)", type=["pdf", "docx", "txt"])
            submitted = st.form_submit_button("Lưu")
            if submitted:
                if not name.strip():
                    st.error("Cần nhập tên tài liệu")
                else:
                    fp, fn = "", ""
                    if f is not None:
                        fp, fn = svc.save_upload(f, "sources")
                    svc.add_source(name.strip(), group, int(year), desc, fp, fn, status)
                    st.success(f"Đã thêm nguồn: {name}")

    st.subheader("Danh sách nguồn")
    srcs = svc.list_sources()
    if not srcs:
        st.info("Chưa có nguồn nào. Hãy thêm tài liệu chuẩn đầu tiên (khuyến nghị: CTGDPT 2018 môn Vật lí – Thông tư 32).")
    for s in srcs:
        with st.expander(f"[{s['group_name']}] {s['name']} ({s.get('year','')})", expanded=False):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.write(f"**Mô tả:** {s.get('description') or '—'}")
                if s.get("file_name"):
                    st.write(f"**File:** {s['file_name']}")
                st.write(f"**Trạng thái:** {s.get('status')}")
            with c2:
                if st.button("Sửa tên", key=f"es_{s['id']}"):
                    new = st.text_input("Tên mới", value=s["name"], key=f"en_{s['id']}")
                    if st.button("Lưu", key=f"esav_{s['id']}"):
                        svc.update_source(s["id"], name=new)
                        st.rerun()
            with c3:
                if st.button("🗑 Xóa", key=f"ds_{s['id']}"):
                    svc.delete_source(s["id"])
                    st.rerun()

            # Edit trực tiếp trong form nhỏ
            with st.form(f"upd_src_{s['id']}"):
                n2 = st.text_input("Tên", value=s["name"], key=f"n2_{s['id']}")
                g2 = st.selectbox("Nhóm", dbm.SOURCE_GROUPS, index=dbm.SOURCE_GROUPS.index(s["group_name"]) if s["group_name"] in dbm.SOURCE_GROUPS else 0, key=f"g2_{s['id']}")
                y2 = st.number_input("Năm", value=int(s.get("year") or 2025), key=f"y2_{s['id']}")
                st2 = st.selectbox("Trạng thái", ["Đang sử dụng", "Ngừng sử dụng"], index=0 if s.get("status") == "Đang sử dụng" else 1, key=f"st2_{s['id']}")
                if st.form_submit_button("Cập nhật"):
                    svc.update_source(s["id"], name=n2, group_name=g2, year=int(y2), status=st2)
                    st.rerun()

# ============================== TAXONOMY ==============================
elif page == "🌳 Taxonomy":
    st.title("🌳 Cấu trúc kiến thức (Taxonomy)")
    st.caption("Cây 4 cấp: Mạch nội dung → Nội dung → Đơn vị kiến thức → Yêu cầu cần đạt (bám CTGDPT 2018 – Thông tư 32)")

    c1, c2 = st.columns([3, 2])
    with c1:
        q = st.text_input("🔍 Tìm trong taxonomy", key="tax_search")
        tree = svc.get_taxonomy_tree()

        def render(node, depth=0):
            pad = "&nbsp;" * (depth * 4)
            marker = "📁" if node["children"] else "📄"
            level_icon = {1: "🟦", 2: "🟩", 3: "🟨", 4: "⬜"}.get(node["level"], "")
            label = f"{pad}{level_icon} {marker} {node['name']}"
            if node.get("grade"):
                label += f" <span style='color:gray'>({node['grade']})</span>"
            st.markdown(label, unsafe_allow_html=True)
            if node["children"]:
                for ch in node["children"]:
                    render(ch, depth + 1)

        if q:
            matches = svc.taxonomy_lookup(q, topn=50)
            if matches:
                for m in matches:
                    st.markdown(f"- 🎯 **L{['', 'Mạch', 'Nội dung', 'ĐVKT', 'YCCĐ'][m['level']]}:** {m['name']}  ({m.get('grade','')})")
            else:
                st.info("Không tìm thấy")
        else:
            with st.container(height=520, border=True):
                for node in tree:
                    render(node)

    with c2:
        st.subheader("➕ Thêm node mới")
        with st.form("add_tax"):
            level = st.selectbox("Cấp", [1, 2, 3, 4], format_func=lambda x: {1: "1 – Mạch nội dung", 2: "2 – Nội dung", 3: "3 – Đơn vị kiến thức", 4: "4 – Yêu cầu cần đạt"}[x])
            # parent theo level
            parent_opts = {}
            nodes = []
            conn = dbm.get_conn()
            allrows = conn.execute("SELECT * FROM taxonomy_nodes ORDER BY level, sort_order, id").fetchall()
            conn.close()
            for r in allrows:
                nodes.append(dict(r))
            if level == 1:
                parent_opts = {"— (cấp gốc)": None}
            elif level == 2:
                parent_opts = {f"🟦 {n['name']}" : n["id"] for n in nodes if n["level"] == 1}
            elif level == 3:
                parent_opts = {f"🟩 {n['name']}" : n["id"] for n in nodes if n["level"] == 2}
            else:
                parent_opts = {f"🟨 {n['name']}" : n["id"] for n in nodes if n["level"] == 3}
            if not parent_opts and level > 1:
                st.warning("Cần có node cấp trên trước (seed đã tạo sẵn)")

            parent_label = st.selectbox("Node cha", list(parent_opts.keys())) if parent_opts else None
            name = st.text_input("Tên node *")
            grade = st.selectbox("Lớp", dbm.CLASS_LEVELS) if level >= 2 else None
            source = st.text_input("Căn cứ (nguồn)", value="Thông tư 32/2018/TT-BGDĐT – CTGDPT 2018 môn Vật lí")
            note = st.text_area("Ghi chú", height=60)
            if st.form_submit_button("Thêm"):
                if not name.strip():
                    st.error("Cần nhập tên")
                elif level > 1 and (not parent_label or parent_opts.get(parent_label) is None):
                    st.error("Cần chọn node cha")
                else:
                    pid = parent_opts.get(parent_label) if parent_label else None
                    svc.add_taxonomy_node(level, name.strip(), pid, grade or "", source, note)
                    st.success(f"Đã thêm: {name}")
                    st.rerun()

        st.divider()
        st.subheader("✏️ Sửa / Xóa / Di chuyển")
        node_opts = {f"L{n['level']} – {n['name']}" : n["id"] for n in nodes}
        if node_opts:
            sel_label = st.selectbox("Chọn node", list(node_opts.keys()), key="tax_sel")
            nid = node_opts[sel_label]
            with st.form("upd_tax"):
                nn = st.text_input("Tên mới", value=sel_label.split(" – ", 1)[1], key="tax_nn")
                ng = st.selectbox("Lớp", dbm.CLASS_LEVELS, key="tax_ng")
                submit = st.form_submit_button("Cập nhật tên")
                if submit:
                    svc.update_taxonomy_node(nid, name=nn, grade=ng if ng and ng != "Không gắn lớp" else "")
                    st.rerun()
            if st.button("🗑 Xóa node này + toàn bộ con", key=f"tax_del_{nid}"):
                svc.delete_taxonomy_node(nid)
                st.rerun()

# ============================== NẠP ĐỀ ==============================
elif page == "📥 Nạp đề":
    st.title("📥 Nạp đề thi")
    st.caption("Upload PDF / DOCX / XLSX / TXT → hệ thống tách câu, phân loại sơ bộ, phát hiện trùng")

    with st.form("upload_exam"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Tên đề *", value="")
        org = c2.text_input("Đơn vị ra đề")
        c3, c4 = st.columns(2)
        year = c3.number_input("Năm", min_value=2000, max_value=2035, value=2025)
        exam_code = c4.text_input("Mã đề")
        c5, c6 = st.columns(2)
        subject = c5.selectbox("Môn", ["Vật lí", "Vật lý"])
        srcs = svc.list_sources()
        src_opts = {s["name"]: s["id"] for s in srcs}
        src_label = st.selectbox("Nguồn (tùy chọn)", ["—"] + list(src_opts.keys())) if src_opts else None
        note = st.text_area("Ghi chú")
        f = st.file_uploader("File đề (*.pdf, *.docx, *.xlsx, *.txt)", type=["pdf", "docx", "xlsx", "txt"])
        submitted = st.form_submit_button("🚀 Tải lên và tách câu")

    if submitted:
        if not name.strip():
            st.error("Cần nhập tên đề")
        else:
            if f is None:
                st.error("Cần chọn file đề")
            else:
                fp, fn = svc.save_upload(f)
                with st.spinner("Đang tách câu hỏi..."):
                    try:
                        questions = psr.parse_exam_file(fp, year, name)
                    except Exception as e:
                        st.error(f"Lỗi đọc file: {e}")
                        questions = []
                if not questions:
                    st.error("Không tách được câu nào. Kiểm tra định dạng file (đề scan cần OCR – Phase 2).")
                else:
                    source_id = src_opts.get(src_label) if src_label != "—" else None
                    exam_id = svc.add_exam(name.strip(), org, int(year), exam_code, source_id, note, fp, fn)
                    st.session_state.last_parsed = questions
                    st.session_state.last_exam_id = exam_id
                    st.success(f"Đã tách **{len(questions)} câu**. Duyệt kết quả bên dưới rồi nhấn 'Lưu vào ngân hàng'.")

    # === Xem & sửa trước khi lưu ===
    if st.session_state.last_parsed:
        st.divider()
        st.subheader(f"Kết quả tách – {len(st.session_state.last_parsed)} câu")
        questions = st.session_state.last_parsed

        # Phân loại heuristic preview
        engine = ClassificationEngine()
        enriched = []
        for i, q in enumerate(questions):
            cl = engine.classify_question(q)
            enriched.append({**q, "_cl": cl})

        # Chỉnh sửa hàng loạt theo từng câu + nút lưu
        with st.expander("⚠️ Ghi chú trước khi lưu", expanded=False):
            st.markdown("""
- **Phân loại mạch/dạng câu** là gợi ý heuristic (confidence ≤ 0.92). Bạn **sửa được** từng câu ở đây
  hoặc chi tiết hơn ở màn hình **Thẩm định** sau khi lưu.
- **Kiểm tra trùng** chạy tự động lúc lưu, so với toàn bộ câu đã có trong ngân hàng.
- Nếu câu **CẦN THẨM ĐỊNH** (không đủ căn cứ), hệ thống vẫn lưu nhưng đánh dấu để người duyệt xử lý.
            """)

        type_map = {"MCQ 4 lựa chọn": "MCQ 4 lựa chọn", "Đúng/Sai": "Đúng/Sai", "Trả lời ngắn": "Trả lời ngắn"}

        for i, q in enumerate(enriched):
            cl = q["_cl"]
            with st.expander(f"Câu {q['question_number']} – {fmt_short(q['question_text'], 80)}", expanded=i == 0):
                c1, c2 = st.columns([3, 2])
                with c1:
                    st.text_area(f"Nội dung câu {q['question_number']}", value=q["question_text"],
                                 key=f"qt_{i}", height=130)
                    if q["options"]:
                        new_opts = []
                        for j, o in enumerate(q["options"]):
                            v = st.text_input(f"Phương án {chr(65+j)}", value=o, key=f"qo_{i}_{j}")
                            new_opts.append(v)
                        q["options"] = new_opts
                    st.text_input(f"Đáp án (nếu có)", value=q.get("answer", ""), key=f"qa_{i}",
                                  placeholder="VD: B hoặc Đ-S-S-Đ")
                with c2:
                    st.markdown("**🎯 Gợi ý phân loại (heuristic):**")
                    st.markdown(f"- Mạch nội dung: **{cl['content_strand'] or '(chưa rõ)'}**")
                    st.markdown(f"- Dạng câu: **{cl['question_type']}**")
                    st.markdown(f"- Mức độ: **{cl['cognitive_level'] or '(chưa rõ)'}**")
                    st.markdown(f"- Độ khó: **{cl['difficulty']}**")
                    st.markdown(f"- Độ tin cậy: **{int(cl['confidence']*100)}%**")
                    if cl.get("needs_review"):
                        st.warning("⚠️ **CẦN THẨM ĐỊNH** – không đủ căn cứ tự động. Vui lòng duyệt tay.")
                    st.markdown(f"- Căn cứ: {cl['classification_basis'] or '—'}")

                    # Người dùng sửa phân loại
                    t2 = st.selectbox("Dạng câu", list(type_map.keys()),
                                       index=list(type_map.keys()).index(cl["question_type"]) if cl["question_type"] in type_map else 0,
                                       key=f"qty_{i}")
                    q["question_type"] = t2
                    lv = st.selectbox("Mức độ", ["", *dbm.COGNITIVE_LEVELS],
                                      index=(dbm.COGNITIVE_LEVELS.index(cl["cognitive_level"]) + 1) if cl["cognitive_level"] in dbm.COGNITIVE_LEVELS else 0,
                                      key=f"qlv_{i}")
                    q["cognitive_level"] = lv
                    df = st.selectbox("Độ khó", dbm.DIFFICULTIES,
                                      index=dbm.DIFFICULTIES.index(cl["difficulty"]) if cl["difficulty"] in dbm.DIFFICULTIES else 0,
                                      key=f"qdf_{i}")
                    q["difficulty"] = df

        if st.button("💾 Lưu toàn bộ vào ngân hàng (chạy kiểm tra trùng tự động)"):
            final = []
            for i, q in enumerate(enriched):
                final.append({
                    "question_number": q["question_number"],
                    "question_text": st.session_state[f"qt_{i}"] if f"qt_{i}" in st.session_state else q["question_text"],
                    "options": q["options"],
                    "answer": st.session_state.get(f"qa_{i}", q.get("answer", "")),
                    "question_type": q["question_type"],
                    "cognitive_level": q["cognitive_level"],
                    "difficulty": q["difficulty"],
                })
            ok_c, flagged_c, errors = svc.import_exam_pipeline(st.session_state.last_exam_id, final)
            if errors:
                st.warning("Một số câu lỗi:\n" + "\n".join(errors[:10]))
            st.success(f"Đã lưu **{ok_c + flagged_c} câu** (cảnh báo trùng/gần trùng: {flagged_c}). Đến màn hình **Thẩm định** để duyệt.")
            st.session_state.last_parsed = []
            st.rerun()

# ============================== THẨM ĐỊNH ==============================
elif page == "✅ Thẩm định":
    st.title("✅ Hàng đợi thẩm định")
    st.caption("Duyệt từng câu: chỉnh nội dung/đáp án/taxonomy/mức độ/độ khó → Đạt đưa vào ngân hàng")

    status_opts = {s: s for s in dbm.REVIEW_STATUSES}
    sel_status = st.selectbox("Trạng thái", ["Chờ duyệt", "Đã duyệt", "Trùng 100%", "Gần trùng", "Cần thẩm định", "Lỗi câu hỏi"],
                              format_func=lambda x: x)
    qs = svc.list_questions({"review_status": sel_status}, limit=500)

    if not qs:
        st.info("Không có câu nào ở trạng thái này.")
    else:
        st.write(f"**{len(qs)} câu** đang ở trạng thái **{sel_status}**")

        for q in qs:
            dup_badge = ""
            if q.get("duplicate_status"):
                dup_badge = f" | {q['duplicate_status']} ({q.get('similarity_score',0):.0%})"
            with st.expander(f"Q{q['id']} – {fmt_short(q['question_text'], 100)}{dup_badge}", expanded=False):
                c1, c2 = st.columns([3, 2])
                with c1:
                    nt = st.text_area("Nội dung (sửa được)", value=q["question_text"], key=f"rv_t_{q['id']}", height=130)
                    opts = q.get("options") or []
                    n_opts = []
                    for j, o in enumerate(opts):
                        n_opts.append(st.text_input(f"PA {chr(65+j)}", value=str(o), key=f"rv_o_{q['id']}_{j}"))
                    na = st.text_input("Đáp án", value=q.get("answer", ""), key=f"rv_a_{q['id']}")
                    nsol = st.text_area("Hướng dẫn giải", value=q.get("solution", ""), key=f"rv_s_{q['id']}", height=80)

                with c2:
                    # Taxonomy select
                    tree = svc.get_taxonomy_tree()
                    strand_opts = {f"🟦 {n['name']}": n for n in tree}
                    cur_strand = q.get("strand_name")
                    strand_label = None
                    if cur_strand:
                        for k, n in strand_opts.items():
                            if n["name"] == cur_strand:
                                strand_label = k
                                break
                    sl = st.selectbox("Mạch nội dung", list(strand_opts.keys()) + ["(xóa)"],
                                      index=(list(strand_opts.keys()).index(strand_label) if strand_label else 0),
                                      key=f"rv_sd_{q['id']}")
                    node = strand_opts.get(sl)
                    content_opts, unit_opts, outcome_opts = {}, {}, {}
                    if node:
                        content_opts = {f"🟩 {n['name']}": n for n in node["children"]}
                    cur_content = q.get("content_name")
                    cl_sel = None
                    if cur_content:
                        for k, n in content_opts.items():
                            if n["name"] == cur_content:
                                cl_sel = k
                                break
                    if content_opts:
                        cl = st.selectbox("Nội dung", list(content_opts.keys()),
                                          index=(list(content_opts.keys()).index(cl_sel) if cl_sel else 0),
                                          key=f"rv_c_{q['id']}")
                        cnode = content_opts.get(cl)
                        if cnode:
                            unit_opts = {f"🟨 {n['name']}": n for n in cnode["children"]}
                        if unit_opts:
                            cur_unit = q.get("unit_name")
                            ul_sel = None
                            for k, n in unit_opts.items():
                                if n["name"] == cur_unit:
                                    ul_sel = k
                                    break
                            ul = st.selectbox("Đơn vị kiến thức", list(unit_opts.keys()),
                                              index=(list(unit_opts.keys()).index(ul_sel) if ul_sel else 0),
                                              key=f"rv_u_{q['id']}")
                            unode = unit_opts.get(ul)
                            if unode:
                                outcome_opts = {f"⬜ {n['name'][:90]}": n for n in unode["children"]}
                            if outcome_opts:
                                cur_out = q.get("outcome_name")
                                ol_sel = None
                                for k, n in outcome_opts.items():
                                    if n["name"] == cur_out:
                                        ol_sel = k
                                        break
                                ol = st.selectbox("Yêu cầu cần đạt", list(outcome_opts.keys()),
                                                  index=(list(outcome_opts.keys()).index(ol_sel) if ol_sel else 0),
                                                  key=f"rv_o3_{q['id']}")

                    st.divider()
                    qtype = st.selectbox("Dạng câu", dbm.QUESTION_TYPES,
                                         index=dbm.QUESTION_TYPES.index(q.get("question_type")) if q.get("question_type") in dbm.QUESTION_TYPES else 0,
                                         key=f"rv_qt_{q['id']}")
                    cog = st.selectbox("Mức độ tư duy", ["", *dbm.COGNITIVE_LEVELS],
                                       index=(dbm.COGNITIVE_LEVELS.index(q.get("cognitive_level")) + 1) if q.get("cognitive_level") in dbm.COGNITIVE_LEVELS else 0,
                                       key=f"rv_cog_{q['id']}")
                    diff = st.selectbox("Độ khó", dbm.DIFFICULTIES,
                                        index=dbm.DIFFICULTIES.index(q.get("difficulty")) if q.get("difficulty") in dbm.DIFFICULTIES else 0,
                                        key=f"rv_df_{q['id']}")
                    nnote = st.text_area("Ghi chú thẩm định (review note)", value=q.get("review_note", ""), key=f"rv_n_{q['id']}", height=60)
                    reviewer = st.text_input("Người duyệt", value=q.get("reviewer", ""), key=f"rv_r_{q['id']}")

                st.markdown("#### Quyết định duyệt")

                # Màn so sánh trùng (§11) — hiện nếu câu có liên quan
                related = q.get("related_question_ids") or []
                if related and isinstance(related, list):
                    with st.expander("⚖️ Xem so sánh song song với câu trùng/gần trùng"):
                        from ui.compare import render_compare_screen
                        for rid in related[:3]:
                            bq = svc.get_question(rid)
                            if bq:
                                cmp = dup.compare_questions(q, bq)
                                render_compare_screen(q, bq, cmp)

                b1, b2, b3, b4, b5 = st.columns(5)
                if b1.button("✅ Đạt → ngân hàng", key=f"rv_ok_{q['id']}"):
                    ok, msg = svc.approve_to_bank(q["id"], reviewer, nnote)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                if b2.button("🔁 Chờ duyệt", key=f"rv_wait_{q['id']}"):
                    svc.review_question(q["id"], "Chờ duyệt", reviewer, nnote)
                    st.rerun()
                if b3.button("🛑 Trùng 100%", key=f"rv_dup_{q['id']}"):
                    svc.review_question(q["id"], "Trùng 100%", reviewer, nnote)
                    st.rerun()
                if b4.button("⚠️ Gần trùng / Cần thẩm định", key=f"rv_need_{q['id']}"):
                    svc.review_question(q["id"], "Cần thẩm định", reviewer, nnote)
                    st.rerun()
                if b5.button("❌ Lỗi câu hỏi", key=f"rv_err_{q['id']}"):
                    svc.review_question(q["id"], "Lỗi câu hỏi", reviewer, nnote)
                    st.rerun()

                # Lưu sửa chữa trước khi bấm duyệt (nút riêng)
                with st.form(f"save_edit_{q['id']}"):
                    if st.form_submit_button("💾 Lưu chỉnh sửa (không đổi trạng thái)"):
                        fields = {
                            "question_text": st.session_state.get(f"rv_t_{q['id']}", q["question_text"]),
                            "options": [st.session_state.get(f"rv_o_{q['id']}_{j}", o) for j, o in enumerate(opts)],
                            "answer": st.session_state.get(f"rv_a_{q['id']}", q.get("answer", "")),
                            "solution": st.session_state.get(f"rv_s_{q['id']}", q.get("solution", "")),
                            "question_type": st.session_state.get(f"rv_qt_{q['id']}", q.get("question_type")),
                            "cognitive_level": st.session_state.get(f"rv_cog_{q['id']}", q.get("cognitive_level")),
                            "difficulty": st.session_state.get(f"rv_df_{q['id']}", q.get("difficulty")),
                            "review_note": st.session_state.get(f"rv_n_{q['id']}", q.get("review_note")),
                            "reviewer": st.session_state.get(f"rv_r_{q['id']}", q.get("reviewer")),
                        }
                        # taxonomy
                        node_obj = strand_opts.get(sl) if sl in strand_opts else None
                        if node_obj:
                            fields["strand_id"] = node_obj["id"]
                            fields["strand_name"] = node_obj["name"]
                        cnode_obj = content_opts.get(cl) if content_opts and cl in content_opts else None
                        if cnode_obj:
                            fields["content_id"] = cnode_obj["id"]
                            fields["content_name"] = cnode_obj["name"]
                        unode_obj = unit_opts.get(ul) if unit_opts and ul in unit_opts else None
                        if unode_obj:
                            fields["unit_id"] = unode_obj["id"]
                            fields["unit_name"] = unode_obj["name"]
                        onode_obj = outcome_opts.get(ol) if outcome_opts and ol in outcome_opts else None
                        if onode_obj:
                            fields["outcome_id"] = onode_obj["id"]
                            fields["outcome_name"] = onode_obj["name"]
                        svc.update_question(q["id"], **fields)
                        st.success("Đã lưu chỉnh sửa")
                        st.rerun()

# ============================== NGÂN HÀNG CÂU HỎI ==============================
elif page == "🗄️ Ngân hàng câu hỏi":
    st.title("🗄️ Ngân hàng câu hỏi")
    st.caption("Tìm kiếm & lọc câu hỏi đã duyệt. Tick để chọn → Tạo đề ở trang 'Tạo đề'.")

    st.markdown("#### Bộ lọc")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        f_strand = st.selectbox("Mạch nội dung", ["(tất cả)"] + sorted({q["strand_name"] for q in svc.list_questions(limit=10000) if q.get("strand_name")}))
    with f2:
        f_type = st.selectbox("Dạng câu", ["(tất cả)"] + dbm.QUESTION_TYPES)
    with f3:
        f_cog = st.selectbox("Mức độ", ["(tất cả)"] + dbm.COGNITIVE_LEVELS)
    with f4:
        f_diff = st.selectbox("Độ khó", ["(tất cả)"] + dbm.DIFFICULTIES)
    f5, f6, f7 = st.columns(3)
    with f5:
        f_year = st.selectbox("Năm", ["(tất cả)"] + sorted({q.get("year") for q in svc.list_questions(limit=10000) if q.get("year")}, reverse=True))
    with f6:
        f_org = st.text_input("Đơn vị ra đề")
    with f7:
        f_src = st.selectbox("Nguồn", ["(tất cả)"] + sorted({q["source_name"] for q in svc.list_questions(limit=10000) if q.get("source_name")}))
    f8, f9 = st.columns(2)
    with f8:
        f_status = st.selectbox("Trạng thái duyệt", ["(tất cả)"] + dbm.REVIEW_STATUSES)
    with f9:
        f_dup = st.selectbox("Trạng thái trùng", ["(tất cả)"] + list(dbm.DUPLICATE_LEVELS))

    kw = st.text_input("🔍 Tìm kiếm theo từ khóa (nội dung câu hỏi)", placeholder="VD: dao động điều hòa, định luật bảo toàn động lượng...")

    filters = {}
    if f_strand != "(tất cả)": filters["strand_name"] = f_strand
    if f_type != "(tất cả)": filters["question_type"] = f_type
    if f_cog != "(tất cả)": filters["cognitive_level"] = f_cog
    if f_diff != "(tất cả)": filters["difficulty"] = f_diff
    if f_year != "(tất cả)": filters["year"] = f_year
    if f_org.strip(): filters["organization"] = f_org.strip()
    if f_src != "(tất cả)": filters["source_name"] = f_src
    if f_status != "(tất cả)": filters["review_status"] = f_status
    if f_dup != "(tất cả)": filters["duplicate_status"] = f_dup
    if kw.strip(): filters["q"] = kw.strip()

    qs = svc.list_questions(filters, limit=2000)
    st.write(f"**{len(qs)} câu** khớp bộ lọc")

    if qs:
        # Header table
        cols = st.columns([1, 4, 2, 2, 2, 2, 1.5])
        cols[0].markdown("**✔ Chọn**")
        cols[1].markdown("**Nội dung**")
        cols[2].markdown("**Dạng**")
        cols[3].markdown("**Mạch**")
        cols[4].markdown("**Mức độ**")
        cols[5].markdown("**Độ khó**")
        cols[6].markdown("**Nguồn/Năm**")

        for q in qs:
            c = st.columns([1, 4, 2, 2, 2, 2, 1.5])
            checked = c[0].checkbox("", key=f"sel_{q['id']}", value=q["id"] in st.session_state.selected_qids)
            if checked:
                st.session_state.selected_qids.add(q["id"])
            else:
                st.session_state.selected_qids.discard(q["id"])
            dup_tag = ""
            if q.get("duplicate_status"):
                dup_tag = f" <span style='color:orange'>[{q['duplicate_status']}]</span>"
            c[1].markdown(f"**Q{q['id']}** · {fmt_short(q['question_text'], 130)}{dup_tag}", unsafe_allow_html=True)
            c[2].write(q.get("question_type") or "—")
            c[3].write(q.get("strand_name") or "—")
            c[4].write(q.get("cognitive_level") or "—")
            c[5].write(q.get("difficulty") or "—")
            c[6].write(f"{q.get('source_name') or '—'} · {q.get('year') or ''}")
            with c[1]:
                with st.popover("Xem chi tiết"):
                    st.markdown("**Nội dung:**")
                    st.write(q["question_text"])
                    for j, o in enumerate(q.get("options") or []):
                        st.write(f"{chr(65+j)}. {o}")
                    st.markdown(f"**Đáp án:** {q.get('answer') or '—'}")
                    if q.get("solution"):
                        st.markdown("**Lời giải:**")
                        st.write(q["solution"])
                    st.markdown("**Taxonomy:**")
                    st.write(f"- Mạch: {q.get('strand_name') or '—'}")
                    st.write(f"- Nội dung: {q.get('content_name') or '—'}")
                    st.write(f"- ĐVKT: {q.get('unit_name') or '—'}")
                    st.write(f"- YCCĐ: {fmt_short(q.get('outcome_name') or '—', 160)}")
                    st.markdown(f"**Căn cứ phân loại:** {q.get('classification_basis') or '—'}")
                    st.markdown(f"**Độ tin cậy:** {q.get('classification_confidence', 0):.0%}")
                    st.markdown(f"**Nguồn:** {q.get('source_name') or '—'} ({q.get('organization') or '—'}, {q.get('year') or '—'})")

        st.divider()
        sel = st.session_state.selected_qids
        c1, c2, c3 = st.columns(3)
        c1.write(f"**Đã chọn: {len(sel)} câu**")
        if c2.button("🗑 Bỏ chọn tất cả"):
            st.session_state.selected_qids.clear()
            st.rerun()
        if c3.button("📤 Xuất JSON các câu đã chọn"):
            sel_qs = [svc.get_question(i) for i in sel if svc.get_question(i)]
            if sel_qs:
                out_path = os.path.join(BASE, "data", "exports", "selected.json")
                exp.export_questions_json(sel_qs, out_path)
                with open(out_path, "rb") as f:
                    st.download_button("⬇️ Tải JSON", data=f.read(), file_name="ngan_hang_chon.json", mime="application/json")
                    st.success("Đã xuất JSON")
            else:
                st.warning("Chưa chọn câu nào.")

# ============================== TẠO ĐỀ ==============================
elif page == "📝 Tạo đề":
    st.title("📝 Tạo đề Word")
    st.caption("Xuất các câu đã chọn thành file .docx (đề thi, ngân hàng, đáp án, câu hỏi+lời giải)")

    sel = st.session_state.selected_qids
    sel_qs = [svc.get_question(i) for i in sel if svc.get_question(i)]

    if not sel_qs:
        st.info("Chưa có câu nào được chọn. Vào **Ngân hàng câu hỏi** tick các câu cần xuất.")
    else:
        st.success(f"Đã chọn **{len(sel_qs)} câu**")
        # Xem nhanh danh sách đang chọn
        with st.expander("Danh sách câu đã chọn", expanded=False):
            for q in sel_qs:
                st.write(f"- Q{q['id']}: {fmt_short(q['question_text'], 90)}")

        st.divider()
        mode = st.radio("Chế độ xuất", ["📄 Đề thi", "🗂 Ngân hàng câu hỏi", "✅ Chỉ đáp án", "📖 Câu hỏi + lời giải"])
        with st.form("export_opts"):
            if mode == "📄 Đề thi":
                exam_name = st.text_input("Tên đề", value="ĐỀ THI VẬT LÍ – TN THPT")
                subject = st.text_input("Môn", value="Vật lí")
                duration = st.text_input("Thời gian", value="50 phút")
                c1, c2, c3 = st.columns(3)
                with_a = c1.checkbox("Kèm đáp án cuối", value=True)
                with_s = c2.checkbox("Kèm lời giải", value=False)
                with_t = c3.checkbox("Kèm taxonomy", value=False)
                shuffle = st.checkbox("Xáo trộn thứ tự câu", value=False)
            elif mode == "🗂 Ngân hàng câu hỏi":
                with_a = st.checkbox("Kèm đáp án", value=True)
                with_s = st.checkbox("Kèm lời giải", value=False)
                with_t = st.checkbox("Kèm taxonomy", value=True)
                shuffle = False
                exam_name, subject, duration = "", "", ""
            elif mode == "✅ Chỉ đáp án":
                exam_name = st.text_input("Tên đề (cho tiêu đề)", value="ĐỀ THI VẬT LÍ")
                with_s = st.checkbox("Kèm hướng dẫn giải", value=True)
                with_a, with_t, shuffle = True, False, False
                subject, duration = "", ""
            else:  # Câu hỏi + lời giải
                exam_name = st.text_input("Tên đề", value="ĐỀ THI VẬT LÍ – CÂU HỎI VÀ LỜI GIẢI")
                with_s = True
                with_a = st.checkbox("Kèm đáp án ngắn", value=False)
                with_t = st.checkbox("Kèm taxonomy", value=False)
                shuffle = False
                subject, duration = "", ""
            submitted = st.form_submit_button("⚡ Xuất Word")

        if submitted:
            out_dir = os.path.join(BASE, "data", "exports")
            os.makedirs(out_dir, exist_ok=True)
            try:
                if mode == "📄 Đề thi":
                    out = os.path.join(out_dir, "de_thi.docx")
                    exp.export_exam(sel_qs, out, exam_name, subject, duration, with_a, with_s, with_t, shuffle)
                    label = "ĐỀ THI"
                elif mode == "🗂 Ngân hàng câu hỏi":
                    out = os.path.join(out_dir, "ngan_hang_cau_hoi.docx")
                    exp.export_bank(sel_qs, out, with_a, with_s, with_t)
                    label = "NGÂN HÀNG CÂU HỎI"
                elif mode == "✅ Chỉ đáp án":
                    out = os.path.join(out_dir, "dap_an.docx")
                    exp.export_answers(sel_qs, out, exam_name, with_s)
                    label = "ĐÁP ÁN"
                else:
                    out = os.path.join(out_dir, "cau_hoi_loi_giai.docx")
                    exp.export_exam(sel_qs, out, exam_name, "Vật lí", "", with_a, True, with_t, False)
                    label = "CÂU HỎI + LỜI GIẢI"
                with open(out, "rb") as f:
                    st.download_button(f"⬇️ Tải {label} (.docx)", data=f.read(),
                                       file_name=f"{label.replace(' ', '_').lower()}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                st.success(f"Đã tạo file: {out}")
            except Exception as e:
                st.error(f"Lỗi xuất Word: {e}")

# ============================== THỐNG KÊ ==============================
elif page == "📈 Thống kê":
    st.title("📈 Thống kê ngân hàng")
    stats = svc.stats_overview()
    st.metric("Tổng câu", stats["total"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Đã duyệt", stats["reviewed"])
    c2.metric("Trùng Mức 1", stats["dups"])
    c3.metric("Cần thẩm định", stats["need_review"])
    c4.metric("Tỷ lệ duyệt", f"{stats['reviewed']/max(stats['total'],1):.0%}")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Phân bố theo mạch nội dung")
        df = pd.DataFrame(stats["by_strand"])
        if not df.empty:
            st.bar_chart(df.set_index("name")["c"])
    with col2:
        st.subheader("Phân bố theo dạng câu")
        df = pd.DataFrame(stats["by_type"])
        if not df.empty:
            st.bar_chart(df.set_index("name")["c"])
    st.subheader("Phân bố theo mức độ")
    df = pd.DataFrame(stats["by_level"])
    if not df.empty:
        st.bar_chart(df.set_index("name")["c"])

st.sidebar.markdown("---")
st.sidebar.caption("Dữ liệu: SQLite (data/bank.db)")