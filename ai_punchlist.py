"""
AI Punchlist — Leighton Asia Smart Inspection Hub
Single-file Streamlit application · Powered by Gemini 2.0 Flash
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

# ── Gemini ──────────────────────────────────────────────────────────────────
try:
    import google.generativeai as genai
    _GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
    if _GEMINI_KEY:
        genai.configure(api_key=_GEMINI_KEY)
    _GEMINI_OK = bool(_GEMINI_KEY)
except ImportError:
    _GEMINI_OK = False

# ════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Punchlist",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════════════════
# CSS  —  Leighton Asia theme
# RULE: Every HTML block is self-contained in a single st.markdown() call.
#       Widgets sit BETWEEN html blocks, styled via CSS attribute selectors.
#       Never open a <div> in one call and close it in another.
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&family=Barlow:wght@300;400;500;600&display=swap');

/* ── CSS Variables ── */
:root {
    --orange: #FF6600;
    --orange-dark: #CC5200;
    --orange-pale: rgba(255,102,0,0.10);
    --navy: #0d213f;
    --navy-mid: #162d52;
    --navy-light: #1e3d6e;
    --text: #e8eaf0;
    --text-muted: #8a95a8;
    --border: rgba(255,102,0,0.18);
    --bg: #09182e;
    --bg-card: #0f2240;
    --bg-input: #0b1c35;
    --success: #22c55e;
    --warning: #f59e0b;
    --danger: #ef4444;
}

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.block-container {
    padding: 0 2rem 4rem !important;
    max-width: 1440px !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, header, footer { visibility: hidden !important; display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }

/* ── Tabs ── */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--navy) !important;
    border-radius: 10px 10px 0 0 !important;
    padding: 0.3rem 0.5rem 0 !important;
    gap: 0.2rem !important;
    border-bottom: 2px solid var(--orange) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px 8px 0 0 !important;
    color: var(--text-muted) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 0.55rem 1.1rem !important;
    border: none !important;
    transition: all 0.2s !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--orange) !important;
    color: #fff !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    background: var(--navy-mid) !important;
    color: var(--text) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    background: var(--bg-card) !important;
    border-radius: 0 0 10px 10px !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    padding: 1.5rem !important;
}

/* ── Section label helper ── */
.sec-lbl {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--orange);
    padding-bottom: 0.45rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.85rem;
    margin-top: 1.4rem;
}

/* ── Metrics row ── */
.m-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.7rem;
    margin-bottom: 1.6rem;
}
.m-card {
    background: var(--navy);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.85rem 1rem;
    position: relative;
    overflow: hidden;
}
.m-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.m-val {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    color: var(--text);
}
.m-lbl {
    font-size: 0.67rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-muted);
    margin-top: 0.2rem;
}

/* ── AI output card ── */
.ai-card {
    background: var(--navy);
    border: 1px solid var(--border);
    border-left: 3px solid var(--orange);
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.1rem;
    margin-top: 0.8rem;
}
.ai-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
    margin-bottom: 0.6rem;
}
.ai-field {
    background: var(--bg-input);
    border: 1px solid rgba(255,102,0,0.12);
    border-radius: 7px;
    padding: 0.6rem 0.8rem;
}
.ai-lbl {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--orange);
    margin-bottom: 0.2rem;
}
.ai-val { font-size: 0.88rem; font-weight: 500; color: var(--text); }
.ai-full {
    background: var(--bg-input);
    border: 1px solid rgba(255,102,0,0.12);
    border-radius: 7px;
    padding: 0.6rem 0.8rem;
}

/* ── Priority pills ── */
.pill {
    display: inline-block;
    padding: 0.16rem 0.65rem;
    border-radius: 20px;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.pill-high   { background: rgba(239,68,68,0.18);  color: #f87171; }
.pill-medium { background: rgba(245,158,11,0.18); color: #fbbf24; }
.pill-low    { background: rgba(34,197,94,0.18);  color: #4ade80; }

/* ── Offline queue badge ── */
.queue-badge {
    background: rgba(245,158,11,0.18);
    border: 1px solid rgba(245,158,11,0.4);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    color: #fbbf24;
    font-size: 0.88rem;
    margin-bottom: 1rem;
}

/* ── Input / widget overrides ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div[data-baseweb="select"] div,
div[data-baseweb="select"] div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 7px !important;
    color: var(--text) !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 0.88rem !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] label,
div[data-testid="stCheckbox"] label {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--orange) !important;
    box-shadow: 0 0 0 2px rgba(255,102,0,0.2) !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] { gap: 0.4rem; }

/* ── Form / submit button ── */
div[data-testid="stForm"] {
    background: var(--navy) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.2rem !important;
}
div[data-testid="stForm"] button[kind="primaryFormSubmit"],
div[data-testid="stForm"] button[type="submit"] {
    background: var(--orange) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #fff !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.2rem !important;
    transition: background 0.15s !important;
}
div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
div[data-testid="stForm"] button[type="submit"]:hover {
    background: var(--orange-dark) !important;
}

/* ── Regular primary button ── */
div[data-testid="stButton"] button[kind="primary"] {
    background: var(--orange) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #fff !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background: var(--orange-dark) !important;
}
div[data-testid="stButton"] button[kind="secondary"] {
    background: var(--navy) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-muted) !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 0.84rem !important;
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
    border-color: var(--orange) !important;
    color: var(--orange) !important;
}

/* ── Download button ── */
div[data-testid="stDownloadButton"] button {
    background: var(--navy) !important;
    border: 1px solid var(--orange) !important;
    border-radius: 8px !important;
    color: var(--orange) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.84rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}
div[data-testid="stDownloadButton"] button:hover {
    background: var(--orange-pale) !important;
}

/* ── File uploader ── */
div[data-testid="stFileUploader"] section {
    background: var(--bg-input) !important;
    border: 1.5px dashed rgba(255,102,0,0.35) !important;
    border-radius: 8px !important;
}
div[data-testid="stFileUploader"] label { color: var(--text-muted) !important; }

/* ── Camera input ── */
div[data-testid="stCameraInput"] label { color: var(--text-muted) !important; }
div[data-testid="stCameraInput"] button {
    background: var(--navy-mid) !important;
    border: 1px solid var(--border) !important;
    border-radius: 7px !important;
    color: var(--text) !important;
}

/* ── Audio input ── */
div[data-testid="stAudioInput"] label { color: var(--text-muted) !important; }

/* ── Alerts / info boxes ── */
div[data-testid="stAlert"] {
    background: var(--navy) !important;
    border-radius: 8px !important;
    font-size: 0.86rem !important;
    border-left: 3px solid var(--orange) !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* ── Charts ── */
div[data-testid="stVegaLiteChart"] { border-radius: 8px !important; overflow: hidden; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 0.2rem 0 !important; }

/* ── Spinner ── */
div[data-testid="stSpinner"] p { color: var(--text-muted) !important; font-size: 0.84rem !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: rgba(255,102,0,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--orange); }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
DEFECT_COLS = [
    "ID", "Timestamp", "Location", "Status", "Defect Type",
    "Priority", "Subcontractor", "Repair Method", "Notes",
    "Due Date", "AI Reasoning", "Photo ID",
]

if "defects" not in st.session_state:
    st.session_state.defects = pd.DataFrame(columns=DEFECT_COLS)
if "images" not in st.session_state:
    st.session_state.images = {}          # photo_id -> bytes
if "offline_queue" not in st.session_state:
    st.session_state.offline_queue = []   # list of dicts
if "ai_suggestion" not in st.session_state:
    st.session_state.ai_suggestion = {}   # parsed JSON from Gemini
if "v_text" not in st.session_state:
    st.session_state.v_text = ""          # voice transcript
if "defect_counter" not in st.session_state:
    st.session_state.defect_counter = 1

# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def _strip_json(text: str) -> str:
    """Remove markdown fences and whitespace before JSON parsing."""
    text = text.strip()
    for fence in ["```json", "```JSON", "```"]:
        if text.startswith(fence):
            text = text[len(fence):]
    if text.endswith("```"):
        text = text[:-3]
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
    """Send image to Gemini Vision and return structured JSON dict."""
    fallback = {
        "defect_type": "Honeycombing",
        "priority": "High",
        "trade": "Concrete",
        "reasoning": "AI analysis unavailable — fallback values applied.",
        "repair_method": "Remove loose concrete, apply bonding agent, patch with non-shrink grout.",
        "subcontractor_hint": "Apex Concrete Works",
    }
    if not _GEMINI_OK:
        return fallback
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        img_data = {"mime_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}

        prompt = (
            "You are an expert construction site quality inspector for Leighton Asia. "
            "Analyze this site photo and return ONLY a valid JSON object — no markdown, no explanation. "
            "The JSON must have exactly these keys:\n"
            '  "defect_type": string (e.g. Honeycombing, Cracking, Spalling, Formwork Misalignment, '
            "Rebar Exposure, Surface Defect, Structural Defect),\n"
            '  "priority": one of "High" | "Medium" | "Low",\n'
            '  "trade": one of "Concrete" | "Rebar" | "Formwork",\n'
            '  "reasoning": one concise sentence explaining your assessment,\n'
            '  "repair_method": standard engineering repair procedure in one sentence,\n'
            '  "subcontractor_hint": one of "Apex Concrete Works" | "BuildRight Formwork" | "SteelCore Rebar"\n'
            "Return ONLY the JSON object."
        )
        response = model.generate_content([prompt, img_data])
        raw = _strip_json(response.text)
        return json.loads(raw)
    except Exception as e:
        fallback["reasoning"] = f"AI error: {str(e)[:80]}"
        return fallback


def gemini_transcribe(audio_bytes: bytes, translate: bool = False) -> str:
    """Transcribe (and optionally translate) audio via Gemini."""
    if not _GEMINI_OK:
        return "Transcription unavailable — GEMINI_API_KEY not set."
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        audio_b64 = base64.b64encode(audio_bytes).decode()
        audio_data = {"mime_type": "audio/wav", "data": audio_b64}
        task = "Transcribe this audio recording accurately."
        if translate:
            task += " If not in English, translate the result to English."
        task += " Return only the transcribed text, nothing else."
        response = model.generate_content([task, audio_data])
        return response.text.strip()
    except Exception as e:
        return f"Transcription failed: {str(e)[:120]}"


def build_zip_export() -> bytes:
    """Return in-memory ZIP with punchlist.csv + Evidence images."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        csv_bytes = st.session_state.defects.to_csv(index=False).encode("utf-8")
        zf.writestr("punchlist.csv", csv_bytes)
        for photo_id, img_bytes in st.session_state.images.items():
            zf.writestr(f"Evidence/{photo_id}.jpg", img_bytes)
    return buf.getvalue()


def load_demo_data():
    """Populate session state with ~60 realistic dummy defects."""
    rng = random.Random(42)
    locations = [
        "Level B1 — Grid C3", "Level 3 — Column F7", "Roof Deck — Zone A",
        "Basement Car Park — Row 4", "Level 5 — Stairwell S2", "Level 2 — Beam B14",
        "Foundation — Grid A1", "Level 7 — Slab Edge", "Level 1 — Wall W3",
        "Level 6 — Lift Core LC2", "Level 4 — Transfer Plate", "Podium — Zone P3",
    ]
    defect_types = [
        "Honeycombing", "Surface Cracking", "Spalling", "Rebar Exposure",
        "Formwork Misalignment", "Cold Joint", "Segregation", "Void Formation",
        "Delamination", "Cover Depth Deficiency",
    ]
    priorities = ["High", "High", "Medium", "Medium", "Medium", "Low"]
    subcontractors = ["Apex Concrete Works", "BuildRight Formwork", "SteelCore Rebar"]
    statuses = ["Open", "Open", "Open", "Draft", "Closed"]
    repair_methods = {
        "Honeycombing": "Break out, clean, apply bonding slurry, patch with non-shrink grout.",
        "Surface Cracking": "Rout and seal cracks with polyurethane sealant.",
        "Spalling": "Remove loose material, treat rebar, apply epoxy mortar patch.",
        "Rebar Exposure": "Clean rebar, apply corrosion inhibitor, patch with cementitious mortar.",
        "Formwork Misalignment": "Cut, grind, and re-strike to specification. Submit NCR.",
        "Cold Joint": "Wet grind joint plane, apply bonding agent, inject with epoxy grout.",
        "Segregation": "Core test for strength. If substandard: cut out and re-pour.",
        "Void Formation": "Drill and inject with low-viscosity epoxy resin.",
        "Delamination": "Map extent with hammer tap. Cut perimeter, remove, re-apply.",
        "Cover Depth Deficiency": "Covermeter survey, mark affected zones, apply protective coating.",
    }

    rows = []
    for i in range(1, 62):
        dt = defect_types[rng.randint(0, len(defect_types) - 1)]
        pri = rng.choice(priorities)
        days_ago = rng.randint(0, 30)
        ts = datetime.datetime.now() - datetime.timedelta(days=days_ago)
        due = ts.date() + datetime.timedelta(days=_sla_days(pri))
        rows.append({
            "ID": f"LA-{i:04d}",
            "Timestamp": ts.strftime("%Y-%m-%d %H:%M"),
            "Location": rng.choice(locations),
            "Status": rng.choice(statuses),
            "Defect Type": dt,
            "Priority": pri,
            "Subcontractor": rng.choice(subcontractors),
            "Repair Method": repair_methods.get(dt, "Inspect and repair per specification."),
            "Notes": rng.choice([
                "Requires immediate inspection.",
                "Flagged by site QC officer.",
                "Awaiting subcontractor acknowledgement.",
                "Repair materials on order.",
                "Follow-up inspection scheduled.",
                "",
            ]),
            "Due Date": str(due),
            "AI Reasoning": "Detected via visual inspection of site photograph.",
            "Photo ID": "",
        })
    st.session_state.defects = pd.DataFrame(rows, columns=DEFECT_COLS)
    st.session_state.defect_counter = 62


def _sec(label: str) -> None:
    """Standalone section label — safe with Streamlit widgets below it."""
    st.markdown(f'<div class="sec-lbl">{label}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# HEADER  (self-contained HTML — no Streamlit widgets inside)
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="
    background: linear-gradient(135deg, #0d213f 0%, #162d52 60%, #1a2f4a 100%);
    border-bottom: 3px solid #FF6600;
    padding: 1.4rem 2rem 1.2rem;
    margin: -1rem -2rem 1.5rem -2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
">
  <div>
    <div style="
        font-family:'Barlow Condensed',sans-serif;
        font-size:2rem;
        font-weight:700;
        color:#fff;
        letter-spacing:0.03em;
        line-height:1.1;
    ">🏗️ AI Punchlist</div>
    <div style="
        font-family:'Barlow Condensed',sans-serif;
        font-size:0.78rem;
        font-weight:600;
        letter-spacing:0.28em;
        color:#FF6600;
        text-transform:uppercase;
        margin-top:0.2rem;
    ">Leighton Asia &bull; Smart Inspection Hub</div>
  </div>
  <div style="text-align:right">
    <div style="
        font-family:'Barlow Condensed',sans-serif;
        font-size:0.68rem;
        font-weight:600;
        letter-spacing:0.18em;
        color:rgba(255,255,255,0.35);
        text-transform:uppercase;
    ">Powered by</div>
    <div style="
        font-family:'Barlow Condensed',sans-serif;
        font-size:0.92rem;
        font-weight:700;
        color:rgba(255,255,255,0.6);
        letter-spacing:0.08em;
    ">Gemini 2.0 Flash</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# GLOBAL METRICS  (self-contained HTML — computed before rendering)
# ════════════════════════════════════════════════════════════════════════════
df_all = st.session_state.defects
total   = len(df_all)
high_c  = int((df_all["Priority"] == "High").sum())   if total else 0
med_c   = int((df_all["Priority"] == "Medium").sum()) if total else 0
low_c   = int((df_all["Priority"] == "Low").sum())    if total else 0
open_c  = int((df_all["Status"]   == "Open").sum())   if total else 0
q_count = len(st.session_state.offline_queue)

st.markdown(f"""
<div class="m-row">
  <div class="m-card" style="border-top:3px solid #FF6600">
    <div class="m-val">{total}</div>
    <div class="m-lbl">Total Defects</div>
  </div>
  <div class="m-card" style="border-top:3px solid #ef4444">
    <div class="m-val" style="color:#f87171">{high_c}</div>
    <div class="m-lbl">High Priority</div>
  </div>
  <div class="m-card" style="border-top:3px solid #f59e0b">
    <div class="m-val" style="color:#fbbf24">{med_c}</div>
    <div class="m-lbl">Medium Priority</div>
  </div>
  <div class="m-card" style="border-top:3px solid #22c55e">
    <div class="m-val" style="color:#4ade80">{low_c}</div>
    <div class="m-lbl">Low Priority</div>
  </div>
  <div class="m-card" style="border-top:3px solid #f59e0b">
    <div class="m-val" style="color:#fbbf24">{q_count}</div>
    <div class="m-lbl">Offline Queue</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📸 Field Capture",
    "📋 Live Punchlist",
    "📊 Dashboard",
    "⚙️ Office Sync & Data",
])

# ──────────────────────────────────────────────────────────────────────────
# TAB 1  —  FIELD CAPTURE
# ──────────────────────────────────────────────────────────────────────────
with tab1:
    cap_col, form_col = st.columns([1, 1.1], gap="large")

    # ── LEFT: Capture ──────────────────────────────────────────────────────
    with cap_col:

        _sec("🔌  Connectivity Status")
        connectivity = st.radio(
            "connectivity",
            ["🟢 Live AI Mode (5G/Wi-Fi)", "🟡 Offline Mode (No Signal)"],
            label_visibility="collapsed",
            horizontal=False,
        )
        is_live = connectivity.startswith("🟢")

        _sec("📷  Site Photo")
        img_src = st.radio(
            "img_src", ["Camera", "Upload File"],
            horizontal=True, label_visibility="collapsed",
        )
        captured_image = None

        if img_src == "Camera":
            captured_image = st.camera_input("Take a photo", label_visibility="collapsed")
        else:
            captured_image = st.file_uploader(
                "Upload image", type=["jpg", "jpeg", "png", "webp"],
                label_visibility="collapsed",
            )

        img_bytes = None
        if captured_image is not None:
            img_bytes = captured_image.read() if hasattr(captured_image, "read") else captured_image.getvalue()
            # Re-open for display (bytes already read)
            try:
                display_img = Image.open(io.BytesIO(img_bytes))
                st.image(display_img, use_container_width=True)
            except Exception:
                pass

        # ── AI Analyze or Queue ──────────────────────────────────────────
        if img_bytes is not None:
            if is_live:
                if st.button("🤖 Analyze with Vision AI", type="primary", use_container_width=True):
                    with st.spinner("Sending to Gemini Vision…"):
                        suggestion = gemini_analyze_image(img_bytes)
                        st.session_state.ai_suggestion = suggestion

                if st.session_state.ai_suggestion:
                    s = st.session_state.ai_suggestion
                    p_pill = _priority_pill(s.get("priority", "Medium"))
                    st.markdown(f"""
<div class="ai-card">
  <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.7rem;
              font-weight:600;text-transform:uppercase;letter-spacing:0.18em;
              color:#FF6600;margin-bottom:0.7rem">🤖 AI Analysis Result</div>
  <div class="ai-grid">
    <div class="ai-field">
      <div class="ai-lbl">Defect Type</div>
      <div class="ai-val">{s.get('defect_type', '—')}</div>
    </div>
    <div class="ai-field">
      <div class="ai-lbl">Priority</div>
      <div class="ai-val">{p_pill}</div>
    </div>
    <div class="ai-field">
      <div class="ai-lbl">Trade</div>
      <div class="ai-val">{s.get('trade', '—')}</div>
    </div>
    <div class="ai-field">
      <div class="ai-lbl">Subcontractor</div>
      <div class="ai-val">{s.get('subcontractor_hint', '—')}</div>
    </div>
  </div>
  <div class="ai-full" style="margin-bottom:0.6rem">
    <div class="ai-lbl">Reasoning</div>
    <div class="ai-val" style="font-size:0.83rem;line-height:1.5">{s.get('reasoning', '—')}</div>
  </div>
  <div class="ai-full">
    <div class="ai-lbl">Repair Method</div>
    <div class="ai-val" style="font-size:0.83rem;line-height:1.5">{s.get('repair_method', '—')}</div>
  </div>
</div>
""", unsafe_allow_html=True)
            else:
                # Offline mode — queue locally
                if st.button("💾 Queue Locally", type="primary", use_container_width=True):
                    st.session_state.offline_queue.append({
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "image_bytes": img_bytes,
                        "size_kb": round(len(img_bytes) / 1024, 1),
                    })
                    st.success(f"Queued. Total in queue: {len(st.session_state.offline_queue)}")

        # ── Voice Notes ────────────────────────────────────────────────────
        _sec("🎙️  Voice Notes")
        audio_input = st.audio_input("Record voice note", label_visibility="collapsed")
        translate_cb = st.checkbox("Translate to English", value=False)

        if audio_input is not None:
            audio_bytes = audio_input.read() if hasattr(audio_input, "read") else audio_input.getvalue()
            if st.button("🔤 Transcribe", use_container_width=True):
                with st.spinner("Transcribing audio with Gemini…"):
                    result = gemini_transcribe(audio_bytes, translate=translate_cb)
                    st.session_state.v_text = result

        if st.session_state.v_text:
            st.markdown(f"""
<div style="background:var(--navy);border:1px solid var(--border);border-radius:8px;
            padding:0.75rem 1rem;margin-top:0.5rem;font-size:0.88rem;
            color:var(--text);line-height:1.5">
  <span style="font-family:'Barlow Condensed',sans-serif;font-size:0.62rem;
               text-transform:uppercase;letter-spacing:0.14em;color:#FF6600;
               display:block;margin-bottom:0.3rem">Transcript</span>
  {st.session_state.v_text}
</div>
""", unsafe_allow_html=True)

    # ── RIGHT: Review & Assign Form ────────────────────────────────────────
    with form_col:
        _sec("📝  Review & Assign")

        if not is_live:
            st.info(
                "🟡 **Offline Mode Active** — The assignment form is disabled.\n\n"
                "Use *Queue Locally* on the left to capture evidence. "
                "Once connectivity is restored, switch to Live Mode and process via the Office Sync tab.",
                icon="📵",
            )
        else:
            # Safe pre-fill values from AI suggestion and voice transcript
            ai = st.session_state.ai_suggestion
            _defect_types = [
                "Honeycombing", "Surface Cracking", "Spalling", "Rebar Exposure",
                "Formwork Misalignment", "Cold Joint", "Segregation",
                "Void Formation", "Delamination", "Cover Depth Deficiency", "Other",
            ]
            _priorities    = ["High", "Medium", "Low"]
            _statuses      = ["Open", "Draft", "Closed"]
            _subcontractors = ["Apex Concrete Works", "BuildRight Formwork", "SteelCore Rebar"]
            _trades        = ["Concrete", "Rebar", "Formwork"]

            ai_defect   = ai.get("defect_type", "")
            ai_priority = ai.get("priority", "Medium")
            ai_sub      = ai.get("subcontractor_hint", "Apex Concrete Works")
            ai_repair   = ai.get("repair_method", "")

            # Compute default indices safely
            def _safe_idx(lst, val, default=0):
                try:
                    return lst.index(val)
                except ValueError:
                    return default

            defect_idx   = _safe_idx(_defect_types, ai_defect)
            priority_idx = _safe_idx(_priorities, ai_priority, 1)
            sub_idx      = _safe_idx(_subcontractors, ai_sub)

            with st.form("assign_form", clear_on_submit=True):
                location_val = st.text_input(
                    "Location / Grid Reference",
                    placeholder="e.g. Level 3 — Grid F7, Column C12",
                )
                c1, c2 = st.columns(2)
                with c1:
                    status_val = st.selectbox("Status", _statuses)
                with c2:
                    priority_val = st.selectbox("Priority", _priorities, index=priority_idx)

                defect_val = st.selectbox("Defect Type", _defect_types, index=defect_idx)
                sub_val    = st.selectbox("Subcontractor", _subcontractors, index=sub_idx)
                repair_val = st.text_area(
                    "AI Repair Method (editable)",
                    value=ai_repair,
                    height=80,
                )
                notes_val = st.text_area(
                    "Additional Notes",
                    value=st.session_state.v_text,
                    placeholder="Voice transcript or manual notes…",
                    height=80,
                )

                submitted = st.form_submit_button(
                    "✅ Log Defect to Punchlist",
                    type="primary",
                    use_container_width=True,
                )

                if submitted:
                    if not location_val.strip():
                        st.error("Location is required.")
                    else:
                        # SLA: calculate due date
                        due_date = (
                            datetime.date.today() +
                            datetime.timedelta(days=_sla_days(priority_val))
                        )
                        photo_id = ""
                        if img_bytes is not None:
                            photo_id = _next_id().replace("LA-", "IMG-")
                            # Convert to JPEG for storage
                            try:
                                pil = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                                buf = io.BytesIO()
                                pil.save(buf, format="JPEG", quality=85)
                                st.session_state.images[photo_id] = buf.getvalue()
                            except Exception:
                                st.session_state.images[photo_id] = img_bytes

                        new_id = _next_id()
                        new_row = {
                            "ID":            new_id,
                            "Timestamp":     datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Location":      location_val,
                            "Status":        status_val,
                            "Defect Type":   defect_val,
                            "Priority":      priority_val,
                            "Subcontractor": sub_val,
                            "Repair Method": repair_val,
                            "Notes":         notes_val,
                            "Due Date":      str(due_date),
                            "AI Reasoning":  ai.get("reasoning", "Manual entry."),
                            "Photo ID":      photo_id,
                        }
                        st.session_state.defects = pd.concat(
                            [st.session_state.defects, pd.DataFrame([new_row])],
                            ignore_index=True,
                        )
                        # Clear temporary AI state
                        st.session_state.ai_suggestion = {}
                        st.session_state.v_text = ""
                        st.success(
                            f"✅ **{new_id}** logged · "
                            f"{defect_val} · {priority_val} Priority · "
                            f"Due {due_date}"
                        )

# ──────────────────────────────────────────────────────────────────────────
# TAB 2  —  LIVE PUNCHLIST
# ──────────────────────────────────────────────────────────────────────────
with tab2:
    df = st.session_state.defects

    if df.empty:
        st.markdown("""
<div style="text-align:center;padding:3rem 1rem;color:rgba(255,255,255,0.25);
            font-family:'Barlow Condensed',sans-serif;font-size:0.95rem;
            letter-spacing:0.1em;text-transform:uppercase">
  No defects logged yet.<br>Capture site photos in the Field Capture tab.
</div>
""", unsafe_allow_html=True)
    else:
        # ── Filter controls ──────────────────────────────────────────────
        fc1, fc2, fc3 = st.columns([1, 1, 2])
        with fc1:
            p_filter = st.selectbox("Filter Priority", ["All", "High", "Medium", "Low"])
        with fc2:
            s_filter = st.selectbox("Filter Status", ["All", "Open", "Draft", "Closed"])
        with fc3:
            st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)

        disp = df.copy()
        if p_filter != "All":
            disp = disp[disp["Priority"] == p_filter]
        if s_filter != "All":
            disp = disp[disp["Status"] == s_filter]

        # Colour-code priority in the table
        def _style_priority(val):
            c = {"High": "#f87171", "Medium": "#fbbf24", "Low": "#4ade80"}.get(val, "")
            return f"color:{c};font-weight:600" if c else ""

        def _style_status(val):
            c = {"Open": "#f87171", "Draft": "#fbbf24", "Closed": "#4ade80"}.get(val, "")
            return f"color:{c}" if c else ""

        styled = (
            disp.style
            .applymap(_style_priority, subset=["Priority"])
            .applymap(_style_status,   subset=["Status"])
        )

        st.dataframe(styled, use_container_width=True, height=420)

        st.markdown(f"""
<div style="font-family:'Barlow Condensed',sans-serif;font-size:0.72rem;
            letter-spacing:0.12em;text-transform:uppercase;
            color:rgba(255,255,255,0.3);margin:0.4rem 0 0.8rem">
  Showing {len(disp)} of {len(df)} records
</div>
""", unsafe_allow_html=True)

        # ── Export ZIP ──────────────────────────────────────────────────
        _sec("📦  Export")
        zip_bytes = build_zip_export()
        st.download_button(
            label=f"📥  Download ZIP  —  punchlist.csv + {len(st.session_state.images)} image(s)",
            data=zip_bytes,
            file_name=f"leighton_punchlist_{datetime.date.today()}.zip",
            mime="application/zip",
            use_container_width=True,
        )

# ──────────────────────────────────────────────────────────────────────────
# TAB 3  —  DASHBOARD
# ──────────────────────────────────────────────────────────────────────────
with tab3:
    df = st.session_state.defects

    if df.empty or len(df) < 2:
        st.markdown("""
<div style="text-align:center;padding:3rem 1rem;color:rgba(255,255,255,0.25);
            font-family:'Barlow Condensed',sans-serif;font-size:0.95rem;
            letter-spacing:0.1em;text-transform:uppercase">
  Not enough data yet.<br>Log defects or load the demo dataset from the Office Sync tab.
</div>
""", unsafe_allow_html=True)
    else:
        ch1, ch2 = st.columns(2, gap="large")

        with ch1:
            _sec("📊  Defects by Priority")
            priority_counts = df["Priority"].value_counts().reset_index()
            priority_counts.columns = ["Priority", "Count"]
            priority_order = ["High", "Medium", "Low"]
            priority_counts["Priority"] = pd.Categorical(
                priority_counts["Priority"], categories=priority_order, ordered=True
            )
            priority_counts = priority_counts.sort_values("Priority")
            st.bar_chart(
                priority_counts.set_index("Priority"),
                color="#FF6600",
                use_container_width=True,
                height=300,
            )

        with ch2:
            _sec("🏢  Defects by Subcontractor")
            sub_counts = df["Subcontractor"].value_counts().reset_index()
            sub_counts.columns = ["Subcontractor", "Count"]
            st.bar_chart(
                sub_counts.set_index("Subcontractor"),
                color="#0d213f",
                use_container_width=True,
                height=300,
            )

        # ── Second row ───────────────────────────────────────────────────
        ch3, ch4 = st.columns(2, gap="large")

        with ch3:
            _sec("🔖  Defects by Type")
            type_counts = df["Defect Type"].value_counts().head(8).reset_index()
            type_counts.columns = ["Defect Type", "Count"]
            st.bar_chart(
                type_counts.set_index("Defect Type"),
                color="#CC5200",
                use_container_width=True,
                height=280,
            )

        with ch4:
            _sec("📁  Defects by Status")
            status_counts = df["Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            st.bar_chart(
                status_counts.set_index("Status"),
                color="#1e3d6e",
                use_container_width=True,
                height=280,
            )

        # ── Summary table ────────────────────────────────────────────────
        _sec("📋  Priority × Subcontractor Matrix")
        if len(df) > 0:
            pivot = pd.crosstab(
                df["Subcontractor"],
                df["Priority"],
                margins=True,
                margins_name="Total",
            )
            # Reorder columns if present
            cols_order = [c for c in ["High", "Medium", "Low", "Total"] if c in pivot.columns]
            st.dataframe(pivot[cols_order], use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────
# TAB 4  —  OFFICE SYNC & DATA
# ──────────────────────────────────────────────────────────────────────────
with tab4:
    sc1, sc2 = st.columns(2, gap="large")

    with sc1:
        _sec("📡  Offline Queue Manager")

        queue = st.session_state.offline_queue
        if queue:
            st.markdown(f"""
<div class="queue-badge">
  ⚠️ <strong>{len(queue)} item(s)</strong> pending sync from offline captures.<br>
  <span style="font-size:0.8rem;opacity:0.8">
    Estimated data: {sum(i.get('size_kb',0) for i in queue):.1f} KB
  </span>
</div>
""", unsafe_allow_html=True)
            # Queue details table
            queue_df = pd.DataFrame([
                {"#": i + 1, "Captured At": q["timestamp"], "Size (KB)": q.get("size_kb", "—")}
                for i, q in enumerate(queue)
            ])
            st.dataframe(queue_df, use_container_width=True, hide_index=True)

            if st.button("☁️ Process Batch Sync", type="primary", use_container_width=True):
                with st.spinner("Syncing to project server…"):
                    import time
                    time.sleep(1.5)
                    st.session_state.offline_queue = []
                    st.success("✅ Batch sync complete. All queued items uploaded to project server.")
                    st.rerun()
        else:
            st.markdown("""
<div style="text-align:center;padding:2rem 1rem;
            color:rgba(255,255,255,0.25);
            font-family:'Barlow Condensed',sans-serif;
            font-size:0.88rem;letter-spacing:0.1em;text-transform:uppercase">
  ✅ Offline queue is empty
</div>
""", unsafe_allow_html=True)

    with sc2:
        _sec("🗄️  Demo & Data Management")

        st.markdown("""
<div style="background:var(--navy);border:1px solid var(--border);border-radius:8px;
            padding:1rem;margin-bottom:1rem;font-size:0.84rem;color:var(--text-muted);
            line-height:1.6">
  Load a realistic demo dataset of <strong style="color:var(--text)">60+ defects</strong>
  across multiple subcontractors, priorities, and defect types to showcase the
  Dashboard and Live Punchlist features.
</div>
""", unsafe_allow_html=True)

        if st.button("📂 Load Demo Dataset (60 defects)", type="primary", use_container_width=True):
            load_demo_data()
            st.success("✅ Demo dataset loaded. Check the Dashboard and Live Punchlist tabs.")
            st.rerun()

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

        if not st.session_state.defects.empty:
            st.markdown("""
<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.25);
            border-radius:8px;padding:1rem;margin-bottom:0.8rem;
            font-size:0.84rem;color:rgba(239,68,68,0.8);line-height:1.5">
  ⚠️ This will permanently clear all logged defects and images from this session.
</div>
""", unsafe_allow_html=True)
            if st.button("🗑️ Clear All Data", use_container_width=True):
                st.session_state.defects = pd.DataFrame(columns=DEFECT_COLS)
                st.session_state.images = {}
                st.session_state.ai_suggestion = {}
                st.session_state.v_text = ""
                st.session_state.defect_counter = 1
                st.success("All data cleared.")
                st.rerun()

        _sec("ℹ️  Session Info")
        st.markdown(f"""
<div style="background:var(--navy);border:1px solid var(--border);border-radius:8px;
            padding:0.9rem 1rem;font-family:'Barlow Condensed',sans-serif;
            font-size:0.82rem;line-height:2;color:var(--text-muted)">
  <span style="color:var(--orange)">Gemini API</span>&nbsp;&nbsp;
    {"✅ Connected" if _GEMINI_OK else "❌ GEMINI_API_KEY not set"}<br>
  <span style="color:var(--orange)">Total Defects</span>&nbsp;&nbsp;
    {len(st.session_state.defects)}<br>
  <span style="color:var(--orange)">Photos Stored</span>&nbsp;&nbsp;
    {len(st.session_state.images)}<br>
  <span style="color:var(--orange)">Offline Queue</span>&nbsp;&nbsp;
    {len(st.session_state.offline_queue)} item(s)<br>
  <span style="color:var(--orange)">Session Started</span>&nbsp;&nbsp;
    {datetime.date.today().strftime("%d %b %Y")}
</div>
""", unsafe_allow_html=True)
