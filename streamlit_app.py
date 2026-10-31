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
    "#6366f1", "#14b8a6", "#f59e0b", "#f43f5e", "#10b981", "#0ea5e9", "#1a1d2e", "#64748b")
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family:'Inter','Segoe UI',sans-serif; }
.stApp { background: radial-gradient(1200px 500px at 85% -10%, #e9e7ff 0%, transparent 60%),
                     radial-gradient(900px 500px at -10% 10%, #d9f7f1 0%, transparent 55%), #f8f9fc; }
.block-container { padding-top: 1.6rem; max-width: 1280px; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background:#fff; border-right:1px solid #e8eaf2; }

/* hero */
.hero { position:relative; overflow:hidden; border-radius:22px; padding:34px 38px; color:#fff;
  background: linear-gradient(120deg,#4338ca,#6366f1 45%,#14b8a6); background-size:200% 200%;
  animation: flow 12s ease infinite; box-shadow:0 18px 40px -18px rgba(79,70,229,.6); margin-bottom:22px; }
@keyframes flow { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
.hero h1 { font-size:34px; font-weight:900; margin:0; letter-spacing:-.5px; }
.hero p { margin:6px 0 0; opacity:.85; font-size:14px; font-weight:500; }
.hero svg { position:absolute; right:20px; top:-10px; opacity:.9; }
.helix-dot { animation: bob 3s ease-in-out infinite; }
@keyframes bob { 0%,100%{transform:translateY(0)} 50%{transform:translateY(6px)} }

/* stat tiles */
.stat { background:#fff; border:1.5px solid #e8eaf2; border-radius:16px; padding:16px 18px;
  transition:.2s; position:relative; overflow:hidden; }
.stat:hover { transform:translateY(-3px); box-shadow:0 12px 26px -14px rgba(99,102,241,.5); }
.stat .big { font-size:30px; font-weight:900; color:var(--c); line-height:1; }
.stat .lbl { font-size:11px; font-weight:700; color:#94a3b8; letter-spacing:1.2px; text-transform:uppercase; margin-top:6px; }
.stat .ico { position:absolute; right:12px; top:10px; opacity:.3; }

/* page title */
.ptitle { display:flex; align-items:center; gap:14px; margin-bottom:14px; }
.ptitle .badge { width:52px; height:52px; border-radius:16px; display:grid; place-items:center; font-size:26px;
  background:linear-gradient(135deg,var(--c),#fff0); background-color:color-mix(in srgb,var(--c) 18%,white);
  border:1.5px solid color-mix(in srgb,var(--c) 40%,white); }
.ptitle h2 { margin:0; font-size:26px; font-weight:900; color:#1a1d2e; letter-spacing:-.4px; }
.chip { display:inline-block; border-radius:99px; padding:3px 11px; font-size:11px; font-weight:700; margin-right:6px;
  background:color-mix(in srgb,var(--c) 12%,white); color:var(--c); border:1px solid color-mix(in srgb,var(--c) 30%,white); }

/* panel */
.shdr { font-size:11px; font-weight:800; color:#6366f1; letter-spacing:1.6px; text-transform:uppercase; margin:6px 0 8px; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius:16px !important; }

/* punnett */
.pun { display:grid; gap:6px; margin:4px 0 10px; }
.pun .h { display:grid; place-items:center; font-weight:800; font-size:13px; color:#fff; border-radius:50%;
  width:38px; height:38px; margin:auto; background:#475569; }
.pun .h.r { background:#ec4899; } .pun .h.c { background:#0ea5e9; }
.pun .cell { border-radius:12px; padding:12px 4px; text-align:center; font-weight:800; font-size:15px; color:#fff;
  transition:.15s; cursor:default; animation:pop .45s ease backwards; }
.pun .cell:hover { transform:scale(1.08); z-index:2; box-shadow:0 8px 18px -8px rgba(0,0,0,.4); }
.pun.big .cell { font-size:12.5px; padding:8px 2px; }
.pun .ic { background:rgba(255,255,255,.88); border-radius:50%; width:48px; height:48px; margin:0 auto 4px;
  display:grid; place-items:center; } .pun.big .ic { width:40px; height:40px; }
@keyframes pop { from{opacity:0; transform:scale(.6)} to{opacity:1; transform:scale(1)} }
.legend { display:flex; flex-wrap:wrap; gap:8px; margin:2px 0 6px; }
.legend span { font-size:12px; font-weight:700; color:#334155; display:inline-flex; align-items:center; gap:6px;
  background:#fff; border:1px solid #e8eaf2; border-radius:99px; padding:3px 11px; }
.legend i { width:11px; height:11px; border-radius:50%; display:inline-block; }

.plgrid { display:flex; flex-wrap:wrap; gap:4px; background:linear-gradient(#f0f9ff,#ecfccb 85%,#bef264);
  border:1.5px solid #e8eaf2; border-radius:16px; padding:12px; margin-bottom:12px; }
.plgrid .pl { animation:pop .4s ease backwards; } .plgrid .pl:hover { transform:scale(1.25); }
/* verdict */
.verdict { border-radius:16px; padding:16px 20px; display:flex; gap:16px; align-items:center; margin:10px 0;
  border:1.5px solid; animation:slide .4s ease; }
@keyframes slide { from{opacity:0; transform:translateY(8px)} to{opacity:1; transform:none} }
.verdict .vi { line-height:1; }
.verdict .vt { font-weight:900; font-size:16px; letter-spacing:.3px; }
.verdict .vd { font-size:12.5px; opacity:.85; margin-top:2px; }
.v-ok { background:#ecfdf5; border-color:#6ee7b7; color:#065f46; }
.v-bad { background:#fff1f2; border-color:#fda4af; color:#9f1239; }
.v-warn { background:#fffbeb; border-color:#fcd34d; color:#92400e; }

/* exp tiles */
.tile { background:#fff; border:1.5px solid #e8eaf2; border-radius:18px; padding:18px; height:100%;
  transition:.2s; border-top:5px solid var(--c); }
.tile:hover { transform:translateY(-4px); box-shadow:0 16px 30px -16px var(--c); }
.tile .e { font-size:34px; } .tile .n { font-size:11px; font-weight:800; color:var(--c); letter-spacing:1.4px; }
.tile .t { font-size:17px; font-weight:800; color:#1a1d2e; margin-top:2px; }

.stButton > button[kind="primary"] { background:linear-gradient(135deg,#6366f1,#4f46e5); border:none; color:#fff;
  border-radius:12px; font-weight:800; padding:.55rem 1.1rem; box-shadow:0 8px 18px -10px #4f46e5; }
.stButton > button[kind="primary"]:hover { transform:translateY(-1px); }
.stButton > button[kind="secondary"] { border-radius:12px; font-weight:700; }
[data-testid="stSidebar"] [role="radiogroup"] label { padding:7px 10px; border-radius:10px; transition:.15s; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background:#eef2ff; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def style_fig(fig, h=320, legend=True):
    fig.update_layout(
        height=h, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, sans-serif", color=INK, size=12),
        showlegend=legend, legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        colorway=PHENO_COLORS, hoverlabel=dict(font_family="Inter"))
    fig.update_xaxes(gridcolor="#eef0f6", zeroline=False)
    fig.update_yaxes(gridcolor="#eef0f6", zeroline=False)
    return fig


def show(fig, key=None):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=key)


def title(emoji, text, color, chips=()):
    ch = "".join(f"<span class='chip' style='--c:{c}'>{t}</span>" for t, c in chips)
    st.markdown(f"<div class='ptitle' style='--c:{color}'><div class='badge'>{ico(emoji, color, 28)}</div>"
                f"<div><h2>{text}</h2><div style='margin-top:4px'>{ch}</div></div></div>", unsafe_allow_html=True)


def shdr(t):
    st.markdown(f"<div class='shdr'>{t}</div>", unsafe_allow_html=True)


def stat(big, label, color, icon):
    return (f"<div class='stat' style='--c:{color}'><div class='ico'>{ico(icon, color, 34)}</div>"
            f"<div class='big'>{big}</div><div class='lbl'>{label}</div></div>")


def verdict(kind, icon, head, detail=""):
    st.markdown(f"<div class='verdict v-{kind}'><div class='vi'>{ico(icon, 'currentColor', 38)}</div><div>"
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
            html.append(f"<div class='cell' style='background:{col};animation-delay:{i*25}ms' "
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
    if rep.is_correct:
        verdict("ok", "target", "Correct", rep.scientific_feedback)
    else:
        verdict("bad", "x_circle", "Not quite", rep.scientific_feedback)
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

def go_to(key):
    st.session_state.nav = key


# ── Sidebar ────────────────────────────────────────────────────────────────────
if "nav" not in st.session_state:
    st.session_state.nav = "dash"

with st.sidebar:
    st.markdown("<div>"+ico("dna", "#6366f1", 40)+"</div>"
                "<div style='font-size:18px;font-weight:900;color:#1a1d2e;margin-top:4px'>Genetics Lab</div>"
                "<div style='font-size:11px;color:#6366f1;font-weight:700;letter-spacing:1px;margin-bottom:12px'>MODULE 01 · MENDELIAN</div>",
                unsafe_allow_html=True)
    st.radio("nav", [k for k, _, _ in NAV], format_func=lambda k: NAV_LABEL[k], key="nav", label_visibility="collapsed")
    st.markdown("---")
    st.markdown("<div class='legend'><span><i style='background:#10b981'></i>Engine online</span>"
                "<span><i style='background:#6366f1'></i>24/24 tests</span></div>", unsafe_allow_html=True)

page = st.session_state.nav
import urllib.parse as _up
_css = "".join(
    "[data-testid='stSidebar'] [role='radiogroup'] label:nth-of-type(%d) > div:last-child::before{content:'';display:inline-block;"
    "width:20px;height:20px;margin-right:10px;vertical-align:-4px;background:url(\"data:image/svg+xml;utf8,%s\") no-repeat center/contain;}"
    % (i + 1, _up.quote(f"<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='#6366f1' "
                       f"stroke-width='1.9' stroke-linecap='round' stroke-linejoin='round'>{ICONS[ic]}</svg>"))
    for i, (_, ic, _) in enumerate(NAV))
st.markdown(f"<style>{_css}</style>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "dash":
    helix = "".join(
        f"<circle class='helix-dot' cx='{20 + i*22}' cy='{60 + 38*np.sin(i/1.6):.1f}' r='7' fill='#fff' style='animation-delay:{i*.2}s'/>"
        f"<circle class='helix-dot' cx='{20 + i*22}' cy='{60 - 38*np.sin(i/1.6):.1f}' r='7' fill='#fde68a' style='animation-delay:{i*.2+.1}s'/>"
        f"<line x1='{20+i*22}' x2='{20+i*22}' y1='{60 + 38*np.sin(i/1.6):.1f}' y2='{60 - 38*np.sin(i/1.6):.1f}' stroke='#fff' stroke-opacity='.4' stroke-width='2'/>"
        for i in range(12))
    st.markdown(f"""<div class='hero'><svg width='290' height='130' viewBox='0 0 290 130'>{helix}</svg>
        <h1>Genetics Lab</h1><p>Cross · Count · Test · Simulate</p></div>""", unsafe_allow_html=True)

    s = st.columns(4)
    for col, (b, l, c, i) in zip(s, [("6", "Experiments", INDIGO, "flask"), ("100%", "Deterministic", TEAL, "shield"),
                                     ("<2ms", "Offline AI", AMBER, "bolt"), ("24/24", "Tests passing", GREEN, "check_circle")]):
        col.markdown(stat(b, l, c, i), unsafe_allow_html=True)
    st.write("")

    tiles = [("exp1", "sprout", "EXP 01", "Monohybrid", INDIGO), ("exp2", "dice", "EXP 02", "Dihybrid", TEAL),
             ("exp3", "flask", "EXP 03", "Test Cross", AMBER), ("exp4", "bars", "EXP 04", "Chi-Square", ROSE),
             ("exp5", "trend", "EXP 05", "Simulation", SKY), ("exp6", "cpu", "EXP 06", "AI Diagnostics", GREEN)]
    shdr("LAUNCH AN EXPERIMENT")
    for row in (tiles[:3], tiles[3:]):
        cols = st.columns(3)
        for col, (k, e, n, t, c) in zip(cols, row):
            with col:
                st.markdown(f"<div class='tile' style='--c:{c}'><div class='e'>{ico(e, c, 34)}</div>"
                            f"<div class='n'>{n}</div><div class='t'>{t}</div></div>", unsafe_allow_html=True)
                st.button("Open →", key=f"go_{k}", on_click=go_to, args=(k,), use_container_width=True)
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
        col.markdown(f"<div class='stat' style='--c:#94a3b8;opacity:.75'><div class='ico'>{ico(e, '#64748b', 34)}</div>"
                     f"<div class='big' style='font-size:20px'>{t}</div><div class='lbl'>Module {n}</div></div>",
                     unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# EXP 01
# ══════════════════════════════════════════════════════════════════════════════
elif page == "exp1":
    title("sprout", "Monohybrid Cross", INDIGO, [("1 locus", INDIGO), ("Complete dominance", GREEN)])
    left, right = st.columns([1, 1.7], gap="large")
    allele_map = {'T': TALL_ALLELE, 't': DWARF_ALLELE}
    with left:
        with st.container(border=True):
            shdr("PARENTS")
            g1 = st.segmented_control("Parent 1 (female)", ["TT", "Tt", "tt"], default="Tt", key="e1p1") or "Tt"
            g2 = st.segmented_control("Parent 2 (male)", ["TT", "Tt", "tt"], default="Tt", key="e1p2") or "Tt"
            pred = st.text_input("Your ratio guess", "3:1")
        with st.expander("Theory"):
            st.write(MENDELIAN_BACKGROUND["exp01_scientific_basis"])
    cr = execute_cross(MultiLocusGenotype.from_str(g1, allele_map), MultiLocusGenotype.from_str(g2, allele_map),
                       MENDELIAN_COMPLETE_DOMINANCE, allele_map)
    with right:
        cross_panel(cr, pred)

# ══════════════════════════════════════════════════════════════════════════════
# EXP 02
# ══════════════════════════════════════════════════════════════════════════════
elif page == "exp2":
    title("dice", "Dihybrid Cross", TEAL, [("2 loci", TEAL), ("Independent assortment", INDIGO)])
    left, right = st.columns([1, 2], gap="large")
    di_map = {'A': LOCUS_A_DOM, 'a': LOCUS_A_REC, 'B': LOCUS_B_DOM, 'b': LOCUS_B_REC}
    choices = ["AaBb", "AABB", "AABb", "AAbb", "AaBB", "Aabb", "aaBB", "aaBb", "aabb"]
    with left:
        with st.container(border=True):
            shdr("PARENTS")
            g1 = st.selectbox("Parent 1 (female)", choices, 0)
            g2 = st.selectbox("Parent 2 (male)", choices, 0)
            pred = st.text_input("Your ratio guess", "9:3:3:1")
        with st.expander("Theory"):
            st.write(MENDELIAN_BACKGROUND["exp02_scientific_basis"])
    cr = execute_cross(MultiLocusGenotype.from_str(g1, di_map), MultiLocusGenotype.from_str(g2, di_map),
                       DIHYBRID_INDEPENDENT_ASSORTMENT, di_map)
    with right:
        cross_panel(cr, pred, big=True)

# ══════════════════════════════════════════════════════════════════════════════
# EXP 03
# ══════════════════════════════════════════════════════════════════════════════
elif page == "exp3":
    title("flask", "Test Cross", AMBER, [("Is it AA or Aa?", AMBER)])
    left, right = st.columns([1, 2], gap="large")
    with left:
        with st.container(border=True):
            shdr("MYSTERY PLANT × aa")
            truth = st.segmented_control("Hidden genotype (truth)", ["AA", "Aa"], default="Aa", key="tc_truth") or "Aa"
            n = st.slider("Offspring (N)", 5, 200, 40, 5)
            if "tc_seed" not in st.session_state:
                st.session_state.tc_seed = 1
            st.button("Resample", type="primary", use_container_width=True,
                      on_click=lambda: st.session_state.update(tc_seed=st.session_state.tc_seed + 1))
    with right:
        rng = np.random.default_rng(st.session_state.tc_seed)
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
        shdr(f"OFFSPRING &nbsp; {plant_svg('tall', 22)} A_ tall &nbsp; {plant_svg('dwarf', 22)} aa dwarf")
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
        with st.container(border=True):
            shdr("DATA")
            pk = st.selectbox("Preset", list(presets))
            d_ratio, d_counts = presets[pk]
            ratio_in = st.text_input("Expected ratio", d_ratio, key=f"r_{pk}")
            counts_in = st.text_input("Observed counts", d_counts, key=f"c_{pk}")
            alpha = st.segmented_control("α", [0.10, 0.05, 0.01], default=0.05, key="alpha") or 0.05

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
            m[0].markdown(stat(f"{res.chi_square_statistic:.2f}", "χ² statistic", INDIGO, "bars"), unsafe_allow_html=True)
            m[1].markdown(stat(f"{res.p_value:.3g}", "p-value", GREEN if ok else ROSE, "target"), unsafe_allow_html=True)
            m[2].markdown(stat(res.degrees_of_freedom, "degrees of freedom", AMBER, "layers"), unsafe_allow_html=True)
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
        with st.container(border=True):
            shdr("SETUP")
            model = st.segmented_control("Cross", ["Tt × Tt", "AaBb × AaBb"], default="Tt × Tt", key="sim_model") or "Tt × Tt"
            N = st.select_slider("Sample size N", [20, 50, 100, 500, 1000, 5000], 100)
            seed = st.number_input("Seed", value=42, step=1)

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
        m[2].markdown(stat(f"{pval:.2f}", "χ² p-value", GREEN if pval >= .05 else ROSE, "target"), unsafe_allow_html=True)
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
        with st.container(border=True):
            shdr("SCENARIO")
            mode = st.selectbox("Cross", ["Tt × tt (test cross)", "Tt × Tt (monohybrid)", "AaBb × AaBb (dihybrid)"], 1)
            student = st.text_input("Student ratio", "1:2:1")
            st.caption("Try: 3:1 · 1:2:1 · 9:3:3:1 · 1:1")

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
            show(style_fig(fig, 250, legend=False))

        fig = ratio_compare(student, exp_p)
        if fig:
            shdr("YOU vs THEORY")
            show(fig)
        if det["is_ambiguous"]:
            st.warning(det["ambiguity_note"])
        st.markdown(f"<div class='legend'><span><i style='background:{GREEN}'></i>{det['latency_ms']:.2f} ms</span>"
                    f"<span><i style='background:{INDIGO}'></i>No cloud</span></div>", unsafe_allow_html=True)
