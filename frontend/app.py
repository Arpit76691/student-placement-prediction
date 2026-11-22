"""
Student Placement Prediction - Frontend Interface
Built with Azure Machine Learning, FastAPI and Streamlit.
"""

import os
import json
import requests
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Placement Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. API URL Resolver
# -----------------------------------------------------------------------------
def resolve_api_url() -> str:
    """Finds the backend API URL across secrets, environment, and Azure default."""
    try:
        if hasattr(st, "secrets"):
            try:
                if "API_URL" in st.secrets:
                    secret_url = st.secrets["API_URL"]
                    if secret_url and str(secret_url).strip():
                        return str(secret_url).strip().rstrip("/")
            except Exception:
                pass
    except Exception:
        pass

    env_url = os.environ.get("API_URL")
    if env_url and env_url.strip():
        return env_url.strip().rstrip("/")

    return "https://placement-api-student101.azurewebsites.net"

API_URL = resolve_api_url()

# -----------------------------------------------------------------------------
# 3. Health Check Helper
# -----------------------------------------------------------------------------
def check_backend_health(base_url: str):
    """Checks whether the backend server is reachable."""
    try:
        resp = requests.get(f"{base_url}/health", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and data.get("status") == "ok":
                return True, "Backend connected", None
            return True, "Backend connected", None
        return False, "Backend offline", f"HTTP status {resp.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Backend offline", "Could not connect to port 8000"
    except requests.exceptions.Timeout:
        return False, "Backend offline", "Connection timed out"
    except Exception as ex:
        return False, "Backend offline", str(ex)

# -----------------------------------------------------------------------------
# 4. Load Model Metrics
# -----------------------------------------------------------------------------
def load_metrics():
    """Reads evaluation metrics from JSON file."""
    paths = [
        os.path.join(os.path.dirname(__file__), "metrics.json"),
        os.path.join(os.path.dirname(__file__), "..", "models", "metrics.json"),
        "models/metrics.json"
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "r") as f:
                    return json.load(f)
            except Exception:
                pass
    return None

metrics_data = load_metrics()

# -----------------------------------------------------------------------------
# 5. Styling & Design Tokens
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    :root {
        --bg: #FAFAF9;
        --card: #FFFFFF;
        --border: #E7E5E4;
        --text: #1C1917;
        --muted: #78716C;
        --accent: #0F766E;
        --accent-hover: #115E59;
        --accent-tint: #CCFBF1;
        --alert: #B45309;
        --alert-tint: #FEF3C7;
        --radius-card: 14px;
        --radius-input: 10px;
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
        --shadow-hover: 0 8px 24px rgba(0, 0, 0, 0.06);
    }

    /* Page and layout */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text);
        background-color: var(--bg);
    }

    .main .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    /* Headings & copy */
    .app-header {
        margin-bottom: 1.75rem;
    }

    .app-title {
        font-size: 2rem;
        font-weight: 600;
        color: var(--text);
        letter-spacing: -0.02em;
        margin: 0 0 0.35rem 0;
        line-height: 1.25;
    }

    .app-subtitle {
        font-size: 0.95rem;
        color: var(--muted);
        margin: 0;
        line-height: 1.5;
    }

    /* Card styling */
    .content-card {
        background-color: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        padding: 1.25rem 1.5rem;
        box-shadow: var(--shadow-sm);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1.25rem;
    }

    .content-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }

    .card-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text);
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .field-helper {
        font-size: 0.8rem;
        color: var(--muted);
        margin-top: -0.4rem;
        margin-bottom: 0.6rem;
    }

    /* Sliders styling */
    /* Add space between widget label and thumb value so they never overlap */
    div[data-testid="stSlider"] > label,
    div[data-testid="stSlider"] [data-testid="stWidgetLabel"] {
        margin-bottom: 24px !important;
        padding-bottom: 0 !important;
    }

    div[data-testid="stSlider"] [data-baseweb="slider"] {
        margin-top: 8px !important;
    }

    /* Slider track: thin (4px) */
    div[data-testid="stSlider"] [data-baseweb="slider"] > div {
        height: 4px !important;
    }

    /* Style ONLY the draggable thumb circle (18px circle, background #0F766E, white 2px border) */
    div[data-testid="stSlider"] div[role="slider"] {
        width: 18px !important;
        height: 18px !important;
        background-color: #0F766E !important;
        border: 2px solid #FFFFFF !important;
        border-radius: 50% !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25) !important;
        top: 50% !important;
        box-sizing: border-box !important;
    }

    /* Current value label above the thumb: transparent background, teal font */
    div[data-testid="stSliderThumbValue"],
    div[data-testid="stSliderThumbValue"] * {
        background: transparent !important;
        background-color: transparent !important;
        color: #0F766E !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 0 !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* Min and max labels at ends of track: transparent background, muted gray font */
    div[data-testid="stSliderTickBarMin"],
    div[data-testid="stSliderTickBarMax"],
    div[data-testid="stSliderTickBar"],
    div[data-testid="stSliderTickBarMin"] *,
    div[data-testid="stSliderTickBarMax"] * {
        background: transparent !important;
        background-color: transparent !important;
        color: #78716C !important;
        font-size: 12px !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* Number inputs */
    div[data-testid="stNumberInput"] input {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-input) !important;
        background-color: #FFFFFF !important;
        color: var(--text) !important;
        font-size: 0.92rem !important;
        padding: 0.45rem 0.75rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    div[data-testid="stNumberInput"] input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px var(--accent-tint) !important;
        outline: none !important;
    }

    /* Primary button */
    div.stButton > button {
        background-color: var(--accent) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--accent) !important;
        border-radius: var(--radius-input) !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        padding: 0.65rem 1.5rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }

    div.stButton > button:hover {
        background-color: var(--accent-hover) !important;
        border-color: var(--accent-hover) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.15) !important;
    }

    div.stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
    }

    /* Sidebar Refresh secondary button */
    [data-testid="stSidebar"] div.stButton > button {
        background-color: transparent !important;
        background: transparent !important;
        border: 1px solid #E7E5E4 !important;
        color: #1C1917 !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 0.35rem 0.85rem !important;
        white-space: nowrap !important;
        width: auto !important;
        box-shadow: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: 0.25rem !important;
    }

    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #F5F5F4 !important;
        background: #F5F5F4 !important;
        border-color: #D6D3D1 !important;
        color: #1C1917 !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Status pill */
    .status-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        background-color: #F5F5F4;
        border: 1px solid var(--border);
        border-radius: 9999px;
        padding: 4px 12px;
        font-size: 0.8rem;
        color: var(--text);
        margin-bottom: 0.5rem;
    }

    .dot-connected {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #059669;
    }

    .dot-offline {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #D97706;
    }

    /* Model performance tiles */
    .perf-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 0.5rem;
        margin-bottom: 0.75rem;
    }

    .perf-tile {
        background-color: #FAFAF9;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.5rem 0.65rem;
    }

    .perf-label {
        font-size: 0.72rem;
        color: var(--muted);
        margin-bottom: 2px;
    }

    .perf-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text);
    }

    /* Result Card with Animation */
    @keyframes slideUpFade {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .result-card {
        background-color: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        animation: slideUpFade 350ms ease-out forwards;
        margin-top: 1.5rem;
        margin-bottom: 1.25rem;
    }

    .result-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
    }

    .result-title-placed {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--accent);
        margin: 0 0 0.25rem 0;
    }

    .result-title-atrisk {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--alert);
        margin: 0 0 0.25rem 0;
    }

    .result-sentence {
        font-size: 0.9rem;
        color: var(--muted);
        margin: 0;
        line-height: 1.4;
    }

    .factor-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }

    .factor-bar-bg {
        width: 120px;
        height: 6px;
        background-color: #F5F5F4;
        border-radius: 9999px;
        overflow: hidden;
    }

    .factor-bar-fill {
        height: 100%;
        background-color: var(--accent);
        border-radius: 9999px;
    }

    /* Calm error banner */
    .calm-message {
        background-color: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: var(--radius-input);
        padding: 1rem 1.25rem;
        margin-top: 1.25rem;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        font-size: 0.8rem;
        color: var(--muted);
        margin-top: 2.5rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. Sidebar (Quiet, Clean & Compact)
# -----------------------------------------------------------------------------
with st.sidebar:
    # Logo and App Title
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 1.25rem;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0F766E" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
            <path d="M6 12v5c3 3 9 3 12 0v-5"/>
        </svg>
        <span style="font-weight: 600; font-size: 15px; color: #1C1917; letter-spacing: -0.01em;">Placement Predictor</span>
    </div>
    """, unsafe_allow_html=True)

    # Status Pill
    is_healthy, status_label, status_detail = check_backend_health(API_URL)
    dot_class = "dot-connected" if is_healthy else "dot-offline"

    st.markdown(f"""
    <div class="status-pill">
        <span class="{dot_class}"></span>
        <span style="font-size: 13px; font-weight: 500;">{status_label}</span>
    </div>
    """, unsafe_allow_html=True)

    if not is_healthy:
        st.caption(status_detail or "Backend not detected on port 8000")

    # Refresh Button (Displays full word, auto width, clean transparent background)
    if st.button("Refresh", key="sidebar_refresh_btn"):
        st.rerun()

    # Connection details expander
    with st.expander("Connection details"):
        st.text(f"URL: {API_URL}")

    st.markdown("<hr style='border: none; border-top: 1px solid #E7E5E4; margin: 1rem 0;'>", unsafe_allow_html=True)

    # Model Performance Stats
    st.markdown("<div style='font-size: 13px; font-weight: 600; color: #1C1917; margin-bottom: 0.25rem;'>Model performance</div>", unsafe_allow_html=True)
    if metrics_data:
        best_name = metrics_data.get("best_model", "Logistic Regression")
        model_stats = metrics_data.get("models", {}).get(best_name, {})

        st.markdown(f"""
        <div class="perf-grid">
            <div class="perf-tile">
                <div class="perf-label">Accuracy</div>
                <div class="perf-value">{model_stats.get('accuracy', 0)*100:.1f}%</div>
            </div>
            <div class="perf-tile">
                <div class="perf-label">Precision</div>
                <div class="perf-value">{model_stats.get('precision', 0)*100:.1f}%</div>
            </div>
            <div class="perf-tile">
                <div class="perf-label">Recall</div>
                <div class="perf-value">{model_stats.get('recall', 0)*100:.1f}%</div>
            </div>
            <div class="perf-tile">
                <div class="perf-label">F1 score</div>
                <div class="perf-value">{model_stats.get('f1_score', 0):.3f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        roc_val = float(model_stats.get("roc_auc", 0.957))
        st.markdown(f"""
        <div style="font-size: 12px; color: #78716C; display: flex; justify-content: space-between; margin-bottom: 3px;">
            <span>ROC-AUC</span>
            <span style="font-weight: 500; color: #1C1917;">{roc_val:.3f}</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(roc_val)

        st.markdown(f"""
        <div style="font-size: 11px; color: #78716C; margin-top: 6px;">
            Model: {best_name}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 1px solid #E7E5E4; margin: 1rem 0;'>", unsafe_allow_html=True)

    # Preset Profiles (Preserved)
    st.markdown("<div style='font-size: 13px; font-weight: 600; color: #1C1917; margin-bottom: 0.25rem;'>Sample profile</div>", unsafe_allow_html=True)
    preset = st.radio(
        "Select a profile:",
        ["Custom", "High Achiever", "Moderate Candidate", "At-Risk Candidate"],
        index=0,
        label_visibility="collapsed"
    )

# -----------------------------------------------------------------------------
# 7. Main Area: Clean Header & Two Cards
# -----------------------------------------------------------------------------
st.markdown("""
<div class="app-header">
    <h1 class="app-title">Will this student get placed?</h1>
    <p class="app-subtitle">Enter a student's profile and get an instant prediction from our trained model.</p>
</div>
""", unsafe_allow_html=True)

# Preset values
defaults = {
    "Custom": (7.50, 1, 2, 7.0, 70.0, 0, 1),
    "High Achiever": (8.90, 2, 4, 8.5, 88.0, 0, 3),
    "Moderate Candidate": (7.20, 1, 2, 6.5, 65.0, 1, 1),
    "At-Risk Candidate": (5.40, 0, 0, 3.5, 40.0, 3, 0)
}
d_cgpa, d_intern, d_proj, d_comm, d_apt, d_backlog, d_cert = defaults[preset]

col_acad, col_skills = st.columns(2, gap="large")

with col_acad:
    st.markdown("""
    <div class="card-title">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#0F766E" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/>
            <path d="M6 6h10"/>
            <path d="M6 10h10"/>
        </svg>
        <span>Academics</span>
    </div>
    """, unsafe_allow_html=True)

    cgpa = st.slider(
        "CGPA",
        min_value=5.0,
        max_value=10.0,
        value=float(d_cgpa),
        step=0.05,
        format="%.2f"
    )
    st.markdown("<div class='field-helper'>Out of 10.0</div>", unsafe_allow_html=True)

    internships = st.number_input(
        "Internships",
        min_value=0,
        max_value=6,
        value=int(d_intern),
        step=1
    )

    projects = st.number_input(
        "Projects",
        min_value=0,
        max_value=10,
        value=int(d_proj),
        step=1
    )

    certifications = st.number_input(
        "Certifications",
        min_value=0,
        max_value=10,
        value=int(d_cert),
        step=1
    )

with col_skills:
    st.markdown("""
    <div class="card-title">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#0F766E" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
        </svg>
        <span>Skills</span>
    </div>
    """, unsafe_allow_html=True)

    aptitude_score = st.slider(
        "Aptitude score",
        min_value=30.0,
        max_value=100.0,
        value=float(d_apt),
        step=1.0,
        format="%.0f"
    )
    st.markdown("<div class='field-helper'>Out of 100</div>", unsafe_allow_html=True)

    communication_skills = st.slider(
        "Communication rating",
        min_value=1.0,
        max_value=10.0,
        value=float(d_comm),
        step=0.5,
        format="%.1f"
    )
    st.markdown("<div class='field-helper'>Out of 10.0</div>", unsafe_allow_html=True)

    backlogs = st.number_input(
        "Active backlogs",
        min_value=0,
        max_value=8,
        value=int(d_backlog),
        step=1
    )

st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

# Primary Button
predict_btn = st.button("Predict placement", use_container_width=True)

# -----------------------------------------------------------------------------
# 8. Prediction Handling & Clean Animated Result Card
# -----------------------------------------------------------------------------
if predict_btn:
    payload = {
        "cgpa": float(cgpa),
        "internships": int(internships),
        "projects": int(projects),
        "communication_skills": float(communication_skills),
        "aptitude_score": float(aptitude_score),
        "backlogs": int(backlogs),
        "certifications": int(certifications)
    }

    with st.spinner("Calculating prediction..."):
        try:
            response = requests.post(
                f"{API_URL}/predict",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                placed_raw = result.get("placed", "No")
                is_placed = (str(placed_raw).strip().lower() == "yes")

                try:
                    prob = float(result.get("probability", 0.0))
                except (ValueError, TypeError):
                    prob = 0.0
                prob = max(0.0, min(1.0, prob))

                message = result.get("message", "Prediction complete.")
                pct = int(round(prob * 100))

                # SVG Ring Geometry: r=38, circumference=2*pi*38 ~ 238.76
                circumference = 238.76
                offset = circumference - (prob * circumference)
                ring_color = "#0F766E" if is_placed else "#B45309"
                title_class = "result-title-placed" if is_placed else "result-title-atrisk"
                title_text = "Likely to be placed" if is_placed else "Needs improvement"

                # Horizontal influence bars
                cgpa_pct = min(100, int((cgpa / 10.0) * 100))
                apt_pct = min(100, int(aptitude_score))
                comm_pct = min(100, int((communication_skills / 10.0) * 100))

                st.markdown(f"""
                <div class="result-card">
                    <div class="result-row">
                        <div style="flex: 1;">
                            <h3 class="{title_class}">{title_text}</h3>
                            <p class="result-sentence">{message}</p>
                            <div style="margin-top: 1.25rem;">
                                <div style="font-size: 12px; font-weight: 500; color: #1C1917; margin-bottom: 6px;">What influenced this</div>
                                <div class="factor-row">
                                    <span style="color: #78716C;">CGPA ({cgpa:.2f}/10)</span>
                                    <div class="factor-bar-bg"><div class="factor-bar-fill" style="width: {cgpa_pct}%;"></div></div>
                                </div>
                                <div class="factor-row">
                                    <span style="color: #78716C;">Aptitude ({aptitude_score:.0f}/100)</span>
                                    <div class="factor-bar-bg"><div class="factor-bar-fill" style="width: {apt_pct}%;"></div></div>
                                </div>
                                <div class="factor-row">
                                    <span style="color: #78716C;">Communication ({communication_skills:.1f}/10)</span>
                                    <div class="factor-bar-bg"><div class="factor-bar-fill" style="width: {comm_pct}%;"></div></div>
                                </div>
                            </div>
                        </div>
                        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-width: 110px;">
                            <svg width="96" height="96" viewBox="0 0 96 96">
                                <circle cx="48" cy="48" r="38" fill="none" stroke="#F5F5F4" stroke-width="7"/>
                                <circle cx="48" cy="48" r="38" fill="none" stroke="{ring_color}" stroke-width="7"
                                    stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                                    stroke-linecap="round" transform="rotate(-90 48 48)"/>
                                <text x="48" y="53" text-anchor="middle" font-family="'Inter', sans-serif" font-size="20" font-weight="600" fill="#1C1917">{pct}%</text>
                            </svg>
                            <div style="font-size: 11px; color: #78716C; margin-top: 4px;">Placement chance</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            elif response.status_code == 422:
                st.markdown("""
                <div class="calm-message">
                    <div style="font-weight: 500; color: #1C1917; margin-bottom: 4px;">Invalid input values</div>
                    <div style="color: #78716C; font-size: 14px;">Please check that your input numbers fall within the expected ranges.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="calm-message">
                    <div style="font-weight: 500; color: #1C1917; margin-bottom: 4px;">Unexpected server response</div>
                    <div style="color: #78716C; font-size: 14px;">The server returned status code {response.status_code}.</div>
                </div>
                """, unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            st.markdown("""
            <div class="calm-message">
                <div style="font-weight: 500; color: #1C1917; margin-bottom: 4px;">Unable to reach the prediction service</div>
                <div style="color: #78716C; font-size: 14px;">The backend appears to be offline. Make sure the server is running on port 8000.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Try again"):
                st.rerun()

        except requests.exceptions.Timeout:
            st.markdown("""
            <div class="calm-message">
                <div style="font-weight: 500; color: #1C1917; margin-bottom: 4px;">Request timed out</div>
                <div style="color: #78716C; font-size: 14px;">The server took longer than expected to respond. Please try again.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Try again"):
                st.rerun()

        except Exception as e:
            st.markdown(f"""
            <div class="calm-message">
                <div style="font-weight: 500; color: #1C1917; margin-bottom: 4px;">Prediction error</div>
                <div style="color: #78716C; font-size: 14px;">{str(e)}</div>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. Small Muted Footer
# -----------------------------------------------------------------------------
st.markdown("""
<div class="app-footer">
    Built with Azure Machine Learning, FastAPI and Streamlit
</div>
""", unsafe_allow_html=True)
