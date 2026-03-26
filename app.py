import io
from math import pi
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Játékos-összehasonlító app", layout="wide")

POSITION_METRICS = {
    "Támadó": ["Goals","xG","Shots","Shots on target","Assists","Chances created","Key passes","Dribbles"],
    "Támadó középpályás": ["Goals","Assists","Chances created","Key passes","Progressive passes","Dribbles","xG"],
    "Középpályás": ["Assists","Passes","Passes accurate, %","Progressive passes","Key passes","Interceptions"],
    "Védő": ["Passes","Passes accurate, %","Interceptions","Tackles"]
}

METRIC_LABELS_HU = {
    "Goals":"Gólok","Assists":"Asszisztok","Chances created":"Helyzetkialakítás",
    "Shots on target":"Kaput eltaláló lövések","Key passes":"Kulcspasszok",
    "Progressive passes":"Progresszív passzok","Dribbles":"Cselek","xG":"xG"
}

def clean_numeric(v):
    try:
        return float(str(v).replace(",", "."))
    except:
        return None

@st.cache_data
def load_excel(file):
    df = pd.read_excel(file, header=None)
    p1 = str(df.iloc[0,2])
    p2 = str(df.iloc[0,3])
    pos = "Támadó középpályás"
    data = pd.DataFrame({
        "metric": df.iloc[:,0],
        "a": [clean_numeric(x) for x in df.iloc[:,2]],
        "b": [clean_numeric(x) for x in df.iloc[:,3]]
    }).dropna()
    return p1,p2,pos,data

st.title("⚽ Játékos összehasonlító")

excel = st.file_uploader("Excel feltöltése", type=["xlsx"])
img1 = st.file_uploader("1. játékos kép", type=["png","jpg","jpeg"])
img2 = st.file_uploader("2. játékos kép", type=["png","jpg","jpeg"])

if not excel:
    st.stop()

p1,p2,pos,data = load_excel(excel)

col1,col2 = st.columns(2)
with col1:
    st.subheader(p1)
    if img1: st.image(img1)
with col2:
    st.subheader(p2)
    if img2: st.image(img2)

metrics = POSITION_METRICS[pos]
data = data[data["metric"].isin(metrics)]

st.subheader("Összehasonlítás")

for _,r in data.iterrows():
    m = METRIC_LABELS_HU.get(r["metric"], r["metric"])
    st.write(f"{m}: {r['a']} vs {r['b']}")

st.subheader("Értelmezés")

better_a = sum(data["a"]>data["b"])
better_b = sum(data["b"]>data["a"])

st.write(f"{p1} {better_a} mutatóban jobb.")
st.write(f"{p2} {better_b} mutatóban jobb.")
