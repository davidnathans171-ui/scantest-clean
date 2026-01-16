import streamlit as st
from PIL import Image
import easyocr
import numpy as np

st.set_page_config(page_title="ScanText Pro – OCR + Editor + Camera", layout="centered")

# --------------------
# DARK MODE TOGGLE
# --------------------
dark_mode = st.toggle("🌙 Dark Mode")

if dark_mode:
    st.markdown("""
        <style>
        body { background-color: #0e1117; color: white; }
        .stTextArea textarea { background-color: #1e1e1e; color: white; }
        .stTextInput input { background-color: #1e1e1e; color: white; }
        </style>
    """, unsafe_allow_html=True)

# --------------------
# TITLE
# --------------------
st.title("ScanText Pro – OCR + Editor + Kamera")
st.success("OCR stabil + bisa diedit + mode gelap + kamera aktif")

# --------------------
# LOAD OCR
# --------------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en', 'id'], gpu=False)

reader = load_reader()

# --------------------
# INPUT MODE
# --------------------
mode = st.radio(
    "Pilih sumber gambar:",
    ["Upload Gambar", "Kamera"]
)

image = None

if mode == "Upload Gambar":
    uploaded_file = st.file_uploader(
        "Upload gambar (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"]
    )
    if uploaded_file:
        image = Image.open(uploaded_file)

elif mode == "Kamera":
    camera_image = st.camera_input("Ambil foto langsung")
    if camera_image:
        image = Image.open(camera_image)

# --------------------
# PREVIEW
# --------------------
if image:
    st.image(image, caption="Preview gambar", use_container_width=True)

    if st.button("📄 Proses OCR"):
        with st.spinner("Sedang memproses OCR..."):
            try:
                img_np = np.array(image)
                result = reader.readtext(img_np)

                raw_text = ""
                for r in result:
                    raw_text += r[1] + "\n"

                st.subheader("✏️ Edit Data")

                judul = st.text_input("Judul", "HASIL OCR")
                tanggal = st.text_input("Tanggal", "16 Januari 2026")
                alamat = st.text_input("Alamat", "Isi alamat di sini")

                edited_text = st.text_area("Edit isi teks OCR:", raw_text, height=250)

                final_text = f"""
{judul}

Tanggal : {tanggal}
Alamat  : {alamat}

{edited_text}
"""

                st.subheader("📄 Hasil Final")
                st.text_area("Teks Final (siap disalin atau download):", final_text, height=300)

                st.download_button(
                    "⬇️ Download sebagai TXT",
                    final_text,
                    file_name="hasil_ocr.txt"
                )

                st.success("OCR + Edit berhasil!")

            except Exception as e:
                st.error("Terjadi error saat OCR:")
                st.code(str(e))
