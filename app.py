import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN API KEY DAN MODEL (PENTING!)
# ==============================================================================

# Mengambil API Key dari secrets Streamlit/GitHub
# Aman dan direkomendasikan untuk produksi.
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    print("Gemini API Key berhasil dikonfigurasi dari secrets.")
except Exception as e:
    st.error(f"Kesalahan: API Key tidak ditemukan. Pastikan 'GEMINI_API_KEY' telah ditambahkan ke Streamlit Secrets. Error: {e}")
    st.stop() # Hentikan eksekusi jika tidak ada API Key

MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot Anda di sini.
INITIAL_CHATBOT_CONTEXT = [
    {"role": "user", "parts": ["Saya adalah seorang tenaga medis. Tuliskan penyakit yang perlu di diagnosis. Jawaban singkat dan jelas. Jangan berikan diagnosis pasti atau menggantikan nasihat medis profesional. Tolak pertanyaan yang tidak berkaitan dengan kesehatan atau medis."]},
    {"role": "model", "parts": ["Baik, saya siap membantu Anda dengan informasi medis umum. Mohon berikan gejala yang Anda rasakan."]}
]

# ==============================================================================
# ANTARMUKA APLIKASI STREAMLIT
# ==============================================================================

st.set_page_config(page_title="🤖 Chatbot Medis Sederhana", page_icon="💊")
st.title("🤖 Chatbot Medis Sederhana")
st.subheader("Berdasarkan Model Google Gemini")
st.info("⚠️ **Peringatan**: Chatbot ini hanya untuk informasi umum dan tidak bisa menggantikan nasihat medis profesional. Konsultasikan dengan dokter untuk diagnosis dan pengobatan.")

# Inisialisasi model dan riwayat chat di state sesi
@st.cache_resource
def get_model():
    """Menginisialisasi model Gemini."""
    return genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )

model = get_model()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = INITIAL_CHATBOT_CONTEXT
    st.session_state.chat = model.start_chat(history=st.session_state.chat_history)

# Tampilkan riwayat chat sebelumnya
for message in st.session_state.chat_history:
    role = message["role"]
    content = message["parts"][0]
    if role == "user":
        with st.chat_message("user"):
            st.markdown(content)
    elif role == "model":
        with st.chat_message("assistant"):
            st.markdown(content)

# Tangani input pengguna baru
if user_input := st.chat_input("Tulis gejala atau pertanyaan Anda di sini..."):
    # Tampilkan input pengguna di UI
    st.session_state.chat_history.append({"role": "user", "parts": [user_input]})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Kirim input pengguna ke model dan dapatkan respons
    with st.chat_message("assistant"):
        with st.spinner("Sedang memproses..."):
            try:
                response = st.session_state.chat.send_message(user_input)
                # Pastikan respons valid sebelum ditampilkan
                if response and response.text:
                    st.markdown(response.text)
                    st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
                else:
                    st.warning("Maaf, saya tidak bisa memberikan balasan. Respons API kosong.")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat berkomunikasi dengan Gemini: {e}")
                st.warning("Kemungkinan penyebab: Masalah koneksi, API Key tidak valid, atau kuota habis.")
