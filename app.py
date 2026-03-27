
import streamlit as st
import pandas as pd
import math

st.set_page_config(layout="wide")

# ----------------------------
# PRINT-FRIENDLY CSS
# ----------------------------
st.markdown("""
<style>
@media print {
    .block-container {
        padding-top: 0px;
    }
    .card {
        break-inside: avoid;
        page-break-inside: avoid;
        border: 1px solid #ccc;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        background: white;
    }
    .row {
        display: flex;
        gap: 16px;
    }
    .col {
        flex: 1;
    }
    h1, h2, h3 {
        margin-bottom: 8px;
    }
}
.card {
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}
.row {
    display: flex;
    gap: 16px;
}
.col {
    flex: 1;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# DATA LOAD
# ----------------------------
uploaded_file = st.file_uploader("CSV feltöltése", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    players = df["Player"].unique()
    player_a = st.selectbox("Játékos A", players, index=0)
    player_b = st.selectbox("Játékos B", players, index=1 if len(players) > 1 else 0)

    metrics = [
        "Gólok",
        "Helyzetkialakítás",
        "Lövések",
        "Kaput eltaláló lövések",
        "Kulcspasszok",
        "Progresszív passzok",
        "Cselek",
        "xG"
    ]

    # ----------------------------
    # NORMALIZATION (0-100)
    # ----------------------------
    norm_df = df.copy()
    for m in metrics:
        if m in df.columns:
            max_val = df[m].max()
            if max_val > 0:
                norm_df[m] = df[m] / max_val * 100
            else:
                norm_df[m] = 0

    row_a = norm_df[norm_df["Player"] == player_a].iloc[0]
    row_b = norm_df[norm_df["Player"] == player_b].iloc[0]

    # ----------------------------
    # RADAR SVG (PRINT-SAFE)
    # ----------------------------
    def radar_svg(values_a, values_b, labels):
        size = 420
        center = size / 2
        radius = 140
        n = len(labels)

        angles = [2 * math.pi * i / n - math.pi/2 for i in range(n)]

        def get_points(values):
            pts = []
            for v, angle in zip(values, angles):
                r = radius * v / 100
                x = center + r * math.cos(angle)
                y = center + r * math.sin(angle)
                pts.append((x, y))
            pts.append(pts[0])
            return pts

        svg = []

        # ---- GRID (STRONG PRINT SAFE)
        levels = 5
        for i in range(1, levels + 1):
            r = radius * i / levels
            pts = []
            for angle in angles:
                x = center + r * math.cos(angle)
                y = center + r * math.sin(angle)
                pts.append((x, y))
            pts.append(pts[0])

            svg.append(
                f"<polygon points='{' '.join(f'{x},{y}' for x,y in pts)}' "
                f"fill='none' stroke='#444' stroke-width='1.2' />"
            )

        # ---- AXIS
        for angle in angles:
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)

            svg.append(
                f"<line x1='{center}' y1='{center}' "
                f"x2='{x}' y2='{y}' "
                f"stroke='#555' stroke-width='1' />"
            )

        # ---- LABELS
        for label, angle in zip(labels, angles):
            x = center + (radius + 20) * math.cos(angle)
            y = center + (radius + 20) * math.sin(angle)

            svg.append(
                f"<text x='{x}' y='{y}' font-size='12' text-anchor='middle'>{label}</text>"
            )

        # ---- DATA
        def polygon(points, color):
            return f"<polygon points='{' '.join(f'{x},{y}' for x,y in points)}' fill='{color}' fill-opacity='0.4' stroke='{color}' stroke-width='2'/>"

        pts_a = get_points(values_a)
        pts_b = get_points(values_b)

        svg.append(polygon(pts_a, "#4A7DFF"))
        svg.append(polygon(pts_b, "#4CAF6A"))

        return f"<svg width='{size}' height='{size}'>{''.join(svg)}</svg>"

    values_a = [row_a[m] for m in metrics if m in row_a]
    values_b = [row_b[m] for m in metrics if m in row_b]

    # ----------------------------
    # LAYOUT
    # ----------------------------
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<h2>Pókháló – fix 0–100 skála</h2>", unsafe_allow_html=True)
    st.markdown(radar_svg(values_a, values_b, metrics), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------
    # CONCLUSION (simple)
    # ----------------------------
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h2>Konklúzió</h2>", unsafe_allow_html=True)
    st.markdown("A két játékos profilja eltérő, nincs egyértelmű fölény.", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
