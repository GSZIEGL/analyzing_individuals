import io
import math
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

# =========================
# CLEAN PRINT + UI STYLE
# =========================
st.markdown("""
<style>
.block-container {max-width:1300px; padding-top:10px;}

.card {
    background:#141821;
    border-radius:14px;
    padding:14px;
    margin-bottom:10px;
}

img {border-radius:12px;}

.player-img img {
    max-height:260px;
    object-fit:contain;
}

@media print {
    header, footer, .stSidebar {display:none !important;}
    .card {page-break-inside:avoid;}
    .section {page-break-inside:avoid;}
    body {background:white;}
}
</style>
""", unsafe_allow_html=True)

# =========================
# FULL POSITION SET
# =========================
POSITION_METRICS = {
    "GK": ["Goals conceded","Saves","Clean sheets"],
    "CB": ["Interceptions","Tackles","Air challenges won, %","Passes"],
    "LB": ["Assists","Key passes","Progressive passes","Dribbles"],
    "RB": ["Assists","Key passes","Progressive passes","Dribbles"],
    "LDM": ["Interceptions","Passes","Challenges won, %"],
    "RDM": ["Interceptions","Passes","Challenges won, %"],
    "CM": ["Passes","Assists","Key passes","Progressive passes"],
    "CAM": ["Goals","Assists","xG","Key passes","Dribbles"],
    "LW": ["Goals","xG","Dribbles","Shots"],
    "RW": ["Goals","xG","Dribbles","Shots"],
    "CF": ["Goals","xG","Shots","Assists"],
    "ST": ["Goals","xG","Shots","Shots on target"]
}

# =========================
# LOAD
# =========================
def load(file):
    df = pd.read_csv(file, sep=";").reset_index(drop=True)

    p1 = str(df.iloc[1,2])
    p2 = str(df.iloc[1,3])

    data = []
    for i in range(len(df)):
        try:
            metric = df.iloc[i,0]
            a = float(str(df.iloc[i,2]).replace(",","."))
            b = float(str(df.iloc[i,3]).replace(",","."))
            data.append({"metric":metric,"a":a,"b":b})
        except:
            continue

    return p1, p2, pd.DataFrame(data)

# =========================
# RADAR (CLEAN)
# =========================
def radar(data,p1,p2):

    labels = data["metric"].tolist()
    N = len(labels)

    max_vals = np.maximum(data["a"],data["b"]) * 1.2
    a = data["a"]/max_vals
    b = data["b"]/max_vals

    pts_a=[]
    pts_b=[]

    for i in range(N):
        ang = 2*np.pi*i/N - np.pi/2
        pts_a.append(f"{250+180*a.iloc[i]*np.cos(ang)},{250+180*a.iloc[i]*np.sin(ang)}")
        pts_b.append(f"{250+180*b.iloc[i]*np.cos(ang)},{250+180*b.iloc[i]*np.sin(ang)}")

    pts_a.append(pts_a[0])
    pts_b.append(pts_b[0])

    svg=f'<svg width="500" height="500">'
    svg+=f'<polygon points="{" ".join(pts_a)}" fill="blue" opacity="0.35"/>'
    svg+=f'<polygon points="{" ".join(pts_b)}" fill="green" opacity="0.35"/>'
    svg+='</svg>'

    st.markdown(svg, unsafe_allow_html=True)
    st.markdown(f"🔵 {p1} | 🟢 {p2}")

# =========================
# APP
# =========================
st.title("SCOUT COMPARISON")

file = st.file_uploader("CSV", type=["csv"])
img1 = st.file_uploader("Player 1 image")
img2 = st.file_uploader("Player 2 image")

if not file:
    st.stop()

p1,p2,data = load(file)

pos = st.selectbox("Poszt", list(POSITION_METRICS.keys()))
metrics = POSITION_METRICS[pos]

filtered = data[data["metric"].isin(metrics)]

# =========================
# HEADER (NO EMPTY BOX!)
# =========================
col1,col2 = st.columns(2)

with col1:
    st.subheader(p1)
    if img1:
        st.markdown('<div class="player-img">', unsafe_allow_html=True)
        st.image(img1)
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.subheader(p2)
    if img2:
        st.markdown('<div class="player-img">', unsafe_allow_html=True)
        st.image(img2)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# RADAR + TEXT (NO OVERLAP)
# =========================
c1,c2 = st.columns([1,1])

with c1:
    radar(filtered.head(6),p1,p2)

with c2:
    st.markdown("### Konklúzió")
    better_a = (filtered["a"]>filtered["b"]).sum()
    better_b = (filtered["b"]>filtered["a"]).sum()

    st.write(f"{p1} jobb {better_a} mutatóban")
    st.write(f"{p2} jobb {better_b} mutatóban")

st.markdown("---")

# =========================
# METRICS (CLEAN BLOCKS)
# =========================
st.markdown("### Kulcsmutatók")

for _,r in filtered.iterrows():
    col1,col2,col3 = st.columns([2,1,1])
    col1.write(r["metric"])

    maxv=max(r["a"],r["b"])

    col2.progress(r["a"]/maxv)
    col3.progress(r["b"]/maxv)

st.markdown(f"🔵 {p1} | 🟢 {p2}")

# =========================
# TABLE (SAFE)
# =========================
st.markdown("### Táblázat")

df_show = filtered.copy()
df_show.columns=["Metric","A","B"]

st.table(df_show)
