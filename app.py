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

/* Sidebar course navigation: text tabs, matching the chapter tab language */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: .12rem !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    width: 100% !important;
    min-height: 34px;
    padding: .38rem .45rem !important;
    border: none !important;
    border-radius: 4px;
    background: transparent !important;
    transition: background-color .15s ease, color .15s ease;
    cursor: pointer;
}
/* Hide Streamlit's circular radio marker completely. */
section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label p {
    margin: 0 !important;
    font-weight: 500;
    color: inherit;
    transition: color .15s ease;
}
/* Hover: subtle tab background + red text. */
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: rgba(255,75,75,.055) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover p {
    color: #ff4b4b !important;
}
/* Selected: only the word becomes red, like the internal chapter tabs. */
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
    color: #ff4b4b !important;
    font-weight: 600;
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
    choice = st.radio("Select a topic", TOPICS, index=TOPICS.index(st.session_state.page), label_visibility="collapsed")
    if choice != st.session_state.page:
        st.session_state.page = choice
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
