from __future__ import annotations

import base64
import os
import sys

import plotly.express as px
import streamlit as st


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
BACKGROUND_IMAGE_PATH = os.path.join(PROJECT_ROOT, "image_0.png")

if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

try:
    from driver_team_circuit_constants import F1_2026_TRACKS
    from engine import get_f1_prediction
    from engine_race import get_f1_race_prediction
    from probability import get_probabilities
    from probability_race import get_race_probabilities
except ImportError as exc:
    st.error(f"Critical startup error: prediction modules could not be loaded. {exc}")
    st.stop()


def get_base64_of_bin_file(file_path: str) -> str:
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode()


@st.cache_data(show_spinner=False)
def run_ranking(track: str, rain: int, mode: str):
    if mode == "Race":
        return get_f1_race_prediction(track, rain)
    return get_f1_prediction(track, rain)


@st.cache_data(show_spinner=False)
def run_probabilities(track: str, rain: int, mode: str):
    if mode == "Race":
        return get_race_probabilities(track, rain)
    return get_probabilities(track, rain)


st.set_page_config(
    page_title="F1 2026 Prediction Center",
    layout="wide",
)

if os.path.exists(BACKGROUND_IMAGE_PATH):
    b64_background = get_base64_of_bin_file(BACKGROUND_IMAGE_PATH)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(90deg, rgba(0, 0, 0, 0.88), rgba(0, 0, 0, 0.64)),
                url("data:image/png;base64,{b64_background}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .block-container {{
            background-color: rgba(0, 0, 0, 0.78);
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 12px;
            padding: 36px !important;
            margin-top: 38px;
        }}
        h1, h2, h3, p, span, label {{
            color: white !important;
        }}
        .stButton > button {{
            width: 100%;
            min-height: 3.25rem;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.28);
            background-color: rgba(225, 6, 0, 0.76);
            color: white;
            font-weight: 700;
        }}
        .stButton > button:hover {{
            border-color: white;
            background-color: rgba(225, 6, 0, 0.94);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


selected_track = st.sidebar.selectbox("Grand Prix", list(F1_2026_TRACKS.keys()))
st.sidebar.markdown("---")
rain_status = 1 if st.sidebar.checkbox("Wet session") else 0
st.sidebar.markdown("---")
prediction_mode = st.sidebar.radio("Session", ["Qualifying", "Race"])

track_meta = F1_2026_TRACKS[selected_track]

st.title("F1 2026 Prediction Center")
st.caption(
    f"Round {track_meta['Round']} / {track_meta['Event']} / "
    f"{'Wet' if rain_status else 'Dry'} {prediction_mode.lower()} scenario"
)

classification_col, probability_col = st.columns([1, 1], gap="large")

with classification_col:
    if st.button("Show classification"):
        results = run_ranking(selected_track, rain_status, prediction_mode)
        score_col = "AI_Race_Score" if prediction_mode == "Race" else "AI_Score"

        if results is None:
            st.error("Prediction could not be calculated for this scenario.")
        else:
            st.subheader(f"{selected_track} expected order")
            table = results[["Rank", "Driver", "Team"]].head(22).copy()
            table.columns = ["No", "Driver", "Team"]
            st.table(table.set_index("No"))
            if score_col in results.columns:
                st.dataframe(
                    results[["Rank", "Driver", "Team", score_col]]
                    .head(22)
                    .set_index("Rank"),
                    use_container_width=True,
                )

with probability_col:
    if st.button("Show win probabilities"):
        probabilities = run_probabilities(selected_track, rain_status, prediction_mode)

        if probabilities is None:
            st.error("Probabilities could not be calculated for this scenario.")
        else:
            st.subheader(f"{selected_track} win probability")
            fig = px.pie(
                probabilities.head(8),
                values="Probability",
                names="Driver",
                hole=0.42,
                color_discrete_sequence=px.colors.sequential.RdBu,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "white"},
                margin={"l": 4, "r": 4, "t": 16, "b": 4},
            )
            st.plotly_chart(fig, use_container_width=True)

            probability_table = probabilities.head(8).copy()
            probability_table["No"] = range(1, len(probability_table) + 1)
            st.dataframe(
                probability_table[["No", "Driver", "Team", "Probability"]]
                .set_index("No")
                .style.format({"Probability": "{:.2f}%"}),
                use_container_width=True,
            )

st.divider()
st.caption("Academic project. Not affiliated with Formula 1, FIA, or any constructor.")
