import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import io
import datetime

# =============================
# Konfigurasi Halaman
# =============================
st.set_page_config(
    page_title="ScanText Pro - OCR + Editor",
    layout="centered"
)

# =============================
# Dark Mode Toggle
# =============================
dark_mode = st.toggle("🌙 Dark Mode")

if dark_mode:
    st.markdown(
        """
        <style>
        body {
            background-color: #0e1117;
            color: white;
        }
        textarea, input {
            background-color: #262730 !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# =============================
# Judul
# =============================
st.title("📄 ScanText Pro – OCR + Editor")
st.success("OCR stabil + bisa diedit + mode gelap tersedia")

# =============================
# Load EasyOCR
# =============================
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en', 'id'], gpu=False)

reader = load_reader()

# =============================
# Upload Gambar / Kamera
# =============================
st.subheader("📷 Upload atau Ambil Gambar")

option = st.radio("Pilih sumber gambar:", ["Upload Gambar", "Kamera"])

uploaded_file = None
image = None

if option == "Upload Gambar":
    uploaded_file = st.file_uploader(
        "Upload gambar (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"]
    )
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview gambar", use_container_width=True)

elif option == "Kamera":
    camera_image = st.camera_input("Ambil foto langsung")
    if camera_image:
        image = Image.open(camera_image)
        st.image(image, caption="Foto dari kamera", use_container_width=True)

# =============================
# Proses OCR
# =============================
if image is not None:
    if st.button("🚀 Proses OCR"):
        with st.spinner("Sedang memproses OCR..."):
            try:
                img_np = np.array(image)
                result = reader.readtext(img_np)

                ocr_text = ""
                for r in result:
                    ocr_text += r[1] + "\n"

                if ocr_text.strip() == "":
                    st.warning("Tidak ada teks terdeteksi.")
                else:
                    st.session_state["ocr_result"] = ocr_text
                    st.success("OCR berhasil!")

            except Exception as e:
                st.error("Terjadi error saat OCR:")
                st.code(str(e))

# =============================
# Editor Teks
# =============================
if "ocr_result" in st.session_state:
    st.subheader("✏️ Edit Data Utama")

    judul = st.text_input("Judul", value="HASIL OCR")
    tanggal = st.text_input(
        "Tanggal",
        value=datetime.date.today().strftime("%d %B %Y")
    )
    alamat = st.text_input("Alamat", value="Isi alamat di sini")

    st.subheader("📝 Edit isi teks OCR:")
    edited_text = st.text_area(
        "Edit teks di bawah ini:",
        st.session_state["ocr_result"],
        height=250
    )

    # =============================
    # Hasil Final
    # =============================
    st.subheader("📄 Hasil Final")

    final_text = f"""
{judul}

Tanggal : {tanggal}
Alamat  : {alamat}

{edited_text}
"""

    st.text_area(
        "Teks Final (siap disalin atau download):",
        final_text,
        height=300
    )

    st.download_button(
        "⬇️ Download sebagai TXT",
        data=final_text,
        file_name="hasil_ocr.txt",
        mime="text/plain"
    )
