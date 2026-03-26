import io
from math import pi
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Játékos-összehasonlító app", layout="wide")

POSITION_METRICS: Dict[str, List[str]] = {
    "Támadó": [
        "Goals", "xG", "Shots", "Shots on target", "Assists",
        "Chances created", "Key passes", "Dribbles",
        "Attacking challenges won, %", "Progressive passes"
    ],
    "Támadó középpályás": [
        "Goals", "Assists", "Chances created", "Key passes",
        "Progressive passes", "Passes into the penalty box",
        "Passes for a shot", "Dribbles", "xG"
    ],
    "Középpályás": [
        "Assists", "Passes", "Passes accurate, %", "Progressive passes",
        "Key passes", "Interceptions", "Challenges won, %", "xG"
    ],
    "Védekező középpályás": [
        "Passes", "Passes accurate, %", "Progressive passes", "Interceptions",
        "Tackles", "Tackles successful, %", "Defensive challenges won, %",
        "Air challenges won, %"
    ],
    "Védő": [
        "Passes", "Passes accurate, %", "Long passes", "Long passes accurate, %",
        "Defensive challenges won, %", "Air challenges won, %",
        "Interceptions", "Tackles successful, %"
    ],
    "Szélső / Wingback": [
        "Assists", "Crosses", "Crosses accurate, %", "Progressive passes",
        "Passes into the penalty box", "Dribbles", "Defensive challenges won, %",
        "Interceptions"
    ],
    "Egyedi": []
}

METRIC_LABELS_HU: Dict[str, str] = {
    "Goals": "Gólok",
    "Assists": "Asszisztok",
    "Chances": "Helyzetek",
    "Chances created": "Helyzetkialakítás",
    "Shots": "Lövések",
    "Shots on target": "Kaput eltaláló lövések",
    "Key passes": "Kulcspasszok",
    "Progressive passes": "Progresszív passzok",
    "Passes into the penalty box": "Büntetőterületbe passzok",
    "Passes for a shot": "Lövést előkészítő passzok",
    "Crosses": "Beadások",
    "Crosses accurate, %": "Pontos beadások %",
    "Passes": "Passzok",
    "Passes accurate, %": "Passzpontosság %",
    "Long passes": "Hosszú passzok",
    "Long passes accurate, %": "Pontos hosszú passzok %",
    "Dribbles": "Cselek",
    "Attacking challenges won, %": "Támadó párharc nyerés %",
    "Challenges won, %": "Párharc nyerés %",
    "Defensive challenges won, %": "Védő párharc nyerés %",
    "Air challenges won, %": "Fejpárbaj nyerés %",
    "Interceptions": "Interceptionök",
    "Tackles": "Szerelések",
    "Tackles successful, %": "Sikeres szerelések %",
    "xG": "xG",
}

METRIC_CEILINGS: Dict[str, float] = {
    "Goals": 0.80,
    "Assists": 0.50,
    "Chances": 3.50,
    "Chances created": 2.20,
    "Shots": 4.50,
    "Shots on target": 2.00,
    "Key passes": 2.50,
    "Progressive passes": 12.00,
    "Passes into the penalty box": 3.00,
    "Passes for a shot": 2.00,
    "Crosses": 5.00,
    "Crosses accurate, %": 1.00,
    "Passes": 80.00,
    "Passes accurate, %": 1.00,
    "Long passes": 10.00,
    "Long passes accurate, %": 1.00,
    "Dribbles": 6.00,
    "Attacking challenges won, %": 1.00,
    "Challenges won, %": 1.00,
    "Defensive challenges won, %": 1.00,
    "Air challenges won, %": 1.00,
    "Interceptions": 5.00,
    "Tackles": 4.00,
    "Tackles successful, %": 1.00,
    "xG": 0.80,
}


def clean_numeric(value):
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.number)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    if text in {"-", "—", ""}:
        return np.nan
    try:
        return float(text)
    except ValueError:
        return np.nan


@st.cache_data
def load_comparison_excel(uploaded_file) -> Tuple[str, str, str, str, pd.DataFrame]:
    df = pd.read_excel(uploaded_file, header=None)

    player_a = str(df.iloc[0, 2]).strip()
    player_b = str(df.iloc[0, 3]).strip()

    position_row = df.index[df[0].astype(str).str.strip().eq("Position")]
    pos_a = str(df.iloc[position_row[0], 2]).strip() if len(position_row) else ""
    pos_b = str(df.iloc[position_row[0], 3]).strip() if len(position_row) else ""

    metrics_df = pd.DataFrame({
        "metric": df.iloc[:, 0].astype(str).str.strip(),
        "player_a": [clean_numeric(v) for v in df.iloc[:, 2]],
        "player_b": [clean_numeric(v) for v in df.iloc[:, 3]],
    })

    metrics_df = metrics_df[
        ~metrics_df["metric"].isin(["nan", "Index", "Minutes played", "Position", ""])
    ].copy()
    metrics_df = metrics_df.dropna(subset=["player_a", "player_b"], how="all").reset_index(drop=True)
    return player_a, player_b, pos_a, pos_b, metrics_df


def infer_position_group(pos_a: str, pos_b: str) -> str:
    positions = f"{pos_a} {pos_b}".upper()
    if any(x in positions for x in ["CF", "ST", "FW", "STRIKER"]):
        return "Támadó"
    if any(x in positions for x in ["CAM", "AM", "LAM", "RAM", "RCAM", "LCAM"]):
        return "Támadó középpályás"
    if any(x in positions for x in ["DM", "CDM"]):
        return "Védekező középpályás"
    if any(x in positions for x in ["CB"]):
        return "Védő"
    if any(x in positions for x in ["WB", "LB", "RB", "LWB", "RWB"]):
        return "Szélső / Wingback"
    return "Középpályás"


def hu_label(metric: str) -> str:
    return METRIC_LABELS_HU.get(metric, metric)


def get_selected_metrics(metrics_df: pd.DataFrame, position_group: str, custom_metrics: List[str]) -> List[str]:
    available = metrics_df["metric"].tolist()
    if position_group == "Egyedi":
        return [m for m in custom_metrics if m in available]
    return [m for m in POSITION_METRICS[position_group] if m in available]


def build_comparison_table(metrics_df: pd.DataFrame, selected_metrics: List[str]) -> pd.DataFrame:
    table = metrics_df[metrics_df["metric"].isin(selected_metrics)].copy()
    table["Mutató"] = table["metric"].map(hu_label)
    table["Jobb"] = np.where(
        table["player_a"].fillna(-999) > table["player_b"].fillna(-999), "A",
        np.where(table["player_b"].fillna(-999) > table["player_a"].fillna(-999), "B", "Döntetlen")
    )
    return table[["metric", "Mutató", "player_a", "player_b", "Jobb"]]


def fixed_scale_scores(table: pd.DataFrame):
    a_scores, b_scores = [], []
    for _, row in table.iterrows():
        ceiling = METRIC_CEILINGS.get(row["metric"])
        if ceiling is None or pd.isna(row["player_a"]) or pd.isna(row["player_b"]):
            a_scores.append(np.nan)
            b_scores.append(np.nan)
            continue
        a_scores.append(min((row["player_a"] / ceiling) * 100, 100))
        b_scores.append(min((row["player_b"] / ceiling) * 100, 100))
    return np.array(a_scores, dtype=float), np.array(b_scores, dtype=float)


def plot_radar(table: pd.DataFrame, player_a: str, player_b: str):
    radar_table = table.dropna(subset=["player_a", "player_b"]).copy()
    if len(radar_table) < 3:
        return None

    labels = radar_table["Mutató"].tolist()
    a_scores, b_scores = fixed_scale_scores(radar_table)

    valid = ~np.isnan(a_scores) & ~np.isnan(b_scores)
    labels = [labels[i] for i in range(len(labels)) if valid[i]]
    a_scores = a_scores[valid]
    b_scores = b_scores[valid]

    if len(labels) < 3:
        return None

    labels_closed = labels + [labels[0]]
    a_closed = list(a_scores) + [a_scores[0]]
    b_closed = list(b_scores) + [b_scores[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=a_closed,
        theta=labels_closed,
        fill="toself",
        name=player_a,
        line=dict(color="#6C63FF", width=3),
        opacity=0.55
    ))
    fig.add_trace(go.Scatterpolar(
        r=b_closed,
        theta=labels_closed,
        fill="toself",
        name=player_b,
        line=dict(color="#00C2A8", width=3),
        opacity=0.50
    ))
    fig.update_layout(
        title="Pókháló – fix 0–100 skála",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickvals=[20, 40, 60, 80, 100]),
        ),
        legend=dict(orientation="h", y=1.1, x=0.2),
        margin=dict(l=40, r=40, t=70, b=40),
        height=520
    )
    return fig


def plot_bar_comparison(table: pd.DataFrame, player_a: str, player_b: str):
    bar = table.dropna(subset=["player_a", "player_b"]).copy()
    if bar.empty:
        return None

    bar["diff"] = (bar["player_a"] - bar["player_b"]).abs()
    bar = bar.sort_values("diff", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bar["player_a"],
        y=bar["Mutató"],
        orientation="h",
        name=player_a,
        marker_color="#6C63FF"
    ))
    fig.add_trace(go.Bar(
        x=bar["player_b"],
        y=bar["Mutató"],
        orientation="h",
        name=player_b,
        marker_color="#00C2A8"
    ))
    fig.update_layout(
        barmode="group",
        title="Nyers mutatók összehasonlítása",
        height=max(420, len(bar) * 42),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    return fig


def top_strengths_weaknesses(table: pd.DataFrame, own_col: str, other_col: str, top_n: int = 3):
    tmp = table.dropna(subset=[own_col, other_col]).copy()
    tmp["delta"] = tmp[own_col] - tmp[other_col]
    strengths = tmp.sort_values("delta", ascending=False).head(top_n)
    weaknesses = tmp.sort_values("delta", ascending=True).head(top_n)
    return strengths, weaknesses


def bullets_from_df(df: pd.DataFrame, own_col: str, other_col: str) -> List[str]:
    items = []
    for _, row in df.iterrows():
        items.append(f"{row['Mutató']}: {row[own_col]:.2f} vs {row[other_col]:.2f}")
    return items


def summary_text(player_a: str, player_b: str, table: pd.DataFrame) -> str:
    valid = table.dropna(subset=["player_a", "player_b"]).copy()
    if valid.empty:
        return "Nincs elég adat a szöveges összehasonlításhoz."

    better_a = int((valid["player_a"] > valid["player_b"]).sum())
    better_b = int((valid["player_b"] > valid["player_a"]).sum())

    a_strengths, a_weaknesses = top_strengths_weaknesses(valid, "player_a", "player_b")
    b_strengths, b_weaknesses = top_strengths_weaknesses(valid, "player_b", "player_a")

    a_best = ", ".join(a_strengths["Mutató"].head(2).tolist())
    b_best = ", ".join(b_strengths["Mutató"].head(2).tolist())
    a_weak = ", ".join(a_weaknesses["Mutató"].head(2).tolist())
    b_weak = ", ".join(b_weaknesses["Mutató"].head(2).tolist())

    return (
        f"**{player_a}** {better_a} kiválasztott mutatóban jobb. "
        f"Fő erősségei: {a_best}. Gyengébb pontjai {player_b}-höz képest: {a_weak}.\n\n"
        f"**{player_b}** {better_b} kiválasztott mutatóban jobb. "
        f"Fő erősségei: {b_best}. Gyengébb pontjai {player_a}-hoz képest: {b_weak}."
    )


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Osszehasonlitas")
    return buffer.getvalue()


st.title("⚽ Játékos-összehasonlító Streamlit app")
st.caption("Excel + játékosfotók + pókháló + rövid scouting összefoglaló")

with st.sidebar:
    st.header("Feltöltések")
    uploaded_excel = st.file_uploader("Excel feltöltése", type=["xlsx"])
    image_a = st.file_uploader("1. játékos képe", type=["png", "jpg", "jpeg", "webp"])
    image_b = st.file_uploader("2. játékos képe", type=["png", "jpg", "jpeg", "webp"])

if uploaded_excel is None:
    st.info("Tölts fel egy összehasonlító Excel-fájlt a kezdéshez.")
    st.stop()

try:
    player_a, player_b, pos_a, pos_b, metrics_df = load_comparison_excel(uploaded_excel)
except Exception as e:
    st.error(f"Nem sikerült beolvasni az Excelt: {e}")
    st.stop()

default_group = infer_position_group(pos_a, pos_b)

with st.sidebar:
    st.header("Szűrés")
    position_group = st.selectbox(
        "Posztcsoport",
        list(POSITION_METRICS.keys()),
        index=list(POSITION_METRICS.keys()).index(default_group)
    )

    custom_metrics = []
    if position_group == "Egyedi":
        custom_metrics = st.multiselect(
            "Egyedi mutatók",
            options=metrics_df["metric"].tolist(),
            default=metrics_df["metric"].tolist()[:8],
            format_func=hu_label
        )

selected_metrics = get_selected_metrics(metrics_df, position_group, custom_metrics)

if not selected_metrics:
    st.warning("A kiválasztott posztcsoporthoz nincs elérhető mutató az Excelben.")
    st.stop()

comparison = build_comparison_table(metrics_df, selected_metrics)

top_left, top_right = st.columns(2)
with top_left:
    st.subheader(player_a)
    st.write(f"**Poszt:** {pos_a}")
    if image_a is not None:
        st.image(image_a, use_container_width=True)
with top_right:
    st.subheader(player_b)
    st.write(f"**Poszt:** {pos_b}")
    if image_b is not None:
        st.image(image_b, use_container_width=True)

st.markdown("---")

left, right = st.columns([1.05, 0.95])

with left:
    radar_fig = plot_radar(comparison, player_a, player_b)
    if radar_fig is not None:
        st.plotly_chart(radar_fig, use_container_width=True)
    else:
        st.info("Nincs elég adat a pókhálóhoz.")

    bar_fig = plot_bar_comparison(comparison, player_a, player_b)
    if bar_fig is not None:
        st.plotly_chart(bar_fig, use_container_width=True)

with right:
    st.subheader("Rövid szöveges összehasonlítás")
    st.markdown(summary_text(player_a, player_b, comparison))

    a_strengths, a_weaknesses = top_strengths_weaknesses(comparison, "player_a", "player_b")
    b_strengths, b_weaknesses = top_strengths_weaknesses(comparison, "player_b", "player_a")

    st.markdown(f"### {player_a} – erősségek")
    for item in bullets_from_df(a_strengths, "player_a", "player_b"):
        st.write("•", item)

    st.markdown(f"### {player_a} – gyengébb területek")
    for item in bullets_from_df(a_weaknesses, "player_a", "player_b"):
        st.write("•", item)

    st.markdown(f"### {player_b} – erősségek")
    for item in bullets_from_df(b_strengths, "player_b", "player_a"):
        st.write("•", item)

    st.markdown(f"### {player_b} – gyengébb területek")
    for item in bullets_from_df(b_weaknesses, "player_b", "player_a"):
        st.write("•", item)

st.markdown("---")
st.subheader("Részletes táblázat")

display_df = comparison.copy().drop(columns=["metric"]).rename(columns={
    "player_a": player_a,
    "player_b": player_b,
})
st.dataframe(display_df, use_container_width=True)

st.download_button(
    "📥 Összehasonlító tábla letöltése Excelben",
    data=dataframe_to_excel_bytes(display_df),
    file_name="jatekos_osszehasonlitas_output.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.code("streamlit run app.py", language="bash")
