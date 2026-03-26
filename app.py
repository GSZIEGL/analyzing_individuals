import streamlit as st
import pandas as pd
import numpy as np
import base64

st.set_page_config(layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
body {background-color:#0e1117;}
h1,h2,h3 {color:white;}
.metric-box {background:#1c1f26;padding:10px;border-radius:10px;margin:5px;}
</style>
""", unsafe_allow_html=True)

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

# ---------- REAL RADAR ----------
def radar_svg(data, p1, p2):
    labels = [LABELS.get(m,m) for m in data["metric"]]
    N = len(labels)

    max_vals = np.maximum(data["a"], data["b"]) * 1.2
    a = (data["a"] / max_vals)
    b = (data["b"] / max_vals)

    def pts(vals):
        res=[]
        for i in range(N):
            angle = 2*np.pi*i/N - np.pi/2
            x = 200 + 150*vals.iloc[i]*np.cos(angle)
            y = 200 + 150*vals.iloc[i]*np.sin(angle)
            res.append(f"{x},{y}")
        res.append(res[0])
        return res

    pa = pts(a)
    pb = pts(b)

    svg = f'<svg width="400" height="400">'

    # grid
    for r in [0.25,0.5,0.75,1]:
        pts_grid=[]
        for i in range(N):
            angle = 2*np.pi*i/N - np.pi/2
            x = 200 + 150*r*np.cos(angle)
            y = 200 + 150*r*np.sin(angle)
            pts_grid.append(f"{x},{y}")
        pts_grid.append(pts_grid[0])
        svg += f'<polyline points="{" ".join(pts_grid)}" fill="none" stroke="gray" opacity="0.3"/>'

    svg += f'<polygon points="{" ".join(pa)}" fill="#4A90E2" opacity="0.4"/>'
    svg += f'<polygon points="{" ".join(pb)}" fill="#00E676" opacity="0.4"/>'

    # labels
    for i,l in enumerate(labels):
        angle = 2*np.pi*i/N - np.pi/2
        x = 200 + 180*np.cos(angle)
        y = 200 + 180*np.sin(angle)
        svg += f'<text x="{x}" y="{y}" fill="white" font-size="10" text-anchor="middle">{l}</text>'

    svg += '</svg>'

    st.markdown(svg, unsafe_allow_html=True)
    st.markdown(f"🔵 {p1} | 🟢 {p2}")

# ---------- EXPORT PDF (HTML PRINT READY) ----------
def export_html(p1,p2,data):
    html = f"""
    <html>
    <body style="background:#0e1117;color:white;font-family:sans-serif">
    <h1>{p1} vs {p2}</h1>
    <table border="1" style="width:100%;border-collapse:collapse">
    <tr><th>Mutató</th><th>{p1}</th><th>{p2}</th></tr>
    """

    for _,r in data.iterrows():
        html += f"<tr><td>{r['metric']}</td><td>{r['a']}</td><td>{r['b']}</td></tr>"

    html += "</table></body></html>"

    b64 = base64.b64encode(html.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="report.html">📄 LETÖLTÉS (PDF-re nyomtatható)</a>'
    st.markdown(href, unsafe_allow_html=True)

# ---------- APP ----------
st.title("⚽ ELITE SCOUT DASHBOARD")

file = st.file_uploader("CSV feltöltése", type=["csv"])
img1 = st.file_uploader("1. játékos kép", type=["png","jpg"])
img2 = st.file_uploader("2. játékos kép", type=["png","jpg"])

if not file:
    st.stop()

p1,p2,data = load(file)

pos = st.selectbox("Poszt", list(POSITION_METRICS.keys()))
metrics = POSITION_METRICS[pos]

filtered = data[data["metric"].isin(metrics)].head(8)

c1,c2 = st.columns(2)

with c1:
    st.subheader(p1)
    if img1: st.image(img1)

with c2:
    st.subheader(p2)
    if img2: st.image(img2)

st.markdown("---")

st.subheader("📊 Pókháló")
radar_svg(filtered,p1,p2)

st.subheader("📊 Kulcsmutatók")

for _,r in filtered.iterrows():
    col1,col2,col3 = st.columns([2,1,1])
    with col1:
        st.write(LABELS.get(r["metric"],r["metric"]))
    with col2:
        st.progress(r["a"]/max(r["a"],r["b"]))
    with col3:
        st.progress(r["b"]/max(r["a"],r["b"]))

st.markdown(f"🔵 {p1} | 🟢 {p2}")

st.subheader("🧠 KONKLÚZIÓ")

better_a = (filtered["a"] > filtered["b"]).sum()
better_b = (filtered["b"] > filtered["a"]).sum()

st.write(f"{p1} jobb {better_a} mutatóban")
st.write(f"{p2} jobb {better_b} mutatóban")

export_html(p1,p2,filtered)
