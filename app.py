import streamlit as st
from PIL import Image
import easyocr
import numpy as np
from streamlit_image_crop import image_cropper
from datetime import date

st.set_page_config(page_title="ScanText Pro - OCR + Editor", layout="centered")

# ------------------ DARK MODE ------------------
dark = st.toggle("🌙 Dark Mode")

if dark:
    st.markdown("""
        <style>
        body { background-color: #121212; color: white; }
        textarea, input { background-color: #1f1f1f !important; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.title("📄 ScanText Pro – OCR + Editor")
st.success("OCR stabil + bisa diedit + kamera + crop + dark mode tersedia")

# ------------------ OCR INIT ------------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['id', 'en'], gpu=False)

reader = load_reader()

# ------------------ IMAGE INPUT ------------------
st.subheader("📸 Upload / Ambil Gambar")
img_source = st.radio("Sumber gambar:", ["Upload File", "Kamera"])

image = None

if img_source == "Upload File":
    uploaded = st.file_uploader("Upload gambar (PNG, JPG, JPEG)", ["png", "jpg", "jpeg"])
    if uploaded:
        image = Image.open(uploaded)

elif img_source == "Kamera":
    camera = st.camera_input("Ambil gambar dari kamera")
    if camera:
        image = Image.open(camera)

if image:
    st.image(image, caption="Gambar Asli", use_container_width=True)

    # ------------------ CROP ------------------
    st.subheader("✂️ Crop Gambar")
    cropped = image_cropper(image, realtime_update=True, box_color="blue", aspect_ratio=None)
    st.image(cropped, caption="Hasil Crop", use_container_width=True)

    # ------------------ OCR BUTTON ------------------
    if st.button("🔍 Proses OCR"):
        with st.spinner("Memproses OCR..."):
            img_np = np.array(cropped)
            result = reader.readtext(img_np)

            ocr_text = "\n".join([r[1] for r in result])
            st.session_state["ocr_text"] = ocr_text

# ------------------ EDIT AREA ------------------
if "ocr_text" in st.session_state:

    st.subheader("📝 Edit Informasi")

    judul = st.text_input("Judul", "HASIL OCR")
    tanggal = st.date_input("Tanggal", value=date.today())
    alamat = st.text_input("Alamat", "Isi alamat di sini")

    st.subheader("✍️ Edit isi teks OCR:")
    edited_text = st.text_area(
        "Teks OCR",
        value=st.session_state["ocr_text"],
        height=250
    )

    # ------------------ FINAL RESULT ------------------
    st.subheader("📄 Hasil Final")

    final_text = f"""
{judul}

Tanggal : {tanggal.strftime("%d %B %Y")}
Alamat  : {alamat}

{edited_text}
"""

    st.text_area("Teks Final (siap disalin atau download)", final_text, height=300)

    st.download_button(
        "⬇️ Download TXT",
        data=final_text,
        file_name="hasil_ocr.txt",
        mime="text/plain"
    )
