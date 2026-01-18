import streamlit as st
from PIL import Image
import numpy as np
import easyocr
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from docx import Document
from datetime import datetime
import re

# ======================================================
# PAGE CONFIG (HANYA SATU KALI)
# ======================================================
st.set_page_config(
    page_title="ScanText Pro Ultimate",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================================================
# MOBILE FRIENDLY UI
# ======================================================
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 16px; }
.main .block-container {
    padding: 1rem;
}
.stButton button {
    width: 100%;
    height: 45px;
    font-size: 16px;
    border-radius: 12px;
}
textarea {
    min-height: 200px !important;
}
input, textarea, select {
    padding: 8px;
    border-radius: 10px;
}
@media (max-width: 768px) {
    h1 { font-size: 24px; }
    h2 { font-size: 20px; }
    h3 { font-size: 18px; }
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# THEME
# ======================================================
theme = st.sidebar.selectbox(
    "🎨 Tema UI",
    ["Light", "Dark", "Blue", "Green", "Minimalist"]
)

def apply_theme(theme):
    if theme == "Dark":
        bg, text, card = "#0E1117", "white", "#262730"
    elif theme == "Blue":
        bg, text, card = "#0A1F44", "white", "#102A56"
    elif theme == "Green":
        bg, text, card = "#0F2F1F", "white", "#1F4F3F"
    elif theme == "Minimalist":
        bg, text, card = "#FFFFFF", "#333333", "#F2F2F2"
    else:
        bg, text, card = "#F5F7FA", "#000000", "#FFFFFF"

    st.markdown(f"""
    <style>
    .stApp {{ background-color:{bg}; color:{text}; }}
    textarea, input, .stButton>button {{
        background-color:{card};
        color:{text};
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme(theme)

# ======================================================
# SESSION STATE
# ======================================================
if "history" not in st.session_state:
    st.session_state.history = []
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""
if "judul" not in st.session_state:
    st.session_state.judul = "HASIL OCR"
if "tanggal" not in st.session_state:
    st.session_state.tanggal = datetime.now().strftime("%d %B %Y")
if "alamat" not in st.session_state:
    st.session_state.alamat = ""

# ======================================================
# SIDEBAR HISTORY (CLICK TO LOAD)
# ======================================================
st.sidebar.title("📚 Riwayat Scan")

if len(st.session_state.history) == 0:
    st.sidebar.info("Belum ada riwayat.")
else:
    for i, item in enumerate(reversed(st.session_state.history)):
        label = f"[{len(st.session_state.history)-i}] {item['time']} - {item['mode']}"
        if st.sidebar.button(label):
            st.session_state.ocr_text = item["text"]
            st.session_state.judul = item["judul"]
            st.session_state.tanggal = item["tanggal"]
            st.session_state.alamat = item["alamat"]
            st.success("Riwayat berhasil dimuat!")

# ======================================================
# TITLE
# ======================================================
st.title("📄 ScanText Pro Ultimate")
st.success("""
✔ OCR  
✔ Kamera  
✔ Upload  
✔ Crop  
✔ Edit Teks  
✔ Mode Surat & Struk  
✔ TXT / PDF / Word  
✔ Tema UI Lengkap  
✔ Multi Bahasa OCR  
✔ Riwayat Scan  
✔ Mobile Friendly  
✔ Smart Extract Struk
""")

# ======================================================
# MODE
# ======================================================
mode = st.selectbox("Pilih Mode:", ["Struk", "Surat"])

# ======================================================
# OCR LANGUAGE
# ======================================================
ocr_lang = st.selectbox(
    "🌍 Bahasa OCR",
    ["Indonesia", "English", "Japanese", "Arabic"]
)

lang_map = {
    "Indonesia": ["id", "en"],
    "English": ["en"],
    "Japanese": ["ja"],
    "Arabic": ["ar"]
}

# ======================================================
# SMART EXTRACT
# ======================================================
def smart_extract(text):
    nama_toko = "Tidak ditemukan"
    tanggal = "Tidak ditemukan"
    telepon = "Tidak ditemukan"
    total = "Tidak ditemukan"

    lines = text.split("\n")

    # Nama toko: baris kapital pertama
    for line in lines:
        l = line.strip()
        if len(l) > 3 and l.isupper():
            nama_toko = l
            break

    # Telepon
    phone = re.search(r'(\+62|08)\d{8,13}', text.replace(" ", ""))
    if phone:
        telepon = phone.group(0)

    # Tanggal
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        r'\d{1,2}\s(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s\d{4}'
    ]
    for p in date_patterns:
        d = re.search(p, text, re.IGNORECASE)
        if d:
            tanggal = d.group(0)
            break

    # Total Harga
    rupiah = re.findall(r'Rp\s?[\d\.]+', text)
    if rupiah:
        total = rupiah[-1]
    else:
        nums = re.findall(r'\d+', text.replace(".", ""))
        if nums:
            total = "Rp " + f"{max(map(int, nums)):,}".replace(",", ".")

    return nama_toko, tanggal, telepon, total

# ======================================================
# INPUT IMAGE
# ======================================================
tab1, tab2 = st.tabs(["📂 Upload", "📷 Kamera"])
image = None

with tab1:
    uploaded = st.file_uploader("Upload gambar", type=["png","jpg","jpeg"])
    if uploaded:
        image = Image.open(uploaded).convert("RGB")

with tab2:
    cam = st.camera_input("Ambil foto")
    if cam:
        image = Image.open(cam).convert("RGB")

# ======================================================
# CROP + OCR
# ======================================================
if image:
    st.image(image, caption="Preview Gambar", use_container_width=True)

    st.subheader("✂ Crop Gambar")
    w, h = image.size
    x1 = st.slider("X Awal", 0, w-1, 0)
    x2 = st.slider("X Akhir", 1, w, w)
    y1 = st.slider("Y Awal", 0, h-1, 0)
    y2 = st.slider("Y Akhir", 1, h, h)

    cropped = image.crop((x1, y1, x2, y2))
    st.image(cropped, caption="Hasil Crop", use_container_width=True)

    if st.button("🔍 Proses OCR"):
        with st.spinner("Membaca teks..."):
            reader = easyocr.Reader(lang_map[ocr_lang], gpu=False)
            result = reader.readtext(np.array(cropped), detail=0)
            st.session_state.ocr_text = "\n".join(result)
            st.success("OCR berhasil!")

# ======================================================
# EDITOR
# ======================================================
if st.session_state.ocr_text:
    st.subheader("✏ Edit Teks")

    st.session_state.judul = st.text_input("Judul", st.session_state.judul)
    st.session_state.tanggal = st.text_input("Tanggal", st.session_state.tanggal)
    st.session_state.alamat = st.text_input("Alamat", st.session_state.alamat)

    edited = st.text_area(
        "Isi teks OCR:",
        st.session_state.ocr_text,
        height=250
    )
    st.session_state.ocr_text = edited

    # ======================================================
    # SMART EXTRACT (STRUK ONLY)
    # ======================================================
    if mode == "Struk":
        nama_toko, tanggal_auto, telepon, total = smart_extract(edited)

        st.subheader("📊 Ringkasan Otomatis (Smart Extract)")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🏪 Nama Toko: {nama_toko}")
            st.info(f"📅 Tanggal: {tanggal_auto}")
        with col2:
            st.info(f"📞 Telepon: {telepon}")
            st.info(f"💰 Total Harga: {total}")

    # ======================================================
    # FINAL TEXT
    # ======================================================
    if mode == "Surat":
        final_text = f"""
{st.session_state.judul}

Tanggal : {st.session_state.tanggal}
Alamat  : {st.session_state.alamat}

{edited}
"""
    else:
        final_text = f"""
{st.session_state.judul}

Tanggal : {st.session_state.tanggal}
Alamat  : {st.session_state.alamat}

{edited}
"""

    st.subheader("📄 Hasil Final")
    st.text_area("Teks Final:", final_text, height=300)

    # ======================================================
    # SAVE HISTORY
    # ======================================================
    if st.button("💾 Simpan ke Riwayat"):
        st.session_state.history.append({
            "time": datetime.now().strftime("%d %b %H:%M"),
            "mode": mode,
            "judul": st.session_state.judul,
            "tanggal": st.session_state.tanggal,
            "alamat": st.session_state.alamat,
            "text": edited
        })
        st.success("Disimpan ke Riwayat!")

    # ======================================================
    # EXPORT TXT
    # ======================================================
    st.download_button(
        "⬇ Download TXT",
        final_text,
        file_name="hasil_ocr.txt"
    )

    # ======================================================
    # EXPORT PDF
    # ======================================================
    def create_pdf(text):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        textobject = c.beginText(40, 800)
        for line in text.split("\n"):
            textobject.textLine(line)
        c.drawText(textobject)
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    pdf = create_pdf(final_text)
    st.download_button(
        "⬇ Download PDF",
        pdf,
        file_name="hasil_ocr.pdf",
        mime="application/pdf"
    )

    # ======================================================
    # EXPORT WORD
    # ======================================================
    def create_word(text):
        doc = Document()
        for line in text.split("\n"):
            doc.add_paragraph(line)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    word = create_word(final_text)
    st.download_button(
        "📑 Download Word (.docx)",
        word,
        file_name="hasil_ocr.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
