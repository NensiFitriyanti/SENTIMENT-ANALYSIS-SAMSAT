# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import datetime
import os
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Cek dan download lexicon NLTK
def ensure_nltk_data():
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)

# Dummy login
USERNAME = "admin"
PASSWORD = "123"

if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def map_sentiment(pelayanan):
    if pelayanan == "Baik":
        return "Positif"
    elif pelayanan == "Sedang":
        return "Netral"
    elif pelayanan == "Buruk":
        return "Negatif"
    return "Netral"

# Halaman Utama
def home():
    st.set_page_config(layout="wide")
    st.title("📌 Analisis Sentimen Pelayanan SAMSAT")
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("🔐 Admin"):
            st.session_state.page = "login"
    st.write("Silakan pilih menu:")
    if st.button("📝 Isi Komentar"):
        st.session_state.page = "form"

# Form Komentar
def form():
    st.title("🗣️ Form Komentar Publik")
    name = st.text_input("Nama")
    tanggal = st.date_input("Tanggal", value=datetime.date.today(), disabled=True)
    sumber = st.selectbox("Mendapatkan informasi dari mana?", 
                          ["YouTube", "Instagram", "Google Maps", "WhatsApp", "Scan di Tempat"])
    pelayanan = st.selectbox("Bagaimana pelayanannya?", ["Baik", "Sedang", "Buruk"])
    if pelayanan:
        komentar = st.text_area("Berikan alasanmu:")
    else:
        komentar = ""

    if st.button("Kirim"):
        sentiment = map_sentiment(pelayanan)
        data = {
            "Tanggal": tanggal,
            "Nama": name,
            "Sumber": sumber,
            "Pelayanan": pelayanan,
            "Komentar": komentar,
            "Sentimen": sentiment
        }
        df = pd.DataFrame([data])
        try:
            df.to_csv("data_komentar.csv", mode="a", header=not os.path.exists("data_komentar.csv"), index=False)
        except:
            df.to_csv("data_komentar.csv", index=False)
        st.session_state.page = "thanks"

# Halaman Terima Kasih
def thanks():
    st.title("✅ Terima Kasih")
    st.markdown("Komentar kamu telah terkirim! 😊")
    if st.button("Kembali ke Beranda"):
        st.session_state.page = "home"

# Login Admin
def login():
    st.title("🔒 Login Admin")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == USERNAME and pw == PASSWORD:
            st.session_state.logged_in = True
            st.session_state.page = "dashboard"
        else:
            st.error("Username atau password salah.")
    if st.button("Kembali"):
        st.session_state.page = "home"

# Dashboard
def dashboard():
    st.title("📊 Dashboard Admin Sentimen SAMSAT")
    if os.path.exists("data_komentar.csv"):
        df = pd.read_csv("data_komentar.csv")

        st.subheader("📺 Total Komentar per Platform")
        platform_counts = df["Sumber"].value_counts()
        for platform, count in platform_counts.items():
            st.markdown(f"- **{platform}**: {count} komentar")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Jumlah Komentar per Platform")
            st.bar_chart(platform_counts)

        with col2:
            st.subheader("🧭 Distribusi Sentimen")
            st.bar_chart(df["Sentimen"].value_counts())

        st.subheader("☁️ Wordcloud Komentar")
        text = " ".join(df["Komentar"].dropna().astype(str))
        if text:
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

        st.subheader("🔍 Insight & Rekomendasi")
        st.write("- Komentar positif menunjukkan pelayanan publik cukup baik.")
        st.write("- Komentar negatif perlu ditindaklanjuti agar kepuasan meningkat.")
        st.write("- Platform terbanyak digunakan masyarakat adalah yang potensial untuk komunikasi lebih lanjut.")

        st.subheader("📋 Data Komentar Lengkap")
        for i in df.index:
            col1, col2 = st.columns([6, 1])
            with col1:
                st.write(df.loc[i].to_dict())
            with col2:
                if st.button(f"Hapus 🗑️ {i}", key=f"hapus_{i}"):
                    df = df.drop(i).reset_index(drop=True)
                    df.to_csv("data_komentar.csv", index=False)
                    st.experimental_rerun()

        st.download_button("📥 Unduh CSV", df.to_csv(index=False).encode(), "komentar.csv", "text/csv")
        st.download_button("📥 Unduh TXT", df.to_string(index=False).encode(), "komentar.txt", "text/plain")
    else:
        st.warning("Belum ada data komentar.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "home"

# Routing
def main():
    ensure_nltk_data()
    if st.session_state.page == "home":
        home()
    elif st.session_state.page == "form":
        form()
    elif st.session_state.page == "thanks":
        thanks()
    elif st.session_state.page == "login":
        login()
    elif st.session_state.page == "dashboard":
        if st.session_state.logged_in:
            dashboard()
        else:
            login()

if __name__ == "__main__":
    main()
