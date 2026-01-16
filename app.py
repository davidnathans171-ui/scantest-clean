import streamlit as st
from PIL import Image
import easyocr
import numpy as np

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="ScanText Pro - OCR MODE",
    layout="centered"
)

st.title("ScanText Pro – OCR MODE")
st.success("OCR aktif menggunakan EasyOCR (stabil untuk Streamlit Cloud)")

# =========================
# LOAD OCR READER (CACHE)
# =========================
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en', 'id'], gpu=False)

reader = load_reader()

# =========================
# UPLOAD GAMBAR
# =========================
uploaded_file = st.file_uploader(
    "📤 Upload gambar (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Preview gambar", use_container_width=True)

    if st.button("🚀 Proses OCR"):
        with st.spinner("Sedang memproses OCR..."):
            try:
                img_np = np.array(image)
                result = reader.readtext(img_np)

                text = ""
                for r in result:
                    text += r[1] + "\n"

                if text.strip() == "":
                    st.warning("Tidak ada teks terdeteksi.")
                else:
                    st.success("OCR berhasil! Silakan edit teks di bawah.")

                    # =========================
                    # FORM EDIT JUDUL, TANGGAL, ALAMAT
                    # =========================
                    st.subheader("✏️ Edit Informasi Struk")

                    judul = st.text_input("📝 Judul", "STRUK PEMBELIAN")
                    tanggal = st.text_input("📅 Tanggal", "16/01/2026")
                    alamat = st.text_input("📍 Alamat", "Toko Contoh, Jakarta")

                    # =========================
                    # EDIT HASIL OCR
                    # =========================
                    edited_text = st.text_area(
                        "🖊 Edit teks hasil OCR:",
                        value=text,
                        height=300
                    )

                    # =========================
                    # GABUNGKAN HASIL AKHIR
                    # =========================
                    final_text = f"""
{judul}

Tanggal : {tanggal}
Alamat  : {alamat}

{edited_text}
"""

                    st.subheader("📄 Hasil Final (Siap disalin / download)")
                    st.text_area("Teks Final:", final_text, height=300)

                    st.download_button(
                        "⬇ Download sebagai TXT",
                        final_text,
                        file_name="hasil_ocr.txt",
                        mime="text/plain"
                    )

            except Exception as e:
                st.error("Terjadi error saat OCR:")
                st.code(str(e))
