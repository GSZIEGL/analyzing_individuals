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

LABELS_HU = {
    "Goals":"Gólok",
    "xG":"xG",
    "Assists":"Asszisztok",
    "Shots":"Lövések",
    "Shots on target":"Kaput eltaláló lövések",
    "Chances created":"Helyzetkialakítás",
    "Key passes":"Kulcspasszok",
    "Progressive passes":"Progresszív passzok",
    "Dribbles":"Cselek"
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


# ---------- RADAR ----------
def draw_radar(data, p1, p2):

    labels = [LABELS_HU.get(m, m) for m in data["metric"]]
    N = len(labels)

    max_vals = np.maximum(data["a"], data["b"]) * 1.2
    a = (data["a"] / max_vals)
    b = (data["b"] / max_vals)

    def get_points(values):
        pts = []
        for i in range(N):
            angle = 2*np.pi*i/N - np.pi/2
            x = 250 + 180*values.iloc[i]*np.cos(angle)
            y = 250 + 180*values.iloc[i]*np.sin(angle)
            pts.append((x,y))
        pts.append(pts[0])
        return pts

    pts_a = get_points(a)
    pts_b = get_points(b)

    # label pozíciók
    label_pos = []
    for i in range(N):
        angle = 2*np.pi*i/N - np.pi/2
        x = 250 + 220*np.cos(angle)
        y = 250 + 220*np.sin(angle)
        label_pos.append((x,y))

    svg = f'<svg width="500" height="500">'

    # körvonalak
    for r in [0.25,0.5,0.75,1]:
        circle_pts = []
        for i in range(N):
            angle = 2*np.pi*i/N - np.pi/2
            x = 250 + 180*r*np.cos(angle)
            y = 250 + 180*r*np.sin(angle)
            circle_pts.append(f"{x},{y}")
        circle_pts.append(circle_pts[0])
        svg += f'<polyline points="{" ".join(circle_pts)}" fill="none" stroke="gray" opacity="0.3"/>'

    # A játékos
    svg += f'<polygon points="{" ".join([f"{x},{y}" for x,y in pts_a])}" fill="blue" opacity="0.4"/>'

    # B játékos
    svg += f'<polygon points="{" ".join([f"{x},{y}" for x,y in pts_b])}" fill="green" opacity="0.4"/>'

    # labels
    for (x,y),label in zip(label_pos, labels):
        svg += f'<text x="{x}" y="{y}" font-size="10" fill="white" text-anchor="middle">{label}</text>'

    svg += '</svg>'

    st.markdown(svg, unsafe_allow_html=True)

    # legenda
    st.markdown(f"🔵 {p1} | 🟢 {p2}")


# ---------- APP ----------
st.title("⚽ SCOUT DASHBOARD PRO")

file = st.file_uploader("CSV feltöltése", type=["csv"])
img1 = st.file_uploader("1. játékos kép", type=["png","jpg"])
img2 = st.file_uploader("2. játékos kép", type=["png","jpg"])

if not file:
    st.stop()

p1, p2, data = load_file(file)

pos = st.selectbox("Poszt", list(POSITION_METRICS.keys()))
metrics = POSITION_METRICS[pos]

filtered = data[data["metric"].isin(metrics)].head(8)

# ---------- PLAYER ----------
c1, c2 = st.columns(2)

with c1:
    st.subheader(p1)
    if img1: st.image(img1)

with c2:
    st.subheader(p2)
    if img2: st.image(img2)

st.markdown("---")

# ---------- RADAR ----------
st.subheader("📊 Pókháló")
draw_radar(filtered, p1, p2)

# ---------- BAR ----------
st.subheader("📊 Kulcsmutatók")

for _, r in filtered.iterrows():
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        st.write(LABELS_HU.get(r["metric"], r["metric"]))
    with col2:
        st.progress(min(r["a"]/max(r["a"],r["b"]),1))
    with col3:
        st.progress(min(r["b"]/max(r["a"],r["b"]),1))

st.markdown(f"🔵 {p1} | 🟢 {p2}")

# ---------- EXTRA ----------
st.subheader("📈 További mutatók")

extra = data[~data["metric"].isin(metrics)]

for _, r in extra.head(10).iterrows():
    st.write(f"{r['metric']}: {r['a']} vs {r['b']}")

# ---------- ANALYSIS ----------
st.subheader("🧠 KONKLÚZIÓ")

better_a = (filtered["a"] > filtered["b"]).sum()
better_b = (filtered["b"] > filtered["a"]).sum()

st.write(f"{p1} jobb {better_a} kulcsmutatóban")
st.write(f"{p2} jobb {better_b} kulcsmutatóban")
