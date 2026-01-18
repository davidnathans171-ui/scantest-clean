import streamlit as st
import streamlit.components.v1 as components
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

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="ScanText Pro Ultimate",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================== SESSION STATE INIT =====================
if "history" not in st.session_state:
    st.session_state.history = []

if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""

if "final_text" not in st.session_state:
    st.session_state.final_text = ""

if "summary_data" not in st.session_state:
    st.session_state.summary_data = {}

# ===================== THEME SELECTOR =====================
st.sidebar.title("🎨 Pilih Tema UI")
theme = st.sidebar.selectbox(
    "Tema:",
    ["Light", "Dark", "Blue", "Green", "Minimalist"]
)

def apply_theme(theme):
    if theme == "Dark":
        bg = "#0E1117"
        text = "white"
        card = "#262730"
    elif theme == "Blue":
        bg = "#0A1F44"
        text = "white"
        card = "#102A56"
    elif theme == "Green":
        bg = "#0F2F1F"
        text = "white"
        card = "#1E4D3A"
    elif theme == "Minimalist":
        bg = "#FFFFFF"
        text = "#111"
        card = "#F2F2F2"
    else:
        bg = "#FFFFFF"
        text = "#000"
        card = "#F5F5F5"

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
        padding: 1rem;
    }}
    .stTextArea textarea {{
        min-height: 220px;
        background-color: {card};
        color: {text};
    }}
    .stTextInput input {{
        background-color: {card};
        color: {text};
    }}
    .stSelectbox div {{
        background-color: {card};
        color: {text};
    }}
    .stButton button {{
        width: 100%;
        font-size: 16px;
    }}

    /* MOBILE FRIENDLY */
    @media (max-width: 768px) {{
        h1 {{ font-size: 26px; }}
        h2 {{ font-size: 22px; }}
        h3 {{ font-size: 18px; }}
        .stButton button {{ font-size: 15px; }}
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme(theme)

# ===================== SIDEBAR HISTORY =====================
st.sidebar.markdown("## 🧾 Riwayat Scan")
if st.session_state.history:
    for i, item in enumerate(st.session_state.history[::-1]):
        st.sidebar.write(f"{len(st.session_state.history)-i}. {item}")
else:
    st.sidebar.info("Belum ada riwayat.")

# ===================== HEADER =====================
st.title("📄 ScanText Pro – OCR Ultimate")
st.success("OCR + Camera + Crop + Edit + PDF + Word + Excel + Multi Bahasa + Tema UI")

# ===================== MODE SELECT =====================
mode = st.selectbox("Pilih Mode:", ["Struk", "Surat"])

# ===================== OCR LANGUAGE =====================
lang_map = {
    "Indonesia": ["id"],
    "Inggris": ["en"],
    "Jepang": ["ja"],
    "Arab": ["ar"]
}
ocr_lang = st.selectbox("🌍 Bahasa OCR:", list(lang_map.keys()))

# ===================== IMAGE INPUT =====================
st.subheader("📷 Upload atau Kamera")
tab1, tab2 = st.tabs(["📂 Upload", "📸 Kamera"])

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

if image:
    st.image(image, caption="Preview Gambar", use_container_width=True)
    # ===================== CROP IMAGE =====================
if image:
    st.subheader("✂ Crop Gambar (Opsional)")
    width, height = image.size

    col_crop1, col_crop2 = st.columns(2)
    with col_crop1:
        x1 = st.slider("X Awal", 0, width, 0)
        x2 = st.slider("X Akhir", 0, width, width)
    with col_crop2:
        y1 = st.slider("Y Awal", 0, height, 0)
        y2 = st.slider("Y Akhir", 0, height, height)

    # Pastikan tidak error posisi
    if x2 <= x1:
        x2 = x1 + 1
    if y2 <= y1:
        y2 = y1 + 1

    cropped_image = image.crop((x1, y1, x2, y2))

    st.image(cropped_image, caption="Hasil Crop", use_container_width=True)

    # ===================== OCR PROCESS =====================
    st.subheader("🔍 Proses OCR")

    if st.button("🚀 Proses OCR Sekarang"):
        with st.spinner("Sedang membaca teks dari gambar..."):
            try:
                reader = easyocr.Reader(lang_map[ocr_lang], gpu=False)
                result = reader.readtext(np.array(cropped_image), detail=0)

                extracted_text = "\n".join(result)

                if extracted_text.strip() == "":
                    st.warning("Tidak ada teks yang terdeteksi.")
                else:
                    st.session_state.ocr_text = extracted_text
                    st.success("OCR berhasil dijalankan!")

            except Exception as e:
                st.error("Terjadi kesalahan saat OCR:")
                st.code(str(e))

# ===================== TAMPILKAN HASIL OCR =====================
if st.session_state.ocr_text:
    st.subheader("📄 Hasil OCR (Bisa Diedit)")
    st.session_state.ocr_text = st.text_area(
        "Edit teks hasil OCR:",
        st.session_state.ocr_text,
        height=250
    )
# ===================== FORM DATA DOKUMEN =====================
if st.session_state.ocr_text:

    st.subheader("📝 Data Dokumen")

    col_form1, col_form2 = st.columns(2)

    with col_form1:
        judul = st.text_input(
            "Judul Dokumen",
            value=st.session_state.get("judul", "HASIL OCR")
        )

        tanggal = st.text_input(
            "Tanggal",
            value=st.session_state.get("tanggal", datetime.now().strftime("%d %B %Y"))
        )

    with col_form2:
        alamat = st.text_input(
            "Alamat (opsional)",
            value=st.session_state.get("alamat", "")
        )

    # Simpan ke session
    st.session_state.judul = judul
    st.session_state.tanggal = tanggal
    st.session_state.alamat = alamat

    # ===================== MODE OUTPUT =====================
    st.subheader("⚙ Mode Output")

    if mode == "Surat":
        st.info("Mode Surat aktif → Format surat formal.")
    else:
        st.info("Mode Struk aktif → Smart Extract akan dijalankan.")

    # ===================== HASIL AKHIR TEKS =====================
    st.subheader("📃 Teks Final")

    if mode == "Surat":
        final_text = f"""{judul}

Tanggal : {tanggal}
Alamat  : {alamat}

{st.session_state.ocr_text}
"""
    else:  # Mode Struk
        final_text = f"""{judul}

Tanggal : {tanggal}

{st.session_state.ocr_text}
"""

    st.session_state.final_text = final_text

    st.text_area(
        "Preview Teks Final:",
        final_text,
        height=300
    )
# ===================== SMART EXTRACT FUNCTION =====================
def smart_extract(text):
    """
    Mengambil:
    - Nama Toko
    - Tanggal
    - Nomor Telepon
    - Total Harga (format Rupiah)
    Hanya digunakan untuk Mode = Struk
    """

    nama_toko = "Tidak ditemukan"
    tanggal_auto = "Tidak ditemukan"
    telepon = "Tidak ditemukan"
    total = "Tidak ditemukan"

    lines = text.split("\n")

    # 1. Nama Toko → ambil baris huruf besar pertama
    for line in lines:
        clean = line.strip()
        if len(clean) > 3 and clean.isupper():
            nama_toko = clean
            break

    # 2. Nomor Telepon → 08xxxx atau +62xxxx
    phone_match = re.search(r'(\+62|08)\d{8,13}', text.replace(" ", ""))
    if phone_match:
        telepon = phone_match.group(0)

    # 3. Tanggal → format umum Indonesia / angka
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # 12/01/2026
        r'\d{1,2}\s(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s\d{4}'
    ]
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            tanggal_auto = date_match.group(0)
            break

    # 4. Total Harga → cari Rp terlebih dahulu
    rupiah_matches = re.findall(r'Rp\s?[\d\.]+', text)
    if rupiah_matches:
        total = rupiah_matches[-1]
    else:
        # fallback → ambil angka terbesar
        numbers = re.findall(r'\d+', text.replace(".", ""))
        if numbers:
            max_number = max(map(int, numbers))
            total = "Rp " + f"{max_number:,}".replace(",", ".")

    return nama_toko, tanggal_auto, telepon, total


# ===================== TAMPILKAN SMART EXTRACT (STRUK ONLY) =====================
if st.session_state.ocr_text and mode == "Struk":

    st.subheader("📊 Ringkasan Otomatis (Smart Extract)")

    # Jalankan Smart Extract
    nama_toko, tanggal_auto, telepon, total = smart_extract(st.session_state.ocr_text)

    # Simpan ke session supaya bisa dipakai Export Excel, PDF, dll
    st.session_state.summary_data = {
        "nama_toko": nama_toko,
        "tanggal": tanggal_auto,
        "telepon": telepon,
        "total": total
    }

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.info(f"🏪 **Nama Toko:** {nama_toko}")
        st.info(f"📅 **Tanggal:** {tanggal_auto}")

    with col_s2:
        st.info(f"📞 **Telepon:** {telepon}")
        st.success(f"💰 **Total Harga:** {total}")
# ===================== SIMPAN KE RIWAYAT =====================
if st.session_state.ocr_text:
    if st.button("💾 Simpan ke Riwayat"):
        history_item = {
            "time": datetime.now().strftime("%d-%m-%Y %H:%M"),
            "mode": mode,
            "judul": st.session_state.judul,
            "tanggal": st.session_state.tanggal,
            "alamat": st.session_state.alamat,
            "text": st.session_state.ocr_text,
            "summary": st.session_state.summary_data if mode == "Struk" else {}
        }
        st.session_state.history.append(history_item)
        st.success("Berhasil disimpan ke riwayat!")


# ===================== EXPORT TXT =====================
if st.session_state.final_text:
    st.download_button(
        label="⬇ Download TXT",
        data=st.session_state.final_text,
        file_name="hasil_ocr.txt",
        mime="text/plain"
    )


# ===================== EXPORT PDF =====================
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
# ================= COPY TO CLIPBOARD =================
if st.session_state.final_text:
    st.subheader("📋 Salin Teks")

    copy_text = st.session_state.final_text.replace("`", "").replace("$", "")

    components.html(
        f"""
        <textarea id="copyText" style="position:absolute; left:-1000px;">{copy_text}</textarea>

        <button onclick="copyToClipboard()" style="
            width:100%;
            padding:12px;
            font-size:16px;
            border-radius:8px;
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

# ===================== EXPORT WORD =====================
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


# ===================== EXPORT EXCEL =====================
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


# ===================== SIDEBAR: RIWAYAT SCAN (KLIK UNTUK LOAD) =====================
st.sidebar.markdown("## 📚 Riwayat Scan")

if len(st.session_state.history) == 0:
    st.sidebar.info("Belum ada data.")
else:
    for i, item in enumerate(reversed(st.session_state.history)):
        label = f"{item['time']} | {item['mode']} | {item['judul']}"
        if st.sidebar.button(label):
            st.session_state.ocr_text = item["text"]
            st.session_state.judul = item["judul"]
            st.session_state.tanggal = item["tanggal"]
            st.session_state.alamat = item["alamat"]
            st.session_state.summary_data = item.get("summary", {})
            st.success("Riwayat berhasil dimuat kembali!")

