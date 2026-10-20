import pandas as pd
import streamlit as st

# Konfigurasi Halaman Dashboard
st.set_page_config(
    page_title="Dashboard Interaktif Data Fiskal & Makroekonomi 97 Kota",
    page_icon="📊",
    layout="wide",
)

# URL Dataset dari GitHub
DATA_URL = "https://raw.githubusercontent.com/Alam-A99/DATAAKSI/refs/heads/main/dataset_fiskal_97_hipoFull.csv"


# Fungsi untuk memuat data dengan cache agar performa lebih cepat
@st.cache_data
def load_data(url):
  df = pd.read_csv(url)
  return df


# Memuat data
try:
  df = load_data(DATA_URL)
except Exception as e:
  st.error(f"Gagal memuat dataset: {e}")
  st.stop()

# Header Utama Dashboard
st.title("📊 Dashboard Interaktif Data Fiskal & Makroekonomi 97 Kota")
st.markdown(
    "Dibuat oleh **VIONA JULIE KALANGIE** | Visualisasi Data Fiskal Daerah"
)
st.markdown("---")

# --- SIDEBAR: PANEL FILTER DATA ---
st.sidebar.header("🔍 Panel Filter Data")

# Deteksi otomatis kolom yang merepresentasikan wilayah (Kota/Kabupaten)
kolom_wilayah = [
    col
    for col in df.columns
    if any(k in col.lower() for k in ["kota", "kabupaten", "wilayah", "daerah"])
]
if not kolom_wilayah:
  kolom_wilayah = [df.columns[0]]  # Fallback ke kolom pertama jika tidak ditemukan

col_pilih = kolom_wilayah[0]

# Pilihan multiselect untuk Kota/Kabupaten
daftar_kota = sorted(df[col_pilih].dropna().unique())
selected_kota = st.sidebar.multiselect(
    "Pilih Kota/Kabupaten:",
    options=daftar_kota,
    default=daftar_kota[:5]  # Default 5 kota pertama terpilih
)

# Filter dataframe berdasarkan pilihan sidebar
if selected_kota:
  df_filtered = df[df[col_pilih].isin(selected_kota)]
else:
  df_filtered = df

# --- TABS UTAMA ---
tab1, tab2, tab3 = st.tabs(
    ["📈 Ringkasan & Statistik", "📋 Tabel Data Mentah", "📉 Grafik Analisis"]
)

# TAB 1: Ringkasan & Statistik
with tab1:
  st.subheader("Ringkasan Statistik Dataset Fiskal")

  # Metrik utama
  col1, col2 = st.columns(2)
  with col1:
    st.metric(
        label="Total Baris Data Ditampilkan", value=f"{len(df_filtered)} baris"
    )
  with col2:
    st.metric(
        label="Total Variabel/Kolom", value=f"{len(df_filtered.columns)} kolom"
    )

  st.markdown("---")
  st.subheader("Statistik Deskriptif")
  st.dataframe(df_filtered.describe(), use_container_width=True)
    
