import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

# ---------- POSZT METRIKÁK ----------
POSITION_METRICS = {
    "Támadó": ["Goals","xG","Shots","Shots on target","Assists","Dribbles","Key passes"],
    "Támadó középpályás": ["Goals","Assists","Chances created","Key passes","Progressive passes","Dribbles","xG"],
    "Középpályás": ["Assists","Passes","Passes accurate, %","Progressive passes","Interceptions","Key passes"],
    "Védő": ["Passes","Passes accurate, %","Interceptions","Tackles","Air challenges won, %"]
}

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

        data.append({"metric": metric, "a": a, "b": b})

    return p1, p2, pd.DataFrame(data)


# ---------- RADAR (jobb, limitált) ----------
def draw_radar(data, p1, p2):
    if len(data) < 3:
        st.warning("Kevés adat a pókhálóhoz")
        return

    labels = data["metric"].tolist()
    N = len(labels)

    max_vals = np.maximum(data["a"], data["b"]) * 1.2
    a = (data["a"] / max_vals)
    b = (data["b"] / max_vals)

    points_a = []
    points_b = []

    for i in range(N):
        angle = 2*np.pi*i/N - np.pi/2
        x1 = 200 + 150*a.iloc[i]*np.cos(angle)
        y1 = 200 + 150*a.iloc[i]*np.sin(angle)
        x2 = 200 + 150*b.iloc[i]*np.cos(angle)
        y2 = 200 + 150*b.iloc[i]*np.sin(angle)

        points_a.append(f"{x1},{y1}")
        points_b.append(f"{x2},{y2}")

    points_a.append(points_a[0])
    points_b.append(points_b[0])

    svg = f"""
    <svg width="400" height="400">
        <polygon points="{' '.join(points_a)}" fill="#6C63FF" opacity="0.5"/>
        <polygon points="{' '.join(points_b)}" fill="#00C2A8" opacity="0.5"/>
    </svg>
    """

    st.markdown(svg, unsafe_allow_html=True)


# ---------- APP ----------
st.title("⚽ SCOUT APP PRO")

file = st.file_uploader("CSV feltöltése", type=["csv"])
img1 = st.file_uploader("1. játékos kép", type=["png","jpg"])
img2 = st.file_uploader("2. játékos kép", type=["png","jpg"])

if not file:
    st.stop()

p1, p2, data = load_file(file)

# POSZT VÁLASZTÁS
pos = st.selectbox("Poszt választás", list(POSITION_METRICS.keys()))
selected_metrics = POSITION_METRICS[pos]

filtered = data[data["metric"].isin(selected_metrics)].copy()

if filtered.empty:
    st.warning("Nincs adat ehhez a poszthoz")
    st.stop()

# ---------- PLAYER CARDS ----------
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
st.subheader("📊 Pókháló (posztspecifikus)")
draw_radar(filtered.head(8), p1, p2)

# ---------- BAR ----------
st.subheader("📊 Fő mutatók")

bar_df = filtered.set_index("metric")[["a","b"]]
bar_df.columns = [p1, p2]

st.bar_chart(bar_df)

# ---------- EXTRA ----------
st.subheader("📈 További mutatók")

extra = data[~data["metric"].isin(selected_metrics)].copy()

if not extra.empty:
    extra_df = extra.set_index("metric")[["a","b"]]
    extra_df.columns = [p1, p2]
    st.bar_chart(extra_df)

# ---------- ANALYSIS ----------
st.subheader("🧠 KONKLÚZIÓ")

better_a = (filtered["a"] > filtered["b"]).sum()
better_b = (filtered["b"] > filtered["a"]).sum()

st.write(f"{p1} jobb {better_a} kulcsmutatóban")
st.write(f"{p2} jobb {better_b} kulcsmutatóban")

filtered["diff"] = filtered["a"] - filtered["b"]

top_a = filtered.sort_values("diff", ascending=False).head(3)
top_b = filtered.sort_values("diff", ascending=True).head(3)

st.markdown(f"### 🔥 {p1} erősségek")
for _, r in top_a.iterrows():
    st.write(r["metric"])

st.markdown(f"### 🔥 {p2} erősségek")
for _, r in top_b.iterrows():
    st.write(r["metric"])

