import streamlit as st
import pandas as pd
import numpy as np
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

st.set_page_config(layout="wide")

POSITION_METRICS = {
    "Támadó": ["Goals","xG","Shots","Shots on target","Assists","Dribbles","Key passes"],
    "Támadó középpályás": ["Goals","Assists","Chances created","Key passes","Progressive passes","Dribbles","xG"],
    "Középpályás": ["Assists","Passes","Passes accurate, %","Progressive passes","Interceptions","Key passes"],
    "Védő": ["Passes","Passes accurate, %","Interceptions","Tackles","Air challenges won, %"]
}

def load_file(file):
    df = pd.read_csv(file, sep=";")
    df = df.reset_index(drop=True)

    p1 = str(df.iloc[0,2])
    p2 = str(df.iloc[0,3])

    data = []
    for i in range(len(df)):
        try:
            a = float(str(df.iloc[i,2]).replace(",", "."))
            b = float(str(df.iloc[i,3]).replace(",", "."))
            metric = df.iloc[i,0]
            data.append({"metric": metric, "a": a, "b": b})
        except:
            continue

    return p1, p2, pd.DataFrame(data)

def create_pdf(p1, p2, data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(f"{p1} vs {p2}", styles['Title']))
    elements.append(Spacer(1, 12))

    better_a = (data["a"] > data["b"]).sum()
    better_b = (data["b"] > data["a"]).sum()

    elements.append(Paragraph(f"{p1} jobb {better_a} mutatóban", styles['Normal']))
    elements.append(Paragraph(f"{p2} jobb {better_b} mutatóban", styles['Normal']))

    doc.build(elements)
    return buffer.getvalue()

st.title("⚽ ULTRA PRO SCOUT APP")

file = st.file_uploader("CSV feltöltése", type=["csv"])
img1 = st.file_uploader("1. játékos kép", type=["png","jpg"])
img2 = st.file_uploader("2. játékos kép", type=["png","jpg"])

if not file:
    st.stop()

p1, p2, data = load_file(file)

pos = st.selectbox("Poszt", list(POSITION_METRICS.keys()))
metrics = POSITION_METRICS[pos]

filtered = data[data["metric"].isin(metrics)].head(8)

c1, c2 = st.columns(2)
with c1:
    st.subheader(p1)
    if img1: st.image(img1)
with c2:
    st.subheader(p2)
    if img2: st.image(img2)

st.markdown("---")

st.subheader("📊 Mutatók")
st.dataframe(filtered)

st.subheader("🧠 Konklúzió")

better_a = (filtered["a"] > filtered["b"]).sum()
better_b = (filtered["b"] > filtered["a"]).sum()

st.write(f"{p1} jobb {better_a} mutatóban")
st.write(f"{p2} jobb {better_b} mutatóban")

pdf = create_pdf(p1, p2, filtered)

st.download_button("📄 PDF letöltés", pdf, file_name="report.pdf")
