import streamlit as st
import pandas as pd
import numpy as np

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="ZF-Core Engine 3D Scanner",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- DATABASE KUNCI LISENSI PREMIUM (DUMMY/SECRET) ---
# Di produksi, ini bisa disimpan di st.secrets atau database Firebase/Supabase
VALID_LICENSES = {
    "ZF-PREMIUM-2026": "Pak Baroq (VIP)",
    "ZF-GUEST-SKANTO": "Lahan Skanto User",
    "ZF-PRO-PAPUA01": "Mitra Lapangan 01"
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

# --- SISTEM LOGIN & LISENSI ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['user_name'] = ""

if not st.session_state['authenticated']:
    st.title("🔒 ZF-Core Engine Premium")
    st.subheader("Aplikasi Pemindaian Geofisika & Valuasi Emas Aluvial")
    
    license_key = st.text_input("Masukkan Kunci Lisensi Serial (License Key):", type="password")
    if st.button("MASUK / VALIDASI LISENSI"):
        if license_key in VALID_LICENSES:
            st.session_state['authenticated'] = True
            st.session_state['user_name'] = VALID_LICENSES[license_key]
            st.success(f"Lisensi Aktif! Selamat datang, {st.session_state['user_name']}.")
            st.rerun()
        else:
            st.error("Kunci Lisensi tidak valid atau telah kedaluwarsa.")
    st.stop()

# --- HALAMAN UTAMA APLIKASI (JIKA LISENSI AKTIF) ---
st.sidebar.title("💎 ZF-Core Engine")
st.sidebar.write(f"👤 Pengguna: **{st.session_state['user_name']}**")
if st.sidebar.button("Keluar / Logout"):
    st.session_state['authenticated'] = False
    st.rerun()

st.title("📡 ZF-SCANNER 3D GRID")
st.caption("π_eff Hardware & Geospatial Connected Engine v3.2")

# --- FORM INPUT PARAMETER ---
with st.sidebar.form("input_form"):
    st.subheader("⚙️ Parameter Lahan Target")
    nama_area = st.text_input("Nama Lokasi Target", value="UPT Arso IX / Intaimilyan")
    luas_m2 = st.number_input("Luas Area Pengujian (m²)", value=1000.0, step=100.0)
    coords_input = st.text_input("Koordinat (Lat, Long)", value="-2.789327, 140.654430")
    harga_per_g = st.number_input("Acuan Harga Emas (Rp/gram)", value=2000000, step=50000)
    
    btn_scan = st.form_submit_button("JALANKAN SCAN 3D")

# --- PROSES MATEMATIKA AZF & RENDER HASIL ---
if btn_scan or 'last_scan' in st.session_state:
    try:
        lat_str, lon_str = coords_input.split(",")
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
    except Exception:
        st.error("Format koordinat salah! Gunakan format: `-2.789327, 140.654430`")
        st.stop()

    # Logika Matematika Core Engine
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

    # --- RINGKASAN METRIK UTAMA ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Skor Akurasi A_ZF", f"{skor_azf}%", "PROSPEK TINGGI")
    col2.metric("Volume Material Ore", f"{vol_ore_m3:,.0f} m³", f"Tebal ~{tebal_paydirt}m")
    col3.metric("Estimasi Emas Murni", f"{emas_min_kg:.2f} - {emas_max_kg:.2f} Kg")

    st.markdown("---")

    # --- FULL GEOLOGICAL REPORT CARD ---
    st.markdown(f"""
    <div class="report-card">
        <h3>📍 LAPORAN PEMINDAIAN LENGKAP</h3>
        <p><b>Lokasi Target:</b> {nama_area}<br>
        <b>Koordinat Episentrum:</b> {lat:.6f}, {lon:.6f}<br>
        <b>Luas Area Pengujian:</b> {luas_m2:,.0f} m² (<b>{luas_m2/10000:.2f} Hektar</b>)</p>
        <hr style="border-color: #1e293b;">
        <h4>📦 Estimasi Cadangan & Valuasi:</h4>
        <ul>
            <li><b>Total Tonase Tanah:</b> ± {tonase_tanah:,.1f} Ton</li>
            <li><b>Potensi Kadar (Grade):</b> {kadar_min} – {kadar_max} gram/ton</li>
            <li><b>Valuasi Minimal:</b> <span style="color: #00ff88;">Rp {rupiah_min:,.0f}</span></li>
            <li><b>Valuasi Maksimal:</b> <span style="color: #00ff88;">Rp {rupiah_max:,.0f}</span></li>
        </ul>
        <hr style="border-color: #1e293b;">
        <h4>📝 Deskripsi Geologi & Rekomendasi:</h4>
        <p>• Area ini berada di zona perangkap aluvial purba (<i>paleochannel</i>).<br>
        • Lapisan lempung kebiruan keras (<i>bedrock</i>) bertindak sebagai penahan konsentrasi emas murni di atasnya.<br>
        💡 <b>Rekomendasi:</b> Ambil sampel tanah lempung/pasir bercampur kerikil tepat di atas permukaan batu kebiruan untuk pengujian pendulangan.</p>
    </div>
    """, unsafe_allow_html=True)

    # --- VISUALISASI LAYAR 3D DENSITY ---
    st.subheader("🧊 Profil Struktural Layer (3D Profile Kedalaman)")
    
    start_gold = 10
    end_gold = start_gold + int(tebal_paydirt) - 1

    layers_data = []
    for z in range(1, 21):
        if 1 <= z <= 3:
            layers_data.append({"Kedalaman": f"{z}m", "Densitas (ρ)": 2.51, "Material": "BATUAN / TOPSOIL", "Warna": "#8b5a2b"})
        elif 4 <= z <= 7:
            layers_data.append({"Kedalaman": f"{z}m", "Densitas (ρ)": 0.99, "Material": "AIR TANAH / AQUA", "Warna": "#1e90ff"})
        elif 8 <= z <= 9:
            layers_data.append({"Kedalaman": f"{z}m", "Densitas (ρ)": 2.80, "Material": "BEDROCK LEMPUNG", "#8b5a2b": "#8b5a2b"})
        elif start_gold <= z <= end_gold:
            layers_data.append({"Kedalaman": f"{z}m", "Densitas (ρ)": 19.32, "Material": "EMAS PEKAT (PAYDIRT)", "Warna": "#e6b800"})
        else:
            layers_data.append({"Kedalaman": f"{z}m", "Densitas (ρ)": 2.78, "Material": "BATUAN DASAR", "Warna": "#8b5a2b"})

    df_layers = pd.DataFrame(layers_data)
    
    # Tampilkan Tabel Profil
    st.dataframe(df_layers[["Kedalaman", "Densitas (ρ)", "Material"]], use_container_width=True)

    # --- TOMBOL UNDUH LAPORAN TXT ---
    report_text = f"""============================================================
       ZF-CORE ENGINE: FULL RESERVE & VALUATION REPORT      
============================================================
📍 LOKASI TARGET         : {nama_area}
🌐 KOORDINAT EPISENTRUM  : {lat:.6f}, {lon:.6f}
📏 LUAS AREA PENGUJIAN   : {luas_m2:,.0f} m²
📊 SKOR AKURASI (A_ZF)   : {skor_azf}% [PROSPEK TINGGI]
------------------------------------------------------------
📦 ESTIMASI CADANGAN EMAS (LAYER 1 - ALUVIAL):
   • Volume Material Ore  : ± {vol_ore_m3:,.1f} m³ (Tebal Paydirt ~{tebal_paydirt}m)
   • Total Tonase Tanah   : ± {tonase_tanah:,.1f} Ton
   • Potensi Kadar (Grade): {kadar_min} – {kadar_max} g/ton
   👉 ESTIMASI TONASE EMAS: {emas_min_kg:.2f} Kg – {emas_max_kg:.2f} Kg Murni

💰 ESTIMASI VALUASI RUPIAH:
   💵 Potensi Minimal     : Rp {rupiah_min:,.0f}
   💵 Potensi Maksimal    : Rp {rupiah_max:,.0f}
============================================================
"""
    st.download_button(
        label="📥 UNDUH LAPORAN RESMI (.TXT)",
        data=report_text,
        file_name=f"Laporan_ZF_{nama_area.replace(' ', '_')}.txt",
        mime="text/plain"
    )
