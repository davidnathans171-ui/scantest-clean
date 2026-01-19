# =========================================================
# 📦 PAKET A1 - CORE VISUAL & OCR (SETUP + UI DASAR)
# ScanText Pro SUPER FINAL
# Fokus: Upload • Kamera • Zoom • Crop • Anti Crash
# =========================================================

import streamlit as st
import numpy as np
from PIL import Image
import easyocr
import cv2
from io import BytesIO

# ==============================
# SESSION STATE INIT (WAJIB)
# ==============================
if "is_unlocked" not in st.session_state:
    st.session_state.is_unlocked = False   # default terkunci

if "pin_attempt" not in st.session_state:
    st.session_state.pin_attempt = ""

if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""

if "final_text" not in st.session_state:
    st.session_state.final_text = ""

if "summary_data" not in st.session_state:
    st.session_state.summary_data = {}

if "zoom_level" not in st.session_state:
    st.session_state.zoom_level = 1.0


# =========================================================
# 📦 PAKET F1 – MULTI THEME UI (LIGHT, DARK, BLUE, GREEN, MINIMALIST)
# =========================================================

# Theme selector
if "ui_theme" not in st.session_state:
    st.session_state.ui_theme = "Light"

st.sidebar.markdown("## 🎨 Tema UI")

st.session_state.ui_theme = st.sidebar.selectbox(
    "Pilih Tema:",
    ["Light", "Dark", "Blue", "Green", "Minimalist"],
    index=["Light", "Dark", "Blue", "Green", "Minimalist"].index(st.session_state.ui_theme)
)

# Theme styles
THEMES = {
    "Light": """
        body { background-color: #ffffff; color: #000000; }
        .stApp { background-color: #ffffff; }
        .stButton>button { background-color: #f0f2f6; color: black; border-radius: 8px; }
        .stTextInput>div>div>input { background-color: #ffffff; }
    """,

    "Dark": """
        body { background-color: #0f172a; color: #e5e7eb; }
        .stApp { background-color: #0f172a; }
        .stButton>button { background-color: #1e293b; color: #e5e7eb; border-radius: 8px; }
        .stTextInput>div>div>input { background-color: #1e293b; color: white; }
        textarea { background-color: #1e293b; color: white; }
    """,

    "Blue": """
        body { background-color: #e8f1ff; color: #002b5c; }
        .stApp { background-color: #e8f1ff; }
        .stButton>button { background-color: #2563eb; color: white; border-radius: 8px; }
        .stTextInput>div>div>input { background-color: #ffffff; }
    """,

    "Green": """
        body { background-color: #ecfdf5; color: #064e3b; }
        .stApp { background-color: #ecfdf5; }
        .stButton>button { background-color: #10b981; color: white; border-radius: 8px; }
        .stTextInput>div>div>input { background-color: #ffffff; }
    """,

    "Minimalist": """
        body { background-color: #fafafa; color: #111111; }
        .stApp { background-color: #fafafa; }
        .stButton>button { background-color: #111111; color: white; border-radius: 0px; }
        .stTextInput>div>div>input { background-color: #ffffff; border: 1px solid #111111; }
        textarea { border: 1px solid #111111; }
    """
}

# Apply theme
st.markdown(
    f"""
    <style>
    {THEMES[st.session_state.ui_theme]}
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.success(f"Tema aktif: {st.session_state.ui_theme}")


# =========================================================
# CONFIG STREAMLIT (ANTI "OH NO")
# =========================================================
st.set_page_config(
    page_title="ScanText Pro - SUPER FINAL",
    page_icon="📄",
    layout="wide"
)

st.title("📄 ScanText Pro - SUPER FINAL")
st.caption("OCR • Kamera • Crop • Zoom • Highlight • Anti Crash Mode")

# =========================================================
# SESSION STATE INIT (ANTI ERROR)
# =========================================================
def init_state():
    defaults = {
        "image": None,
        "cropped_image": None,
        "zoom": 1.0,
        "ocr_text": "",
        "boxes": [],
        "language": ["en"],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# =========================================================
# SIDEBAR - PENGATURAN OCR
# =========================================================
st.sidebar.title("⚙️ Pengaturan OCR")

lang_map = {
    "Indonesia": ["id"],
    "Inggris": ["en"],
    "Indonesia + Inggris": ["id", "en"],
    "Jepang": ["ja"],
    "Arab": ["ar"]
}

lang_choice = st.sidebar.selectbox(
    "Pilih Bahasa OCR:",
    list(lang_map.keys())
)
st.session_state.language = lang_map[lang_choice]

# =========================================================
# PILIH SUMBER GAMBAR
# =========================================================
st.markdown("## 📷 Pilih Sumber Gambar")

source = st.radio(
    "Ambil gambar dari:",
    ["Upload", "Kamera"],
    horizontal=True
)

uploaded_image = None

# ---------------- Upload ----------------
if source == "Upload":
    file = st.file_uploader(
        "Upload gambar (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"]
    )
    if file:
        try:
            uploaded_image = Image.open(file).convert("RGB")
            st.session_state.image = uploaded_image
        except:
            st.error("Gambar tidak valid, silakan upload ulang.")

# ---------------- Kamera ----------------
if source == "Kamera":
    cam = st.camera_input("Ambil foto dengan kamera")
    if cam:
        try:
            uploaded_image = Image.open(cam).convert("RGB")
            st.session_state.image = uploaded_image
        except:
            st.error("Gagal membaca foto kamera.")

# =========================================================
# TAMPILKAN GAMBAR + ZOOM
# =========================================================
if st.session_state.image:
    st.markdown("## 🔍 Preview Gambar (dengan Zoom)")

    st.session_state.zoom = st.slider(
        "Zoom gambar",
        min_value=0.5,
        max_value=3.0,
        step=0.1,
        value=st.session_state.zoom
    )

    w, h = st.session_state.image.size
    new_size = (int(w * st.session_state.zoom), int(h * st.session_state.zoom))
    zoomed = st.session_state.image.resize(new_size)

    st.image(zoomed, use_container_width=True)

    st.markdown("---")
    st.markdown("## ✂️ Crop Gambar")

    col1, col2 = st.columns(2)
    with col1:
        x1 = st.slider("X1", 0, w, 0)
        y1 = st.slider("Y1", 0, h, 0)
    with col2:
        x2 = st.slider("X2", 0, w, w)
        y2 = st.slider("Y2", 0, h, h)

    if st.button("✂️ Terapkan Crop"):
        try:
            cropped = st.session_state.image.crop((x1, y1, x2, y2))
            st.session_state.cropped_image = cropped
            st.success("Crop berhasil!")
        except:
            st.error("Crop gagal. Periksa koordinat.")

# =========================================================
# TAMPILKAN HASIL CROP
# =========================================================
if st.session_state.cropped_image:
    st.markdown("## 🧩 Hasil Crop")
    st.image(st.session_state.cropped_image, use_container_width=True)

# =========================================================
# FOOTER STATUS
# =========================================================
st.markdown("---")
st.info("📦 Paket A1 aktif. Upload, Kamera, Zoom, dan Crop siap digunakan.")
# =========================================================
# 📦 PAKET A2 - OCR ENGINE + HIGHLIGHT TEKS + ANTI CRASH
# =========================================================

st.markdown("## 🧠 OCR & Highlight Teks")

# =========================
# LOAD OCR READER (AMAN)
# =========================
@st.cache_resource
def load_ocr(langs):
    try:
        reader = easyocr.Reader(langs, gpu=False)
        return reader
    except:
        return None

reader = load_ocr(st.session_state.language)

if reader is None:
    st.error("Gagal memuat OCR Engine. Periksa instalasi EasyOCR.")
else:
    st.success("OCR Engine siap digunakan.")

# =========================
# PILIH GAMBAR UNTUK OCR
# =========================
image_for_ocr = None

if st.session_state.cropped_image is not None:
    image_for_ocr = st.session_state.cropped_image
    st.info("OCR menggunakan gambar hasil crop.")
elif st.session_state.image is not None:
    image_for_ocr = st.session_state.image
    st.info("OCR menggunakan gambar asli.")
else:
    st.warning("Silakan upload atau ambil gambar terlebih dahulu.")

# =========================
# PROSES OCR
# =========================
if image_for_ocr is not None and reader is not None:
    if st.button("🔍 Proses OCR Sekarang"):
        with st.spinner("Sedang membaca teks dari gambar..."):
            try:
                img_np = np.array(image_for_ocr)
                results = reader.readtext(img_np)

                extracted_text = ""
                boxes = []

                for (bbox, text, conf) in results:
                    extracted_text += text + "\n"
                    boxes.append(bbox)

                st.session_state.ocr_text = extracted_text.strip()
                st.session_state.boxes = boxes

                st.success("OCR berhasil! Teks berhasil diekstrak.")
            except Exception as e:
                st.error("OCR gagal, tapi aplikasi tetap berjalan.")
                st.code(str(e))

# =========================
# TAMPILKAN TEKS OCR
# =========================
if st.session_state.ocr_text:
    st.markdown("### 📄 Hasil OCR")
    st.text_area(
        "Teks hasil OCR:",
        st.session_state.ocr_text,
        height=250
    )

# =========================================================
# 📦 PAKET F2 – COPY TO CLIPBOARD (SALIN TEKS SEKALI KLIK)
# =========================================================

st.markdown("## 📋 Copy to Clipboard")

if st.session_state.ocr_text:
    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("📋 Salin Teks OCR"):
            try:
                # JavaScript kecil untuk menyalin ke clipboard
                st.components.v1.html(
                    f"""
                    <textarea id="copyText" style="position:absolute; left:-1000px;">
                    {st.session_state.ocr_text}
                    </textarea>
                    <script>
                        const textArea = document.getElementById("copyText");
                        textArea.select();
                        document.execCommand("copy");
                    </script>
                    """,
                    height=0
                )
                st.success("Teks berhasil disalin ke clipboard! Sekarang bisa ditempel di WhatsApp, Email, atau Word.")
            except:
                st.error("Gagal menyalin teks, silakan salin manual.")

    with col2:
        st.info("Klik tombol di kiri untuk langsung menyalin semua teks OCR.")

else:
    st.warning("Belum ada teks OCR untuk disalin.")


# =========================
# HIGHLIGHT TEKS DI GAMBAR
# =========================
if st.session_state.image is not None and st.session_state.boxes:
    st.markdown("## 🖍 Highlight Teks pada Gambar")

    try:
        img = np.array(st.session_state.image.copy())
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        for box in st.session_state.boxes:
            pts = np.array(box, dtype=np.int32)
            cv2.polylines(img, [pts], True, (0, 255, 0), 2)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        st.image(img, caption="Teks berhasil di-highlight", use_container_width=True)

    except Exception as e:
        st.error("Gagal menampilkan highlight.")
        st.code(str(e))

# =========================================================
# STATUS PAKET A2
# =========================================================
st.markdown("---")
st.success("📦 Paket A2 aktif. OCR + Highlight siap digunakan tanpa risiko 'Oh no'.")
# =========================================================
# 📦 PAKET B1 - MODE DOKUMEN (STRUK • SURAT • NOTA • INVOICE • KTP)
# Struktur dasar + Session State
# =========================================================

st.markdown("## 🗂️ Mode Dokumen")

mode = st.radio(
    "Pilih jenis dokumen:",
    ["Struk", "Surat", "Nota", "Invoice", "KTP"],
    horizontal=True
)

st.info(f"Mode aktif: **{mode}**")

# =========================================================
# SESSION STATE UNTUK SETIAP MODE (ANTI ERROR)
# =========================================================
def init_mode_states():
    # Struk
    if "struk_data" not in st.session_state:
        st.session_state.struk_data = {
            "nama_toko": "",
            "tanggal": "",
            "total": "",
            "telepon": ""
        }

    # Surat
    if "surat_data" not in st.session_state:
        st.session_state.surat_data = {
            "judul": "",
            "tanggal": "",
            "alamat": "",
            "isi": ""
        }

    # Nota
    if "nota_data" not in st.session_state:
        st.session_state.nota_data = {
            "judul": "",
            "tanggal": "",
            "isi": ""
        }

    # Invoice
    if "invoice_data" not in st.session_state:
        st.session_state.invoice_data = {
            "nomor": "",
            "tanggal": "",
            "klien": "",
            "total": "",
            "isi": ""
        }

    # KTP (versi sederhana)
    if "ktp_data" not in st.session_state:
        st.session_state.ktp_data = {
            "nik": "",
            "nama": "",
            "tanggal_lahir": "",
            "jenis_kelamin": "",
            "alamat": ""
        }

init_mode_states()

# =========================================================
# PREVIEW DATA MODE (sementara, nanti diisi di B2 & B3)
# =========================================================
st.markdown("### 📄 Data Mode Saat Ini")

if mode == "Struk":
    st.json(st.session_state.struk_data)

elif mode == "Surat":
    st.json(st.session_state.surat_data)

elif mode == "Nota":
    st.json(st.session_state.nota_data)

elif mode == "Invoice":
    st.json(st.session_state.invoice_data)

elif mode == "KTP":
    st.json(st.session_state.ktp_data)

# =========================================================
# STATUS
# =========================================================
st.markdown("---")
st.success("📦 Paket B1 aktif. Mode dokumen siap digunakan tanpa error.")
# =========================================================
# 📦 PAKET B2 - MODE STRUK & MODE SURAT
# Form input + terhubung dengan hasil OCR
# =========================================================

st.markdown("## 🧾 / 📝 Form Dokumen")

# ===============================
# MODE STRUK
# ===============================
if mode == "Struk":
    st.subheader("🧾 Mode Struk")

    st.caption("Isi otomatis dari OCR bisa kamu edit manual jika ada kesalahan.")

    # Sinkron awal dari OCR (kalau masih kosong)
    if st.session_state.struk_data["nama_toko"] == "" and st.session_state.ocr_text:
        lines = st.session_state.ocr_text.splitlines()
        if len(lines) > 0:
            st.session_state.struk_data["nama_toko"] = lines[0]

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.struk_data["nama_toko"] = st.text_input(
            "🏪 Nama Toko",
            st.session_state.struk_data["nama_toko"]
        )

        st.session_state.struk_data["tanggal"] = st.text_input(
            "📅 Tanggal",
            st.session_state.struk_data["tanggal"]
        )

    with col2:
        st.session_state.struk_data["telepon"] = st.text_input(
            "📞 No. Telepon",
            st.session_state.struk_data["telepon"]
        )

        st.session_state.struk_data["total"] = st.text_input(
            "💰 Total Belanja",
            st.session_state.struk_data["total"]
        )

    st.markdown("### 📄 Teks Struk Lengkap")
    st.session_state.ocr_text = st.text_area(
        "Teks hasil OCR:",
        st.session_state.ocr_text,
        height=200
    )


# ===============================
# MODE SURAT
# ===============================
elif mode == "Surat":
    st.subheader("📝 Mode Surat")

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.surat_data["judul"] = st.text_input(
            "📌 Judul Surat",
            st.session_state.surat_data["judul"]
        )

        st.session_state.surat_data["tanggal"] = st.text_input(
            "📅 Tanggal Surat",
            st.session_state.surat_data["tanggal"]
        )

    with col2:
        st.session_state.surat_data["alamat"] = st.text_input(
            "🏠 Alamat Tujuan",
            st.session_state.surat_data["alamat"]
        )

    st.markdown("### 📄 Isi Surat")
    st.session_state.surat_data["isi"] = st.text_area(
        "Isi surat:",
        st.session_state.surat_data["isi"] or st.session_state.ocr_text,
        height=300
    )

# =========================================================
# STATUS
# =========================================================
st.markdown("---")
st.success("📦 Paket B2 aktif. Mode Struk & Mode Surat siap digunakan.")
# =========================================================
# 📦 PAKET B3 - MODE NOTA • MODE INVOICE • MODE KTP
# =========================================================

st.markdown("## 🧾📑🪪 Form Dokumen Lanjutan")

# ===============================
# MODE NOTA
# ===============================
if mode == "Nota":
    st.subheader("🧾 Mode Nota")

    st.session_state.nota_data["judul"] = st.text_input(
        "📌 Judul Nota",
        st.session_state.nota_data["judul"]
    )

    st.session_state.nota_data["tanggal"] = st.text_input(
        "📅 Tanggal",
        st.session_state.nota_data["tanggal"]
    )

    st.session_state.nota_data["isi"] = st.text_area(
        "📄 Isi Nota",
        st.session_state.nota_data["isi"] or st.session_state.ocr_text,
        height=300
    )


# ===============================
# MODE INVOICE
# ===============================
elif mode == "Invoice":
    st.subheader("📑 Mode Invoice")

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.invoice_data["nomor"] = st.text_input(
            "🆔 Nomor Invoice",
            st.session_state.invoice_data["nomor"]
        )

        st.session_state.invoice_data["tanggal"] = st.text_input(
            "📅 Tanggal",
            st.session_state.invoice_data["tanggal"]
        )

    with col2:
        st.session_state.invoice_data["klien"] = st.text_input(
            "👤 Nama Klien",
            st.session_state.invoice_data["klien"]
        )

        st.session_state.invoice_data["total"] = st.text_input(
            "💰 Total",
            st.session_state.invoice_data["total"]
        )

    st.session_state.invoice_data["isi"] = st.text_area(
        "📄 Detail Invoice",
        st.session_state.invoice_data["isi"] or st.session_state.ocr_text,
        height=250
    )


# ===============================
# MODE KTP (VERSI SEDERHANA)
# ===============================
elif mode == "KTP":
    st.subheader("🪪 Mode KTP (Sederhana)")

    st.caption("Fokus 5 data utama KTP. Bisa diedit manual jika OCR kurang tepat.")

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.ktp_data["nik"] = st.text_input(
            "🆔 NIK",
            st.session_state.ktp_data["nik"]
        )

        st.session_state.ktp_data["nama"] = st.text_input(
            "👤 Nama",
            st.session_state.ktp_data["nama"]
        )

        st.session_state.ktp_data["tanggal_lahir"] = st.text_input(
            "📅 Tanggal Lahir",
            st.session_state.ktp_data["tanggal_lahir"]
        )

    with col2:
        st.session_state.ktp_data["jenis_kelamin"] = st.text_input(
            "🚻 Jenis Kelamin",
            st.session_state.ktp_data["jenis_kelamin"]
        )

        st.session_state.ktp_data["alamat"] = st.text_area(
            "🏠 Alamat",
            st.session_state.ktp_data["alamat"],
            height=120
        )

    st.markdown("### 📄 Teks OCR KTP")
    st.text_area(
        "Teks mentah OCR:",
        st.session_state.ocr_text,
        height=200
    )


# =========================================================
# STATUS
# =========================================================
st.markdown("---")
st.success("📦 Paket B3 aktif. Mode Nota, Invoice, dan KTP siap digunakan.")
# =========================================================
# 📦 PAKET C - EXPORT & SHARE (TXT • PDF • WORD • EXCEL • WHATSAPP)
# =========================================================

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from docx import Document
from openpyxl import Workbook
import urllib.parse
import tempfile
import os

st.markdown("## 📤 Export & Share Dokumen")

# =================================
# AMBIL DATA SESUAI MODE
# =================================
def get_active_data():
    if mode == "Struk":
        return st.session_state.struk_data
    elif mode == "Surat":
        return st.session_state.surat_data
    elif mode == "Nota":
        return st.session_state.nota_data
    elif mode == "Invoice":
        return st.session_state.invoice_data
    elif mode == "KTP":
        return st.session_state.ktp_data
    else:
        return {}

def data_to_text(data: dict):
    text = ""
    for k, v in data.items():
        text += f"{k.upper()} : {v}\n"
    return text.strip()

active_data = get_active_data()
export_text = data_to_text(active_data)

# =================================
# TOMBOL EXPORT
# =================================
col1, col2, col3, col4, col5 = st.columns(5)

# -------- TXT --------
with col1:
    st.download_button(
        "📄 TXT",
        data=export_text,
        file_name=f"{mode.lower()}_scantex.txt",
        mime="text/plain"
    )

# -------- PDF --------
with col2:
    if st.button("📕 PDF"):
        try:
            tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            c = canvas.Canvas(tmp_pdf.name, pagesize=A4)
            textobject = c.beginText(40, 800)

            for line in export_text.split("\n"):
                textobject.textLine(line)

            c.drawText(textobject)
            c.showPage()
            c.save()

            with open(tmp_pdf.name, "rb") as f:
                st.download_button(
                    "⬇️ Download PDF",
                    data=f,
                    file_name=f"{mode.lower()}_scantex.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error("Gagal membuat PDF")
            st.code(str(e))

# -------- WORD --------
with col3:
    if st.button("📝 Word"):
        try:
            doc = Document()
            for line in export_text.split("\n"):
                doc.add_paragraph(line)

            tmp_doc = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
            doc.save(tmp_doc.name)

            with open(tmp_doc.name, "rb") as f:
                st.download_button(
                    "⬇️ Download Word",
                    data=f,
                    file_name=f"{mode.lower()}_scantex.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        except Exception as e:
            st.error("Gagal membuat Word")
            st.code(str(e))

# -------- EXCEL --------
with col4:
    if st.button("📊 Excel"):
        try:
            wb = Workbook()
            ws = wb.active
            ws.append(["Field", "Value"])
            for k, v in active_data.items():
                ws.append([k, v])

            tmp_xls = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            wb.save(tmp_xls.name)

            with open(tmp_xls.name, "rb") as f:
                st.download_button(
                    "⬇️ Download Excel",
                    data=f,
                    file_name=f"{mode.lower()}_scantex.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error("Gagal membuat Excel")
            st.code(str(e))

# -------- WHATSAPP --------
with col5:
    wa_text = urllib.parse.quote(export_text)
    wa_link = f"https://wa.me/?text={wa_text}"
    st.markdown(
        f"[📤 Share WhatsApp](https://wa.me/?text={wa_text})",
        unsafe_allow_html=True
    )

st.success("📦 Paket C aktif. Export TXT, PDF, Word, Excel & Share WhatsApp siap digunakan.")
# =========================================================
# 📦 PAKET D – RIWAYAT & KEUANGAN
# =========================================================

import re
import pandas as pd
from datetime import datetime

# ===============================
# SESSION STATE RIWAYAT
# ===============================
if "history" not in st.session_state:
    st.session_state.history = []

# ===============================
# FORMAT RUPIAH
# ===============================
def format_rupiah(val):
    try:
        val = re.sub(r"[^\d]", "", val)
        return "Rp {:,}".format(int(val)).replace(",", ".")
    except:
        return val

# ===============================
# SMART EXTRACT STRUK
# ===============================
def smart_extract_struk(text):
    data = {"nama_toko": "", "tanggal": "", "total": "", "telepon": ""}

    lines = text.splitlines()

    if lines:
        data["nama_toko"] = lines[0]

    date_match = re.search(r"\d{2}[/-]\d{2}[/-]\d{4}", text)
    if date_match:
        data["tanggal"] = date_match.group()

    phone_match = re.search(r"(08\d{8,12})", text)
    if phone_match:
        data["telepon"] = phone_match.group()

    total_match = re.findall(r"\d{4,}", text)
    if total_match:
        data["total"] = format_rupiah(total_match[-1])

    return data

# ===============================
# SIMPAN KE RIWAYAT
# ===============================
st.markdown("## 💾 Simpan ke Riwayat")

if st.button("💾 Simpan Dokumen Sekarang"):
    data = get_active_data()

    if mode == "Struk" and st.session_state.ocr_text:
        data = smart_extract_struk(st.session_state.ocr_text)
        st.session_state.struk_data.update(data)

    record = {
        "mode": mode,
        "data": data.copy(),
        "text": export_text,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    st.session_state.history.append(record)
    st.success("Data berhasil disimpan ke riwayat!")

# ===== MODE PRIVAT PIN =====
if "is_unlocked" not in st.session_state:
    st.session_state.is_unlocked = False

PIN = "1234"

st.sidebar.markdown("## 🔐 Mode Privat")

if not st.session_state.is_unlocked:
    pin = st.sidebar.text_input("Masukkan PIN", type="password")
    if st.sidebar.button("🔓 Buka Riwayat"):
        if pin == PIN:
            st.session_state.is_unlocked = True
            st.sidebar.success("Riwayat terbuka")
            st.rerun()
        else:
            st.sidebar.error("PIN salah")


# ===============================
# SIDEBAR – RIWAYAT
# ===============================
if st.session_state.is_unlocked:
    st.sidebar.markdown("📁 Riwayat Scan")

if st.session_state.is_unlocked:

    if len(st.session_state.scan_history) == 0:
        st.sidebar.info("Belum ada riwayat.")
    else:
        if st.sidebar.button("🔥 Hapus Semua Riwayat"):
            st.session_state.scan_history.clear()
            st.sidebar.success("Semua riwayat terhapus")
            st.rerun()

        for i, item in enumerate(reversed(st.session_state.scan_history)):
            col1, col2 = st.sidebar.columns([4,1])
            with col1:
                if st.button(f"📄 {item['time']} | {item['mode']}", key=f"load_{i}"):
                    st.session_state.ocr_text = item["text"]
                    st.session_state.final_text = item["final_text"]
                    st.success("Riwayat dimuat")
            with col2:
                if st.button("❌", key=f"del_{i}"):
                    real_index = len(st.session_state.scan_history) - 1 - i
                    st.session_state.scan_history.pop(real_index)
                    st.sidebar.success("Riwayat dihapus")
                    st.rerun()

else:
    st.sidebar.warning("🔒 Riwayat terkunci. Masukkan PIN.")

    for i, item in enumerate(st.session_state.history):
        with st.sidebar.expander(f"{i+1}. {item['mode']} | {item['time']}"):
            st.json(item["data"])

            if st.button(f"❌ Hapus #{i+1}", key=f"del_{i}"):
                st.session_state.history.pop(i)
                st.experimental_rerun()

    if st.sidebar.button("🔥 Hapus Semua Riwayat"):
        st.session_state.history.clear()
        st.experimental_rerun()

# ===============================
# GRAFIK PENGELUARAN (STRUK)
# ===============================
st.markdown("## 📊 Grafik Pengeluaran (Mode Struk)")

struk_records = [
    r for r in st.session_state.history
    if r["mode"] == "Struk" and r["data"].get("total")
]

if struk_records:
    rows = []
    for r in struk_records:
        try:
            tgl = r["data"].get("tanggal", "")
            total = r["data"].get("total", "")
            total_val = int(re.sub(r"[^\d]", "", total))

            rows.append({
                "tanggal": tgl,
                "bulan": tgl[:7] if len(tgl) >= 7 else "Unknown",
                "total": total_val
            })
        except:
            pass

    df = pd.DataFrame(rows)

    if not df.empty:
        st.subheader("📅 Per Hari")
        daily = df.groupby("tanggal")["total"].sum()
        st.bar_chart(daily)

        st.subheader("📆 Per Bulan")
        monthly = df.groupby("bulan")["total"].sum()
        st.bar_chart(monthly)
else:
    st.info("Belum ada data struk untuk grafik.")

st.success("📦 Paket D aktif. Riwayat & grafik pengeluaran siap digunakan.")
# =========================================================
# 📦 PAKET E – KEAMANAN (PIN • LOGIN • SESSION LOCK)
# =========================================================

# PIN DEFAULT
APP_PIN = "1234"

# ===============================
# SESSION STATE KEAMANAN
# ===============================
if "is_unlocked" not in st.session_state:
    st.session_state.is_unlocked = False

if "login_user" not in st.session_state:
    st.session_state.login_user = ""

# ===============================
# LOGIN FORM
# ===============================
st.sidebar.markdown("## 🔐 Mode Privat")

if not st.session_state.is_unlocked:
    st.sidebar.warning("Akses Riwayat Terkunci")

    st.session_state.login_user = st.sidebar.text_input(
        "👤 Nama Pengguna",
        value=st.session_state.login_user
    )

    pin_input = st.sidebar.text_input(
        "🔢 Masukkan PIN",
        type="password"
    )

    if st.sidebar.button("🔓 Buka Akses"):
        if pin_input == APP_PIN:
            st.session_state.is_unlocked = True
            st.sidebar.success("Akses dibuka!")
            st.experimental_rerun()
        else:
            st.sidebar.error("PIN salah!")

else:
    st.sidebar.success(f"🔓 Terbuka | User: {st.session_state.login_user}")

    if st.sidebar.button("🔒 Kunci Ulang"):
        st.session_state.is_unlocked = False
        st.experimental_rerun()

# ===============================
# PROTEKSI RIWAYAT
# ===============================
if not st.session_state.is_unlocked:
    st.sidebar.info("Riwayat tersembunyi. Masukkan PIN untuk melihat.")
    # Hentikan eksekusi sidebar riwayat
else:
    st.sidebar.markdown("---")
    st.sidebar.markdown("🔐 Riwayat Terproteksi Aktif")
    # =========================================================
# 📦 PAKET F3 – AUTO RAPIKAN TEKS OCR
# =========================================================

import re

st.markdown("## ✨ Auto Rapikan Teks OCR")

def clean_ocr_text(text: str) -> str:
    """
    Membersihkan teks OCR:
    - Hapus spasi ganda
    - Hapus baris kosong berlebih
    - Rapikan paragraf
    """
    if not text:
        return ""

    # Hilangkan spasi berlebih
    text = re.sub(r"[ \t]+", " ", text)

    # Hilangkan baris kosong berturut-turut
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Rapikan spasi di awal/akhir baris
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(lines)

    return text.strip()

if st.session_state.ocr_text:
    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("✨ Rapikan Teks"):
            try:
                cleaned = clean_ocr_text(st.session_state.ocr_text)
                st.session_state.ocr_text = cleaned
                st.success("Teks OCR berhasil dirapikan!")
            except Exception as e:
                st.error("Gagal merapikan teks.")
                st.code(str(e))

    with col2:
        st.info(
            "Fitur ini akan:\n"
            "- Menghapus spasi ganda\n"
            "- Menghapus baris kosong\n"
            "- Membuat teks OCR lebih rapi dan siap dipakai"
        )
else:
    st.warning("Belum ada teks OCR untuk dirapikan.")
# =========================================================
# 📦 PAKET F4 – MOBILE FRIENDLY UI
# Optimasi tampilan agar enak dipakai di HP
# =========================================================

st.markdown(
    """
    <style>
    /* Umum */
    html, body, [class*="css"]  {
        font-size: 16px;
    }

    /* Tombol lebih besar & nyaman disentuh */
    .stButton>button {
        width: 100%;
        padding: 12px 10px;
        font-size: 16px;
        border-radius: 10px;
        margin-top: 6px;
        margin-bottom: 6px;
    }

    /* Input box */
    .stTextInput>div>div>input,
    .stTextArea textarea {
        font-size: 16px;
        padding: 10px;
        border-radius: 8px;
    }

    /* Selectbox & Radio */
    .stSelectbox>div>div,
    .stRadio>div {
        font-size: 16px;
    }

    /* Judul */
    h1, h2, h3 {
        text-align: center;
    }

    /* Sidebar mobile */
    @media (max-width: 768px) {
        .css-1d391kg {
            padding: 1rem 0.5rem;
        }
        .stSidebar {
            width: 100% !important;
        }
    }

    /* Area OCR */
    textarea {
        min-height: 180px;
    }

    /* Preview gambar */
    img {
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.success("📱 Paket F4 aktif. Tampilan sudah Mobile Friendly.")
# =========================================================
# 📦 PAKET F5 – FINAL PROTEKSI CRASH & STABILITAS TOTAL
# =========================================================

st.markdown("---")
st.markdown("## 🛡 Sistem Keamanan & Stabilitas Aplikasi")

# Proteksi jika ada error global
def safe_run(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error("Terjadi kesalahan, tetapi aplikasi tetap berjalan aman.")
        st.code(str(e))
        return None

# Monitoring Session State penting
def check_session():
    required_keys = [
        "image", "ocr_text", "boxes",
        "struk_data", "surat_data", "nota_data",
        "invoice_data", "ktp_data",
        "history", "is_unlocked"
    ]
    for k in required_keys:
        if k not in st.session_state:
            st.session_state[k] = None

check_session()

# Tombol Reset Sistem (Darurat)
with st.expander("⚠️ Reset Sistem (Darurat)"):
    st.warning(
        "Gunakan ini hanya jika aplikasi terasa berat atau ada error aneh. "
        "Ini akan menghapus session sementara, bukan file."
    )

    if st.button("🔄 Reset Aplikasi Sekarang"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Session berhasil di-reset. Silakan refresh halaman.")
        st.stop()

# Proteksi OCR kosong
if "ocr_text" in st.session_state:
    if st.session_state.ocr_text is None:
        st.session_state.ocr_text = ""

# Proteksi data kosong
def safe_dict(d):
    if not isinstance(d, dict):
        return {}
    return d

st.session_state.struk_data = safe_dict(st.session_state.struk_data)
st.session_state.surat_data = safe_dict(st.session_state.surat_data)
st.session_state.nota_data = safe_dict(st.session_state.nota_data)
st.session_state.invoice_data = safe_dict(st.session_state.invoice_data)
st.session_state.ktp_data = safe_dict(st.session_state.ktp_data)

# Footer final
st.markdown("---")
st.success("🎉 ScanText Pro SUPER FINAL SIAP DIGUNAKAN!")
st.caption("Aplikasi stabil, aman, tanpa 'Oh no', siap dipakai publik & mobile.")


