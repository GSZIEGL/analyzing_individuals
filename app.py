import streamlit as st
import pandas as pd
import numpy as np
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(layout="wide")

POSITION_METRICS = {
    "Támadó": ["Goals","xG","Shots","Shots on target","Assists","Dribbles","Key passes"],
    "Támadó középpályás": ["Goals","Assists","Chances created","Key passes","Progressive passes","Dribbles","xG"],
    "Középpályás": ["Assists","Passes","Passes accurate, %","Progressive passes","Interceptions","Key passes"],
    "Védő": ["Passes","Passes accurate, %","Interceptions","Tackles","Air challenges won, %"]
}

LABELS = {
    "Goals":"Gólok","xG":"xG","Assists":"Asszisztok",
    "Shots":"Lövések","Shots on target":"Kaput eltaláló lövések",
    "Chances created":"Helyzetkialakítás","Key passes":"Kulcspasszok",
    "Progressive passes":"Progresszív passzok","Dribbles":"Cselek"
}

def load(file):
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

def create_pdf(p1,p2,data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(f"{p1} vs {p2}", styles['Title']))
    elements.append(Spacer(1, 12))

    for _,r in data.iterrows():
        elements.append(Paragraph(f"{r['metric']}: {r['a']} vs {r['b']}", styles['Normal']))

    doc.build(elements)
    return buffer.getvalue()

st.title("⚽ ELITE SCOUT DASHBOARD FIX")

file = st.file_uploader("CSV feltöltése", type=["csv"])

if not file:
    st.stop()

p1,p2,data = load(file)

pos = st.selectbox("Poszt", list(POSITION_METRICS.keys()))
metrics = POSITION_METRICS[pos]

filtered = data[data["metric"].isin(metrics)].head(8)

st.subheader("📊 Kulcsmutatók")

for _,r in filtered.iterrows():
    col1,col2,col3 = st.columns([2,1,1])
    with col1:
        st.write(LABELS.get(r["metric"],r["metric"]))
    with col2:
        st.markdown(f"<div style='background:#4A90E2;height:10px;width:{int(r['a']/max(r['a'],r['b'])*100)}%'></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='background:#00E676;height:10px;width:{int(r['b']/max(r['a'],r['b'])*100)}%'></div>", unsafe_allow_html=True)

st.markdown(f"🔵 {p1} | 🟢 {p2}")

pdf = create_pdf(p1,p2,filtered)

st.download_button("📄 PDF letöltés", pdf, file_name="report.pdf")
