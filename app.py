import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ---------- LOAD FILE ----------
def load_file(file):
    df = pd.read_csv(file, sep=";")
    df = df.reset_index(drop=True)

    # játékos nevek (feltételezve struktúrát)
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

    data = pd.DataFrame(data)

    return p1, p2, data


# ---------- RADAR ----------
def radar(data, p1, p2):
    labels = data["metric"].tolist()

    # NORMALIZÁLÁS (nem torz)
    max_vals = np.maximum(data["a"], data["b"]) * 1.2

    a = (data["a"] / max_vals) * 100
    b = (data["b"] / max_vals) * 100

    labels += [labels[0]]
    a = list(a) + [a.iloc[0]]
    b = list(b) + [b.iloc[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(r=a, theta=labels, fill='toself', name=p1, line=dict(color='blue')))
    fig.add_trace(go.Scatterpolar(r=b, theta=labels, fill='toself', name=p2, line=dict(color='green')))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,100])),
        showlegend=True,
        template="plotly_dark"
    )

    return fig


# ---------- APP ----------
st.title("⚽ SCOUT DASHBOARD")

file = st.file_uploader("CSV feltöltése", type=["csv"])
img1 = st.file_uploader("1. játékos kép", type=["png","jpg"])
img2 = st.file_uploader("2. játékos kép", type=["png","jpg"])

if not file:
    st.stop()

p1, p2, data = load_file(file)

col1, col2 = st.columns(2)

with col1:
    st.subheader(p1)
    if img1:
        st.image(img1)

with col2:
    st.subheader(p2)
    if img2:
        st.image(img2)

st.markdown("---")

# RADAR
st.plotly_chart(radar(data, p1, p2), use_container_width=True)

# BAR
st.subheader("📊 Összehasonlítás")

data["diff"] = data["a"] - data["b"]

fig = go.Figure()

fig.add_trace(go.Bar(y=data["metric"], x=data["a"], name=p1, orientation='h'))
fig.add_trace(go.Bar(y=data["metric"], x=data["b"], name=p2, orientation='h'))

fig.update_layout(barmode='group', template="plotly_dark")

st.plotly_chart(fig, use_container_width=True)

# ---------- ANALYSIS ----------
st.subheader("🧠 KONKLÚZIÓ")

better_a = (data["a"] > data["b"]).sum()
better_b = (data["b"] > data["a"]).sum()

st.write(f"👉 {p1} erősebb {better_a} mutatóban")
st.write(f"👉 {p2} erősebb {better_b} mutatóban")

top_a = data.sort_values("diff", ascending=False).head(3)
top_b = data.sort_values("diff", ascending=True).head(3)

st.markdown(f"### 🔥 {p1} erősségek")
for _, r in top_a.iterrows():
    st.write(f"{r['metric']}")

st.markdown(f"### 🔥 {p2} erősségek")
for _, r in top_b.iterrows():
    st.write(f"{r['metric']}")

