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
/* ── Fonts: Plus Jakarta Sans (display) + DM Sans (body) ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Design Tokens ── */
:root {
    /* Backgrounds */
    --bg-page:      #F2F2F7;
    --bg-card:      #FFFFFF;
    --bg-input:     #F5F5F7;

    /* Text hierarchy */
    --text-primary:   #1D1D1F;
    --text-secondary: #6E6E73;
    --text-tertiary:  #AEAEB2;

    /* Accent — Leighton Orange, used surgically */
    --orange:        #FF6600;
    --orange-soft:   rgba(255,102,0,0.08);

    /* Semantic colors — muted, professional */
    --red:           #FF3B30;
    --red-soft:      rgba(255,59,48,0.08);
    --amber:         #FF9500;
    --amber-soft:    rgba(255,149,0,0.08);
    --green:         #34C759;
    --green-soft:    rgba(52,199,89,0.08);
    --blue:          #007AFF;
    --blue-soft:     rgba(0,122,255,0.08);

    /* Shadows */
    --shadow-xs: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
    --shadow-sm: 0 2px 8px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04);

    /* Borders */
    --border:    rgba(0,0,0,0.06);
    --border-md: rgba(0,0,0,0.10);

    /* Radius */
    --r-sm:  8px;
    --r-md:  12px;
    --r-lg:  16px;

    /* Type */
    --font-display: 'Plus Jakarta Sans', sans-serif;
    --font-body:    'DM Sans', sans-serif;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    background-color: var(--bg-page) !important;
    color: var(--text-primary) !important;
    -webkit-font-smoothing: antialiased !important;
}
.block-container {
    padding: 0 2.5rem 6rem !important;
    max-width: 1320px !important;
}
#MainMenu, header, footer { visibility: hidden !important; display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }

/* Page entrance */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.block-container { animation: fadeUp 0.45s cubic-bezier(0.16,1,0.3,1) both; }

/* ── Tabs ── */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-radius: 0 !important;
    padding: 0 !important;
    gap: 0 !important;
    border-bottom: 1px solid var(--border) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 0 !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-display) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    text-transform: none !important;
    padding: 0.75rem 1.25rem !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    transition: color 0.2s ease, border-color 0.2s ease !important;
    margin-bottom: -1px !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    color: var(--text-primary) !important;
    background: transparent !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--orange) !important;
    border-bottom: 2px solid var(--orange) !important;
    background: transparent !important;
    font-weight: 600 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    background: transparent !important;
    border: none !important;
    padding: 2rem 0 0 !important;
}

/* ── Inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: 0.875rem !important;
    padding: 0.6rem 0.85rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    box-shadow: var(--shadow-xs) !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--orange) !important;
    box-shadow: 0 0 0 3px rgba(255,102,0,0.12), var(--shadow-xs) !important;
}
div[data-testid="stSelectbox"] > div > div,
div[data-baseweb="select"] div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: 0.875rem !important;
    box-shadow: var(--shadow-xs) !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] > label,
div[data-testid="stCheckbox"] label,
div[data-testid="stMultiSelect"] label {
    color: var(--text-secondary) !important;
    font-family: var(--font-display) !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
div[data-testid="stRadio"] label span {
    font-size: 0.875rem !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}

/* ── Buttons ── */
div[data-testid="stButton"] button[kind="primary"] {
    background: var(--orange) !important;
    border: none !important;
    border-radius: var(--r-sm) !important;
    color: #FFFFFF !important;
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.01em !important;
    padding: 0.6rem 1.2rem !important;
    box-shadow: 0 1px 3px rgba(255,102,0,0.3) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background: #E55A00 !important;
    box-shadow: 0 4px 12px rgba(255,102,0,0.35) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stButton"] button[kind="secondary"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-body) !important;
    font-size: 0.82rem !important;
    box-shadow: var(--shadow-xs) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
    color: var(--text-primary) !important;
    box-shadow: var(--shadow-sm) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stForm"] button[kind="primaryFormSubmit"],
div[data-testid="stForm"] button[type="submit"] {
    background: var(--orange) !important;
    border: none !important;
    border-radius: var(--r-sm) !important;
    color: #FFFFFF !important;
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.7rem 1.5rem !important;
    box-shadow: 0 1px 3px rgba(255,102,0,0.3) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
div[data-testid="stForm"] button[type="submit"]:hover {
    background: #E55A00 !important;
    box-shadow: 0 4px 12px rgba(255,102,0,0.35) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stDownloadButton"] button {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--r-sm) !important;
    color: var(--orange) !important;
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    box-shadow: var(--shadow-xs) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stDownloadButton"] button:hover {
    background: var(--orange-soft) !important;
    box-shadow: var(--shadow-sm) !important;
    transform: translateY(-1px) !important;
}

/* ── Form container ── */
div[data-testid="stForm"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
    padding: 1.5rem !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Alerts ── */
div[data-testid="stAlert"] {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    font-family: var(--font-body) !important;
    font-size: 0.875rem !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-xs) !important;
}

/* ── File uploader / Camera / Audio ── */
div[data-testid="stFileUploader"] section {
    background: var(--bg-input) !important;
    border: 1.5px dashed var(--border-md) !important;
    border-radius: var(--r-md) !important;
    transition: border-color 0.2s ease !important;
}
div[data-testid="stFileUploader"] section:hover { border-color: var(--orange) !important; }
div[data-testid="stFileUploader"] label,
div[data-testid="stCameraInput"] label,
div[data-testid="stAudioInput"] label { color: var(--text-secondary) !important; }
div[data-testid="stCameraInput"] button {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text-primary) !important;
    transition: all 0.2s ease !important;
}

/* ── Spinner ── */
div[data-testid="stSpinner"] p {
    font-family: var(--font-body) !important;
    font-size: 0.875rem !important;
    color: var(--text-secondary) !important;
}

/* ── Caption ── */
div[data-testid="stCaptionContainer"] p {
    font-family: var(--font-body) !important;
    font-size: 0.75rem !important;
    color: var(--text-tertiary) !important;
}

/* ═══════════════════════════════
   CUSTOM HTML COMPONENTS
   ═══════════════════════════════ */

/* Section label */
.sec-lbl {
    font-family: var(--font-display);
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-tertiary);
    margin-bottom: 0.75rem;
    margin-top: 1.75rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.sec-lbl::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* KPI grid */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 2rem;
}
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: 1.25rem 1.4rem;
    box-shadow: var(--shadow-xs);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.kpi-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}
.kpi-accent {
    width: 24px;
    height: 3px;
    border-radius: 2px;
    margin-bottom: 0.85rem;
}
.kpi-val {
    font-family: var(--font-display);
    font-size: 1.9rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
}
.kpi-lbl {
    font-family: var(--font-body);
    font-size: 0.78rem;
    color: var(--text-secondary);
}
.kpi-sub {
    font-family: var(--font-body);
    font-size: 0.7rem;
    color: var(--text-tertiary);
    margin-top: 0.15rem;
}

/* AI output card */
.ai-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: 1.25rem 1.4rem;
    margin-top: 0.75rem;
    box-shadow: var(--shadow-sm);
}
.ai-card-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
}
.ai-card-title {
    font-family: var(--font-display);
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-secondary);
}
.ai-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 8px;
}
.ai-field {
    background: var(--bg-input);
    border-radius: var(--r-sm);
    padding: 0.65rem 0.85rem;
}
.ai-lbl {
    font-family: var(--font-display);
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-tertiary);
    margin-bottom: 0.25rem;
}
.ai-val {
    font-family: var(--font-body);
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-primary);
    line-height: 1.4;
}
.ai-full {
    background: var(--bg-input);
    border-radius: var(--r-sm);
    padding: 0.65rem 0.85rem;
    margin-top: 8px;
}

/* Priority pills */
.pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.2rem 0.65rem;
    border-radius: 100px;
    font-family: var(--font-display);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.pill::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
}
.pill-high   { background: var(--red-soft);   color: var(--red);   }
.pill-high::before   { background: var(--red);   }
.pill-medium { background: var(--amber-soft); color: var(--amber); }
.pill-medium::before { background: var(--amber); }
.pill-low    { background: var(--green-soft); color: var(--green); }
.pill-low::before    { background: var(--green); }

/* Offline queue badge */
.queue-badge {
    background: var(--amber-soft);
    border: 1px solid rgba(255,149,0,0.2);
    border-radius: var(--r-md);
    padding: 1rem 1.2rem;
    color: #9A5200;
    font-family: var(--font-body);
    font-size: 0.875rem;
    margin-bottom: 1rem;
    line-height: 1.5;
}

/* Info card */
.info-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: 1.25rem 1.4rem;
    box-shadow: var(--shadow-xs);
    font-family: var(--font-body);
    font-size: 0.875rem;
    color: var(--text-secondary);
    line-height: 1.65;
}
.info-card strong { color: var(--text-primary); font-weight: 600; }

/* Transcript box */
.transcript-box {
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    padding: 0.85rem 1rem;
    margin-top: 0.5rem;
    font-family: var(--font-body);
    font-size: 0.875rem;
    color: var(--text-primary);
    line-height: 1.6;
}
.transcript-label {
    font-family: var(--font-display);
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-tertiary);
    margin-bottom: 0.4rem;
}

/* Record count */
.record-count {
    display: inline-block;
    background: var(--bg-input);
    border-radius: 100px;
    padding: 0.2rem 0.7rem;
    font-family: var(--font-body);
    font-size: 0.75rem;
    color: var(--text-tertiary);
    margin: 0.3rem 0 0.75rem;
}

/* Session info */
.session-info {
    background: var(--bg-input);
    border-radius: var(--r-md);
    padding: 1rem 1.2rem;
    font-family: var(--font-body);
    font-size: 0.82rem;
    color: var(--text-secondary);
}
.session-key {
    font-family: var(--font-display);
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-tertiary);
}
.session-val { color: var(--text-primary); font-weight: 500; }

/* Empty state */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text-tertiary);
}
.empty-state-icon { font-size: 2.5rem; margin-bottom: 0.75rem; opacity: 0.4; }
.empty-state-text {
    font-family: var(--font-body);
    font-size: 0.875rem;
    line-height: 1.6;
    color: var(--text-tertiary);
}

/* Misc */
hr { border-color: var(--border) !important; margin: 0.25rem 0 !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.12); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.2); }
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

def _sec(label: str) -> None:
    st.markdown(f'<div class="sec-lbl">{label}</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# HEADER — Apple style: white bar, minimal, title left, status right
# ═════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="
    background:var(--bg-card);
    border-bottom:1px solid var(--border);
    padding:1.5rem 2.5rem 1.25rem;
    margin:0 -2.5rem 2rem -2.5rem;
    display:flex;align-items:center;justify-content:space-between;
    box-shadow:0 1px 0 rgba(0,0,0,0.04);
">
  <div style="display:flex;align-items:center;gap:1rem">
    <div style="width:40px;height:40px;background:var(--orange);border-radius:10px;
                display:flex;align-items:center;justify-content:center;font-size:1.2rem;
                box-shadow:0 2px 8px rgba(255,102,0,0.3)">🏗️</div>
    <div>
      <div style="font-family:var(--font-display);font-size:1.15rem;font-weight:700;
                  color:var(--text-primary);letter-spacing:-0.01em;line-height:1.2">
        AI Punchlist
      </div>
      <div style="font-family:var(--font-body);font-size:0.78rem;color:var(--text-tertiary);
                  letter-spacing:0.01em;margin-top:1px">
        Leighton Asia &nbsp;&middot;&nbsp; Smart Inspection Hub
      </div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:1rem">
    <div style="text-align:right">
      <div style="font-family:var(--font-display);font-size:0.68rem;font-weight:700;
                  text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary)">
        Powered by
      </div>
      <div style="font-family:var(--font-display);font-size:0.82rem;font-weight:600;
                  color:var(--text-secondary)">Gemini 2.0 Flash</div>
    </div>
    <div style="
        background:{'rgba(52,199,89,0.1)' if _GEMINI_OK else 'rgba(0,0,0,0.04)'};
        border:1px solid {'rgba(52,199,89,0.25)' if _GEMINI_OK else 'var(--border)'};
        border-radius:100px;padding:0.3rem 0.75rem;
        font-family:var(--font-display);font-size:0.68rem;font-weight:700;
        text-transform:uppercase;letter-spacing:0.08em;
        color:{'var(--green)' if _GEMINI_OK else 'var(--text-tertiary)'};
        display:flex;align-items:center;gap:0.4rem;
    ">
      <span style="width:6px;height:6px;border-radius:50%;
                   background:{'var(--green)' if _GEMINI_OK else 'var(--text-tertiary)'}"></span>
      {'API Connected' if _GEMINI_OK else 'No API Key'}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL KPI STRIP — white cards with colour accent bars + hover elevation
# ═════════════════════════════════════════════════════════════════════════════
df_all  = st.session_state.defects
total   = len(df_all)
high_c  = int((df_all["Priority"] == "High").sum())   if total else 0
med_c   = int((df_all["Priority"] == "Medium").sum()) if total else 0
low_c   = int((df_all["Priority"] == "Low").sum())    if total else 0
open_c  = int((df_all["Status"]   == "Open").sum())   if total else 0
q_count = len(st.session_state.offline_queue)

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-accent" style="background:var(--orange)"></div>
    <div class="kpi-val">{total}</div>
    <div class="kpi-lbl">Total Defects</div>
    <div class="kpi-sub">all time</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-accent" style="background:var(--red)"></div>
    <div class="kpi-val" style="color:var(--red)">{high_c}</div>
    <div class="kpi-lbl">High Priority</div>
    <div class="kpi-sub">require urgent action</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-accent" style="background:var(--amber)"></div>
    <div class="kpi-val" style="color:var(--amber)">{med_c}</div>
    <div class="kpi-lbl">Medium Priority</div>
    <div class="kpi-sub">within 7 days</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-accent" style="background:var(--green)"></div>
    <div class="kpi-val" style="color:var(--green)">{low_c}</div>
    <div class="kpi-lbl">Low Priority</div>
    <div class="kpi-sub">within 14 days</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-accent" style="background:{'var(--amber)' if q_count>0 else 'var(--blue)'}"></div>
    <div class="kpi-val" style="color:{'var(--amber)' if q_count>0 else 'var(--text-primary)'}">
      {q_count}
    </div>
    <div class="kpi-lbl">Offline Queue</div>
    <div class="kpi-sub">{'pending sync' if q_count>0 else 'all synced'}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TABS — underline style
# ═════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📸  Field Capture",
    "📋  Live Punchlist",
    "📊  Dashboard",
    "⚙️  Office Sync",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — FIELD CAPTURE
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    cap_col, form_col = st.columns([1, 1.1], gap="large")

    with cap_col:
        _sec("Connectivity")
        connectivity = st.radio(
            "connectivity",
            ["🟢 Live AI Mode (5G/Wi-Fi)", "🟡 Offline Mode (No Signal)"],
            label_visibility="collapsed",
        )
        is_live = connectivity.startswith("🟢")

        _sec("Site Photo")
        img_src = st.radio("img_src", ["Camera", "Upload File"],
                           horizontal=True, label_visibility="collapsed")

        captured_image = None
        if img_src == "Camera":
            captured_image = st.camera_input("Take a photo", label_visibility="collapsed")
        else:
            captured_image = st.file_uploader(
                "Upload image", type=["jpg","jpeg","png","webp"],
                label_visibility="collapsed",
            )

        img_bytes = None
        if captured_image is not None:
            img_bytes = (captured_image.read()
                         if hasattr(captured_image, "read")
                         else captured_image.getvalue())
            try:
                st.image(Image.open(io.BytesIO(img_bytes)), use_container_width=True)
            except Exception:
                pass

        if img_bytes is not None:
            if is_live:
                if st.button("Analyze with Vision AI", type="primary",
                             use_container_width=True):
                    with st.spinner("Analyzing with Gemini Vision…"):
                        st.session_state.ai_suggestion = gemini_analyze_image(img_bytes)

                if st.session_state.ai_suggestion:
                    s      = st.session_state.ai_suggestion
                    p_pill = _priority_pill(s.get("priority", "Medium"))
                    st.markdown(f"""
<div class="ai-card">
  <div class="ai-card-header">
    <div style="width:28px;height:28px;background:var(--orange-soft);border-radius:8px;
                display:flex;align-items:center;justify-content:center;font-size:0.9rem">🤖</div>
    <div class="ai-card-title">AI Analysis</div>
    <div style="margin-left:auto">{p_pill}</div>
  </div>
  <div class="ai-grid">
    <div class="ai-field">
      <div class="ai-lbl">Defect Type</div>
      <div class="ai-val">{s.get('defect_type','—')}</div>
    </div>
    <div class="ai-field">
      <div class="ai-lbl">Trade</div>
      <div class="ai-val">{s.get('trade','—')}</div>
    </div>
    <div class="ai-field" style="grid-column:span 2">
      <div class="ai-lbl">Subcontractor</div>
      <div class="ai-val">{s.get('subcontractor_hint','—')}</div>
    </div>
  </div>
  <div class="ai-full">
    <div class="ai-lbl">Reasoning</div>
    <div class="ai-val">{s.get('reasoning','—')}</div>
  </div>
  <div class="ai-full" style="margin-top:8px">
    <div class="ai-lbl">Repair Method</div>
    <div class="ai-val">{s.get('repair_method','—')}</div>
  </div>
</div>
""", unsafe_allow_html=True)
            else:
                if st.button("Save to Offline Queue", type="primary",
                             use_container_width=True):
                    st.session_state.offline_queue.append({
                        "timestamp":   datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "image_bytes": img_bytes,
                        "size_kb":     round(len(img_bytes)/1024, 1),
                    })
                    st.success(
                        f"Saved. Queue: {len(st.session_state.offline_queue)} item(s)"
                    )

        _sec("Voice Notes")
        audio_input  = st.audio_input("Record voice note", label_visibility="collapsed")
        translate_cb = st.checkbox("Translate to English", value=False)

        if audio_input is not None:
            audio_bytes = (audio_input.read()
                           if hasattr(audio_input, "read")
                           else audio_input.getvalue())
            if st.button("Transcribe", use_container_width=True):
                with st.spinner("Transcribing…"):
                    st.session_state.v_text = gemini_transcribe(
                        audio_bytes, translate=translate_cb
                    )

        if st.session_state.v_text:
            st.markdown(f"""
<div class="transcript-box">
  <div class="transcript-label">Transcript</div>
  {st.session_state.v_text}
</div>
""", unsafe_allow_html=True)

    with form_col:
        _sec("Review & Assign")

        if not is_live:
            st.markdown("""
<div class="info-card">
  <strong>Offline Mode Active</strong><br>
  The assignment form is unavailable without connectivity.
  Use the queue button on the left to save captures locally,
  then sync via the Office Sync tab once signal is restored.
</div>
""", unsafe_allow_html=True)
        else:
            ai             = st.session_state.ai_suggestion
            _defect_types  = [
                "Honeycombing","Surface Cracking","Spalling","Rebar Exposure",
                "Formwork Misalignment","Cold Joint","Segregation",
                "Void Formation","Delamination","Cover Depth Deficiency","Other",
            ]
            _priorities     = ["High","Medium","Low"]
            _statuses       = ["Open","Draft","Closed"]
            _subcontractors = ["Apex Concrete Works","BuildRight Formwork","SteelCore Rebar"]

            def _safe_idx(lst, val, default=0):
                try: return lst.index(val)
                except ValueError: return default

            defect_idx   = _safe_idx(_defect_types,  ai.get("defect_type",""))
            priority_idx = _safe_idx(_priorities,     ai.get("priority","Medium"), 1)
            sub_idx      = _safe_idx(_subcontractors, ai.get("subcontractor_hint","Apex Concrete Works"))

            with st.form("assign_form", clear_on_submit=True):
                location_val = st.text_input(
                    "Location / Grid Reference",
                    placeholder="e.g. Level 3 — Grid F7, Column C12",
                )
                c1, c2 = st.columns(2)
                with c1: status_val   = st.selectbox("Status", _statuses)
                with c2: priority_val = st.selectbox("Priority", _priorities, index=priority_idx)
                defect_val = st.selectbox("Defect Type", _defect_types, index=defect_idx)
                sub_val    = st.selectbox("Subcontractor", _subcontractors, index=sub_idx)
                repair_val = st.text_area("Repair Method",
                                          value=ai.get("repair_method",""), height=80)
                notes_val  = st.text_area(
                    "Notes",
                    value=st.session_state.v_text,
                    placeholder="Voice transcript or additional notes…",
                    height=80,
                )
                submitted = st.form_submit_button(
                    "Log Defect to Punchlist",
                    type="primary", use_container_width=True,
                )
                if submitted:
                    if not location_val.strip():
                        st.error("Location is required.")
                    else:
                        due_date = (
                            datetime.date.today() +
                            datetime.timedelta(days=_sla_days(priority_val))
                        )
                        photo_id = ""
                        if img_bytes is not None:
                            photo_id = _next_id().replace("LA-","IMG-")
                            try:
                                pil = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                                buf = io.BytesIO()
                                pil.save(buf, format="JPEG", quality=85)
                                st.session_state.images[photo_id] = buf.getvalue()
                            except Exception:
                                st.session_state.images[photo_id] = img_bytes

                        new_id  = _next_id()
                        new_row = {
                            "ID": new_id,
                            "Timestamp":     datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Location":      location_val,
                            "Status":        status_val,
                            "Defect Type":   defect_val,
                            "Priority":      priority_val,
                            "Subcontractor": sub_val,
                            "Repair Method": repair_val,
                            "Notes":         notes_val,
                            "Due Date":      str(due_date),
                            "AI Reasoning":  ai.get("reasoning","Manual entry."),
                            "Photo ID":      photo_id,
                        }
                        st.session_state.defects = pd.concat(
                            [st.session_state.defects, pd.DataFrame([new_row])],
                            ignore_index=True,
                        )
                        st.session_state.ai_suggestion = {}
                        st.session_state.v_text        = ""
                        st.success(
                            f"✓  **{new_id}** logged — {defect_val} · "
                            f"{priority_val} Priority · Due {due_date}"
                        )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — LIVE PUNCHLIST
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    df = st.session_state.defects

    if df.empty:
        st.markdown("""
<div class="empty-state">
  <div class="empty-state-icon">📋</div>
  <div class="empty-state-text">
    No defects logged yet.<br>
    Start by capturing a site photo in the Field Capture tab.
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        fc1, fc2, _ = st.columns([1, 1, 2])
        with fc1: p_filter = st.selectbox("Priority", ["All","High","Medium","Low"])
        with fc2: s_filter = st.selectbox("Status",   ["All","Open","Draft","Closed"])

        disp = df.copy()
        if p_filter != "All": disp = disp[disp["Priority"] == p_filter]
        if s_filter != "All": disp = disp[disp["Status"]   == s_filter]

        st.markdown(
            f'<div class="record-count">{len(disp)} of {len(df)} records</div>',
            unsafe_allow_html=True,
        )

        def _style_p(val):
            c = {"High":"#FF3B30","Medium":"#FF9500","Low":"#34C759"}.get(val,"")
            return f"color:{c};font-weight:600" if c else ""

        def _style_s(val):
            c = {"Open":"#FF3B30","Draft":"#FF9500","Closed":"#34C759"}.get(val,"")
            return f"color:{c}" if c else ""

        st.dataframe(
            disp.style.applymap(_style_p, subset=["Priority"])
                      .applymap(_style_s, subset=["Status"]),
            use_container_width=True, height=420,
        )

        _sec("Export")
        st.download_button(
            label=f"Download ZIP — punchlist.csv + {len(st.session_state.images)} photo(s)",
            data=build_zip_export(),
            file_name=f"leighton_punchlist_{datetime.date.today()}.zip",
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
<div class="empty-state">
  <div class="empty-state-icon">📊</div>
  <div class="empty-state-text">
    Not enough data yet.<br>
    Log defects or load the demo dataset from the Office Sync tab.
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        ch1, ch2 = st.columns(2, gap="large")
        with ch1:
            _sec("Defects by Priority")
            pc = df["Priority"].value_counts().reset_index()
            pc.columns = ["Priority","Count"]
            pc["Priority"] = pd.Categorical(
                pc["Priority"], categories=["High","Medium","Low"], ordered=True
            )
            st.bar_chart(pc.sort_values("Priority").set_index("Priority"),
                         color="#FF6600", use_container_width=True, height=280)
        with ch2:
            _sec("Defects by Subcontractor")
            sc = df["Subcontractor"].value_counts().reset_index()
            sc.columns = ["Subcontractor","Count"]
            st.bar_chart(sc.set_index("Subcontractor"),
                         color="#1D1D1F", use_container_width=True, height=280)

        ch3, ch4 = st.columns(2, gap="large")
        with ch3:
            _sec("Defects by Type")
            tc = df["Defect Type"].value_counts().head(8).reset_index()
            tc.columns = ["Defect Type","Count"]
            st.bar_chart(tc.set_index("Defect Type"),
                         color="#E55A00", use_container_width=True, height=260)
        with ch4:
            _sec("Defects by Status")
            stc = df["Status"].value_counts().reset_index()
            stc.columns = ["Status","Count"]
            st.bar_chart(stc.set_index("Status"),
                         color="#6E6E73", use_container_width=True, height=260)

        _sec("Priority × Subcontractor Matrix")
        pivot = pd.crosstab(df["Subcontractor"], df["Priority"],
                            margins=True, margins_name="Total")
        cols_order = [c for c in ["High","Medium","Low","Total"] if c in pivot.columns]
        st.dataframe(pivot[cols_order], use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — OFFICE SYNC & DATA
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    sc1, sc2 = st.columns(2, gap="large")

    with sc1:
        _sec("Offline Queue")
        queue = st.session_state.offline_queue
        if queue:
            total_kb = sum(i.get("size_kb",0) for i in queue)
            st.markdown(f"""
<div class="queue-badge">
  <strong>{len(queue)} capture(s)</strong> pending sync
  &nbsp;&middot;&nbsp; {total_kb:.1f} KB total
</div>
""", unsafe_allow_html=True)
            st.dataframe(
                pd.DataFrame([
                    {"#": i+1, "Captured At": q["timestamp"],
                     "Size (KB)": q.get("size_kb","—")}
                    for i, q in enumerate(queue)
                ]),
                use_container_width=True, hide_index=True,
            )
            if st.button("Process Batch Sync", type="primary", use_container_width=True):
                with st.spinner("Syncing to project server…"):
                    import time; time.sleep(1.5)
                    st.session_state.offline_queue = []
                    st.success("Batch sync complete.")
                    st.rerun()
        else:
            st.markdown("""
<div class="empty-state" style="padding:2rem 1rem">
  <div class="empty-state-icon">✓</div>
  <div class="empty-state-text">Offline queue is empty</div>
</div>
""", unsafe_allow_html=True)

    with sc2:
        _sec("Demo Data")
        st.markdown("""
<div class="info-card" style="margin-bottom:1rem">
  Load <strong>60+ realistic defects</strong> across multiple subcontractors,
  priorities, and locations to showcase the Dashboard and Punchlist.
</div>
""", unsafe_allow_html=True)

        if st.button("Load Demo Dataset", type="primary", use_container_width=True):
            load_demo_data()
            st.success("Demo dataset loaded.")
            st.rerun()

        if not st.session_state.defects.empty:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            st.markdown("""
<div style="background:var(--red-soft);border:1px solid rgba(255,59,48,0.15);
            border-radius:var(--r-md);padding:0.85rem 1rem;font-size:0.82rem;
            color:#C0392B;line-height:1.5;margin-bottom:0.75rem">
  This will permanently clear all logged defects and images from this session.
</div>
""", unsafe_allow_html=True)
            if st.button("Clear All Data", use_container_width=True):
                st.session_state.defects        = pd.DataFrame(columns=DEFECT_COLS)
                st.session_state.images         = {}
                st.session_state.ai_suggestion  = {}
                st.session_state.v_text         = ""
                st.session_state.defect_counter = 1
                st.success("All data cleared.")
                st.rerun()

        _sec("Session")
        st.markdown(f"""
<div class="session-info">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem 1.5rem">
    <span class="session-key">Gemini API</span>
    <span class="session-val">{'Connected' if _GEMINI_OK else 'No key set'}</span>
    <span class="session-key">Total Defects</span>
    <span class="session-val">{len(st.session_state.defects)}</span>
    <span class="session-key">Photos Stored</span>
    <span class="session-val">{len(st.session_state.images)}</span>
    <span class="session-key">Offline Queue</span>
    <span class="session-val">{len(st.session_state.offline_queue)} item(s)</span>
    <span class="session-key">Session Date</span>
    <span class="session-val">{datetime.date.today().strftime('%d %b %Y')}</span>
  </div>
</div>
""", unsafe_allow_html=True)
