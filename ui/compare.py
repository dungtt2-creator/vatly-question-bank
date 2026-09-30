# -*- coding: utf-8 -*-
"""
Màn hình so sánh câu trùng theo §11 đặc tả.
Cho phép xem song song câu mới | câu đã có, highlight phần giống nhau,
hiển thị % tương đồng, loại, ID liên quan, nguồn, đáp án, taxonomy.
"""
import difflib
import streamlit as st

from core import service as svc
from core import duplicate as dup


def highlight_diff(a, b):
    """
    Trả về 2 chuỗi HTML: a_html, b_html — các đoạn giống nhau bọc <mark>, khác nhau để trần.
    Dùng SequenceMatcher ở dạng char-level cho highlight chính xác.
    """
    na = dup.normalize_text(a)
    nb = dup.normalize_text(b)
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out_a, out_b = [], []
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            out_a.append(f"<mark>{a[i1:i2]}</mark>")
            out_b.append(f"<mark>{b[j1:j2]}</mark>")
        elif op == "replace":
            out_a.append(a[i1:i2])
            out_b.append(b[j1:j2])
        elif op == "delete":
            out_a.append(a[i1:i2])
        elif op == "insert":
            out_b.append(b[j1:j2])
    return "".join(out_a), "".join(out_b)


def render_compare_screen(new_q, bank_q, cmp):
    """
    Hiển thị so sánh song song.
    new_q: dict câu mới (chưa lưu hoặc vừa nạp)
    bank_q: dict câu đã có
    cmp: kết quả dup.compare_questions(new_q, bank_q)
    """
    st.markdown("### ⚖️ So sánh song song: Câu mới | Câu đã có")

    c1, c2 = st.columns(2)
    a_html, b_html = highlight_diff(
        new_q.get("question_text", ""),
        bank_q.get("question_text", ""),
    )

    with c1:
        st.markdown("**🆕 Câu mới**")
        st.markdown(f"<div style='background:#f7f7f7;padding:8px;border-radius:6px;'>{a_html}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"**📦 Câu đã có (Q{bank_q.get('id')})**")
        st.markdown(f"<div style='background:#f7f7f7;padding:8px;border-radius:6px;'>{b_html}</div>", unsafe_allow_html=True)

    st.divider()

    # Thông tin tương đồng
    level_color = {
        "Mức 1 – Trùng 100%": "red",
        "Mức 2 – Gần trùng": "orange",
        "Mức 3 – Tương đồng": "blue",
        "Mức 4 – Không trùng": "green",
    }
    color = level_color.get(cmp["level"], "gray")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Loại tương đồng:** <span style='color:{color};font-weight:bold'>{cmp['level']}</span>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"**% tương đồng:** {cmp['score']:.0%}")
    with c3:
        st.markdown(f"**Nội dung:** {cmp['text_score']:.0%} | **Phương án:** {cmp['opt_score']:.0%}")

    # Metadata cả 2 câu
    with st.expander("Chi tiết nguồn / đáp án / taxonomy", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Câu mới**")
            st.write(f"- Nguồn: {new_q.get('source_name') or new_q.get('exam_name') or '—'} ({new_q.get('year') or ''})")
            st.write(f"- Đáp án: {new_q.get('answer') or '—'}")
            st.write(f"- Dạng: {new_q.get('question_type') or '—'}")
            st.write(f"- Taxonomy: {new_q.get('strand_name') or '—'} / {new_q.get('unit_name') or '—'}")
        with c2:
            st.markdown(f"**Câu đã có (Q{bank_q.get('id')})**")
            st.write(f"- Nguồn: {bank_q.get('source_name') or bank_q.get('exam_name') or '—'} ({bank_q.get('year') or ''})")
            st.write(f"- Đáp án: {bank_q.get('answer') or '—'}")
            st.write(f"- Dạng: {bank_q.get('question_type') or '—'}")
            st.write(f"- Taxonomy: {bank_q.get('strand_name') or '—'} / {bank_q.get('unit_name') or '—'}")

    # Nút quyết định
    st.markdown("**Quyết định:**")
    b1, b2, b3, b4 = st.columns(4)
    if b1.button("🛑 Xác nhận trùng 100%", key=f"c_dup_{new_q.get('id', 'new')}_{bank_q.get('id')}"):
        svc.review_question(new_q["id"], "Trùng 100%", st.session_state.get("reviewer", ""),
                            f"Trùng với Q{bank_q.get('id')} ({cmp['score']:.0%})")
        svc.update_question(new_q["id"], duplicate_status="Mức 1 – Trùng 100%", similarity_score=cmp["score"],
                            related_question_ids=[bank_q.get("id")])
        st.success("Đã xác nhận trùng 100%. Câu không vào ngân hàng.")
        st.rerun()
    if b2.button("⚠️ Gần trùng", key=f"c_near_{new_q.get('id', 'new')}"):
        svc.review_question(new_q["id"], "Gần trùng", st.session_state.get("reviewer", ""),
                            f"Gần trùng với Q{bank_q.get('id')} ({cmp['score']:.0%})")
        svc.update_question(new_q["id"], duplicate_status="Mức 2 – Gần trùng", similarity_score=cmp["score"],
                            related_question_ids=[bank_q.get("id")])
        st.success("Đã đánh dấu Gần trùng — cần thẩm định.")
        st.rerun()
    if b3.button("✅ Không trùng", key=f"c_not_{new_q.get('id', 'new')}"):
        svc.review_question(new_q["id"], "Cần thẩm định", st.session_state.get("reviewer", ""),
                            f"Đã kiểm tra với Q{bank_q.get('id')} — không trùng.")
        svc.update_question(new_q["id"], duplicate_status="Mức 4 – Không trùng", similarity_score=cmp["score"])
        st.success("Đã xác nhận không trùng — chuyển sang thẩm định bình thường.")
        st.rerun()
    if b4.button("❓ Cần thẩm định", key=f"c_need_{new_q.get('id', 'new')}"):
        svc.review_question(new_q["id"], "Cần thẩm định", st.session_state.get("reviewer", ""))
        st.success("Đã chuyển sang Cần thẩm định.")
        st.rerun()