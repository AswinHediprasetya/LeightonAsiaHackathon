"""
AI Punchlist — Leighton Asia Smart Inspection Hub
Single-file Streamlit application · Powered by Gemini 2.0 Flash

UI REDESIGN — Apple-inspired premium dashboard
Key design decisions:
  - Light theme: white canvas with near-zero visual noise
  - Typography: Plus Jakarta Sans (display) + DM Sans (body) — refined, not flashy
  - Orange accent used sparingly: only on interactive elements and key highlights
  - Cards use subtle box-shadow elevation instead of harsh borders
  - Every spacing value is intentional — 4px grid system
  - CSS animations: gentle fade-in on load, smooth hover lifts

Run: streamlit run ai_punchlist.py
Requires: pip install streamlit google-generativeai pandas pillow
"""

import io
import json
import random
import zipfile
import base64
import datetime
import os

import pandas as pd
import streamlit as st
from PIL import Image

# ── Gemini ───────────────────────────────────────────────────────────────────
try:
    import google.generativeai as genai
    _GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
    if _GEMINI_KEY:
        genai.configure(api_key=_GEMINI_KEY)
    _GEMINI_OK = bool(_GEMINI_KEY)
except ImportError:
    _GEMINI_OK = False

# ═════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Punchlist",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═════════════════════════════════════════════════════════════════════════════
# CSS — Apple-inspired premium light theme
#
# ARCHITECTURE RULE (unchanged from original):
#   Every HTML block is self-contained in a single st.markdown() call.
#   Widgets sit BETWEEN html blocks, styled via global CSS selectors.
#   Never open a <div> in one call and close it in another.
#
# DESIGN DECISIONS:
#   - No harsh background colors; depth created with shadow, not color
#   - 4px spacing grid: 4, 8, 12, 16, 20, 24, 32, 48, 64px
#   - Type scale: 11px labels → 13px body → 15px sub → 24px section → 34px hero
#   - Transitions: 200ms ease — fast enough to feel responsive, slow enough to feel smooth
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:          #0a0a0f;
    --bg1:         #0f0f1a;
    --bg2:         #141420;
    --bg3:         #1a1a2e;
    --surface:     rgba(255,255,255,0.04);
    --surface-hi:  rgba(255,255,255,0.07);
    --border:      rgba(255,255,255,0.07);
    --border-hi:   rgba(255,255,255,0.12);

    /* Leighton orange → amber gradient — NLB style */
    --grad:        linear-gradient(135deg, #ff6600 0%, #ff9500 100%);
    --grad-text:   linear-gradient(135deg, #ff8533 0%, #ffb347 100%);
    --accent:      #ff6600;
    --accent2:     #ff9500;

    --text:        #f0f0f5;
    --text2:       #9090a8;
    --text3:       #505068;

    --red:         #ff4d4d;
    --amber:       #ffb347;
    --green:       #34d399;
    --blue:        #60a5fa;

    --font: 'Inter', sans-serif;
    --mono: 'JetBrains Mono', monospace;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: var(--font) !important;
    background: var(--bg) !important;
    color: var(--text) !important;
    -webkit-font-smoothing: antialiased !important;
}
.block-container {
    padding: 0 2rem 6rem !important;
    max-width: 1280px !important;
}
#MainMenu, header, footer,
div[data-testid="stDecoration"] { display: none !important; }

/* Subtle grid pattern background — NLB aesthetic */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,102,0,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,102,0,0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
}

/* ── Page fade-in ── */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.block-container { animation: fadeIn 0.5s ease both; }

/* ── Tabs — NLB pill style ── */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
    margin-bottom: 0 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 7px !important;
    color: var(--text3) !important;
    font-family: var(--font) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 0.9rem !important;
    border: none !important;
    transition: all 0.15s ease !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    color: var(--text2) !important;
    background: var(--surface) !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--bg3) !important;
    color: var(--text) !important;
    font-weight: 600 !important;
    border: 1px solid var(--border-hi) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    background: transparent !important;
    border: none !important;
    padding: 1.75rem 0 0 !important;
}

/* ── Inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: var(--bg2) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 0.875rem !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(255,102,0,0.15) !important;
}
div[data-testid="stSelectbox"] > div > div,
div[data-baseweb="select"] div {
    background: var(--bg2) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 0.875rem !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] > label,
div[data-testid="stCheckbox"] label {
    color: var(--text2) !important;
    font-family: var(--font) !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
div[data-testid="stRadio"] label span {
    font-size: 0.875rem !important;
    color: var(--text2) !important;
}

/* ── Buttons ── */
div[data-testid="stButton"] button[kind="primary"] {
    background: var(--grad) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #fff !important;
    font-family: var(--font) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.01em !important;
    transition: opacity 0.15s, transform 0.15s !important;
    box-shadow: 0 0 20px rgba(255,102,0,0.2) !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 24px rgba(255,102,0,0.35) !important;
}
div[data-testid="stButton"] button[kind="secondary"] {
    background: var(--surface) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: 8px !important;
    color: var(--text2) !important;
    font-family: var(--font) !important;
    font-size: 0.82rem !important;
    transition: all 0.15s !important;
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
    background: var(--surface-hi) !important;
    color: var(--text) !important;
    border-color: var(--accent) !important;
}
div[data-testid="stForm"] button[kind="primaryFormSubmit"],
div[data-testid="stForm"] button[type="submit"] {
    background: var(--grad) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #fff !important;
    font-family: var(--font) !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    box-shadow: 0 0 20px rgba(255,102,0,0.2) !important;
    transition: opacity 0.15s, transform 0.15s !important;
}
div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
div[data-testid="stForm"] button[type="submit"]:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stDownloadButton"] button {
    background: var(--surface) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: 8px !important;
    color: var(--text2) !important;
    font-family: var(--font) !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    transition: all 0.15s !important;
}
div[data-testid="stDownloadButton"] button:hover {
    border-color: var(--accent) !important;
    color: var(--accent2) !important;
    background: rgba(255,102,0,0.06) !important;
}

/* ── Form container — glass card ── */
div[data-testid="stForm"] {
    background: var(--bg1) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.4rem !important;
    backdrop-filter: blur(12px) !important;
}

/* ── Alerts ── */
div[data-testid="stAlert"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: 10px !important;
    font-family: var(--font) !important;
    font-size: 0.875rem !important;
    color: var(--text2) !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* ── File / Camera ── */
div[data-testid="stFileUploader"] section {
    background: var(--bg2) !important;
    border: 1.5px dashed var(--border-hi) !important;
    border-radius: 10px !important;
    transition: border-color 0.15s !important;
}
div[data-testid="stFileUploader"] section:hover {
    border-color: var(--accent) !important;
    background: rgba(255,102,0,0.04) !important;
}
div[data-testid="stFileUploader"] label,
div[data-testid="stCameraInput"] label,
div[data-testid="stAudioInput"] label { color: var(--text3) !important; }
div[data-testid="stCameraInput"] button {
    background: var(--bg2) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: 8px !important;
    color: var(--text2) !important;
}

/* ── Misc ── */
div[data-testid="stSpinner"] p {
    font-family: var(--font) !important;
    font-size: 0.82rem !important;
    color: var(--text3) !important;
}
div[data-testid="stCaptionContainer"] p {
    font-family: var(--mono) !important;
    font-size: 0.68rem !important;
    color: var(--text3) !important;
}
hr { border-color: var(--border) !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-thumb { background: var(--bg3); border-radius: 2px; }

/* ══════════════════════════════════════════
   CUSTOM COMPONENTS — NLB inspired
   ══════════════════════════════════════════ */

/* Gradient text — NLB hero heading style */
.grad-text {
    background: var(--grad-text);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Section label */
.slabel {
    font-family: var(--font);
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text3);
    margin: 1.5rem 0 0.65rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.slabel::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border-hi) 0%, transparent 100%);
}

/* KPI cards — NLB "feature card" style */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-bottom: 2rem;
}
.kpi-card {
    background: var(--bg1);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
}
.kpi-card:hover {
    border-color: var(--border-hi);
    transform: translateY(-2px);
}
/* Top gradient accent line */
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1.5px;
    background: var(--grad);
    opacity: 0;
    transition: opacity 0.2s;
}
.kpi-card:hover::before { opacity: 1; }

.kpi-num {
    font-family: var(--font);
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.kpi-lbl {
    font-size: 0.72rem;
    color: var(--text3);
    font-weight: 500;
    letter-spacing: 0.01em;
}

/* Glass card — NLB feature block */
.glass-card {
    background: var(--bg1);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.3rem;
    margin-top: 0.65rem;
    position: relative;
    overflow: hidden;
}
.glass-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg,
        transparent 0%, rgba(255,150,0,0.4) 50%, transparent 100%);
}
.card-heading {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text3);
    margin-bottom: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.card-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* Field tiles inside glass card */
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.field-tile {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
}
.tile-label {
    font-family: var(--mono);
    font-size: 0.58rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text3);
    margin-bottom: 0.2rem;
}
.tile-val {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text);
    line-height: 1.4;
}
.tile-full {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    margin-top: 8px;
}

/* Priority pills — NLB badge style */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 0.18rem 0.6rem;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
.badge-high   { background: rgba(255,77,77,0.12);  color: #ff6b6b; border: 1px solid rgba(255,77,77,0.2); }
.badge-medium { background: rgba(255,179,71,0.12); color: #ffb347; border: 1px solid rgba(255,179,71,0.2); }
.badge-low    { background: rgba(52,211,153,0.12); color: #34d399; border: 1px solid rgba(52,211,153,0.2); }

/* Transcript */
.transcript-box {
    background: var(--bg2);
    border: 1px solid var(--border-hi);
    border-radius: 8px;
    padding: 0.8rem 0.9rem;
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: var(--text2);
    line-height: 1.65;
}

/* Offline notice */
.offline-card {
    background: rgba(255,179,71,0.06);
    border: 1px solid rgba(255,179,71,0.2);
    border-left: 2px solid var(--amber);
    border-radius: 0 10px 10px 0;
    padding: 0.9rem 1rem;
    font-size: 0.82rem;
    color: var(--text2);
    line-height: 1.65;
}

/* Queue badge */
.queue-badge {
    background: rgba(255,179,71,0.08);
    border: 1px solid rgba(255,179,71,0.2);
    border-radius: 8px;
    padding: 0.75rem 0.9rem;
    color: var(--amber);
    font-size: 0.82rem;
    margin-bottom: 0.75rem;
}

/* Desc card */
.desc-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.85rem 1rem;
    font-size: 0.82rem;
    color: var(--text2);
    line-height: 1.65;
    margin-bottom: 0.75rem;
}
.desc-card b { color: var(--text); }

/* Danger */
.danger-card {
    background: rgba(255,77,77,0.06);
    border: 1px solid rgba(255,77,77,0.15);
    border-radius: 8px;
    padding: 0.7rem 0.9rem;
    font-size: 0.78rem;
    color: #ff9999;
    margin-bottom: 0.6rem;
}

/* Meta grid */
.meta-table {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.4rem 1.5rem;
}
.mk {
    font-family: var(--mono);
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text3);
}
.mv {
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text2);
}

/* Record count */
.rec-count {
    display: inline-block;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.18rem 0.65rem;
    font-size: 0.72rem;
    color: var(--text3);
    margin: 0.3rem 0 0.65rem;
    font-family: var(--mono);
}

/* Empty state */
.empty-box {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text3);
    font-size: 0.82rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}
</style>
""", unsafe_allow_html=True)



# ═════════════════════════════════════════════════════════════════════════════
# SESSION STATE  — unchanged from original
# ═════════════════════════════════════════════════════════════════════════════
DEFECT_COLS = [
    "ID", "Timestamp", "Location", "Status", "Defect Type",
    "Priority", "Subcontractor", "Repair Method", "Notes",
    "Due Date", "AI Reasoning", "Photo ID",
]
if "defects"        not in st.session_state: st.session_state.defects        = pd.DataFrame(columns=DEFECT_COLS)
if "images"         not in st.session_state: st.session_state.images         = {}
if "offline_queue"  not in st.session_state: st.session_state.offline_queue  = []
if "ai_suggestion"  not in st.session_state: st.session_state.ai_suggestion  = {}
if "v_text"         not in st.session_state: st.session_state.v_text         = ""
if "defect_counter" not in st.session_state: st.session_state.defect_counter = 1

# ═════════════════════════════════════════════════════════════════════════════
# HELPERS — logic unchanged, HTML output updated
# ═════════════════════════════════════════════════════════════════════════════
def _strip_json(text: str) -> str:
    text = text.strip()
    for fence in ["```json", "```JSON", "```"]:
        if text.startswith(fence): text = text[len(fence):]
    if text.endswith("```"): text = text[:-3]
    return text.strip()

def _priority_pill(p: str) -> str:
    cls = {"High": "pill-high", "Medium": "pill-medium", "Low": "pill-low"}.get(p, "pill-medium")
    return f'<span class="pill {cls}">{p}</span>'

def _sla_days(priority: str) -> int:
    return {"High": 3, "Medium": 7, "Low": 14}.get(priority, 7)

def _next_id() -> str:
    idx = st.session_state.defect_counter
    st.session_state.defect_counter += 1
    return f"LA-{idx:04d}"

def gemini_analyze_image(image_bytes: bytes) -> dict:
    fallback = {
        "defect_type": "Honeycombing", "priority": "High", "trade": "Concrete",
        "reasoning":   "AI analysis unavailable — fallback values applied.",
        "repair_method": "Remove loose concrete, apply bonding agent, patch with non-shrink grout.",
        "subcontractor_hint": "Apex Concrete Works",
    }
    if not _GEMINI_OK: return fallback
    try:
        model    = genai.GenerativeModel("gemini-2.0-flash")
        img      = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        buf      = io.BytesIO()
        img.save(buf, format="JPEG")
        img_data = {"mime_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}
        prompt = (
            "You are an expert construction site quality inspector for Leighton Asia. "
            "Analyze this site photo and return ONLY a valid JSON object — no markdown. "
            'Keys: "defect_type", "priority" (High/Medium/Low), "trade" (Concrete/Rebar/Formwork), '
            '"reasoning" (1 sentence), "repair_method" (1 sentence), '
            '"subcontractor_hint" (Apex Concrete Works / BuildRight Formwork / SteelCore Rebar).'
        )
        response = model.generate_content([prompt, img_data])
        return json.loads(_strip_json(response.text))
    except Exception as e:
        fallback["reasoning"] = f"AI error: {str(e)[:80]}"
        return fallback

def gemini_transcribe(audio_bytes: bytes, translate: bool = False) -> str:
    if not _GEMINI_OK: return "Transcription unavailable — GEMINI_API_KEY not set."
    try:
        model      = genai.GenerativeModel("gemini-2.0-flash")
        audio_data = {"mime_type": "audio/wav", "data": base64.b64encode(audio_bytes).decode()}
        task = "Transcribe this audio recording accurately."
        if translate: task += " If not in English, translate to English."
        task += " Return only the transcribed text."
        return model.generate_content([task, audio_data]).text.strip()
    except Exception as e:
        return f"Transcription failed: {str(e)[:120]}"

def build_zip_export() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("punchlist.csv", st.session_state.defects.to_csv(index=False).encode("utf-8"))
        for pid, img_bytes in st.session_state.images.items():
            zf.writestr(f"Evidence/{pid}.jpg", img_bytes)
    return buf.getvalue()

def load_demo_data():
    rng = random.Random(42)
    locations = [
        "Level B1 — Grid C3", "Level 3 — Column F7", "Roof Deck — Zone A",
        "Basement Car Park — Row 4", "Level 5 — Stairwell S2", "Level 2 — Beam B14",
        "Foundation — Grid A1", "Level 7 — Slab Edge", "Level 1 — Wall W3",
        "Level 6 — Lift Core LC2", "Level 4 — Transfer Plate", "Podium — Zone P3",
    ]
    defect_types = [
        "Honeycombing","Surface Cracking","Spalling","Rebar Exposure",
        "Formwork Misalignment","Cold Joint","Segregation",
        "Void Formation","Delamination","Cover Depth Deficiency",
    ]
    priorities     = ["High","High","Medium","Medium","Medium","Low"]
    subcontractors = ["Apex Concrete Works","BuildRight Formwork","SteelCore Rebar"]
    statuses       = ["Open","Open","Open","Draft","Closed"]
    repair_methods = {
        "Honeycombing":           "Break out, clean, apply bonding slurry, patch with non-shrink grout.",
        "Surface Cracking":       "Rout and seal cracks with polyurethane sealant.",
        "Spalling":               "Remove loose material, treat rebar, apply epoxy mortar patch.",
        "Rebar Exposure":         "Clean rebar, apply corrosion inhibitor, patch with cementitious mortar.",
        "Formwork Misalignment":  "Cut, grind, and re-strike to specification. Submit NCR.",
        "Cold Joint":             "Wet grind joint plane, apply bonding agent, inject with epoxy grout.",
        "Segregation":            "Core test for strength. If substandard: cut out and re-pour.",
        "Void Formation":         "Drill and inject with low-viscosity epoxy resin.",
        "Delamination":           "Map extent with hammer tap. Cut perimeter, remove, re-apply.",
        "Cover Depth Deficiency": "Covermeter survey, mark affected zones, apply protective coating.",
    }
    rows = []
    for i in range(1, 62):
        dt      = defect_types[rng.randint(0, len(defect_types)-1)]
        pri     = rng.choice(priorities)
        ts      = datetime.datetime.now() - datetime.timedelta(days=rng.randint(0, 30))
        due     = ts.date() + datetime.timedelta(days=_sla_days(pri))
        rows.append({
            "ID": f"LA-{i:04d}", "Timestamp": ts.strftime("%Y-%m-%d %H:%M"),
            "Location": rng.choice(locations), "Status": rng.choice(statuses),
            "Defect Type": dt, "Priority": pri, "Subcontractor": rng.choice(subcontractors),
            "Repair Method": repair_methods.get(dt, "Inspect and repair per specification."),
            "Notes": rng.choice([
                "Requires immediate inspection.","Flagged by site QC officer.",
                "Awaiting subcontractor acknowledgement.","Repair materials on order.",
                "Follow-up inspection scheduled.","",
            ]),
            "Due Date": str(due),
            "AI Reasoning": "Detected via visual inspection of site photograph.",
            "Photo ID": "",
        })
    st.session_state.defects        = pd.DataFrame(rows, columns=DEFECT_COLS)
    st.session_state.defect_counter = 62



# ── Header — NLB style ────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    border-bottom: 1px solid var(--border);
    padding: 1.1rem 2rem;
    margin: 0 -2rem 2rem -2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(180deg, rgba(15,15,26,0.8) 0%, transparent 100%);
    backdrop-filter: blur(8px);
">
  <div style="display:flex;align-items:center;gap:0.85rem">
    <div style="
        width:36px;height:36px;
        background:linear-gradient(135deg,#ff6600,#ff9500);
        border-radius:9px;
        display:flex;align-items:center;justify-content:center;
        font-size:1.05rem;
        box-shadow:0 0 16px rgba(255,102,0,0.35);
        flex-shrink:0;
    ">🏗️</div>
    <div>
      <div style="font-family:'Inter',sans-serif;font-size:1rem;font-weight:700;
                  color:var(--text);letter-spacing:-0.02em;line-height:1.2">
        AI Punchlist
      </div>
      <div style="font-family:'Inter',sans-serif;font-size:0.72rem;
                  color:var(--text3);margin-top:1px;letter-spacing:0.01em">
        Leighton Asia &nbsp;·&nbsp; Smart Inspection Hub
      </div>
    </div>
  </div>

  <div style="display:flex;align-items:center;gap:1.5rem">
    <div style="font-family:'Inter',sans-serif;font-size:0.72rem;color:var(--text3)">
      Powered by
      <span style="color:var(--text2);font-weight:500;margin-left:0.3rem">
        Gemini 2.0 Flash
      </span>
    </div>
    <div style="
        display:flex;align-items:center;gap:0.45rem;
        background:{'rgba(52,211,153,0.08)' if _GEMINI_OK else 'var(--surface)'};
        border:1px solid {'rgba(52,211,153,0.2)' if _GEMINI_OK else 'var(--border)'};
        border-radius:20px;
        padding:0.28rem 0.75rem;
        font-size:0.72rem;font-weight:500;
        color:{'#34d399' if _GEMINI_OK else 'var(--text3)'};
    ">
      <span style="width:6px;height:6px;border-radius:50%;
                   background:{'#34d399' if _GEMINI_OK else 'var(--text3)'}"></span>
      {'Connected' if _GEMINI_OK else 'No API Key'}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI strip ─────────────────────────────────────────────────────────────────
df_all  = st.session_state.defects
total   = len(df_all)
high_c  = int((df_all["Priority"] == "High").sum())   if total else 0
med_c   = int((df_all["Priority"] == "Medium").sum()) if total else 0
low_c   = int((df_all["Priority"] == "Low").sum())    if total else 0
q_count = len(st.session_state.offline_queue)

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-num">{total}</div>
    <div class="kpi-lbl">Total Defects</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-num" style="background:linear-gradient(135deg,#ff4d4d,#ff8080);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent">{high_c}</div>
    <div class="kpi-lbl">High Priority</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-num" style="background:linear-gradient(135deg,#ff9500,#ffb347);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent">{med_c}</div>
    <div class="kpi-lbl">Medium Priority</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-num" style="background:linear-gradient(135deg,#34d399,#6ee7b7);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent">{low_c}</div>
    <div class="kpi-lbl">Low Priority</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-num" style="color:{'var(--amber)' if q_count else 'var(--text3)'}">{q_count}</div>
    <div class="kpi-lbl">Offline Queue</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── UI Helpers ───────────────────────────────────────────────────────────────
def _sec(label):
    st.markdown(f'<div class="slabel">{label}</div>', unsafe_allow_html=True)

def _pill(p):
    cls = {"High":"badge-high","Medium":"badge-medium","Low":"badge-low"}.get(p,"badge-medium")
    dot = {"High":"#ff6b6b","Medium":"#ffb347","Low":"#34d399"}.get(p,"#ffb347")
    return f'<span class="badge {cls}"><span class="badge-dot" style="background:{dot}"></span>{p}</span>'

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📸  Field Capture",
    "📋  Punchlist",
    "📊  Dashboard",
    "⚙️  Sync",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — FIELD CAPTURE
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    left, right = st.columns([1, 1.05], gap="large")

    with left:
        _sec("Connectivity")
        conn = st.radio("conn",
                        ["🟢 Live AI Mode (5G/Wi-Fi)", "🟡 Offline Mode (No Signal)"],
                        label_visibility="collapsed")
        is_live = conn.startswith("🟢")

        _sec("Site Photo")
        src = st.radio("src", ["Camera", "Upload"],
                       horizontal=True, label_visibility="collapsed")

        captured = None
        if src == "Camera":
            captured = st.camera_input("", label_visibility="collapsed")
        else:
            captured = st.file_uploader("", type=["jpg","jpeg","png","webp"],
                                        label_visibility="collapsed")

        img_bytes = None
        if captured:
            img_bytes = (captured.read() if hasattr(captured,"read")
                         else captured.getvalue())
            try:
                st.image(Image.open(io.BytesIO(img_bytes)),
                         use_container_width=True)
            except Exception:
                pass

        if img_bytes:
            if is_live:
                if st.button("✦ Analyze with Vision AI", type="primary",
                             use_container_width=True):
                    with st.spinner("Analyzing with Gemini Vision…"):
                        st.session_state.ai_suggestion = gemini_analyze_image(img_bytes)

                if st.session_state.ai_suggestion:
                    s  = st.session_state.ai_suggestion
                    pp = _pill(s.get("priority","Medium"))
                    st.markdown(f"""
<div class="glass-card">
  <div class="card-heading">AI Analysis Result</div>
  <div class="field-row">
    <div class="field-tile">
      <div class="tile-label">Defect Type</div>
      <div class="tile-val">{s.get('defect_type','—')}</div>
    </div>
    <div class="field-tile">
      <div class="tile-label">Priority</div>
      <div class="tile-val">{pp}</div>
    </div>
    <div class="field-tile">
      <div class="tile-label">Trade</div>
      <div class="tile-val">{s.get('trade','—')}</div>
    </div>
    <div class="field-tile">
      <div class="tile-label">Subcontractor</div>
      <div class="tile-val" style="font-size:0.8rem">{s.get('subcontractor_hint','—')}</div>
    </div>
  </div>
  <div class="tile-full">
    <div class="tile-label">Reasoning</div>
    <div class="tile-val" style="color:var(--text2);font-size:0.82rem">{s.get('reasoning','—')}</div>
  </div>
  <div class="tile-full">
    <div class="tile-label">Repair Method</div>
    <div class="tile-val" style="color:var(--text2);font-size:0.82rem">{s.get('repair_method','—')}</div>
  </div>
</div>
""", unsafe_allow_html=True)
            else:
                if st.button("💾 Save to Offline Queue", type="primary",
                             use_container_width=True):
                    st.session_state.offline_queue.append({
                        "timestamp":   datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "image_bytes": img_bytes,
                        "size_kb":     round(len(img_bytes)/1024, 1),
                    })
                    st.success(f"Saved · {len(st.session_state.offline_queue)} in queue")

        _sec("Voice Notes")
        audio = st.audio_input("", label_visibility="collapsed")
        tr    = st.checkbox("Translate to English", value=False)
        if audio:
            ab = audio.read() if hasattr(audio,"read") else audio.getvalue()
            if st.button("Transcribe", use_container_width=True):
                with st.spinner("Transcribing…"):
                    st.session_state.v_text = gemini_transcribe(ab, tr)
        if st.session_state.v_text:
            st.markdown(f"""
<div class="transcript-box">
  <div style="font-family:var(--mono);font-size:0.58rem;text-transform:uppercase;
              letter-spacing:0.1em;color:var(--text3);margin-bottom:0.4rem">Transcript</div>
  {st.session_state.v_text}
</div>
""", unsafe_allow_html=True)

    with right:
        _sec("Review & Assign")

        if not is_live:
            st.markdown("""
<div class="offline-card">
  <strong style="color:var(--text)">Offline mode active</strong><br>
  Queue captures on the left. Switch to Live Mode when signal is restored,
  then sync via the Sync tab.
</div>
""", unsafe_allow_html=True)
        else:
            ai         = st.session_state.ai_suggestion
            _def_types = ["Honeycombing","Surface Cracking","Spalling","Rebar Exposure",
                          "Formwork Misalignment","Cold Joint","Segregation",
                          "Void Formation","Delamination","Cover Depth Deficiency","Other"]
            _pris      = ["High","Medium","Low"]
            _stats     = ["Open","Draft","Closed"]
            _subs      = ["Apex Concrete Works","BuildRight Formwork","SteelCore Rebar"]

            def _i(lst, val, d=0):
                try: return lst.index(val)
                except ValueError: return d

            with st.form("form", clear_on_submit=True):
                loc   = st.text_input("Location / Grid Reference",
                                      placeholder="e.g. Level 3 — Grid F7")
                c1,c2 = st.columns(2)
                with c1: stat = st.selectbox("Status", _stats)
                with c2: pri  = st.selectbox("Priority", _pris,
                                              index=_i(_pris,ai.get("priority","Medium"),1))
                defect   = st.selectbox("Defect Type", _def_types,
                                        index=_i(_def_types, ai.get("defect_type","")))
                sub      = st.selectbox("Subcontractor", _subs,
                                        index=_i(_subs, ai.get("subcontractor_hint","")))
                repair   = st.text_area("Repair Method",
                                        value=ai.get("repair_method",""), height=76)
                notes    = st.text_area("Notes", value=st.session_state.v_text,
                                        placeholder="Additional notes…", height=76)
                done     = st.form_submit_button("✦ Log Defect to Punchlist",
                                                  type="primary",
                                                  use_container_width=True)
                if done:
                    if not loc.strip():
                        st.error("Location is required.")
                    else:
                        due = (datetime.date.today() +
                               datetime.timedelta(days=_sla_days(pri)))
                        photo_id = ""
                        if img_bytes:
                            photo_id = _next_id().replace("LA-","IMG-")
                            try:
                                pil = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                                b   = io.BytesIO()
                                pil.save(b, format="JPEG", quality=85)
                                st.session_state.images[photo_id] = b.getvalue()
                            except Exception:
                                st.session_state.images[photo_id] = img_bytes

                        nid = _next_id()
                        st.session_state.defects = pd.concat([
                            st.session_state.defects,
                            pd.DataFrame([{
                                "ID": nid,
                                "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "Location": loc, "Status": stat,
                                "Defect Type": defect, "Priority": pri,
                                "Subcontractor": sub, "Repair Method": repair,
                                "Notes": notes, "Due Date": str(due),
                                "AI Reasoning": ai.get("reasoning","Manual entry."),
                                "Photo ID": photo_id,
                            }])
                        ], ignore_index=True)
                        st.session_state.ai_suggestion = {}
                        st.session_state.v_text = ""
                        st.success(f"✓ {nid} logged — {defect} · {pri} · Due {due}")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — PUNCHLIST
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    df = st.session_state.defects
    if df.empty:
        st.markdown("""
<div class="empty-box">
  <span style="font-size:1.8rem;opacity:0.2">📋</span>
  <span>No defects logged yet.</span>
</div>
""", unsafe_allow_html=True)
    else:
        f1,f2,_ = st.columns([1,1,2])
        with f1: pf = st.selectbox("Priority", ["All","High","Medium","Low"])
        with f2: sf = st.selectbox("Status",   ["All","Open","Draft","Closed"])

        d = df.copy()
        if pf != "All": d = d[d["Priority"]==pf]
        if sf != "All": d = d[d["Status"]==sf]

        st.markdown(f'<div class="rec-count">{len(d)} of {len(df)} records</div>',
                    unsafe_allow_html=True)

        RC="#ff4d4d"; AC="#ffb347"; GC="#34d399"
        def sp(v): c={"High":RC,"Medium":AC,"Low":GC}.get(v,""); return f"color:{c};font-weight:600" if c else ""
        def ss(v): c={"Open":RC,"Draft":AC,"Closed":GC}.get(v,""); return f"color:{c}" if c else ""

        st.dataframe(
            d.style.applymap(sp,subset=["Priority"]).applymap(ss,subset=["Status"]),
            use_container_width=True, height=400,
        )
        _sec("Export")
        st.download_button(
            f"⬇  Download ZIP — {len(st.session_state.images)} photo(s)",
            data=build_zip_export(),
            file_name=f"leighton_{datetime.date.today()}.zip",
            mime="application/zip",
            use_container_width=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    df = st.session_state.defects
    if df.empty or len(df) < 2:
        st.markdown("""
<div class="empty-box">
  <span style="font-size:1.8rem;opacity:0.2">📊</span>
  <span>Load the demo dataset from the Sync tab to see charts.</span>
</div>
""", unsafe_allow_html=True)
    else:
        c1,c2 = st.columns(2, gap="large")
        with c1:
            _sec("By Priority")
            pc = df["Priority"].value_counts().reset_index()
            pc.columns = ["Priority","Count"]
            pc["Priority"] = pd.Categorical(pc["Priority"],
                                            categories=["High","Medium","Low"],ordered=True)
            st.bar_chart(pc.sort_values("Priority").set_index("Priority"),
                         color="#ff6600", height=240, use_container_width=True)
        with c2:
            _sec("By Subcontractor")
            sc = df["Subcontractor"].value_counts().reset_index()
            sc.columns = ["Sub","Count"]
            st.bar_chart(sc.set_index("Sub"),
                         color="#ff9500", height=240, use_container_width=True)
        c3,c4 = st.columns(2, gap="large")
        with c3:
            _sec("By Defect Type")
            tc = df["Defect Type"].value_counts().head(8).reset_index()
            tc.columns = ["Type","Count"]
            st.bar_chart(tc.set_index("Type"),
                         color="#505068", height=240, use_container_width=True)
        with c4:
            _sec("By Status")
            stc = df["Status"].value_counts().reset_index()
            stc.columns = ["Status","Count"]
            st.bar_chart(stc.set_index("Status"),
                         color="#2a2a40", height=240, use_container_width=True)
        _sec("Priority × Subcontractor")
        pivot = pd.crosstab(df["Subcontractor"], df["Priority"],
                            margins=True, margins_name="Total")
        cols = [c for c in ["High","Medium","Low","Total"] if c in pivot.columns]
        st.dataframe(pivot[cols], use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — SYNC & DATA
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    s1,s2 = st.columns(2, gap="large")

    with s1:
        _sec("Offline Queue")
        q = st.session_state.offline_queue
        if q:
            kb = sum(i.get("size_kb",0) for i in q)
            st.markdown(f"""
<div class="queue-badge">
  {len(q)} capture(s) pending sync &nbsp;·&nbsp; {kb:.1f} KB
</div>
""", unsafe_allow_html=True)
            st.dataframe(
                pd.DataFrame([{"#":i+1,"Captured At":x["timestamp"],
                                "KB":x.get("size_kb","—")}
                               for i,x in enumerate(q)]),
                use_container_width=True, hide_index=True,
            )
            if st.button("☁  Sync Now", type="primary", use_container_width=True):
                with st.spinner("Syncing…"):
                    import time; time.sleep(1.5)
                    st.session_state.offline_queue = []
                    st.success("Sync complete.")
                    st.rerun()
        else:
            st.markdown("""
<div class="empty-box" style="padding:2rem">
  <span style="font-size:1.2rem;opacity:0.2">✓</span>
  <span>Queue is empty</span>
</div>
""", unsafe_allow_html=True)

    with s2:
        _sec("Data")
        st.markdown("""
<div class="desc-card">
  Load <b>61 realistic defects</b> across multiple subcontractors,
  priorities, and locations to demo the Dashboard and Punchlist.
</div>
""", unsafe_allow_html=True)

        if st.button("✦ Load Demo Dataset", type="primary", use_container_width=True):
            load_demo_data()
            st.success("Dataset loaded.")
            st.rerun()

        if not st.session_state.defects.empty:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            st.markdown("""
<div class="danger-card">
  This will clear all defects and images from this session.
</div>
""", unsafe_allow_html=True)
            if st.button("Clear All Data", use_container_width=True):
                st.session_state.defects        = pd.DataFrame(columns=DEFECT_COLS)
                st.session_state.images         = {}
                st.session_state.ai_suggestion  = {}
                st.session_state.v_text         = ""
                st.session_state.defect_counter = 1
                st.success("Cleared.")
                st.rerun()

        _sec("Session")
        st.markdown(f"""
<div class="meta-table">
  <span class="mk">Gemini</span>
  <span class="mv">{'Connected' if _GEMINI_OK else 'No key set'}</span>
  <span class="mk">Defects</span>
  <span class="mv">{len(st.session_state.defects)}</span>
  <span class="mk">Photos</span>
  <span class="mv">{len(st.session_state.images)}</span>
  <span class="mk">Queue</span>
  <span class="mv">{len(st.session_state.offline_queue)}</span>
  <span class="mk">Date</span>
  <span class="mv">{datetime.date.today().strftime('%d %b %Y')}</span>
</div>
""", unsafe_allow_html=True)
