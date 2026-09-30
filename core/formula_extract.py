# -*- coding: utf-8 -*-
"""
Xử lý công thức MathType / OLE / ảnh minh họa trong DOCX (dùng lxml qua python-docx).

Vấn đề: đề Vật lí dùng MathType → công thức trong `w:object` (OLE) + ảnh WMF.
python-docx bỏ qua w:object → công thức mất khỏi text.

Giải pháp (free, local):
  1) Duyệt cây XML (python-docx/lxml) — mỗi w:object → text `[[FORMULA:n]]`,
     mỗi w:drawing (ảnh png/jpg) → `[[IMG:n]]`; blob ảnh giải nén vào out_dir.
  2) Word COM (máy có Word) CopyAsPicture từng OLE → doc tạm → PDF →
     pypdfium2 render từng trang → PIL auto-crop → PNG sắc nét.
  3) Parser/UI/Exporter đọc placeholder + path ảnh để hiển thị/chèn.
Cache theo hash path file (không render lại nếu đã có file + stamp).
"""
import os
import re
import tempfile
import shutil
import hashlib

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

_win32 = None
try:
    import win32com.client
    _win32 = True
except Exception:
    _win32 = False

FORMULA_RE = re.compile(r"\[\[FORMULA:(\d+)\]\]")
IMG_RE = re.compile(r"\[\[IMG:(\d+)\]\]")


def _dir_for(src_path):
    h = hashlib.md5(os.path.abspath(src_path).encode("utf-8")).hexdigest()[:10]
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "formulas")
    d = os.path.join(base, h)
    os.makedirs(d, exist_ok=True)
    return d


def _rels_of(doc):
    return doc.part.rels


def _replace_with_text(el, text):
    """
    Thay element (w:object/w:drawing) bằng run text.
    Đặt run mới ĐÚNG CẤP W:P (không lồng trong w:r cũ) để python-docx đọc được.
    """
    parent = el.getparent()
    new_r = OxmlElement("w:r")
    new_t = OxmlElement("w:t")
    new_t.text = text
    new_t.set(qn("xml:space"), "preserve")
    new_r.append(new_t)

    # đi lên tới con trực tiếp của w:p
    target = el
    while target.getparent() is not None and target.getparent().tag != qn("w:p"):
        target = target.getparent()
    target.addprevious(new_r)

    # xóa chuỗi object cũ (cha w:r/pict còn lại trống thì xóa luôn)
    chain = el
    while chain.getparent() is not None and chain.getparent().tag != qn("w:p"):
        chain = chain.getparent()
    p = chain.getparent()
    if p is not None:
        p.remove(chain)
    elif parent is not None:
        parent.remove(el)


def extract_asset_placeholders(src_path, out_dir):
    """
    Bước 1: thay w:object → [[FORMULA:n]], w:drawing (ảnh rast) → [[IMG:n]].
    Trả (count_formula, images {n: path}). Lưu docx đã xử lý vào out_dir/_prepared.docx.
    """
    os.makedirs(out_dir, exist_ok=True)
    doc = Document(src_path)
    rels = _rels_of(doc)
    body = doc.element.body

    counter = {"f": 0, "i": 0}
    images = {}

    # --- w:object (MathType / OLE) ---
    for obj in list(body.iter(qn("w:object"))):
        # tìm v:imagedata để lấy rId (ưu tiên r:id, fallback o:relid)
        rid = None
        for el in obj.iter():
            tag = el.tag
            if tag.endswith("}imagedata"):
                rid = el.get(qn("r:id")) or el.get(
                    "{urn:schemas-microsoft-com:office:office}relid") or el.get("o:relid")
                break
        if not rid or rid not in rels:
            continue
        n = counter["f"]
        counter["f"] += 1
        _replace_with_text(obj, f"[[FORMULA:{n}]]")

    # --- w:drawing với blip ảnh (png/jpg) ---
    for draw in list(body.iter(qn("w:drawing"))):
        rid = None
        for el in draw.iter():
            if el.tag == qn("a:blip"):
                rid = el.get(qn("r:embed"))
                break
        if not rid or rid not in rels:
            continue
        target = getattr(rels[rid], "target_ref", "") or ""
        ext = os.path.splitext(target)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg", ".gif"):
            continue
        try:
            blob = rels[rid].target_part.blob
        except Exception:
            continue
        n = counter["i"]
        counter["i"] += 1
        fp = os.path.join(out_dir, f"img_{n}{ext}")
        with open(fp, "wb") as f:
            f.write(blob)
        images[n] = fp
        _replace_with_text(draw, f"[[IMG:{n}]]")

    # lưu docx với placeholder (giữ nguyên phần còn lại)
    prepared = os.path.join(out_dir, "_prepared.docx")
    doc.save(prepared)
    return counter["f"], images, prepared


def _autocrop(pil_img, margin=4, threshold=245):
    from PIL import Image
    gray = pil_img.convert("L")
    mask = gray.point(lambda p: 255 if p < threshold else 0)
    bbox = mask.getbbox()
    if not bbox:
        return pil_img
    w, h = pil_img.size
    l, t, r, b = bbox
    l = max(0, l - margin); t = max(0, t - margin)
    r = min(w, r + margin); b = min(h, b + margin)
    return pil_img.crop((l, t, r, b))


def render_formulas_via_word(src_path, count, out_dir):
    """
    Bước 2: Word COM render count công thức OLE -> PNG (cache theo stamp).
    Trả {n: png_path}.
    """
    if count <= 0:
        return {}
    stamp = os.path.join(out_dir, ".rendered_ok")
    cached = all(os.path.exists(os.path.join(out_dir, f"formula_{i}.png"))
                 for i in range(count)) and os.path.exists(stamp)
    if cached:
        return {i: os.path.join(out_dir, f"formula_{i}.png") for i in range(count)}

    if not _win32:
        raise RuntimeError("pywin32 chưa cài (pip install pywin32) — cần Word COM để render MathType")
    tmp_dir = tempfile.mkdtemp(prefix="oleconv_")
    results = {}
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        try:
            doc = word.Documents.Open(os.path.abspath(src_path), ReadOnly=True)
            shapes = list(doc.InlineShapes)
            ole = []
            for s in shapes:
                try:
                    if s.Type == 1:  # wdInlineShapeEmbeddedOLEObject
                        ole.append(s)
                except Exception:
                    pass
            n_target = min(count, len(ole))
            tmp_doc = word.Documents.Add()
            for s in ole[:count]:
                try:
                    s.Range.CopyAsPicture()
                    rng = tmp_doc.Content
                    rng.Collapse(0)
                    rng.Paste()
                    rng.InsertAfter("\r")
                    rng.InsertBreak(7)  # wdPageBreak — mỗi công thức 1 trang để crop đúng
                except Exception:
                    continue
            pdf = os.path.join(tmp_dir, "out.pdf")
            try:
                tmp_doc.ExportAsFixedFormat(os.path.abspath(pdf), 17)
            except Exception:
                tmp_doc.SaveAs2(os.path.abspath(pdf), FileFormat=17)
            tmp_doc.Close(False)
            if not os.path.exists(pdf):
                raise RuntimeError("Word không export được PDF")

            import pypdfium2 as pdfium
            pd = pdfium.PdfDocument(pdf)
            formula_i = 0
            for page_i in range(len(pd)):
                if formula_i >= count:
                    break
                im = pd[page_i].render(scale=3.0).to_pil().convert("RGB")
                im = _autocrop(im)
                if im.size[0] < 20 or im.size[1] < 20:
                    continue
                fp = os.path.join(out_dir, f"formula_{formula_i}.png")
                im.save(fp)
                results[formula_i] = fp
                formula_i += 1
            pd.close()
            with open(stamp, "w") as f:
                f.write(str(formula_i))
            print(f"[formula] render {len(results)}/{count} PNG")
        finally:
            word.Quit()
        return results
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def prepare_exam_assets(src_path):
    """
    API tổng cho parser:
      (text_docx_path, formulas {n:path}, images {n:path})
    """
    out_dir = _dir_for(src_path)
    # xóa cache hỏng (stamp thiếu)
    if os.path.exists(os.path.join(out_dir, "_prepared.docx")):
        os.remove(os.path.join(out_dir, "_prepared.docx"))
    f_count, images, prepared = extract_asset_placeholders(src_path, out_dir)
    formulas = {}
    if f_count:
        try:
            formulas = render_formulas_via_word(src_path, f_count, out_dir)
        except Exception as e:
            print(f"WARN render formulas: {e}")
    # nếu render thiếu → đánh dấu UNCONVERTED để UI hiển thị thông báo
    for i in range(f_count):
        formulas.setdefault(i, "UNCONVERTED")
    return prepared, formulas, images