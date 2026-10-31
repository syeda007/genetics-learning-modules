"""
Web Application: Streamlit Genetics Research System v5.0
Visual-first interactive genetics laboratory (Streamlit Community Cloud).
"""
import sys
import os
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from scipy import stats

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from genetics_engine.allele import TALL_ALLELE, DWARF_ALLELE, LOCUS_A_DOM, LOCUS_A_REC, LOCUS_B_DOM, LOCUS_B_REC
from genetics_engine.genotype import MultiLocusGenotype
from genetics_engine.models import MENDELIAN_COMPLETE_DOMINANCE, DIHYBRID_INDEPENDENT_ASSORTMENT
from genetics_engine.crosses import execute_cross
from biostatistics.chi_square import calculate_chi_square
from biostatistics.ratios import parse_ratio_string
from simulations.population import simulate_offspring_population
from ml.deterministic_evaluator import evaluate_student_prediction
from ml.error_classifier import get_error_classifier
from content.scientific_text import MENDELIAN_BACKGROUND

st.set_page_config(page_title="Genetics Lab", page_icon=os.path.join(BASE_DIR, "assets", "favicon.png"), layout="wide",
                   initial_sidebar_state="expanded")

# ── Palette ────────────────────────────────────────────────────────────────────
INDIGO, TEAL, AMBER, ROSE, GREEN, SKY, INK, MUTE = (
    "#4f46e5", "#0d9488", "#d97706", "#e11d48", "#059669", "#0284c7", "#0f172a", "#64748b")
PHENO_COLORS = [INDIGO, TEAL, AMBER, ROSE, SKY, GREEN]

NAV = [
    ("dash", "home", "Dashboard"),
    ("exp1", "sprout", "Monohybrid"),
    ("exp2", "dice", "Dihybrid"),
    ("exp3", "flask", "Test Cross"),
    ("exp4", "bars", "Chi-Square"),
    ("exp5", "trend", "Simulation"),
    ("exp6", "cpu", "AI Diagnostics"),
]
NAV_LABEL = {k: n for k, i, n in NAV}


ICONS = {
    "home": "<path d='M3 11l9-8 9 8M5 10v10h5v-6h4v6h5V10'/>",
    "sprout": "<path d='M12 22V11M12 11c0-4 3-6 7-6 0 4-3 6-7 6zM12 15c0-3-2-5-6-5 0 3 2 5 6 5z'/>",
    "dice": "<rect x='3' y='3' width='18' height='18' rx='4'/><circle cx='8.5' cy='8.5' r='1'/><circle cx='15.5' cy='8.5' r='1'/><circle cx='12' cy='12' r='1'/><circle cx='8.5' cy='15.5' r='1'/><circle cx='15.5' cy='15.5' r='1'/>",
    "flask": "<path d='M9 3h6M10 3v6L4 19a2 2 0 0 0 2 3h12a2 2 0 0 0 2-3l-6-10V3M7 15h10'/>",
    "bars": "<path d='M4 20V10M10 20V4M16 20v-8M22 20H2'/>",
    "trend": "<path d='M3 3v18h18M7 15l4-5 3 3 5-7'/>",
    "trend_down": "<path d='M3 6l6 6 4-4 7 7M20 10v5h-5'/>",
    "cpu": "<rect x='5' y='5' width='14' height='14' rx='2'/><rect x='9' y='9' width='6' height='6'/><path d='M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3'/>",
    "check_circle": "<circle cx='12' cy='12' r='9'/><path d='M8 12l3 3 5-6'/>",
    "x_circle": "<circle cx='12' cy='12' r='9'/><path d='M15 9l-6 6M9 9l6 6'/>",
    "alert": "<path d='M12 3l10 18H2zM12 10v5M12 18h.01'/>",
    "search": "<circle cx='11' cy='11' r='7'/><path d='M21 21l-5-5'/>",
    "target": "<circle cx='12' cy='12' r='9'/><circle cx='12' cy='12' r='5'/><circle cx='12' cy='12' r='1'/>",
    "users": "<path d='M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'/><circle cx='9' cy='7' r='4'/><path d='M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8'/>",
    "bolt": "<path d='M13 2L3 14h8l-1 8 10-12h-8z'/>",
    "link": "<path d='M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1'/>",
    "globe": "<circle cx='12' cy='12' r='9'/><path d='M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18'/>",
    "layers": "<path d='M12 2l10 5-10 5L2 7zM2 12l10 5 10-5M2 17l10 5 10-5'/>",
    "dna": "<path d='M7 3c0 6 10 6 10 12s-10 6-10 6M17 3c0 6-10 6-10 12s10 6 10 6M8 7h8M8 17h8'/>",
    "shield": "<path d='M12 3l8 3v6c0 5-4 8-8 9-4-1-8-4-8-9V6z'/>",
    "pencil": "<path d='M4 20l4-1 11-11-3-3L5 16zM14 6l3 3'/>",
    "pie": "<circle cx='12' cy='12' r='9'/><path d='M12 3v9h9'/>",
    "question": "<circle cx='12' cy='12' r='9'/><path d='M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 1-1 1.7M12 17h.01'/>",
}


def ico(name, color="currentColor", size=24):
    """Inline SVG line icon."""
    return (f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{color}' stroke-width='1.9' "
            f"stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle'>{ICONS[name]}</svg>")


# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600;8..60,700&display=swap');
:root { --ink:#0f172a; --mute:#64748b; --line:#e5e7ef; --navy:#0b1226; --accent:#4f46e5; --gold:#c8a24b; }
html, body, [class*="css"] { font-family:'Inter','Segoe UI',sans-serif; color:var(--ink); }
.stApp { background:#f5f6fa; }
.block-container { padding-top:2.2rem; padding-bottom:3rem; max-width:1280px; }
header[data-testid="stHeader"] { background:transparent; }
[data-testid="stToolbar"], [data-testid="stDeployButton"], #MainMenu, footer { display:none !important; }
h1,h2,h3 { font-family:'Source Serif 4', Georgia, serif; }

/* sidebar */
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0b1226,#111a3a); border-right:none; }
[data-testid="stSidebar"] * { color:#cbd5e1; }
[data-testid="stSidebar"] hr { border-color:#ffffff1a; }
[data-testid="stSidebar"] [role="radiogroup"] { gap:4px; }
[data-testid="stSidebar"] [data-testid="stRadioOption"] { padding:11px 14px; border-radius:12px; transition:.15s; width:100%; min-height:46px; }
[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child { display:none; }
[data-testid="stSidebar"] [data-testid="stRadioOption"]:hover { background:#ffffff0f; }
[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] { background:#ffffff1c; box-shadow:inset 3px 0 0 var(--gold); }
[data-testid="stSidebar"] [data-testid="stRadioOption"] p { font-size:15px; font-weight:500; color:#cbd5e1 !important; margin:0; }
[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] p { color:#fff !important; font-weight:700; }
[data-testid="stSidebar"] [data-testid="stRadioOption"] [data-testid="stMarkdownContainer"] p { display:flex; align-items:center; gap:12px; }
.hero h1, .ptitle h2, .brand .nm, .tile .t, .verdict .vt { font-family:'Source Serif 4', Georgia, serif !important; }
.brand { padding:6px 4px 18px; border-bottom:1px solid #ffffff1a; margin-bottom:16px; }
.brand .nm { font-family:'Source Serif 4',serif; font-size:22px; font-weight:700; color:#fff !important; margin-top:8px; letter-spacing:.2px; }
.brand .sb { font-size:10.5px; font-weight:700; letter-spacing:1.8px; color:var(--gold) !important; margin-top:2px; }
.sbfoot { display:flex; gap:8px; flex-wrap:wrap; }
.sbfoot span { font-size:11px; font-weight:600; border:1px solid #ffffff22; border-radius:99px; padding:4px 11px; display:inline-flex; align-items:center; gap:7px; }
.sbfoot i { width:7px; height:7px; border-radius:50%; background:#34d399; display:inline-block; }

/* hero */
.hero { position:relative; overflow:hidden; border-radius:20px; padding:40px 44px; color:#fff; margin-bottom:22px;
  background:radial-gradient(600px 260px at 90% 0%, #3b3fa8 0%, transparent 70%), linear-gradient(135deg,#0b1226,#16225a);
  box-shadow:0 24px 48px -28px rgba(11,18,38,.8); }
.hero .eyebrow { font-size:11px; font-weight:700; letter-spacing:2.4px; color:var(--gold); }
.hero h1 { font-size:42px; font-weight:700; margin:8px 0 6px; letter-spacing:-.5px; color:#fff; line-height:1.1; }
.hero p { margin:0; color:#aab4d6; font-size:15px; font-weight:400; }
.hero svg { position:absolute; right:30px; top:50%; transform:translateY(-50%); }
.hero .tags { margin-top:20px; display:flex; gap:8px; flex-wrap:wrap; }
.hero .tags span { font-size:12px; font-weight:600; border:1px solid #ffffff2e; color:#dbe2ff; border-radius:99px; padding:5px 13px; }

/* stat tiles */
.stat { background:#fff; border:1px solid var(--line); border-radius:16px; padding:18px 20px; display:flex; gap:14px; align-items:center;
  box-shadow:0 1px 2px rgba(15,23,42,.04); }
.stat .ico { width:46px; height:46px; border-radius:13px; display:grid; place-items:center; flex:none;
  background:color-mix(in srgb,var(--c) 11%,white); }
.stat .big { font-size:26px; font-weight:800; color:var(--ink); line-height:1.05; letter-spacing:-.4px; }
.stat .lbl { font-size:11px; font-weight:600; color:var(--mute); letter-spacing:.9px; text-transform:uppercase; margin-top:3px; }

/* page title */
.ptitle { margin-bottom:22px; padding-bottom:16px; border-bottom:1px solid var(--line); display:flex; align-items:center; gap:16px; }
.ptitle .badge { width:56px; height:56px; border-radius:16px; display:grid; place-items:center; flex:none;
  background:var(--c); box-shadow:0 10px 20px -10px var(--c); }
.ptitle .eb { font-size:11px; font-weight:700; letter-spacing:2px; color:var(--mute); }
.ptitle h2 { margin:2px 0 6px; font-size:32px; font-weight:700; color:var(--ink); letter-spacing:-.4px; line-height:1.1; }
.chip { display:inline-block; border-radius:99px; padding:3px 11px; font-size:11.5px; font-weight:600; margin-right:6px;
  background:#fff; color:#334155; border:1px solid var(--line); }
.chip::before { content:''; display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--c); margin-right:7px; }

/* panels & forms */
.shdr { font-size:11px; font-weight:700; color:var(--mute); letter-spacing:1.8px; text-transform:uppercase; margin:18px 0 10px;
  display:flex; align-items:center; gap:12px; }
.shdr::after { content:''; flex:1; height:1px; background:var(--line); }
[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
  background:#fff; border:1px solid var(--line) !important; border-radius:18px !important; box-shadow:0 1px 2px rgba(15,23,42,.04), 0 12px 28px -22px rgba(15,23,42,.35); }
[data-testid="stForm"] { padding:22px; }
[data-testid="stForm"] .shdr { margin-top:0; }
[data-testid="stExpander"] { background:#fff; border:1px solid var(--line); border-radius:14px; }
[data-testid="stPlotlyChart"] { background:#fff; border:1px solid var(--line); border-radius:16px; padding:8px; }
label p { font-weight:600 !important; font-size:13px !important; color:#334155 !important; }
[data-baseweb="input"], [data-baseweb="select"] > div { min-height:46px; border-radius:12px !important; background:#f8f9fc; }
[data-testid="stSegmentedControl"] button { min-height:44px; font-weight:700; }
.stButton > button, [data-testid="stFormSubmitButton"] > button { min-height:48px; border-radius:12px; font-weight:700; letter-spacing:.2px; }
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"] {
  background:linear-gradient(180deg,#4f46e5,#4338ca); color:#fff; border:none; box-shadow:0 10px 20px -12px #4338ca; }
.stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] > button:hover { filter:brightness(1.08); }
.stButton > button[kind="secondary"] { background:#fff; border:1px solid var(--line); color:var(--ink); }
.stButton > button[kind="secondary"]:hover { border-color:var(--accent); color:var(--accent); }

/* punnett */
.pun { display:grid; gap:8px; margin:4px 0 10px; background:#fff; border:1px solid var(--line); border-radius:18px; padding:16px; }
.pun .h { display:grid; place-items:center; font-weight:700; font-size:13px; color:#fff; border-radius:50%;
  width:38px; height:38px; margin:auto; background:var(--navy); }
.pun .h.r { background:#475569; }
.pun .cell { border-radius:14px; padding:10px 4px; text-align:center; font-weight:700; font-size:15px; letter-spacing:.3px;
  background:color-mix(in srgb,var(--c) 11%,white); border:1.5px solid color-mix(in srgb,var(--c) 45%,white);
  color:color-mix(in srgb,var(--c) 65%,black); transition:.15s; animation:pop .4s ease backwards; }
.pun .cell:hover { transform:translateY(-2px); box-shadow:0 10px 18px -12px var(--c); }
.pun.big .cell { font-size:12.5px; padding:7px 2px; }
@keyframes pop { from{opacity:0; transform:scale(.8)} to{opacity:1; transform:scale(1)} }
.pun .ic { background:#fff; border-radius:50%; width:50px; height:50px; margin:0 auto 4px; display:grid; place-items:center;
  box-shadow:0 0 0 1px color-mix(in srgb,var(--c) 25%,white); } .pun.big .ic { width:40px; height:40px; }
.legend { display:flex; flex-wrap:wrap; gap:8px; margin:2px 0 8px; }
.legend span { font-size:12px; font-weight:600; color:#334155; display:inline-flex; align-items:center; gap:7px;
  background:#fff; border:1px solid var(--line); border-radius:99px; padding:4px 12px; }
.legend i { width:10px; height:10px; border-radius:50%; display:inline-block; }
.plgrid { display:flex; flex-wrap:wrap; gap:4px; background:linear-gradient(#f4f8ff,#eef6e6 85%,#d9ecb8);
  border:1px solid var(--line); border-radius:16px; padding:14px; margin-bottom:12px; }
.plgrid .pl { animation:pop .4s ease backwards; } .plgrid .pl:hover { transform:scale(1.2); }

/* verdict */
.verdict { border-radius:16px; padding:18px 22px; display:flex; gap:18px; align-items:center; margin:2px 0 14px; background:#fff;
  border:1px solid var(--line); border-left:6px solid var(--c); box-shadow:0 12px 26px -20px var(--c); animation:slide .35s ease; }
@keyframes slide { from{opacity:0; transform:translateY(6px)} to{opacity:1; transform:none} }
.verdict .vi { width:50px; height:50px; border-radius:50%; display:grid; place-items:center; flex:none;
  background:color-mix(in srgb,var(--c) 12%,white); color:var(--c); }
.verdict .vt { font-family:'Source Serif 4',serif; font-weight:700; font-size:21px; color:var(--ink); }
.verdict .vd { font-size:13px; color:var(--mute); margin-top:2px; line-height:1.45; }
.v-ok { --c:#059669; } .v-bad { --c:#e11d48; } .v-warn { --c:#d97706; }

/* dashboard tiles */
.tile { padding:4px 2px 2px; }
.tile .row { display:flex; justify-content:space-between; align-items:flex-start; }
.tile .ib { width:48px; height:48px; border-radius:14px; display:grid; place-items:center; background:var(--c); box-shadow:0 10px 18px -10px var(--c); }
.tile .no { font-family:'Source Serif 4',serif; font-size:38px; font-weight:600; color:#e2e5ee; line-height:1; }
.tile .t { font-family:'Source Serif 4',serif; font-size:21px; font-weight:700; color:var(--ink); margin-top:14px; }
.tile .d { font-size:13px; color:var(--mute); margin:2px 0 10px; }

.idle { border:1.5px dashed #c5cbe0; border-radius:20px; min-height:380px; display:flex; flex-direction:column;
  align-items:center; justify-content:center; gap:12px; color:#94a3b8; font-weight:600; font-size:14px; background:#ffffffb0; }

@media (max-width: 1024px) {
  .block-container { padding:1.2rem 1rem 3rem; }
  .hero { padding:28px 24px; } .hero h1 { font-size:32px; } .hero svg { display:none; }
  .ptitle h2 { font-size:26px; }
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def style_fig(fig, h=320, legend=True):
    fig.update_layout(
        height=h, margin=dict(l=14, r=14, t=24, b=10), paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, sans-serif", color=INK, size=12),
        showlegend=legend, legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        colorway=PHENO_COLORS, hoverlabel=dict(font_family="Inter"))
    fig.update_xaxes(gridcolor="#eef0f6", zeroline=False, linecolor="#e5e7ef")
    fig.update_yaxes(gridcolor="#eef0f6", zeroline=False)
    return fig


def show(fig, key=None):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=key)


def title(icon, text, color, chips=()):
    ch = "".join(f"<span class='chip' style='--c:{c}'>{t}</span>" for t, c in chips)
    n = st.session_state.get("nav", "")
    eb = f"EXPERIMENT 0{n[-1]}" if n.startswith("exp") else ""
    st.markdown(f"<div class='ptitle' style='--c:{color}'><div class='badge'>{ico(icon, '#fff', 28)}</div>"
                f"<div><div class='eb'>{eb}</div><h2>{text}</h2><div>{ch}</div></div></div>", unsafe_allow_html=True)


def shdr(t):
    st.markdown(f"<div class='shdr'>{t}</div>", unsafe_allow_html=True)


def stat(big, label, color, icon):
    return (f"<div class='stat' style='--c:{color}'><div class='ico'>{ico(icon, color, 24)}</div>"
            f"<div><div class='big'>{big}</div><div class='lbl'>{label}</div></div></div>")


def verdict(kind, icon, head, detail=""):
    st.markdown(f"<div class='verdict v-{kind}'><div class='vi'>{ico(icon, 'currentColor', 26)}</div><div>"
                f"<div class='vt'>{head}</div><div class='vd'>{detail}</div></div></div>", unsafe_allow_html=True)


def short(ph):
    """Compact phenotype label: 'Yellow · Round' / 'Tall'."""
    hits = re.findall(r"e\.g\.,\s*([A-Za-z]+)", ph)
    return " · ".join(hits) if hits else ph


def emo(ph):
    return short(ph)


def plant_svg(ph, size=34, kind=None):
    """Inline SVG: tall/dwarf pea plant, or a round/wrinkled yellow/green seed."""
    low = (kind or ph).lower()
    if "yellow" in low or "green" in low or "round" in low or "wrinkled" in low:
        col = "#fbbf24" if "yellow" in low else "#4ade80"
        if "wrinkled" in low:
            body = (f"<path d='M20 5 Q28 7 32 14 Q36 22 31 29 Q25 36 17 33 Q8 30 7 21 Q7 11 20 5Z' fill='{col}' stroke='#0003' stroke-width='1.5'/>"
                    "<path d='M13 14 Q18 17 15 23 M24 12 Q27 18 23 24 M18 28 Q23 26 27 29' stroke='#0004' stroke-width='1.6' fill='none' stroke-linecap='round'/>")
        else:
            body = (f"<circle cx='20' cy='20' r='14' fill='{col}' stroke='#0003' stroke-width='1.5'/>"
                    "<ellipse cx='14' cy='14' rx='5' ry='3' fill='#fff' opacity='.55' transform='rotate(-35 14 14)'/>")
        return f"<svg width='{size}' height='{size}' viewBox='0 0 40 40'>{body}</svg>"
    tall = "tall" in low or "dominant" in low
    top = 9 if tall else 34
    flower = "#f472b6" if tall else "#c084fc"
    leaves = (f"<ellipse cx='12' cy='{top+14}' rx='7' ry='3.2' fill='#22c55e' transform='rotate(-30 12 {top+14})'/>"
              f"<ellipse cx='28' cy='{top+22 if tall else top+12}' rx='7' ry='3.2' fill='#16a34a' transform='rotate(30 28 {top+22 if tall else top+12})'/>")
    if tall:
        leaves += "<ellipse cx='12' cy='42' rx='6' ry='3' fill='#16a34a' transform='rotate(-30 12 42)'/>"
    body = (f"<path d='M20 58 L20 {top}' stroke='#15803d' stroke-width='3.5' stroke-linecap='round'/>{leaves}"
            f"<circle cx='20' cy='{top}' r='6' fill='{flower}'/><circle cx='20' cy='{top}' r='2.4' fill='#fde047'/>")
    return f"<svg width='{size*0.7:.0f}' height='{size}' viewBox='0 0 40 60'>{body}</svg>"


def donut(labels, values, colors, center, h=280):
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=.62, marker=dict(colors=colors, line=dict(color="#fff", width=3)),
                           textinfo="percent", textfont=dict(size=13, color="#fff"), sort=False,
                           hovertemplate="%{label}<br>%{percent}<extra></extra>"))
    fig.add_annotation(text=center, showarrow=False, font=dict(size=18, weight=800, color=INK))
    return style_fig(fig, h, legend=True)


def punnett_html(cr, colors, big=False):
    ps = cr.punnett_square
    n = len(ps.col_gametes)
    cols = f"46px repeat({n}, 1fr)"
    html = [f"<div class='pun {'big' if big else ''}' style='grid-template-columns:{cols}'><div></div>"]
    html += [f"<div class='h c'>{g}</div>" for g, _ in ps.col_gametes]
    for (rg, _), row in zip(ps.row_gametes, ps.grid):
        html.append(f"<div class='h r'>{rg}</div>")
        for i, c in enumerate(row):
            col = colors[c.zygote_phenotype]
            html.append(f"<div class='cell' style='--c:{col};animation-delay:{i*25}ms' "
                        f"title='{short(c.zygote_phenotype)} · p={c.probability:.3f}'>"
                        f"<div class='ic'>{plant_svg(c.zygote_phenotype, 30 if big else 40)}</div>{c.zygote_genotype}</div>")
    html.append("</div>")
    return "".join(html)


def pheno_colors(cr):
    return {p: PHENO_COLORS[i % len(PHENO_COLORS)] for i, p in enumerate(sorted(cr.phenotype_frequencies))}


def legend_html(colors):
    return "<div class='legend'>" + "".join(
        f"<span><i style='background:{c}'></i>{plant_svg(p, 22)} {short(p)}</span>" for p, c in colors.items()) + "</div>"


def ratio_compare(student, expected, h=240):
    s, e = parse_ratio_string(student or ""), parse_ratio_string(expected or "")
    if not s or not e or len(s) != len(e):
        return None
    x = [f"Class {i+1}" for i in range(len(s))]
    fig = go.Figure([go.Bar(name="Your hypothesis", x=x, y=s, marker_color=AMBER, marker_cornerradius=8),
                     go.Bar(name="Theory", x=x, y=e, marker_color=INDIGO, marker_cornerradius=8)])
    fig.update_layout(barmode="group", yaxis_tickformat=".0%")
    return style_fig(fig, h)


def cross_panel(cr, pred_ratio, big=False):
    rep = evaluate_student_prediction(cr, pred_ratio, target_attribute="phenotype")
    fb = re.sub(r"^(CORRECT|DISCREPANCY)[^:]{0,40}:\s*", "", rep.scientific_feedback)
    if rep.is_correct:
        verdict("ok", "target", "Correct", fb)
    else:
        verdict("bad", "x_circle", "Not quite", fb)
        cmp_fig = ratio_compare(pred_ratio, rep.expected_ratio)
        if cmp_fig:
            show(cmp_fig, None)

    colors = pheno_colors(cr)
    shdr("PUNNETT SQUARE")
    st.markdown(legend_html(colors) + punnett_html(cr, colors, big), unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        shdr("PHENOTYPES")
        ph = cr.phenotype_frequencies
        show(donut([emo(k) for k in ph], list(ph.values()), [colors[k] for k in ph], cr.phenotype_ratios), None)
    with c2:
        shdr("GENOTYPES")
        gf = dict(sorted(cr.genotype_frequencies.items(), key=lambda kv: -kv[1]))
        fig = go.Figure(go.Bar(x=list(gf.values()), y=list(gf.keys()), orientation="h", marker_color=INDIGO,
                               marker_cornerradius=6, text=[f"{v:.1%}" for v in gf.values()], textposition="outside"))
        fig.update_layout(yaxis=dict(autorange="reversed"), xaxis_tickformat=".0%")
        show(style_fig(fig, 280, legend=False), None)

def idle():
    st.markdown(f"<div class='idle'>{ico('dna', '#a5b4fc', 64)}<div>Press Enter to run</div></div>", unsafe_allow_html=True)


def go_to(key):
    st.session_state.nav = key


# ── Sidebar ────────────────────────────────────────────────────────────────────
if "nav" not in st.session_state:
    st.session_state.nav = "dash"

with st.sidebar:
    st.markdown(f"<div class='brand'>{ico('dna', '#c8a24b', 34)}<div class='nm'>Genetics Lab</div>"
                "<div class='sb'>MODULE 01 · MENDELIAN</div></div>", unsafe_allow_html=True)
    st.radio("nav", [k for k, _, _ in NAV], format_func=lambda k: NAV_LABEL[k], key="nav", label_visibility="collapsed")
    st.markdown("<div style='height:28px'></div><div class='sbfoot'><span><i></i>Engine online</span>"
                "<span>24/24 tests</span></div>", unsafe_allow_html=True)

page = st.session_state.nav

# Every experiment starts fresh: wipe all widget/sim state when the page changes.
if st.session_state.get("_last_page") != page:
    for k in [k for k in st.session_state if k not in ("nav", "_last_page")]:
        del st.session_state[k]
    st.session_state["_last_page"] = page
import urllib.parse as _up
_css = "".join(
    "[data-testid='stSidebar'] [role='radiogroup'] > :nth-child(%d) [data-testid='stMarkdownContainer'] p::before{content:'';display:inline-block;"
    "width:20px;height:20px;flex:none;background:url(\"data:image/svg+xml;utf8,%s\") no-repeat center/contain;}"
    % (i + 1, _up.quote(f"<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='#a5b4fc' "
                       f"stroke-width='1.9' stroke-linecap='round' stroke-linejoin='round'>{ICONS[ic]}</svg>"))
    for i, (_, ic, _) in enumerate(NAV))
st.markdown(f"<style>{_css}</style>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "dash":
    xs = np.linspace(0, 300, 120)
    w1 = " ".join(f"{x:.0f},{70 + 42*np.sin(x/24):.1f}" for x in xs)
    w2 = " ".join(f"{x:.0f},{70 - 42*np.sin(x/24):.1f}" for x in xs)
    rungs = "".join(f"<line x1='{x}' x2='{x}' y1='{70 + 42*np.sin(x/24):.1f}' y2='{70 - 42*np.sin(x/24):.1f}' "
                    f"stroke='#fff' stroke-opacity='.22' stroke-width='2'/>" for x in range(6, 300, 14))
    st.markdown(f"""<div class='hero'><svg width='310' height='140' viewBox='0 0 310 140'>{rungs}
        <polyline points='{w1}' fill='none' stroke='#c8a24b' stroke-width='3' stroke-linecap='round'/>
        <polyline points='{w2}' fill='none' stroke='#e0e7ff' stroke-width='3' stroke-linecap='round'/></svg>
        <div class='eyebrow'>MODULE 01 · MENDELIAN GENETICS</div>
        <h1>Genetics Laboratory</h1><p>Cross, count, test and simulate inheritance.</p>
        <div class='tags'><span>6 experiments</span><span>Offline</span><span>Tablet ready</span></div></div>""", unsafe_allow_html=True)

    s = st.columns(4)
    for col, (b, l, c, i) in zip(s, [("6", "Experiments", INDIGO, "flask"), ("100%", "Deterministic", TEAL, "shield"),
                                     ("<2 ms", "Offline AI", AMBER, "bolt"), ("24/24", "Tests passing", GREEN, "check_circle")]):
        col.markdown(stat(b, l, c, i), unsafe_allow_html=True)
    st.write("")

    tiles = [("exp1", "sprout", "01", "Monohybrid Cross", "Single-locus segregation", INDIGO),
             ("exp2", "dice", "02", "Dihybrid Cross", "Independent assortment", TEAL),
             ("exp3", "flask", "03", "Test Cross", "Zygosity discrimination", AMBER),
             ("exp4", "bars", "04", "Chi-Square", "Goodness of fit", ROSE),
             ("exp5", "trend", "05", "Simulation", "Sampling variation", SKY),
             ("exp6", "cpu", "06", "AI Diagnostics", "Offline error classifier", GREEN)]
    shdr("EXPERIMENTS")
    for row in (tiles[:3], tiles[3:]):
        cols = st.columns(3)
        for col, (k, e, n, t, d, c) in zip(cols, row):
            with col.container(border=True):
                st.markdown(f"<div class='tile' style='--c:{c}'><div class='row'><div class='ib'>{ico(e, '#fff', 24)}</div>"
                            f"<div class='no'>{n}</div></div><div class='t'>{t}</div><div class='d'>{d}</div></div>",
                            unsafe_allow_html=True)
                st.button("Open", key=f"go_{k}", on_click=go_to, args=(k,), use_container_width=True)
        st.write("")

    l, r = st.columns(2)
    with l:
        shdr("MENDEL'S F2 · LIVE")
        a = {'T': TALL_ALLELE, 't': DWARF_ALLELE}
        cr = execute_cross(MultiLocusGenotype.from_str("Tt", a), MultiLocusGenotype.from_str("Tt", a),
                           MENDELIAN_COMPLETE_DOMINANCE, a)
        colors = pheno_colors(cr)
        st.markdown(punnett_html(cr, colors), unsafe_allow_html=True)
    with r:
        shdr("WHAT 9:3:3:1 LOOKS LIKE")
        fig = go.Figure(go.Treemap(
            labels=["Round Yellow", "Round Green", "Wrinkled Yellow", "Wrinkled Green"],
            parents=[""] * 4, values=[9, 3, 3, 1],
            marker=dict(colors=[AMBER, GREEN, "#fbbf24", "#34d399"], line=dict(width=3, color="#fff")),
            textinfo="label+value", textfont=dict(size=14, color="#fff")))
        show(style_fig(fig, 240, legend=False))

    shdr("COMING NEXT")
    nx = st.columns(4)
    for col, (n, t, e) in zip(nx, [("02", "Extensions", "layers"), ("03", "Linkage", "link"),
                                   ("04", "Populations", "globe"), ("05", "Quantitative", "trend")]):
        col.markdown(f"<div class='stat' style='--c:#94a3b8;opacity:.8'><div class='ico'>{ico(e, '#64748b', 24)}</div>"
                     f"<div><div class='big' style='font-size:17px'>{t}</div><div class='lbl'>Module {n}</div></div></div>",
                     unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# EXP 01
# ══════════════════════════════════════════════════════════════════════════════
elif page == "exp1":
    title("sprout", "Monohybrid Cross", INDIGO, [("1 locus", INDIGO), ("Complete dominance", GREEN)])
    left, right = st.columns([1, 1.7], gap="large")
    allele_map = {'T': TALL_ALLELE, 't': DWARF_ALLELE}
    with left:
        with st.form("f_exp1"):
            shdr("PARENTS")
            g1 = st.segmented_control("Parent 1 (female)", ["TT", "Tt", "tt"], default="Tt") or "Tt"
            g2 = st.segmented_control("Parent 2 (male)", ["TT", "Tt", "tt"], default="Tt") or "Tt"
            pred = st.text_input("Your ratio guess", "", placeholder="e.g. 3:1")
            if st.form_submit_button("Run cross", type="primary", use_container_width=True):
                st.session_state.r1 = (g1, g2, pred)
        with st.expander("Theory"):
            st.write(MENDELIAN_BACKGROUND["exp01_scientific_basis"])
    r = st.session_state.get("r1")
    with right:
        if not r:
            idle()
        elif not r[2].strip():
            verdict("warn", "pencil", "Type your ratio guess first")
        else:
            cr = execute_cross(MultiLocusGenotype.from_str(r[0], allele_map), MultiLocusGenotype.from_str(r[1], allele_map),
                               MENDELIAN_COMPLETE_DOMINANCE, allele_map)
            cross_panel(cr, r[2])

# ══════════════════════════════════════════════════════════════════════════════
# EXP 02
# ══════════════════════════════════════════════════════════════════════════════
elif page == "exp2":
    title("dice", "Dihybrid Cross", TEAL, [("2 loci", TEAL), ("Independent assortment", INDIGO)])
    left, right = st.columns([1, 2], gap="large")
    di_map = {'A': LOCUS_A_DOM, 'a': LOCUS_A_REC, 'B': LOCUS_B_DOM, 'b': LOCUS_B_REC}
    choices = ["AaBb", "AABB", "AABb", "AAbb", "AaBB", "Aabb", "aaBB", "aaBb", "aabb"]
    with left:
        with st.form("f_exp2"):
            shdr("PARENTS")
            g1 = st.selectbox("Parent 1 (female)", choices, 0)
            g2 = st.selectbox("Parent 2 (male)", choices, 0)
            pred = st.text_input("Your ratio guess", "", placeholder="e.g. 9:3:3:1")
            if st.form_submit_button("Run cross", type="primary", use_container_width=True):
                st.session_state.r2 = (g1, g2, pred)
        with st.expander("Theory"):
            st.write(MENDELIAN_BACKGROUND["exp02_scientific_basis"])
    r = st.session_state.get("r2")
    with right:
        if not r:
            idle()
        elif not r[2].strip():
            verdict("warn", "pencil", "Type your ratio guess first")
        else:
            cr = execute_cross(MultiLocusGenotype.from_str(r[0], di_map), MultiLocusGenotype.from_str(r[1], di_map),
                               DIHYBRID_INDEPENDENT_ASSORTMENT, di_map)
            cross_panel(cr, r[2], big=True)

# ══════════════════════════════════════════════════════════════════════════════
# EXP 03
# ══════════════════════════════════════════════════════════════════════════════
elif page == "exp3":
    title("flask", "Test Cross", AMBER, [("Is it AA or Aa?", AMBER)])
    left, right = st.columns([1, 2], gap="large")
    with left:
        with st.form("f_exp3"):
            shdr("MYSTERY PLANT × aa")
            truth = st.segmented_control("Hidden genotype (truth)", ["AA", "Aa"], default="Aa") or "Aa"
            n = st.slider("Offspring (N)", 5, 200, 40, 5)
            if st.form_submit_button("Run test cross", type="primary", use_container_width=True):
                prev = st.session_state.get("r3")
                st.session_state.r3 = (truth, n, (prev[2] + 1) if prev else 1)
    r = st.session_state.get("r3")
    with right:
        if not r:
            idle()
            st.stop()
        truth, n, seed = r
        rng = np.random.default_rng(seed)
        rec = 0 if truth == "AA" else int(rng.binomial(n, 0.5))
        dom = n - rec
        order = np.concatenate([np.zeros(dom), np.ones(rec)])
        rng.shuffle(order)
        if rec > 0:
            verdict("ok", "dna", "Heterozygous (Aa)", f"{rec} recessive offspring prove a hidden a allele.")
        else:
            p = 0.5 ** n
            verdict("warn", "question", f"Probably AA — P(Aa gives 0 aa) = {p:.2e}")

        tall_svg, dwarf_svg = plant_svg("tall", 46), plant_svg("dwarf", 46)
        cells = "".join(f"<div class='pl' style='animation-delay:{i*12}ms'>{dwarf_svg if o else tall_svg}</div>"
                        for i, o in enumerate(order))
        shdr(f"OFFSPRING &nbsp; {plant_svg('tall', 22)} dominant &nbsp; {plant_svg('dwarf', 22)} recessive")
        st.markdown(f"<div class='plgrid'>{cells}</div>", unsafe_allow_html=True)

        m = st.columns(3)
        m[0].markdown(stat(dom, "Dominant", GREEN, "sprout"), unsafe_allow_html=True)
        m[1].markdown(stat(rec, "Recessive", ROSE, "sprout"), unsafe_allow_html=True)
        m[2].markdown(stat(f"{rec/n:.0%}", "aa share", AMBER, "pie"), unsafe_allow_html=True)

        shdr("CONFIDENCE GROWS WITH N")
        ns = np.arange(1, 31)
        fig = go.Figure(go.Scatter(x=ns, y=1 - 0.5 ** ns, mode="lines", fill="tozeroy", line=dict(color=INDIGO, width=3),
                                   fillcolor="rgba(99,102,241,.15)", name="Confidence of AA"))
        if truth == "AA":
            k = min(n, 30)
            fig.add_trace(go.Scatter(x=[k], y=[1 - 0.5 ** k], mode="markers", marker=dict(size=14, color=AMBER, line=dict(color="#fff", width=2)),
                                     name="Your N"))
        fig.update_layout(yaxis_tickformat=".0%", xaxis_title="Offspring with no recessive")
        show(style_fig(fig, 220))

# ══════════════════════════════════════════════════════════════════════════════
# EXP 04
# ══════════════════════════════════════════════════════════════════════════════
elif page == "exp4":
    title("bars", "Chi-Square Test", ROSE, [("Goodness of fit", ROSE)])
    left, right = st.columns([1, 2], gap="large")
    presets = {"Mendel · Monohybrid": ("3:1", "556, 184"),
               "Mendel · Dihybrid": ("9:3:3:1", "315, 108, 101, 32"),
               "Linked genes (deviation)": ("1:1:1:1", "450, 48, 52, 450")}
    with left:
        shdr("DATA")
        pk = st.selectbox("Preset", list(presets))
        d_ratio, d_counts = presets[pk]
        with st.form("f_exp4"):
            ratio_in = st.text_input("Expected ratio", d_ratio, key=f"r_{pk}")
            counts_in = st.text_input("Observed counts", d_counts, key=f"c_{pk}")
            alpha = st.segmented_control("α", [0.10, 0.05, 0.01], default=0.05) or 0.05
            if st.form_submit_button("Calculate", type="primary", use_container_width=True):
                st.session_state.r4 = (pk, ratio_in, counts_in, alpha)
    r = st.session_state.get("r4")
    if not r or r[0] != pk:
        with right:
            idle()
        st.stop()
    _, ratio_in, counts_in, alpha = r

    props = parse_ratio_string(ratio_in)
    try:
        counts = [float(c) for c in counts_in.split(",") if c.strip()]
    except ValueError:
        counts = []
    with right:
        if not props or not counts or len(props) != len(counts):
            verdict("warn", "pencil", "Check inputs", "Ratio and counts need the same number of classes.")
        else:
            names = [f"Class {i+1}" for i in range(len(counts))]
            res = calculate_chi_square(dict(zip(names, counts)), dict(zip(names, props)), alpha=alpha)
            ok = not res.is_significant
            m = st.columns(3)
            m[0].markdown(stat(f"{res.chi_square_statistic:.2f}", "χ²", INDIGO, "bars"), unsafe_allow_html=True)
            m[1].markdown(stat(f"{res.p_value:.3g}", "p-value", GREEN if ok else ROSE, "target"), unsafe_allow_html=True)
            m[2].markdown(stat(res.degrees_of_freedom, "df", AMBER, "layers"), unsafe_allow_html=True)
            st.write("")

            if ok:
                verdict("ok", "check_circle", "Fits the ratio", f"p = {res.p_value:.3f} ≥ α = {alpha}")
            else:
                verdict("bad", "alert", "Rejects the ratio", f"p = {res.p_value:.2e} < α = {alpha}")

            cats = res.categories
            fig = go.Figure([
                go.Bar(name="Expected", x=[c.category for c in cats], y=[c.expected for c in cats],
                       marker_color="#c7d2fe", marker_cornerradius=8),
                go.Bar(name="Observed", x=[c.category for c in cats], y=[c.observed for c in cats],
                       marker_color=INDIGO, marker_cornerradius=8, text=[f"{c.observed:.0f}" for c in cats], textposition="outside")])
            fig.update_layout(barmode="group")
            c1, c2 = st.columns(2)
            with c1:
                shdr("OBSERVED vs EXPECTED")
                show(style_fig(fig, 300))
            with c2:
                shdr("WHO DRIVES χ²?")
                contrib = [c.chi_square_contribution for c in cats]
                fig = go.Figure(go.Pie(labels=[c.category for c in cats], values=contrib, hole=.6,
                                       marker=dict(colors=PHENO_COLORS, line=dict(color="#fff", width=3)), textinfo="percent"))
                show(style_fig(fig, 300))

            shdr("WHERE YOUR χ² LANDS")
            df_ = res.degrees_of_freedom
            crit = stats.chi2.ppf(1 - alpha, df_)
            hi = max(crit * 1.8, res.chi_square_statistic * 1.15, 8)
            x = np.linspace(0.001, hi, 400)
            y = stats.chi2.pdf(x, df_)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=INDIGO, width=3), name=f"χ² (df={df_})"))
            xr = x[x >= crit]
            fig.add_trace(go.Scatter(x=xr, y=stats.chi2.pdf(xr, df_), fill="tozeroy", mode="none",
                                     fillcolor="rgba(244,63,94,.28)", name=f"Reject zone (α={alpha})"))
            ymax = max(y[5:]) if df_ > 1 else min(max(y), 1.2)
            fig.add_vline(x=res.chi_square_statistic, line=dict(color=ROSE if not ok else GREEN, width=3, dash="dash"),
                          annotation_text=f"χ² = {res.chi_square_statistic:.2f}", annotation_position="top")
            fig.update_yaxes(range=[0, ymax * 1.25], showticklabels=False)
            show(style_fig(fig, 280))
            if res.warning_message:
                st.warning(res.warning_message)

# ══════════════════════════════════════════════════════════════════════════════
# EXP 05
# ══════════════════════════════════════════════════════════════════════════════
elif page == "exp5":
    title("trend", "Population Simulation", SKY, [("Sampling noise", SKY), ("Law of large numbers", INDIGO)])
    left, right = st.columns([1, 2], gap="large")
    with left:
        with st.form("f_exp5"):
            shdr("SETUP")
            model = st.segmented_control("Cross", ["Tt × Tt", "AaBb × AaBb"], default="Tt × Tt") or "Tt × Tt"
            N = st.select_slider("Sample size N", [20, 50, 100, 500, 1000, 5000], 100)
            seed = st.number_input("Seed", value=42, step=1)
            if st.form_submit_button("Run simulation", type="primary", use_container_width=True):
                st.session_state.r5 = (model, N, seed)
    r = st.session_state.get("r5")
    if not r:
        with right:
            idle()
        st.stop()
    model, N, seed = r

    if model == "Tt × Tt":
        am = {'T': TALL_ALLELE, 't': DWARF_ALLELE}
        cr = execute_cross(MultiLocusGenotype.from_str("Tt", am), MultiLocusGenotype.from_str("Tt", am),
                           MENDELIAN_COMPLETE_DOMINANCE, am)
    else:
        am = {'A': LOCUS_A_DOM, 'a': LOCUS_A_REC, 'B': LOCUS_B_DOM, 'b': LOCUS_B_REC}
        cr = execute_cross(MultiLocusGenotype.from_str("AaBb", am), MultiLocusGenotype.from_str("AaBb", am),
                           DIHYBRID_INDEPENDENT_ASSORTMENT, am)
    colors = pheno_colors(cr)
    sim = simulate_offspring_population(cr, sample_size=N, seed=int(seed))
    labels = [emo(i.category) for i in sim.items]
    cols_ = [colors[i.category] for i in sim.items]

    with right:
        m = st.columns(3)
        avg_dev = float(np.mean([i.percentage_deviation for i in sim.items]))
        pval = sim.chi_square_result.p_value
        m[0].markdown(stat(N, "Offspring", SKY, "users"), unsafe_allow_html=True)
        m[1].markdown(stat(f"{avg_dev:.1f}%", "Avg deviation", AMBER, "trend_down"), unsafe_allow_html=True)
        m[2].markdown(stat(f"{pval:.2f}", "p-value", GREEN if pval >= .05 else ROSE, "target"), unsafe_allow_html=True)
        st.write("")

        c1, c2 = st.columns(2)
        with c1:
            shdr("EXPECTED vs SIMULATED")
            fig = go.Figure([
                go.Bar(name="Expected", x=labels, y=[i.expected_count for i in sim.items], marker_color="#c7d2fe", marker_cornerradius=8),
                go.Bar(name="Simulated", x=labels, y=[i.simulated_count for i in sim.items], marker_color=cols_, marker_cornerradius=8,
                       text=[i.simulated_count for i in sim.items], textposition="outside")])
            fig.update_layout(barmode="group")
            show(style_fig(fig, 300))
        with c2:
            shdr("COMPOSITION")
            show(donut(labels, [i.simulated_count for i in sim.items], cols_, f"N={N}", 300))

        shdr("CONVERGENCE · BIGGER N → CLOSER TO THEORY")
        ns = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
        devs = [np.mean([i.percentage_deviation for i in simulate_offspring_population(cr, n, seed=int(seed)).items]) for n in ns]
        fig = go.Figure(go.Scatter(x=ns, y=devs, mode="lines+markers", line=dict(color=INDIGO, width=3, shape="spline"),
                                   marker=dict(size=10, color=INDIGO, line=dict(color="#fff", width=2)), fill="tozeroy",
                                   fillcolor="rgba(99,102,241,.12)", name="Avg deviation %"))
        fig.add_trace(go.Scatter(x=[N], y=[avg_dev], mode="markers", name="You are here",
                                 marker=dict(size=18, color=AMBER, symbol="star", line=dict(color="#fff", width=2))))
        fig.update_xaxes(type="log", title="Sample size")
        fig.update_yaxes(title="Deviation %")
        show(style_fig(fig, 270))

        shdr("500 REPEATED EXPERIMENTS")
        first = sim.items[0]
        draws = np.random.default_rng(int(seed)).binomial(N, first.theoretical_prob, 500) / N
        fig = go.Figure(go.Histogram(x=draws, nbinsx=30, marker=dict(color=SKY, line=dict(color="#fff", width=1)), opacity=.9))
        fig.add_vline(x=first.theoretical_prob, line=dict(color=ROSE, width=3, dash="dash"),
                      annotation_text="theory", annotation_position="top")
        fig.add_vline(x=first.simulated_count / N, line=dict(color=AMBER, width=3), annotation_text="yours", annotation_position="bottom")
        fig.update_xaxes(tickformat=".0%", title=f"Share of “{labels[0]}”")
        show(style_fig(fig, 250, legend=False))

# ══════════════════════════════════════════════════════════════════════════════
# EXP 06
# ══════════════════════════════════════════════════════════════════════════════
elif page == "exp6":
    title("cpu", "AI Error Diagnostics", GREEN, [("Offline decision tree", GREEN), ("100% local", INDIGO)])
    clf = get_error_classifier()
    left, right = st.columns([1, 2], gap="large")
    with left:
        with st.form("f_exp6"):
            shdr("SCENARIO")
            mode = st.selectbox("Cross", ["Tt × tt (test cross)", "Tt × Tt (monohybrid)", "AaBb × AaBb (dihybrid)"], 1)
            student = st.text_input("Student ratio", "", placeholder="e.g. 1:2:1")
            if st.form_submit_button("Diagnose", type="primary", use_container_width=True):
                st.session_state.r6 = (mode, student)
    r = st.session_state.get("r6")
    if not r:
        with right:
            idle()
        st.stop()
    mode, student = r
    if not student.strip():
        with right:
            verdict("warn", "pencil", "Type a ratio first")
        st.stop()

    loci = 2 if "dihybrid" in mode else 1
    exp_p = "9:3:3:1" if loci == 2 else ("1:1" if "test" in mode else "3:1")
    exp_g = "1:2:1:2:4:2:1:2:1" if loci == 2 else ("1:1" if "test" in mode else "1:2:1")
    det = clf.predict_detailed(loci, exp_p, exp_g, student)
    cat, conf = det["predicted_category"], det["class_probability"]

    with right:
        if cat == "CORRECT_PREDICTION":
            verdict("ok", "target", "Correct", "Matches theory.")
        elif cat == "CONFUSING_GENOTYPE_WITH_PHENOTYPE_RATIO":
            verdict("warn", "search", "Genotype ≠ phenotype", "Observable traits mask the gene pairs.")
        else:
            verdict("bad", "search", cat.replace("_", " ").title(), "Systematic deviation from Mendelian expectation.")

        c1, c2 = st.columns([1, 1.3])
        with c1:
            shdr("CONFIDENCE")
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=conf * 100, number=dict(suffix="%", font=dict(size=34, weight=800)),
                gauge=dict(axis=dict(range=[0, 100], tickwidth=0), bar=dict(color=GREEN if conf > .8 else AMBER, thickness=.3),
                           bgcolor="#eef0f6", borderwidth=0,
                           steps=[dict(range=[0, 50], color="#fee2e2"), dict(range=[50, 80], color="#fef3c7"),
                                  dict(range=[80, 100], color="#d1fae5")])))
            show(style_fig(fig, 250, legend=False))
        with c2:
            shdr("CLASS PROBABILITIES")
            pr = sorted(det["all_probabilities"].items(), key=lambda kv: kv[1])[-6:]
            fig = go.Figure(go.Bar(x=[p for _, p in pr], y=[k.replace("_", " ").title()[:34] for k, _ in pr], orientation="h",
                                   marker_color=[GREEN if k == cat else "#c7d2fe" for k, _ in pr], marker_cornerradius=6,
                                   text=[f"{p:.0%}" for _, p in pr], textposition="outside"))
            fig.update_xaxes(range=[0, 1.15], tickformat=".0%")
            fig.update_yaxes(automargin=True)
            show(style_fig(fig, 250, legend=False))

        fig = ratio_compare(student, exp_p)
        if fig:
            shdr("YOU vs THEORY")
            show(fig)
        if det["is_ambiguous"]:
            st.warning(det["ambiguity_note"])
        st.markdown(f"<div class='legend'><span><i style='background:{GREEN}'></i>{det['latency_ms']:.2f} ms</span>"
                    f"<span><i style='background:{INDIGO}'></i>No cloud</span></div>", unsafe_allow_html=True)
