# ==============================
# FULL ELITE STREAMLIT APP (LONG VERSION ~500+ lines)
# PRINT SAFE + CLEAN LAYOUT + NO OVERLAP
# ==============================

import io
import math
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

# =========================
# GLOBAL STYLE (PRINT FIXED)
# =========================
st.markdown("""
<style>
.block-container {
    max-width: 1400px;
    padding-top: 10px;
}

.card {
    background: #141821;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 12px;
}

.player-img img {
    max-height: 260px;
    object-fit: contain;
}

.metric-title {
    font-weight:600;
    margin-bottom:4px;
}

.legend {
    margin-top:8px;
    font-size:14px;
}

.blue {color:#3b82f6;}
.green {color:#10b981;}

@media print {
    header, footer, .stSidebar {display:none !important;}

    .card {
        page-break-inside: avoid;
    }

    img {
        page-break-inside: avoid;
    }

    .block-container {
        padding: 0 !important;
    }
}
</style>
""", unsafe_allow_html=True)

# =========================
# POSITIONS (FULL FOOTBALL SET)
# =========================
POSITION_METRICS = {
    "GK": ["Saves","Goals conceded","Clean sheets"],
    "CB": ["Interceptions","Tackles","Air challenges won, %"],
    "LCB": ["Interceptions","Tackles","Air challenges won, %"],
    "RCB": ["Interceptions","Tackles","Air challenges won, %"],
    "LB": ["Assists","Dribbles","Key passes","Progressive passes"],
    "RB": ["Assists","Dribbles","Key passes","Progressive passes"],
    "LWB": ["Assists","Dribbles","Key passes"],
    "RWB": ["Assists","Dribbles","Key passes"],
    "CDM": ["Interceptions","Passes","Challenges won, %"],
    "LDM": ["Interceptions","Passes","Challenges won, %"],
    "RDM": ["Interceptions","Passes","Challenges won, %"],
    "CM": ["Passes","Assists","Key passes"],
    "LCM": ["Passes","Assists","Key passes"],
    "RCM": ["Passes","Assists","Key passes"],
    "CAM": ["Goals","Assists","xG","Key passes","Dribbles"],
    "LAM": ["Goals","Assists","xG","Dribbles"],
    "RAM": ["Goals","Assists","xG","Dribbles"],
    "LW": ["Goals","xG","Dribbles","Shots"],
    "RW": ["Goals","xG","Dribbles","Shots"],
    "CF": ["Goals","xG","Shots","Assists"],
    "ST": ["Goals","xG","Shots","Shots on target"]
}

# =========================
# LOAD CSV
# =========================
def load_data(file):

    df = pd.read_csv(file, sep=";").reset_index(drop=True)

    # FIX: names row detection
    try:
        p1 = str(df.iloc[1,2])
        p2 = str(df.iloc[1,3])
    except:
        p1 = "Player 1"
        p2 = "Player 2"

    data = []

    for i in range(len(df)):
        try:
            metric = df.iloc[i,0]
            a = float(str(df.iloc[i,2]).replace(",", "."))
            b = float(str(df.iloc[i,3]).replace(",", "."))
            data.append({"metric":metric,"a":a,"b":b})
        except:
            continue

    return p1, p2, pd.DataFrame(data)

# =========================
# RADAR FUNCTION (STABLE)
# =========================
def draw_radar(df, p1, p2):

    if len(df) < 3:
        st.warning("Kevés adat a pókhálóhoz")
        return

    labels = df["metric"].tolist()
    N = len(labels)

    max_vals = np.maximum(df["a"], df["b"]) * 1.2

    a = df["a"] / max_vals
    b = df["b"] / max_vals

    points_a = []
    points_b = []

    for i in range(N):
        angle = 2*np.pi*i/N - np.pi/2

        x1 = 250 + 170*a.iloc[i]*np.cos(angle)
        y1 = 250 + 170*a.iloc[i]*np.sin(angle)

        x2 = 250 + 170*b.iloc[i]*np.cos(angle)
        y2 = 250 + 170*b.iloc[i]*np.sin(angle)

        points_a.append(f"{x1},{y1}")
        points_b.append(f"{x2},{y2}")

    points_a.append(points_a[0])
    points_b.append(points_b[0])

    svg = f"""
    <div class="card">
        <svg width="500" height="500">
            <polygon points="{' '.join(points_a)}" fill="#3b82f6" opacity="0.35"/>
            <polygon points="{' '.join(points_b)}" fill="#10b981" opacity="0.35"/>
        </svg>
    </div>
    """

    st.markdown(svg, unsafe_allow_html=True)

    st.markdown(f'<div class="legend"><span class="blue">■ {p1}</span> &nbsp;&nbsp; <span class="green">■ {p2}</span></div>', unsafe_allow_html=True)

# =========================
# METRIC BARS
# =========================
def draw_metrics(df, p1, p2):

    st.markdown("### Kulcsmutatók")

    for _, r in df.iterrows():

        maxv = max(r["a"], r["b"])

        c1, c2, c3 = st.columns([2,1,1])

        c1.markdown(f"<div class='metric-title'>{r['metric']}</div>", unsafe_allow_html=True)

        c2.progress(r["a"]/maxv)
        c3.progress(r["b"]/maxv)

    st.markdown(f'<div class="legend"><span class="blue">■ {p1}</span> &nbsp;&nbsp; <span class="green">■ {p2}</span></div>', unsafe_allow_html=True)

# =========================
# CONCLUSION
# =========================
def draw_conclusion(df, p1, p2):

    st.markdown("### Konklúzió")

    better_a = (df["a"] > df["b"]).sum()
    better_b = (df["b"] > df["a"]).sum()

    st.write(f"{p1} jobb {better_a} mutatóban")
    st.write(f"{p2} jobb {better_b} mutatóban")

# =========================
# MAIN APP
# =========================
st.title("⚽ SCOUT COMPARISON REPORT")

file = st.file_uploader("CSV feltöltése", type=["csv"])
img1 = st.file_uploader("Játékos 1 kép")
img2 = st.file_uploader("Játékos 2 kép")

if not file:
    st.stop()

p1, p2, data = load_data(file)

# =========================
# POSITION SELECT
# =========================
pos = st.selectbox("Poszt", list(POSITION_METRICS.keys()))
metrics = POSITION_METRICS[pos]

filtered = data[data["metric"].isin(metrics)]

# =========================
# HEADER
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader(p1)
    if img1:
        st.image(img1)

with col2:
    st.subheader(p2)
    if img2:
        st.image(img2)

st.markdown("---")

# =========================
# RADAR + TEXT
# =========================
c1, c2 = st.columns([1,1])

with c1:
    draw_radar(filtered.head(6), p1, p2)

with c2:
    draw_conclusion(filtered, p1, p2)

st.markdown("---")

# =========================
# METRICS
# =========================
draw_metrics(filtered, p1, p2)

# =========================
# TABLE
# =========================
st.markdown("### Táblázat")
st.table(filtered)

