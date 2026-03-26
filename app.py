# FULL ELITE SCOUT APP - LONG VERSION (PRINT OPTIMIZED)

import io
import math
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

# =========================
# STYLE (PRINT SAFE)
# =========================
st.markdown("""
<style>
.block-container {max-width:1400px;}

.card {
    background:#151922;
    border-radius:14px;
    padding:16px;
    margin-bottom:12px;
}

img {border-radius:12px;}

@media print {
    header, footer, .stSidebar {display:none !important;}
    .card {page-break-inside:avoid;}
}
</style>
""", unsafe_allow_html=True)

# =========================
# POSITIONS (FULL)
# =========================
POSITION_METRICS = {
    "GK":["Saves","Goals conceded","Clean sheets"],
    "CB":["Interceptions","Tackles","Air challenges won, %"],
    "LB":["Assists","Dribbles","Key passes"],
    "RB":["Assists","Dribbles","Key passes"],
    "CDM":["Interceptions","Passes","Challenges won, %"],
    "CM":["Passes","Assists","Key passes"],
    "CAM":["Goals","Assists","xG","Key passes","Dribbles"],
    "LW":["Goals","xG","Dribbles","Shots"],
    "RW":["Goals","xG","Dribbles","Shots"],
    "CF":["Goals","xG","Shots"],
    "ST":["Goals","xG","Shots","Shots on target"]
}

# =========================
# LOAD
# =========================
def load(file):
    df = pd.read_csv(file, sep=";")
    df = df.reset_index(drop=True)

    p1 = str(df.iloc[1,2])
    p2 = str(df.iloc[1,3])

    rows=[]
    for i in range(len(df)):
        try:
            rows.append({
                "metric":df.iloc[i,0],
                "a":float(str(df.iloc[i,2]).replace(",", ".")),
                "b":float(str(df.iloc[i,3]).replace(",", "."))
            })
        except:
            continue

    return p1,p2,pd.DataFrame(rows)

# =========================
# RADAR
# =========================
def radar(data,p1,p2):

    labels=data["metric"].tolist()
    N=len(labels)

    max_vals=np.maximum(data["a"],data["b"])*1.2
    a=data["a"]/max_vals
    b=data["b"]/max_vals

    pts_a=[]
    pts_b=[]

    for i in range(N):
        ang=2*np.pi*i/N - np.pi/2
        pts_a.append(f"{250+180*a.iloc[i]*np.cos(ang)},{250+180*a.iloc[i]*np.sin(ang)}")
        pts_b.append(f"{250+180*b.iloc[i]*np.cos(ang)},{250+180*b.iloc[i]*np.sin(ang)}")

    pts_a.append(pts_a[0])
    pts_b.append(pts_b[0])

    svg=f'<svg width="500" height="500">'
    svg+=f'<polygon points="{" ".join(pts_a)}" fill="#3b82f6" opacity="0.35"/>'
    svg+=f'<polygon points="{" ".join(pts_b)}" fill="#10b981" opacity="0.35"/>'
    svg+='</svg>'

    st.markdown(svg, unsafe_allow_html=True)
    st.write(f"🔵 {p1} | 🟢 {p2}")

# =========================
# APP
# =========================
st.title("SCOUT REPORT")

file=st.file_uploader("CSV",type=["csv"])
img1=st.file_uploader("Player 1 image")
img2=st.file_uploader("Player 2 image")

if not file:
    st.stop()

p1,p2,data=load(file)

pos=st.selectbox("Position", list(POSITION_METRICS.keys()))
metrics=POSITION_METRICS[pos]

filtered=data[data["metric"].isin(metrics)]

# =========================
# HEADER
# =========================
c1,c2=st.columns(2)

with c1:
    st.subheader(p1)
    if img1:
        st.image(img1)

with c2:
    st.subheader(p2)
    if img2:
        st.image(img2)

st.markdown("---")

# =========================
# RADAR + TEXT
# =========================
c1,c2=st.columns(2)

with c1:
    radar(filtered.head(6),p1,p2)

with c2:
    st.markdown("### Summary")
    st.write(f"{p1} better in {(filtered['a']>filtered['b']).sum()} metrics")
    st.write(f"{p2} better in {(filtered['b']>filtered['a']).sum()} metrics")

st.markdown("---")

# =========================
# BARS
# =========================
st.markdown("### Metrics")

for _,r in filtered.iterrows():
    c1,c2,c3=st.columns([2,1,1])
    c1.write(r["metric"])

    maxv=max(r["a"],r["b"])
    c2.progress(r["a"]/maxv)
    c3.progress(r["b"]/maxv)

st.write(f"🔵 {p1} | 🟢 {p2}")

# =========================
# TABLE
# =========================
st.markdown("### Table")
st.table(filtered)
