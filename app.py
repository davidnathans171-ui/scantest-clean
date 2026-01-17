import streamlit as st
from PIL import Image
import numpy as np
import easyocr
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(page_title="ScanText Pro", layout="centered")

# ================= THEME =================
theme = st.selectbox(
    "🎨 Pilih Tema UI",
    ["Light", "Dark", "Blue", "Green", "Minimalist"]
)

def apply_theme(theme):
    if theme == "Dark":
        bg, text, card = "#0E1117", "white", "#262730"
    elif theme == "Blue":
        bg, text, card = "#0A1F44", "white", "#102A56"
    elif theme == "Green":
        bg, text, card = "#0F2E1F", "white", "#1B4D3A"
    elif theme == "Minimalist":
        bg, text, card = "#FFFFFF", "#111111", "#F2F2F2"
    else:
        bg, text, card = "#F5F7FA", "#000000", "#FFFFFF"

    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg};
        color: {text};
    }}
    textarea, input, .stButton>button {{
        background-color: {card};
        color: {text};
        border-radius: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme(theme)

# ================= SESSION STATE =================
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "judul" not in st.session_state:
    st.session_state.judul = "HASIL OCR"
if "tanggal" not in st.session_state:
    st.session_state.tanggal = datetime.now().strftime("%d %B %Y")
if "alamat" not in st.session_state:
    st.session_state.alamat = ""

# ================= SIDEBAR HISTORY =================
st.sidebar.title("📚 Riwayat Scan")

if len(st.session_state.history) == 0:
    st.sidebar.info("Belum ada riwayat scan.")
else:
    for i, item in enumerate(reversed(st.session_state.history)):
        label = f"[{len(st.session_state.history)-i}] {item['time']} - {item['mode']}"
        if st.sidebar.button(label):
            st.session_state.ocr_text = item["text"]
            st.session_state.judul = item["judul"]
            st.session_state.tanggal = item["tanggal"]
            st.session_state.alamat = item["alamat"]
            st.success("Riwayat berhasil dimuat!")

# ================= TITLE =================
st.title("📄 ScanText Pro")
st.success("Upload • Kamera • Crop • OCR • Edit • Mode Surat • TXT • PDF • Tema UI • History")

# ================= MODE =================
mode = st.selectbox("Pilih Mode Output:", ["Struk", "Surat"])

# ================= IMAGE INPUT =================
tab1, tab2 = st.tabs(["📁 Upload", "📷 Kamera"])
image = None

with tab1:
    uploaded = st.file_uploader("Upload gambar", type=["png", "jpg", "jpeg"])
    if uploaded:
        image = Image.open(uploaded).convert("RGB")

with tab2:
    cam = st.camera_input("Ambil foto")
    if cam:
        image = Image.open(cam).convert("RGB")

# ================= CROP =================
if image:
    st.subheader("✂ Crop Gambar")
    w, h = image.size
    x1 = st.slider("X awal", 0, w-1, 0)
    x2 = st.slider("X akhir", 1, w, w)
    y1 = st.slider("Y awal", 0, h-1, 0)
    y2 = st.slider("Y akhir", 1, h, h)

    cropped = image.crop((x1, y1, x2, y2))
    st.image(cropped, caption="Hasil Crop", use_column_width=True)

    if st.button("🔍 Proses OCR"):
        with st.spinner("Membaca teks..."):
            reader = easyocr.Reader(["en", "id"], gpu=False)
            result = reader.readtext(np.array(cropped), detail=0)
            text = "\n".join(result)
            st.session_state.ocr_text = text
            st.success("OCR berhasil!")

# ================= EDIT =================
if st.session_state.ocr_text:
    st.subheader("✏ Edit Teks")

    st.session_state.judul = st.text_input("Judul", st.session_state.judul)
    st.session_state.tanggal = st.text_input("Tanggal", st.session_state.tanggal)
    st.session_state.alamat = st.text_input("Alamat", st.session_state.alamat)

    edited = st.text_area(
        "Edit isi teks OCR:",
        st.session_state.ocr_text,
        height=250
    )

    st.session_state.ocr_text = edited

    if mode == "Surat":
        final_text = f"""
{st.session_state.judul}

Tanggal : {st.session_state.tanggal}
Alamat  : {st.session_state.alamat}

Dengan hormat,

{edited}

Hormat kami,
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

    # ================= SAVE TO HISTORY =================
    if st.button("💾 Simpan ke Riwayat"):
        st.session_state.history.append({
            "time": datetime.now().strftime("%d %b %H:%M"),
            "mode": mode,
            "judul": st.session_state.judul,
            "tanggal": st.session_state.tanggal,
            "alamat": st.session_state.alamat,
            "text": edited
        })
        st.success("Disimpan ke riwayat!")

    # ================= DOWNLOAD TXT =================
    st.download_button(
        "⬇ Download TXT",
        final_text,
        file_name="hasil_ocr.txt"
    )

    # ================= DOWNLOAD PDF =================
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
