"""
app.py
======
Single-page executive dashboard for the EV Charging Scheduler.
iOS 26-style glassmorphism design with dark/light theme toggle.
"""

import streamlit as st
import numpy as np
import skfuzzy as fuzz
from fuzzy_engine import (
    get_optimal_charge,
    soc as soc_var,
    price as price_var,
    time as time_var,
    charge_power as cp_var,
)

# ───────────────────────────────────────────────
# Page Configuration
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="EV Charge Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ───────────────────────────────────────────────
# Session State
# ───────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

is_dark = st.session_state.theme == "dark"

# ───────────────────────────────────────────────
# Theme Palette
# ───────────────────────────────────────────────
if is_dark:
    BG       = "#050a15"
    BG2      = "#0c1222"
    GLASS    = "rgba(255,255,255,0.04)"
    GLASS_H  = "rgba(255,255,255,0.08)"
    GLASS_BR = "rgba(255,255,255,0.10)"
    TXT      = "#e8ecf4"
    TXT2     = "rgba(255,255,255,0.55)"
    TXT3     = "rgba(255,255,255,0.28)"
    ACC      = "#34d399"
    ACC2     = "#a78bfa"
    GRAD     = "linear-gradient(135deg, #34d399, #a78bfa)"
    ORB1     = "rgba(52,211,153,0.10)"
    ORB2     = "rgba(167,139,250,0.08)"
    ORB3     = "rgba(251,191,36,0.06)"
    RES_BG   = "rgba(255,255,255,0.03)"
    RES_BRD  = "rgba(52,211,153,0.15)"
    FT_BG    = "rgba(0,0,0,0.3)"
    INP_BG   = "rgba(255,255,255,0.06)"
    INP_BRD  = "rgba(255,255,255,0.10)"
    B_ECO    = ("rgba(52,211,153,0.12)", "#34d399", "rgba(52,211,153,0.25)")
    B_BAL    = ("rgba(251,191,36,0.12)", "#fbbf24", "rgba(251,191,36,0.25)")
    B_FAST   = ("rgba(248,113,113,0.12)", "#f87171", "rgba(248,113,113,0.25)")
    MPL      = dict(fig="#050a15", ax="#0c1222", txt="#ccc", lbl="#aaa",
                    tick="#777", edge="#1e293b", grid="#1a2236")
else:
    BG       = "#f0f4f8"
    BG2      = "#ffffff"
    GLASS    = "rgba(255,255,255,0.55)"
    GLASS_H  = "rgba(255,255,255,0.75)"
    GLASS_BR = "rgba(255,255,255,0.60)"
    TXT      = "#0f172a"
    TXT2     = "#475569"
    TXT3     = "#94a3b8"
    ACC      = "#059669"
    ACC2     = "#7c3aed"
    GRAD     = "linear-gradient(135deg, #059669, #7c3aed)"
    ORB1     = "rgba(5,150,105,0.12)"
    ORB2     = "rgba(124,58,237,0.10)"
    ORB3     = "rgba(245,158,11,0.08)"
    RES_BG   = "rgba(255,255,255,0.6)"
    RES_BRD  = "rgba(5,150,105,0.18)"
    FT_BG    = "rgba(255,255,255,0.5)"
    INP_BG   = "rgba(255,255,255,0.7)"
    INP_BRD  = "rgba(0,0,0,0.08)"
    B_ECO    = ("rgba(5,150,105,0.10)", "#059669", "rgba(5,150,105,0.22)")
    B_BAL    = ("rgba(217,119,6,0.10)", "#d97706", "rgba(217,119,6,0.22)")
    B_FAST   = ("rgba(220,38,38,0.10)", "#dc2626", "rgba(220,38,38,0.22)")
    MPL      = dict(fig="#f0f4f8", ax="#ffffff", txt="#334155", lbl="#475569",
                    tick="#64748b", edge="#e2e8f0", grid="#e2e8f0")

# ───────────────────────────────────────────────
# Global CSS — iOS 26 Glassmorphism
# ───────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Reset & Background ── */
html, body, .stApp {{
    background: {BG} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: {TXT} !important;
}}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stHeader"] {{
    background: transparent !important;
}}

/* ── Gradient Orbs (iOS 26 ambient light) ── */
.stApp::before {{
    content: '';
    position: fixed;
    top: -180px;
    right: -120px;
    width: 550px;
    height: 550px;
    background: radial-gradient(circle, {ORB1}, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    animation: orbFloat1 20s ease-in-out infinite;
}}
.stApp::after {{
    content: '';
    position: fixed;
    bottom: -200px;
    left: -150px;
    width: 650px;
    height: 650px;
    background: radial-gradient(circle, {ORB2}, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    animation: orbFloat2 25s ease-in-out infinite;
}}
@keyframes orbFloat1 {{
    0%, 100% {{ transform: translate(0, 0); }}
    50% {{ transform: translate(-40px, 60px); }}
}}
@keyframes orbFloat2 {{
    0%, 100% {{ transform: translate(0, 0); }}
    50% {{ transform: translate(50px, -40px); }}
}}

/* ── Hide Streamlit chrome ── */
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebar"],
#MainMenu, footer, header {{
    display: none !important;
}}

/* ── Glass Card (iOS 26) ── */
.glass {{
    background: {GLASS};
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border: 1px solid {GLASS_BR};
    border-radius: 22px;
    padding: 28px;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    z-index: 1;
}}
.glass:hover {{
    background: {GLASS_H};
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}}

/* ── Buttons ── */
.stButton > button {{
    background: {GLASS} !important;
    backdrop-filter: blur(20px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(160%) !important;
    border: 1px solid {GLASS_BR} !important;
    color: {TXT2} !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 10px 24px !important;
    border-radius: 14px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}
.stButton > button:hover {{
    background: {GLASS_H} !important;
    color: {TXT} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.1) !important;
}}
.stButton > button[kind="primary"] {{
    background: {GRAD} !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(52,211,153,0.25) !important;
    backdrop-filter: none !important;
}}
.stButton > button[kind="primary"]:hover {{
    opacity: 0.92 !important;
    box-shadow: 0 8px 30px rgba(52,211,153,0.35) !important;
}}

/* ── Sliders ── */
.stSlider > div > div > div {{ color: {TXT2} !important; }}
.stSlider [data-testid="stThumbValue"] {{ color: {TXT} !important; font-weight: 600 !important; }}
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"] {{ color: {TXT3} !important; }}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {{
    background: {INP_BG} !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid {INP_BRD} !important;
    color: {TXT} !important;
    border-radius: 14px !important;
    font-family: 'Inter', sans-serif !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: {ACC} !important;
    box-shadow: 0 0 0 2px rgba(52,211,153,0.15) !important;
}}
.stTextInput label, .stTextArea label {{
    color: {TXT2} !important;
    font-family: 'Inter', sans-serif !important;
}}

/* ── Form ── */
[data-testid="stForm"] {{
    background: {GLASS} !important;
    backdrop-filter: blur(24px) saturate(160%) !important;
    border: 1px solid {GLASS_BR} !important;
    border-radius: 22px !important;
    padding: 24px !important;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background: {GLASS} !important;
    backdrop-filter: blur(20px) saturate(160%) !important;
    border: 1px solid {GLASS_BR} !important;
    border-radius: 18px !important;
    overflow: hidden;
}}
.streamlit-expanderHeader {{
    color: {TXT2} !important;
    font-family: 'Inter', sans-serif !important;
}}

/* ── Metric Row ── */
.ev-metrics {{
    display: flex;
    gap: 14px;
    margin: 20px 0;
}}
.ev-metrics-tile {{
    flex: 1;
    background: {GLASS};
    backdrop-filter: blur(24px) saturate(160%);
    -webkit-backdrop-filter: blur(24px) saturate(160%);
    border: 1px solid {GLASS_BR};
    border-radius: 18px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s ease;
}}
.ev-metrics-tile:hover {{
    background: {GLASS_H};
    transform: translateY(-2px);
}}

/* ── Section Divider ── */
.ev-divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, {GLASS_BR}, transparent);
    margin: 60px auto;
    max-width: 300px;
}}

/* ── Responsive ── */
@media (max-width: 768px) {{
    .ev-metrics {{ flex-direction: column; }}
    .ev-stat-bar {{ flex-direction: column !important; }}
    .ev-hero-title {{ font-size: 2.4rem !important; }}
    .ev-result-val {{ font-size: 3.2rem !important; }}
}}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#   NAVBAR
# ═══════════════════════════════════════════════
nav_left, _, nav_right = st.columns([3, 6, 1])

nav_left.markdown(f"""
<div style="display:flex; align-items:center; gap:10px; padding:4px 0;">
    <span style="font-size:1.3rem;">⚡</span>
    <span style="font-size:1.1rem; font-weight:700; color:{TXT}; letter-spacing:-0.3px;">
        EV Charge
    </span>
</div>
""", unsafe_allow_html=True)

theme_icon = "☀️" if is_dark else "🌙"
if nav_right.button(theme_icon, key="theme_btn", use_container_width=True):
    st.session_state.theme = "light" if is_dark else "dark"
    st.rerun()

st.markdown(f"""
<div style="height:1px; background:linear-gradient(90deg, transparent, {GLASS_BR}, transparent);
            margin:8px 0 40px;"></div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#   SECTION: HERO
# ═══════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center; padding:60px 20px 50px; position:relative; z-index:1;">
    <h1 class="ev-hero-title" style="
        font-size:3.6rem; font-weight:900;
        background:{GRAD}; -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        margin:0; line-height:1.1; letter-spacing:-2px;
    ">EV Charge Optimizer</h1>
    <p style="
        color:{TXT3}; font-size:0.78rem; font-weight:500;
        text-transform:uppercase; letter-spacing:5px; margin-top:16px;
    ">Intelligent Charging · Optimization Platform</p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#   SECTION: FEATURES
# ═══════════════════════════════════════════════
features = [
    ("⚡", "Adaptive Scheduling",
     "Dynamic power allocation based on real-time grid conditions, battery state, and departure constraints."),
    ("📉", "Tariff Optimization",
     "Minimize electricity expenditure through intelligent time-of-use pricing and demand-response strategies."),
    ("🔋", "Battery Preservation",
     "SOC-aware charge profiles that protect long-term battery health while ensuring departure readiness."),
]
f_cols = st.columns(3)
for col, (icon, title, desc) in zip(f_cols, features):
    col.markdown(f"""
    <div class="glass" style="min-height:210px;">
        <div style="
            width:48px; height:48px; border-radius:14px;
            background:{GRAD}; display:flex; align-items:center;
            justify-content:center; font-size:1.4rem; margin-bottom:16px;
            box-shadow:0 4px 15px rgba(52,211,153,0.2);
        ">{icon}</div>
        <div style="font-size:1.05rem; font-weight:600; color:{TXT}; margin-bottom:10px;">
            {title}
        </div>
        <div style="font-size:0.84rem; color:{TXT2}; line-height:1.75;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Stats Bar ──
st.markdown('<div style="height:40px;"></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="ev-stat-bar" style="
    display:flex; gap:0;
    background:{GLASS};
    backdrop-filter:blur(28px) saturate(180%);
    -webkit-backdrop-filter:blur(28px) saturate(180%);
    border:1px solid {GLASS_BR};
    border-radius:22px;
    overflow:hidden;
    position:relative; z-index:1;
">
""", unsafe_allow_html=True)

stats = [("22 kW", "Max Power"), ("20", "Fuzzy Rules"),
         ("3", "Input Parameters"), ("<1s", "Inference")]
for j, (val, lbl) in enumerate(stats):
    sep = f"border-right:1px solid {GLASS_BR};" if j < 3 else ""
    st.markdown(f"""
    <div style="flex:1; text-align:center; padding:26px 16px; {sep}">
        <div style="font-size:1.7rem; font-weight:800;
                    background:{GRAD}; -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;">{val}</div>
        <div style="font-size:0.68rem; color:{TXT3};
                    text-transform:uppercase; letter-spacing:2px; margin-top:6px;">
            {lbl}
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# ── Divider ──
st.markdown('<div class="ev-divider"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#   SECTION: SCHEDULER
# ═══════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center; padding:0 0 36px; position:relative; z-index:1;">
    <h2 style="font-size:2rem; font-weight:700; color:{TXT}; margin:0 0 8px;">
        Charging Optimizer
    </h2>
    <div style="width:50px; height:3px; background:{GRAD};
                border-radius:2px; margin:0 auto;"></div>
</div>
""", unsafe_allow_html=True)

# Inputs inside glass container
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<p style="font-size:0.70rem; font-weight:600; text-transform:uppercase;
                letter-spacing:2px; color:{TXT3}; margin-bottom:0;">
        State of Charge</p>""", unsafe_allow_html=True)
    soc_input = st.slider("SOC", 0, 100, 35, 1, label_visibility="collapsed")

with col2:
    st.markdown(f"""<p style="font-size:0.70rem; font-weight:600; text-transform:uppercase;
                letter-spacing:2px; color:{TXT3}; margin-bottom:0;">
        Grid Tariff</p>""", unsafe_allow_html=True)
    price_input = st.slider("Price", 0, 50, 20, 1, label_visibility="collapsed")

with col3:
    st.markdown(f"""<p style="font-size:0.70rem; font-weight:600; text-transform:uppercase;
                letter-spacing:2px; color:{TXT3}; margin-bottom:0;">
        Time to Departure</p>""", unsafe_allow_html=True)
    time_input = st.slider("Time", 0, 24, 8, 1, label_visibility="collapsed")

# Compute
power = get_optimal_charge(soc_input, price_input, time_input)

if power <= 7.5:
    tier_text, badge = "ECO", B_ECO
elif power <= 15:
    tier_text, badge = "BALANCED", B_BAL
else:
    tier_text, badge = "RAPID", B_FAST

# Result display — glass card
st.markdown(f"""
<div style="
    background:{RES_BG};
    backdrop-filter:blur(32px) saturate(200%);
    -webkit-backdrop-filter:blur(32px) saturate(200%);
    border:1px solid {RES_BRD};
    border-radius:24px;
    padding:48px 24px;
    text-align:center;
    margin:24px 0;
    position:relative; z-index:1;
    box-shadow: 0 8px 40px rgba(0,0,0,0.08);
">
    <p style="font-size:0.70rem; font-weight:600; text-transform:uppercase;
              letter-spacing:3px; color:{TXT3}; margin-bottom:20px;">
        Recommended Power Output
    </p>
    <p class="ev-result-val" style="
        font-size:4.5rem; font-weight:900;
        background:{GRAD}; -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        line-height:1; margin:0;
    ">{power:.1f}</p>
    <p style="font-size:1rem; color:{TXT2}; font-weight:300; margin-top:8px;">
        kilowatts
    </p>
    <span style="
        display:inline-block; padding:6px 22px; border-radius:50px;
        font-size:0.70rem; font-weight:600; letter-spacing:2px;
        margin-top:20px;
        background:{badge[0]}; color:{badge[1]}; border:1px solid {badge[2]};
        backdrop-filter:blur(12px);
    ">{tier_text}</span>
</div>
""", unsafe_allow_html=True)

# Metric tiles
st.markdown(f"""
<div class="ev-metrics">
    <div class="ev-metrics-tile">
        <div style="font-size:1.6rem; font-weight:700; color:{TXT};">{soc_input}%</div>
        <div style="font-size:0.66rem; text-transform:uppercase; letter-spacing:1.5px;
                    color:{TXT3}; margin-top:6px;">Battery</div>
    </div>
    <div class="ev-metrics-tile">
        <div style="font-size:1.6rem; font-weight:700; color:{TXT};">{price_input}¢</div>
        <div style="font-size:0.66rem; text-transform:uppercase; letter-spacing:1.5px;
                    color:{TXT3}; margin-top:6px;">Tariff</div>
    </div>
    <div class="ev-metrics-tile">
        <div style="font-size:1.6rem; font-weight:700; color:{TXT};">{time_input}h</div>
        <div style="font-size:0.66rem; text-transform:uppercase; letter-spacing:1.5px;
                    color:{TXT3}; margin-top:6px;">Departure</div>
    </div>
    <div class="ev-metrics-tile">
        <div style="font-size:1.6rem; font-weight:700; color:{TXT};">{power:.1f}</div>
        <div style="font-size:0.66rem; text-transform:uppercase; letter-spacing:1.5px;
                    color:{TXT3}; margin-top:6px;">kW Output</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Membership function visualization
st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)
with st.expander("Membership Function Analysis"):
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rcParams.update({
        'figure.facecolor': MPL["fig"],
        'axes.facecolor':   MPL["ax"],
        'text.color':       MPL["txt"],
        'axes.labelcolor':  MPL["lbl"],
        'xtick.color':      MPL["tick"],
        'ytick.color':      MPL["tick"],
        'axes.edgecolor':   MPL["edge"],
        'grid.color':       MPL["grid"],
    })

    fig, axes = plt.subplots(1, 4, figsize=(16, 3.2))
    plot_colors = [ACC, ACC2, '#f472b6']

    for ax, var, title, val in zip(
        axes,
        [soc_var, price_var, time_var, cp_var],
        ['SOC (%)', 'Tariff (¢/kWh)', 'Time (h)', 'Power (kW)'],
        [soc_input, price_input, time_input, power],
    ):
        for i, term in enumerate(var.terms):
            ax.plot(var.universe, var[term].mf,
                    color=plot_colors[i % len(plot_colors)],
                    linewidth=2, label=term)
            ax.fill_between(var.universe, var[term].mf,
                            alpha=0.08, color=plot_colors[i % len(plot_colors)])
        ax.axvline(val, color=TXT, linestyle='--', alpha=0.3, linewidth=1)
        ax.set_title(title, fontsize=9, fontweight='600', pad=8)
        ax.legend(fontsize=7, framealpha=0.3)
        ax.set_ylim(-0.05, 1.1)

    plt.tight_layout()
    st.pyplot(fig)


# ── Divider ──
st.markdown('<div class="ev-divider"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#   SECTION: ABOUT
# ═══════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center; padding:0 0 36px; position:relative; z-index:1;">
    <h2 style="font-size:2rem; font-weight:700; color:{TXT}; margin:0 0 8px;">
        How It Works
    </h2>
    <div style="width:50px; height:3px; background:{GRAD};
                border-radius:2px; margin:0 auto;"></div>
</div>
""", unsafe_allow_html=True)

about_cols = st.columns(2)

about_cols[0].markdown(f"""
<div class="glass" style="min-height:240px;">
    <div style="font-size:0.68rem; font-weight:600; text-transform:uppercase;
                letter-spacing:2px; color:{ACC}; margin-bottom:12px;">System Overview</div>
    <p style="font-size:0.88rem; color:{TXT2}; line-height:1.85;">
        The EV Charge Optimizer employs a Mamdani-type fuzzy inference engine to determine
        optimal charging power for electric vehicles. It evaluates battery state of charge,
        prevailing electricity tariff, and scheduled departure window to produce a real-time
        recommendation between 0 and 22 kW — balancing urgency, cost efficiency, and
        battery longevity in every decision.
    </p>
</div>
""", unsafe_allow_html=True)

about_cols[1].markdown(f"""
<div class="glass" style="min-height:240px;">
    <div style="font-size:0.68rem; font-weight:600; text-transform:uppercase;
                letter-spacing:2px; color:{ACC2}; margin-bottom:12px;">Methodology</div>
    <p style="font-size:0.88rem; color:{TXT2}; line-height:1.85;">
        The engine operates on 20 fuzzy rules with triangular membership functions.
        Each input variable is fuzzified into three linguistic terms. The rule base covers
        critical scenarios — from emergency fast-charging under imminent departure to
        cost-optimized trickle-charging during off-peak tariff windows. Centroid
        defuzzification produces the final crisp power output.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

# Variable spec table in glass card
st.markdown(f"""
<div class="glass" style="overflow-x:auto; position:relative; z-index:1;">
    <div style="font-size:0.68rem; font-weight:600; text-transform:uppercase;
                letter-spacing:2px; color:{TXT3}; margin-bottom:18px;">
        Variable Specification
    </div>
    <table style="width:100%; border-collapse:collapse; font-size:0.84rem;">
        <thead>
            <tr style="border-bottom:1px solid {GLASS_BR};">
                <th style="text-align:left; padding:12px; color:{TXT3}; font-weight:600;
                           text-transform:uppercase; letter-spacing:1px; font-size:0.70rem;">
                    Variable</th>
                <th style="text-align:left; padding:12px; color:{TXT3}; font-weight:600;
                           text-transform:uppercase; letter-spacing:1px; font-size:0.70rem;">
                    Range</th>
                <th style="text-align:left; padding:12px; color:{TXT3}; font-weight:600;
                           text-transform:uppercase; letter-spacing:1px; font-size:0.70rem;">
                    Terms</th>
                <th style="text-align:left; padding:12px; color:{TXT3}; font-weight:600;
                           text-transform:uppercase; letter-spacing:1px; font-size:0.70rem;">
                    Role</th>
            </tr>
        </thead>
        <tbody>
            <tr style="border-bottom:1px solid {GLASS_BR};">
                <td style="padding:14px 12px; color:{TXT}; font-weight:500;">SOC</td>
                <td style="padding:14px 12px; color:{TXT2};">0 – 100 %</td>
                <td style="padding:14px 12px; color:{TXT2};">Low · Medium · High</td>
                <td style="padding:14px 12px;"><span style="
                    background:{B_ECO[0]}; color:{B_ECO[1]}; padding:3px 10px;
                    border-radius:8px; font-size:0.72rem; font-weight:500;">Input</span></td>
            </tr>
            <tr style="border-bottom:1px solid {GLASS_BR};">
                <td style="padding:14px 12px; color:{TXT}; font-weight:500;">Price</td>
                <td style="padding:14px 12px; color:{TXT2};">0 – 50 ¢/kWh</td>
                <td style="padding:14px 12px; color:{TXT2};">Low · Medium · High</td>
                <td style="padding:14px 12px;"><span style="
                    background:{B_ECO[0]}; color:{B_ECO[1]}; padding:3px 10px;
                    border-radius:8px; font-size:0.72rem; font-weight:500;">Input</span></td>
            </tr>
            <tr style="border-bottom:1px solid {GLASS_BR};">
                <td style="padding:14px 12px; color:{TXT}; font-weight:500;">Time</td>
                <td style="padding:14px 12px; color:{TXT2};">0 – 24 h</td>
                <td style="padding:14px 12px; color:{TXT2};">Short · Medium · Long</td>
                <td style="padding:14px 12px;"><span style="
                    background:{B_ECO[0]}; color:{B_ECO[1]}; padding:3px 10px;
                    border-radius:8px; font-size:0.72rem; font-weight:500;">Input</span></td>
            </tr>
            <tr>
                <td style="padding:14px 12px; color:{TXT}; font-weight:500;">Charge Power</td>
                <td style="padding:14px 12px; color:{TXT2};">0 – 22 kW</td>
                <td style="padding:14px 12px; color:{TXT2};">Low · Medium · High</td>
                <td style="padding:14px 12px;"><span style="
                    background:rgba(167,139,250,0.12); color:{ACC2}; padding:3px 10px;
                    border-radius:8px; font-size:0.72rem; font-weight:500;">Output</span></td>
            </tr>
        </tbody>
    </table>
</div>
""", unsafe_allow_html=True)

# Tech stack cards
st.markdown('<div style="height:32px;"></div>', unsafe_allow_html=True)

t_cols = st.columns(4)
stack = [
    ("🐍", "Python 3", "Runtime"),
    ("🔬", "scikit-fuzzy", "Inference"),
    ("📊", "NumPy · SciPy", "Compute"),
    ("🖥️", "Streamlit", "Interface"),
]
for col, (icon, name, role) in zip(t_cols, stack):
    col.markdown(f"""
    <div class="glass" style="text-align:center; min-height:140px;">
        <div style="
            width:44px; height:44px; border-radius:13px;
            background:{GLASS_H}; display:flex; align-items:center;
            justify-content:center; font-size:1.5rem;
            margin:0 auto 12px; border:1px solid {GLASS_BR};
        ">{icon}</div>
        <div style="font-size:0.9rem; font-weight:600; color:{TXT};">{name}</div>
        <div style="font-size:0.68rem; color:{TXT3}; margin-top:4px;
                    text-transform:uppercase; letter-spacing:1px;">{role}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Divider ──
st.markdown('<div class="ev-divider"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#   SECTION: CONTACT
# ═══════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center; padding:0 0 36px; position:relative; z-index:1;">
    <h2 style="font-size:2rem; font-weight:700; color:{TXT}; margin:0 0 8px;">
        Get in Touch
    </h2>
    <div style="width:50px; height:3px; background:{GRAD};
                border-radius:2px; margin:0 auto;"></div>
</div>
""", unsafe_allow_html=True)

_, form_col, _ = st.columns([1, 2, 1])
with form_col:
    with st.form("contact_form", clear_on_submit=True):
        name    = st.text_input("Full Name")
        email   = st.text_input("Email Address")
        subject = st.text_input("Subject")
        message = st.text_area("Message", height=140)
        submitted = st.form_submit_button("Send Message", use_container_width=True,
                                           type="primary")
        if submitted:
            if name and email and message:
                st.success("Message submitted successfully.")
            else:
                st.warning("Please complete all required fields.")

st.markdown('<div style="height:32px;"></div>', unsafe_allow_html=True)

# Contact info tiles
info_cols = st.columns(3)
contact_data = [
    ("📧", "Email", "ev-charging@optimizer.io"),
    ("📍", "Location", "Hyderabad, India"),
    ("⏱️", "Availability", "Mon – Sat · 9 AM – 6 PM"),
]
for col, (icon, label, value) in zip(info_cols, contact_data):
    col.markdown(f"""
    <div class="glass" style="text-align:center; min-height:120px;">
        <div style="font-size:1.6rem; margin-bottom:10px;">{icon}</div>
        <div style="font-size:0.68rem; text-transform:uppercase; letter-spacing:1.5px;
                    color:{TXT3}; margin-bottom:6px;">{label}</div>
        <div style="font-size:0.88rem; font-weight:500; color:{TXT};">{value}</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#   FOOTER
# ═══════════════════════════════════════════════
st.markdown(f"""
<div style="
    background:{FT_BG};
    backdrop-filter:blur(24px) saturate(160%);
    -webkit-backdrop-filter:blur(24px) saturate(160%);
    border-top:1px solid {GLASS_BR};
    padding:40px 24px 32px;
    margin-top:80px;
    text-align:center;
    border-radius:24px 24px 0 0;
    position:relative; z-index:1;
">
    <div style="display:flex; align-items:center; justify-content:center;
                gap:10px; margin-bottom:20px;">
        <span style="font-size:1.2rem;">⚡</span>
        <span style="font-size:1.05rem; font-weight:700; color:{TXT};
                     letter-spacing:-0.3px;">EV Charge Optimizer</span>
    </div>
    <div style="display:flex; justify-content:center; gap:32px; margin-bottom:20px;
                flex-wrap:wrap;">
        <span style="font-size:0.8rem; color:{TXT2};">Home</span>
        <span style="font-size:0.8rem; color:{TXT2};">About</span>
        <span style="font-size:0.8rem; color:{TXT2};">Scheduler</span>
        <span style="font-size:0.8rem; color:{TXT2};">Contact</span>
    </div>
    <div style="width:60px; height:1px; background:{GLASS_BR}; margin:0 auto 16px;"></div>
    <p style="font-size:0.66rem; color:{TXT3}; letter-spacing:2px; margin:0;">
        &copy; 2026 EV CHARGE OPTIMIZER &middot; ALL RIGHTS RESERVED
    </p>
</div>
""", unsafe_allow_html=True)
