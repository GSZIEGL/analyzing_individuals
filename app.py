import io
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import pi
import streamlit as st


st.set_page_config(page_title="Játékos-összehasonlító app", layout="wide")

# -----------------------------
# Konfiguráció
# -----------------------------

POSITION_METRICS: Dict[str, List[str]] = {
    "CF": [
        "Goals", "xG", "Shots", "Shots on target", "Chances", "Chances created",
        "Key passes", "Attacking challenges won, %", "Dribbles"
    ],
    "ST": [
        "Goals", "xG", "Shots", "Shots on target", "Chances", "Chances created",
        "Key passes", "Attacking challenges won, %", "Dribbles"
    ],
    "CAM": [
        "Goals", "Assists", "Chances created", "Key passes", "Progressive passes",
        "Passes into the penalty box", "Passes for a shot", "Dribbles", "xG"
    ],
    "WINGER": [
        "Goals", "Assists", "Chances created", "Key passes", "Crosses",
        "Crosses accurate, %", "Dribbles", "Dribbling in the final third",
        "xG"
    ],
    "CM": [
        "Assists", "Progressive passes", "Passes", "Passes accurate, %",
        "Key passes", "Interceptions", "Challenges won, %", "xG"
    ],
    "DM": [
        "Passes", "Passes accurate, %", "Progressive passes", "Interceptions",
        "Tackles", "Tackles successful, %", "Defensive challenges won, %",
        "Air challenges won, %"
    ],
    "CB": [
        "Passes", "Passes accurate, %", "Long passes", "Long passes accurate, %",
        "Defensive challenges won, %", "Air challenges won, %",
        "Interceptions", "Tackles successful, %"
    ],
    "FB/WB": [
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
    "Dribbling in the final third": "Cselek a támadó harmadban",
    "Attacking challenges won, %": "Támadó párharc nyerés %",
    "Challenges won, %": "Párharc nyerés %",
    "Defensive challenges won, %": "Védő párharc nyerés %",
    "Air challenges won, %": "Fejpárbaj nyerés %",
    "Interceptions": "Interceptionök",
    "Tackles": "Szerelések",
    "Tackles successful, %": "Sikeres szerelések %",
    "xG": "xG",
}

# Fix 0-100 skála (életszerű plafonok, per 90)
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
    "Dribbling in the final third": 4.00,
    "Attacking challenges won, %": 1.00,
    "Challenges won, %": 1.00,
    "Defensive challenges won, %": 1.00,
    "Air challenges won, %": 1.00,
    "Interceptions": 5.00,
    "Tackles": 4.00,
    "Tackles successful, %": 1.00,
    "xG": 0.80,
}


def clean_numeric(value) -> float:
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

    player_a = str(df.iloc[1, 2]).strip()
    player_b = str(df.iloc[1, 3]).strip()
    position_a = str(df.iloc[4, 2]).strip()
    position_b = str(df.iloc[4, 3]).strip()

    metrics_df = pd.DataFrame({
        "metric": df.iloc[2:, 0].astype(str).str.strip(),
        "player_a": [clean_numeric(v) for v in df.iloc[2:, 2]],
        "player_b": [clean_numeric(v) for v in df.iloc[2:, 3]],
    })

    metrics_df = metrics_df.dropna(subset=["metric"]).reset_index(drop=True)
    metrics_df = metrics_df[~metrics_df["metric"].isin(["nan", "Index", "Minutes played", "Position"])].copy()
    return player_a, player_b, position_a, position_b, metrics_df


def infer_position_group(pos_a: str, pos_b: str) -> str:
    positions = f"{pos_a} {pos_b}".upper()
    if any(x in positions for x in ["CF", "ST"]):
        return "CF"
    if any(x in positions for x in ["CAM", "AM", "LAM", "RAM", "RCAM", "LCAM"]):
        return "CAM"
    if any(x in positions for x in ["LW", "RW", "WINGER"]):
        return "WINGER"
    if any(x in positions for x in ["DM", "CDM"]):
        return "DM"
    if any(x in positions for x in ["CB"]):
        return "CB"
    if any(x in positions for x in ["WB", "LB", "RB", "LWB", "RWB"]):
        return "FB/WB"
    if any(x in positions for x in ["CM", "LCM", "RCM"]):
        return "CM"
    return "CAM"


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
    table["Jobbik játékos"] = np.where(
        table["player_a"].fillna(-999) > table["player_b"].fillna(-999), "A",
        np.where(table["player_b"].fillna(-999) > table["player_a"].fillna(-999), "B", "Döntetlen")
    )
    return table[["Mutató", "player_a", "player_b", "Jobbik játékos", "metric"]]


def fixed_scale_scores(table: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    a_scores, b_scores = [], []
    for _, row in table.iterrows():
        metric = row["metric"]
        ceiling = METRIC_CEILINGS.get(metric)
        if ceiling is None or pd.isna(row["player_a"]) or pd.isna(row["player_b"]):
            a_scores.append(np.nan)
            b_scores.append(np.nan)
            continue
        a_scores.append(min((row["player_a"] / ceiling) * 100, 100))
        b_scores.append(min((row["player_b"] / ceiling) * 100, 100))
    return np.array(a_scores, dtype=float), np.array(b_scores, dtype=float)


def plot_radar(table: pd.DataFrame, player_a: str, player_b: str):
    radar_table = table.dropna(subset=["player_a", "player_b"]).copy()
    if radar_table.empty:
        return None

    labels = radar_table["Mutató"].tolist()
    a_scores, b_scores = fixed_scale_scores(radar_table)

    valid = ~np.isnan(a_scores) & ~np.isnan(b_scores)
    labels = [labels[i] for i in range(len(labels)) if valid[i]]
    a_scores = a_scores[valid]
    b_scores = b_scores[valid]

    if len(labels) < 3:
        return None

    N = len(labels)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    a_plot = list(a_scores) + [a_scores[0]]
    b_plot = list(b_scores) + [b_scores[0]]

    fig = plt.figure(figsize=(7, 7))
    ax = plt.subplot(111, polar=True)

    ax.plot(angles, a_plot, linewidth=2.5, label=player_a)
    ax.fill(angles, a_plot, alpha=0.20)

    ax.plot(angles, b_plot, linewidth=2.5, label=player_b)
    ax.fill(angles, b_plot, alpha=0.20)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=9)
    ax.set_title("Pókháló – fix 0–100 skála", pad=24, fontsize=16)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=2, fontsize=10)
    fig.tight_layout()
    return fig


def plot_bar_comparison(table: pd.DataFrame, player_a: str, player_b: str):
    bar = table.dropna(subset=["player_a", "player_b"]).copy()
    if bar.empty:
        return None

    bar = bar.copy()
    bar["diff"] = (bar["player_a"] - bar["player_b"]).abs()
    bar = bar.sort_values("diff", ascending=True)

    fig = plt.figure(figsize=(8, max(4, len(bar) * 0.5)))
    ax = plt.gca()
    y = np.arange(len(bar))

    ax.barh(y - 0.18, bar["player_a"], height=0.35, label=player_a)
    ax.barh(y + 0.18, bar["player_b"], height=0.35, label=player_b)

    ax.set_yticks(y)
    ax.set_yticklabels(bar["Mutató"])
    ax.set_title("Nyers mutatók összehasonlítása")
    ax.legend()
    fig.tight_layout()
    return fig


def top_strengths_weaknesses(table: pd.DataFrame, player_col: str, other_col: str, top_n: int = 3):
    tmp = table.dropna(subset=[player_col, other_col]).copy()
    tmp["delta"] = tmp[player_col] - tmp[other_col]
    strengths = tmp.sort_values("delta", ascending=False).head(top_n)
    weaknesses = tmp.sort_values("delta", ascending=True).head(top_n)
    return strengths, weaknesses


def make_bullets(strengths: pd.DataFrame, weaknesses: pd.DataFrame, own_col: str, other_col: str) -> Tuple[List[str], List[str]]:
    s_list, w_list = [], []
    for _, row in strengths.iterrows():
        s_list.append(f"{row['Mutató']}: {row[own_col]:.2f} vs {row[other_col]:.2f}")
    for _, row in weaknesses.iterrows():
        w_list.append(f"{row['Mutató']}: {row[own_col]:.2f} vs {row[other_col]:.2f}")
    return s_list, w_list


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
        f"**{player_a}** {better_a} kiválasztott mutatóban jobb, "
        f"fő erősségei: {a_best}. Ahol kevésbé erős {player_b}-höz képest: {a_weak}.\n\n"
        f"**{player_b}** {better_b} kiválasztott mutatóban jobb, "
        f"fő erősségei: {b_best}. Ahol kevésbé erős {player_a}-hoz képest: {b_weak}."
    )


def dataframe_to_download_bytes(df: pd.DataFrame) -> bytes:
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Osszehasonlitas")
    return out.getvalue()


st.title("⚽ Játékos-összehasonlító app")
st.caption("Excel alapú, posztspecifikus összehasonlítás két játékos között.")

uploaded = st.file_uploader("Töltsd fel az összehasonlító Excel-fájlt", type=["xlsx"])

demo_path = "26.03.2026 - Gergő Pálinkás - Comparison.xlsx"
use_demo = st.toggle("Demo fájl használata, ha nincs feltöltés", value=True)

if uploaded is None and use_demo:
    uploaded = demo_path

if uploaded is None:
    st.info("Tölts fel egy Excel-fájlt a folytatáshoz.")
    st.stop()

try:
    player_a, player_b, pos_a, pos_b, metrics_df = load_comparison_excel(uploaded)
except Exception as e:
    st.error(f"Nem sikerült beolvasni az Excel-fájlt. Részletek: {e}")
    st.stop()

default_group = infer_position_group(pos_a, pos_b)

with st.sidebar:
    st.header("Beállítások")
    position_group = st.selectbox(
        "Posztcsoport",
        options=list(POSITION_METRICS.keys()),
        index=list(POSITION_METRICS.keys()).index(default_group) if default_group in POSITION_METRICS else 0
    )

    custom_metrics = []
    if position_group == "Egyedi":
        custom_metrics = st.multiselect(
            "Válassz egyedi mutatókat",
            options=metrics_df["metric"].tolist(),
            default=metrics_df["metric"].tolist()[:8],
            format_func=hu_label
        )

selected_metrics = get_selected_metrics(metrics_df, position_group, custom_metrics)

if not selected_metrics:
    st.warning("Ehhez a poszthoz nincs elérhető mutató az Excelben. Válassz másik posztot vagy egyedi módot.")
    st.stop()

comparison = build_comparison_table(metrics_df, selected_metrics)
comparison_display = comparison.copy().rename(columns={
    "player_a": player_a,
    "player_b": player_b,
})

col1, col2 = st.columns(2)
with col1:
    st.subheader(player_a)
    st.write(f"**Poszt:** {pos_a}")
with col2:
    st.subheader(player_b)
    st.write(f"**Poszt:** {pos_b}")

st.markdown("---")

left, right = st.columns([1.15, 1])

with left:
    radar_fig = plot_radar(comparison, player_a, player_b)
    if radar_fig is not None:
        st.pyplot(radar_fig, clear_figure=True)
    else:
        st.info("Nincs elég adat a pókhálóhoz.")

with right:
    st.subheader("Rövid szöveges összehasonlítás")
    st.markdown(summary_text(player_a, player_b, comparison))

    a_strengths, a_weaknesses = top_strengths_weaknesses(comparison, "player_a", "player_b")
    b_strengths, b_weaknesses = top_strengths_weaknesses(comparison, "player_b", "player_a")

    a_s, a_w = make_bullets(a_strengths, a_weaknesses, "player_a", "player_b")
    b_s, b_w = make_bullets(b_strengths, b_weaknesses, "player_b", "player_a")

    st.markdown(f"### {player_a} – erősségek")
    for item in a_s:
        st.write("•", item)

    st.markdown(f"### {player_a} – gyengébb területek")
    for item in a_w:
        st.write("•", item)

    st.markdown(f"### {player_b} – erősségek")
    for item in b_s:
        st.write("•", item)

    st.markdown(f"### {player_b} – gyengébb területek")
    for item in b_w:
        st.write("•", item)

st.markdown("---")

bar_fig = plot_bar_comparison(comparison, player_a, player_b)
if bar_fig is not None:
    st.pyplot(bar_fig, clear_figure=True)

st.subheader("Részletes táblázat")
show_df = comparison_display.drop(columns=["metric"])
st.dataframe(show_df, use_container_width=True)

excel_bytes = dataframe_to_download_bytes(show_df)
st.download_button(
    "📥 Táblázat letöltése Excelben",
    data=excel_bytes,
    file_name="jatekos_osszehasonlitas_output.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.code("streamlit run app.py", language="bash")
