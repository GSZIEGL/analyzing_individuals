import streamlit as st
import pandas as pd
import numpy as np
import base64

st.set_page_config(layout="wide")

# ---------- CONFIG ----------
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

# ---------- LOAD ----------
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

# ---------- SIMPLE RADAR (CLEAN) ----------
def radar(data, p1, p2):
    st.markdown("### 📊 Pókháló (egyszerű, átlátható)")

    for _,r in data.iterrows():
        col1,col2,col3 = st.columns([2,1,1])
        with col1:
            st.write(LABELS.get(r["metric"], r["metric"]))
        with col2:
            st.progress(min(r["a"]/max(r["a"],r["b"]),1))
        with col3:
            st.progress(min(r["b"]/max(r["a"],r["b"]),1))

    st.write(f"🔵 {p1} | 🟢 {p2}")

# ---------- HTML EXPORT ----------
def create_html(p1,p2,data):
    html = f"<h1>{p1} vs {p2}</h1>"
    html += "<table border=1 style='border-collapse:collapse'>"
    html += "<tr><th>Mutató</th><th>{}</th><th>{}</th></tr>".format(p1,p2)

    for _,r in data.iterrows():
        html += f"<tr><td>{r['metric']}</td><td>{r['a']}</td><td>{r['b']}</td></tr>"

    html += "</table>"
    return html

def download_html(html):
    b64 = base64.b64encode(html.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="report.html">📄 Report letöltése</a>'
    st.markdown(href, unsafe_allow_html=True)

# ---------- APP ----------
st.title("⚽ FINAL BOSS SCOUT APP")

file = st.file_uploader("CSV feltöltése", type=["csv"])
img1 = st.file_uploader("1. játékos kép", type=["png","jpg"])
img2 = st.file_uploader("2. játékos kép", type=["png","jpg"])

if not file:
    st.stop()

p1,p2,data = load(file)

pos = st.selectbox("Poszt", list(POSITION_METRICS.keys()))
metrics = POSITION_METRICS[pos]

filtered = data[data["metric"].isin(metrics)].head(8)

# ---------- PLAYER CARDS ----------
c1,c2 = st.columns(2)

with c1:
    st.subheader(p1)
    if img1: st.image(img1)

with c2:
    st.subheader(p2)
    if img2: st.image(img2)

st.markdown("---")

# ---------- RADAR ----------
radar(filtered,p1,p2)

# ---------- ANALYSIS ----------
st.markdown("## 🧠 KONKLÚZIÓ")

better_a = (filtered["a"] > filtered["b"]).sum()
better_b = (filtered["b"] > filtered["a"]).sum()

st.write(f"{p1} jobb {better_a} mutatóban")
st.write(f"{p2} jobb {better_b} mutatóban")

filtered["diff"] = filtered["a"] - filtered["b"]

st.markdown(f"### 🔥 {p1} erősségek")
for _,r in filtered.sort_values("diff",ascending=False).head(3).iterrows():
    st.write(r["metric"])

st.markdown(f"### 🔥 {p2} erősségek")
for _,r in filtered.sort_values("diff",ascending=True).head(3).iterrows():
    st.write(r["metric"])

# ---------- EXPORT ----------
html = create_html(p1,p2,filtered)
download_html(html)
