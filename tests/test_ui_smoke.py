# -*- coding: utf-8 -*-
"""Smoke test UI: render từng trang qua streamlit.testing AppTest."""
import os, sys, traceback

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from streamlit.testing.v1 import AppTest

PAGES = [
    "📊 Dashboard",
    "📚 Nguồn chuẩn",
    "🌳 Taxonomy",
    "📥 Nạp đề",
    "✅ Thẩm định",
    "🗄️ Ngân hàng câu hỏi",
    "📝 Tạo đề",
    "📈 Thống kê",
]

ok = True
for page in PAGES:
    try:
        at = AppTest.from_file(os.path.join(BASE, "app.py"), default_timeout=30)
        at.run()
        # chọn radio để chuyển trang
        radios = at.sidebar.radio
        for r in radios:
            if r.label == "Điều hướng":
                r.set_value(page)
        at.run()
        errors = [e.value for e in at.error]
        if errors:
            ok = False
            print(f"[FAIL] {page}: {errors[:2]}")
        else:
            print(f"[OK  ] {page}")
    except Exception as e:
        ok = False
        print(f"[FAIL] {page}: {type(e).__name__}: {e}")
        traceback.print_exc(limit=2)

print("\nUI SMOKE:", "ALL PASS" if ok else "HAS FAILURES")
sys.exit(0 if ok else 1)