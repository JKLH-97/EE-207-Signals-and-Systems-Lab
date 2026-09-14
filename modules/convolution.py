import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# ============================================================
# EE-207 — Convolution
# Native Streamlit implementation.
# No copied HTML/CSS/JS animation from the reference demo.
# ============================================================

C_X = "tab:blue"
C_H = "tab:orange"
C_Y = "tab:green"
C_NOW = "tab:purple"

TAU = np.linspace(-6.0, 6.0, 1601)
DT = TAU[1] - TAU[0]

def unit_step(t):
    return (np.asarray(t) >= 0).astype(float)

def rect_centered(t, width=2.0):
    t = np.asarray(t)
    return (np.abs(t) <= width / 2.0).astype(float)

def rect_causal(t, width=2.0):
    t = np.asarray(t)
    return ((t >= 0) & (t <= width)).astype(float)

def triangle_centered(t, width=4.0):
    t = np.asarray(t)
    return np.maximum(1.0 - np.abs(t) / (width / 2.0), 0.0)

SIGNALS = {
    "Rectangular pulse (centered)": lambda t: rect_centered(t, 2.0),
    "Wide rectangular pulse": lambda t: rect_centered(t, 4.0),
    "Causal rectangular pulse": lambda t: rect_causal(t, 2.0),
    "Triangular pulse": lambda t: triangle_centered(t, 4.0),
    "Gaussian exp(-t²)": lambda t: np.exp(-np.asarray(t) ** 2),
    "Decaying exponential e^(-t)u(t)": lambda t: np.exp(-np.maximum(np.asarray(t), 0)) * unit_step(t),
    "Unit step u(t)": lambda t: unit_step(t),
}

def sig(name, t):
    return np.asarray(SIGNALS[name](np.asarray(t)), dtype=float)

def convolution_output(x_name, h_name):
    x = sig(x_name, TAU)
    h = sig(h_name, TAU)
    y_full = np.convolve(x, h, mode="full") * DT
    t_full = np.linspace(TAU[0] + TAU[0], TAU[-1] + TAU[-1], len(y_full))
    return np.interp(TAU, t_full, y_full)

def render_chapter_header(title, subtitle):
    st.markdown(
        f"""
        <div style="text-align:center; padding:2.25rem 0 1.35rem 0;">
            <div style="
                font-family:Georgia,'Times New Roman',serif;
                font-size:clamp(2.8rem,5vw,4.9rem);
                font-weight:600;
                letter-spacing:.075em;
                line-height:1.08;">
                {title}
            </div>
            <div style="
                width:92px;height:2px;margin:1.1rem auto .9rem auto;
                background:currentColor;opacity:.30;"></div>
            <div style="
                font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
                font-size:1rem;opacity:.68;">
                {subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def format_axes(ax, title, xlabel):
    ax.set_title(title, fontsize=9, fontweight="bold", pad=5)
    ax.set_xlabel(xlabel, fontsize=7)
    ax.set_ylabel("Amplitude", fontsize=7)
    ax.tick_params(labelsize=6.5)
    ax.grid(True, alpha=0.25)
    ax.set_xlim(-6, 6)

def compact_live_figure(x_name, h_name, t_now):
    """Three vertically compact synchronized plots."""
    x_tau = sig(x_name, TAU)
    h_shift = sig(h_name, t_now - TAU)
    product = x_tau * h_shift
    y = convolution_output(x_name, h_name)

    area = float(np.trapezoid(product, TAU))
    y_now = float(np.interp(t_now, TAU, y))

    fig, axes = plt.subplots(3, 1, figsize=(8.7, 4.55))
    fig.subplots_adjust(hspace=0.72, left=0.09, right=0.98, top=0.96, bottom=0.09)

    ax = axes[0]
    ax.plot(TAU, x_tau, color=C_X, lw=2.0, label=r"$x(\tau)$")
    ax.plot(TAU, h_shift, color=C_H, lw=2.0, label=r"$h(t-\tau)$")
    overlap = (np.abs(x_tau) > 1e-9) & (np.abs(h_shift) > 1e-9)
    if np.any(overlap):
        ymax = np.minimum(np.abs(x_tau), np.abs(h_shift))
        ax.fill_between(TAU, 0, ymax, where=overlap, alpha=0.13)
    format_axes(ax, f"1. Slide and overlap     t = {t_now:.2f}", r"$\tau$")
    ax.legend(fontsize=6.5, ncol=2, loc="upper right")

    ax = axes[1]
    ax.plot(TAU, product, color=C_Y, lw=2.1, label=r"$x(\tau)h(t-\tau)$")
    ax.fill_between(TAU, 0, product, alpha=0.15)
    format_axes(ax, f"2. Multiply and integrate     y({t_now:.2f}) = {area:.3f}", r"$\tau$")
    ax.legend(fontsize=6.5, loc="upper right")

    ax = axes[2]
    future = TAU > t_now
    past = ~future
    ax.plot(TAU[future], y[future], color=C_Y, lw=1.5, alpha=0.22, label="future")
    ax.plot(TAU[past], y[past], color=C_Y, lw=2.2, label="built output")
    ax.scatter([t_now], [y_now], s=28, color=C_NOW, zorder=6, label="current point")
    ax.axvline(t_now, ls="--", lw=1.0, color=C_NOW, alpha=0.8)
    format_axes(ax, "3. Build the output  y(t) = x(t) * h(t)", "Time t")
    ax.legend(fontsize=6.5, ncol=3, loc="upper right")

    return fig, area, y_now

def mini_plot(series, title, xlabel=r"$\tau$"):
    """Small teaching plot used in Concept and Step-by-Step."""
    fig, ax = plt.subplots(figsize=(4.0, 1.85))
    for values, label, color, style, width in series:
        ax.plot(TAU, values, label=label, color=color, ls=style, lw=width)
    format_axes(ax, title, xlabel)
    ax.legend(fontsize=6.5, loc="upper right")
    fig.tight_layout(pad=0.65)
    st.pyplot(fig, clear_figure=True, use_container_width=True)

def worked_example():
    st.markdown("## Worked example — graphical convolution")
    st.write("Use two causal rectangular pulses:")
    e1, e2 = st.columns(2)
    with e1:
        st.latex(r"x(t)=u(t)-u(t-2)")
        st.caption("x(t) = 1 for 0 ≤ t ≤ 2")
    with e2:
        st.latex(r"h(t)=u(t)-u(t-3)")
        st.caption("h(t) = 1 for 0 ≤ t ≤ 3")

    x_tau = rect_causal(TAU, 2.0)
    h_tau = rect_causal(TAU, 3.0)
    h_flip = rect_causal(-TAU, 3.0)
    t_example = 2.0
    h_shift = rect_causal(t_example - TAU, 3.0)
    product = x_tau * h_shift
    area = float(np.trapezoid(product, TAU))

    st.markdown("### Step 1 — Flip  |  Step 2 — Shift")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.latex(r"h(\tau)\rightarrow h(-\tau)")
        mini_plot(
            [(h_tau, r"$h(\tau)$", C_H, "--", 1.4),
             (h_flip, r"$h(-\tau)$", C_H, "-", 2.1)],
            "Step 1 — Flip",
        )
    with c2:
        st.latex(r"h(-\tau)\rightarrow h(2-\tau)")
        mini_plot(
            [(h_flip, r"$h(-\tau)$", C_H, "--", 1.4),
             (h_shift, r"$h(2-\tau)$", C_H, "-", 2.1)],
            "Step 2 — Shift to t = 2",
        )

    st.markdown("### Step 3 — Overlay  |  Step 4 — Multiply")
    c3, c4 = st.columns(2, gap="large")
    with c3:
        st.latex(r"x(\tau)\ \text{and}\ h(2-\tau)")
        mini_plot(
            [(x_tau, r"$x(\tau)$", C_X, "-", 2.1),
             (h_shift, r"$h(2-\tau)$", C_H, "-", 2.1)],
            "Step 3 — Overlap",
        )
    with c4:
        st.latex(r"x(\tau)h(2-\tau)")
        mini_plot(
            [(product, r"$x(\tau)h(2-\tau)$", C_Y, "-", 2.2)],
            "Step 4 — Product",
        )

    st.markdown("### Step 5 — Integrate")
    st.latex(r"y(2)=\int_{-\infty}^{\infty}x(\tau)h(2-\tau)\,d\tau")
    st.latex(rf"\boxed{{y(2)={area:.2f}}}")
    st.success("At t = 2, the overlap has width 2 and height 1, so its area — and therefore y(2) — is 2.")

def render_live_lab():
    st.header("Live Convolution Lab")
    st.write(
        "Watch the same three quantities change together in real time: "
        "the sliding signals, their product, and the output being built."
    )

    c1, c2 = st.columns(2)
    with c1:
        x_name = st.selectbox("Input x(t)", list(SIGNALS), index=0, key="rt_x")
    with c2:
        h_name = st.selectbox("Impulse response h(t)", list(SIGNALS), index=1, key="rt_h")

    if "rt_t" not in st.session_state:
        st.session_state.rt_t = -5.0
    if "rt_playing" not in st.session_state:
        st.session_state.rt_playing = False
    if "rt_speed" not in st.session_state:
        st.session_state.rt_speed = 1.0

    b1, b2, b3, b4 = st.columns([1, 1, 1, 2])
    with b1:
        if st.button("↺ Reset", key="rt_reset", use_container_width=True):
            st.session_state.rt_t = -5.0
            st.session_state.rt_playing = False
    with b2:
        if st.button("▶ Play", key="rt_play", use_container_width=True):
            st.session_state.rt_playing = True
    with b3:
        if st.button("⏸ Pause", key="rt_pause", use_container_width=True):
            st.session_state.rt_playing = False
    with b4:
        st.session_state.rt_speed = st.select_slider(
            "Speed", options=[0.5, 1.0, 2.0], value=st.session_state.rt_speed, key="rt_speed_widget"
        )

    # Manual slider when paused.
    if not st.session_state.rt_playing:
        st.session_state.rt_t = st.slider(
            "Current time t", -5.0, 5.0, float(st.session_state.rt_t), 0.1, key="rt_manual_t"
        )

    # Native Streamlit animation area.
    chart = st.empty()
    values = st.empty()
    equation = st.empty()

    def paint(t_now):
        fig, area, y_now = compact_live_figure(x_name, h_name, t_now)
        chart.pyplot(fig, clear_figure=True, use_container_width=True)
        with values.container():
            m1, m2, m3 = st.columns(3)
            m1.metric("Current t", f"{t_now:.2f}")
            m2.metric("Overlap integral", f"{area:.4f}")
            m3.metric("Current y(t)", f"{y_now:.4f}")
        with equation.container():
            st.latex(
                rf"y({t_now:.2f})=\int_{{-\infty}}^{{\infty}}"
                rf"x(\tau)h({t_now:.2f}-\tau)\,d\tau\approx {area:.4f}"
            )

    paint(float(st.session_state.rt_t))

    if st.session_state.rt_playing:
        # Deliberately animate in this run so the three Matplotlib axes visibly update
        # in the same Streamlit placeholders. This is native Streamlit/Matplotlib,
        # not the HTML/JS format from the reference demo.
        step = 0.10
        delay = {0.5: 0.16, 1.0: 0.085, 2.0: 0.045}[float(st.session_state.rt_speed)]
        t0 = float(st.session_state.rt_t)
        for t_now in np.arange(t0, 5.0001, step):
            st.session_state.rt_t = float(t_now)
            paint(float(t_now))
            time.sleep(delay)
        st.session_state.rt_t = 5.0
        st.session_state.rt_playing = False
        st.success("Animation complete. Press Reset to run it again.")

def render_step_by_step():
    st.header("Step-by-Step")
    st.write("Freeze the process at one value of t and inspect each operation.")
    c1, c2 = st.columns(2)
    with c1:
        x_name = st.selectbox("Choose x(t)", list(SIGNALS), index=0, key="sb_x")
    with c2:
        h_name = st.selectbox("Choose h(t)", list(SIGNALS), index=1, key="sb_h")
    t_now = st.slider("Choose t", -5.0, 5.0, 0.0, 0.25, key="sb_t")

    x_tau = sig(x_name, TAU)
    h_tau = sig(h_name, TAU)
    h_flip = sig(h_name, -TAU)
    h_shift = sig(h_name, t_now - TAU)
    product = x_tau * h_shift
    area = float(np.trapezoid(product, TAU))
    y = convolution_output(x_name, h_name)

    r1, r2 = st.columns(2, gap="large")
    with r1:
        st.markdown("#### 1 — Flip")
        st.latex(r"h(\tau)\rightarrow h(-\tau)")
        mini_plot([(h_tau, r"$h(\tau)$", C_H, "--", 1.4),
                   (h_flip, r"$h(-\tau)$", C_H, "-", 2.1)], "Flip")
    with r2:
        st.markdown("#### 2 — Shift")
        st.latex(r"h(-\tau)\rightarrow h(t-\tau)")
        mini_plot([(h_flip, r"$h(-\tau)$", C_H, "--", 1.4),
                   (h_shift, r"$h(t-\tau)$", C_H, "-", 2.1)], f"Shift: t={t_now:.2f}")

    r3, r4 = st.columns(2, gap="large")
    with r3:
        st.markdown("#### 3 — Overlay")
        mini_plot([(x_tau, r"$x(\tau)$", C_X, "-", 2.1),
                   (h_shift, r"$h(t-\tau)$", C_H, "-", 2.1)], "Overlap")
    with r4:
        st.markdown("#### 4 — Multiply")
        mini_plot([(product, r"$x(\tau)h(t-\tau)$", C_Y, "-", 2.2)], "Product")

    st.markdown("#### 5 — Integrate")
    st.latex(rf"\boxed{{y({t_now:.2f})\approx {area:.4f}}}")

    _, center, _ = st.columns([1, 1.55, 1])
    with center:
        fig, ax = plt.subplots(figsize=(4.8, 2.0))
        ax.plot(TAU, y, color=C_Y, lw=2.1, label="y(t)")
        ax.scatter([t_now], [np.interp(t_now, TAU, y)], s=30, color=C_NOW, zorder=5)
        ax.axvline(t_now, ls="--", color=C_NOW, lw=1.0)
        format_axes(ax, "Complete convolution output", "Time t")
        ax.legend(fontsize=6.5)
        fig.tight_layout(pad=0.7)
        st.pyplot(fig, clear_figure=True, use_container_width=True)

def render_properties():
    st.header("Convolution Properties")
    props = [
        ("Commutative", r"x(t)*h(t)=h(t)*x(t)", "Interchanging x and h does not change the output."),
        ("Associative", r"[g*h]*x=g*[h*x]", "The grouping of cascaded convolutions does not change the result."),
        ("Distributive", r"x*[h_1+h_2]=x*h_1+x*h_2", "Parallel contributions may be handled separately."),
        ("Causal * Causal", r"x,h\text{ causal}\Rightarrow y\text{ causal}", "Two causal signals produce a causal convolution."),
        ("Time shift", r"h(t-T_1)*x(t-T_2)=y(t-T_1-T_2)", "The delays add in the output."),
        ("Impulse", r"x(t)*\delta(t-T)=x(t-T)", "A shifted impulse shifts the signal."),
        ("Area", r"A_y=A_xA_h", "The output area is the product of the input areas."),
        ("Step / Integration", r"x(t)*u(t)=\int_{-\infty}^{t}x(\tau)d\tau", "A unit-step impulse response performs integration."),
    ]
    for name, eq, desc in props:
        with st.expander(name):
            st.latex(eq)
            st.write(desc)

def render_practice():
    st.header("Practice")
    questions = [
        ("What is the first graphical operation applied to h(τ)?", ["Flip", "Shift", "Integrate"], "Flip"),
        ("After flipping, what produces h(t−τ)?", ["Scale", "Shift", "Differentiate"], "Shift"),
        ("What becomes one point of y(t)?", ["Overlap integral", "Peak only", "Signal width only"], "Overlap integral"),
        ("Does x*h equal h*x?", ["Yes", "No"], "Yes"),
    ]
    for i, (q, opts, ans) in enumerate(questions):
        st.markdown(f"### {i+1}. {q}")
        choice = st.radio("Answer", opts, index=None, horizontal=True, key=f"pr_{i}")
        if st.button("Check answer", key=f"pr_check_{i}"):
            if choice == ans:
                st.success("✓ Correct")
            else:
                st.error(f"✗ Incorrect — Correct answer: {ans}")

def render():
    render_chapter_header(
        "CONVOLUTION",
        "Signals and Systems | Graphical intuition, real-time convolution, and step-by-step analysis",
    )

    concept, live, steps, properties, practice = st.tabs(
        ["Concept", "Live Convolution Lab", "Step-by-Step", "Properties", "Practice"]
    )

    with concept:
        st.subheader("What is convolution?")
        st.write("For an LTI system, the output is obtained by convolving the input with the impulse response.")
        st.latex(r"\boxed{y(t)=x(t)*h(t)=\int_{-\infty}^{\infty}x(\tau)h(t-\tau)\,d\tau}")
        worked_example()

    with live:
        render_live_lab()

    with steps:
        render_step_by_step()

    with properties:
        render_properties()

    with practice:
        render_practice()

    st.divider()
    st.caption("EE-207 Convolution Module — Watch the process, then analyze it mathematically.")
