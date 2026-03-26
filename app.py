import io
import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(layout="wide")

# ---------- FILE LOAD ----------
def load_file(file):
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file, header=None)
        else:
            df = pd.read_excel(file, header=None)
    except:
        st.error("Excel olvasási hiba. Használj CSV-t (mentés másként).")
        st.stop()

    p1 = str(df.iloc[0,2])
    p2 = str(df.iloc[0,3])

    data = pd.DataFrame({
        "metric": df.iloc[:,0],
        "a": pd.to_numeric(df.iloc[:,2], errors="coerce"),
        "b": pd.to_numeric(df.iloc[:,3], errors="coerce")
    }).dropna()

    return p1, p2, data


# ---------- UI ----------
st.title("⚽ Játékos összehasonlító")

file = st.file_uploader("CSV vagy Excel feltöltése", type=["csv","xlsx"])
img1 = st.file_uploader("1. játékos képe", type=["png","jpg","jpeg"])
img2 = st.file_uploader("2. játékos képe", type=["png","jpg","jpeg"])

if not file:
    st.stop()

p1, p2, data = load_file(file)

# ---------- PLAYER CARDS ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader(p1)
    if img1:
        st.image(img1, use_container_width=True)

with col2:
    st.subheader(p2)
    if img2:
        st.image(img2, use_container_width=True)

st.markdown("---")

# ---------- COMPARISON ----------
st.subheader("Mutatók összehasonlítása")

for _, r in data.iterrows():
    st.write(f"{r['metric']}: {r['a']} vs {r['b']}")

# ---------- SUMMARY ----------
st.subheader("Gyors elemzés")

better_a = sum(data["a"] > data["b"])
better_b = sum(data["b"] > data["a"])

st.write(f"👉 {p1} jobb {better_a} mutatóban")
st.write(f"👉 {p2} jobb {better_b} mutatóban")

# ---------- STRENGTHS ----------
st.subheader("Erősségek")

data["diff"] = data["a"] - data["b"]

top_a = data.sort_values("diff", ascending=False).head(3)
top_b = data.sort_values("diff", ascending=True).head(3)

st.write(f"🔥 {p1}")
for _, r in top_a.iterrows():
    st.write(f"{r['metric']}")

st.write(f"🔥 {p2}")
for _, r in top_b.iterrows():
    st.write(f"{r['metric']}")

# ---------- DOWNLOAD ----------
st.download_button(
    "Letöltés CSV-ben",
    data=data.to_csv(index=False),
    file_name="osszehasonlitas.csv"
)

st.code("streamlit run app.py")
