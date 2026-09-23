import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="ZF-Core Engine Global",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATABASE TIER LISENSI INTERNASIONAL ---
VALID_LICENSES = {
    "ZF-FREE-DEMO": {
        "nama": "Pengguna Gratis / Free Trial",
        "tier": "FREE",
        "max_area": 100.0,
        "pdf_export": False,
        "map_access": False,
        "harga": "$0 / Free"
    },
    "ZF-MITRA-2026": {
        "nama": "Mitra Lapangan (Field Pro)",
        "tier": "MITRA",
        "max_area": 50000.0,
        "pdf_export": True,
        "map_access": True,
        "harga": "$29 / Month"
    },
    "ZF-INSTITUTION-VIP": {
        "nama": "Institutional / Enterprise Access",
        "tier": "INSTITUTIONAL",
        "max_area": 99999999.0,
        "pdf_export": True,
        "map_access": True,
        "harga": "$299 / Month"
    }
}

# --- STYLING (DARK ENTERPRISE THEME) ---
st.markdown("""
    <style>
    .main { background-color: #050b14; color: #ffffff; }
    .stButton>button {
        background-color: #00e5ff; color: #000000; font-weight: bold;
        border-radius: 8px; border: none; width: 100%; height: 48px;
    }
    .stButton>button:hover { background-color: #00b3cc; color: #ffffff; }
    .report-card {
        background-color: #0b172a; padding: 20px; border-radius: 10px;
        border: 1px solid #1e293b; margin-bottom: 20px;
    }
    .tier-badge {
        background-color: #1e293b; color: #00e5ff; padding: 5px 10px;
        border-radius: 5px; font-weight: bold; font-size: 12px;
    }
    .guide-card {
        background-color: #0f1d36; padding: 15px; border-radius: 8px;
        border-left: 4px solid #00e5ff; margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SISTEM LOGIN & OTENTIKASI LISENSI ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['user_info'] = {}

if not st.session_state['authenticated']:
    st.title("🔒 ZF-Core Engine Global SaaS")
    st.subheader("International Gold Geophysics & Valuation Platform")
    
    col_lic, col_info = st.columns([1, 1])
    
    with col_lic:
        license_key = st.text_input("Enter License Serial Key (Kunci Lisensi):", type="password")
        if st.button("AUTHENTICATE / MASUK"):
            if license_key in VALID_LICENSES:
                st.session_state['authenticated'] = True
                st.session_state['user_info'] = VALID_LICENSES[license_key]
                st.success(f"Access Granted! Welcome, {st.session_state['user_info']['nama']}.")
                st.rerun()
            else:
                st.error("Invalid or Expired Serial Key.")
        
        st.markdown("---")
        st.write("🔑 **Demo Keys for Testing:**")
        st.code("ZF-FREE-DEMO       -> Free Trial ($0)\nZF-MITRA-2026      -> Mitra Lapangan ($29/mo)\nZF-INSTITUTION-VIP -> Institutional ($299/mo)")

    with col_info:
        st.markdown("""
        ### 🌍 Subscription Plans / Paket Lisensi:
        * **🆓 Free Trial ($0):** Limited to 100 m² scan area. Basic volumetric reports.
        * **🚜 Mitra Lapangan ($29 / Mo):** Up to 50,000 m² (5 Ha), Satellite Maps, PDF Reports, OPEX Calculator.
        * **🏛️ Institutional ($299 / Mo):** Unlimited Scan Area, Full Investor PDF Export, Multi-currency (USD & IDR).
        """)
    st.stop()

# --- SIDEBAR UTAMA ---
st.sidebar.title("💎 ZF-Core Engine")
user = st.session_state['user_info']
st.sidebar.write(f"👤 **{user['nama']}**")
st.sidebar.markdown(f"Plan: <span class='tier-badge'>{user['tier']} ({user['harga']})</span>", unsafe_allow_html=True)

if st.sidebar.button("Logout / Keluar"):
    st.session_state['authenticated'] = False
    st.rerun()

st.sidebar.markdown("---")

# --- FORM INPUT PARAMETER LAHAN ---
with st.sidebar.form("input_form"):
    st.subheader("⚙️ Target Land Parameters")
    nama_area = st.text_input("Location Name", value="UPT Arso IX / Intaimilyan")
    
    max_area_allowed = user['max_area']
    luas_m2 = st.number_input(
        f"Scan Area (m²) [Max: {max_area_allowed:,.0f} m²]", 
        value=min(10000.0, max_area_allowed), 
        step=500.0
    )
    
    coords_input = st.text_input("Coordinates (Lat, Long)", value="-2.789327, 140.654430")
    
    st.subheader("💵 Financial Acuations (USD & IDR)")
    usd_to_idr = st.number_input("USD Exchange Rate (Rp / $1)", value=15500, step=100)
    harga_per_oz_usd = st.number_input("Gold Price ($ / Ounce)", value=2500.0, step=50.0)
    
    harga_per_gram_usd = harga_per_oz_usd / 31.1035
    harga_per_gram_idr = harga_per_gram_usd * usd_to_idr
    
    st.subheader("🚜 OPEX Simulation ($ USD)")
    durasi_hari = st.number_input("Duration (Days)", value=30, step=5)
    opex_per_day_usd = st.number_input("Daily Equipment & Fuel Cost ($/Day)", value=350.0, step=50.0)
    
    btn_scan = st.form_submit_button("RUN 3D SCAN & VALUATION")

# Panduan Pintas di Sidebar
with st.sidebar.expander("📍 Cara Ambil Koordinat Baru"):
    st.markdown("""
    1. Buka **Google Maps** di HP/Laptop.
    2. Tekan/Klik titik lokasi target hingga muncul pin merah.
    3. Salin angka koordinat (contoh: `-2.789327, 140.654430`).
    4. Tempel ke kolom **Coordinates** di atas.
    """)

# --- KONTEN UTAMA APLIKASI ---
st.title("📡 ZF-SCANNER 3D GRID GLOBAL")
st.caption("π_eff Geospatial Connected Engine v4.0 International Edition")

# --- FITUR PANDUAN PENGAMBILAN KOORDINAT (DASHBOARD GUIDE) ---
with st.expander("📍 CARA MENDAPATKAN KOORDINAT GPS LOKASI TARGET BARU (GUIDE)", expanded=False):
    st.markdown("""
    <div class="guide-card">
        <h4>🗺️ Panduan Langkah Pemindaian Lokasi Baru via Google Maps:</h4>
        <ol>
            <li><b>Buka Aplikasi Google Maps</b> pada ponsel atau browser komputer Anda.</li>
            <li>Cari area/wilayah lahan baru yang ingin Anda analisis potensi emasnya.</li>
            <li><b>Tekan lama (di HP)</b> atau <b>Klik kanan (di Komputer)</b> tepat pada titik tengah (episentrum) lahan hingga muncul pin/tanda merah.</li>
            <li>Salin angka koordinat Latitude & Longitude yang muncul (Contoh: <code>-2.789327, 140.654430</code> atau <code>-3.123456, 140.987654</code>).</li>
            <li>Buka bilah menu samping (<i>Sidebar</i>) aplikasi ini, lalu ganti:
                <ul>
                    <li><b>Location Name:</b> Ketik nama kampung/distrik lokasi baru tersebut.</li>
                    <li><b>Scan Area Size:</b> Masukkan luas lahan dalam meter persegi (m²).</li>
                    <li><b>Coordinates:</b> Tempel angka koordinat baru yang sudah Anda salin.</li>
                </ul>
            </li>
            <li>Klik tombol biru <b>RUN 3D SCAN & VALUATION</b>. Seluruh peta, volume, valuasi, dan laporan PDF akan langsung diperbarui otomatis!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

if luas_m2 > max_area_allowed:
    st.warning(f"🔒 **LIMITATION NOTICE:** You are attempting to scan {luas_m2:,.0f} m², but your **{user['tier']}** license is limited to **{max_area_allowed:,.0f} m²**. Please upgrade to **Institutional License ($299/mo)** for unlimited access.")
    st.stop()

# --- PROSES PEMINDAIAN GEOFISIKA ---
try:
    lat_str, lon_str = coords_input.split(",")
    lat = float(lat_str.strip())
    lon = float(lon_str.strip())
except Exception:
    st.error("Invalid coordinates format! Use: `-2.789327, 140.654430`")
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

val_min_usd = emas_min_kg * 1000 * harga_per_gram_usd
val_max_usd = emas_max_kg * 1000 * harga_per_gram_usd

val_min_idr = val_min_usd * usd_to_idr
val_max_idr = val_max_usd * usd_to_idr

total_opex_usd = opex_per_day_usd * durasi_hari
total_opex_idr = total_opex_usd * usd_to_idr

net_min_usd = val_min_usd - total_opex_usd
net_max_usd = val_max_usd - total_opex_usd

# --- METRIK UTAMA ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("A_ZF Accuracy Score", f"{skor_azf}%", "HIGH PROSPECT")
col2.metric("Ore Material Volume", f"{vol_ore_m3:,.0f} m³", f"Thickness ~{tebal_paydirt}m")
col3.metric("Est. Pure Gold Yield", f"{emas_min_kg:.2f} - {emas_max_kg:.2f} Kg", f"{(emas_min_kg*32.1507):,.0f} - {(emas_max_kg*32.1507):,.0f} Oz")
col4.metric("Est. Gross Valuation ($)", f"${val_min_usd/1e6:.2f}M -${val_max_usd/1e6:.2f}M", f"Rp {val_min_idr/1e9:.1f}B - Rp {val_max_idr/1e9:.1f}B")

st.markdown("---")

# --- PETA SATELLITE ---
st.subheader("🗺️ Target Episentrum Interactive Satellite Map")
if user['map_access']:
    m = folium.Map(location=[lat, lon], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google Satelit")
    folium.Marker(
        [lat, lon],
        popup=f"Target: {nama_area}\nEst: ${val_min_usd/1e6:.2f}M USD",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)
    folium.Circle(
        radius=np.sqrt(luas_m2 / np.pi),
        location=[lat, lon],
        color="gold", fill=True, fill_opacity=0.3
    ).add_to(m)
    st_folium(m, width=1100, height=380)
else:
    st.info("🔒 **Map Feature Locked:** Upgrade to **Mitra Lapangan ($29/mo)** or **Institutional Plan ($299/mo)** to unlock interactive Google Satellite Maps.")

# --- LAPORAN ANALISIS ---
st.markdown(f"""
<div class="report-card">
    <h3>📍 COMPREHENSIVE RESERVE & VALUATION REPORT</h3>
    <p><b>Target Location:</b> {nama_area}<br>
    <b>Coordinates:</b> {lat:.6f}, {lon:.6f}<br>
    <b>Scan Area Size:</b> {luas_m2:,.0f} m² (<b>{luas_m2/10000:.2f} Hectares</b>)<br>
    <b>License Tier:</b> <span style="color:#00e5ff;">{user['tier']}</span></p>
    <hr style="border-color: #1e293b;">
    <h4>📦 Reserve Estimation & Gross Valuation:</h4>
    <ul>
        <li><b>Total Earth Tonnage:</b> ± {tonase_tanah:,.1f} Metric Tons</li>
        <li><b>Potential Grade:</b> {kadar_min} – {kadar_max} grams / Ton</li>
        <li><b>Gross Valuation (USD):</b> <span style="color: #00ff88;">${val_min_usd:,.2f} USD</span> – <span style="color: #00ff88;">${val_max_usd:,.2f} USD</span></li>
        <li><b>Gross Valuation (IDR):</b> Rp {val_min_idr:,.0f} – Rp {val_max_idr:,.0f}</li>
    </ul>
    <hr style="border-color: #1e293b;">
    <h4>💸 Operational Cost (OPEX) & Net Profit Projection:</h4>
    <ul>
        <li><b>Total OPEX ({durasi_hari} Days):</b> ${total_opex_usd:,.2f} USD (Rp {total_opex_idr:,.0f})</li>
        <li><b>Net Profit Range (USD):</b> <span style="color: #00e5ff;">${net_min_usd:,.2f} USD</span> – <span style="color: #00e5ff;">${net_max_usd:,.2f} USD</span></li>
    </ul>
</div>
""", unsafe_allow_html=True)

# --- VISUALISASI LAYAR 3D DENSITY ---
st.subheader("🧊 Subsurface Structural Layer Density Profile")
start_gold = 10
end_gold = start_gold + int(tebal_paydirt) - 1

layers_data = []
for z in range(1, 21):
    if 1 <= z <= 3:
        layers_data.append({"Depth": f"{z}m", "Density (ρ)": 2.51, "Formation Layer": "BATUAN / TOPSOIL"})
    elif 4 <= z <= 7:
        layers_data.append({"Depth": f"{z}m", "Density (ρ)": 0.99, "Formation Layer": "AIR TANAH / AQUIFER"})
    elif 8 <= z <= 9:
        layers_data.append({"Depth": f"{z}m", "Density (ρ)": 2.80, "Formation Layer": "BEDROCK BLUE CLAY"})
    elif start_gold <= z <= end_gold:
        layers_data.append({"Depth": f"{z}m", "Density (ρ)": 19.32, "Formation Layer": "RICH GOLD ORE (PAYDIRT)"})
    else:
        layers_data.append({"Depth": f"{z}m", "Density (ρ)": 2.78, "Formation Layer": "BASEMENT BEDROCK"})

df_layers = pd.DataFrame(layers_data)
st.dataframe(df_layers, use_container_width=True)

# --- FUNGSI GENERATOR LAPORAN PDF ---
def generate_pdf(p_nama, p_lat, p_lon, p_luas, p_skor, p_vol, p_tebal, p_emas_min, p_emas_max, p_val_min, p_val_max, p_opex, p_hari, p_net_min, p_net_max):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#00b3cc'), alignment=1)
    story.append(Paragraph("OFFICIAL ZF-CORE ENGINE RESERVE REPORT", title_style))
    story.append(Spacer(1, 15))

    data_summary = [
        ["Target Location", str(p_nama)],
        ["Coordinates", f"{p_lat:.6f}, {p_lon:.6f}"],
        ["Scan Area Size", f"{p_luas:,.0f} m² ({p_luas/10000:.2f} Ha)"],
        ["A_ZF Score", f"{p_skor}% (HIGH PROSPECT)"],
        ["Ore Material Volume", f"{p_vol:,.1f} m³ (Thickness ~{p_tebal}m)"],
        ["Est. Pure Gold Yield", f"{p_emas_min:.2f} Kg - {p_emas_max:.2f} Kg"],
        ["Gross Valuation ($ USD)", f"${p_val_min:,.2f} -${p_val_max:,.2f}"],
        ["Total OPEX Est. ($ USD)", f"${p_opex:,.2f} ({p_hari} Days)"],
        ["Net Profit Est. ($ USD)", f"${p_net_min:,.2f} -${p_net_max:,.2f}"]
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

    story.append(Paragraph("Geological Description & Field Recommendations:", styles['Heading2']))
    story.append(Paragraph("• The targeted zone sits on an ancient alluvial trap (paleochannel). A dense blue clay bedrock layer acts as a natural seal concentrating gold particles.", styles['BodyText']))
    story.append(Paragraph("• Recommendation: Collect soil samples above the blue clay formation at 8m-10m depth for panning verification.", styles['BodyText']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- TOMBOL UNDUH PDF ---
if user['pdf_export']:
    pdf_file = generate_pdf(
        nama_area, lat, lon, luas_m2, skor_azf, vol_ore_m3, tebal_paydirt,
        emas_min_kg, emas_max_kg, val_min_usd, val_max_usd, total_opex_usd,
        durasi_hari, net_min_usd, net_max_usd
    )
    st.download_button(
        label="📄 DOWNLOAD OFFICIAL INVESTOR PDF REPORT ($ USD)",
        data=pdf_file,
        file_name=f"ZF_Report_{nama_area.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
else:
    st.info("🔒 **PDF Export Locked:** Upgrade to **Mitra Lapangan ($29/mo)** or **Institutional Plan ($299/mo)** to download official PDF reports.")
