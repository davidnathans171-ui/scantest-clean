import streamlit as st
from PIL import Image
import easyocr
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

st.set_page_config(page_title="ScanText Pro", layout="centered")

st.title("📄 ScanText Pro – OCR + PDF Export")
st.success("OCR stabil + teks bisa diedit + export PDF")

# MODE
mode = st.selectbox("Pilih Mode Output:", ["Struk", "Surat"])

# INPUT GAMBAR
st.subheader("📷 Ambil dari Kamera atau Upload Gambar")
tab1, tab2 = st.tabs(["📁 Upload File", "📸 Kamera"])

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

# OCR
if image:
    st.image(image, caption="Preview gambar", use_container_width=True)

    if "reader" not in st.session_state:
        st.session_state.reader = easyocr.Reader(["en", "id"], gpu=False)

    if st.button("🔍 Proses OCR"):
        with st.spinner("Sedang membaca teks..."):
            result = st.session_state.reader.readtext(np.array(image), detail=0)
            ocr_text = "\n".join(result)
            st.session_state.ocr_text = ocr_text

# EDIT TEXT
if "ocr_text" in st.session_state:
    st.subheader("✏️ Edit isi teks OCR")
    edited_text = st.text_area(
        "Teks hasil OCR (bisa diedit):",
        value=st.session_state.ocr_text,
        height=300
    )

    # Metadata
    st.subheader("📝 Informasi Tambahan")
    judul = st.text_input("Judul", "HASIL OCR")
    tanggal = st.text_input("Tanggal", "Isi tanggal di sini")
    alamat = st.text_input("Alamat", "Isi alamat di sini")

    final_text = f"""{judul}

Tanggal : {tanggal}
Alamat  : {alamat}

{edited_text}
"""

    st.subheader("📄 Hasil Final")
    st.text_area("Teks Final:", final_text, height=300)

    # DOWNLOAD TXT
    st.download_button(
        "⬇️ Download TXT",
        data=final_text,
        file_name="hasil_ocr.txt",
        mime="text/plain"
    )

    # ===== EXPORT PDF =====
    def generate_pdf(text):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        x = 2 * cm
        y = height - 2 * cm

        for line in text.split("\n"):
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm
            c.drawString(x, y, line)
            y -= 14

        c.save()
        buffer.seek(0)
        return buffer

    pdf_file = generate_pdf(final_text)

    st.download_button(
        "📄 Download sebagai PDF",
        data=pdf_file,
        file_name="hasil_ocr.pdf",
        mime="application/pdf"
    )
