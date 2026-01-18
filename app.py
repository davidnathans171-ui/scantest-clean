import streamlit as st
from PIL import Image
import numpy as np
import easyocr
import re
import base64
import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from docx import Document
from openpyxl import Workbook
import streamlit.components.v1 as components

# ================= CONFIG =================
st.set_page_config(
    page_title="ScanText Pro Ultimate",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= SESSION STATE =================
def init_state():
    defaults = {
        "ocr_text": "",
        "final_text": "",
        "current_image": None,
        "scan_history": [],
        "summary_data": {},
        "judul": "HASIL OCR",
        "tanggal": datetime.now().strftime("%d %B %Y"),
        "alamat": "",
        "cleaned_once": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ================= THEME =================
st.sidebar.markdown("🎨 **Tema UI**")
theme = st.sidebar.selectbox(
    "Pilih Tema:",
    ["Light", "Dark", "Blue", "Green", "Minimalist"]
)

def apply_theme(theme):
    if theme == "Dark":
        bg, text, card = "#0e1117", "white", "#262730"
    elif theme == "Blue":
        bg, text, card = "#0A1F44", "white", "#102A56"
    elif theme == "Green":
        bg, text, card = "#0B3D2E", "white", "#145A32"
    elif theme == "Minimalist":
        bg, text, card = "#F5F5F5", "#111", "#FFFFFF"
    else:
        bg, text, card = "#FFFFFF", "#000", "#F0F2F6"

    st.markdown(f"""
    <style>
    body, .stApp {{
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

# ================= MOBILE FRIENDLY =================
st.markdown("""
<style>
html, body {
    font-size: 16px;
}
section[data-testid="stSidebar"] {
    min-width: 250px !important;
}
.stButton>button {
    width: 100%;
}
@media (max-width: 768px) {
    h1 { font-size: 26px; }
    h2 { font-size: 22px; }
    h3 { font-size: 18px; }
}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR: RIWAYAT + KELOLA =================
st.sidebar.markdown("📂 **Riwayat Scan**")

if len(st.session_state.scan_history) == 0:
    st.sidebar.info("Belum ada riwayat.")
else:
    # Tombol hapus semua
    if st.sidebar.button("🔥 Hapus Semua Riwayat"):
        st.session_state.scan_history.clear()
        st.success("Semua riwayat berhasil dihapus!")
        st.experimental_rerun()

    st.sidebar.markdown("---")

    # Daftar riwayat satu per satu
    for i, item in enumerate(reversed(st.session_state.scan_history)):
        col1, col2 = st.sidebar.columns([4, 1])

        with col1:
            if st.button(f"📄 {item['time']} | {item['mode']}", key=f"load_{i}"):
                st.session_state.ocr_text = item["text"]
                st.session_state.final_text = item["final_text"]
                st.session_state.judul = item["judul"]
                st.session_state.tanggal = item["tanggal"]
                st.session_state.alamat = item["alamat"]
                st.session_state.summary_data = item.get("summary", {})
                st.success("Riwayat berhasil dimuat kembali!")

        with col2:
            if st.button("❌", key=f"del_{i}"):
                # karena kita pakai reversed, index aslinya:
                real_index = len(st.session_state.scan_history) - 1 - i
                st.session_state.scan_history.pop(real_index)
                st.success("Satu riwayat berhasil dihapus!")
                st.experimental_rerun()


# ================= HEADER =================
st.title("📄 ScanText Pro – Ultimate Final")
st.success(
    "OCR + Kamera + Crop + Edit + Rapikan + Smart Extract + Export Lengkap + Grafik Pengeluaran"
)

# ================= MODE =================
mode = st.selectbox(
    "📌 Pilih Mode Dokumen:",
    ["Struk", "Surat"]
)

# ================= OCR LANGUAGE =================
ocr_language = st.selectbox(
    "🌍 Bahasa OCR:",
    ["Indonesia", "English", "Japanese", "Arabic"]
)

lang_map = {
    "Indonesia": ["id", "en"],
    "English": ["en"],
    "Japanese": ["ja", "en"],
    "Arabic": ["ar", "en"]
}

selected_lang = lang_map[ocr_language]

st.markdown("---")
st.subheader("📷 Upload, Kamera & OCR akan dimulai di PART 2")
# ================= UPLOAD & KAMERA =================
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

with tab2:
    camera_file = st.camera_input("Ambil foto langsung dari kamera")
    if camera_file:
        image = Image.open(camera_file).convert("RGB")

# ================= PREVIEW GAMBAR =================
if image:
    st.session_state.current_image = image

if st.session_state.current_image is not None:
    st.markdown("### 🖼️ Preview Gambar Asli")
    st.image(st.session_state.current_image, use_container_width=True)

    # ================= CROP GAMBAR =================
    st.markdown("### ✂️ Crop Gambar (Opsional)")
    st.caption("Atur area yang ingin dibaca OCR. Biarkan default jika ingin membaca seluruh gambar.")

    img_width, img_height = st.session_state.current_image.size

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        left = st.number_input("Left", 0, img_width, 0)
    with col2:
        top = st.number_input("Top", 0, img_height, 0)
    with col3:
        right = st.number_input("Right", 0, img_width, img_width)
    with col4:
        bottom = st.number_input("Bottom", 0, img_height, img_height)

    # Validasi agar tidak error
    if right <= left:
        right = left + 1
    if bottom <= top:
        bottom = top + 1

    cropped_image = st.session_state.current_image.crop((left, top, right, bottom))

    st.markdown("### 🔍 Hasil Crop")
    st.image(cropped_image, use_container_width=True)

    # Simpan hasil crop ke session untuk OCR
    st.session_state.current_image = cropped_image
else:
    st.info("Silakan upload gambar atau ambil dari kamera terlebih dahulu.")

# ================= OCR PROCESS =================
if st.session_state.current_image is not None:
    st.markdown("## 🔍 Proses OCR")

    if st.button("🚀 Jalankan OCR"):
        with st.spinner("Sedang membaca teks dari gambar..."):
            try:
                reader = easyocr.Reader(selected_lang, gpu=False)
                result = reader.readtext(
                    np.array(st.session_state.current_image),
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


# ================= AUTO RAPIKAN TEKS OCR =================
def clean_ocr_text(text):
    # Hapus spasi ganda
    text = re.sub(r'[ \t]+', ' ', text)

    # Hapus baris kosong berlebihan
    text = re.sub(r'\n\s*\n+', '\n\n', text)

    # Rapikan spasi tiap baris
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()


# ================= EDIT + RAPIKAN TEKS =================
if st.session_state.ocr_text:
    st.markdown("## ✏️ Edit & Rapikan Teks OCR")

    col_edit, col_clean = st.columns([4, 1])

    with col_edit:
        edited_text = st.text_area(
            "Kamu bisa mengedit hasil OCR di sini:",
            value=st.session_state.ocr_text,
            height=260
        )

    with col_clean:
        st.markdown(" ")
        st.markdown(" ")
        if st.button("✨ Rapikan Teks"):
            st.session_state.ocr_text = clean_ocr_text(st.session_state.ocr_text)
            st.success("Teks OCR berhasil dirapikan!")

    # Simpan edit manual
    st.session_state.ocr_text = edited_text


# ================= FORM DATA DOKUMEN =================
if st.session_state.ocr_text:
    st.markdown("## 📝 Data Dokumen")

    col_a, col_b = st.columns(2)

    with col_a:
        judul = st.text_input(
            "Judul Dokumen",
            value=st.session_state.judul
        )

        tanggal = st.text_input(
            "Tanggal",
            value=st.session_state.tanggal
        )

    with col_b:
        alamat = st.text_input(
            "Alamat (Opsional)",
            value=st.session_state.alamat
        )

    st.session_state.judul = judul
    st.session_state.tanggal = tanggal
    st.session_state.alamat = alamat


# ================= MODE STRUK / SURAT =================
if st.session_state.ocr_text:
    st.markdown("## ⚙️ Mode Output")

    if mode == "Struk":
        st.info("Mode **Struk** aktif → Smart Extract akan dijalankan.")
    else:
        st.info("Mode **Surat** aktif → Format surat formal akan digunakan.")


# ================= TEKS FINAL =================
if st.session_state.ocr_text:
    st.markdown("## 📄 Preview Teks Final")

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
        height=320
    )
# ================= SMART EXTRACT FUNCTION =================
def smart_extract(text):
    """
    Mengambil otomatis:
    - Nama Toko
    - Tanggal (dari struk)
    - Nomor Telepon
    - Total Harga (format Rupiah)
    Hanya dipakai untuk Mode = Struk
    """

    nama_toko = "Tidak ditemukan"
    tanggal_auto = "Tidak ditemukan"
    telepon = "Tidak ditemukan"
    total = "Tidak ditemukan"

    lines = text.split("\n")

    # 1. Nama Toko → baris pertama yang full huruf besar
    for line in lines:
        clean = line.strip()
        if len(clean) > 3 and clean.isupper():
            nama_toko = clean
            break

    # 2. Nomor Telepon → 08xxxx atau +62xxxx
    phone_match = re.search(r'(\+62|08)\d{8,13}', text.replace(" ", ""))
    if phone_match:
        telepon = phone_match.group(0)

    # 3. Tanggal → format umum
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # 12/01/2026
        r'\d{1,2}\s(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s\d{4}'
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            tanggal_auto = match.group(0)
            break

    # 4. Total Harga → cari Rp terlebih dahulu
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


# ================= TAMPILKAN SMART EXTRACT =================
if st.session_state.ocr_text and mode == "Struk":

    st.markdown("## 📊 Ringkasan Otomatis (Smart Extract)")

    # Jalankan Smart Extract
    nama_toko, tanggal_auto, telepon, total = smart_extract(st.session_state.ocr_text)

    # Simpan ke session_state untuk export
    st.session_state.summary_data = {
        "nama_toko": nama_toko,
        "tanggal": tanggal_auto,
        "telepon": telepon,
        "total": total
    }

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"🏪 **Nama Toko:** {nama_toko}")
        st.info(f"📅 **Tanggal (dari struk):** {tanggal_auto}")

    with col2:
        st.info(f"📞 **Telepon:** {telepon}")
        st.success(f"💰 **Total Harga:** {total}")
# ================= SIMPAN KE RIWAYAT =================
if st.session_state.final_text:
    if st.button("💾 Simpan ke Riwayat Scan"):
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
    st.markdown("## 📋 Salin Teks ke Clipboard")

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


# ================= GRAFIK PENGELUARAN =================
st.markdown("---")
st.subheader("📊 Grafik Pengeluaran (Mode Struk)")

expense_data = []

for item in st.session_state.scan_history:
    if item["mode"] == "Struk":
        summary = item.get("summary", {})
        tanggal = summary.get("tanggal", "")
        total = summary.get("total", "")

        if total:
            total_clean = re.sub(r"[^\d]", "", total)
            if total_clean.isdigit():
                total_value = int(total_clean)
            else:
                continue
        else:
            continue

        expense_data.append({
            "tanggal": tanggal,
            "total": total_value
        })

if len(expense_data) == 0:
    st.info("Belum ada data struk untuk ditampilkan di grafik.")
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
        st.warning("Format tanggal belum konsisten, tidak bisa dibuat grafik.")
    else:
        chart_mode = st.radio(
            "Pilih Tampilan Grafik:",
            ["Harian", "Bulanan"],
            index=0
        )

        if chart_mode == "Harian":
            df_group = df.groupby(df["tanggal"].dt.date)["total"].sum().reset_index()
            df_group.columns = ["Tanggal", "Total Pengeluaran"]
        else:
            df_group = df.groupby(df["tanggal"].dt.to_period("M"))["total"].sum().reset_index()
            df_group["Tanggal"] = df_group["tanggal"].astype(str)
            df_group = df_group.rename(columns={"total": "Total Pengeluaran"})
            df_group = df_group[["Tanggal", "Total Pengeluaran"]]

        st.bar_chart(df_group.set_index("Tanggal"))

        st.markdown("### 📋 Ringkasan Data")
        df_group["Total Pengeluaran (Rp)"] = df_group["Total Pengeluaran"].apply(
            lambda x: f"Rp {x:,}".replace(",", ".")
        )
        st.dataframe(df_group)
