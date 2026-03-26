import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

# ---------- LOAD ----------
def load_file(file):
    df = pd.read_csv(file, sep=";")
    df = df.reset_index(drop=True)

    p1 = str(df.iloc[0,2])
    p2 = str(df.iloc[0,3])

    data = []

    for i in range(len(df)):
        metric = df.iloc[i,0]

        try:
            a = float(str(df.iloc[i,2]).replace(",", "."))
            b = float(str(df.iloc[i,3]).replace(",", "."))
        except:
            continue

        if metric:
            data.append({"metric": metric, "a": a, "b": b})

    return p1, p2, pd.DataFrame(data)


# ---------- RADAR (NO LIB!) ----------
def draw_radar(data, p1, p2):
    labels = data["metric"].tolist()
    N = len(labels)

    # normalizálás
    max_vals = np.maximum(data["a"], data["b"]) * 1.2
    a = (data["a"] / max_vals)
    b = (data["b"] / max_vals)

    points_a = []
    points_b = []

    for i in range(N):
        angle = 2*np.pi*i/N
        x1 = 150 + 120*a.iloc[i]*np.cos(angle)
        y1 = 150 + 120*a.iloc[i]*np.sin(angle)
        x2 = 150 + 120*b.iloc[i]*np.cos(angle)
        y2 = 150 + 120*b.iloc[i]*np.sin(angle)

        points_a.append(f"{x1},{y1}")
        points_b.append(f"{x2},{y2}")

    points_a.append(points_a[0])
    points_b.append(points_b[0])

    svg = f"""
    <svg width="300" height="300">
        <polygon points="{' '.join(points_a)}" fill="blue" opacity="0.4"/>
        <polygon points="{' '.join(points_b)}" fill="green" opacity="0.4"/>
    </svg>
    """

    st.markdown(svg, unsafe_allow_html=True)


# ---------- APP ----------
st.title("⚽ SCOUT DASHBOARD")

file = st.file_uploader("CSV feltöltése", type=["csv"])
img1 = st.file_uploader("1. játékos kép", type=["png","jpg"])
img2 = st.file_uploader("2. játékos kép", type=["png","jpg"])

if not file:
    st.stop()

p1, p2, data = load_file(file)

# ---------- PLAYERS ----------
c1, c2 = st.columns(2)

with c1:
    st.subheader(p1)
    if img1:
        st.image(img1)

with c2:
    st.subheader(p2)
    if img2:
        st.image(img2)

st.markdown("---")

# ---------- RADAR ----------
st.subheader("📊 Pókháló")
draw_radar(data, p1, p2)

# ---------- BAR ----------
st.subheader("📊 Összehasonlítás")

for _, r in data.iterrows():
    st.write(f"{r['metric']}: {r['a']} vs {r['b']}")

# ---------- ANALYSIS ----------
st.subheader("🧠 KONKLÚZIÓ")

better_a = (data["a"] > data["b"]).sum()
better_b = (data["b"] > data["a"]).sum()

st.write(f"{p1} jobb {better_a} mutatóban")
st.write(f"{p2} jobb {better_b} mutatóban")

data["diff"] = data["a"] - data["b"]

top_a = data.sort_values("diff", ascending=False).head(3)
top_b = data.sort_values("diff", ascending=True).head(3)

st.markdown(f"### 🔥 {p1} erősségek")
for _, r in top_a.iterrows():
    st.write(r["metric"])

st.markdown(f"### 🔥 {p2} erősségek")
for _, r in top_b.iterrows():
    st.write(r["metric"])
