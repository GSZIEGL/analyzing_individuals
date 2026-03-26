# FULL STREAMLIT SCOUT APP (STABLE VERSION)

import io
import math
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Scout Comparison App", layout="wide")

st.markdown("""
<style>
.block-container{max-width:1400px;}
.card{background:#171a21;border-radius:16px;padding:16px;margin-bottom:12px;}
@media print {
 header, footer, .stSidebar {display:none !important;}
 .card{page-break-inside:avoid;}
}
</style>
""", unsafe_allow_html=True)

POSITION_METRICS = {
    "GK":[], "CB":[], "LB":[], "RB":[],
    "CDM":[], "CM":[], "CAM":[],
    "LW":[], "RW":[], "CF":[], "ST":[],
    "AUTO":[]
}

def load(file):
    raw = file.getvalue().decode("utf-8", errors="ignore")
    df = pd.read_csv(io.StringIO(raw), sep=";", header=None)

    p1, p2 = "Player A","Player B"
    for i in range(5):
        try:
            a,b=str(df.iloc[i,2]),str(df.iloc[i,3])
            if "202" not in a:
                p1,p2=a,b
                break
        except: pass

    rows=[]
    for i in range(len(df)):
        try:
            rows.append({
                "metric":str(df.iloc[i,0]),
                "a":float(str(df.iloc[i,2]).replace(",", ".")),
                "b":float(str(df.iloc[i,3]).replace(",", "."))
            })
        except: pass

    return p1,p2,pd.DataFrame(rows)

def radar(df,p1,p2):
    if len(df)<3:
        df=data.head(6)

    df=df.head(6)
    N=len(df)

    max_vals=np.maximum(df["a"],df["b"])
    max_vals[max_vals==0]=1

    a=df["a"]/max_vals
    b=df["b"]/max_vals

    pts_a=[]; pts_b=[]

    for i in range(N):
        ang=2*np.pi*i/N - np.pi/2
        pts_a.append(f"{250+160*a.iloc[i]*np.cos(ang)},{250+160*a.iloc[i]*np.sin(ang)}")
        pts_b.append(f"{250+160*b.iloc[i]*np.cos(ang)},{250+160*b.iloc[i]*np.sin(ang)}")

    pts_a.append(pts_a[0]); pts_b.append(pts_b[0])

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

file = st.file_uploader("CSV", type=["csv"])
img1 = st.file_uploader("Player 1 image")
img2 = st.file_uploader("Player 2 image")

if not file:
    st.stop()

p1,p2,data = load(file)

pos = st.selectbox("Position", list(POSITION_METRICS.keys()))
filtered = data

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

c1,c2 = st.columns(2)
with c1:
    radar(filtered,p1,p2)
with c2:
    st.markdown("### Konklúzió")
    st.write(f"{p1}: {(filtered['a']>filtered['b']).sum()}")
    st.write(f"{p2}: {(filtered['b']>filtered['a']).sum()}")

st.markdown("---")

for _,r in filtered.iterrows():
    c1,c2,c3 = st.columns([2,1,1])
    c1.write(r["metric"])
    maxv=max(r["a"],r["b"])
    c2.progress(r["a"]/maxv if maxv else 0)
    c3.progress(r["b"]/maxv if maxv else 0)

st.markdown("---")
st.table(filtered)
