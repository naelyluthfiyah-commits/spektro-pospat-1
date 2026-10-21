import streamlit as st
import numpy as np
from scipy import stats

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Simulasi & Analisis UV-Vis Fosfat", layout="wide")

st.title("🧪 Simulasi & Komputer Data UV-Vis Shimadzu UV-1800")
st.markdown("### Analisis Penetapan Fosfat - Metode Biru Molibdat")

# Layout Utama Dibagi 2 Kolom
col_visual, col_data = st.columns([1.1, 1])

with col_visual:
    st.subheader("🔬 Visualisasi Bagian Dalam & Alur Kerja Alat")
    
    # Simulasi Skema Animasi Jalur Optik via HTML/Canvas
    html_animasi = """
    <div style="background-color: #1e1e1e; padding: 12px; border-radius: 8px; color: white; text-align: center;">
        <p style="font-size: 13px; margin-bottom: 8px; font-weight: bold;">Simulasi Jalur Sinar Double-Beam UV-1800</p>
        <canvas id="optikCanvas" width="420" height="200" style="background-color: #111; border-radius: 6px;"></canvas>
    </div>
    <script>
        const canvas = document.getElementById('optikCanvas');
        const ctx = canvas.getContext('2d');
        let xPos = 30;
        
        function drawOptics() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 1. Sumber Cahaya
            ctx.fillStyle = "orange"; ctx.fillRect(15, 80, 25, 40);
            ctx.fillStyle = "white"; ctx.font = "9px Arial"; ctx.fillText("Sumber", 10, 75);
            
            // 2. Monokromator
            ctx.fillStyle = "lightblue"; ctx.fillRect(70, 75, 35, 50);
            ctx.fillText("Monokro-", 65, 63); ctx.fillText("mator", 70, 138);
            
            // 3. Beamsplitter
            ctx.fillStyle = "purple";
            ctx.beginPath(); ctx.moveTo(130, 65); ctx.lineTo(150, 100); ctx.lineTo(140, 100); ctx.lineTo(120, 65); ctx.fill();
            
            // 4. Kuvet (Blangko/Sampel)
            ctx.fillStyle = "yellow"; ctx.fillRect(200, 40, 25, 25);
            ctx.fillStyle = "lightgreen"; ctx.fillRect(200, 135, 25, 25);
            ctx.fillText("Ref", 203, 33); ctx.fillText("Sampel", 195, 175);
            
            // 5. Detektor
            ctx.fillStyle = "salmon"; ctx.fillRect(290, 40, 25, 25); ctx.fillRect(290, 135, 25, 25);
            ctx.fillText("Detektor", 282, 33);
            
            // Jalur Garis Optik
            ctx.strokeStyle = "rgba(255,255,255,0.3)"; ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(40, 100); ctx.lineTo(70, 100);
            ctx.moveTo(105, 100); ctx.lineTo(125, 82);
            ctx.moveTo(135, 82); ctx.lineTo(200, 52); ctx.moveTo(225, 52); ctx.lineTo(290, 52);
            ctx.moveTo(135, 82); ctx.lineTo(200, 148); ctx.moveTo(225, 148); ctx.lineTo(290, 148);
            ctx.stroke();
            
            // Titik Sinar Bergerak
            ctx.fillStyle = "red";
            ctx.beginPath(); ctx.arc(xPos, 100, 4, 0, Math.PI * 2); ctx.fill();
            
            xPos += 2;
            if (xPos > 340) xPos = 30;
            requestAnimationFrame(drawOptics);
        }
        drawOptics();
    </script>
    """
    st.components.v1.html(html_animasi, height=240)
    
    st.info(
        "*Penjelasan Prosedur Alat (Metode Biru Molibdat):*\n"
        "1. *Warming Up:* Nyalakan alat 15–30 menit agar lampu stabil.\n"
        "2. *Panjang Gelombang Maksimum ($\\lambda$ maks):* Masukkan blanko aquadest, atur mode Spectrum Scan, lalu cari puncak serapan pada kisaran *700–880 nm* tempat kompleks biru molibdat menyerap optimal.\n"
        "3. *Pengukuran Sampel Air/Pupuk:* Baca nilai absorbansi sampel duplo dan larutan spike akurasi pada $\\lambda$ maks tersebut."
    )

with col_data:
    st.subheader("💻 Komputer Data: Input & Kalkulator")
    
    # Input Data Kurva Standar Fosfat
    st.markdown("*1. Data Deret Standar Fosfat (ppm)*")
    kons_input = st.text_input("Konsentrasi Standar:", "0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6")
    abs_std_input = st.text_input("Absorbansi Standar (Blangko s.d 0.6 ppm):", "0, 0.12, 0.25, 0.37, 0.50, 0.62, 0.75")
    
    # Input Data Sampel Air / Pupuk
    st.markdown("*2. Data Sampel Uji (Duplo / Spike)*")
    abs_samp_input = st.text_input("Absorbansi Sampel (pisahkan koma):", "0.31, 0.315, 0.45")
    
    proses_btn = st.button("Hitung Regresi & Tampilkan Kurva", type="primary")

# Eksekusi Kalkulator & Grafik
if proses_btn:
    try:
        kons_standar = np.array([float(x.strip()) for x in kons_input.split(',')])
        abs_standar = np.array([float(y.strip()) for y in abs_std_input.split(',')])
        abs_sampel = np.array([float(y.strip()) for y in abs_samp_input.split(',')])
        
        if len(kons_standar) != len(abs_standar) or len(kons_standar) < 2:
            st.error("Jumlah data konsentrasi dan absorbansi standar harus sama dan minimal 2 data.")
        else:
            # Perhitungan Regresi Linear (Hukum Lambert-Beer: A = mC + c)
            slope, intercept, r_value, p_value, std_err = stats.linregress(kons_standar, abs_standar)
            r_squared = r_value**2
            
            # Hitung Konsentrasi Sampel: C = (A - intercept) / slope
            kons_sampel_dihitung = (abs_sampel - intercept) / slope
            
            st.markdown("---")
            st.subheader("📈 Hasil Analisis & Perhitungan Regresi")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Slope (m)", f"{slope:.4f}")
            m2.metric("Intercept (c)", f"{intercept:.4f}")
            m3.metric("Koefisien Determinasi (R²)", f"{r_squared:.4f}")
            
            if r_squared < 0.99:
                st.warning("Peringatan: Kelinearan kurva kalibrasi kurang baik ($R^2 < 0.99$). Periksa kembali larutan standar Anda.")
            else:
                st.success("Status: Kurva kalibrasi sangat linear dan valid.")
                
            st.write("*Hasil Konsentrasi Sampel Fosfat Terhitung:*")
            for i, (a_val, c_val) in enumerate(zip(abs_sampel, kons_sampel_dihitung)):
                st.write(f"- *Sampel {i+1}: Absorbansi = {a_val:.4f} $\rightarrow$ **Konsentrasi = {c_val:.4f} mg/L (ppm)*")
            
            # Plot Kurva Kalibrasi
            st.markdown("---")
            st.subheader("📉 Diagram Kurva Kalibrasi Biru Molibdat")
            
            fig, ax = plt.subplots(figsize=(8, 4.8))
            kons_fit = np.linspace(min(kons_standar), max(kons_standar), 100)
            abs_fit = slope * kons_fit + intercept
            
            ax.scatter(kons_standar, abs_standar, color='blue', label='Data Standar Fosfat', s=80, zorder=3)
            ax.plot(kons_fit, abs_fit, color='red', linestyle='--', label=f'Regresi: A = {slope:.4f}C + {intercept:.4f}', zorder=2)
            
            for i, (a_val, c_val) in enumerate(zip(abs_sampel, kons_sampel_dihitung)):
                ax.scatter(c_val, a_val, color='green', marker='X', s=100, 
            label=f'Sampel {i+1}' if i == 1 else "", zorder=4)
                ax.plot([c_val, c_val], [0, a_val], color='green', linestyle=':', alpha=0.6)
                ax.plot([0, c_val], [a_val, a_val], color='green', linestyle=':', alpha=0.6)
            
            ax.set_title('Kurva Kalibrasi Penetapan Fosfat (Metode Biru Molibdat)', fontsize=11, fontweight='bold')
            ax.set_xlabel('Konsentrasi Fosfat (ppm / mg/L)', fontsize=9)
            ax.set_ylabel('Absorbansi (A)', fontsize=9)
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.legend(loc='lower right', fontsize=8)
            
            st.pyplot(fig)
            
    except Exception as e:
        st.error(f"Terjadi kesalahan dalam format input data: {e}")
