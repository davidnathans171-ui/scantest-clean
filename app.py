import streamlit as st
from PIL import Image

st.set_page_config(page_title="ScanText Pro - Image Upload", layout="centered")

st.title("ScanText Pro – Upload Gambar")
st.info("Mode ini hanya untuk upload dan preview gambar (OCR belum dipakai).")

uploaded_file = st.file_uploader(
    "Upload gambar (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Preview Gambar", use_container_width=True)
    st.success("Gambar berhasil diupload!")
