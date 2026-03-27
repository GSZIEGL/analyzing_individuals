
def fmt_val(x):
    try:
        x = float(x)
        if x.is_integer():
            return str(int(x))
        return str(round(x,2)).rstrip('0').rstrip('.')
    except:
        return x
import io
import math
from typing import Dict, List, Tuple

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

def extract_names(df: pd.DataFrame) -> Tuple[str, str]:
    if df.shape[0] > 1 and df.shape[1] > 3:
        row1_c2 = str(df.iloc[1, 2]).strip()
        row1_c3 = str(df.iloc[1, 3]).strip()
        if row1_c2 and row1_c3 and row1_c2.lower() != "nan" and row1_c3.lower() != "nan":
            return normalize_player_name(row1_c2), normalize_player_name(row1_c3)

    for i in range(min(6, len(df))):
        c2 = str(df.iloc[i, 2]).strip() if df.shape[1] > 2 else ""
        c3 = str(df.iloc[i, 3]).strip() if df.shape[1] > 3 else ""
        if c2 and c3 and c2.lower() != "nan" and c3.lower() != "nan":
            if "2025/" in c2 or "2026" in c2 or "2025/" in c3 or "2026" in c3:
                continue
            return normalize_player_name(c2), normalize_player_name(c3)
    return "Játékos 1", "Játékos 2"

def extract_metrics(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for i in range(len(df)):
        metric = str(df.iloc[i, 0]).strip()
        if metric.lower() in {"nan", "", "index", "minutes played", "position"}:
            continue
        if df.shape[1] < 4:
            continue
        a = safe_float(df.iloc[i, 2])
        b = safe_float(df.iloc[i, 3])
        if pd.isna(a) and pd.isna(b):
            continue
        rows.append({"metric": metric, "a": a, "b": b})
    return pd.DataFrame(rows)

def pick_metrics(all_data: pd.DataFrame, position: str, custom_metrics: List[str]) -> pd.DataFrame:
    wanted = custom_metrics if position == "Egyedi" else POSITION_METRICS[position]
    return all_data[all_data["metric"].isin(wanted)].copy().head(9)

def fixed_scores(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    a_scores, b_scores = [], []
    for _, row in df.iterrows():
        dynamic = 1.0
        if pd.notna(row["a"]) and pd.notna(row["b"]):
            dynamic = max(float(row["a"]), float(row["b"])) * 1.15
        ceiling = DEFAULT_CEILINGS.get(row["metric"], dynamic if dynamic > 0 else 1.0)
        if ceiling == 0 or pd.isna(row["a"]) or pd.isna(row["b"]):
            a_scores.append(np.nan)
            b_scores.append(np.nan)
            continue
        a_scores.append(min((row["a"] / ceiling) * 100, 100))
        b_scores.append(min((row["b"] / ceiling) * 100, 100))
    return np.array(a_scores, dtype=float), np.array(b_scores, dtype=float)

def build_radar_svg(df: pd.DataFrame, player_a: str, player_b: str) -> str:
    if len(df) < 3:
        return "<div class='small-muted'>Nincs elég adat a pókhálóhoz.</div>"

    labels = [hu(m) for m in df["metric"].tolist()]
    a_scores, b_scores = fixed_scores(df)
    valid = ~np.isnan(a_scores) & ~np.isnan(b_scores)
    labels = [labels[i] for i in range(len(labels)) if valid[i]]
    a_scores = a_scores[valid]
    b_scores = b_scores[valid]

    if len(labels) < 3:
        return "<div class='small-muted'>Nincs elég adat a pókhálóhoz.</div>"

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    angles_closed = np.concatenate([angles, [angles[0]]])
    a_closed = np.concatenate([a_scores, [a_scores[0]]])
    b_closed = np.concatenate([b_scores, [b_scores[0]]])

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

    ax.plot(angles_closed, a_closed, color="#60a5fa", linewidth=2.8)
    ax.fill(angles_closed, a_closed, color="#3b82f6", alpha=0.28)

    ax.plot(angles_closed, b_closed, color="#34d399", linewidth=2.8)
    ax.fill(angles_closed, b_closed, color="#10b981", alpha=0.28)

    from matplotlib.lines import Line2D
    legend_items = [
        Line2D([0], [0], color="#60a5fa", lw=3, label=player_a),
        Line2D([0], [0], color="#34d399", lw=3, label=player_b),
    ]
    leg = ax.legend(
        handles=legend_items,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.16),
        ncol=2,
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

def render_metric_bars(df: pd.DataFrame, player_a: str, player_b: str):
    st.markdown("### Kulcsmutatók")
    st.markdown(
        f"<div class='small-muted'><span class='legend-dot' style='background:#3b82f6;'></span>{player_a} &nbsp;&nbsp; "
        f"<span class='legend-dot' style='background:#10b981;'></span>{player_b}</div><div style='height:12px;'></div>",
        unsafe_allow_html=True
    )
    for _, row in df.iterrows():
        maxv = max(row["a"], row["b"]) if pd.notna(row["a"]) and pd.notna(row["b"]) else 1.0
        if maxv == 0:
            maxv = 1.0
        width_a = int((row["a"] / maxv) * 100) if pd.notna(row["a"]) else 0
        width_b = int((row["b"] / maxv) * 100) if pd.notna(row["b"]) else 0
        st.markdown(f"""
        <div class="card metric-row keep-together">
          <div class="metric-label">{hu(row["metric"])}</div>
          <div class="bar-wrap">
            <div style="flex:1;">
              <div class="small-muted">{player_a}</div>
              <div class="bar-box"><div class="bar-fill-blue" style="width:{width_a}%;"></div></div>
            </div>
            <div class="value-label">{fmt_val(val) if 'val' in locals() else ''}</div>
          </div>
          <div class="bar-wrap" style="margin-top:8px;">
            <div style="flex:1;">
              <div class="small-muted">{player_b}</div>
              <div class="bar-box"><div class="bar-fill-green" style="width:{width_b}%;"></div></div>
            </div>
            <div class="value-label">{fmt_val(val) if 'val' in locals() else ''}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

def conclusions(df: pd.DataFrame, player_a: str, player_b: str) -> Tuple[str, List[str], List[str]]:
    tmp = df.dropna(subset=["a", "b"]).copy()
    if tmp.empty:
        return "Nincs elég adat a konklúzióhoz.", [], []

    tmp["diff"] = tmp["a"] - tmp["b"]
    better_a = int((tmp["a"] > tmp["b"]).sum())
    better_b = int((tmp["b"] > tmp["a"]).sum())

    top_a = tmp.sort_values("diff", ascending=False).head(3)
    top_b = tmp.sort_values("diff", ascending=True).head(3)

    text = (
        f"{player_a} {better_a} kulcsmutatóban jobb, míg {player_b} {better_b} kulcsmutatóban erősebb. "
        f"A kiválasztott poszthoz tartozó fő mutatók alapján ez inkább profilkülönbség, mint abszolút fölény."
    )

    bullets_a = [f"{hu(r['metric'])}: {fmt_val(r['a'])} vs {fmt_val(r['b'])}" for _, r in top_a.iterrows()]
    bullets_b = [f"{hu(r['metric'])}: {fmt_val(r['b'])} vs {fmt_val(r['a'])}" for _, r in top_b.iterrows()]
    return text, bullets_a, bullets_b

st.title("Játékos-összehasonlítás")

with st.sidebar:
    st.header("Feltöltések")
    uploaded = st.file_uploader("CSV feltöltése", type=["csv"])
    img_a = st.file_uploader("1. játékos képe", type=["png", "jpg", "jpeg", "webp"])
    img_b = st.file_uploader("2. játékos képe", type=["png", "jpg", "jpeg", "webp"])

if uploaded is None:
    st.info("Tölts fel egy CSV-fájlt a kezdéshez.")
    st.stop()

try:
    df_raw = try_read_csv(uploaded)
except Exception as e:
    st.error(f"Nem sikerült beolvasni a fájlt: {e}")
    st.stop()

player_a, player_b = extract_names(df_raw)
all_data = extract_metrics(df_raw)

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

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"<div class='card keep-together name-card' style='margin-bottom:14px;'><h3>{player_a}</h3></div>", unsafe_allow_html=True)
    if img_a is not None:
        st.image(img_a, use_container_width=True)
with c2:
    st.markdown(f"<div class='card keep-together name-card' style='margin-bottom:14px;'><h3>{player_b}</h3></div>", unsafe_allow_html=True)
    if img_b is not None:
        st.image(img_b, use_container_width=True)

summary, strengths_a, strengths_b = conclusions(filtered, player_a, player_b)
st.markdown("<div class='radar-grid'>", unsafe_allow_html=True)
st.markdown(build_radar_svg(filtered, player_a, player_b), unsafe_allow_html=True)
st.markdown("<div class='card keep-together'><h3 class='section-title'>Konklúzió</h3>", unsafe_allow_html=True)
st.write(summary)
st.markdown(f"**{player_a} fő erősségei**")
for item in strengths_a:
    st.write("•", item)
st.markdown(f"**{player_b} fő erősségei**")
for item in strengths_b:
    st.write("•", item)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr class='page-break'>", unsafe_allow_html=True)

render_metric_bars(filtered, player_a, player_b)

st.markdown("---")
st.subheader("Részletes táblázat")
table_show = filtered.copy()
table_show["Mutató"] = table_show["metric"].map(hu)
table_show = table_show[["Mutató", "a", "b"]].rename(columns={"a": "Játékos A", "b": "Játékos B"})
st.table(table_show)
