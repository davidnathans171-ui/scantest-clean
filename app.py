import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import datetime

st.set_page_config(page_title="ScanText Pro – OCR + Editor", layout="centered")

# =====================
# Dark Mode
# =====================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark

if dark:
    st.markdown("""
    <style>
    body {background-color: #0E1117; color: white;}
    textarea, input {background-color:#262730 !important; color:white !important;}
    </style>
    """, unsafe_allow_html=True)

# =====================
# Title
# =====================
st.title("📄 ScanText Pro – OCR + Editor")
st.success("OCR stabil + bisa diedit + kamera + dark mode")

# =====================
# Load OCR
# =====================
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en', 'id'], gpu=False)

reader = load_reader()

# =====================
# Upload / Camera
# =====================
st.subheader("📷 Ambil dari Kamera atau Upload Gambar")

camera_image = st.camera_input("Gunakan kamera")
uploaded_file = st.file_uploader(
    "Atau upload gambar (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"]
)

image = None
if camera_image:
    image = Image.open(camera_image)
elif uploaded_file:
    image = Image.open(uploaded_file)

if image:
    st.image(image, caption="Preview Gambar", use_container_width=True)

    if st.button("🚀 Proses OCR"):
        with st.spinner("Memproses OCR..."):
            img_np = np.array(image)
            result = reader.readtext(img_np)
            text = "\n".join([r[1] for r in result])

            st.session_state.ocr_text = text
            st.session_state.show_editor = True

# =====================
# Session Defaults
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

    st.subheader("✏️ Edit Judul, Tanggal, Alamat")
    st.session_state.judul = st.text_input("Judul", st.session_state.judul)
    st.session_state.tanggal = st.text_input("Tanggal", st.session_state.tanggal)
    st.session_state.alamat = st.text_input("Alamat", st.session_state.alamat)

    st.subheader("📝 Edit Teks OCR")
    st.session_state.ocr_text = st.text_area(
        "Edit isi teks OCR:",
        value=st.session_state.ocr_text,
        height=250
    )

    final_text = f"""
{st.session_state.judul}

Tanggal : {st.session_state.tanggal}
Alamat  : {st.session_state.alamat}

{st.session_state.ocr_text}
""".strip()

    st.subheader("📄 Hasil Final (Bisa Diedit)")
    st.session_state.final_text = st.text_area(
        "Teks Final:",
        value=final_text,
        height=300
    )

    st.download_button(
        "⬇️ Download TXT",
        st.session_state.final_text,
        file_name="hasil_ocr.txt"
    )
