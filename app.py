import streamlit as st
from PIL import Image
import numpy as np
import easyocr

# ================== KONFIGURASI AWAL ==================
st.set_page_config(
    page_title="ScanText Pro",
    page_icon="📄",
    layout="centered"
)

st.title("📄 ScanText Pro – OCR + Editor + Mode Surat")
st.success("OCR stabil • Bisa diedit • Kamera & Upload aktif • Mode Struk & Surat")

# ================== LOAD OCR ==================
@st.cache_resource
def load_reader():
    return easyocr.Reader(['id', 'en'], gpu=False)

reader = load_reader()

# ================== SESSION STATE ==================
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""
if "processed" not in st.session_state:
    st.session_state.processed = False

# ================== PILIH MODE ==================
mode = st.selectbox("Pilih Mode Output:", ["Struk", "Surat"])

# ================== INPUT GAMBAR ==================
st.subheader("📷 Ambil dari Kamera atau Upload Gambar")

tab1, tab2 = st.tabs(["📁 Upload File", "📸 Kamera"])

image = None

with tab1:
    uploaded_file = st.file_uploader(
        "Upload gambar (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"]
    )
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert("RGB")
        except:
            st.error("Gambar tidak valid.")

with tab2:
    camera_file = st.camera_input("Ambil foto langsung")
    if camera_file is not None:
        try:
            image = Image.open(camera_file).convert("RGB")
        except:
            st.error("Gambar kamera tidak valid.")

# ================== PREVIEW GAMBAR ==================
if image is not None:
    st.image(image, caption="Preview gambar", use_column_width=True)

    if st.button("🔍 Proses OCR"):
        with st.spinner("Sedang memproses OCR..."):
            try:
                img_np = np.array(image)
                result = reader.readtext(img_np)
                text = "\n".join([r[1] for r in result])

                st.session_state.ocr_text = text
                st.session_state.processed = True
                st.success("OCR berhasil!")

            except Exception as e:
                st.error("Terjadi error saat OCR:")
                st.code(str(e))

# ================== EDITOR ==================
if st.session_state.processed:

    st.subheader("✏️ Edit Informasi Utama")

    judul = st.text_input("Judul:", value="HASIL OCR")
    tanggal = st.text_input("Tanggal:", value="")
    alamat = st.text_input("Alamat:", value="")

    st.subheader("📝 Edit isi teks OCR:")
    edited_text = st.text_area(
        "Edit teks OCR di sini:",
        value=st.session_state.ocr_text,
        height=250
    )

    # ================== FORMAT OUTPUT ==================
    if mode == "Struk":
        final_text = f"""{judul}

Tanggal : {tanggal}
Alamat  : {alamat}

{edited_text}
"""
    else:  # MODE SURAT
        final_text = f"""Perihal : {judul}

Tanggal : {tanggal}
Alamat Tujuan :
{alamat}

Dengan hormat,

{edited_text}

Demikian surat ini disampaikan.
Terima kasih.
"""

    # ================== HASIL FINAL ==================
    st.subheader("📄 Hasil Final")
    st.text_area(
        "Teks Final (siap disalin atau diunduh):",
        final_text,
        height=300
    )

    st.download_button(
        "⬇️ Download sebagai TXT",
        final_text,
        file_name="hasil_ocr.txt"
    )
