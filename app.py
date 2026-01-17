import streamlit as st
from PIL import Image
import easyocr
import numpy as np
from streamlit_cropper import st_cropper
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

st.set_page_config(page_title="ScanText Pro", layout="centered")
# ===== DARK MODE TOGGLE =====
dark_mode = st.toggle("🌙 Dark Mode")

if dark_mode:
    st.markdown("""
        <style>
        body {
            background-color: #0E1117;
            color: white;
        }
        .stTextInput input, .stTextArea textarea {
            background-color: #262730;
            color: white;
        }
        .stSelectbox, .stButton>button {
            background-color: #262730;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)


st.title("📄 ScanText Pro – OCR + Editor + Crop")
st.success("OCR stabil • Bisa diedit • Bisa crop • Bisa export PDF")

# MODE PILIHAN
mode = st.selectbox("Pilih Mode Output:", ["Struk", "Surat"])

st.subheader("📸 Ambil gambar dari Upload atau Kamera")

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

# ================== CROP ==================
if image:
    st.subheader("✂️ Crop Gambar (Opsional)")
    cropped_img = st_cropper(
        image,
        realtime_update=True,
        box_color="#00ff00",
        aspect_ratio=None
    )

    st.image(cropped_img, caption="Hasil setelah crop", use_container_width=True)

    if st.button("🔍 Proses OCR"):
        with st.spinner("Sedang memproses OCR..."):
            reader = easyocr.Reader(['en', 'id'], gpu=False)
            result = reader.readtext(np.array(cropped_img), detail=0)
            ocr_text = "\n".join(result)
            st.session_state["ocr"] = ocr_text

# ================== EDIT TEXT ==================
if "ocr" in st.session_state:
    st.subheader("✏️ Edit hasil OCR")

    judul = st.text_input("Judul", "HASIL OCR")
    tanggal = st.text_input("Tanggal", "")
    alamat = st.text_input("Alamat", "")

    edited_text = st.text_area(
        "Edit isi teks OCR:",
        value=st.session_state["ocr"],
        height=250
    )

    final_text = f"""
{judul}

Tanggal : {tanggal}
Alamat  : {alamat}

{edited_text}
"""

    st.subheader("📑 Hasil Final")
    st.text_area("Teks Final:", final_text, height=250)

    # DOWNLOAD TXT
    st.download_button(
        "⬇️ Download TXT",
        final_text,
        file_name="hasil_ocr.txt",
        mime="text/plain"
    )

    # ================= PDF EXPORT =================
    def generate_pdf(text):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        textobject = c.beginText(40, 800)
        for line in text.split("\n"):
            textobject.textLine(line)
        c.drawText(textobject)
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    pdf_file = generate_pdf(final_text)

    st.download_button(
        "📄 Download sebagai PDF",
        pdf_file,
        file_name="hasil_ocr.pdf",
        mime="application/pdf"
    )
