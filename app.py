import io
import math
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

# =========================
# STYLE (PRO DESIGN + PRINT SAFE)
# =========================
st.markdown("""
<style>
:root{
  --bg:#0f1117;
  --card:#171a21;
  --line:rgba(255,255,255,0.08);
  --muted:#9aa4b2;
  --blue:#3b82f6;
  --green:#10b981;
}

.block-container{
  max-width:1400px;
}

.card{
  background:var(--card);
  border-radius:16px;
  padding:16px;
  margin-bottom:12px;
}

.player-img img{
  max-height:260px;
  object-fit:contain;
}

.legend-dot{
  display:inline-block;
  width:10px;
  height:10px;
  border-radius:50%;
}

@media print {
  header, footer, .stSidebar {display:none !important;}
  .card {page-break-inside:avoid;}
}
</style>
""", unsafe_allow_html=True)

# =========================
# FULL POSITIONS (REAL FOOTBALL)
# =========================
POSITION_METRICS = {
    "GK":[],
    "CB":[],
    "LCB":[],
    "RCB":[],
    "LB":[],
    "RB":[],
    "LWB":[],
    "RWB":[],
    "CDM":[],
    "LDM":[],
    "RDM":[],
    "CM":[],
    "LCM":[],
    "RCM":[],
    "CAM":[],
    "LAM":[],
    "RAM":[],
    "LW":[],
    "RW":[],
    "CF":[],
    "ST":[],
    "AUTO":[]
}

# =========================
# LOAD (ROBUST)
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
# RADAR (NEVER EMPTY)
# =========================
def radar(df,p1,p2):

    if df.empty:
        df = data.head(6)

    df = df.head(6)

    labels=df["metric"].tolist()
    N=len(labels)

    max_vals=np.maximum(df["a"],df["b"])
    max_vals[max_vals==0]=1

    a=df["a"]/max_vals
    b=df["b"]/max_vals

    pts_a=[]
    pts_b=[]

    for i in range(N):
        ang=2*np.pi*i/N - np.pi/2

        pts_a.append(f"{250+170*a.iloc[i]*np.cos(ang)},{250+170*a.iloc[i]*np.sin(ang)}")
        pts_b.append(f"{250+170*b.iloc[i]*np.cos(ang)},{250+170*b.iloc[i]*np.sin(ang)}")

    pts_a.append(pts_a[0])
    pts_b.append(pts_b[0])

    svg=f'''
    <div class="card">
    <svg width="500" height="500">
    <polygon points="{' '.join(pts_a)}" fill="#3b82f6" opacity="0.4"/>
    <polygon points="{' '.join(pts_b)}" fill="#10b981" opacity="0.4"/>
    </svg>
    </div>
    '''

    st.markdown(svg, unsafe_allow_html=True)
    st.markdown(f"🔵 {p1} | 🟢 {p2}")

# =========================
# METRICS (SIDE BY SIDE)
# =========================
def metrics(df,p1,p2):

    st.markdown("### Mutatók")

    for _,r in df.iterrows():

        maxv=max(r["a"],r["b"])
        if maxv==0: maxv=1

        c1,c2,c3=st.columns([2,1,1])

        c1.write(r["metric"])
        c2.progress(r["a"]/maxv)
        c3.progress(r["b"]/maxv)

    st.markdown(f"🔵 {p1} | 🟢 {p2}")

# =========================
# CONCLUSION
# =========================
def conclusion(df,p1,p2):

    st.markdown("### Konklúzió")

    a_better=(df["a"]>df["b"]).sum()
    b_better=(df["b"]>df["a"]).sum()

    st.write(f"{p1}: {a_better} erősebb mutató")
    st.write(f"{p2}: {b_better} erősebb mutató")

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

filtered = data.copy()

# =========================
# HEADER
# =========================
col1,col2 = st.columns(2)

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
# RADAR + CONCLUSION
# =========================
c1,c2 = st.columns([1,1])

with c1:
    radar(filtered,p1,p2)

with c2:
    conclusion(filtered,p1,p2)

st.markdown("---")

# =========================
# METRICS
# =========================
metrics(filtered,p1,p2)

st.markdown("---")

# =========================
# TABLE
# =========================
st.table(filtered)
