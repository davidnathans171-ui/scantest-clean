import streamlit as st
from PIL import Image

# =============================
# KONFIGURASI HALAMAN
# =============================
st.set_page_config(
    page_title="ScanText Pro - Upload Mode",
    layout="centered"
)

st.title("📷 ScanText Pro - Upload Gambar")
st.success("Mode awal: Upload & preview gambar (tanpa OCR).")

st.write(
    "Kalau gambar bisa muncul dengan benar di sini, berarti aplikasi sudah 100% stabil. "
    "OCR baru akan kita tambahkan setelah ini aman."
)

# =============================
# UPLOAD GAMBAR
# =============================
uploaded_file = st.file_uploader(
    "Upload gambar (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"]
)

# =============================
# PREVIEW GAMBAR
# =============================
if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview gambar yang diupload", use_container_width=True)
        st.success("Gambar berhasil diupload dan ditampilkan.")
    except Exception as e:
        st.error("Gagal membaca gambar.")
        st.code(str(e))
else:
    st.info("Silakan upload satu gambar untuk melihat preview.")
