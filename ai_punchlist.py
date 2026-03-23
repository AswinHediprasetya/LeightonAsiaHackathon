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
/* Instrument Sans only. No serif. No fallback clutter. */
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:root {
  --void:  #0c0c0e;
  --s1:    #111115;
  --s2:    #17171d;
  --line:  rgba(255,255,255,0.06);
  --line2: rgba(255,255,255,0.10);

  --t1:    #eeede6;
  --t2:    #6e6e7c;
  --t3:    #38383f;

  --fire:  #ff5c00;
  --fire2: #ff8040;
  --fdim:  rgba(255,92,0,0.10);
  --fglow: rgba(255,92,0,0.22);

  --red:   #e04040;
  --amber: #e89030;
  --green: #28b868;

  --rdim:  rgba(224,64,64,0.10);
  --adim:  rgba(232,144,48,0.10);
  --gdim:  rgba(40,184,104,0.10);

  --r:  6px;
  --r2: 10px;
  --r3: 14px;

  --sans: 'Instrument Sans', sans-serif;
  --mono: 'DM Mono', monospace;

  --sh1: 0 1px 2px rgba(0,0,0,0.35), 0 0 0 1px rgba(255,255,255,0.04);
  --sh2: 0 4px 16px rgba(0,0,0,0.45), 0 0 0 1px rgba(255,255,255,0.06);
}

html, body, [class*="css"] {
  font-family: var(--sans) !important;
  background: var(--void) !important;
  color: var(--t1) !important;
  -webkit-font-smoothing: antialiased !important;
}
.block-container {
  padding: 0 2.25rem 8rem !important;
  max-width: 1160px !important;
}
#MainMenu, header, footer,
div[data-testid="stDecoration"] { display: none !important; }

@keyframes up {
  from { opacity:0; transform:translateY(8px); }
  to   { opacity:1; transform:translateY(0); }
}
.block-container { animation: up 0.4s cubic-bezier(0.22,1,0.36,1) both; }

/* Tabs */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--line) !important;
  padding: 0 !important; gap: 0 !important; border-radius: 0 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent !important; border-radius: 0 !important;
  color: var(--t3) !important;
  font-family: var(--sans) !important; font-size: 0.78rem !important;
  font-weight: 500 !important; letter-spacing: 0.01em !important;
  padding: 0.65rem 1rem !important;
  border: none !important; border-bottom: 1.5px solid transparent !important;
  margin-bottom: -1px !important; transition: color 0.15s !important;
  text-transform: none !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
  color: var(--t2) !important; background: transparent !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--t1) !important; border-bottom-color: var(--fire) !important;
  font-weight: 600 !important; background: transparent !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-panel"] {
  background: transparent !important; border: none !important;
  padding: 1.75rem 0 0 !important;
}

/* Inputs */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
  background: var(--s2) !important; border: 1px solid var(--line2) !important;
  border-radius: var(--r) !important; color: var(--t1) !important;
  font-family: var(--sans) !important; font-size: 0.875rem !important;
  box-shadow: var(--sh1) !important;
  transition: border-color 0.15s, box-shadow 0.15s !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
  border-color: var(--fire) !important;
  box-shadow: 0 0 0 3px var(--fdim), var(--sh1) !important;
}
div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder { color: var(--t3) !important; }
div[data-testid="stSelectbox"] > div > div,
div[data-baseweb="select"] div {
  background: var(--s2) !important; border: 1px solid var(--line2) !important;
  border-radius: var(--r) !important; color: var(--t1) !important;
  font-family: var(--sans) !important; font-size: 0.875rem !important;
  box-shadow: var(--sh1) !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] > label,
div[data-testid="stCheckbox"] label {
  color: var(--t3) !important; font-family: var(--mono) !important;
  font-size: 0.62rem !important; font-weight: 500 !important;
  text-transform: uppercase !important; letter-spacing: 0.1em !important;
}
div[data-testid="stRadio"] label span {
  font-family: var(--sans) !important; font-size: 0.875rem !important;
  color: var(--t2) !important;
}

/* Primary button */
div[data-testid="stButton"] button[kind="primary"] {
  background: linear-gradient(135deg, var(--fire) 0%, var(--fire2) 100%) !important;
  border: none !important; border-radius: var(--r) !important; color: #fff !important;
  font-family: var(--sans) !important; font-weight: 600 !important;
  font-size: 0.8rem !important; letter-spacing: 0.02em !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,92,0,0.45) !important;
  transition: opacity 0.15s, transform 0.15s, box-shadow 0.15s !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
  opacity: 0.9 !important; transform: translateY(-1px) !important;
  box-shadow: 0 4px 16px var(--fglow), 0 0 0 1px rgba(255,92,0,0.6) !important;
}
div[data-testid="stButton"] button[kind="primary"]:active {
  transform: translateY(0) !important; opacity: 0.82 !important;
}
div[data-testid="stButton"] button[kind="secondary"] {
  background: var(--s2) !important; border: 1px solid var(--line2) !important;
  border-radius: var(--r) !important; color: var(--t2) !important;
  font-family: var(--sans) !important; font-size: 0.8rem !important;
  font-weight: 500 !important; box-shadow: var(--sh1) !important;
  transition: all 0.15s !important;
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
  color: var(--t1) !important; border-color: var(--line2) !important;
  box-shadow: var(--sh2) !important;
}
div[data-testid="stForm"] button[kind="primaryFormSubmit"],
div[data-testid="stForm"] button[type="submit"] {
  background: linear-gradient(135deg, var(--fire) 0%, var(--fire2) 100%) !important;
  border: none !important; border-radius: var(--r) !important; color: #fff !important;
  font-family: var(--sans) !important; font-weight: 600 !important;
  font-size: 0.875rem !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,92,0,0.45) !important;
  transition: opacity 0.15s, transform 0.15s !important;
}
div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
div[data-testid="stForm"] button[type="submit"]:hover {
  opacity: 0.9 !important; transform: translateY(-1px) !important;
}
div[data-testid="stDownloadButton"] button {
  background: var(--s2) !important; border: 1px solid var(--line2) !important;
  border-radius: var(--r) !important; color: var(--t2) !important;
  font-family: var(--sans) !important; font-weight: 500 !important;
  font-size: 0.8rem !important; box-shadow: var(--sh1) !important;
  transition: all 0.15s !important;
}
div[data-testid="stDownloadButton"] button:hover {
  border-color: var(--fire) !important; color: var(--fire2) !important;
}

/* Form */
div[data-testid="stForm"] {
  background: var(--s1) !important; border: 1px solid var(--line) !important;
  border-radius: var(--r3) !important; padding: 1.5rem !important;
  box-shadow: var(--sh1) !important;
}
div[data-testid="stAlert"] {
  background: var(--s2) !important; border: 1px solid var(--line2) !important;
  border-radius: var(--r2) !important; font-family: var(--sans) !important;
  font-size: 0.875rem !important; color: var(--t2) !important;
}
div[data-testid="stDataFrame"] {
  border: 1px solid var(--line) !important; border-radius: var(--r2) !important;
  overflow: hidden !important; box-shadow: var(--sh1) !important;
}
div[data-testid="stFileUploader"] section {
  background: var(--s2) !important; border: 1px dashed var(--line2) !important;
  border-radius: var(--r2) !important; transition: border-color 0.15s, background 0.15s !important;
}
div[data-testid="stFileUploader"] section:hover {
  border-color: var(--fire) !important; background: var(--fdim) !important;
}
div[data-testid="stFileUploader"] label,
div[data-testid="stCameraInput"] label,
div[data-testid="stAudioInput"] label { color: var(--t3) !important; }
div[data-testid="stCameraInput"] button {
  background: var(--s2) !important; border: 1px solid var(--line2) !important;
  border-radius: var(--r) !important; color: var(--t2) !important;
}
div[data-testid="stSpinner"] p {
  font-family: var(--mono) !important; font-size: 0.72rem !important;
  color: var(--t3) !important; letter-spacing: 0.06em !important;
}
div[data-testid="stCaptionContainer"] p {
  font-family: var(--mono) !important; font-size: 0.65rem !important;
  color: var(--t3) !important;
}
div[data-testid="stCheckbox"] label span {
  font-family: var(--sans) !important; font-size: 0.82rem !important;
  color: var(--t2) !important; text-transform: none !important; letter-spacing: 0 !important;
}

/* ── Custom components ── */

/* Row label — just text + line, no box */
.rl {
  font-family: var(--mono);
  font-size: 0.6rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--t3);
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin: 1.6rem 0 0.7rem;
}
.rl::after { content:''; flex:1; height:1px; background:var(--line); }

/* KPI strip — one seamless band */
.ks {
  display: grid;
  grid-template-columns: repeat(5,1fr);
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
  border-radius: var(--r3);
  overflow: hidden;
  margin-bottom: 2.25rem;
}
.kc {
  background: var(--s1);
  padding: 1.2rem 1.4rem;
  transition: background 0.15s;
}
.kc:hover { background: var(--s2); }
.kn {
  font-family: var(--sans);
  font-size: 2.1rem;
  font-weight: 700;
  letter-spacing: -0.05em;
  line-height: 1;
  margin-bottom: 0.3rem;
}
.kl {
  font-family: var(--mono);
  font-size: 0.6rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--t3);
}

/* Panel */
.pn {
  background: var(--s1);
  border: 1px solid var(--line);
  border-radius: var(--r3);
  padding: 1.2rem 1.35rem;
  margin-top: 0.5rem;
  box-shadow: var(--sh1);
}
.ph {
  display: flex; align-items: center; gap: 0.5rem;
  margin-bottom: 0.9rem;
  padding-bottom: 0.7rem;
  border-bottom: 1px solid var(--line);
}
.pt {
  font-family: var(--mono); font-size: 0.6rem;
  text-transform: uppercase; letter-spacing: 0.14em; color: var(--t3);
}

/* Data cells */
.dg { display:grid; grid-template-columns:1fr 1fr; gap:6px; }
.dc {
  background: var(--s2); border: 1px solid var(--line);
  border-radius: var(--r); padding: 0.6rem 0.8rem;
}
.dk { font-family:var(--mono); font-size:0.57rem; text-transform:uppercase;
      letter-spacing:0.12em; color:var(--t3); margin-bottom:0.2rem; }
.dv { font-family:var(--sans); font-size:0.875rem; font-weight:500;
      color:var(--t1); line-height:1.4; }
.df { background:var(--s2); border:1px solid var(--line); border-radius:var(--r);
      padding:0.6rem 0.8rem; margin-top:6px; }

/* Badge */
.bg {
  display:inline-flex; align-items:center; gap:4px;
  padding:0.15rem 0.5rem; border-radius:var(--r);
  font-family:var(--sans); font-size:0.7rem; font-weight:600;
}
.bd { width:5px; height:5px; border-radius:50%; flex-shrink:0; }
.bh { background:var(--rdim); color:#e06060; border:1px solid rgba(224,64,64,0.18); }
.bm { background:var(--adim); color:#d08840; border:1px solid rgba(232,144,48,0.18); }
.bl { background:var(--gdim); color:#40a870; border:1px solid rgba(40,184,104,0.18); }

/* Transcript */
.tx {
  background:var(--s2); border:1px solid var(--line2); border-radius:var(--r2);
  padding:0.85rem 1rem; margin-top:0.5rem;
  font-family:var(--sans); font-size:0.875rem; color:var(--t2); line-height:1.65;
}
.txl {
  font-family:var(--mono); font-size:0.57rem; text-transform:uppercase;
  letter-spacing:0.14em; color:var(--t3); margin-bottom:0.35rem;
}

/* Notices */
.nw {
  background:var(--adim); border:1px solid rgba(232,144,48,0.18);
  border-left:2px solid var(--amber); border-radius:0 var(--r2) var(--r2) 0;
  padding:0.85rem 1rem; font-family:var(--sans); font-size:0.82rem;
  color:#a87040; line-height:1.6;
}
.nd {
  background:var(--rdim); border:1px solid rgba(224,64,64,0.18);
  border-radius:var(--r); padding:0.65rem 0.85rem;
  font-family:var(--sans); font-size:0.78rem; color:#b06060;
  margin-bottom:0.6rem;
}
.nw strong, .nd strong { color:var(--t1); }

/* Queue notice */
.qn {
  background:var(--adim); border:1px solid rgba(232,144,48,0.18);
  border-radius:var(--r); padding:0.65rem 0.85rem; margin-bottom:0.75rem;
  font-family:var(--sans); font-size:0.78rem; color:#a87040;
}

/* Record count */
.rc {
  display:inline-block; background:var(--s2); border:1px solid var(--line);
  border-radius:20px; padding:0.14rem 0.55rem;
  font-family:var(--mono); font-size:0.65rem; color:var(--t3);
  margin:0.25rem 0 0.6rem;
}

/* Meta */
.mt {
  background:var(--s2); border:1px solid var(--line); border-radius:var(--r2);
  padding:0.9rem 1.1rem; display:grid;
  grid-template-columns:auto 1fr; gap:0.4rem 1.4rem; align-items:baseline;
}
.mk { font-family:var(--mono); font-size:0.6rem; text-transform:uppercase;
      letter-spacing:0.1em; color:var(--t3); }
.mv { font-family:var(--sans); font-size:0.82rem; font-weight:500; color:var(--t2); }

/* Empty */
.em {
  display:flex; flex-direction:column; align-items:center;
  justify-content:center; padding:5rem 2rem; gap:0.4rem;
  font-family:var(--mono); font-size:0.68rem; color:var(--t3);
  text-transform:uppercase; letter-spacing:0.1em;
}
.ei { font-size:1.4rem; opacity:0.12; margin-bottom:0.15rem; }

hr { border-color:var(--line) !important; }
::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-thumb { background:var(--s2); border-radius:2px; }
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
    st.markdown(f'<div class="rl">{label}</div>', unsafe_allow_html=True)

def _badge(p: str) -> str:
    m = {"High":("bh","#e04040"),"Medium":("bm","#e89030"),"Low":("bl","#28b868")}
    cls, dot = m.get(p, ("bm","#e89030"))
    return (f'<span class="bg {cls}"><span class="bd" style="background:{dot}"></span>'
            f'{p}</span>')

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
  border-bottom:1px solid var(--line);
  padding:1rem 2.25rem;
  margin:0 -2.25rem 2rem -2.25rem;
  display:flex;align-items:center;justify-content:space-between;
">
  <div style="display:flex;align-items:center;gap:0.8rem">
    <div style="
      width:32px;height:32px;
      background:linear-gradient(135deg,var(--fire),var(--fire2));
      border-radius:7px;display:flex;align-items:center;justify-content:center;
      font-size:0.95rem;flex-shrink:0;
      box-shadow:0 0 0 1px rgba(255,92,0,0.4),0 2px 8px var(--fglow);
    ">🏗️</div>
    <span style="font-family:var(--sans);font-size:0.9rem;font-weight:700;
                 color:var(--t1);letter-spacing:-0.01em">AI Punchlist</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.45rem;
              padding:0.22rem 0.65rem;
              background:{'var(--gdim)' if _GEMINI_OK else 'var(--s2)'};
              border:1px solid {'rgba(40,184,104,0.2)' if _GEMINI_OK else 'var(--line)'};
              border-radius:20px;font-family:var(--mono);font-size:0.6rem;
              font-weight:500;text-transform:uppercase;letter-spacing:0.1em;
              color:{'var(--green)' if _GEMINI_OK else 'var(--t3)'}">
    <span style="width:5px;height:5px;border-radius:50%;flex-shrink:0;
                 background:{'var(--green)' if _GEMINI_OK else 'var(--t3)'}"></span>
    {'live' if _GEMINI_OK else 'offline'}
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI strip ──────────────────────────────────────────────────────────────
df_all = st.session_state.defects
total  = len(df_all)
high_c = int((df_all["Priority"]=="High").sum())   if total else 0
med_c  = int((df_all["Priority"]=="Medium").sum()) if total else 0
low_c  = int((df_all["Priority"]=="Low").sum())    if total else 0
q_c    = len(st.session_state.offline_queue)

st.markdown(f"""
<div class="ks">
  <div class="kc"><div class="kn">{total}</div><div class="kl">Total</div></div>
  <div class="kc"><div class="kn" style="color:var(--red)">{high_c}</div><div class="kl">High</div></div>
  <div class="kc"><div class="kn" style="color:var(--amber)">{med_c}</div><div class="kl">Medium</div></div>
  <div class="kc"><div class="kn" style="color:var(--green)">{low_c}</div><div class="kl">Low</div></div>
  <div class="kc">
    <div class="kn" style="color:{'var(--amber)' if q_c else 'var(--t3)'}">{q_c}</div>
    <div class="kl">Queue</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Field Capture", "Punchlist", "Dashboard", "Sync"
])

# ─── TAB 1 ────────────────────────────────────────────────────────────────
with tab1:
    L, R = st.columns([1, 1.05], gap="large")

    with L:
        _sec("Connectivity")
        conn    = st.radio("conn",
                           ["🟢 Live — AI Mode", "🟡 Offline — No Signal"],
                           label_visibility="collapsed")
        is_live = conn.startswith("🟢")

        _sec("Site Photo")
        src = st.radio("src", ["Camera","Upload"],
                       horizontal=True, label_visibility="collapsed")
        cap = None
        if src == "Camera":
            cap = st.camera_input("", label_visibility="collapsed")
        else:
            cap = st.file_uploader("", type=["jpg","jpeg","png","webp"],
                                   label_visibility="collapsed")

        img = None
        if cap:
            img = cap.read() if hasattr(cap,"read") else cap.getvalue()
            try: st.image(Image.open(io.BytesIO(img)), use_container_width=True)
            except Exception: pass

        if img:
            if is_live:
                if st.button("Analyze with Vision AI",
                             type="primary", use_container_width=True):
                    with st.spinner("Analyzing…"):
                        st.session_state.ai_suggestion = gemini_analyze_image(img)

                if st.session_state.ai_suggestion:
                    s  = st.session_state.ai_suggestion
                    bp = _badge(s.get("priority","Medium"))
                    st.markdown(f"""
<div class="pn">
  <div class="ph">
    <span class="pt">AI Analysis</span>
    <span style="margin-left:auto">{bp}</span>
  </div>
  <div class="dg">
    <div class="dc"><div class="dk">Defect</div><div class="dv">{s.get('defect_type','—')}</div></div>
    <div class="dc"><div class="dk">Trade</div><div class="dv">{s.get('trade','—')}</div></div>
    <div class="dc" style="grid-column:span 2">
      <div class="dk">Subcontractor</div>
      <div class="dv">{s.get('subcontractor_hint','—')}</div>
    </div>
  </div>
  <div class="df"><div class="dk">Reasoning</div>
    <div class="dv" style="color:var(--t2);font-size:0.82rem">{s.get('reasoning','—')}</div></div>
  <div class="df"><div class="dk">Repair Method</div>
    <div class="dv" style="color:var(--t2);font-size:0.82rem">{s.get('repair_method','—')}</div></div>
</div>
""", unsafe_allow_html=True)
            else:
                if st.button("Save to Queue",
                             type="primary", use_container_width=True):
                    st.session_state.offline_queue.append({
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "image_bytes": img,
                        "size_kb": round(len(img)/1024, 1),
                    })
                    st.success(f"Saved — {len(st.session_state.offline_queue)} in queue")

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
<div class="tx">
  <div class="txl">Transcript</div>
  {st.session_state.v_text}
</div>
""", unsafe_allow_html=True)

    with R:
        _sec("Review & Assign")
        if not is_live:
            st.markdown("""
<div class="nw">
  <strong>Offline</strong> — form unavailable.
  Queue captures on the left and sync when signal is restored.
</div>
""", unsafe_allow_html=True)
        else:
            ai  = st.session_state.ai_suggestion
            _dt = ["Honeycombing","Surface Cracking","Spalling","Rebar Exposure",
                   "Formwork Misalignment","Cold Joint","Segregation",
                   "Void Formation","Delamination","Cover Depth Deficiency","Other"]
            _pr = ["High","Medium","Low"]
            _st = ["Open","Draft","Closed"]
            _sb = ["Apex Concrete Works","BuildRight Formwork","SteelCore Rebar"]

            def _i(lst,v,d=0):
                try: return lst.index(v)
                except ValueError: return d

            with st.form("f", clear_on_submit=True):
                loc  = st.text_input("Location / Grid Reference",
                                     placeholder="e.g. Level 3 — Grid F7")
                c1,c2 = st.columns(2)
                with c1: stat = st.selectbox("Status", _st)
                with c2: pri  = st.selectbox("Priority", _pr,
                                              index=_i(_pr,ai.get("priority","Medium"),1))
                dft  = st.selectbox("Defect Type",_dt,index=_i(_dt,ai.get("defect_type","")))
                sub  = st.selectbox("Subcontractor",_sb,index=_i(_sb,ai.get("subcontractor_hint","")))
                rep  = st.text_area("Repair Method",value=ai.get("repair_method",""),height=72)
                nts  = st.text_area("Notes",value=st.session_state.v_text,
                                    placeholder="Additional notes…",height=72)
                done = st.form_submit_button("Log Defect",type="primary",use_container_width=True)

                if done:
                    if not loc.strip():
                        st.error("Location required.")
                    else:
                        due = datetime.date.today() + datetime.timedelta(days=_sla_days(pri))
                        pid = ""
                        if img:
                            pid = _next_id().replace("LA-","IMG-")
                            try:
                                p = Image.open(io.BytesIO(img)).convert("RGB")
                                b = io.BytesIO(); p.save(b,format="JPEG",quality=85)
                                st.session_state.images[pid] = b.getvalue()
                            except Exception:
                                st.session_state.images[pid] = img
                        nid = _next_id()
                        st.session_state.defects = pd.concat([
                            st.session_state.defects,
                            pd.DataFrame([{
                                "ID":nid,
                                "Timestamp":datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "Location":loc,"Status":stat,"Defect Type":dft,
                                "Priority":pri,"Subcontractor":sub,"Repair Method":rep,
                                "Notes":nts,"Due Date":str(due),
                                "AI Reasoning":ai.get("reasoning","Manual entry."),
                                "Photo ID":pid,
                            }])
                        ],ignore_index=True)
                        st.session_state.ai_suggestion = {}
                        st.session_state.v_text = ""
                        st.success(f"{nid} — {dft} · {pri} · Due {due}")

# ─── TAB 2 ────────────────────────────────────────────────────────────────
with tab2:
    df = st.session_state.defects
    if df.empty:
        st.markdown('<div class="em"><div class="ei">📋</div>No defects logged</div>',
                    unsafe_allow_html=True)
    else:
        f1,f2,_ = st.columns([1,1,2])
        with f1: pf = st.selectbox("Priority",["All","High","Medium","Low"])
        with f2: sf = st.selectbox("Status",  ["All","Open","Draft","Closed"])
        d = df.copy()
        if pf!="All": d=d[d["Priority"]==pf]
        if sf!="All": d=d[d["Status"]==sf]
        st.markdown(f'<div class="rc">{len(d)} of {len(df)}</div>',unsafe_allow_html=True)
        R="#e04040";A="#e89030";G="#28b868"
        def sp(v): c={"High":R,"Medium":A,"Low":G}.get(v,""); return f"color:{c};font-weight:600" if c else ""
        def ss(v): c={"Open":R,"Draft":A,"Closed":G}.get(v,""); return f"color:{c}" if c else ""
        st.dataframe(d.style.applymap(sp,subset=["Priority"]).applymap(ss,subset=["Status"]),
                     use_container_width=True,height=400)
        _sec("Export")
        st.download_button(
            f"Download ZIP — {len(st.session_state.images)} photo(s)",
            data=build_zip_export(),
            file_name=f"leighton_{datetime.date.today()}.zip",
            mime="application/zip",use_container_width=True,
        )

# ─── TAB 3 ────────────────────────────────────────────────────────────────
with tab3:
    df = st.session_state.defects
    if df.empty or len(df)<2:
        st.markdown('<div class="em"><div class="ei">📊</div>Load demo data from Sync</div>',
                    unsafe_allow_html=True)
    else:
        c1,c2 = st.columns(2,gap="large")
        with c1:
            _sec("By Priority")
            pc = df["Priority"].value_counts().reset_index()
            pc.columns=["Priority","Count"]
            pc["Priority"]=pd.Categorical(pc["Priority"],categories=["High","Medium","Low"],ordered=True)
            st.bar_chart(pc.sort_values("Priority").set_index("Priority"),
                         color="#ff5c00",height=220,use_container_width=True)
        with c2:
            _sec("By Subcontractor")
            sc=df["Subcontractor"].value_counts().reset_index(); sc.columns=["Sub","Count"]
            st.bar_chart(sc.set_index("Sub"),color="#3d3d48",height=220,use_container_width=True)
        c3,c4=st.columns(2,gap="large")
        with c3:
            _sec("By Defect Type")
            tc=df["Defect Type"].value_counts().head(8).reset_index(); tc.columns=["Type","Count"]
            st.bar_chart(tc.set_index("Type"),color="#1c1c23",height=220,use_container_width=True)
        with c4:
            _sec("By Status")
            stc=df["Status"].value_counts().reset_index(); stc.columns=["Status","Count"]
            st.bar_chart(stc.set_index("Status"),color="#17171d",height=220,use_container_width=True)
        _sec("Matrix")
        pivot=pd.crosstab(df["Subcontractor"],df["Priority"],margins=True,margins_name="Total")
        cols=[c for c in ["High","Medium","Low","Total"] if c in pivot.columns]
        st.dataframe(pivot[cols],use_container_width=True)

# ─── TAB 4 ────────────────────────────────────────────────────────────────
with tab4:
    s1,s2 = st.columns(2,gap="large")

    with s1:
        _sec("Offline Queue")
        q = st.session_state.offline_queue
        if q:
            kb=sum(i.get("size_kb",0) for i in q)
            st.markdown(f'<div class="qn">{len(q)} pending · {kb:.1f} KB</div>',
                        unsafe_allow_html=True)
            st.dataframe(
                pd.DataFrame([{"#":i+1,"Captured":x["timestamp"],"KB":x.get("size_kb","—")}
                               for i,x in enumerate(q)]),
                use_container_width=True,hide_index=True)
            if st.button("Sync Now",type="primary",use_container_width=True):
                with st.spinner("Syncing…"):
                    import time; time.sleep(1.5)
                    st.session_state.offline_queue=[]
                    st.success("Complete.")
                    st.rerun()
        else:
            st.markdown('<div class="em" style="padding:2rem"><div class="ei">✓</div>Queue empty</div>',
                        unsafe_allow_html=True)

    with s2:
        _sec("Data")
        if st.button("Load Demo Dataset",type="primary",use_container_width=True):
            load_demo_data(); st.success("Loaded."); st.rerun()

        if not st.session_state.defects.empty:
            st.markdown("<div style='height:0.5rem'></div>",unsafe_allow_html=True)
            st.markdown('<div class="nd">Clears all defects and images from this session.</div>',
                        unsafe_allow_html=True)
            if st.button("Clear All Data",use_container_width=True):
                st.session_state.defects=pd.DataFrame(columns=DEFECT_COLS)
                st.session_state.images={}
                st.session_state.ai_suggestion={}
                st.session_state.v_text=""
                st.session_state.defect_counter=1
                st.success("Cleared."); st.rerun()

        _sec("Session")
        st.markdown(f"""
<div class="mt">
  <span class="mk">API</span><span class="mv">{'Connected' if _GEMINI_OK else 'No key'}</span>
  <span class="mk">Defects</span><span class="mv">{len(st.session_state.defects)}</span>
  <span class="mk">Photos</span><span class="mv">{len(st.session_state.images)}</span>
  <span class="mk">Queue</span><span class="mv">{len(st.session_state.offline_queue)}</span>
  <span class="mk">Date</span><span class="mv">{datetime.date.today().strftime('%d %b %Y')}</span>
</div>
""", unsafe_allow_html=True)
