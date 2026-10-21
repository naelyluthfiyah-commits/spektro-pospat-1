import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Konfigurasi Halaman
st.set_page_config(page_title="Kalkulator Analisis Kimia & Validasi", page_icon="🧪", layout="wide")

st.title("🧪 Aplikasi Kalkulator Analisis Instrumentasi & Validasi Metode")
st.markdown("Silakan pilih menu pengujian di bawah ini:")

# Buat Navigasi Menggunakan Tab / Tombol Menu Utama
tab1, tab2, tab3, tab4 = st.tabs([
    "1. 📈 Kurva Kalibrasi & Regresi Linear",
    "2. 🧪 Perhitungan Kadar",
    "3. 📊 Uji Presisi",
    "4. 🎯 Uji Akurasi"
])

# =========================================================================
# MENU 1: KURVA KALIBRASI, REGRESI LINEAR & PERHITUNGAN DERET STANDAR
# =========================================================================
with tab1:
    st.header("📈 Kurva Kalibrasi, Regresi Linear & Pembuatan Deret Standar")
    
    # Sub-Fitur A: Perhitungan Deret Standar (V1 . C1 = V2 . C2)
    with st.expander("🧪 Perhitungan Pemipetan Deret Standar ($V_1 \cdot C_1 = V_2 \cdot C_2$)", expanded=True):
        st.write("Hitung volume larutan induk ($V_1$) yang harus dipipet untuk membuat larutan standar dengan konsentrasi tertentu.")
        
        col_c1, col_v2 = st.columns(2)
        with col_c1:
            c1 = st.number_input("Konsentrasi Larutan Induk ($C_1$)", value=100.0, step=1.0, help="Misal: 100 ppm")
        with col_v2:
            v2 = st.number_input("Volume Labu Ukur yang Digunakan ($V_2$ dalam mL)", value=50.0, step=1.0)
            
        st.markdown("**Masukkan Konsentrasi Standar yang Diinginkan ($C_2$):**")
        c2_inputs = st.text_input("Pisahkan dengan koma (contoh: 0, 2, 4, 6, 8)", "0, 2, 4, 6, 8")
        
        if st.button("Hitung Volume Pemipetan ($V_1$)"):
            try:
                c2_list = [float(x.strip()) for x in c2_inputs.split(",")]
                v1_list = [(c2 * v2) / c1 for c2 in c2_list]
                
                df_deret = pd.DataFrame({
                    "Konsentrasi Target (C2)": c2_list,
                    "Volume Pipet V1 (mL)": v1_list,
                    "Volume Labu Ukur V2 (mL)": [v2] * len(c2_list),
                    "Konsentrasi Induk C1": [c1] * len(c2_list)
                })
                st.dataframe(df_deret, use_container_width=True)
            except ValueError:
                st.error("Format konsentrasi salah. Pastikan hanya memasukkan angka yang dipisahkan koma.")

    st.markdown("---")
    
    # Sub-Fitur B: Kurva Kalibrasi & Regresi Linear
    st.subheader("📊 Kurva Kalibrasi & Regresi Linear")
    num_points = st.number_input("Jumlah Titik Standar", min_value=3, max_value=15, value=5)
    
    default_data = pd.DataFrame({
        "Konsentrasi (ppm)": [0.0, 2.0, 4.0, 6.0, 8.0][:num_points],
        "Absorbansi (Y)": [0.0, 0.150, 0.310, 0.455, 0.600][:num_points]
    })

    edited_df = st.data_editor(default_data, num_rows="dynamic", key="editor_kalibrasi")

    if st.button("Hitung Regresi & Tampilkan Kurva", type="primary"):
        # Konversi tipe data agar aman dari TypeError
        x = pd.to_numeric(edited_df["Konsentrasi (ppm)"], errors='coerce').fillna(0).values.astype(float)
        y = pd.to_numeric(edited_df["Absorbansi (Y)"], errors='coerce').fillna(0).values.astype(float)

        n = len(x)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_xx = np.sum(x**2)
        sum_yy = np.sum(y**2)

        # Perhitungan Regresi
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x**2)
        intercept = (sum_y - slope * sum_x) / n
        r_value = (n * sum_xy - sum_x * sum_y) / np.sqrt((n * sum_xx - sum_x**2) * (n * sum_yy - sum_y**2))
        r_squared = r_value**2

        st.success("Perhitungan Berhasil!")
        c_m, c_c, c_r = st.columns(3)
        c_m.metric("Slope ($m$)", f"{slope:.4f}")
        c_c.metric("Intercept ($c$)", f"{intercept:.4f}")
        c_r.metric("Koefisien Korelasi ($r$)", f"{r_value:.4f}")
        st.info(f"Koefisien Determinasi ($R^2$): **{r_squared:.4f}** | Persamaan: **y = {slope:.4f}x + ({intercept:.4f})**")

        # Visualisasi Kurva
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.scatter(x, y, color='red', label='Data Standar', zorder=5)
        ax.plot(x, slope * x + intercept, color='blue', label=f'y = {slope:.4f}x + {intercept:.4f}')
        ax.set_xlabel("Konsentrasi (ppm)")
        ax.set_ylabel("Absorbansi (Y)")
        ax.set_title("Kurva Kalibrasi Linearitas")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)


# =========================================================================
# MENU 2: PERHITUNGAN KADAR
# =========================================================================
with tab2:
    st.header("🧪 Perhitungan Kadar Sampel")
    st.write("Menghitung kadar sampel berdasarkan persamaan kurva regresi $y = mx + c$.")

    col_m, col_c = st.columns(2)
    with col_m:
        slope_in = st.number_input("Slope ($m$)", value=0.0752, format="%.4f")
    with col_c:
        intercept_in = st.number_input("Intercept ($c$)", value=0.0020, format="%.4f")

    col_abs, col_fp = st.columns(2)
    with col_abs:
        abs_sampel = st.number_input("Absorbansi Sampel ($Y$)", value=0.3100, format="%.4f")
    with col_fp:
        fp_in = st.number_input("Faktor Pengenceran (FP)", value=1.0)

    if st.button("Hitung Kadar Sampel", type="primary"):
        kadar_baca = (abs_sampel - intercept_in) / slope_in
        kadar_akhir = kadar_baca * fp_in

        st.markdown("---")
        st.subheader("Hasil Perhitungan:")
        st.metric("Konsentrasi Terbaca (x)", f"{kadar_baca:.4f} ppm")
        st.metric("Kadar Akhir Sampel (x × FP)", f"{kadar_akhir:.4f} ppm")


# =========================================================================
# MENU 3: UJI PRESISI
# =========================================================================
with tab3:
    st.header("📊 Uji Presisi (% RSD / % RPD)")
    
    pilihan_presisi = st.radio("Pilih Tipe Uji Presisi:", ["% RSD (Replikasi Banyak)", "% RPD (Duplo / 2 Pengujian)"], horizontal=True)

    if pilihan_presisi == "% RSD (Replikasi Banyak)":
        st.write("Masukkan nilai hasil pembacaan replikasi sampel (pisahkan dengan koma):")
        input_rsd = st.text_input("Data Replikasi", "10.2, 10.4, 10.1, 10.3, 10.2")
        
        if st.button("Hitung % RSD", type="primary"):
            try:
                vals = [float(i.strip()) for i in input_rsd.split(",")]
                mean_v = np.mean(vals)
                sd_v = np.std(vals, ddof=1)
                rsd_v = (sd_v / mean_v) * 100

                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Rata-rata (Mean)", f"{mean_v:.4f}")
                col_b.metric("Standar Deviasi (SD)", f"{sd_v:.4f}")
                col_c.metric("% RSD", f"{rsd_v:.2f}%")
            except ValueError:
                st.error("Pastikan semua input berupa angka yang dipisahkan dengan koma.")

    else:
        st.write("Masukkan hasil pengujian dua sampel sejenis (Duplo):")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            d1 = st.number_input("Hasil Pengujian 1 ($x_1$)", value=10.2)
        with col_d2:
            d2 = st.number_input("Hasil Pengujian 2 ($x_2$)", value=10.5)

        if st.button("Hitung % RPD", type="primary"):
            rpd_v = (abs(d1 - d2) / ((d1 + d2) / 2)) * 100
            st.metric("% RPD (Relative Percent Difference)", f"{rpd_v:.2f}%")


# =========================================================================
# MENU 4: UJI AKURASI
# =========================================================================
with tab4:
    st.header("🎯 Uji Akurasi (% Recovery)")
    st.latex(r"\% \text{Recovery} = \frac{C_{\text{terukur}} - C_{\text{sampel}}}{C_{\text{spike}}} \times 100\%")

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        c_sampel = st.number_input("Konsentrasi Sampel Tanpa Spike ($C_{\text{sampel}}$)", value=5.0)
    with col_s2:
        c_spike = st.number_input("Konsentrasi Standard yang Ditambahkan ($C_{\text{spike}}$)", value=5.0)
    with col_s3:
        c_terukur = st.number_input("Konsentrasi Sampel + Spike Terukur ($C_{\text{terukur}}$)", value=9.8)

    if st.button("Hitung % Recovery", type="primary"):
        recovery = ((c_terukur - c_sampel) / c_spike) * 100
        st.metric("Hasil % Recovery", f"{recovery:.2f}%")
        
        if 80 <= recovery <= 120:
            st.success("✅ Nilai % Recovery memenuhi kriteria keberterimaan (80% - 120%).")
        else:
            st.warning("⚠️ Nilai % Recovery di luar rentang standar (80% - 120%).")
