# ================================
# PART 1 - CORE SETUP & UI SYSTEM
# ================================

import streamlit as st
import easyocr
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
from datetime import datetime
import re

from datetime import datetime

def save_to_history(mode, ocr_text, final_text, summary):
    if "scan_history" not in st.session_state:
        st.session_state.scan_history = []

    data = {
        "time": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "mode": mode,
        "text": ocr_text,
        "final_text": final_text,
        "summary": summary
    }

    st.session_state.scan_history.append(data)

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from docx import Document
from openpyxl import Workbook

# ================================
# STREAMLIT PAGE CONFIG
# ================================
st.set_page_config(
    page_title="ScanText Pro Ultimate",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# SESSION STATE INIT
# ================================
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

# ================================
# THEME SYSTEM
# ================================
st.sidebar.markdown("🎨 **Tema UI**")
theme = st.sidebar.selectbox(
    "Pilih Tema:",
    ["Light", "Dark", "Blue", "Green", "Minimalist"]
)

def apply_theme(theme):
    if theme == "Dark":
        bg = "#0E1117"
        text = "white"
        card = "#262730"
    elif theme == "Blue":
        bg = "#EAF4FF"
        text = "#003366"
        card = "#CFE3FF"
    elif theme == "Green":
        bg = "#E9F7EF"
        text = "#145A32"
        card = "#D5F5E3"
    elif theme == "Minimalist":
        bg = "#F5F5F5"
        text = "#222"
        card = "#FFFFFF"
    else:  # Light
        bg = "white"
        text = "#111"
        card = "#F2F2F2"

    st.markdown(f"""
    <style>
    body {{
        background-color: {bg};
        color: {text};
    }}
    .stTextArea textarea {{
        background-color: {card};
        color: {text};
    }}
    .stTextInput input {{
        background-color: {card};
        color: {text};
    }}
    .stButton>button {{
        background-color: #4CAF50;
        color: white;
        border-radius: 6px;
        padding: 8px 14px;
        border: none;
    }}
    .stButton>button:hover {{
        opacity: 0.85;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme(theme)

# ================================
# MOBILE FRIENDLY UI
# ================================
st.markdown("""
<style>
/* Global font */
html, body, [class*="css"] {
    font-size: 15px;
}

/* Textarea tinggi nyaman */
textarea {
    min-height: 220px !important;
}

/* Upload box */
div[data-testid="stFileUploader"] {
    padding: 12px;
    border-radius: 10px;
}

/* Sidebar width mobile */
section[data-testid="stSidebar"] {
    min-width: 260px !important;
}

/* Responsive font */
@media (max-width: 768px) {
    h1 { font-size: 24px; }
    h2 { font-size: 20px; }
    h3 { font-size: 18px; }
    .stButton button {
        width: 100%;
        font-size: 14px;
    }
}
</style>
""", unsafe_allow_html=True)

# ================================
# APP HEADER
# ================================
st.title("📄 ScanText Pro – OCR Ultimate")
st.markdown(
    "OCR + Kamera + Crop + Edit + PDF + Word + Excel + Multi Bahasa + Tema UI + Riwayat + Grafik + Smart Extract"
)

# ================================
# MODE SELECTION
# ================================
mode = st.selectbox("📌 Pilih Mode:", ["Surat", "Struk"])

# ================================
# OCR LANGUAGE
# ================================
lang_map = {
    "Indonesia": ["id"],
    "Inggris": ["en"],
    "Jepang": ["ja"],
    "Arab": ["ar"]
}

ocr_lang = st.selectbox("🌐 Bahasa OCR:", list(lang_map.keys()))

# ================================
# EASY OCR READER INIT (CACHED)
# ================================
@st.cache_resource
def load_ocr_reader(lang):
    return easyocr.Reader(lang, gpu=False)

reader = load_ocr_reader(lang_map[ocr_lang])

# ================================
# HELPER FUNCTIONS
# ================================

def format_rupiah(number):
    try:
        number = int(number)
        return f"Rp {number:,.0f}".replace(",", ".")
    except:
        return number

def clean_ocr_text(text):
    # Auto Rapikan OCR
    text = re.sub(r'\n\s*\n+', '\n\n', text)  # hapus baris kosong berlebih
    text = re.sub(r'[ \t]+', ' ', text)       # hapus spasi ganda
    return text.strip()

# ================================
# PART 2 - SIDEBAR RIWAYAT + KELOLA (HAPUS)
# ================================

st.sidebar.markdown("📂 Riwayat Scan")

# Pastikan session_state scan_history ada
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

# Jika belum ada riwayat
if len(st.session_state.scan_history) == 0:
    st.sidebar.info("Belum ada riwayat.")
else:
    # 🔥 Hapus semua riwayat
    if st.sidebar.button("🔥 Hapus Semua Riwayat"):
        st.session_state.scan_history.clear()
        st.sidebar.success("Semua riwayat berhasil dihapus!")
        st.experimental_rerun()

    st.sidebar.markdown("---")

    # 📜 Daftar riwayat satu per satu
    for i, item in enumerate(reversed(st.session_state.scan_history)):
        col1, col2 = st.sidebar.columns([4, 1])

        # Tombol load riwayat
        with col1:
            if st.button(
                f"📄 {item['time']} | {item['mode']}",
                key=f"load_{i}"
            ):
                st.session_state.ocr_text = item.get("text", "")
                st.session_state.final_text = item.get("final_text", "")
                st.session_state.judul = item.get("judul", "")
                st.session_state.tanggal = item.get("tanggal", "")
                st.session_state.alamat = item.get("alamat", "")
                st.session_state.summary_data = item.get("summary", {})
                st.success("Riwayat berhasil dimuat kembali!")

        # Tombol hapus satu riwayat
        with col2:
            if st.button("❌", key=f"delete_{i}"):
                real_index = len(st.session_state.scan_history) - 1 - i
                st.session_state.scan_history.pop(real_index)
                st.sidebar.success("Satu riwayat berhasil dihapus!")
                st.experimental_rerun()


# ================================
# FUNGSI SIMPAN KE RIWAYAT
# ================================

def save_to_history(mode, ocr_text, final_text, summary=None):
    history_item = {
        "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "mode": mode,
        "text": ocr_text,
        "final_text": final_text,
        "judul": st.session_state.judul,
        "tanggal": st.session_state.tanggal,
        "alamat": st.session_state.alamat,
        "summary": summary if summary else {}
    }
    st.session_state.scan_history.append(history_item)
# ================================
# PART 3 – UPLOAD, KAMERA & CROP GAMBAR
# ================================

st.markdown("## 📷 Ambil atau Upload Gambar")

tab1, tab2 = st.tabs(["📁 Upload Gambar", "📸 Kamera"])

image = None

with tab1:
    uploaded_file = st.file_uploader(
        "Upload gambar (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"]
    )
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Gambar yang diupload", use_container_width=True)

with tab2:
    camera_file = st.camera_input("Ambil foto langsung")
    if camera_file:
        image = Image.open(camera_file).convert("RGB")
        st.image(image, caption="Foto dari kamera", use_container_width=True)

# ================================
# CROP GAMBAR
# ================================

if image:
    st.markdown("## ✂️ Crop Gambar")

    width, height = image.size
    st.info(f"Ukuran gambar: {width} x {height}")

    col1, col2 = st.columns(2)

    with col1:
        x1 = st.number_input("X awal", 0, width, 0)
        y1 = st.number_input("Y awal", 0, height, 0)

    with col2:
        x2 = st.number_input("X akhir", 0, width, width)
        y2 = st.number_input("Y akhir", 0, height, height)

    if st.button("✂️ Crop Sekarang"):
        if x2 > x1 and y2 > y1:
            cropped_image = image.crop((x1, y1, x2, y2))
            st.session_state.cropped_image = cropped_image
            st.image(cropped_image, caption="Hasil Crop", use_container_width=True)
            st.success("Gambar berhasil di-crop!")
        else:
            st.error("Koordinat crop tidak valid!")

# Pastikan ada state cropped_image
if "cropped_image" not in st.session_state:
    st.session_state.cropped_image = None

# ================================
# PILIH GAMBAR UNTUK OCR
# ================================

st.markdown("## 🖼️ Pilih Gambar untuk OCR")

if st.session_state.cropped_image is not None:
    selected_image = st.session_state.cropped_image
    st.info("OCR menggunakan hasil crop.")
elif image is not None:
    selected_image = image
    st.info("OCR menggunakan gambar asli.")
else:
    selected_image = None
    st.warning("Silakan upload gambar atau ambil foto terlebih dahulu.")

# ================================
# PART 4 – OCR ENGINE (MULTI BAHASA + MODE STRUK / SURAT)
# ================================

st.markdown("## 🔍 OCR (Pengenalan Teks dari Gambar)")

# Pilih Bahasa OCR
ocr_lang = st.selectbox(
    "🌍 Pilih Bahasa OCR",
    ["Indonesia", "Inggris", "Jepang", "Arab"]
)

lang_map = {
    "Indonesia": ["id"],
    "Inggris": ["en"],
    "Jepang": ["ja"],
    "Arab": ["ar"]
}

# Pilih Mode
mode = st.selectbox(
    "📄 Pilih Mode Output",
    ["Struk", "Surat"]
)

# Inisialisasi OCR Reader (cache supaya tidak reload terus)
@st.cache_resource
def load_reader(lang):
    return easyocr.Reader(lang, gpu=False)

reader = load_reader(lang_map[ocr_lang])

# Tombol OCR
if st.button("🔎 Jalankan OCR"):
    if selected_image is None:
        st.error("Belum ada gambar untuk OCR!")
    else:
        with st.spinner("Sedang memproses OCR..."):
            np_img = np.array(selected_image)
            result = reader.readtext(np_img, detail=0, paragraph=True)

            ocr_text = "\n".join(result)

            # Simpan ke session
            st.session_state.ocr_text = ocr_text
            st.session_state.final_text = ocr_text
            st.success("OCR selesai!")

# Pastikan state ada
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""
if "final_text" not in st.session_state:
    st.session_state.final_text = ""

# ================================
# TAMPILKAN HASIL OCR
# ================================

if st.session_state.ocr_text:
    st.markdown("## 📝 Hasil OCR")

    edited_text = st.text_area(
        "Edit teks OCR di sini:",
        st.session_state.final_text,
        height=300
    )

    st.session_state.final_text = edited_text

# ================================
# MODE SURAT (FORMAT OTOMATIS)
# ================================

if mode == "Surat" and st.session_state.final_text:
    st.markdown("## ✉️ Mode Surat")

    if "judul" not in st.session_state:
        st.session_state.judul = ""
    if "tanggal" not in st.session_state:
        st.session_state.tanggal = ""
    if "alamat" not in st.session_state:
        st.session_state.alamat = ""

    st.session_state.judul = st.text_input("Judul Surat", st.session_state.judul)
    st.session_state.tanggal = st.text_input("Tanggal", st.session_state.tanggal)
    st.session_state.alamat = st.text_input("Alamat Tujuan", st.session_state.alamat)

    formatted_surat = f"""
{st.session_state.judul}

Tanggal: {st.session_state.tanggal}
Alamat: {st.session_state.alamat}

{st.session_state.final_text}
    """.strip()

    st.session_state.final_text = formatted_surat
    st.success("Format Surat diterapkan.")

# ================================
# MODE STRUK (UNTUK SMART EXTRACT)
# ================================

if mode == "Struk" and st.session_state.final_text:
    st.markdown("## 🧾 Mode Struk Aktif")
    st.info("Teks ini akan dipakai untuk Smart Extract (Total, Tanggal, Toko, Telepon).")

# ================================
# PART 5 – SMART EXTRACT STRUK + FORMAT RUPIAH
# ================================

st.markdown("## 📊 Smart Extract (Khusus Mode Struk)")

def smart_extract_struk(text):
    data = {
        "nama_toko": "Tidak ditemukan",
        "tanggal": "Tidak ditemukan",
        "telepon": "Tidak ditemukan",
        "total": "Tidak ditemukan"
    }

    lines = text.split("\n")

    # 1. Nama Toko → biasanya baris paling atas & huruf besar
    for line in lines[:5]:
        clean = line.strip()
        if len(clean) > 3 and clean.isupper():
            data["nama_toko"] = clean
            break

    # 2. Nomor Telepon
    phone_match = re.search(r'(\+62|08)\d{8,13}', text.replace(" ", ""))
    if phone_match:
        data["telepon"] = phone_match.group(0)

    # 3. Tanggal
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        r'\d{1,2}\s(?:Jan|Feb|Mar|Apr|Mei|Jun|Jul|Agu|Sep|Okt|Nov|Des)[a-z]*\s\d{2,4}',
        r'\d{1,2}\s(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s\d{4}'
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["tanggal"] = match.group(0)
            break

    # 4. Total Harga (Rp)
    rupiah_match = re.findall(r'Rp[\s\.]*([\d\.]+)', text)
    if rupiah_match:
        total_num = rupiah_match[-1].replace(".", "")
        data["total"] = format_rupiah(total_num)
    else:
        # fallback: ambil angka terbesar
        numbers = re.findall(r'\d+', text.replace(".", ""))
        if numbers:
            max_number = max(map(int, numbers))
            data["total"] = format_rupiah(max_number)

    return data


# ================================
# TAMPILKAN SMART EXTRACT
# ================================

if mode == "Struk" and st.session_state.final_text:
    summary = smart_extract_struk(st.session_state.final_text)
    st.session_state.summary_data = summary

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"🏪 Nama Toko: {summary['nama_toko']}")
        st.info(f"📅 Tanggal: {summary['tanggal']}")

    with col2:
        st.info(f"📞 Telepon: {summary['telepon']}")
        st.success(f"💰 Total Harga: {summary['total']}")

    st.markdown("---")
    st.subheader("📌 Ringkasan Data Struk")
    df_summary = pd.DataFrame(summary.items(), columns=["Field", "Value"])
    st.table(df_summary)


# ================================
# SIMPAN KE RIWAYAT OTOMATIS
# ================================

if st.session_state.final_text:
    if st.button("💾 Simpan ke Riwayat Scan"):
        save_to_history(
            mode=mode,
            ocr_text=st.session_state.ocr_text,
            final_text=st.session_state.final_text,
            summary=st.session_state.summary_data if mode == "Struk" else {}
        )
        st.success("Data berhasil disimpan ke riwayat!")
        st.rerun()

# ================================
# PART 6 – EXPORT, CLIPBOARD, GRAFIK & UTILITAS
# ================================

st.markdown("## 🧰 Tools & Export")

# ================================
# ✨ AUTO RAPIKAN OCR
# ================================
if st.session_state.final_text:
    if st.button("✨ Rapikan Teks OCR"):
        st.session_state.final_text = clean_ocr_text(st.session_state.final_text)
        st.success("Teks OCR berhasil dirapikan!")


# ================================
# 📋 COPY TO CLIPBOARD
# ================================
if st.session_state.final_text:
    st.markdown("### 📋 Copy ke Clipboard")
    copy_text = st.session_state.final_text.replace("`", "").replace("$", "")
    st.components.v1.html(
        f"""
        <textarea id="copyText" style="position:absolute; left:-1000px;">{copy_text}</textarea>
        <button onclick="copyTextFunc()" style="
            width:100%;
            padding:12px;
            font-size:16px;
            border-radius:8px;
            background:#4CAF50;
            color:white;
            border:none;
            cursor:pointer;">
            📋 Salin Teks
        </button>

        <script>
        function copyTextFunc() {{
            var copyText = document.getElementById("copyText");
            copyText.select();
            document.execCommand("copy");
            alert("Teks berhasil disalin ke clipboard!");
        }}
        </script>
        """,
        height=90
    )


# ================================
# 📄 EXPORT TXT
# ================================
if st.session_state.final_text:
    st.download_button(
        "⬇ Download TXT",
        st.session_state.final_text,
        file_name=f"hasil_ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )


# ================================
# 📑 EXPORT PDF
# ================================
def create_pdf(text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    textobject = c.beginText(40, height - 40)
    textobject.setFont("Helvetica", 10)

    for line in text.split("\n"):
        textobject.textLine(line)

    c.drawText(textobject)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

if st.session_state.final_text:
    pdf_file = create_pdf(st.session_state.final_text)
    st.download_button(
        "⬇ Download PDF",
        pdf_file,
        file_name=f"hasil_ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )


# ================================
# 📝 EXPORT WORD
# ================================
def create_word(text):
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

if st.session_state.final_text:
    word_file = create_word(st.session_state.final_text)
    st.download_button(
        "⬇ Download Word (.docx)",
        word_file,
        file_name=f"hasil_ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


# ================================
# 📊 EXPORT EXCEL (KHUSUS STRUK)
# ================================
def create_excel(summary, full_text):
    wb = Workbook()
    ws = wb.active
    ws.title = "Hasil OCR"

    ws.append(["Field", "Value"])
    for k, v in summary.items():
        ws.append([k, v])

    ws.append([])
    ws.append(["Teks Lengkap OCR"])
    ws.append([full_text])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

if mode == "Struk" and st.session_state.final_text:
    excel_file = create_excel(st.session_state.summary_data, st.session_state.final_text)
    st.download_button(
        "⬇ Download Excel (.xlsx)",
        excel_file,
        file_name=f"hasil_struk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ================================
# 📈 GRAFIK PENGELUARAN
# ================================
st.markdown("## 📈 Grafik Pengeluaran (Mode Struk)")

expense_data = []

for item in st.session_state.scan_history:
    if item["mode"] == "Struk":
        summary = item.get("summary", {})
        tanggal = summary.get("tanggal", "")
        total = summary.get("total", "")

        if total:
            total_clean = re.sub(r"[^\d]", "", total)
            if total_clean.isdigit():
                expense_data.append({
                    "tanggal": tanggal,
                    "total": int(total_clean)
                })

if len(expense_data) == 0:
    st.info("Belum ada data struk untuk grafik.")
else:
    df = pd.DataFrame(expense_data)

    def parse_date(x):
        try:
            return pd.to_datetime(x, dayfirst=True)
        except:
            return None

    df["tanggal"] = df["tanggal"].apply(parse_date)
    df = df.dropna()

    if df.empty:
        st.warning("Format tanggal tidak konsisten, grafik tidak bisa dibuat.")
    else:
        chart_mode = st.radio("Pilih Grafik:", ["Harian", "Bulanan"])

        if chart_mode == "Harian":
            df_group = df.groupby(df["tanggal"].dt.date)["total"].sum().reset_index()
            df_group.columns = ["Tanggal", "Total"]
        else:
            df_group = df.groupby(df["tanggal"].dt.to_period("M"))["total"].sum().reset_index()
            df_group["Tanggal"] = df_group["tanggal"].astype(str)
            df_group = df_group.rename(columns={"total": "Total"})
            df_group = df_group[["Tanggal", "Total"]]

        st.bar_chart(df_group.set_index("Tanggal"))

        df_group["Total (Rp)"] = df_group["Total"].apply(lambda x: format_rupiah(x))
        st.dataframe(df_group)
