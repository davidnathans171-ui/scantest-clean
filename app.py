import streamlit as st
from PIL import Image
import easyocr
import numpy as np

# =========================
# Konfigurasi Halaman
# =========================
st.set_page_config(page_title="ScanText Pro", layout="centered")

st.title("ScanText Pro – OCR MODE")
st.success("OCR aktif menggunakan EasyOCR (stabil untuk Streamlit Cloud)")

# =========================
# Load EasyOCR (cache agar tidak reload terus)
# =========================
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en', 'id'], gpu=False)

reader = load_reader()

# =========================
# Upload Gambar
# =========================
uploaded_file = st.file_uploader(
    "Upload gambar (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Preview gambar", use_container_width=True)

    # =========================
    # Tombol Proses OCR
    # =========================
    if st.button("🔍 Proses OCR"):
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
                    st.success("OCR berhasil!")

                    # =========================
                    # MODE EDIT
                    # =========================
                    st.subheader("✏️ Edit Data Dokumen")

                    judul = st.text_input("Judul Dokumen", "Struk Belanja")
                    tanggal = st.text_input("Tanggal", "16/01/2026")
                    alamat = st.text_input("Alamat", "Masukkan alamat di sini")

                    st.subheader("📝 Edit Teks OCR")
                    edited_text = st.text_area(
                        "Teks OCR (bisa diedit bebas)",
                        text,
                        height=300
                    )

                    # =========================
                    # HASIL FINAL
                    # =========================
                    st.subheader("📄 Hasil Final")

                    final_text = f"""
{judul}

Tanggal : {tanggal}
Alamat  : {alamat}

{edited_text}
"""

                    st.text_area("Teks Final (siap disalin / disimpan)", final_text, height=350)

                    st.download_button(
                        "⬇️ Download sebagai TXT",
                        final_text,
                        file_name="hasil_ocr.txt"
                    )

            except Exception as e:
                st.error("Terjadi error saat OCR:")
                st.code(str(e))
