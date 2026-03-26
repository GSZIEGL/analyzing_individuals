import io
import math
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Scout Comparison App", layout="wide")

# =========================
# STYLES
# =========================
st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
.card {
    background: linear-gradient(180deg, #171a21 0%, #11141b 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 16px 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}
.small-muted {color:#9aa4b2; font-size: 0.92rem;}
.legend-dot {
    display:inline-block; width:12px; height:12px; border-radius:50%; margin-right:8px;
}
.metric-row {margin-bottom: 10px;}
.metric-label {font-weight:600; margin-bottom:4px;}
.bar-wrap {display:flex; gap:14px; align-items:center;}
.bar-box {
    flex:1;
    background:#0d1117;
    border:1px solid rgba(255,255,255,0.07);
    border-radius:10px;
    height:18px;
    overflow:hidden;
}
.bar-fill-blue {
    height:100%;
    background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}
.bar-fill-green {
    height:100%;
    background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
}
.value-label {
    width:72px;
    text-align:right;
    font-size:0.92rem;
}
.section-title {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CONFIG
# =========================
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
    "Air challenges won, %": "Fejpárbaj nyerés %",
    "Shots": "Lövések"
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

# =========================
# HELPERS
# =========================
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
    # Prefer the second row if first row contains season labels like 2025/2026
    if df.shape[0] > 1 and df.shape[1] > 3:
        row1_c2 = str(df.iloc[1, 2]).strip()
        row1_c3 = str(df.iloc[1, 3]).strip()
        if row1_c2 and row1_c3 and row1_c2.lower() != "nan" and row1_c3.lower() != "nan":
            return normalize_player_name(row1_c2), normalize_player_name(row1_c3)

    for i in range(min(6, len(df))):
        c2 = str(df.iloc[i, 2]).strip() if df.shape[1] > 2 else ""
        c3 = str(df.iloc[i, 3]).strip() if df.shape[1] > 3 else ""
        if c2 and c3 and c2.lower() != "nan" and c3.lower() != "nan":
            # Skip obvious season labels
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
    if position == "Egyedi":
        wanted = custom_metrics
    else:
        wanted = POSITION_METRICS[position]
    out = all_data[all_data["metric"].isin(wanted)].copy()
    return out.head(9)

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

    size = 520
    cx = cy = size / 2
    radius = 170
    N = len(labels)

    def pt(ratio: float, angle: float):
        x = cx + radius * ratio * math.cos(angle)
        y = cy + radius * ratio * math.sin(angle)
        return x, y

    def polygon_points(values):
        pts = []
        for i, val in enumerate(values):
            angle = (2 * math.pi * i / N) - math.pi / 2
            x, y = pt(val / 100.0, angle)
            pts.append(f"{x:.1f},{y:.1f}")
        pts.append(pts[0])
        return " ".join(pts)

    grid = []
    for ring in [0.2, 0.4, 0.6, 0.8, 1.0]:
        ring_pts = []
        for i in range(N):
            angle = (2 * math.pi * i / N) - math.pi / 2
            x, y = pt(ring, angle)
            ring_pts.append(f"{x:.1f},{y:.1f}")
        ring_pts.append(ring_pts[0])
        grid.append(f"<polyline points=\"{' '.join(ring_pts)}\" fill=\"none\" stroke=\"rgba(255,255,255,0.18)\" stroke-width=\"1\"/>")

    spokes = []
    text_nodes = []
    for i, label in enumerate(labels):
        angle = (2 * math.pi * i / N) - math.pi / 2
        x, y = pt(1.0, angle)
        lx, ly = pt(1.22, angle)
        spokes.append(f"<line x1=\"{cx}\" y1=\"{cy}\" x2=\"{x:.1f}\" y2=\"{y:.1f}\" stroke=\"rgba(255,255,255,0.14)\" stroke-width=\"1\"/>")
        text_nodes.append(f"<text x=\"{lx:.1f}\" y=\"{ly:.1f}\" fill=\"white\" font-size=\"11\" text-anchor=\"middle\">{label}</text>")

    poly_a = polygon_points(a_scores)
    poly_b = polygon_points(b_scores)

    svg = f"""
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <div style="font-weight:700; font-size:1.1rem;">Pókháló – fix 0–100 skála</div>
        <div class="small-muted">
          <span class="legend-dot" style="background:#3b82f6;"></span>{player_a}
          &nbsp;&nbsp;
          <span class="legend-dot" style="background:#10b981;"></span>{player_b}
        </div>
      </div>
      <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
        {''.join(grid)}
        {''.join(spokes)}
        <polygon points="{poly_a}" fill="rgba(59,130,246,0.34)" stroke="#60a5fa" stroke-width="3"/>
        <polygon points="{poly_b}" fill="rgba(16,185,129,0.34)" stroke="#34d399" stroke-width="3"/>
        {''.join(text_nodes)}
      </svg>
      <div class="small-muted">A tengelyek a kulcsmutatókat jelölik. Kék = {player_a}, zöld = {player_b}.</div>
    </div>
    """
    return svg

def render_metric_bars(df: pd.DataFrame, player_a: str, player_b: str):
    st.markdown("### Kulcsmutatók")
    st.markdown(
        f"<div class='small-muted'><span class='legend-dot' style='background:#3b82f6;'></span>{player_a} &nbsp;&nbsp; "
        f"<span class='legend-dot' style='background:#10b981;'></span>{player_b}</div>",
        unsafe_allow_html=True
    )
    for _, row in df.iterrows():
        maxv = max(row["a"], row["b"]) if pd.notna(row["a"]) and pd.notna(row["b"]) else 1.0
        if maxv == 0:
            maxv = 1.0
        width_a = int((row["a"] / maxv) * 100) if pd.notna(row["a"]) else 0
        width_b = int((row["b"] / maxv) * 100) if pd.notna(row["b"]) else 0

        html = f"""
        <div class="card metric-row">
          <div class="metric-label">{hu(row["metric"])}</div>
          <div class="bar-wrap">
            <div style="flex:1;">
              <div class="small-muted">{player_a}</div>
              <div class="bar-box"><div class="bar-fill-blue" style="width:{width_a}%;"></div></div>
            </div>
            <div class="value-label">{row["a"]:.2f}</div>
          </div>
          <div class="bar-wrap" style="margin-top:8px;">
            <div style="flex:1;">
              <div class="small-muted">{player_b}</div>
              <div class="bar-box"><div class="bar-fill-green" style="width:{width_b}%;"></div></div>
            </div>
            <div class="value-label">{row["b"]:.2f}</div>
          </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

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
        f"A kiválasztott poszthoz tartozó fő mutatók alapján az összevetés inkább profilkülönbséget mutat, "
        f"nem csak egyszerű győztest."
    )

    bullets_a = [f"{hu(r['metric'])}: {r['a']:.2f} vs {r['b']:.2f}" for _, r in top_a.iterrows()]
    bullets_b = [f"{hu(r['metric'])}: {r['b']:.2f} vs {r['a']:.2f}" for _, r in top_b.iterrows()]
    return text, bullets_a, bullets_b

# Pure-Python PDF generator
def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

def build_simple_pdf(title: str, lines: List[str]) -> bytes:
    y = 800
    content_lines = ["BT", "/F1 16 Tf 50 810 Td", f"({_pdf_escape(title)}) Tj", "/F1 10 Tf"]
    for line in lines:
        y -= 16
        if y < 50:
            break
        content_lines.append(f"1 0 0 1 50 {y} Tm ({_pdf_escape(line)}) Tj")
    content_lines.append("ET")
    content = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(f"<< /Length {len(content)} >>\nstream\n".encode("latin-1") + content + b"\nendstream")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{i} 0 obj\n".encode("latin-1"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_pos = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)+1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf.extend(f"{off:010d} 00000 n \n".encode("latin-1"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF".encode("latin-1")
    )
    return bytes(pdf)

# =========================
# APP
# =========================
st.title("⚽ ELITE DESIGN MODE – Scout Comparison App")
st.caption("CSV alapú, posztspecifikus összehasonlítás képekkel, pókhálóval, kulcsmutatókkal és PDF exporttal.")

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

# HEADER CARDS
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"<div class='card'><h3>{player_a}</h3><div class='small-muted'>Első játékos</div></div>", unsafe_allow_html=True)
    if img_a is not None:
        st.image(img_a, use_container_width=True)
with c2:
    st.markdown(f"<div class='card'><h3>{player_b}</h3><div class='small-muted'>Második játékos</div></div>", unsafe_allow_html=True)
    if img_b is not None:
        st.image(img_b, use_container_width=True)

st.markdown("---")

left, right = st.columns([1.1, 1])

with left:
    st.markdown(build_radar_svg(filtered, player_a, player_b), unsafe_allow_html=True)

with right:
    st.markdown("<div class='card'><h3 class='section-title'>Konklúzió</h3>", unsafe_allow_html=True)
    summary, strengths_a, strengths_b = conclusions(filtered, player_a, player_b)
    st.write(summary)
    st.markdown(f"**{player_a} fő erősségei**")
    for item in strengths_a:
        st.write("•", item)
    st.markdown(f"**{player_b} fő erősségei**")
    for item in strengths_b:
        st.write("•", item)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
render_metric_bars(filtered, player_a, player_b)

st.markdown("---")
st.subheader("Részletes táblázat")
table_show = filtered.copy()
table_show["Mutató"] = table_show["metric"].map(hu)
table_show = table_show[["Mutató", "a", "b"]].rename(columns={"a": "Játékos A", "b": "Játékos B"})
st.table(table_show)

st.markdown(f"<div class='small-muted'>Játékos A = {player_a} | Játékos B = {player_b}</div>", unsafe_allow_html=True)

# PDF export
pdf_lines = [f"Poszt: {position}", ""]
pdf_lines.append("Kulcsmutatók:")
for _, row in filtered.iterrows():
    pdf_lines.append(f"{hu(row['metric'])}: {row['a']:.2f} vs {row['b']:.2f}")
pdf_lines.append("")
pdf_lines.append("Konklúzió:")
pdf_lines.append(summary)
pdf_lines.append("")
pdf_lines.append(f"{player_a} fő erősségei:")
for item in strengths_a:
    pdf_lines.append(f"- {item}")
pdf_lines.append(f"{player_b} fő erősségei:")
for item in strengths_b:
    pdf_lines.append(f"- {item}")

pdf_bytes = build_simple_pdf(f"{player_a} vs {player_b}", pdf_lines)

st.download_button(
    "📄 PDF letöltése",
    data=pdf_bytes,
    file_name="scout_report.pdf",
    mime="application/pdf"
)
