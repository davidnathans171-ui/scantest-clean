import streamlit as st
from PIL import Image
import easyocr
import numpy as np
from datetime import date

st.set_page_config(page_title="ScanText Pro", layout="centered")

# ====== CACHE OCR ======
@st.cache_resource
def load_reader():
    return easyocr.Reader(['id', 'en'], gpu=False)

reader = load_reader()

# ====== HEADER ======
st.title("📄 ScanText Pro – OCR + Mode Surat")
st.success("OCR stabil + bisa diedit + Mode Surat aktif")

# ====== MODE PILIHAN ======
mode = st.selectbox("Pilih Mode Output:", ["Struk", "Surat"])

# ====== UPLOAD GAMBAR ======
uploaded_file = st.file_uploader("Upload gambar (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

ocr_text = ""

if uploaded_file:
    try:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Preview Gambar", use_container_width=True)

        if st.button("🔍 Proses OCR"):
            with st.spinner("Memproses OCR..."):
                img_np = np.array(image)
                results = reader.readtext(img_np)

                ocr_text = "\n".join([r[1] for r in results])

                if ocr_text.strip() == "":
                    st.warning("Tidak ada teks terdeteksi.")
                else:
                    st.session_state["ocr_text"] = ocr_text
                    st.success("OCR berhasil!")
    except:
        st.error("Gagal membaca gambar. Pastikan file gambar valid.")

# ====== SIMPAN OCR AGAR TIDAK HILANG ======
if "ocr_text" not in st.session_state:
    st.session_state["ocr_text"] = ""

# ====== EDITOR OCR ======
st.subheader("✏️ Edit Isi Teks OCR")
edited_text = st.text_area(
    "Edit teks OCR di sini:",
    value=st.session_state["ocr_text"],
    height=200
)

# ====== MODE STRUK ======
if mode == "Struk":
    st.subheader("🧾 Mode Struk")

    judul = st.text_input("Judul", "HASIL OCR")
    tanggal = st.text_input("Tanggal", date.today().strftime("%d %B %Y"))
    alamat = st.text_input("Alamat", "Isi alamat di sini")

    final_text = f"""
{judul}

Tanggal : {tanggal}
Alamat  : {alamat}

{edited_text}
"""

# ====== MODE SURAT ======
else:
    st.subheader("✉️ Mode Surat")

    judul = st.text_input("Judul Surat", "SURAT KETERANGAN")
    tanggal = st.text_input("Tanggal", date.today().strftime("%d %B %Y"))
    tujuan = st.text_input("Tujuan Surat", "Bapak/Ibu ...")
    penutup = st.text_input("Penutup", "Hormat kami,")
    nama = st.text_input("Nama Pengirim", "Nama Anda")

    final_text = f"""
{judul}

Tanggal: {tanggal}

Kepada Yth:
{tujuan}
Di Tempat

Dengan hormat,

{edited_text}

{penutup}

{nama}
"""

# ====== HASIL AKHIR ======
st.subheader("📄 Hasil Final")
st.text_area("Teks Final (siap disalin / download)", final_text, height=300)

st.download_button(
    "⬇️ Download sebagai TXT",
    data=final_text,
    file_name="hasil_ocr.txt",
    mime="text/plain"
)
