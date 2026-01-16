import streamlit as st
from PIL import Image
import easyocr
import numpy as np

st.set_page_config(page_title="ScanText Pro - OCR + Editor", layout="centered")

st.title("ScanText Pro – OCR + Editor")
st.success("OCR stabil + hasil tidak hilang walau scroll atau klik.")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en', 'id'], gpu=False)

reader = load_reader()

# Simpan hasil di session_state agar tidak hilang saat scroll
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""
if "show_editor" not in st.session_state:
    st.session_state.show_editor = False

uploaded_file = st.file_uploader(
    "Upload gambar (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Preview Gambar", use_container_width=True)

    if st.button("🔍 Proses OCR"):
        with st.spinner("Sedang memproses OCR..."):
            img_np = np.array(image)
            result = reader.readtext(img_np)

            text = ""
            for r in result:
                text += r[1] + "\n"

            st.session_state.ocr_text = text
            st.session_state.show_editor = True
            st.success("OCR berhasil! Sekarang kamu bisa mengedit.")

# ===============================
# MODE EDIT (MUNCUL SETELAH OCR)
# ===============================
if st.session_state.show_editor:

    st.subheader("📝 Edit Data Dokumen")

    judul = st.text_input("Judul Dokumen", "Surat Resmi")
    tanggal = st.text_input("Tanggal", "16 Januari 2026")
    alamat = st.text_input("Alamat", "Jl. Contoh No. 123, Jakarta")

    edited_text = st.text_area(
        "Hasil OCR (Bisa Diedit)",
        value=st.session_state.ocr_text,
        height=300
    )

    final_text = f"""
{judul}

Tanggal : {tanggal}
Alamat  : {alamat}

{edited_text}
"""

    st.subheader("📄 Hasil Final")
    st.text_area("Teks Final (Siap Disimpan)", final_text, height=300)

    st.download_button(
        label="⬇ Download sebagai TXT",
        data=final_text,
        file_name="hasil_ocr_edit.txt",
        mime="text/plain"
    )
