import io
import math
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

# =========================
# STYLE
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

.two-col-print {
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:20px;
}

@media print {
  header, footer, .stSidebar {display:none !important;}

  .card {page-break-inside:avoid;}

  .two-col-print{
    display:grid;
    grid-template-columns:1fr 1fr;
  }

  .no-break{
    break-inside:avoid;
    page-break-inside:avoid;
  }
}
</style>
""", unsafe_allow_html=True)

# =========================
# POSITIONS (FULL)
# =========================
POSITION_METRICS: Dict[str, List[str]] = {
    "GK": ["Passes", "Passes accurate, %"],

    "CB": ["Interceptions", "Tackles", "Air challenges won, %"],
    "LCB": ["Interceptions", "Tackles", "Air challenges won, %"],
    "RCB": ["Interceptions", "Tackles", "Air challenges won, %"],

    "LB": ["Assists", "Dribbles", "Key passes"],
    "RB": ["Assists", "Dribbles", "Key passes"],

    "LWB": ["Assists", "Dribbles", "Key passes"],
    "RWB": ["Assists", "Dribbles", "Key passes"],

    "CDM": ["Interceptions", "Passes"],
    "LDM": ["Interceptions", "Passes"],
    "RDM": ["Interceptions", "Passes"],

    "CM": ["Passes", "Assists", "Key passes"],
    "LCM": ["Passes", "Assists", "Key passes"],
    "RCM": ["Passes", "Assists", "Key passes"],

    "CAM": ["Goals", "Assists", "xG", "Key passes", "Dribbles"],
    "LAM": ["Goals", "Assists", "xG"],
    "RAM": ["Goals", "Assists", "xG"],

    "LW": ["Goals", "xG", "Dribbles", "Shots"],
    "RW": ["Goals", "xG", "Dribbles", "Shots"],

    "CF": ["Goals", "xG", "Shots"],
    "ST": ["Goals", "xG", "Shots", "Shots on target"],

    "Egyedi": []
}

# =========================
# HELPERS
# =========================
def safe_float(v):
    try:
        return float(str(v).replace(",", "."))
    except:
        return np.nan

def try_read_csv(uploaded_file):
    raw = uploaded_file.getvalue()
    for sep in [";", ","]:
        try:
            return pd.read_csv(io.StringIO(raw.decode("utf-8")), sep=sep, header=None)
        except:
            continue
    raise ValueError("CSV hiba")

def extract_names(df):
    return str(df.iloc[1,2]), str(df.iloc[1,3])

def extract_metrics(df):
    rows=[]
    for i in range(len(df)):
        try:
            rows.append({
                "metric":df.iloc[i,0],
                "a":safe_float(df.iloc[i,2]),
                "b":safe_float(df.iloc[i,3])
            })
        except:
            pass
    return pd.DataFrame(rows)

def pick_metrics(all_data, position):
    if position=="Egyedi":
        return all_data.head(8)
    df = all_data[all_data["metric"].isin(POSITION_METRICS[position])]
    if len(df)<3:
        return all_data.head(6)
    return df.head(8)

# =========================
# RADAR
# =========================
def radar(df,p1,p2):

    df=df.head(6)

    labels=df["metric"].tolist()
    N=len(labels)

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

    svg=f"""
    <div class="card no-break">
    <svg width="500" height="500">
    <polygon points="{' '.join(pts_a)}" fill="#3b82f6" opacity="0.35"/>
    <polygon points="{' '.join(pts_b)}" fill="#10b981" opacity="0.35"/>
    </svg>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)
    st.markdown(f"🔵 {p1} | 🟢 {p2}")

# =========================
# MAIN
# =========================
uploaded = st.file_uploader("CSV")
img_a = st.file_uploader("Kép A")
img_b = st.file_uploader("Kép B")

if not uploaded:
    st.stop()

df_raw = try_read_csv(uploaded)
player_a, player_b = extract_names(df_raw)
all_data = extract_metrics(df_raw)

position = st.selectbox("Poszt", list(POSITION_METRICS.keys()))
filtered = pick_metrics(all_data, position)

# HEADER
c1,c2 = st.columns(2)

with c1:
    st.subheader(player_a)
    if img_a:
        st.image(img_a)

with c2:
    st.subheader(player_b)
    if img_b:
        st.image(img_b)

st.markdown("---")

# RADAR + TEXT
st.markdown('<div class="two-col-print">', unsafe_allow_html=True)

col1,col2 = st.columns(2)

with col1:
    radar(filtered,player_a,player_b)

with col2:
    st.markdown('<div class="card no-break">', unsafe_allow_html=True)
    st.write(f"{player_a}: {(filtered['a']>filtered['b']).sum()}")
    st.write(f"{player_b}: {(filtered['b']>filtered['a']).sum()}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# METRICS
for _,r in filtered.iterrows():
    c1,c2,c3 = st.columns([2,1,1])
    c1.write(r["metric"])
    maxv=max(r["a"],r["b"])
    c2.progress(r["a"]/maxv if maxv else 0)
    c3.progress(r["b"]/maxv if maxv else 0)

st.markdown("---")

st.table(filtered)
