import streamlit as st
from PIL import Image
import easyocr
import numpy as np

# =========================
# SESSION STATE (ANTI HILANG SAAT SCROLL / RERUN)
# =========================
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""

if "final_text" not in st.session_state:
    st.session_state.final_text = ""

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(page_title="ScanText Pro - OCR Editor", layout="centered")

st.title("ScanText Pro – OCR + Editor")
st.success("OCR stabil + hasil tidak hilang walau scroll atau klik.")

# =========================
# LOAD OCR READER
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

    # =========================
    # TOMBOL PROSES OCR
    # =========================
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
                    st.session_state.ocr_text = text
                    st.success("OCR berhasil! Silakan edit teks di bawah.")

            except Exception as e:
                st.error("Terjadi error saat OCR:")
                st.code(str(e))

# =========================
# MODE EDIT (TIDAK HILANG SAAT SCROLL)
# =========================
if st.session_state.ocr_text != "":
    st.subheader("✏️ Edit Informasi Dokumen")

    judul = st.text_input("📝 Judul", "STRUK PEMBELIAN")
    tanggal = st.text_input("📅 Tanggal", "16/01/2026")
    alamat = st.text_input("📍 Alamat", "Toko Contoh, Jakarta")

    st.subheader("🖊 Edit Teks OCR")
    edited_text = st.text_area(
        "Teks hasil OCR (bisa diedit bebas):",
        value=st.session_state.ocr_text,
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
    st.session_state.final_text = final_text

    st.subheader("📄 Hasil Final")
    st.text_area("Teks Final (siap disalin / download):", st.session_state.final_text, height=300)

    st.download_button(
        "⬇ Download sebagai TXT",
        st.session_state.final_text,
        file_name="hasil_ocr.txt",
        mime="text/plain"
    )
