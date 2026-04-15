def fmt_val(x):
    try:
        x = float(x)
        if x.is_integer():
            return str(int(x))
        return str(round(x, 2)).rstrip('0').rstrip('.')
    except:
        return x

import io
import math
from typing import Dict, List

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import base64

st.set_page_config(page_title="Scout Comparison App", layout="wide")

st.markdown("""
<style>
:root{
  --bg:#0f1117;
  --card:#171a21;
  --card2:#11141b;
  --line:rgba(255,255,255,0.08);
  --muted:#9aa4b2;
  --blue:#3b82f6;
  --blue2:#60a5fa;
  --green:#10b981;
  --green2:#34d399;
  --orange:#f59e0b;
  --orange2:#fbbf24;
}

.block-container{
  padding-top:1rem;
  padding-bottom:2rem;
  max-width:1400px;
}

html, body, [data-testid="stAppViewContainer"]{
  background:var(--bg);
}

.card{
  background: linear-gradient(180deg, var(--card) 0%, var(--card2) 100%);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  overflow:hidden;
}

.name-card h3{
  margin:0;
  font-size:2.2rem;
}

.small-muted{
  color:var(--muted);
  font-size:0.92rem;
}

.legend-dot{
  display:inline-block;
  width:12px;
  height:12px;
  border-radius:50%;
  margin-right:8px;
}

.metric-row{margin-bottom:10px;}
.metric-label{font-weight:600; margin-bottom:4px;}
.bar-wrap{display:flex; gap:14px; align-items:center;}
.bar-box{
  flex:1;
  background:#0d1117;
  border:1px solid rgba(255,255,255,0.07);
  border-radius:10px;
  height:18px;
  overflow:hidden;
}
.bar-fill-blue{
  height:100%;
  background: linear-gradient(90deg, var(--blue) 0%, var(--blue2) 100%);
}
.bar-fill-green{
  height:100%;
  background: linear-gradient(90deg, var(--green) 0%, var(--green2) 100%);
}
.bar-fill-orange{
  height:100%;
  background: linear-gradient(90deg, var(--orange) 0%, var(--orange2) 100%);
}
.value-label{
  width:72px;
  text-align:right;
  font-size:0.92rem;
}
.section-title{
  margin-top:0;
  margin-bottom:0.8rem;
}

.player-photo-wrap{
  display:flex;
  align-items:center;
  justify-content:center;
  border-radius:16px;
  overflow:hidden;
  border:1px solid rgba(255,255,255,0.08);
  background:#0d1117;
}

.player-photo-wrap img{
  display:block;
  width:100%;
  height:auto;
  object-fit:cover;
}

.radar-card svg{
  display:block;
  width:100%;
  height:auto;
  max-width:100%;
}

.radar-card{
  overflow:hidden;
}

.radar-grid{
  display:grid;
  grid-template-columns:minmax(0,1.08fr) minmax(0,0.92fr);
  gap:24px;
  align-items:start;
}

.page-break{
  height:1px;
  border:none;
  margin:24px 0;
}

@media (max-width: 1100px){
  .radar-grid{
    grid-template-columns:1fr;
  }
}

@media print {
    .page-break {
        page-break-before: always;
        break-before: page;
    }
  @page{
    size:A4 portrait;
    margin:10mm 9mm 10mm 9mm;
  }

  html, body{
    background:white !important;
    color:black !important;
    -webkit-print-color-adjust:exact;
    print-color-adjust:exact;
  }

  [data-testid="stSidebar"],
  header,
  footer,
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  [data-testid="stFileUploaderDropzoneInstructions"],
  .stDownloadButton,
  .print-hide,
  hr{
    display:none !important;
  }

  [data-testid="stAppViewContainer"],
  [data-testid="stMainBlockContainer"],
  .block-container{
    background:white !important;
    color:black !important;
    max-width:100% !important;
    padding:0 !important;
    margin:0 !important;
  }

  [data-testid="stVerticalBlock"]{
    gap:0.4rem !important;
  }

  .card{
    background:white !important;
    color:black !important;
    border:1px solid #d9d9d9 !important;
    box-shadow:none !important;
    break-inside:avoid;
    page-break-inside:avoid;
    margin-bottom:8px !important;
  }

  .small-muted{
    color:#444 !important;
  }

  h1, h2, h3, h4, p, div, span, strong, li, label{
    color:black !important;
  }

  .player-photo-wrap{
    background:white !important;
    border:1px solid #d9d9d9 !important;
    break-inside:avoid;
    page-break-inside:avoid;
  }

  .player-photo-wrap img{
    max-height:86mm;
    object-fit:contain;
  }

  .stImage,
  [data-testid="stImage"],
  [data-testid="column"]{
    break-inside:avoid;
    page-break-inside:avoid;
  }

  .bar-box{
    background:#f1f1f1 !important;
    border:1px solid #d0d0d0 !important;
  }

  .bar-fill-blue{
    background:#3b82f6 !important;
  }

  .bar-fill-green{
    background:#10b981 !important;
  }

  .bar-fill-orange{
    background:#f59e0b !important;
  }

  svg text{
    fill:black !important;
  }

  .first-page-block,
  .keep-together,
  .radar-grid,
  .radar-card{
    break-inside:avoid;
    page-break-inside:avoid;
  }

  .page-break{
    break-before:page;
    page-break-before:always;
  }
}
</style>
""", unsafe_allow_html=True)

POSITION_METRICS: Dict[str, List[str]] = {
    "Támadó": [
        "Goals", "xG", "Shots", "Shots on target", "Assists",
        "Chances created", "Key passes", "Dribbles", "Progressive passes"
    ],
    "Támadó középpályás": [
        "Goals", "Assists", "Chances created", "Key passes",
        "Progressive passes", "Passes for a shot", "Dribbles", "xG"
    ],
    "Középpályás": [
        "Assists", "Passes", "Passes accurate, %", "Progressive passes",
        "Interceptions", "Key passes", "Challenges won, %"
    ],
    "Védő": [
        "Passes", "Passes accurate, %", "Interceptions", "Tackles",
        "Tackles successful, %", "Air challenges won, %"
    ],
    "Egyedi": []
}

LABELS_HU: Dict[str, str] = {
    "Goals": "Gólok",
    "xG": "xG",
    "Assists": "Asszisztok",
    "Shots": "Lövések",
    "Shots on target": "Kaput eltaláló lövések",
    "Chances created": "Helyzetkialakítás",
    "Key passes": "Kulcspasszok",
    "Progressive passes": "Progresszív passzok",
    "Passes for a shot": "Lövést előkészítő passzok",
    "Dribbles": "Cselek",
    "Passes": "Passzok",
    "Passes accurate, %": "Passzpontosság %",
    "Interceptions": "Interceptionök",
    "Challenges won, %": "Párharc nyerés %",
    "Tackles": "Szerelések",
    "Tackles successful, %": "Sikeres szerelések %",
    "Air challenges won, %": "Fejpárbaj nyerés %"
}

DEFAULT_CEILINGS: Dict[str, float] = {
    "Goals": 0.80,
    "xG": 0.80,
    "Assists": 0.50,
    "Shots": 5.00,
    "Shots on target": 2.00,
    "Chances created": 2.50,
    "Key passes": 2.50,
    "Progressive passes": 12.00,
    "Passes for a shot": 2.50,
    "Dribbles": 6.00,
    "Passes": 90.00,
    "Passes accurate, %": 1.00,
    "Interceptions": 5.00,
    "Challenges won, %": 1.00,
    "Tackles": 4.00,
    "Tackles successful, %": 1.00,
    "Air challenges won, %": 1.00,
}

PLAYER_COLORS = [
    {"name": "Kék", "line": "#60a5fa", "fill": "#3b82f6", "bar_class": "bar-fill-blue"},
    {"name": "Zöld", "line": "#34d399", "fill": "#10b981", "bar_class": "bar-fill-green"},
    {"name": "Narancs", "line": "#fbbf24", "fill": "#f59e0b", "bar_class": "bar-fill-orange"},
]

def hu(metric: str) -> str:
    return LABELS_HU.get(metric, metric)

def safe_float(v):
    if pd.isna(v):
        return np.nan
    s = str(v).strip().replace(",", ".")
    if s in {"", "-", "—", "nan", "None"}:
        return np.nan
    try:
        return float(s)
    except Exception:
        return np.nan

def try_read_csv(uploaded_file) -> pd.DataFrame:
    raw = uploaded_file.getvalue()
    last_err = None
    for enc in ["utf-8", "utf-8-sig", "cp1250", "latin1"]:
        for sep in [";", ",", "\t"]:
            try:
                text = raw.decode(enc, errors="ignore")
                df = pd.read_csv(io.StringIO(text), sep=sep, header=None, engine="python")
                if df.shape[1] >= 4:
                    return df
            except Exception as e:
                last_err = e
                continue
    raise ValueError(f"Nem sikerült beolvasni a CSV-t. Utolsó hiba: {last_err}")

def normalize_player_name(name: str) -> str:
    name = str(name).strip()
    mapping = {
        "Gergő Pálinkás": "Pálinkás Gergő",
        "Mate Gyurko": "Gyurkó Máté",
        "Máté Gyurkó": "Gyurkó Máté"
    }
    return mapping.get(name, name)

def detect_player_columns(df: pd.DataFrame) -> List[int]:
    candidates = []
    for col in range(2, df.shape[1]):
        numeric_count = 0
        for i in range(len(df)):
            val = safe_float(df.iloc[i, col])
            if pd.notna(val):
                numeric_count += 1
        if numeric_count >= 3:
            candidates.append(col)
    return candidates[:3]

def extract_names(df: pd.DataFrame, player_cols: List[int]) -> List[str]:
    names = []

    if df.shape[0] > 1:
        for col in player_cols:
            cell = str(df.iloc[1, col]).strip()
            if cell and cell.lower() != "nan":
                names.append(normalize_player_name(cell))
            else:
                names.append("")
        if all(n != "" for n in names):
            return names

    names = []
    for col in player_cols:
        found_name = None
        for i in range(min(6, len(df))):
            cell = str(df.iloc[i, col]).strip()
            if not cell or cell.lower() == "nan":
                continue
            if "2025/" in cell or "2026" in cell or "2024/" in cell:
                continue
            if pd.notna(safe_float(cell)):
                continue
            found_name = normalize_player_name(cell)
            break
        names.append(found_name if found_name else f"Játékos {len(names)+1}")

    return names

def extract_metrics(df: pd.DataFrame, player_cols: List[int]) -> pd.DataFrame:
    rows = []
    for i in range(len(df)):
        metric = str(df.iloc[i, 0]).strip()
        if metric.lower() in {"nan", "", "index", "minutes played", "position"}:
            continue

        row_data = {"metric": metric}
        valid_numeric = False

        for idx, col in enumerate(player_cols):
            val = safe_float(df.iloc[i, col]) if col < df.shape[1] else np.nan
            row_data[f"p{idx+1}"] = val
            if pd.notna(val):
                valid_numeric = True

        if valid_numeric:
            rows.append(row_data)

    return pd.DataFrame(rows)

def pick_metrics(all_data: pd.DataFrame, position: str, custom_metrics: List[str]) -> pd.DataFrame:
    wanted = custom_metrics if position == "Egyedi" else POSITION_METRICS[position]
    return all_data[all_data["metric"].isin(wanted)].copy().head(9)

def fixed_scores(df: pd.DataFrame, n_players: int) -> Dict[str, np.ndarray]:
    scores = {f"p{i+1}": [] for i in range(n_players)}

    for _, row in df.iterrows():
        vals = []
        for i in range(n_players):
            v = row.get(f"p{i+1}", np.nan)
            if pd.notna(v):
                vals.append(float(v))

        dynamic = max(vals) * 1.15 if vals else 1.0
        ceiling = DEFAULT_CEILINGS.get(row["metric"], dynamic if dynamic > 0 else 1.0)

        for i in range(n_players):
            v = row.get(f"p{i+1}", np.nan)
            if ceiling == 0 or pd.isna(v):
                scores[f"p{i+1}"].append(np.nan)
            else:
                scores[f"p{i+1}"].append(min((v / ceiling) * 100, 100))

    for k in scores:
        scores[k] = np.array(scores[k], dtype=float)

    return scores

def build_radar_svg(df: pd.DataFrame, player_names: List[str]) -> str:
    if len(df) < 3:
        return "<div class='small-muted'>Nincs elég adat a pókhálóhoz.</div>"

    n_players = len(player_names)
    labels = [hu(m) for m in df["metric"].tolist()]
    scores = fixed_scores(df, n_players)

    valid = np.ones(len(df), dtype=bool)
    for i in range(n_players):
        valid &= ~np.isnan(scores[f"p{i+1}"])

    labels = [labels[i] for i in range(len(labels)) if valid[i]]
    filtered_scores = {}
    for i in range(n_players):
        filtered_scores[f"p{i+1}"] = scores[f"p{i+1}"][valid]

    if len(labels) < 3:
        return "<div class='small-muted'>Nincs elég adat a pókhálóhoz.</div>"

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    angles_closed = np.concatenate([angles, [angles[0]]])

    fig, ax = plt.subplots(figsize=(6.2, 6.2), subplot_kw={"polar": True}, facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=9, color="#cbd5e1")
    ax.set_rlabel_position(0)

    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=10, color="white")

    ax.yaxis.grid(True, color="#94a3b8", linewidth=1.2, alpha=0.9)
    ax.xaxis.grid(True, color="#64748b", linewidth=1.0, alpha=0.85)
    ax.spines["polar"].set_color("#e2e8f0")
    ax.spines["polar"].set_linewidth(1.2)

    from matplotlib.lines import Line2D
    legend_items = []

    for i, player_name in enumerate(player_names):
        color_cfg = PLAYER_COLORS[i]
        arr = filtered_scores[f"p{i+1}"]
        closed = np.concatenate([arr, [arr[0]]])

        ax.plot(angles_closed, closed, color=color_cfg["line"], linewidth=2.8)
        ax.fill(angles_closed, closed, color=color_cfg["fill"], alpha=0.22)

        legend_items.append(
            Line2D([0], [0], color=color_cfg["line"], lw=3, label=player_name)
        )

    leg = ax.legend(
        handles=legend_items,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.18),
        ncol=min(3, len(player_names)),
        frameon=False,
        fontsize=10,
    )
    for txt in leg.get_texts():
        txt.set_color("white")

    plt.tight_layout(pad=2.0)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")

    return f"""
    <div class="card keep-together">
      <div style="font-weight:700; font-size:1.1rem; margin-bottom:8px;">Pókháló – fix 0–100 skála</div>
      <img style="margin-top:8px;" src="data:image/png;base64,{img_b64}" style="width:100%; max-width:620px; display:block; margin:0 auto;" />
    </div>
    """

def render_metric_bars(df: pd.DataFrame, player_names: List[str]):
    st.markdown("### Kulcsmutatók")

    legend_html_parts = []
    for i, name in enumerate(player_names):
        dot_color = PLAYER_COLORS[i]["fill"]
        legend_html_parts.append(
            f"<span class='legend-dot' style='background:{dot_color};'></span>{name}"
        )

    st.markdown(
        f"<div class='small-muted'>{' &nbsp;&nbsp; '.join(legend_html_parts)}</div><div style='height:12px;'></div>",
        unsafe_allow_html=True
    )

    for _, row in df.iterrows():
        vals = []
        for i in range(len(player_names)):
            v = row.get(f"p{i+1}", np.nan)
            if pd.notna(v):
                vals.append(v)

        maxv = max(vals) if vals else 1.0
        if maxv == 0:
            maxv = 1.0

        html = f"""
        <div class="card metric-row keep-together">
          <div class="metric-label">{hu(row["metric"])}</div>
        """

        for i, name in enumerate(player_names):
            v = row.get(f"p{i+1}", np.nan)
            width = int((v / maxv) * 100) if pd.notna(v) else 0
            bar_class = PLAYER_COLORS[i]["bar_class"]
            display_val = fmt_val(v) if pd.notna(v) else "-"

            html += f"""
            <div class="bar-wrap" style="margin-top:{'0' if i == 0 else '8px'};">
              <div style="flex:1;">
                <div class="small-muted">{name}</div>
                <div class="bar-box"><div class="{bar_class}" style="width:{width}%;"></div></div>
              </div>
              <div class="value-label">{display_val}</div>
            </div>
            """

        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

def conclusions(df: pd.DataFrame, player_names: List[str]):
    player_cols = [f"p{i+1}" for i in range(len(player_names))]
    tmp = df.dropna(subset=player_cols, how="all").copy()

    if tmp.empty:
        return "Nincs elég adat a konklúzióhoz.", {}

    wins = {name: 0 for name in player_names}
    strengths = {name: [] for name in player_names}

    for _, row in tmp.iterrows():
        vals = {player_names[i]: row.get(f"p{i+1}", np.nan) for i in range(len(player_names))}
        valid_vals = {k: v for k, v in vals.items() if pd.notna(v)}

        if len(valid_vals) < 2:
            continue

        best_player = max(valid_vals, key=valid_vals.get)
        wins[best_player] += 1

    for i, name in enumerate(player_names):
        diffs = []
        my_col = f"p{i+1}"

        for _, row in tmp.iterrows():
            my_val = row.get(my_col, np.nan)
            if pd.isna(my_val):
                continue

            others = []
            for j in range(len(player_names)):
                if i == j:
                    continue
                other_val = row.get(f"p{j+1}", np.nan)
                if pd.notna(other_val):
                    others.append(other_val)

            if not others:
                continue

            avg_others = np.mean(others)
            diffs.append({
                "metric": row["metric"],
                "my_val": my_val,
                "others_avg": avg_others,
                "diff": my_val - avg_others
            })

        diffs_df = pd.DataFrame(diffs)
        if not diffs_df.empty:
            top = diffs_df.sort_values("diff", ascending=False).head(3)
            strengths[name] = [
                f"{hu(r['metric'])}: {fmt_val(r['my_val'])} vs átlag {fmt_val(r['others_avg'])}"
                for _, r in top.iterrows()
            ]

    ranking = sorted(wins.items(), key=lambda x: x[1], reverse=True)
    ranking_text = ", ".join([f"{name}: {count}" for name, count in ranking])

    summary = (
        f"A kiválasztott kulcsmutatók alapján a legtöbb első helyezést ez a sorrend adja: {ranking_text}. "
        f"Ez inkább profilkülönbséget mutat, nem feltétlen abszolút fölényt."
    )

    return summary, strengths

st.title("Játékos-összehasonlítás")

with st.sidebar:
    st.header("Feltöltések")
    uploaded = st.file_uploader("CSV feltöltése", type=["csv"])
    img_a = st.file_uploader("1. játékos képe", type=["png", "jpg", "jpeg", "webp"])
    img_b = st.file_uploader("2. játékos képe", type=["png", "jpg", "jpeg", "webp"])
    img_c = st.file_uploader("3. játékos képe", type=["png", "jpg", "jpeg", "webp"])

if uploaded is None:
    st.info("Tölts fel egy CSV-fájlt a kezdéshez.")
    st.stop()

try:
    df_raw = try_read_csv(uploaded)
except Exception as e:
    st.error(f"Nem sikerült beolvasni a fájlt: {e}")
    st.stop()

player_cols = detect_player_columns(df_raw)

if len(player_cols) < 2:
    st.error("Legalább 2 játékos adat-oszlop szükséges a fájlban.")
    st.stop()

player_names = extract_names(df_raw, player_cols)
all_data = extract_metrics(df_raw, player_cols)

if all_data.empty:
    st.error("Nem találtam értelmezhető numerikus adatokat a fájlban.")
    st.table(df_raw.head(10).astype(str))
    st.stop()

with st.sidebar:
    st.header("Szűrés")
    position = st.selectbox("Poszt", list(POSITION_METRICS.keys()))
    custom_metrics = []
    if position == "Egyedi":
        custom_metrics = st.multiselect(
            "Mutatók kiválasztása",
            options=all_data["metric"].tolist(),
            default=all_data["metric"].tolist()[:8],
            format_func=hu
        )

filtered = pick_metrics(all_data, position, custom_metrics)
if filtered.empty:
    st.warning("Ehhez a poszthoz nincs megfelelő adat a feltöltött fájlban.")
    st.stop()

st.markdown("<div class='first-page-block'>", unsafe_allow_html=True)

imgs = [img_a, img_b, img_c]
cols = st.columns(len(player_names))

for i, name in enumerate(player_names):
    with cols[i]:
        st.markdown(
            f"<div class='card keep-together name-card' style='margin-bottom:14px;'><h3>{name}</h3></div>",
            unsafe_allow_html=True
        )
        if i < len(imgs) and imgs[i] is not None:
            st.image(imgs[i], use_container_width=True)

summary, strengths = conclusions(filtered, player_names)

st.markdown("<div class='radar-grid'>", unsafe_allow_html=True)
st.markdown(build_radar_svg(filtered, player_names), unsafe_allow_html=True)
st.markdown("<div class='card keep-together'><h3 class='section-title'>Konklúzió</h3>", unsafe_allow_html=True)
st.write(summary)

for name in player_names:
    st.markdown(f"**{name} fő erősségei**")
    if strengths.get(name):
        for item in strengths[name]:
            st.write("•", item)
    else:
        st.write("• Nincs elég adat.")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr class='page-break'>", unsafe_allow_html=True)

render_metric_bars(filtered, player_names)

st.markdown("---")
st.subheader("Részletes táblázat")
table_show = filtered.copy()
table_show["Mutató"] = table_show["metric"].map(hu)

keep_cols = ["Mutató"]
rename_map = {}
for i, name in enumerate(player_names):
    col = f"p{i+1}"
    keep_cols.append(col)
    rename_map[col] = name

table_show = table_show[["metric"] + [f"p{i+1}" for i in range(len(player_names))]].copy()
table_show["Mutató"] = table_show["metric"].map(hu)
table_show = table_show[keep_cols].rename(columns=rename_map)

st.table(table_show)
