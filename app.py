import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import datetime

# =====================
# Page Config
# =====================
st.set_page_config(page_title="ScanText Pro – OCR + Editor", layout="centered")

# =====================
# Dark Mode Toggle
# =====================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark

if dark:
    st.markdown(
        """
        <style>
        body {background-color: #0E1117; color: white;}
        textarea, input {background-color:#262730 !important; color:white !important;}
        </style>
        """,
        unsafe_allow_html=True
    )

# =====================
# Title
# =====================
st.title("📄 ScanText Pro – OCR + Editor")
st.success("OCR stabil + bisa diedit + mode gelap tersedia")

# =====================
# Load OCR
# =====================
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en', 'id'], gpu=False)

reader = load_reader()

# =====================
# Upload Image
# =====================
uploaded_file = st.file_uploader(
    "📷 Upload gambar (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Preview Gambar", use_container_width=True)

    if st.button("🚀 Proses OCR"):
        with st.spinner("Memproses OCR..."):
            img_np = np.array(image)
            result = reader.readtext(img_np)

            text = "\n".join([r[1] for r in result])

            st.session_state.ocr_text = text
            st.session_state.show_editor = True

# =====================
# Default Session
# =====================
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""

if "show_editor" not in st.session_state:
    st.session_state.show_editor = False

if "judul" not in st.session_state:
    st.session_state.judul = "HASIL OCR"

if "tanggal" not in st.session_state:
    st.session_state.tanggal = datetime.date.today().strftime("%d %B %Y")

if "alamat" not in st.session_state:
    st.session_state.alamat = "Isi alamat di sini"

if "final_text" not in st.session_state:
    st.session_state.final_text = ""

# =====================
# EDITOR
# =====================
if st.session_state.show_editor:

    st.subheader("✏️ Edit Metadata")

    st.session_state.judul = st.text_input("Judul", st.session_state.judul)
    st.session_state.tanggal = st.text_input("Tanggal", st.session_state.tanggal)
    st.session_state.alamat = st.text_input("Alamat", st.session_state.alamat)

    st.subheader("📝 Edit Isi Teks OCR")
    st.session_state.ocr_text = st.text_area(
        "Edit isi teks OCR:",
        value=st.session_state.ocr_text,
        height=250
    )

    # =====================
    # Final Text Builder
    # =====================
    final_text = f"""
{st.session_state.judul}

Tanggal : {st.session_state.tanggal}
Alamat  : {st.session_state.alamat}

{st.session_state.ocr_text}
""".strip()

    st.session_state.final_text = final_text

    st.subheader("📄 Hasil Final (Bisa Diedit Langsung)")
    st.session_state.final_text = st.text_area(
        "Teks Final:",
        value=st.session_state.final_text,
        height=300
    )

    st.download_button(
        "⬇️ Download sebagai TXT",
        st.session_state.final_text,
        file_name="hasil_ocr.txt"
    )
