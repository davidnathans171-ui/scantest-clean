import streamlit as st
from PIL import Image

st.set_page_config(page_title="ScanText Pro - Upload Mode", layout="centered")

st.title("ScanText Pro")
st.subheader("Mode: Upload Gambar (Tanpa OCR)")
st.success("Fitur upload gambar aktif dan stabil.")

uploaded_file = st.file_uploader(
    "Upload gambar (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview Gambar", use_container_width=True)
        st.success("Gambar berhasil diupload dan ditampilkan.")
    except Exception as e:
        st.error("Gagal membuka gambar.")
        st.code(str(e))
else:
    st.info("Silakan upload gambar untuk melihat preview.")
