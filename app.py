# ==================================================
# PART 1 FINAL
# CORE SYSTEM + SESSION + PIN PROTECTION
# ==================================================

import streamlit as st
import easyocr
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
from datetime import datetime
import re

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from docx import Document
from openpyxl import Workbook

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="ScanText Pro – OCR Ultimate",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# PIN SYSTEM (MODE PRIVAT)
# ==================================================
PIN_CODE = "1234"

if "riwayat_unlocked" not in st.session_state:
    st.session_state.riwayat_unlocked = False

# ==================================================
# SESSION STATE INIT
# ==================================================
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""

if "final_text" not in st.session_state:
    st.session_state.final_text = ""

if "summary_data" not in st.session_state:
    st.session_state.summary_data = {}

if "judul" not in st.session_state:
    st.session_state.judul = ""

if "tanggal" not in st.session_state:
    st.session_state.tanggal = ""

if "alamat" not in st.session_state:
    st.session_state.alamat = ""

if "cropped_image" not in st.session_state:
    st.session_state.cropped_image = None

# ==================================================
# SAVE TO HISTORY FUNCTION
# ==================================================
def save_to_history(mode, ocr_text, final_text, summary):
    data = {
        "time": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "mode": mode,
        "text": ocr_text,
        "final_text": final_text,
        "judul": st.session_state.judul,
        "tanggal": st.session_state.tanggal,
        "alamat": st.session_state.alamat,
        "summary": summary
    }
    st.session_state.scan_history.append(data)

# ==================================================
# HELPER FUNCTIONS
# ==================================================
def format_rupiah(number):
    try:
        number = int(number)
        return f"Rp {number:,.0f}".replace(",", ".")
    except:
        return number

def clean_ocr_text(text):
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

# ==================================================
# HEADER
# ==================================================
st.title("📄 ScanText Pro – OCR Ultimate")
st.caption("OCR • Kamera • Crop • PDF • Word • Excel • Riwayat • PIN Protection")
# ==================================================
# PART 2 FINAL
# THEME SYSTEM + MOBILE FRIENDLY UI
# ==================================================

# ===============================
# THEME SELECTOR
# ===============================
st.sidebar.markdown("🎨 Tema Tampilan")

theme = st.sidebar.selectbox(
    "Pilih Tema UI:",
    ["Light (Default)", "Dark", "Blue", "Green", "Minimalist"]
)

def apply_theme(theme_name):
    if theme_name == "Dark":
        css = """
        <style>
        body { background-color: #0f172a; color: #e5e7eb; }
        .stApp { background-color: #0f172a; }
        </style>
        """
    elif theme_name == "Blue":
        css = """
        <style>
        body { background-color: #0f172a; color: #93c5fd; }
        .stApp { background-color: #0f172a; }
        </style>
        """
    elif theme_name == "Green":
        css = """
        <style>
        body { background-color: #022c22; color: #6ee7b7; }
        .stApp { background-color: #022c22; }
        </style>
        """
    elif theme_name == "Minimalist":
        css = """
        <style>
        body { background-color: #ffffff; color: #111827; }
        .stApp { background-color: #ffffff; }
        .block-container { padding: 1.5rem; }
        </style>
        """
    else:  # Light Default
        css = """
        <style>
        body { background-color: #f9fafb; color: #111827; }
        .stApp { background-color: #f9fafb; }
        </style>
        """

    st.markdown(css, unsafe_allow_html=True)

apply_theme(theme)

# ===============================
# MOBILE FRIENDLY UI
# ===============================
mobile_css = """
<style>
/* Make buttons larger and more touch-friendly */
button[kind="primary"], button {
    padding: 12px 20px;
    font-size: 16px;
    border-radius: 8px;
}

/* Make text areas and inputs mobile friendly */
textarea, input {
    font-size: 16px !important;
}

/* Reduce side padding for mobile */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.5rem;
    }
    .stSidebar {
        width: 100% !important;
    }
}
</style>
"""
st.markdown(mobile_css, unsafe_allow_html=True)

# ===============================
# PIN LOCK UI (SIDEBAR)
# ===============================
st.sidebar.markdown("---")
st.sidebar.markdown("🔐 **Mode Privat Riwayat**")

if not st.session_state.riwayat_unlocked:
    pin_input = st.sidebar.text_input(
        "Masukkan PIN:",
        type="password"
    )
    if st.sidebar.button("🔓 Buka Riwayat"):
        if pin_input == PIN_CODE:
            st.session_state.riwayat_unlocked = True
            st.sidebar.success("Riwayat berhasil dibuka!")
            st.rerun()
        else:
            st.sidebar.error("❌ PIN salah!")
else:
    st.sidebar.success("Riwayat dalam keadaan terbuka")
    if st.sidebar.button("🔒 Kunci Ulang Riwayat"):
        st.session_state.riwayat_unlocked = False
        st.sidebar.warning("Riwayat dikunci kembali")
        st.rerun()

# ===============================
# MAIN MODE SELECTOR
# ===============================
st.markdown("## 🧭 Mode Pemindaian")

mode = st.radio(
    "Pilih Mode:",
    ["Struk", "Surat"],
    horizontal=True
)

st.info(f"Mode aktif: **{mode}**")

# ==================================================
# END PART 2
# ==================================================
# ==================================================
# PART 3 FINAL
# UPLOAD IMAGE • CAMERA • CROP IMAGE
# ==================================================

st.markdown("## 📸 Input Gambar")

# Pilih sumber gambar
source = st.radio(
    "Pilih sumber gambar:",
    ["Upload File", "Kamera"],
    horizontal=True
)

uploaded_image = None

# ===============================
# UPLOAD FILE
# ===============================
if source == "Upload File":
    uploaded_file = st.file_uploader(
        "Upload gambar (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"]
    )
    if uploaded_file:
        uploaded_image = Image.open(uploaded_file)

# ===============================
# CAMERA
# ===============================
elif source == "Kamera":
    camera_image = st.camera_input("Ambil gambar dengan kamera")
    if camera_image:
        uploaded_image = Image.open(camera_image)

# ===============================
# SHOW ORIGINAL IMAGE
# ===============================
if uploaded_image:
    st.image(uploaded_image, caption="📷 Gambar Asli", use_container_width=True)

    # Simpan gambar asli ke session
    st.session_state.original_image = uploaded_image

    st.markdown("---")
    st.markdown("## ✂️ Crop Gambar")

    # Slider crop sederhana
    width, height = uploaded_image.size

    col1, col2 = st.columns(2)
    with col1:
        x1 = st.slider("X1", 0, width, 0)
        y1 = st.slider("Y1", 0, height, 0)
    with col2:
        x2 = st.slider("X2", 0, width, width)
        y2 = st.slider("Y2", 0, height, height)

    if st.button("✂️ Terapkan Crop"):
        cropped = uploaded_image.crop((x1, y1, x2, y2))
        st.session_state.cropped_image = cropped
        st.success("Gambar berhasil di-crop!")

# ===============================
# SHOW CROPPED IMAGE
# ===============================
if st.session_state.cropped_image is not None:
    st.image(
        st.session_state.cropped_image,
        caption="✂️ Hasil Crop",
        use_container_width=True
    )

# ==================================================
# END PART 3
# ==================================================
# ==================================================
# PART 4 FINAL
# OCR ENGINE • MULTI BAHASA • PROSES OCR
# ==================================================

st.markdown("## 🧠 OCR – Pengenalan Teks dari Gambar")

# ===============================
# PILIH BAHASA OCR
# ===============================
language_map = {
    "Indonesia": ["id"],
    "Inggris": ["en"],
    "Jepang": ["ja"],
    "Arab": ["ar"],
    "Indonesia + Inggris": ["id", "en"],
    "Indonesia + Inggris + Jepang": ["id", "en", "ja"],
    "Indonesia + Inggris + Arab": ["id", "en", "ar"]
}

selected_language = st.selectbox(
    "🌐 Pilih Bahasa OCR:",
    list(language_map.keys())
)

ocr_langs = language_map[selected_language]

st.caption(f"Bahasa OCR aktif: {', '.join(ocr_langs)}")

# ===============================
# LOAD EASY OCR READER (CACHE)
# ===============================
@st.cache_resource
def load_reader(langs):
    return easyocr.Reader(langs, gpu=False)

reader = load_reader(ocr_langs)

# ===============================
# PILIH GAMBAR UNTUK OCR
# ===============================
image_for_ocr = None

if st.session_state.cropped_image is not None:
    image_for_ocr = st.session_state.cropped_image
    st.info("OCR menggunakan gambar hasil crop.")
elif "original_image" in st.session_state:
    image_for_ocr = st.session_state.original_image
    st.info("OCR menggunakan gambar asli.")

# ===============================
# TOMBOL PROSES OCR
# ===============================
if image_for_ocr:
    if st.button("🔍 Proses OCR"):
        with st.spinner("Sedang membaca teks dari gambar..."):
            try:
                img_np = np.array(image_for_ocr)
                results = reader.readtext(img_np)

                text = ""
                for res in results:
                    text += res[1] + "\n"

                text = clean_ocr_text(text)

                st.session_state.ocr_text = text
                st.session_state.final_text = text

                st.success("OCR berhasil dilakukan!")

            except Exception as e:
                st.error("Terjadi kesalahan saat OCR")
                st.code(str(e))
else:
    st.warning("Silakan upload atau ambil gambar terlebih dahulu.")

# ===============================
# TAMPILKAN HASIL OCR
# ===============================
if st.session_state.ocr_text:
    st.markdown("### 📄 Hasil OCR (Teks Asli)")
    st.text_area(
        "OCR Text:",
        st.session_state.ocr_text,
        height=200
    )

    st.markdown("### ✏️ Teks Siap Edit")
    st.session_state.final_text = st.text_area(
        "Edit teks hasil OCR:",
        st.session_state.final_text,
        height=250
    )

# ==================================================
# END PART 4
# ==================================================
# ==================================================
# PART 5 FINAL
# AUTO RAPIIKAN TEKS • COPY TO CLIPBOARD • MODE SURAT & MODE STRUK
# ==================================================

st.markdown("## ✨ Edit & Optimasi Teks OCR")

col_a, col_b, col_c = st.columns(3)

# ===============================
# AUTO RAPIIKAN TEKS
# ===============================
with col_a:
    if st.button("✨ Rapikan Teks OCR"):
        st.session_state.final_text = clean_ocr_text(st.session_state.final_text)
        st.success("Teks OCR berhasil dirapikan!")

# ===============================
# COPY TO CLIPBOARD
# ===============================
with col_b:
    if st.button("📋 Salin ke Clipboard"):
        st.write(
            f"""
            <script>
            navigator.clipboard.writeText(`{st.session_state.final_text}`);
            </script>
            """,
            unsafe_allow_html=True
        )
        st.success("Teks berhasil disalin ke clipboard!")

# ===============================
# RESET TEKS
# ===============================
with col_c:
    if st.button("🗑️ Hapus Teks"):
        st.session_state.final_text = ""
        st.session_state.ocr_text = ""
        st.success("Teks berhasil dihapus!")

# ==================================================
# MODE SURAT & MODE STRUK
# ==================================================
st.markdown("---")
st.markdown("## 📝 Mode Surat & 🧾 Mode Struk")

if mode == "Surat":
    st.info("Mode Surat aktif. Fokus pada dokumen formal.")

    st.session_state.judul = st.text_input("Judul Surat:", st.session_state.judul)
    st.session_state.tanggal = st.text_input("Tanggal Surat:", st.session_state.tanggal)
    st.session_state.alamat = st.text_input("Alamat Tujuan:", st.session_state.alamat)

    st.markdown("### 📄 Teks Surat")
    st.session_state.final_text = st.text_area(
        "Isi Surat:",
        st.session_state.final_text,
        height=300
    )

elif mode == "Struk":
    st.info("Mode Struk aktif. Fokus pada data transaksi.")

    st.markdown("### 🧾 Hasil OCR Struk")
    st.session_state.final_text = st.text_area(
        "Teks Struk:",
        st.session_state.final_text,
        height=250
    )

    st.caption("Gunakan Smart Extract di part berikut untuk ringkasan otomatis.")

# ==================================================
# END PART 5
# ==================================================
# ==================================================
# PART 6 FINAL
# SMART EXTRACT (STRUK) • FORMAT RUPIAH OTOMATIS
# ==================================================

st.markdown("## 📊 Smart Extract (Khusus Mode Struk)")

# Fungsi bantu untuk mencari data dari teks struk
def smart_extract_struk(text):
    summary = {
        "nama_toko": "",
        "tanggal": "",
        "total": "",
        "telepon": ""
    }

    lines = text.splitlines()

    # Nama toko → biasanya di baris awal
    if len(lines) > 0:
        summary["nama_toko"] = lines[0].strip()

    # Cari tanggal (format umum Indonesia)
    date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    for line in lines:
        match = re.search(date_pattern, line)
        if match:
            summary["tanggal"] = match.group(1)
            break

    # Cari nomor telepon
    phone_pattern = r'(\+62|0)\d{8,13}'
    for line in lines:
        match = re.search(phone_pattern, line)
        if match:
            summary["telepon"] = match.group(0)
            break

    # Cari total harga (kata kunci: total, jumlah, grand total)
    total_pattern = r'(total|jumlah|grand total)[^\d]*(\d+[.,]?\d*)'
    for line in lines:
        match = re.search(total_pattern, line.lower())
        if match:
            raw_total = match.group(2).replace(".", "").replace(",", "")
            summary["total"] = format_rupiah(raw_total)
            break

    return summary


# ===============================
# JALANKAN SMART EXTRACT
# ===============================
if mode == "Struk" and st.session_state.final_text:

    if st.button("🧠 Jalankan Smart Extract"):
        st.session_state.summary_data = smart_extract_struk(st.session_state.final_text)
        st.success("Smart Extract berhasil dijalankan!")

    # ===============================
    # TAMPILKAN HASIL SMART EXTRACT
    # ===============================
    if st.session_state.summary_data:
        st.markdown("### 📋 Ringkasan Otomatis Struk")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "🏪 Nama Toko",
                st.session_state.summary_data.get("nama_toko", ""),
                key="summary_nama_toko"
            )

            st.text_input(
                "📅 Tanggal",
                st.session_state.summary_data.get("tanggal", ""),
                key="summary_tanggal"
            )

        with col2:
            st.text_input(
                "📞 No. Telepon",
                st.session_state.summary_data.get("telepon", ""),
                key="summary_telepon"
            )

            st.text_input(
                "💰 Total Belanja",
                st.session_state.summary_data.get("total", ""),
                key="summary_total"
            )

        st.caption("Semua data ini bisa kamu edit manual jika OCR kurang tepat.")

# ==================================================
# END PART 6
# ==================================================
# ==================================================
# PART 7 FINAL
# EXPORT TXT • PDF • WORD • EXCEL
# ==================================================

st.markdown("## 💾 Export Hasil OCR")

export_col1, export_col2, export_col3, export_col4 = st.columns(4)

# ===============================
# EXPORT KE TXT
# ===============================
with export_col1:
    if st.button("📄 Export TXT"):
        txt_data = st.session_state.final_text.encode("utf-8")
        st.download_button(
            label="⬇️ Download TXT",
            data=txt_data,
            file_name="hasil_ocr.txt",
            mime="text/plain"
        )

# ===============================
# EXPORT KE PDF
# ===============================
with export_col2:
    if st.button("📕 Export PDF"):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        textobject = c.beginText(40, height - 40)
        for line in st.session_state.final_text.split("\n"):
            textobject.textLine(line)

        c.drawText(textobject)
        c.showPage()
        c.save()

        buffer.seek(0)
        st.download_button(
            label="⬇️ Download PDF",
            data=buffer,
            file_name="hasil_ocr.pdf",
            mime="application/pdf"
        )

# ===============================
# EXPORT KE WORD
# ===============================
with export_col3:
    if st.button("📝 Export Word"):
        doc = Document()
        doc.add_heading("Hasil OCR", level=1)
        doc.add_paragraph(st.session_state.final_text)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="⬇️ Download Word",
            data=buffer,
            file_name="hasil_ocr.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# ===============================
# EXPORT KE EXCEL
# ===============================
with export_col4:
    if st.button("📊 Export Excel"):
        wb = Workbook()
        ws = wb.active
        ws.title = "Hasil OCR"

        ws["A1"] = "Hasil OCR"
        ws["A2"] = st.session_state.final_text

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="⬇️ Download Excel",
            data=buffer,
            file_name="hasil_ocr.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ==================================================
# END PART 7
# ==================================================
# ==================================================
# PART 8 FINAL
# SIMPAN KE RIWAYAT • SIDEBAR RIWAYAT • HAPUS SATU • HAPUS SEMUA
# TERINTEGRASI DENGAN MODE PRIVAT (PIN)
# ==================================================

st.markdown("## 💾 Simpan ke Riwayat Scan")

# Tombol simpan hanya muncul kalau sudah ada hasil OCR
if st.session_state.final_text.strip() != "":
    if st.button("💾 Simpan ke Riwayat Scan"):
        save_to_history(
            mode=mode,
            ocr_text=st.session_state.ocr_text,
            final_text=st.session_state.final_text,
            summary=st.session_state.summary_data if mode == "Struk" else {}
        )
        st.success("Data berhasil disimpan ke riwayat!")
        st.rerun()
else:
    st.info("Lakukan OCR terlebih dahulu sebelum menyimpan ke riwayat.")


# ==================================================
# SIDEBAR - RIWAYAT SCAN (DILINDUNGI PIN)
# ==================================================

st.sidebar.markdown("---")
st.sidebar.markdown("📁 Riwayat Scan")

# Pastikan variabel scan_history ada
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

# Jika riwayat belum dibuka dengan PIN
if not st.session_state.riwayat_unlocked:
    st.sidebar.info("🔐 Riwayat terkunci. Masukkan PIN untuk membukanya.")
else:
    # Jika sudah dibuka
    if len(st.session_state.scan_history) == 0:
        st.sidebar.info("Belum ada riwayat.")
    else:
        # 🔥 Hapus semua riwayat
        if st.sidebar.button("🔥 Hapus Semua Riwayat"):
            st.session_state.scan_history.clear()
            st.sidebar.success("Semua riwayat berhasil dihapus!")
            st.rerun()

        st.sidebar.markdown("---")

        # Tampilkan daftar riwayat (yang terbaru di atas)
        for i, item in enumerate(reversed(st.session_state.scan_history)):
            col1, col2 = st.sidebar.columns([4, 1])

            # Load riwayat
            with col1:
                if st.button(
                    f"📄 {item['time']} | {item['mode']}",
                    key=f"load_{i}"
                ):
                    st.session_state.ocr_text = item["text"]
                    st.session_state.final_text = item["final_text"]
                    st.session_state.judul = item.get("judul", "")
                    st.session_state.tanggal = item.get("tanggal", "")
                    st.session_state.alamat = item.get("alamat", "")
                    st.session_state.summary_data = item.get("summary", {})
                    st.success("Riwayat berhasil dimuat kembali!")
                    st.rerun()

            # Hapus satu riwayat
            with col2:
                if st.button("❌", key=f"delete_{i}"):
                    real_index = len(st.session_state.scan_history) - 1 - i
                    st.session_state.scan_history.pop(real_index)
                    st.sidebar.success("Satu riwayat berhasil dihapus!")
                    st.rerun()

# ==================================================
# END PART 8
# ==================================================
# ==================================================
# PART 9 FINAL
# 📊 GRAFIK PENGELUARAN (DARI RIWAYAT STRUK)
# ==================================================

st.markdown("## 📊 Grafik Pengeluaran")

# Fungsi bantu untuk ambil data struk dari riwayat
def get_struk_data_from_history():
    data = []
    for item in st.session_state.scan_history:
        if item["mode"] == "Struk" and item.get("summary"):
            total_raw = item["summary"].get("total", "")
            tanggal = item["summary"].get("tanggal", "")

            # Bersihkan format Rupiah -> angka
            if total_raw:
                try:
                    angka = (
                        total_raw.replace("Rp", "")
                        .replace(".", "")
                        .replace(" ", "")
                    )
                    total = int(angka)
                except:
                    total = 0
            else:
                total = 0

            data.append({
                "tanggal": tanggal,
                "total": total
            })
    return data


# ===============================
# PROSES DATA
# ===============================
if len(st.session_state.scan_history) == 0:
    st.info("Belum ada data riwayat untuk ditampilkan grafik.")
else:
    struk_data = get_struk_data_from_history()

    if len(struk_data) == 0:
        st.warning("Belum ada data Struk yang memiliki total belanja.")
    else:
        df = pd.DataFrame(struk_data)

        # Konversi tanggal ke format datetime jika bisa
        try:
            df["tanggal"] = pd.to_datetime(df["tanggal"], dayfirst=True, errors="coerce")
        except:
            pass

        st.markdown("### 📅 Total Pengeluaran per Hari")
        daily = df.groupby(df["tanggal"].dt.date)["total"].sum()
        st.bar_chart(daily)

        st.markdown("### 📆 Total Pengeluaran per Bulan")
        monthly = df.groupby(df["tanggal"].dt.to_period("M"))["total"].sum()
        st.bar_chart(monthly.astype(int))


# ==================================================
# END PART 9
# ==================================================
# ==================================================
# PART 10 FINAL
# FINAL STABILITY • VALIDATION • FOOTER
# ==================================================

st.markdown("---")
st.markdown("## 🧪 Status Sistem")

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    st.success("OCR Engine Aktif")

with status_col2:
    if st.session_state.riwayat_unlocked:
        st.success("Mode Privat: Terbuka")
    else:
        st.warning("Mode Privat: Terkunci")

with status_col3:
    st.info(f"Total Riwayat: {len(st.session_state.scan_history)} data")

# ==================================================
# VALIDASI SESSION STATE AGAR TIDAK ERROR
# ==================================================
required_states = [
    "ocr_text",
    "final_text",
    "summary_data",
    "scan_history",
    "judul",
    "tanggal",
    "alamat",
    "cropped_image",
]

for state in required_states:
    if state not in st.session_state:
        st.session_state[state] = ""

# ==================================================
# FOOTER
# ==================================================
st.markdown("""
---
<div style='text-align:center; font-size:14px; color:gray;'>
🚀 <b>ScanText Pro – OCR Ultimate</b><br>
OCR • Kamera • Crop • PDF • Word • Excel • Grafik • Riwayat • PIN Protection<br>
Dikembangkan oleh Nathans AI © 2026
</div>
""", unsafe_allow_html=True)

# ==================================================
# FINAL MESSAGE
# ==================================================
st.toast("🎉 ScanText Pro siap digunakan!", icon="✅")
