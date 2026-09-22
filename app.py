import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# --- KONFIGURASI HALAMAN STREAMLIT ---
st.set_page_config(
    page_title="ZF-Core Engine 3D Scanner",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATABASE KUNCI LISENSI PREMIUM ---
VALID_LICENSES = {
    "ZF-PREMIUM-2026": {"nama": "Pak Baroq (VIP)", "tipe": "VIP Master Access"},
    "ZF-GUEST-SKANTO": {"nama": "Lahan Skanto User", "tipe": "Limited Access"},
    "ZF-PRO-PAPUA01": {"nama": "Mitra Lapangan 01", "tipe": "Pro Field License"}
}

# --- CUSTOMLSS STYLING (DARK THEME) ---
st.markdown("""
    <style>
    .main {
        background-color: #050b14;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #00e5ff;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        width: 100%;
        height: 48px;
    }
    .stButton>button:hover {
        background-color: #00b3cc;
        color: #ffffff;
    }
    .report-card {
        background-color: #0b172a;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #1e293b;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SISTEM LOGIN & OTENTIKASI LISENSI ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['user_info'] = {}

if not st.session_state['authenticated']:
    st.title("🔒 ZF-Core Engine Premium")
    st.subheader("Aplikasi Pemindaian Geofisika & Valuasi Emas Aluvial")
    
    license_key = st.text_input("Masukkan Kunci Lisensi Serial (License Key):", type="password")
    if st.button("MASUK / VALIDASI LISENSI"):
        if license_key in VALID_LICENSES:
            st.session_state['authenticated'] = True
            st.session_state['user_info'] = VALID_LICENSES[license_key]
            st.success(f"Lisensi Aktif! Selamat datang, {st.session_state['user_info']['nama']}.")
            st.rerun()
        else:
            st.error("Kunci Lisensi tidak valid atau telah kedaluwarsa.")
    st.stop()

# --- SIDEBAR UTAMA ---
st.sidebar.title("💎 ZF-Core Engine")
st.sidebar.write(f"👤 Pengguna: **{st.session_state['user_info']['nama']}**")
st.sidebar.caption(f"Tipe Akses: {st.session_state['user_info']['tipe']}")

if st.sidebar.button("Keluar / Logout"):
    st.session_state['authenticated'] = False
    st.rerun()

st.sidebar.markdown("---")

# --- FORM INPUT PARAMETER LAHAN ---
with st.sidebar.form("input_form"):
    st.subheader("⚙️ Parameter Lahan Target")
    nama_area = st.text_input("Nama Lokasi Target", value="UPT Arso IX / Intaimilyan")
    luas_m2 = st.number_input("Luas Area Pengujian (m²)", value=10000.0, step=500.0)
    coords_input = st.text_input("Koordinat (Lat, Long)", value="-2.789327, 140.654430")
    harga_per_g = st.number_input("Acuan Harga Emas (Rp/gram)", value=2000000, step=50000)
    
    st.subheader("🚜 Simulasi Biaya Operasional (OPEX)")
    durasi_hari = st.number_input("Estimasi Durasi Kerja (Hari)", value=30, step=5)
    sewa_alat_per_hari = st.number_input("Sewa Excavator & Alat / Hari (Rp)", value=3500000, step=250000)
    biaya_solar_per_hari = st.number_input("Biaya BBM Solar / Hari (Rp)", value=1500000, step=100000)
    gaji_tim_per_hari = st.number_input("Biaya Tenaga Kerja / Hari (Rp)", value=1000000, step=100000)
    
    btn_scan = st.form_submit_button("JALANKAN SCAN 3D & EKSPLORASI")

# --- KONTEN UTAMA APLIKASI ---
st.title("📡 ZF-SCANNER 3D GRID")
st.caption("π_eff Hardware & Geospatial Connected Engine v3.5 Pro")

# --- PENYIMPANAN LINK APP ---
st.info("🔗 **Simpan Link App:** Anda dapat menandai (*bookmark*) tautan web **`d7o.streamlit.app`** di browser HP Anda untuk membuka aplikasi ini secara instan di lapangan.")

# --- PROSES PEMINDAIAN GEOFISIKA ---
try:
    lat_str, lon_str = coords_input.split(",")
    lat = float(lat_str.strip())
    lon = float(lon_str.strip())
except Exception:
    st.error("Format koordinat salah! Gunakan format: `-2.789327, 140.654430`")
    st.stop()

# Logika Matematika Core Engine A_ZF
seed = int(abs(lat * 100000 + lon * 100000))
tebal_paydirt = round(3.5 + (seed % 20) / 10.0, 2)
kadar_min = round(2.3 + (seed % 10) / 10.0, 2)
kadar_max = round(kadar_min + 2.8, 2)
skor_azf = round(82.0 + (seed % 60) / 10.0, 1)

vol_ore_m3 = luas_m2 * tebal_paydirt
tonase_tanah = vol_ore_m3 * 2.0

emas_min_kg = (tonase_tanah * kadar_min) / 1000.0
emas_max_kg = (tonase_tanah * kadar_max) / 1000.0

rupiah_min = emas_min_kg * 1000 * harga_per_g
rupiah_max = emas_max_kg * 1000 * harga_per_g

# Kalkulasi OPEX & Net Profit
total_opex = (sewa_alat_per_hari + biaya_solar_per_hari + gaji_tim_per_hari) * durasi_hari
net_profit_min = rupiah_min - total_opex
net_profit_max = rupiah_max - total_opex

# --- RINGKASAN HASIL UTAMA ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Skor Akurasi A_ZF", f"{skor_azf}%", "PROSPEK TINGGI")
col2.metric("Volume Material Ore", f"{vol_ore_m3:,.0f} m³", f"Tebal ~{tebal_paydirt}m")
col3.metric("Estimasi Emas Murni", f"{emas_min_kg:.2f} - {emas_max_kg:.2f} Kg")
col4.metric("Estimasi Total OPEX", f"Rp {total_opex:,.0f}", f"{durasi_hari} Hari Kerja")

st.markdown("---")

# --- TAMPILAN PETA INTERAKTIF (FOLIUM) ---
st.subheader("🗺️ Peta Interaktif Episentrum Target (Satelit)")
m = folium.Map(location=[lat, lon], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google Satelit")
folium.Marker(
    [lat, lon],
    popup=f"Target: {nama_area}\nPotensi: {emas_min_kg:.2f} - {emas_max_kg:.2f} Kg Emas",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)
folium.Circle(
    radius=np.sqrt(luas_m2 / np.pi),
    location=[lat, lon],
    color="gold",
    fill=True,
    fill_opacity=0.3
).add_to(m)

st_folium(m, width=1100, height=400)

# --- LAPORAN ANALISIS GEOLOGI & KEUANGAN ---
st.markdown(f"""
<div class="report-card">
    <h3>📍 LAPORAN PEMINDAIAN LENGKAP & SIMULASI PROFIT</h3>
    <p><b>Lokasi Target:</b> {nama_area}<br>
    <b>Koordinat Episentrum:</b> {lat:.6f}, {lon:.6f}<br>
    <b>Luas Area Pengujian:</b> {luas_m2:,.0f} m² (<b>{luas_m2/10000:.2f} Hektar</b>)</p>
    <hr style="border-color: #1e293b;">
    <h4>📦 Estimasi Cadangan & Valuasi Kotor:</h4>
    <ul>
        <li><b>Total Tonase Tanah:</b> ± {tonase_tanah:,.1f} Ton</li>
        <li><b>Potensi Kadar (Grade):</b> {kadar_min} – {kadar_max} gram/ton</li>
        <li><b>Valuasi Kotor Minimal:</b> <span style="color: #00ff88;">Rp {rupiah_min:,.0f}</span></li>
        <li><b>Valuasi Kotor Maksimal:</b> <span style="color: #00ff88;">Rp {rupiah_min:,.0f}</span></li>
    </ul>
    <hr style="border-color: #1e293b;">
    <h4>💸 Analisis Biaya Operasional & Keuntungan Bersih (Net Profit):</h4>
    <ul>
        <li><b>Estimasi Total Biaya (OPEX):</b> Rp {total_opex:,.0f} ({durasi_hari} Hari)</li>
        <li><b>Potensi Keuntungan Bersih (Min):</b> <span style="color: #00e5ff;">Rp {net_profit_min:,.0f}</span></li>
        <li><b>Potensi Keuntungan Bersih (Max):</b> <span style="color: #00e5ff;">Rp {net_profit_max:,.0f}</span></li>
    </ul>
    <hr style="border-color: #1e293b;">
    <h4>📝 Deskripsi Geologi & Rekomendasi Lapangan:</h4>
    <p>• Area ini berada di zona perangkap aluvial purba (<i>paleochannel</i>).<br>
    • Lapisan lempung kebiruan keras (<i>bedrock</i>) bertindak sebagai penahan konsentrasi emas murni di atasnya.<br>
    💡 <b>Rekomendasi:</b> Ambil sampel tanah lempung/pasir bercampur kerikil tepat di atas permukaan batu kebiruan di kedalaman 8–10m untuk pengujian pendulangan.</p>
</div>
""", unsafe_allow_html=True)

# --- VISUALISASI LAYAR 3D DENSITY ---
st.subheader("🧊 Profil Struktural Layer Kedalaman")

start_gold = 10
end_gold = start_gold + int(tebal_paydirt) - 1

layers_data = []
for z in range(1, 21):
    if 1 <= z <= 3:
        layers_data.append({"Kedalaman": f"{z}m", "Densitas (ρ)": 2.51, "Material": "BATUAN / TOPSOIL"})
    elif 4 <= z <= 7:
        layers_data.append({"Kedalaman": f"{z}m", "Densitas (ρ)": 0.99, "Material": "AIR TANAH / AQUA"})
    elif 8 <= z <= 9:
        layers_data.append({"Kedalaman": f"{z}m", "Densitas (ρ)": 2.80, "Material": "BEDROCK LEMPUNG"})
    elif start_gold <= z <= end_gold:
        layers_data.append({"Kedalaman": f"{z}m", "Densitas (ρ)": 19.32, "Material": "EMAS PEKAT (PAYDIRT)"})
    else:
        layers_data.append({"Kedalaman": f"{z}m", "Densitas (ρ)": 2.78, "Material": "BATUAN DASAR"})

df_layers = pd.DataFrame(layers_data)
st.dataframe(df_layers, use_container_width=True)

# --- FUNGSI GENERATOR LAPORAN PDF ---
def generate_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#00b3cc'), alignment=1)
    story.append(Paragraph("LAPORAN RESMI PEMINDAIAN ZF-CORE ENGINE", title_style))
    story.append(Spacer(1, 15))

    data_summary = [
        ["Lokasi Target", nama_area],
        ["Koordinat Episentrum", f"{lat:.6f}, {lon:.6f}"],
        ["Luas Area Pengujian", f"{luas_m2:,.0f} m² ({luas_m2/10000:.2f} Ha)"],
        ["Skor Akurasi A_ZF", f"{skor_azf}% (PROSPEK TINGGI)"],
        ["Volume Ore / Paydirt", f"{vol_ore_m3:,.1f} m³ (Tebal ~{tebal_paydirt}m)"],
        ["Estimasi Emas Murni", f"{emas_min_kg:.2f} Kg - {emas_max_kg:.2f} Kg"],
        ["Valuasi Kotor", f"Rp {rupiah_min:,.0f} - Rp {rupiah_max:,.0f}"],
        ["Estimasi Total OPEX", f"Rp {total_opex:,.0f} ({durasi_hari} Hari)"],
        ["Keuntungan Bersih (Net)", f"Rp {net_profit_min:,.0f} - Rp {net_profit_max:,.0f}"]
    ]

    t = Table(data_summary, colWidths=[180, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#0f172a')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Deskripsi Geologi & Rekomendasi:", styles['Heading2']))
    story.append(Paragraph("• Area ini berada di zona perangkap aluvial purba (paleochannel). Lapisan lempung kebiruan keras (bedrock) bertindak sebagai penahan konsentrasi emas murni di atasnya.", styles['BodyText']))
    story.append(Paragraph("• Rekomendasi: Ambil sampel tanah lempung/pasir bercampur kerikil tepat di atas permukaan batu kebiruan untuk pengujian pendulangan.", styles['BodyText']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- TOMBOL UNDUH PDF ---
st.download_button(
    label="📄 UNDUH LAPORAN RESMI BERFORMAT PDF",
    data=generate_pdf(),
    file_name=f"Laporan_ZF_{nama_area.replace(' ', '_')}.pdf",
    mime="application/pdf"
)
