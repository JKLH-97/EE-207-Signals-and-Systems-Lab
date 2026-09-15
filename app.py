import streamlit as st
from pathlib import Path
import numpy as np
from modules import lti, convolution, placeholder

st.set_page_config(page_title="EE-207 Signals and Systems Lab", page_icon="📈", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.course-card {padding: 1rem 1.1rem; border: 1px solid #3b3f49; border-radius: 14px; min-height: 128px; margin-bottom: .45rem;}
.course-card h3 {margin: 0 0 .35rem 0;}
.hero {padding: 1.4rem 1.6rem; border: 1px solid #3b3f49; border-radius: 18px; margin-bottom: 1.2rem;}

/* Sidebar course navigation — real buttons, not radio controls */
section[data-testid="stSidebar"] div[data-testid="stButton"] {
    margin-bottom: .42rem;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    width: 100%;
    min-height: 46px;
    justify-content: flex-start;
    padding: .60rem .90rem;
    border-radius: 4px;
    font-weight: 500;
    transition: background-color .15s ease, border-color .15s ease, color .15s ease;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent;
    border: 1px solid rgba(125,130,142,.38);
    color: inherit;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: rgba(255,75,75,.055);
    border-color: rgba(255,75,75,.72);
    color: #ff4b4b;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
    background: rgba(255,75,75,.10);
    border: 1px solid #ff4b4b;
    color: #ff4b4b;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: rgba(255,75,75,.15);
    border-color: #ff4b4b;
    color: #ff4b4b;
}
</style>
""", unsafe_allow_html=True)

TOPICS = [
    "Home",
    "LTI Systems",
    "Convolution",
    "Laplace Transform",
    "Fourier Analysis",
    "Filters",
    "Sampling",
]

if "page" not in st.session_state:
    st.session_state.page = "Home"

with st.sidebar:
    st.title("EE-207")
    st.caption("Signals & Systems")
    st.markdown("### Course Topics")
    for topic in TOPICS:
        selected = (topic == st.session_state.page)
        if st.button(
            topic,
            key=f"sidebar_topic_{topic}",
            type="primary" if selected else "secondary",
            use_container_width=True,
        ):
            if not selected:
                st.session_state.page = topic
                st.rerun()
    st.divider()
    st.caption("Interactive modules will be added as the course progresses.")



def home():
    # Main course cover: use the exact same full-width rendering strategy as the LTI chapter.
    home_banner = Path(__file__).resolve().parent / "assets" / "home_banner.png"

    st.markdown(
        """
        <style>
        /* Only the Home cover image: remove Streamlit's intrinsic image width cap. */
        .ee207-home-cover-marker + div[data-testid="stImage"],
        .ee207-home-cover-marker + div[data-testid="stImage"] > div {
            width: 100% !important;
            max-width: none !important;
        }
        .ee207-home-cover-marker + div[data-testid="stImage"] img {
            width: 100% !important;
            max-width: none !important;
            height: auto !important;
            display: block !important;
            object-fit: contain !important;
        }
        </style>
        <div class="ee207-home-cover-marker"></div>
        """,
        unsafe_allow_html=True,
    )

    if home_banner.exists():
        st.image(str(home_banner), use_container_width=True)
    else:
        st.title("EE-207 : Signals and Systems")

    st.markdown("## Course Modules")

    modules = [
        ("LTI Systems", "Linearity, time invariance, system grapher, and mini exam.", True),
        ("Convolution", "Graphical interpretation and step-by-step convolution.", True),
        ("Laplace Transform", "Transforms, poles and zeros, and system analysis.", False),
        ("Fourier Analysis", "Fourier series and Fourier transform visualization.", False),
        ("Filters", "Frequency-selective systems and filter behavior.", False),
        ("Sampling", "Sampling theorem, aliasing, and reconstruction.", False),
    ]
    for row in range(0, len(modules), 3):
        cols = st.columns(3, gap="large")
        for col, (name, desc, ready) in zip(cols, modules[row:row+3]):
            with col:
                status = "Available" if ready else "Coming soon"
                st.markdown(f'<div class="course-card"><h3>{name}</h3><p>{desc}</p><small>{status}</small></div>', unsafe_allow_html=True)
                if st.button("Open module" if ready else "Preview", key=f"home_{name}", use_container_width=True):
                    st.session_state.page = name
                    st.rerun()

page = st.session_state.page
if page == "Home":
    home()
elif page == "LTI Systems":
    lti.render()
elif page == "Convolution":
    convolution.render()
else:
    placeholder.render(page)
