import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Dashboard Fiskal & IPM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Dark Mode / Clean Theme)
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stMetric {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Fungsi untuk memuat dataset dengan cache
@st.cache_data
def load_data(url):
  try:
    df = pd.read_csv(url)
    return df
  except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    return None


DATA_URL = "https://raw.githubusercontent.com/Alam-A99/DATAAKSI/refs/heads/main/dataset_fiskal_97_hipoFull.csv"
df = load_data(DATA_URL)

if df is not None:
  # Sidebar Navigasi & Filter
  st.sidebar.header("🎛️ Panel Kontrol & Filter")

  # Deteksi kolom secara otomatis atau gunakan nama standar
  columns = df.columns.tolist()

  # Contoh pencarian kolom yang relevan (Tahun, Wilayah/Kabupaten/Kota, IPM, Pendapatan)
  tahun_col = (
      next((c for c in columns if "tahun" in c.lower() or "year" in c.lower()), None)
      if "tahun" in [c.lower() for c in columns]
      else columns[0]
  )
  wilayah_col = next(
      (
          c
          for c in columns
          if "kabupaten" in c.lower()
          or "kota" in c.lower()
          or "wilayah" in c.lower()
          or "daerah" in c.lower()
      ),
      columns[1] if len(columns) > 1 else None,
  )
  ipm_col = next(
      (c for c in columns if "ipm" in c.lower()),
      columns[2] if len(columns) > 2 else None,
  )

  # Filter Tahun
  if tahun_col and tahun_col in df.columns:
    sorted_years = sorted(df[tahun_col].dropna().unique())
    selected_years = st.sidebar.multiselect(
        "Pilih Tahun:", options=sorted_years, default=sorted_years
    )
    if selected_years:
      df_filtered = df[df[tahun_col].isin(selected_years)]
    else:
      df_filtered = df
  else:
    df_filtered = df

  # Header Utama
  st.title("📈 Dashboard Analisis Fiskal & IPM")
  st.markdown(
      "Visualisasi tren Indeks Pembangunan Manusia (IPM), perbandingan antarkota,"
      " serta data pendapatan dan transfer fiskal."
  )
  st.markdown("---")

  # 1. Metrik Utama (KPIs)
  col1, col2, col3, col4 = st.columns(4)
  with col1:
    total_obs = len(df_filtered)
    st.metric(label="Total Observasi / Data", value=f"{total_obs:,}")

  with col2:
    if ipm_col and ipm_col in df_filtered.columns:
      avg_ipm = df_filtered[ipm_col].mean()
      st.metric(label="Rata-rata IPM", value=f"{avg_ipm:.2f}")
    else:
      st.metric(label="Rata-rata IPM", value="N/A")

  with col3:
    if wilayah_col and wilayah_col in df_filtered.columns:
      total_wilayah = df_filtered[wilayah_col].nunique()
      st.metric(label="Jumlah Wilayah", value=f"{total_wilayah}")
    else:
      st.metric(label="Jumlah Wilayah", value="N/A")

  with col4:
    if tahun_col and tahun_col in df_filtered.columns:
      rentang_tahun = (
          f"{int(df_filtered[tahun_col].min())} - {int(df_filtered[tahun_col].max())}"
      )
      st.metric(label="Rentang Tahun", value=rentang_tahun)
    else:
      st.metric(label="Rentang Tahun", value="N/A")

  st.markdown("---")

  # 2. Visualisasi Tren IPM per Tahun (Sesuai contoh gambar)
  st.subheader("📉 Tren IPM")
  if tahun_col and ipm_col in df.columns:
    df_trend = (
        df.groupby(tahun_col)[ipm_col].mean().reset_index(name="Rata-rata IPM")
    )

    fig_trend = px.line(
        df_trend,
        x=tahun_col,
        y="Rata-rata IPM",
        markers=True,
        title="Rata-rata IPM per Tahun",
        template="plotly_dark",
    )
    fig_trend.update_traces(
        line=dict(color="#60a5fa", width=2.5), marker=dict(size=8)
    )
    fig_trend.update_layout(
        xaxis_title="Tahun",
        yaxis_title="Rata-rata IPM",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_trend, use_container_width=True)
  else:
    st.info("Kolom Tahun atau IPM tidak terdeteksi otomatis untuk grafik tren.")

  # 3. Bagian Dua Kolom: Perbandingan Antarkota & Pendapatan/Transfer
  col_left, col_right = st.columns(2)

  with col_left:
    st.subheader("🏙️ Perbandingan Antarkota")
    if wilayah_col and ipm_col in df_filtered.columns:
      # Ambil data rata-rata IPM tertinggi per wilayah
      df_wilayah = (
          df_filtered.groupby(wilayah_col)[ipm_col]
          .mean()
          .reset_index(name="Rata-rata IPM")
          .sort_values(by="Rata-rata IPM", ascending=False)
          .head(10)
      )

      fig_bar = px.bar(
          df_wilayah,
          x="Rata-rata IPM",
          y=wilayah_col,
          orientation="h",
          title="Top 10 Wilayah Berdasarkan IPM",
          template="plotly_dark",
          color="Rata-rata IPM",
          color_continuous_scale="Blues",
      )
      fig_bar.update_layout(
          yaxis=dict(autorange="reversed"),
          plot_bgcolor="rgba(0,0,0,0)",
          paper_bgcolor="rgba(0,0,0,0)",
      )
      st.plotly_chart(fig_bar, use_container_width=True)
    else:
      st.info("Data wilayah/kota tidak tersedia untuk perbandingan.")

  with col_right:
    st.subheader("💰 Pendapatan dan Transfer")
    # Mencari kolom yang mengandung kata 'pendapatan', 'transfer', 'fiskal', atau 'APBD'
    fiscal_cols = [
        c
        for c in columns
        if any(
            keyword in c.lower()
            for keyword in ["pendapatan", "transfer", "fiskal", "apbd", "dana"]
        )
    ]

    if fiscal_cols and tahun_col in df_filtered.columns:
      selected_fiscal = st.selectbox(
          "Pilih Indikator Pendapatan/Transfer:", options=fiscal_cols
      )
      df_fiscal = (
          df_filtered.groupby(tahun_col)[selected_fiscal]
          .sum()
          .reset_index(name="Total")
      )

      fig_fiscal = px.area(
          df_fiscal,
          x=tahun_col,
          y="Total",
          title=f"Total {selected_fiscal} per Tahun",
          template="plotly_dark",
      )
      fig_fiscal.update_traces(line=dict(color="#34d399", width=2))
      fig_fiscal.update_layout(
          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
      )
      st.plotly_chart(fig_fiscal, use_container_width=True)
    else:
      # Fallback jika kolom spesifik fiskal tidak ditemukan secara persis
      numeric_cols = df_filtered.select_dtypes(
          include=["float64", "int64"]
      ).columns.tolist()
      if len(numeric_cols) > 2 and tahun_col in df_filtered.columns:
        fallback_col = st.selectbox(
            "Pilih Variabel Numerik Alternatif:",
            options=[c for c in numeric_cols if c != tahun_col],
        )
        df_alt = (
            df_filtered.groupby(tahun_col)[fallback_col]
            .mean()
            .reset_index(name="Nilai")
        )
        fig_alt = px.line(
            df_alt,
            x=tahun_col,
            y="Nilai",
            markers=True,
            title=f"Tren {fallback_col} per Tahun",
            template="plotly_dark",
        )
        st.plotly_chart(fig_alt, use_container_width=True)
      else:
        st.info("Kolom fiskal atau pendapatan tidak ditemukan dalam dataset.")

  # 4. Preview Tabel Data Mentah
  st.markdown("---")
  with st.expander("📄 Lihat Data Mentah (Raw Dataset)"):
    st.dataframe(df_filtered, use_container_width=True)

else:
  st.warning(
      "Gagal memuat dataset. Periksa kembali koneksi internet atau URL GitHub"
      " Anda."
  )
