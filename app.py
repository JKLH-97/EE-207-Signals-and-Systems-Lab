import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from modules import lti, placeholder

st.set_page_config(page_title="EE-207 Signals and Systems Lab", page_icon="📈", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.course-card {padding: 1rem 1.1rem; border: 1px solid #3b3f49; border-radius: 14px; min-height: 128px; margin-bottom: .45rem;}
.course-card h3 {margin: 0 0 .35rem 0;}
.hero {padding: 1.4rem 1.6rem; border: 1px solid #3b3f49; border-radius: 18px; margin-bottom: 1.2rem;}
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
    st.caption("Signals & Systems Lab")
    st.markdown("### Course Topics")
    choice = st.radio("Select a topic", TOPICS, index=TOPICS.index(st.session_state.page), label_visibility="collapsed")
    if choice != st.session_state.page:
        st.session_state.page = choice
        st.rerun()
    st.divider()
    st.caption("Interactive modules will be added as the course progresses.")


def signal_hero():
    t = np.linspace(-2*np.pi, 2*np.pi, 900)
    y = np.sin(t) + 0.35*np.sin(3*t)
    fig, ax = plt.subplots(figsize=(10, 2.5))
    ax.plot(t, y, linewidth=2.7)
    ax.axhline(0, linewidth=.8, alpha=.4)
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    ax.set_title("Signals connect time, frequency, systems, and information")
    ax.grid(True, alpha=.22)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True, use_container_width=True)


def home():
    st.title("EE-207 : Signals and Systems Lab")
    st.markdown("""
    <div class="hero">
    <h3>Interactive course workspace</h3>
    Explore each chapter through graphical demonstrations, experiments, and practice activities.
    </div>
    """, unsafe_allow_html=True)
    signal_hero()
    st.markdown("## Course Modules")

    modules = [
        ("LTI Systems", "Linearity, time invariance, system grapher, and mini exam.", True),
        ("Convolution", "Graphical interpretation and step-by-step convolution.", False),
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
else:
    placeholder.render(page)
