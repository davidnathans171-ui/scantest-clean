import streamlit as st
import pandas as pd
from PIL import Image
import numpy as np
import easyocr
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from docx import Document
from openpyxl import Workbook
from datetime import datetime
import re
import base64
import streamlit.components.v1 as components

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="ScanText Pro Ultimate",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= SESSION STATE =================
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""

if "final_text" not in st.session_state:
    st.session_state.final_text = ""

if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

if "summary_data" not in st.session_state:
    st.session_state.summary_data = {}

# ================= THEME UI =================
st.sidebar.markdown("🎨 **Pilih Tema UI**")
theme = st.sidebar.selectbox(
    "Tema:",
    ["Light", "Dark", "Blue", "Green", "Minimalist"]
)

def apply_theme(theme):
    if theme == "Dark":
        bg = "#0e1117"
        text = "white"
        card = "#262730"
    elif theme == "Blue":
        bg = "#0A1F44"
        text = "white"
        card = "#102A56"
    elif theme == "Green":
        bg = "#0B3D2E"
        text = "white"
        card = "#145A32"
    elif theme == "Minimalist":
        bg = "#F5F5F5"
        text = "#111"
        card = "#FFFFFF"
    else:  # Light
        bg = "#FFFFFF"
        text = "#000"
        card = "#F0F2F6"

    st.markdown(f"""
    <style>
    body {{
        background-color: {bg};
        color: {text};
    }}
    .stApp {{
        background-color: {bg};
        color: {text};
    }}
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 2rem;
    }}
    .card {{
        background-color: {card};
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }}
    textarea {{
        min-height: 200px !important;
        font-size: 15px !important;
    }}
    button {{
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme(theme)

# ================= MOBILE FRIENDLY CSS =================
st.markdown("""
<style>
/* Global */
html, body {
    font-size: 16px;
}

/* Sidebar width mobile */
section[data-testid="stSidebar"] {
    min-width: 250px !important;
}

/* Upload box */
div[data-testid="stFileUploader"] {
    padding: 12px;
    border-radius: 10px;
}

/* Button mobile friendly */
.stButton>button {
    width: 100%;
    font-size: 15px;
}

/* Responsive */
@media (max-width: 768px) {
    h1 { font-size: 26px; }
    h2 { font-size: 22px; }
    h3 { font-size: 18px; }
}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR: RIWAYAT SCAN =================
st.sidebar.markdown("📂 **Riwayat Scan**")

if len(st.session_state.scan_history) == 0:
    st.sidebar.info("Belum ada riwayat.")
else:
    for i, item in enumerate(st.session_state.scan_history):
        st.sidebar.write(f"{i+1}. {item[:40]}...")

# ================= HEADER =================
st.title("📄 ScanText Pro – OCR Ultimate")
st.success(
    "OCR + Kamera + Crop + Edit + PDF + Word + Excel + Multi Bahasa + Tema UI + Smart Extract"
)

# ================= MODE PILIHAN =================
mode = st.selectbox(
    "📌 Pilih Mode:",
    ["Struk", "Surat"]
)

# ================= BAHASA OCR =================
ocr_language = st.selectbox(
    "🌍 Bahasa OCR:",
    ["Indonesia", "English", "Japanese", "Arabic"]
)

# Mapping bahasa ke EasyOCR
lang_map = {
    "Indonesia": ["id", "en"],
    "English": ["en"],
    "Japanese": ["ja", "en"],
    "Arabic": ["ar", "en"]
}

selected_lang = lang_map[ocr_language]

# ================= TEMPAT KONTEN LANJUTAN =================
st.markdown("---")
st.subheader("📷 Upload atau Kamera")
st.info("Part berikutnya akan berisi Upload, Kamera, Crop, dan OCR.")
# ================= UPLOAD & KAMERA =================
tab1, tab2 = st.tabs(["📁 Upload Gambar", "📷 Kamera"])

image = None

with tab1:
    uploaded_file = st.file_uploader(
        "Upload gambar (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"]
    )
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")

with tab2:
    camera_file = st.camera_input("Ambil foto langsung")
    if camera_file:
        image = Image.open(camera_file).convert("RGB")

# ================= PREVIEW & CROP =================
if image:
    st.markdown("### 🖼 Preview Gambar Asli")
    st.image(image, use_container_width=True)

    st.markdown("### ✂️ Crop Gambar (Opsional)")
    st.caption("Atur area yang ingin di-OCR")

    width, height = image.size

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        left = st.number_input("Left", 0, width, 0)
    with col2:
        top = st.number_input("Top", 0, height, 0)
    with col3:
        right = st.number_input("Right", 0, width, width)
    with col4:
        bottom = st.number_input("Bottom", 0, height, height)

    cropped_image = image.crop((left, top, right, bottom))

    st.markdown("### 🔍 Hasil Crop")
    st.image(cropped_image, use_container_width=True)

    st.session_state["current_image"] = cropped_image
else:
    st.info("Silakan upload gambar atau ambil dari kamera terlebih dahulu.")
# ================= OCR PROCESS =================
if "current_image" in st.session_state:

    st.markdown("### 🔍 Proses OCR")

    if st.button("🚀 Jalankan OCR"):
        with st.spinner("Sedang membaca teks dari gambar..."):
            try:
                reader = easyocr.Reader(selected_lang, gpu=False)
                result = reader.readtext(
                    np.array(st.session_state["current_image"]),
                    detail=0
                )

                text_result = "\n".join(result)

                if text_result.strip() == "":
                    st.warning("Tidak ada teks yang terdeteksi.")
                else:
                    st.session_state.ocr_text = text_result
                    st.success("OCR berhasil dijalankan!")

            except Exception as e:
                st.error("Terjadi kesalahan saat OCR:")
                st.code(str(e))


# ================= EDIT TEKS OCR =================
if st.session_state.ocr_text:

    st.markdown("### ✏️ Edit Teks Hasil OCR")

    edited_text = st.text_area(
        "Kamu bisa mengedit hasil OCR di sini:",
        value=st.session_state.ocr_text,
        height=250
    )

    st.session_state.ocr_text = edited_text


# ================= FORM JUDUL, TANGGAL, ALAMAT =================
if st.session_state.ocr_text:

    st.markdown("### 📝 Data Dokumen")

    col_a, col_b = st.columns(2)

    with col_a:
        judul = st.text_input(
            "Judul Dokumen",
            value=st.session_state.get("judul", "HASIL OCR")
        )

        tanggal = st.text_input(
            "Tanggal",
            value=st.session_state.get("tanggal", datetime.now().strftime("%d %B %Y"))
        )

    with col_b:
        alamat = st.text_input(
            "Alamat (Opsional)",
            value=st.session_state.get("alamat", "")
        )

    st.session_state.judul = judul
    st.session_state.tanggal = tanggal
    st.session_state.alamat = alamat


# ================= MODE STRUK / SURAT =================
if st.session_state.ocr_text:

    st.markdown("### ⚙️ Mode Output")

    if mode == "Struk":
        st.info("Mode **Struk** aktif → Smart Extract akan digunakan.")
    else:
        st.info("Mode **Surat** aktif → Format dokumen surat formal.")


# ================= TEKS FINAL =================
if st.session_state.ocr_text:

    st.markdown("### 📄 Preview Teks Final")

    if mode == "Surat":
        final_text = f"""{st.session_state.judul}

Tanggal : {st.session_state.tanggal}
Alamat  : {st.session_state.alamat}

{st.session_state.ocr_text}
"""
    else:  # Mode Struk
        final_text = f"""{st.session_state.judul}

Tanggal : {st.session_state.tanggal}

{st.session_state.ocr_text}
"""

    st.session_state.final_text = final_text

    st.text_area(
        "Hasil akhir dokumen:",
        final_text,
        height=300
    )
# ================= SMART EXTRACT FUNCTION =================
def smart_extract(text):
    """
    Mengambil otomatis:
    - Nama Toko
    - Tanggal
    - Nomor Telepon
    - Total Harga (format Rupiah: Rp 23.500)
    Hanya dipakai untuk Mode = Struk
    """

    nama_toko = "Tidak ditemukan"
    tanggal_auto = "Tidak ditemukan"
    telepon = "Tidak ditemukan"
    total = "Tidak ditemukan"

    lines = text.split("\n")

    # 1. Nama Toko → baris huruf besar pertama
    for line in lines:
        clean = line.strip()
        if len(clean) > 3 and clean.isupper():
            nama_toko = clean
            break

    # 2. Nomor Telepon → 08xxxx atau +62xxxx
    phone_match = re.search(r'(\+62|08)\d{8,13}', text.replace(" ", ""))
    if phone_match:
        telepon = phone_match.group(0)

    # 3. Tanggal → format umum Indonesia
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # 12/01/2026
        r'\d{1,2}\s(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s\d{4}'
    ]
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            tanggal_auto = date_match.group(0)
            break

    # 4. Total Harga → cari format Rp dulu
    rupiah_matches = re.findall(r'Rp\s?[\d\.]+', text)
    if rupiah_matches:
        total = rupiah_matches[-1]
    else:
        # fallback: ambil angka terbesar
        numbers = re.findall(r'\d+', text.replace(".", ""))
        if numbers:
            max_number = max(map(int, numbers))
            total = "Rp " + f"{max_number:,}".replace(",", ".")

    return nama_toko, tanggal_auto, telepon, total


# ================= JALANKAN SMART EXTRACT (STRUK ONLY) =================
if st.session_state.ocr_text and mode == "Struk":

    st.markdown("### 📊 Ringkasan Otomatis (Smart Extract)")

    # Jalankan fungsi
    nama_toko, tanggal_auto, telepon, total = smart_extract(st.session_state.ocr_text)

    # Simpan ke session untuk export PDF/Word/Excel
    st.session_state.summary_data = {
        "nama_toko": nama_toko,
        "tanggal": tanggal_auto,
        "telepon": telepon,
        "total": total
    }

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"🏪 **Nama Toko:** {nama_toko}")
        st.info(f"📅 **Tanggal:** {tanggal_auto}")

    with col2:
        st.info(f"📞 **Telepon:** {telepon}")
        st.success(f"💰 **Total Harga:** {total}")
# ================= SIMPAN KE RIWAYAT SCAN =================
if st.session_state.final_text:
    if st.button("💾 Simpan ke Riwayat"):
        history_item = {
            "time": datetime.now().strftime("%d-%m-%Y %H:%M"),
            "mode": mode,
            "judul": st.session_state.judul,
            "tanggal": st.session_state.tanggal,
            "alamat": st.session_state.alamat,
            "text": st.session_state.ocr_text,
            "final_text": st.session_state.final_text,
            "summary": st.session_state.summary_data if mode == "Struk" else {}
        }
        st.session_state.scan_history.append(history_item)
        st.success("Berhasil disimpan ke Riwayat Scan!")


# ================= COPY TO CLIPBOARD =================
if st.session_state.final_text:
    st.markdown("### 📋 Salin Teks ke Clipboard")

    copy_text = st.session_state.final_text.replace("`", "").replace("$", "")

    components.html(
        f"""
        <textarea id="copyText" style="position:absolute; left:-1000px;">{copy_text}</textarea>

        <button onclick="copyToClipboard()" style="
            width:100%;
            padding:12px;
            font-size:16px;
            border-radius:10px;
            background-color:#4CAF50;
            color:white;
            border:none;
            cursor:pointer;
        ">
        📋 Salin Teks ke Clipboard
        </button>

        <script>
        function copyToClipboard() {{
            var text = document.getElementById("copyText");
            text.select();
            text.setSelectionRange(0, 99999);
            document.execCommand("copy");
            alert("Teks berhasil disalin ke clipboard!");
        }}
        </script>
        """,
        height=90
    )


# ================= EXPORT TXT =================
if st.session_state.final_text:
    st.download_button(
        label="⬇ Download TXT",
        data=st.session_state.final_text,
        file_name="hasil_ocr.txt",
        mime="text/plain"
    )


# ================= EXPORT PDF =================
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
        label="⬇ Download PDF",
        data=pdf_file,
        file_name="hasil_ocr.pdf",
        mime="application/pdf"
    )


# ================= EXPORT WORD =================
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
        label="⬇ Download Word (.docx)",
        data=word_file,
        file_name="hasil_ocr.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


# ================= EXPORT EXCEL =================
def create_excel(summary, full_text):
    wb = Workbook()
    ws = wb.active
    ws.title = "OCR Result"

    ws.append(["Field", "Value"])
    ws.append(["Nama Toko", summary.get("nama_toko", "—")])
    ws.append(["Tanggal", summary.get("tanggal", "—")])
    ws.append(["Telepon", summary.get("telepon", "—")])
    ws.append(["Total Harga", summary.get("total", "—")])

    ws.append([])
    ws.append(["Teks Lengkap OCR"])
    ws.append([full_text])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


if st.session_state.final_text and mode == "Struk":
    excel_file = create_excel(st.session_state.summary_data, st.session_state.final_text)
    st.download_button(
        label="⬇ Download Excel (.xlsx)",
        data=excel_file,
        file_name="hasil_ocr.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ================= SIDEBAR: RIWAYAT SCAN (KLIK UNTUK LOAD) =================
st.sidebar.markdown("## 📚 Riwayat Scan")

if len(st.session_state.scan_history) == 0:
    st.sidebar.info("Belum ada data.")
else:
    for i, item in enumerate(reversed(st.session_state.scan_history)):
        label = f"{item['time']} | {item['mode']} | {item['judul']}"
        if st.sidebar.button(label):
            st.session_state.ocr_text = item["text"]
            st.session_state.final_text = item["final_text"]
            st.session_state.judul = item["judul"]
            st.session_state.tanggal = item["tanggal"]
            st.session_state.alamat = item["alamat"]
            st.session_state.summary_data = item.get("summary", {})
            st.success("Riwayat berhasil dimuat kembali!")
            # ===================== GRAFIK PENGELUARAN =====================
st.markdown("---")
st.subheader("📊 Grafik Pengeluaran (Mode Struk)")

# Ambil semua data struk dari riwayat
expense_data = []

for item in st.session_state.scan_history:
    if item["mode"] == "Struk":
        summary = item.get("summary", {})
        tanggal = summary.get("tanggal", "")
        total = summary.get("total", "")

        # Bersihkan Rupiah → angka
        if total:
            total_clean = re.sub(r"[^\d]", "", total)
            if total_clean.isdigit():
                total_value = int(total_clean)
            else:
                continue
        else:
            continue

        # Simpan
        expense_data.append({
            "tanggal": tanggal,
            "total": total_value
        })

if len(expense_data) == 0:
    st.info("Belum ada data struk untuk ditampilkan di grafik.")
else:
    df = pd.DataFrame(expense_data)

    # Convert tanggal → datetime
    def parse_date(x):
        try:
            return pd.to_datetime(x, dayfirst=True)
        except:
            return None

    df["tanggal"] = df["tanggal"].apply(parse_date)
    df = df.dropna()

    if df.empty:
        st.warning("Format tanggal belum konsisten, tidak bisa dibuat grafik.")
    else:
        # Pilihan grafik
        chart_mode = st.radio(
            "Pilih Tampilan Grafik:",
            ["Harian", "Bulanan"],
            index=0  # Default Harian sesuai pilihan kamu
        )

        if chart_mode == "Harian":
            df_group = df.groupby(df["tanggal"].dt.date)["total"].sum().reset_index()
            df_group.columns = ["Tanggal", "Total Pengeluaran"]
        else:
            df_group = df.groupby(df["tanggal"].dt.to_period("M"))["total"].sum().reset_index()
            df_group["Tanggal"] = df_group["tanggal"].astype(str)
            df_group = df_group.rename(columns={"total": "Total Pengeluaran"})
            df_group = df_group[["Tanggal", "Total Pengeluaran"]]

        st.markdown("### 📊 Grafik Batang Pengeluaran")
        st.bar_chart(df_group.set_index("Tanggal"))

        # Tabel ringkasan
        st.markdown("### 📋 Ringkasan Data")
        df_group["Total Pengeluaran (Rp)"] = df_group["Total Pengeluaran"].apply(
            lambda x: f"Rp {x:,}".replace(",", ".")
        )
        st.dataframe(df_group)

