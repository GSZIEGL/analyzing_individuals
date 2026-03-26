import io
import math
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

# =========================
# STYLE (PRO)
# =========================
st.markdown("""
<style>
.block-container {max-width:1400px;}

.card {
    background:#141821;
    border-radius:16px;
    padding:18px;
    margin-bottom:14px;
}

.legend {margin-top:10px;font-size:14px;}
.blue {color:#3b82f6;}
.green {color:#10b981;}

@media print {
    header, footer, .stSidebar {display:none !important;}
    .card {page-break-inside:avoid;}
}
</style>
""", unsafe_allow_html=True)

# =========================
# FIX SCALE (KEY!!!)
# =========================
FIX_SCALE = {
    "Goals":1,
    "xG":1,
    "Assists":0.5,
    "Shots":6,
    "Shots on target":3,
    "Key passes":3,
    "Progressive passes":12,
    "Dribbles":7,
    "Passes":100,
    "Interceptions":6,
    "Tackles":5
}

# =========================
# POSITIONS
# =========================
POSITION_METRICS = {
    "CAM":["Goals","xG","Assists","Key passes","Dribbles"],
    "CM":["Passes","Assists","Key passes","Interceptions"],
    "CDM":["Interceptions","Tackles","Passes"],
    "CB":["Interceptions","Tackles"],
    "ST":["Goals","xG","Shots","Shots on target"],
    "LW":["Goals","xG","Dribbles","Shots"],
    "RW":["Goals","xG","Dribbles","Shots"],
    "AUTO":[]
}

# =========================
# LOAD
# =========================
def load(file):

    raw = file.read().decode("utf-8", errors="ignore")

    try:
        df = pd.read_csv(io.StringIO(raw), sep=";")
    except:
        df = pd.read_csv(io.StringIO(raw), sep=",")

    df = df.reset_index(drop=True)

    p1, p2 = "Player A", "Player B"

    for i in range(6):
        try:
            a = str(df.iloc[i,2])
            b = str(df.iloc[i,3])
            if "202" not in a:
                p1, p2 = a, b
                break
        except:
            continue

    rows=[]
    for i in range(len(df)):
        try:
            rows.append({
                "metric":str(df.iloc[i,0]),
                "a":float(str(df.iloc[i,2]).replace(",", ".")),
                "b":float(str(df.iloc[i,3]).replace(",", "."))
            })
        except:
            continue

    return p1, p2, pd.DataFrame(rows)

# =========================
# FIXED SCALING
# =========================
def scale(df):

    a_scaled=[]
    b_scaled=[]

    for _,r in df.iterrows():

        max_val = FIX_SCALE.get(r["metric"], max(r["a"],r["b"])*1.2)

        if max_val == 0:
            max_val = 1

        a_scaled.append(min(r["a"]/max_val,1))
        b_scaled.append(min(r["b"]/max_val,1))

    return np.array(a_scaled), np.array(b_scaled)

# =========================
# RADAR (PRO VERSION)
# =========================
def radar(df,p1,p2):

    if df.empty:
        df = data.head(6)

    df = df.head(6)

    labels=df["metric"].tolist()
    N=len(labels)

    a,b = scale(df)

    cx,cy=250,250
    R=170

    def point(val,angle):
        return cx+R*val*np.cos(angle), cy+R*val*np.sin(angle)

    pts_a=[]
    pts_b=[]

    for i in range(N):
        angle=2*np.pi*i/N - np.pi/2

        x1,y1=point(a[i],angle)
        x2,y2=point(b[i],angle)

        pts_a.append(f"{x1},{y1}")
        pts_b.append(f"{x2},{y2}")

    pts_a.append(pts_a[0])
    pts_b.append(pts_b[0])

    # GRID
    grid=""
    for r in [0.25,0.5,0.75,1]:
        pts=[]
        for i in range(N):
            angle=2*np.pi*i/N - np.pi/2
            x,y=point(r,angle)
            pts.append(f"{x},{y}")
        pts.append(pts[0])
        grid+=f'<polyline points="{" ".join(pts)}" fill="none" stroke="gray" opacity="0.3"/>'

    # LABELS
    texts=""
    for i,label in enumerate(labels):
        angle=2*np.pi*i/N - np.pi/2
        x,y=point(1.15,angle)
        texts+=f'<text x="{x}" y="{y}" fill="white" font-size="11" text-anchor="middle">{label}</text>'

    svg=f'''
    <div class="card">
    <svg width="500" height="500">
    {grid}
    <polygon points="{" ".join(pts_a)}" fill="#3b82f6" opacity="0.35"/>
    <polygon points="{" ".join(pts_b)}" fill="#10b981" opacity="0.35"/>
    {texts}
    </svg>
    </div>
    '''

    st.markdown(svg, unsafe_allow_html=True)

    st.markdown(f'<div class="legend"><span class="blue">■ {p1}</span> &nbsp;&nbsp; <span class="green">■ {p2}</span></div>', unsafe_allow_html=True)

# =========================
# METRICS
# =========================
def metrics(df,p1,p2):

    st.markdown("### Kulcsmutatók")

    for _,r in df.iterrows():

        maxv=max(r["a"],r["b"])
        if maxv==0: maxv=1

        c1,c2,c3=st.columns([2,1,1])

        c1.write(r["metric"])
        c2.progress(r["a"]/maxv)
        c3.progress(r["b"]/maxv)

    st.markdown(f'<div class="legend"><span class="blue">■ {p1}</span> <span class="green">■ {p2}</span></div>', unsafe_allow_html=True)

# =========================
# CONCLUSION
# =========================
def conclusion(df,p1,p2):

    st.markdown("### Konklúzió")

    a_better=(df["a"]>df["b"]).sum()
    b_better=(df["b"]>df["a"]).sum()

    st.write(f"{p1}: {a_better}")
    st.write(f"{p2}: {b_better}")

# =========================
# MAIN
# =========================
st.title("⚽ SCOUT REPORT PRO")

file = st.file_uploader("CSV", type=["csv"])
img1 = st.file_uploader("Player 1 image")
img2 = st.file_uploader("Player 2 image")

if not file:
    st.stop()

p1,p2,data = load(file)

pos = st.selectbox("Position", list(POSITION_METRICS.keys()))

if pos == "AUTO":
    filtered = data
else:
    filtered = data[data["metric"].isin(POSITION_METRICS[pos])]

if filtered.empty:
    filtered = data

# HEADER
c1,c2 = st.columns(2)

with c1:
    st.subheader(p1)
    if img1:
        st.image(img1)

with c2:
    st.subheader(p2)
    if img2:
        st.image(img2)

st.markdown("---")

# RADAR + TEXT
c1,c2 = st.columns([1,1])

with c1:
    radar(filtered,p1,p2)

with c2:
    conclusion(filtered,p1,p2)

st.markdown("---")

metrics(filtered,p1,p2)

st.markdown("---")

st.table(filtered)
