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
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500&display=swap');

:root {
    --bg:        #09090b;
    --surface:   #111113;
    --surface2:  #18181b;
    --surface3:  #1f1f23;
    --border:    rgba(255,255,255,0.06);
    --border2:   rgba(255,255,255,0.10);
    --text:      #fafafa;
    --text2:     #a1a1aa;
    --text3:     #52525b;
    --accent:    #ff6600;
    --accent-bg: rgba(255,102,0,0.10);
    --red:       #ef4444;
    --red-bg:    rgba(239,68,68,0.10);
    --amber:     #f59e0b;
    --amber-bg:  rgba(245,158,11,0.10);
    --green:     #22c55e;
    --green-bg:  rgba(34,197,94,0.10);
}

html, body, [class*="css"] {
    font-family: 'Geist', sans-serif !important;
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

/* ── Tabs ── */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 0 !important;
    gap: 0 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text3) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    padding: 0.7rem 1rem !important;
    border: none !important;
    border-bottom: 1.5px solid transparent !important;
    margin-bottom: -1px !important;
    transition: color 0.15s !important;
    text-transform: none !important;
    border-radius: 0 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    color: var(--text2) !important;
    background: transparent !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--text) !important;
    border-bottom-color: var(--text) !important;
    font-weight: 600 !important;
    background: transparent !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    background: transparent !important;
    border: none !important;
    padding: 1.75rem 0 0 !important;
}

/* ── Inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.15s !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-bg) !important;
}
div[data-testid="stSelectbox"] > div > div,
div[data-baseweb="select"] div {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.875rem !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] > label,
div[data-testid="stCheckbox"] label,
div[data-testid="stMultiSelect"] label {
    color: var(--text3) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}
div[data-testid="stRadio"] label span {
    font-size: 0.875rem !important;
    color: var(--text2) !important;
    font-family: 'Geist', sans-serif !important;
}

/* ── Buttons ── */
div[data-testid="stButton"] button[kind="primary"] {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 6px !important;
    color: #fff !important;
    font-family: 'Geist', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 0.55rem 1.1rem !important;
    transition: opacity 0.15s !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover { opacity: 0.88 !important; }

div[data-testid="stButton"] button[kind="secondary"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 6px !important;
    color: var(--text2) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.82rem !important;
    transition: border-color 0.15s, color 0.15s !important;
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
    border-color: var(--border2) !important;
    color: var(--text) !important;
}

div[data-testid="stForm"] button[kind="primaryFormSubmit"],
div[data-testid="stForm"] button[type="submit"] {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 6px !important;
    color: #fff !important;
    font-family: 'Geist', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: opacity 0.15s !important;
}
div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
div[data-testid="stForm"] button[type="submit"]:hover { opacity: 0.88 !important; }

div[data-testid="stDownloadButton"] button {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 6px !important;
    color: var(--text2) !important;
    font-family: 'Geist', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    transition: color 0.15s, border-color 0.15s !important;
}
div[data-testid="stDownloadButton"] button:hover {
    color: var(--text) !important;
    border-color: var(--border2) !important;
}

/* ── Form container ── */
div[data-testid="stForm"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1.25rem !important;
}

/* ── Alerts ── */
div[data-testid="stAlert"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.875rem !important;
    color: var(--text2) !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* ── File / Camera / Audio ── */
div[data-testid="stFileUploader"] section {
    background: var(--surface2) !important;
    border: 1px dashed var(--border2) !important;
    border-radius: 8px !important;
    transition: border-color 0.15s !important;
}
div[data-testid="stFileUploader"] section:hover { border-color: var(--accent) !important; }
div[data-testid="stFileUploader"] label,
div[data-testid="stCameraInput"] label,
div[data-testid="stAudioInput"] label { color: var(--text3) !important; }
div[data-testid="stCameraInput"] button {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 6px !important;
    color: var(--text2) !important;
}

/* ── Spinner / caption ── */
div[data-testid="stSpinner"] p {
    font-family: 'Geist', sans-serif !important;
    font-size: 0.82rem !important;
    color: var(--text3) !important;
}
div[data-testid="stCaptionContainer"] p {
    font-family: 'Geist Mono', monospace !important;
    font-size: 0.7rem !important;
    color: var(--text3) !important;
}

/* ── Custom components ── */

.section-label {
    font-family: 'Geist', sans-serif;
    font-size: 0.68rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text3);
    margin: 1.5rem 0 0.65rem;
    display: flex;
    align-items: center;
    gap: 0.65rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

.kpi-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;
    margin-bottom: 1.75rem;
}
.kpi {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.1rem;
}
.kpi-num {
    font-family: 'Geist', sans-serif;
    font-size: 1.7rem;
    font-weight: 600;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.kpi-label {
    font-family: 'Geist', sans-serif;
    font-size: 0.75rem;
    color: var(--text3);
    letter-spacing: 0.01em;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.1rem 1.2rem;
    margin-top: 0.6rem;
}
.card-label {
    font-family: 'Geist', sans-serif;
    font-size: 0.65rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text3);
    margin-bottom: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.card-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}
.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.field {
    background: var(--surface2);
    border-radius: 6px;
    padding: 0.6rem 0.8rem;
}
.field-label {
    font-family: 'Geist Mono', monospace;
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text3);
    margin-bottom: 0.2rem;
}
.field-value {
    font-family: 'Geist', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text);
    line-height: 1.4;
}
.field-full {
    background: var(--surface2);
    border-radius: 6px;
    padding: 0.6rem 0.8rem;
    margin-top: 8px;
}

.pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 0.18rem 0.55rem;
    border-radius: 4px;
    font-family: 'Geist', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
}
.pill-dot { width: 5px; height: 5px; border-radius: 50%; }
.pill-high   { background: var(--red-bg);   color: var(--red);   }
.pill-medium { background: var(--amber-bg); color: var(--amber); }
.pill-low    { background: var(--green-bg); color: var(--green); }

.transcript {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.75rem 0.9rem;
    margin-top: 0.5rem;
    font-family: 'Geist', sans-serif;
    font-size: 0.875rem;
    color: var(--text2);
    line-height: 1.6;
}

.offline-note {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-left: 2px solid var(--amber);
    border-radius: 0 6px 6px 0;
    padding: 0.9rem 1rem;
    font-family: 'Geist', sans-serif;
    font-size: 0.82rem;
    color: var(--text2);
    line-height: 1.65;
}

.queue-notice {
    background: var(--amber-bg);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 6px;
    padding: 0.75rem 0.9rem;
    font-family: 'Geist', sans-serif;
    font-size: 0.82rem;
    color: var(--amber);
    margin-bottom: 0.75rem;
}

.empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    color: var(--text3);
    font-family: 'Geist', sans-serif;
    font-size: 0.82rem;
    gap: 0.5rem;
}

.meta-grid {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.35rem 1.5rem;
    background: var(--surface2);
    border-radius: 6px;
    padding: 0.9rem 1rem;
}
.meta-key {
    font-family: 'Geist Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text3);
}
.meta-val {
    font-family: 'Geist', sans-serif;
    font-size: 0.82rem;
    color: var(--text2);
    font-weight: 500;
}

.desc-card {
    background: var(--surface2);
    border-radius: 6px;
    padding: 0.9rem 1rem;
    font-family: 'Geist', sans-serif;
    font-size: 0.82rem;
    color: var(--text2);
    line-height: 1.65;
    margin-bottom: 0.75rem;
}
.danger-notice {
    background: var(--red-bg);
    border: 1px solid rgba(239,68,68,0.15);
    border-radius: 6px;
    padding: 0.7rem 0.9rem;
    font-family: 'Geist', sans-serif;
    font-size: 0.78rem;
    color: #fca5a5;
    margin-bottom: 0.6rem;
}

hr { border-color: var(--border) !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-thumb { background: var(--surface3); border-radius: 2px; }
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



# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    border-bottom:1px solid var(--border);
    padding:1.25rem 2rem;
    margin:0 -2rem 1.75rem;
    display:flex;align-items:center;justify-content:space-between;
">
  <div style="display:flex;align-items:center;gap:0.75rem">
    <div style="
        width:32px;height:32px;background:var(--accent);
        border-radius:7px;display:flex;align-items:center;
        justify-content:center;font-size:1rem;flex-shrink:0
    ">🏗️</div>
    <div>
      <div style="font-family:'Geist',sans-serif;font-size:0.95rem;
                  font-weight:600;color:var(--text);letter-spacing:-0.01em">
        AI Punchlist
      </div>
      <div style="font-family:'Geist',sans-serif;font-size:0.72rem;
                  color:var(--text3);margin-top:1px">
        Leighton Asia · Smart Inspection Hub
      </div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:0.65rem">
    <div style="
        width:6px;height:6px;border-radius:50%;
        background:{'var(--green)' if _GEMINI_OK else 'var(--text3)'};
        flex-shrink:0
    "></div>
    <span style="
        font-family:'Geist',sans-serif;font-size:0.75rem;
        color:var(--text3);letter-spacing:0.01em
    ">
        {'Gemini Connected' if _GEMINI_OK else 'No API Key'}
    </span>
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
  <div class="kpi">
    <div class="kpi-num">{total}</div>
    <div class="kpi-label">Total Defects</div>
  </div>
  <div class="kpi">
    <div class="kpi-num" style="color:var(--red)">{high_c}</div>
    <div class="kpi-label">High Priority</div>
  </div>
  <div class="kpi">
    <div class="kpi-num" style="color:var(--amber)">{med_c}</div>
    <div class="kpi-label">Medium</div>
  </div>
  <div class="kpi">
    <div class="kpi-num" style="color:var(--green)">{low_c}</div>
    <div class="kpi-label">Low Priority</div>
  </div>
  <div class="kpi">
    <div class="kpi-num" style="color:{'var(--amber)' if q_count else 'var(--text3)'}">{q_count}</div>
    <div class="kpi-label">Offline Queue</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Field Capture", "Live Punchlist", "Dashboard", "Sync & Data"
])

def _sec(label):
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — FIELD CAPTURE
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    left, right = st.columns([1, 1.05], gap="large")

    with left:
        _sec("Connectivity")
        connectivity = st.radio(
            "con", ["🟢 Live AI Mode", "🟡 Offline Mode"],
            label_visibility="collapsed",
        )
        is_live = connectivity.startswith("🟢")

        _sec("Site Photo")
        src = st.radio("src", ["Camera", "Upload"], horizontal=True,
                       label_visibility="collapsed")

        captured = None
        if src == "Camera":
            captured = st.camera_input("", label_visibility="collapsed")
        else:
            captured = st.file_uploader("", type=["jpg","jpeg","png","webp"],
                                        label_visibility="collapsed")

        img_bytes = None
        if captured:
            img_bytes = (captured.read() if hasattr(captured, "read")
                         else captured.getvalue())
            try:
                st.image(Image.open(io.BytesIO(img_bytes)),
                         use_container_width=True)
            except Exception:
                pass

        if img_bytes:
            if is_live:
                if st.button("Analyze with AI", type="primary",
                             use_container_width=True):
                    with st.spinner("Analyzing…"):
                        st.session_state.ai_suggestion = gemini_analyze_image(img_bytes)

                if st.session_state.ai_suggestion:
                    s  = st.session_state.ai_suggestion
                    pp = _priority_pill(s.get("priority", "Medium"))
                    st.markdown(f"""
<div class="card">
  <div class="card-label">AI Analysis</div>
  <div class="field-grid">
    <div class="field">
      <div class="field-label">Defect Type</div>
      <div class="field-value">{s.get('defect_type','—')}</div>
    </div>
    <div class="field">
      <div class="field-label">Priority</div>
      <div class="field-value">{pp}</div>
    </div>
    <div class="field">
      <div class="field-label">Trade</div>
      <div class="field-value">{s.get('trade','—')}</div>
    </div>
    <div class="field">
      <div class="field-label">Subcontractor</div>
      <div class="field-value" style="font-size:0.8rem">{s.get('subcontractor_hint','—')}</div>
    </div>
  </div>
  <div class="field-full">
    <div class="field-label">Reasoning</div>
    <div class="field-value" style="font-size:0.82rem;color:var(--text2)">{s.get('reasoning','—')}</div>
  </div>
  <div class="field-full">
    <div class="field-label">Repair Method</div>
    <div class="field-value" style="font-size:0.82rem;color:var(--text2)">{s.get('repair_method','—')}</div>
  </div>
</div>
""", unsafe_allow_html=True)
            else:
                if st.button("Save to Queue", type="primary",
                             use_container_width=True):
                    st.session_state.offline_queue.append({
                        "timestamp":   datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "image_bytes": img_bytes,
                        "size_kb":     round(len(img_bytes)/1024, 1),
                    })
                    st.success(f"Saved — {len(st.session_state.offline_queue)} in queue")

        _sec("Voice Notes")
        audio = st.audio_input("", label_visibility="collapsed")
        translate = st.checkbox("Translate to English", value=False)
        if audio:
            ab = audio.read() if hasattr(audio, "read") else audio.getvalue()
            if st.button("Transcribe", use_container_width=True):
                with st.spinner("Transcribing…"):
                    st.session_state.v_text = gemini_transcribe(ab, translate)

        if st.session_state.v_text:
            st.markdown(f"""
<div class="transcript">
  <div style="font-family:'Geist Mono',monospace;font-size:0.6rem;
              text-transform:uppercase;letter-spacing:0.1em;
              color:var(--text3);margin-bottom:0.4rem">Transcript</div>
  {st.session_state.v_text}
</div>
""", unsafe_allow_html=True)

    with right:
        _sec("Review & Assign")

        if not is_live:
            st.markdown("""
<div class="offline-note">
  <strong style="color:var(--text)">Offline mode</strong> — form unavailable.<br>
  Queue captures on the left, then sync when signal is restored.
</div>
""", unsafe_allow_html=True)
        else:
            ai             = st.session_state.ai_suggestion
            _defects       = ["Honeycombing","Surface Cracking","Spalling","Rebar Exposure",
                               "Formwork Misalignment","Cold Joint","Segregation",
                               "Void Formation","Delamination","Cover Depth Deficiency","Other"]
            _priorities    = ["High","Medium","Low"]
            _statuses      = ["Open","Draft","Closed"]
            _subs          = ["Apex Concrete Works","BuildRight Formwork","SteelCore Rebar"]

            def _idx(lst, val, d=0):
                try: return lst.index(val)
                except ValueError: return d

            with st.form("form", clear_on_submit=True):
                location = st.text_input("Location / Grid Reference",
                                         placeholder="e.g. Level 3 — Grid F7")
                c1, c2 = st.columns(2)
                with c1: status   = st.selectbox("Status", _statuses)
                with c2: priority = st.selectbox("Priority", _priorities,
                                                 index=_idx(_priorities, ai.get("priority","Medium"), 1))
                defect_type = st.selectbox("Defect Type", _defects,
                                           index=_idx(_defects, ai.get("defect_type","")))
                sub         = st.selectbox("Subcontractor", _subs,
                                           index=_idx(_subs, ai.get("subcontractor_hint","")))
                repair      = st.text_area("Repair Method", value=ai.get("repair_method",""), height=76)
                notes       = st.text_area("Notes", value=st.session_state.v_text,
                                           placeholder="Additional notes…", height=76)
                submitted   = st.form_submit_button("Log Defect", type="primary",
                                                    use_container_width=True)

                if submitted:
                    if not location.strip():
                        st.error("Location is required.")
                    else:
                        due = datetime.date.today() + datetime.timedelta(days=_sla_days(priority))
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
                                "ID": nid, "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "Location": location, "Status": status, "Defect Type": defect_type,
                                "Priority": priority, "Subcontractor": sub,
                                "Repair Method": repair, "Notes": notes, "Due Date": str(due),
                                "AI Reasoning": ai.get("reasoning","Manual entry."),
                                "Photo ID": photo_id,
                            }])
                        ], ignore_index=True)
                        st.session_state.ai_suggestion = {}
                        st.session_state.v_text        = ""
                        st.success(f"{nid} logged — {defect_type} · {priority} · Due {due}")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — PUNCHLIST
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    df = st.session_state.defects
    if df.empty:
        st.markdown("""
<div class="empty">
  <span style="font-size:1.5rem;opacity:0.3">📋</span>
  No defects logged yet.
</div>
""", unsafe_allow_html=True)
    else:
        f1, f2, _ = st.columns([1, 1, 2])
        with f1: pf = st.selectbox("Priority", ["All","High","Medium","Low"])
        with f2: sf = st.selectbox("Status",   ["All","Open","Draft","Closed"])

        d = df.copy()
        if pf != "All": d = d[d["Priority"] == pf]
        if sf != "All": d = d[d["Status"]   == sf]

        st.caption(f"{len(d)} of {len(df)} records")

        def sp(v): c={"High":var_red,"Medium":var_amb,"Low":var_grn}.get(v,""); return f"color:{c};font-weight:500" if c else ""
        def ss(v): c={"Open":var_red,"Draft":var_amb,"Closed":var_grn}.get(v,""); return f"color:{c}" if c else ""

        var_red = "#ef4444"; var_amb = "#f59e0b"; var_grn = "#22c55e"

        st.dataframe(
            d.style.applymap(sp, subset=["Priority"]).applymap(ss, subset=["Status"]),
            use_container_width=True, height=400,
        )

        _sec("Export")
        st.download_button(
            f"Download ZIP — {len(st.session_state.images)} photo(s)",
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
<div class="empty">
  <span style="font-size:1.5rem;opacity:0.3">📊</span>
  No data yet — load the demo dataset from Sync &amp; Data.
</div>
""", unsafe_allow_html=True)
    else:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            _sec("By Priority")
            pc = df["Priority"].value_counts().reset_index()
            pc.columns = ["Priority","Count"]
            pc["Priority"] = pd.Categorical(pc["Priority"],
                                            categories=["High","Medium","Low"], ordered=True)
            st.bar_chart(pc.sort_values("Priority").set_index("Priority"),
                         color="#ff6600", height=240, use_container_width=True)
        with c2:
            _sec("By Subcontractor")
            sc = df["Subcontractor"].value_counts().reset_index()
            sc.columns = ["Subcontractor","Count"]
            st.bar_chart(sc.set_index("Subcontractor"),
                         color="#52525b", height=240, use_container_width=True)

        c3, c4 = st.columns(2, gap="large")
        with c3:
            _sec("By Defect Type")
            tc = df["Defect Type"].value_counts().head(8).reset_index()
            tc.columns = ["Defect Type","Count"]
            st.bar_chart(tc.set_index("Defect Type"),
                         color="#a1a1aa", height=240, use_container_width=True)
        with c4:
            _sec("By Status")
            stc = df["Status"].value_counts().reset_index()
            stc.columns = ["Status","Count"]
            st.bar_chart(stc.set_index("Status"),
                         color="#3f3f46", height=240, use_container_width=True)

        _sec("Priority × Subcontractor")
        pivot = pd.crosstab(df["Subcontractor"], df["Priority"],
                            margins=True, margins_name="Total")
        cols  = [c for c in ["High","Medium","Low","Total"] if c in pivot.columns]
        st.dataframe(pivot[cols], use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — SYNC & DATA
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    s1, s2 = st.columns(2, gap="large")

    with s1:
        _sec("Offline Queue")
        q = st.session_state.offline_queue
        if q:
            kb = sum(i.get("size_kb",0) for i in q)
            st.markdown(f"""
<div class="queue-notice">
  {len(q)} capture(s) pending &nbsp;·&nbsp; {kb:.1f} KB
</div>
""", unsafe_allow_html=True)
            st.dataframe(
                pd.DataFrame([{"#":i+1,"Captured At":x["timestamp"],
                                "KB":x.get("size_kb","—")}
                               for i,x in enumerate(q)]),
                use_container_width=True, hide_index=True,
            )
            if st.button("Sync Now", type="primary", use_container_width=True):
                with st.spinner("Syncing…"):
                    import time; time.sleep(1.5)
                    st.session_state.offline_queue = []
                    st.success("Sync complete.")
                    st.rerun()
        else:
            st.markdown("""
<div class="empty" style="padding:2rem">
  <span style="font-size:1.2rem;opacity:0.3">✓</span>
  Queue is empty
</div>
""", unsafe_allow_html=True)

    with s2:
        _sec("Data")
        st.markdown("""
<div class="desc-card">
  Load <b style="color:var(--text)">61 realistic defects</b> to demo the dashboard
  and punchlist features.
</div>
""", unsafe_allow_html=True)

        if st.button("Load Demo Dataset", type="primary", use_container_width=True):
            load_demo_data()
            st.success("Dataset loaded.")
            st.rerun()

        if not st.session_state.defects.empty:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            st.markdown("""
<div class="danger-notice">
  This clears all defects and images from this session.
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
<div class="meta-grid">
  <span class="meta-key">Gemini</span>
  <span class="meta-val">{'Connected' if _GEMINI_OK else 'No key'}</span>
  <span class="meta-key">Defects</span>
  <span class="meta-val">{len(st.session_state.defects)}</span>
  <span class="meta-key">Photos</span>
  <span class="meta-val">{len(st.session_state.images)}</span>
  <span class="meta-key">Queue</span>
  <span class="meta-val">{len(st.session_state.offline_queue)}</span>
  <span class="meta-key">Date</span>
  <span class="meta-val">{datetime.date.today().strftime('%d %b %Y')}</span>
</div>
""", unsafe_allow_html=True)
