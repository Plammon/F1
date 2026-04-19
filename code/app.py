import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os
import sys

# --- 1. DOSYA YOLLARI VE IMPORT ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

project_root = os.path.dirname(current_dir)
background_image_path = os.path.join(project_root, 'image_0.png') 

try:
    from engine import get_f1_prediction
    from probability import get_probabilities 
    from driver_team_circuit_constants import F1_2026_TRACKS
except ImportError as e:
    st.error(f"❌ Kritik Hata: Modüller yüklenemedi! {e}")
    sys.exit(1)

# --- 2. GÖRSEL AYARLAR (CSS) ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

st.set_page_config(page_title="F1 2026 Strateji Merkezi", layout="wide", page_icon="🏎️")

if os.path.exists(background_image_path):
    b64_background = get_base64_of_bin_file(background_image_path)
    st.markdown(f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{b64_background}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .block-container {{
            background-color: rgba(0, 0, 0, 0.75); 
            border-radius: 20px;
            padding: 40px !important;
            margin-top: 50px;
        }}
        .stApp {{ color: white; }}
        h1, h2, h3, p, span {{ color: white !important; }}
        
        .stButton>button {{
            width: 100%;
            border-radius: 10px;
            height: 3.5em;
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
            font-weight: bold;
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            background-color: rgba(255, 0, 0, 0.3);
            border: 1px solid red;
            transform: scale(1.02);
        }}
        </style>
        ''', unsafe_allow_html=True)

# --- 3. SİDEBAR ---
selected_gp = st.sidebar.selectbox("Pist Seçin", list(F1_2026_TRACKS.keys()))

st.sidebar.markdown("---")
st.sidebar.write("Hava Durumu") 
is_rainy = 1 if st.sidebar.checkbox("Yağmurlu Seans") else 0

st.sidebar.markdown("---")
prediction_mode = st.sidebar.radio("Seans tipi:", ["Qualify Tahmini", "Race Tahmini"])

# --- 4. ANA PANEL ---
st.title("🏎️ F1 2026 Prediction & Strategy Center")
st.markdown("19 Nisan 2026 | Canlı Veri ve Regülasyon Odaklı Tahmin Motoru")
st.divider()

col1, col2 = st.columns([1, 1])

# SOL: Seans Sonuçları (Yarış yerine Seansın yazıldı)
with col1:
    if st.button("Seansın sonuçlarını ver"):
        results = get_f1_prediction(selected_gp, is_rainy)
        if results is not None:
            st.markdown(f"### 🏁 {selected_gp} Beklenen Sıralama")
            
            final_table = results[['Rank', 'Driver', 'Team']].head(22).copy()
            final_table.columns = ['No', 'Driver', 'Team']
            
            st.table(final_table.set_index('No'))
        else:
            st.error("Hesaplama yapılamadı!")

# SAĞ: Seansın Kazanılma Dağılımı (Yarış yerine Seansın yazıldı)
with col2:
    if st.button("Seansın kazanılma dağılımı"):
        probs = get_probabilities(selected_gp, is_rainy)
        if probs is not None:
            st.markdown(f"### 🔮 {selected_gp} Galibiyet Olasılığı")
            
            fig = px.pie(probs.head(8), values='Probability', names='Driver', 
                         hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color="white")
            )
            st.plotly_chart(fig, use_container_width=True)
            
            probs_list = probs.head(8).copy()
            probs_list['No'] = range(1, len(probs_list) + 1)
            st.dataframe(
                probs_list[['No', 'Driver', 'Probability']]
                .set_index('No')
                .style.format({"Probability": "%%{:.2f}"})
            )
        else:
            st.error("Olasılıklar hesaplanamadı!")

st.markdown("---")
st.caption("©️ F1 2026 Prediction Center | Baran Karluk & Ekibi")