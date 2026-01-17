import streamlit as st
from PIL import Image
import easyocr
import numpy as np

# ======================
# Konfigurasi Halaman
# ======================
st.set_page_config(
    page_title="ScanText Pro – OCR + Editor",
    page_icon="📄",
    layout="centered"
)

# ======================
# Dark Mode Toggle
# ======================
dark_mode = st.toggle("🌙 Dark Mode")

if dark_mode:
    st.markdown(
        """
        <style>
        body {
            background-color: #0f172a;
            color: white;
        }
        .stTextArea textarea, .stTextInput input {
            background-color: #1e293b !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ======================
# Judul
# ======================
st.title("📄 ScanText Pro – OCR + Editor")
st.success("OCR stabil + bisa diedit + mode gelap tersedia")

# ======================
# Upload Gambar / Kamera
# ======================
st.subheader("📷 Ambil atau Upload Gambar")

tab1, tab2 = st.tabs(["Upload File", "Kamera"])

image = None

with tab1:
    uploaded_file = st.file_uploader(
        "Upload gambar (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"]
    )
    if uploaded_file:
        image = Image.open(uploaded_file)

with tab2:
    camera_image = st.camera_input("Ambil foto dari kamera")
    if camera_image:
        image = Image.open(camera_image)

# ======================
# Preview Gambar
# ======================
if image:
    st.image(image, caption="Preview gambar", use_column_width=True)

    # ======================
    # Proses OCR
    # ======================
    if st.button("🔍 Proses OCR"):
        with st.spinner("Sedang memproses OCR..."):
            reader = easyocr.Reader(["id", "en"], gpu=False)
            result = reader.readtext(np.array(image), detail=0)
            ocr_text = "\n".join(result)

            # Simpan di session supaya tidak hilang saat scroll
            st.session_state["ocr_text"] = ocr_text
            st.session_state["judul"] = "HASIL OCR"
            st.session_state["tanggal"] = ""
            st.session_state["alamat"] = ""

# ======================
# Editor
# ======================
if "ocr_text" in st.session_state:

    st.subheader("✏️ Edit Data Utama")

    judul = st.text_input(
        "Judul",
        value=st.session_state.get("judul", "")
    )

    tanggal = st.text_input(
        "Tanggal",
        value=st.session_state.get("tanggal", "")
    )

    alamat = st.text_input(
        "Alamat",
        value=st.session_state.get("alamat", "")
    )

    st.subheader("📝 Edit isi teks OCR:")
    edited_text = st.text_area(
        "Edit teks bebas:",
        value=st.session_state["ocr_text"],
        height=250
    )

    # Simpan perubahan
    st.session_state["judul"] = judul
    st.session_state["tanggal"] = tanggal
    st.session_state["alamat"] = alamat
    st.session_state["ocr_text"] = edited_text

    # ======================
    # Hasil Final
    # ======================
    st.subheader("📄 Hasil Final")

    final_text = f"""
{judul}

Tanggal : {tanggal}
Alamat  : {alamat}

{edited_text}
    """.strip()

    st.text_area(
        "Teks Final (siap disalin atau download):",
        value=final_text,
        height=250
    )

    st.download_button(
        label="⬇️ Download sebagai TXT",
        data=final_text,
        file_name="hasil_ocr.txt",
        mime="text/plain"
    )
