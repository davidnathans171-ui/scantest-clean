import streamlit as st
from PIL import Image
import numpy as np
import easyocr
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from docx import Document
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(page_title="ScanText Pro Ultimate", layout="centered")

# ================= THEME =================
theme = st.sidebar.selectbox(
    "🎨 Pilih Tema UI",
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
        bg, text, card = "#FFFFFF", "#333333", "#F4F4F4"
    else:
        bg, text, card = "white", "black", "#F0F2F6"

    st.markdown(f"""
        <style>
        body {{
            background-color: {bg};
            color: {text};
        }}
        textarea, input, select {{
            background-color: {card};
            color: {text};
        }}
        </style>
    """, unsafe_allow_html=True)

apply_theme(theme)

# ================= SIDEBAR =================
st.sidebar.title("📜 Riwayat Scan")
if "history" not in st.session_state:
    st.session_state.history = []

# ================= TITLE =================
st.title("📄 ScanText Pro – OCR Ultimate")
st.success("OCR + Camera + Crop + Edit + PDF + Word + Multi Bahasa + Tema UI")

# ================= MODE =================
mode = st.selectbox("Pilih Mode:", ["Struk", "Surat"])

# ================= OCR LANGUAGE =================
lang = st.selectbox(
    "🌐 Bahasa OCR:",
    {
        "Indonesia": ["id", "en"],
        "English": ["en"],
        "Japanese": ["ja", "en"],
        "Arabic": ["ar", "en"]
    }.keys()
)

lang_map = {
    "Indonesia": ["id", "en"],
    "English": ["en"],
    "Japanese": ["ja", "en"],
    "Arabic": ["ar", "en"]
}

# ================= IMAGE INPUT =================
st.subheader("📷 Upload atau Kamera")

tab1, tab2 = st.tabs(["Upload", "Kamera"])
image = None

with tab1:
    file = st.file_uploader("Upload gambar", type=["png", "jpg", "jpeg"])
    if file:
        image = Image.open(file).convert("RGB")

with tab2:
    cam = st.camera_input("Ambil foto")
    if cam:
        image = Image.open(cam).convert("RGB")

if image:
    st.image(image, caption="Preview", use_container_width=True)

    # ================= OCR =================
    reader = easyocr.Reader(lang_map[lang], gpu=False)
    result = reader.readtext(np.array(image), detail=0)
    ocr_text = "\n".join(result)

    st.subheader("✏ Edit Hasil OCR")
    edited_text = st.text_area("Edit teks OCR:", ocr_text, height=250)

    # ================= MODE OUTPUT =================
    st.subheader("📄 Hasil Final")
    if mode == "Struk":
        final_text = f"HASIL OCR STRUK\n\n{edited_text}"
    else:
        final_text = f"SURAT RESMI\nTanggal: {datetime.now().strftime('%d %B %Y')}\n\n{edited_text}"

    st.text_area("Teks Final:", final_text, height=250)

    # ================= SAVE HISTORY =================
    st.session_state.history.append(final_text)

    # ================= EXPORT TXT =================
    st.download_button(
        "⬇ Download TXT",
        final_text,
        file_name="hasil_ocr.txt"
    )

    # ================= EXPORT PDF =================
    def create_pdf(text):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        textobj = c.beginText(40, 800)
        for line in text.split("\n"):
            textobj.textLine(line)
        c.drawText(textobj)
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

    # ================= EXPORT WORD =================
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
        "⬇ Download Word (.docx)",
        word,
        file_name="hasil_ocr.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# ================= SHOW HISTORY =================
st.sidebar.subheader("Riwayat:")
for i, h in enumerate(st.session_state.history[::-1][:5]):
    st.sidebar.text(f"{i+1}. {h[:30]}...")
