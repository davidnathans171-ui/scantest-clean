import streamlit as st
from PIL import Image
import numpy as np
import easyocr
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

# ================= CONFIG =================
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
    .stApp {{ background-color:{bg}; color:{text}; }}
    textarea, input, .stButton>button {{
        background-color:{card};
        color:{text};
        border-radius:8px;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme(theme)

# ================= TITLE =================
st.title("📄 ScanText Pro – OCR + Editor + PDF")
st.success("Upload • Kamera • Crop • OCR • Edit • Mode Surat • TXT • PDF • Tema UI")

# ================= MODE =================
mode = st.selectbox("Pilih Mode Output:", ["Struk", "Surat"])

# ================= IMAGE INPUT =================
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

# ================= CROP =================
if image:
    st.subheader("✂ Crop Gambar")
    w, h = image.size
    x1 = st.slider("X awal", 0, w-1, 0)
    x2 = st.slider("X akhir", 1, w, w)
    y1 = st.slider("Y awal", 0, h-1, 0)
    y2 = st.slider("Y akhir", 1, h, h)

    cropped = image.crop((x1, y1, x2, y2))
    st.image(cropped, caption="Hasil Crop", use_container_width=True)

    # ================= OCR =================
    if st.button("🔍 Proses OCR"):
        with st.spinner("Membaca teks..."):
            reader = easyocr.Reader(["en","id"])
            result = reader.readtext(np.array(cropped), detail=0)
            ocr_text = "\n".join(result)
            st.session_state["ocr_text"] = ocr_text

# ================= EDIT TEXT =================
if "ocr_text" in st.session_state:
    st.subheader("✏ Edit Teks OCR")
    edited = st.text_area("Edit teks:", st.session_state["ocr_text"], height=250)

    judul = st.text_input("Judul", "HASIL OCR")
    tanggal = st.text_input("Tanggal", datetime.now().strftime("%d %B %Y"))
    alamat = st.text_input("Alamat", "Isi alamat di sini")

    if mode == "Surat":
        final_text = f"""
{judul}

Tanggal : {tanggal}
Alamat  : {alamat}

{edited}
"""
    else:
        final_text = f"""
{judul}
Tanggal : {tanggal}
Alamat  : {alamat}

{edited}
"""

    st.subheader("📄 Hasil Final")
    st.text_area("Teks Final:", final_text, height=250)

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
