import streamlit as st
from PIL import Image
import easyocr
import numpy as np

st.set_page_config(page_title="ScanText Pro", layout="centered")

st.title("ScanText Pro – OCR MODE")
st.success("OCR aktif menggunakan EasyOCR (stabil untuk Streamlit Cloud)")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en', 'id'], gpu=False)

reader = load_reader()

uploaded_file = st.file_uploader(
    "Upload gambar (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Preview gambar", use_container_width=True)

    if st.button("Proses OCR"):
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

                    # ===============================
                    # FITUR EDIT DATA
                    # ===============================
                    st.subheader("✏️ Edit Data Dokumen")

                    judul = st.text_input("Judul Dokumen", "Judul belum diisi")
                    tanggal = st.text_input("Tanggal", "Tanggal belum diisi")
                    alamat = st.text_input("Alamat", "Alamat belum diisi")

                    st.subheader("📄 Hasil OCR (Bisa Diedit)")
                    edited_text = st.text_area(
                        "Edit teks hasil OCR di sini:",
                        text,
                        height=300
                    )

                    st.subheader("📑 Hasil Final Dokumen")
                    final_text = f"""
JUDUL   : {judul}
TANGGAL : {tanggal}
ALAMAT  : {alamat}

------------------------
{edited_text}
"""
                    st.text_area("Output Final", final_text, height=350)

                    st.download_button(
                        "⬇️ Download sebagai TXT",
                        final_text,
                        file_name="hasil_scantext.txt",
                        mime="text/plain"
                    )

            except Exception as e:
                st.error("Terjadi error saat OCR:")
                st.code(str(e))
