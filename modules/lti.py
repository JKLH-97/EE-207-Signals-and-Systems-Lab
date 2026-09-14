import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ---------- Core signal definitions ----------
def unit_step(t):
    return (t >= 0).astype(float)

def get_signal(name, t):
    if name == "sin(t)": return np.sin(t)
    if name == "cos(2t)": return np.cos(2*t)
    if name == "Gaussian exp(-t²)": return np.exp(-t**2)
    if name == "Rectangular pulse": return (np.abs(t) <= 1).astype(float)
    if name == "Triangular pulse": return np.maximum(1-np.abs(t), 0)
    if name == "Unit step u(t)": return unit_step(t)
    if name == "Decaying exponential e^(-t)u(t)": return np.exp(-t)*unit_step(t)
    raise ValueError("Unknown signal")

def apply_system(name, t, x_func):
    x = x_func(t)
    if name == "y(t) = 3x(t)": return 3*x
    if name == "y(t) = 3x(t) + 1": return 3*x + 1
    if name == "y(t) = t x(t)": return t*x
    if name == "y(t) = x(-t)": return x_func(-t)
    if name == "y(t) = x(t)u(t)": return x*unit_step(t)
    if name == "y(t) = sin[x(t)]": return np.sin(x)
    if name == "y(t) = x(t - 1)": return x_func(t-1)
    if name == "y(t) = dx(t)/dt":
        dt = t[1]-t[0]
        return np.gradient(x, dt)
    raise ValueError("Unknown system")

SIGNALS = ["sin(t)", "cos(2t)", "Gaussian exp(-t²)", "Rectangular pulse", "Triangular pulse", "Unit step u(t)", "Decaying exponential e^(-t)u(t)"]
SYSTEMS = ["y(t) = 3x(t)", "y(t) = 3x(t) + 1", "y(t) = t x(t)", "y(t) = x(-t)", "y(t) = x(t)u(t)", "y(t) = sin[x(t)]", "y(t) = x(t - 1)", "y(t) = dx(t)/dt"]
KNOWN = {
    "y(t) = 3x(t)": (True, True),
    "y(t) = 3x(t) + 1": (False, True),
    "y(t) = t x(t)": (True, False),
    "y(t) = x(-t)": (True, False),
    "y(t) = x(t)u(t)": (True, False),
    "y(t) = sin[x(t)]": (False, True),
    "y(t) = x(t - 1)": (True, True),
    "y(t) = dx(t)/dt": (True, True),
}

t = np.linspace(-6, 6, 2401)

# ---------- Consistent visual language ----------
# x1-related quantities stay blue, x2-related quantities stay orange.
# Newly produced combined/final results use green.
C_X1 = "tab:blue"
C_X2 = "tab:orange"
C_RESULT = "tab:green"
C_PATH2 = "tab:purple"
C_INPUT = "tab:blue"

def finish_plot(title):
    plt.title(title)
    plt.xlabel("Time t")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=.3)
    plt.legend()
    plt.xlim(-6, 6)
    plt.tight_layout()

SIGNAL_LATEX = {
    "sin(t)": r"\sin(t)",
    "cos(2t)": r"\cos(2t)",
    "Gaussian exp(-t²)": r"e^{-t^2}",
    "Rectangular pulse": r"\operatorname{rect}(t/2)",
    "Triangular pulse": r"\max(1-|t|,0)",
    "Unit step u(t)": r"u(t)",
    "Decaying exponential e^(-t)u(t)": r"e^{-t}u(t)",
}

def fmt_num(v):
    if abs(v-round(v)) < 1e-12:
        return str(int(round(v)))
    return f"{v:.2f}".rstrip("0").rstrip(".")

def signal_eq(name):
    return SIGNAL_LATEX[name]

def system_of_expr(system_name, expr, var="t"):
    if system_name == "y(t) = 3x(t)": return rf"3\left[{expr}\right]"
    if system_name == "y(t) = 3x(t) + 1": return rf"3\left[{expr}\right]+1"
    if system_name == "y(t) = t x(t)": return rf"{var}\left[{expr}\right]"
    if system_name == "y(t) = x(-t)": return rf"\left.{expr}\right|_{{t\to -t}}"
    if system_name == "y(t) = x(t)u(t)": return rf"\left[{expr}\right]u({var})"
    if system_name == "y(t) = sin[x(t)]": return rf"\sin\!\left({expr}\right)"
    if system_name == "y(t) = x(t - 1)": return rf"\left.{expr}\right|_{{t\to t-1}}"
    if system_name == "y(t) = dx(t)/dt": return rf"\frac{{d}}{{dt}}\left[{expr}\right]"
    return rf"T\{{{expr}\}}"

def small_plot(series, title):
    fig, ax = plt.subplots(figsize=(4.8, 2.45))
    for y, label, color, style, width in series:
        ax.plot(t, y, linestyle=style, color=color, linewidth=width, label=label)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("Time t", fontsize=9)
    ax.set_ylabel("Amplitude", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.grid(True, alpha=.3)
    ax.legend(fontsize=8)
    ax.set_xlim(-6,6)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True, use_container_width=True)



def render_time_invariance_experiment(system_name, signal_name, t0, key_prefix="ti"):
    """Render the time-invariance test in two-column, step-by-step format."""
    xf = lambda z: get_signal(signal_name, z)
    xd = lambda z: xf(z - t0)
    y = apply_system(system_name, t, xf)
    path1 = apply_system(system_name, t, xd)
    path2 = apply_system(system_name, t - t0, xf)

    sig_current = signal_eq(signal_name)
    delayed_current = rf"\left.{sig_current}\right|_{{t\to t-{fmt_num(t0)}}}"

    st.markdown("#### Path 1 — Delay the input first, then apply the system")
    st.latex(r"\boxed{y_{P1}(t)=T\{x(t-t_0)\}}")
    st.latex(rf"\text{{Current example:}}\quad y_{{P1}}(t)={system_of_expr(system_name, delayed_current)}")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("##### Step 1 — Original input")
        st.latex(rf"x(t)={sig_current}")
        small_plot([(xf(t), "x(t)", C_INPUT, "-", 2.5)], "Original input")
    with c2:
        st.markdown("##### Step 2 — Delay the input")
        st.latex(rf"x_d(t)=x(t-{fmt_num(t0)})")
        small_plot([
            (xf(t), "previous: x(t)", C_INPUT, "--", 1.8),
            (xd(t), "new: x(t-t0)", C_RESULT, "-", 2.7),
        ], "Delayed input")

    st.markdown("##### Final — Apply the system")
    _, c3, _ = st.columns([1, 1.65, 1], gap="large")
    with c3:
        st.latex(r"y_{P1}(t)=T\{x(t-t_0)\}")
        small_plot([
            (xd(t), "previous: delayed input", C_RESULT, "--", 1.8),
            (path1, "new: Path 1 output", C_RESULT, "-", 2.8),
        ], "Path 1 final output")
    st.markdown("##### Path 1 — Final result")
    st.latex(rf"\boxed{{y_{{P1}}(t)={system_of_expr(system_name, delayed_current)}}}")

    st.markdown("---")
    st.markdown("#### Path 2 — Apply the system first, then delay the output")
    st.latex(r"\boxed{y_{P2}(t)=y(t-t_0),\qquad y(t)=T\{x(t)\}}")
    st.latex(rf"\text{{Current example:}}\quad y(t)={system_of_expr(system_name, sig_current)}")

    c4, c5 = st.columns(2, gap="large")
    with c4:
        st.markdown("##### Step 1 — Original input")
        st.latex(rf"x(t)={sig_current}")
        small_plot([(xf(t), "x(t)", C_INPUT, "-", 2.5)], "Original input")
    with c5:
        st.markdown("##### Step 2 — Apply the system")
        st.latex(r"y(t)=T\{x(t)\}")
        small_plot([
            (xf(t), "previous: x(t)", C_INPUT, "--", 1.8),
            (y, "new: y(t)", C_PATH2, "-", 2.7),
        ], "System output")

    st.markdown("##### Final — Delay the output")
    _, c6, _ = st.columns([1, 1.65, 1], gap="large")
    with c6:
        st.latex(rf"y_{{P2}}(t)=y(t-{fmt_num(t0)})")
        small_plot([
            (y, "previous: y(t)", C_PATH2, "--", 1.8),
            (path2, "new: Path 2 output", C_RESULT, "-", 2.8),
        ], "Path 2 final output")
    st.markdown("##### Path 2 — Final result")
    st.latex(rf"\boxed{{y_{{P2}}(t)=y(t-{fmt_num(t0)})}}")

    st.markdown("### Step 3 — Compare the two paths")
    maxerr = float(np.max(np.abs(path1 - path2)))
    relation = r"=" if maxerr <= 1e-6 else r"\ne"
    st.latex(rf"\boxed{{y_{{P1}}(t)\;{relation}\;y_{{P2}}(t)}}")
    fig, ax = plt.subplots(figsize=(6.2, 2.55))
    ax.plot(t, path1, color=C_RESULT, linewidth=2.7, label="Path 1")
    ax.plot(t, path2, "--", color=C_PATH2, linewidth=2.2, label="Path 2")
    ax.set_title("MATCH" if maxerr <= 1e-6 else "MISMATCH", fontweight="bold")
    ax.set_xlabel("Time t"); ax.set_ylabel("Amplitude")
    ax.grid(True, alpha=.3); ax.legend(); ax.set_xlim(-6,6)
    fig.tight_layout()
    _, cmp_col, _ = st.columns([1, 1.75, 1])
    with cmp_col:
        st.pyplot(fig, clear_figure=True, use_container_width=True)
    return maxerr



def render():

    st.markdown(
        """
        <div style="text-align:center; padding:2.35rem 0 1.45rem 0;">
            <div style="
                font-family: Georgia, 'Times New Roman', serif;
                font-size: clamp(2.8rem, 5vw, 4.9rem);
                font-weight: 600;
                letter-spacing: 0.075em;
                line-height: 1.08;
                color: inherit;">
                LTI SYSTEMS
            </div>
            <div style="
                width:92px; height:2px; margin:1.15rem auto 0.95rem auto;
                background:currentColor; opacity:0.32;"></div>
            <div style="
                font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                font-size:1rem; font-weight:400; letter-spacing:0.015em; opacity:0.68;">
                Signals and Systems | Explore linearity and time invariance graphically
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    def reveal_cards(linear=None, time_invariant=None, lti=None):
        """Show large YES/NO answer cards consistently in every lab."""
        items = []
        if linear is not None:
            items.append(("Linear", "YES" if linear else "NO"))
        if time_invariant is not None:
            items.append(("Time-Invariant", "YES" if time_invariant else "NO"))
        if lti is not None:
            items.append(("LTI", "YES" if lti else "NO"))
        cols = st.columns(len(items))
        for col, (label, value) in zip(cols, items):
            col.metric(label, value)
    
    
    def safe_custom_expr(expr, time_values, x_values=None):
        allowed = {
            "np": np, "t": time_values, "sin": np.sin, "cos": np.cos,
            "exp": np.exp, "sqrt": np.sqrt, "abs": np.abs,
            "where": np.where, "pi": np.pi,
            "u": lambda z: (np.asarray(z) >= 0).astype(float),
        }
        if x_values is not None:
            allowed["x"] = x_values
        value = eval(expr, {"__builtins__": {}}, allowed)
        arr = np.asarray(value, dtype=float)
        if arr.ndim == 0:
            arr = np.full_like(time_values, float(arr), dtype=float)
        return np.broadcast_to(arr, time_values.shape).astype(float)
    
    def custom_apply(expr, time_values, input_values):
        return safe_custom_expr(expr, time_values, input_values)
    
    def custom_compare_plot(path1, path2, title):
        fig, ax = plt.subplots(figsize=(6.2,2.55))
        ax.plot(t,path1,color=C_RESULT,linewidth=2.6,label="Path 1")
        ax.plot(t,path2,"--",color=C_PATH2,linewidth=2.1,label="Path 2")
        ax.set_title(title,fontweight="bold")
        ax.set_xlabel("Time t"); ax.set_ylabel("Amplitude")
        ax.grid(True,alpha=.3); ax.legend(); ax.set_xlim(-6,6); fig.tight_layout()
        _, cc, _ = st.columns([1,1.75,1])
        with cc:
            st.pyplot(fig,clear_figure=True,use_container_width=True)
    
    intro, linear_tab, time_tab, challenge_tab, custom_tab, quiz_tab = st.tabs(["Concept", "Linearity Lab", "Time-Invariance Lab", "LTI Lab", "System Grapher", "Mini Exam"])
    
    with intro:
        st.subheader("What makes a system LTI?")
    
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 1. Linearity")
            st.latex(r"T\{a x_1(t)+b x_2(t)\}=aT\{x_1(t)\}+bT\{x_2(t)\}")
            st.write("The order of **combining/scaling** and **applying the system** must not matter.")
        with c2:
            st.markdown("### 2. Time Invariance")
            st.latex(r"T\{x(t-t_0)\}=y(t-t_0),\qquad y(t)=T\{x(t)\}")
            st.write("The order of **delaying** and **applying the system** must not matter.")
    
        st.markdown("### LTI requirement")
        st.latex(r"\boxed{\text{LTI}=\text{Linear AND Time-Invariant}}")
    
        st.divider()
        st.markdown("## Examples")
        st.write("Use the labs to test the following examples.")
    
        e1, e2 = st.columns(2, gap="large")
        with e1:
            st.markdown("### Linearity")
            st.write("Try this system and verify that it is **linear**:")
            st.latex(r"T\{x(t)\}=3x(t)")
            st.write("Try this system and verify that it is **nonlinear**:")
            st.latex(r"T\{x(t)\}=3x(t)+1")
        with e2:
            st.markdown("### Time Invariance")
            st.write("Try this system and verify that it is **time-invariant**:")
            st.latex(r"T\{x(t)\}=2x(t-1)-x(t+2)")
            st.write("Try this system and verify that it is **time-varying**:")
            st.latex(r"T\{x(t)\}=t\,x(t)")
    
        st.markdown("### LTI")
        l1, l2 = st.columns(2, gap="large")
        with l1:
            st.write("Try this system and verify that it is **LTI**:")
            st.latex(r"T\{x(t)\}=3\frac{d}{dt}x(t-1)+2x(t+2)")
        with l2:
            st.write("Try this system and verify that it is **not LTI**:")
            st.latex(r"T\{x(t)\}=x(-t)+2x(t)")
    
    with linear_tab:
        st.header("Linearity Lab — Superposition Test")
        st.latex(r"\text{Path A}=T\{a x_1+b x_2\}\qquad\text{vs.}\qquad\text{Path B}=aT\{x_1\}+bT\{x_2\}")
    
        st.markdown("### Step 1 — Choose the experiment")
        c1, c2, c3 = st.columns(3)
        with c1: lin_sys_choice = st.selectbox("Choose the system", SYSTEMS, index=0, key="lin_sys_choice")
        with c2: lin_s1_choice = st.selectbox("Choose x₁(t)", SIGNALS, index=SIGNALS.index("Unit step u(t)"), key="lin_s1_choice")
        with c3: lin_s2_choice = st.selectbox("Choose x₂(t)", SIGNALS, index=SIGNALS.index("Unit step u(t)"), key="lin_s2_choice")
        ca, cb = st.columns(2)
        with ca: lin_a_choice = st.slider("Coefficient a", -5.0, 5.0, 2.0, 0.25, key="lin_a_choice")
        with cb: lin_b_choice = st.slider("Coefficient b", -5.0, 5.0, 1.0, 0.25, key="lin_b_choice")
    
        if st.button("Confirm system and inputs", type="primary", key="confirm_linearity"):
            st.session_state.lin_confirmed = {
                "system": lin_sys_choice, "s1": lin_s1_choice, "s2": lin_s2_choice,
                "a": lin_a_choice, "b": lin_b_choice
            }
    
        if "lin_confirmed" not in st.session_state:
            st.info("Choose the system and input signals, then click **Confirm system and inputs** to start the experiment.")
        else:
            cfg = st.session_state.lin_confirmed
            sys_l, s1, s2, a, b = cfg["system"], cfg["s1"], cfg["s2"], cfg["a"], cfg["b"]
    
            st.markdown("### Step 2 — Build both paths graphically, step by step")
            d1, d2, d3 = st.columns(3)
            d1.markdown(f"**System**  \n`{sys_l}`")
            d2.markdown(f"**Input 1**  \n`x₁(t) = {s1}`")
            d3.markdown(f"**Input 2**  \n`x₂(t) = {s2}`")
            st.markdown(f"**Selected coefficients:**  a = `{a:.2f}`, b = `{b:.2f}`")
    
            if sys_l == "y(t) = 3x(t) + 1" and abs((a + b) - 1.0) < 1e-12:
                st.warning("Special case: for y(t)=3x(t)+1, choosing a+b=1 can make this particular superposition test match even though the system is nonlinear. Change a or b (for example, a=2 and b=1) to expose the nonlinearity.")
    
            x1 = lambda z: get_signal(s1, z)
            x2 = lambda z: get_signal(s2, z)
            xc = lambda z: a*x1(z)+b*x2(z)
            y1 = apply_system(sys_l, t, x1)
            y2 = apply_system(sys_l, t, x2)
    
            e1, e2 = signal_eq(s1), signal_eq(s2)
            aa, bb = fmt_num(a), fmt_num(b)
            combined_expr = rf"{aa}\left[{e1}\right]+{bb}\left[{e2}\right]"
    
            st.markdown("#### Path 1 — Scale and add the inputs first, then apply the system")
            st.latex(r"\boxed{y_{P1}(t)=T\{a x_1(t)+b x_2(t)\}}")
            st.markdown("**Current example:**")
            st.latex(rf"y_{{P1}}(t)=T\{{{combined_expr}\}}={system_of_expr(sys_l, combined_expr)}")
    
            p1c1, p1c2 = st.columns(2, gap="large")
            with p1c1:
                st.markdown("##### Step 1 — Original first input")
                st.latex(r"x_1(t)")
                st.latex(rf"x_1(t)={e1}")
                small_plot([(x1(t),"x1(t)",C_X1,"-",2.5)], "Original x1(t)")
            with p1c2:
                st.markdown("##### Step 2 — Scale the first input")
                st.latex(r"a x_1(t)")
                st.latex(rf"{aa}x_1(t)={aa}\left[{e1}\right]")
                small_plot([(x1(t),"previous: x1(t)",C_X1,"--",1.7),(a*x1(t),f"new: {aa} x1(t)",C_X1,"-",2.6)], "Scale x1(t)")
    
            p1c3, p1c4 = st.columns(2, gap="large")
            with p1c3:
                st.markdown("##### Step 3 — Original second input")
                st.latex(r"x_2(t)")
                st.latex(rf"x_2(t)={e2}")
                small_plot([(x2(t),"x2(t)",C_X2,"-",2.5)], "Original x2(t)")
            with p1c4:
                st.markdown("##### Step 4 — Scale the second input")
                st.latex(r"b x_2(t)")
                st.latex(rf"{bb}x_2(t)={bb}\left[{e2}\right]")
                small_plot([(x2(t),"previous: x2(t)",C_X2,"--",1.7),(b*x2(t),f"new: {bb} x2(t)",C_X2,"-",2.6)], "Scale x2(t)")
    
            path1=apply_system(sys_l,t,xc)
            p1c5, p1c6 = st.columns(2, gap="large")
            with p1c5:
                st.markdown("##### Step 5 — Add the scaled inputs")
                st.latex(r"v(t)=a x_1(t)+b x_2(t)")
                st.latex(rf"v(t)={combined_expr}")
                small_plot([(a*x1(t),f"{aa} x1(t)",C_X1,"--",1.7),(b*x2(t),f"{bb} x2(t)",C_X2,"--",1.7),(xc(t),"new: v(t)",C_RESULT,"-",2.7)], "Combined input v(t)")
            with p1c6:
                st.markdown("##### Final — Apply the system")
                st.latex(r"y_{P1}(t)=T\{v(t)\}")
                st.latex(rf"y_{{P1}}(t)={system_of_expr(sys_l, combined_expr)}")
                small_plot([(xc(t),"previous: v(t)",C_RESULT,"--",1.7),(path1,"new: Path 1 output",C_RESULT,"-",2.7)], "Path 1 final output")
    
            # Show the fully substituted Path 1 result before starting Path 2.
            st.markdown("##### Path 1 — Final equation for the selected example")
            st.latex(rf"\boxed{{y_{{P1}}(t)={system_of_expr(sys_l, combined_expr)}}}")
    
            st.markdown("---")
            st.markdown("#### Path 2 — Apply the system first, then scale and add the outputs")
            st.latex(r"\boxed{y_{P2}(t)=aT\{x_1(t)\}+bT\{x_2(t)\}}")
            y1_expr=system_of_expr(sys_l,e1)
            y2_expr=system_of_expr(sys_l,e2)
            st.markdown("**Current example:**")
            st.latex(rf"y_{{P2}}(t)={aa}\left[{y1_expr}\right]+{bb}\left[{y2_expr}\right]")
    
            p2c1, p2c2 = st.columns(2, gap="large")
            with p2c1:
                st.markdown("##### Step 1 — Apply the system to x1(t)")
                st.latex(r"y_1(t)=T\{x_1(t)\}")
                st.latex(rf"y_1(t)={y1_expr}")
                small_plot([(x1(t),"previous: x1(t)",C_X1,"--",1.7),(y1,"new: T{x1(t)}",C_X1,"-",2.6)], "System applied to x1(t)")
            with p2c2:
                st.markdown("##### Step 2 — Scale the first output")
                st.latex(r"a y_1(t)=aT\{x_1(t)\}")
                st.latex(rf"{aa}y_1(t)={aa}\left[{y1_expr}\right]")
                small_plot([(y1,"previous: T{x1(t)}",C_X1,"--",1.7),(a*y1,f"new: {aa}T{{x1}}",C_X1,"-",2.6)], "Scale first output")
    
            p2c3, p2c4 = st.columns(2, gap="large")
            with p2c3:
                st.markdown("##### Step 3 — Apply the system to x2(t)")
                st.latex(r"y_2(t)=T\{x_2(t)\}")
                st.latex(rf"y_2(t)={y2_expr}")
                small_plot([(x2(t),"previous: x2(t)",C_X2,"--",1.7),(y2,"new: T{x2(t)}",C_X2,"-",2.6)], "System applied to x2(t)")
            with p2c4:
                st.markdown("##### Step 4 — Scale the second output")
                st.latex(r"b y_2(t)=bT\{x_2(t)\}")
                st.latex(rf"{bb}y_2(t)={bb}\left[{y2_expr}\right]")
                small_plot([(y2,"previous: T{x2(t)}",C_X2,"--",1.7),(b*y2,f"new: {bb}T{{x2}}",C_X2,"-",2.6)], "Scale second output")
    
            path2=a*y1+b*y2
            st.markdown("##### Final — Add the scaled outputs")
            _, pf1, _ = st.columns([1, 1.65, 1], gap="large")
            with pf1:
                st.latex(r"y_{P2}(t)=aT\{x_1(t)\}+bT\{x_2(t)\}")
                st.latex(rf"y_{{P2}}(t)={aa}\left[{y1_expr}\right]+{bb}\left[{y2_expr}\right]")
                small_plot([(a*y1,f"{aa}T{{x1}}",C_X1,"--",1.7),(b*y2,f"{bb}T{{x2}}",C_X2,"--",1.7),(path2,"new: Path 2 output",C_RESULT,"-",2.7)], "Path 2 final output")
    
            st.markdown("##### Path 2 — Final equation for the selected example")
            _, eq_p2_col, _ = st.columns([1, 1.65, 1])
            with eq_p2_col:
                st.latex(rf"\boxed{{y_{{P2}}(t)={aa}\left[{y1_expr}\right]+{bb}\left[{y2_expr}\right]}}")
    
            st.markdown("### Step 3 — Compare the two paths")
            lin_err = float(np.max(np.abs(path1-path2)))
            lin_relation = r"=" if lin_err <= 1e-6 else r"\ne"
            st.latex(rf"\boxed{{y_{{P1}}(t)\;{lin_relation}\;y_{{P2}}(t)}}")
            fig_cmp, ax_cmp = plt.subplots(figsize=(6.2, 2.55))
            ax_cmp.plot(t, path1, color=C_RESULT, linewidth=2.5, label="Path 1")
            ax_cmp.plot(t, path2, "--", color=C_PATH2, linewidth=2.0, label="Path 2")
            ax_cmp.set_title("MATCH" if lin_err <= 1e-6 else "MISMATCH", fontsize=11, fontweight="bold")
            ax_cmp.set_xlabel("Time t", fontsize=9)
            ax_cmp.set_ylabel("Amplitude", fontsize=9)
            ax_cmp.tick_params(labelsize=8)
            ax_cmp.grid(True, alpha=.3)
            ax_cmp.legend(fontsize=8)
            ax_cmp.set_xlim(-6,6)
            fig_cmp.tight_layout()
            _, cmp_col, _ = st.columns([1, 1.75, 1])
            with cmp_col:
                st.pyplot(fig_cmp, clear_figure=True, use_container_width=True)
    
            st.markdown("### Step 4 — Predict and reveal")
            pred_l = st.radio("Before revealing the classification, predict:", ["Linear", "Nonlinear"], horizontal=True, key="pred_l")
            if st.button("Reveal answer", type="primary", key="reveal_l"):
                truth = KNOWN[sys_l][0]
                correct = (pred_l == ("Linear" if truth else "Nonlinear"))
                classification = "LINEAR" if truth else "NONLINEAR"
                if correct:
                    st.success(f"✓ Correct — The system is {classification}.")
                else:
                    st.error(f"✗ Incorrect — The system is {classification}.")
                if (not truth) and sys_l == "y(t) = 3x(t) + 1":
                    st.write("The constant +1 breaks the superposition property. A linear system must also satisfy T{0}=0.")
    
    
    with time_tab:
        st.header("Time-Invariance Lab — Delay Test")
        st.latex(r"T\{x(t-t_0)\}\stackrel{?}{=}y(t-t_0),\qquad y(t)=T\{x(t)\}")
        st.markdown("### Step 1 — Choose the experiment")
        c1, c2 = st.columns(2)
        with c1:
            ti_sys_choice = st.selectbox("Choose the system", SYSTEMS, index=0, key="ti_sys_choice")
        with c2:
            ti_sig_choice = st.selectbox("Choose x(t)", SIGNALS, index=SIGNALS.index("Unit step u(t)"), key="ti_sig_choice")
        ti_t0_choice = st.slider("Delay t₀", -5.0, 5.0, 2.0, 0.25, key="ti_t0_choice")
    
        if st.button("Confirm system and input", type="primary", key="confirm_ti"):
            st.session_state.ti_confirmed = {"system": ti_sys_choice, "signal": ti_sig_choice, "t0": ti_t0_choice}
    
        if "ti_confirmed" not in st.session_state:
            st.info("Choose the system, input signal, and delay, then click **Confirm system and input**.")
        else:
            cfg = st.session_state.ti_confirmed
            sys_t, sig_t, t0 = cfg["system"], cfg["signal"], cfg["t0"]
            st.markdown("### Step 2 — Build both paths graphically")
            d1, d2, d3 = st.columns(3)
            d1.markdown(f"**System**  \n`{sys_t}`")
            d2.markdown(f"**Input**  \n`x(t) = {sig_t}`")
            d3.markdown(f"**Delay**  \n`t₀ = {t0:.2f}`")
    
            maxerrt = render_time_invariance_experiment(sys_t, sig_t, t0, "ti")
    
            st.markdown("### Step 4 — Predict and reveal")
            pred_t = st.radio("Before revealing the classification, predict:", ["Time-invariant", "Time-varying"], horizontal=True, key="pred_t")
            if st.button("Reveal answer", type="primary", key="reveal_t"):
                truth = KNOWN[sys_t][1]
                correct = (pred_t == ("Time-invariant" if truth else "Time-varying"))
                classification = "TIME-INVARIANT" if truth else "TIME-VARYING"
                if correct:
                    st.success(f"✓ Correct — The system is {classification}.")
                else:
                    st.error(f"✗ Incorrect — The system is {classification}.")
    
    
    with challenge_tab:
        st.header("LTI Lab")
        st.write("Choose the complete experiment. You can change the system, x₁(t), x₂(t), the coefficients a and b, and the delay t₀.")
    
        st.markdown("### Step 1 — Choose the experiment")
        r1, r2, r3 = st.columns(3)
        with r1:
            ch_sys_choice = st.selectbox("Choose the system", SYSTEMS, key="challenge_sys_choice")
        with r2:
            ch_x1_choice = st.selectbox("Choose x₁(t)", SIGNALS, index=SIGNALS.index("Unit step u(t)"), key="challenge_x1")
        with r3:
            ch_x2_choice = st.selectbox("Choose x₂(t)", SIGNALS, index=SIGNALS.index("Unit step u(t)"), key="challenge_x2")
    
        r4, r5, r6 = st.columns(3)
        with r4:
            ch_a_choice = st.slider("Coefficient a", -5.0, 5.0, 2.0, 0.25, key="challenge_a")
        with r5:
            ch_b_choice = st.slider("Coefficient b", -5.0, 5.0, 1.0, 0.25, key="challenge_b")
        with r6:
            ch_t0_choice = st.slider("Delay t₀", -5.0, 5.0, 2.0, 0.25, key="challenge_t0")
    
        if st.button("Confirm LTI example", type="primary", key="confirm_challenge"):
            st.session_state.challenge_confirmed = {
                "system": ch_sys_choice, "x1": ch_x1_choice, "x2": ch_x2_choice,
                "a": ch_a_choice, "b": ch_b_choice, "t0": ch_t0_choice
            }
    
        if "challenge_confirmed" not in st.session_state:
            st.info("Choose the system, x₁(t), x₂(t), a, b, and t₀, then click **Confirm LTI example**.")
        else:
            cfg = st.session_state.challenge_confirmed
            csys = cfg["system"]; cx1_name = cfg["x1"]; cx2_name = cfg["x2"]
            ca = cfg["a"]; cb = cfg["b"]; ct0 = cfg["t0"]
    
            st.markdown("### Step 2 — Linearity test")
            st.latex(r"T\{a x_1(t)+b x_2(t)\}\stackrel{?}{=}aT\{x_1(t)\}+bT\{x_2(t)\}")
            st.caption(f"Current example: a = {fmt_num(ca)}, b = {fmt_num(cb)}, x₁(t) = {cx1_name}, x₂(t) = {cx2_name}")
    
            cx1 = lambda z: get_signal(cx1_name, z)
            cx2 = lambda z: get_signal(cx2_name, z)
            cxc = lambda z: ca*cx1(z) + cb*cx2(z)
            cy1 = apply_system(csys, t, cx1); cy2 = apply_system(csys, t, cx2)
            cP1 = apply_system(csys, t, cxc)
            cP2 = ca*cy1 + cb*cy2
    
            # Linearity Path 1
            st.markdown("#### Path 1 — Scale and add the inputs first, then apply the system")
            st.latex(r"\boxed{y_{P1}(t)=T\{a x_1(t)+b x_2(t)\}}")
            st.latex(rf"\text{{Current example:}}\quad y_{{P1}}(t)={system_of_expr(csys, rf'{fmt_num(ca)}[{signal_eq(cx1_name)}]+{fmt_num(cb)}[{signal_eq(cx2_name)}]')}")
            l1, l2 = st.columns(2, gap="large")
            with l1:
                st.latex(rf"a x_1(t)={fmt_num(ca)}[{signal_eq(cx1_name)}]")
                small_plot([(cx1(t), "previous: x1(t)", C_X1, "--", 1.7), (ca*cx1(t), "new: a x1(t)", C_X1, "-", 2.6)], "Scale x1")
            with l2:
                st.latex(rf"b x_2(t)={fmt_num(cb)}[{signal_eq(cx2_name)}]")
                small_plot([(cx2(t), "previous: x2(t)", C_X2, "--", 1.7), (cb*cx2(t), "new: b x2(t)", C_X2, "-", 2.6)], "Scale x2")
            l3, l4 = st.columns(2, gap="large")
            with l3:
                st.latex(r"v(t)=a x_1(t)+b x_2(t)")
                small_plot([(ca*cx1(t), "a x1(t)", C_X1, "--", 1.8), (cb*cx2(t), "b x2(t)", C_X2, "--", 1.8), (cxc(t), "new: v(t)", C_RESULT, "-", 2.7)], "Combined input")
            with l4:
                st.latex(r"y_{P1}(t)=T\{v(t)\}")
                small_plot([(cxc(t), "previous: v(t)", C_RESULT, "--", 1.8), (cP1, "new: Path 1", C_RESULT, "-", 2.8)], "Path 1 final output")
            st.latex(rf"\boxed{{y_{{P1}}(t)={system_of_expr(csys, rf'{fmt_num(ca)}[{signal_eq(cx1_name)}]+{fmt_num(cb)}[{signal_eq(cx2_name)}]')}}}")
    
            # Linearity Path 2
            st.markdown("#### Path 2 — Apply the system first, then scale and add the outputs")
            st.latex(r"\boxed{y_{P2}(t)=aT\{x_1(t)\}+bT\{x_2(t)\}}")
            p21, p22 = st.columns(2, gap="large")
            with p21:
                st.latex(r"T\{x_1(t)\}")
                small_plot([(cx1(t), "previous: x1(t)", C_X1, "--", 1.7), (cy1, "new: T{x1}", C_X1, "-", 2.6)], "System applied to x1")
            with p22:
                st.latex(r"T\{x_2(t)\}")
                small_plot([(cx2(t), "previous: x2(t)", C_X2, "--", 1.7), (cy2, "new: T{x2}", C_X2, "-", 2.6)], "System applied to x2")
            p23, p24 = st.columns(2, gap="large")
            with p23:
                st.latex(r"aT\{x_1(t)\}\quad\text{and}\quad bT\{x_2(t)\}")
                small_plot([(cy1, "T{x1}", C_X1, "--", 1.7), (ca*cy1, "aT{x1}", C_X1, "-", 2.6), (cy2, "T{x2}", C_X2, "--", 1.7), (cb*cy2, "bT{x2}", C_X2, "-", 2.6)], "Scale system outputs")
            with p24:
                st.latex(r"y_{P2}(t)=aT\{x_1(t)\}+bT\{x_2(t)\}")
                small_plot([(ca*cy1, "aT{x1}", C_X1, "--", 1.8), (cb*cy2, "bT{x2}", C_X2, "--", 1.8), (cP2, "new: Path 2", C_RESULT, "-", 2.8)], "Path 2 final output")
    
            lin_err = float(np.max(np.abs(cP1-cP2)))
            lin_rel = r"=" if lin_err <= 1e-6 else r"\ne"
            st.markdown("#### Linearity — Final comparison")
            st.latex(rf"\boxed{{y_{{P1}}(t)\;{lin_rel}\;y_{{P2}}(t)}}")
            fig, ax = plt.subplots(figsize=(6.2,2.55))
            ax.plot(t,cP1,color=C_RESULT,linewidth=2.7,label="Path 1")
            ax.plot(t,cP2,"--",color=C_PATH2,linewidth=2.2,label="Path 2")
            ax.set_title("MATCH" if lin_err <= 1e-6 else "MISMATCH",fontweight="bold")
            ax.set_xlabel("Time t"); ax.set_ylabel("Amplitude"); ax.grid(True,alpha=.3); ax.legend(); ax.set_xlim(-6,6)
            fig.tight_layout()
            _, lti_cmp_col, _ = st.columns([1, 1.75, 1])
            with lti_cmp_col:
                st.pyplot(fig, clear_figure=True, use_container_width=True)
    
            st.markdown("### Step 3 — Time-invariance test")
            st.latex(r"T\{x_1(t-t_0)\}\stackrel{?}{=}y(t-t_0)")
            st.caption(f"For the time-invariance test, x(t) = x₁(t) = {cx1_name} and t₀ = {fmt_num(ct0)}.")
            ti_err = render_time_invariance_experiment(csys, cx1_name, ct0, "challenge_ti")
    
            st.markdown("### Step 4 — Predict and reveal the LTI classification")
            p1 = st.radio("Is it linear?", ["Yes","No"], horizontal=True, key="cp1")
            p2 = st.radio("Is it time-invariant?", ["Yes","No"], horizontal=True, key="cp2")
            p3 = st.radio("Therefore, is it LTI?", ["Yes","No"], horizontal=True, key="cp3")
            if st.button("Reveal answer", type="primary", key="challenge_reveal"):
                lin, ti = KNOWN[csys]
                lti = lin and ti
    
                answers = [
                    ("Linear", p1, "Yes" if lin else "No", "LINEAR" if lin else "NONLINEAR"),
                    ("Time-Invariant", p2, "Yes" if ti else "No", "TIME-INVARIANT" if ti else "TIME-VARYING"),
                    ("LTI", p3, "Yes" if lti else "No", "LTI" if lti else "NOT LTI"),
                ]
    
                cols = st.columns(3)
                for col, (label, prediction, correct_answer, classification) in zip(cols, answers):
                    with col:
                        if prediction == correct_answer:
                            st.success(f"✓ Correct — {classification}")
                        else:
                            st.error(f"✗ Incorrect — {classification}")
    
                score = sum(prediction == correct_answer for _, prediction, correct_answer, _ in answers)
                st.caption(f"Prediction score: {score}/3")
    
                if lti:
                    st.success("This system is LTI because it is both LINEAR and TIME-INVARIANT.")
                else:
                    st.error("This system is NOT LTI because an LTI system must be both LINEAR and TIME-INVARIANT.")
    
    
    with custom_tab:
        st.header("System Grapher — Build Your Own Experiment")
        st.write("Enter your own pointwise system and signals. Enter a system and signals, then graph the same two-path tests used in the LTI Lab.")
        st.info("Examples: system `3*x`, `3*x + 1`, `t*x`, `x**2`, `sin(x)`; signals `u(t)`, `sin(t)`, `cos(2*t)`, `exp(-t**2)`.")
    
        st.markdown("### Step 1 — Choose the experiment")
        c1,c2,c3=st.columns(3)
        with c1: cs=st.text_input("System y(t) =", "3*x", key="cus_sys")
        with c2: cx1=st.text_input("x₁(t) =", "u(t)", key="cus_x1")
        with c3: cx2=st.text_input("x₂(t) =", "sin(t)", key="cus_x2")
        c4,c5,c6=st.columns(3)
        with c4: ca=st.slider("Coefficient a",-5.0,5.0,2.0,0.25,key="cus_a")
        with c5: cb=st.slider("Coefficient b",-5.0,5.0,1.0,0.25,key="cus_b")
        with c6: ct0=st.slider("Delay t₀",-5.0,5.0,2.0,0.25,key="cus_t0")
        if st.button("Graph",type="primary",key="cus_confirm"):
            st.session_state.cus_cfg=(cs,cx1,cx2,ca,cb,ct0)
    
        if "cus_cfg" in st.session_state:
            cs,cx1,cx2,ca,cb,ct0=st.session_state.cus_cfg
            try:
                x1v=safe_custom_expr(cx1,t); x2v=safe_custom_expr(cx2,t)
                combined=ca*x1v+cb*x2v
                lp1=custom_apply(cs,t,combined)
                y1=custom_apply(cs,t,x1v); y2=custom_apply(cs,t,x2v)
                lp2=ca*y1+cb*y2
    
                st.markdown("### Step 2 — Confirmed experiment")
                d1,d2,d3=st.columns(3)
                d1.markdown(f"**System**  \n`y(t) = {cs}`")
                d2.markdown(f"**Input 1**  \n`x₁(t) = {cx1}`")
                d3.markdown(f"**Input 2**  \n`x₂(t) = {cx2}`")
                d4,d5,d6=st.columns(3)
                d4.markdown(f"**a**  \n`{ca:.2f}`"); d5.markdown(f"**b**  \n`{cb:.2f}`"); d6.markdown(f"**t₀**  \n`{ct0:.2f}`")
    
                st.markdown("### Step 3 — Linearity test")
                st.latex(r"T\{a x_1+b x_2\}\stackrel{?}{=}aT\{x_1\}+bT\{x_2\}")
                st.markdown("#### Path 1 — Scale and add the inputs first, then apply the system")
                q1,q2=st.columns(2,gap="large")
                with q1:
                    st.latex(r"a x_1(t)")
                    small_plot([(x1v,"previous: x1",C_X1,"--",1.7),(ca*x1v,"new: a x1",C_X1,"-",2.6)],"Scale x1")
                with q2:
                    st.latex(r"b x_2(t)")
                    small_plot([(x2v,"previous: x2",C_X2,"--",1.7),(cb*x2v,"new: b x2",C_X2,"-",2.6)],"Scale x2")
                q3,q4=st.columns(2,gap="large")
                with q3:
                    st.latex(r"v(t)=a x_1(t)+b x_2(t)")
                    small_plot([(ca*x1v,"a x1",C_X1,"--",1.7),(cb*x2v,"b x2",C_X2,"--",1.7),(combined,"new: v",C_RESULT,"-",2.7)],"Combined input")
                with q4:
                    st.latex(r"y_{P1}(t)=T\{v(t)\}")
                    small_plot([(combined,"previous: v",C_RESULT,"--",1.7),(lp1,"new: Path 1",C_RESULT,"-",2.7)],"Path 1 final output")
    
                st.markdown("#### Path 2 — Apply the system first, then scale and add the outputs")
                r1,r2=st.columns(2,gap="large")
                with r1:
                    st.latex(r"T\{x_1(t)\}")
                    small_plot([(x1v,"previous: x1",C_X1,"--",1.7),(y1,"new: T{x1}",C_X1,"-",2.6)],"System applied to x1")
                with r2:
                    st.latex(r"T\{x_2(t)\}")
                    small_plot([(x2v,"previous: x2",C_X2,"--",1.7),(y2,"new: T{x2}",C_X2,"-",2.6)],"System applied to x2")
                st.markdown("##### Final — Add the scaled outputs")
                _,rc,_=st.columns([1,1.65,1])
                with rc:
                    st.latex(r"y_{P2}(t)=aT\{x_1(t)\}+bT\{x_2(t)\}")
                    small_plot([(ca*y1,"aT{x1}",C_X1,"--",1.7),(cb*y2,"bT{x2}",C_X2,"--",1.7),(lp2,"new: Path 2",C_RESULT,"-",2.7)],"Path 2 final output")
                lerr=float(np.max(np.abs(lp1-lp2)))
                st.markdown("#### Compare the two paths")
                custom_compare_plot(lp1,lp2,"MATCH" if lerr<=1e-6 else "MISMATCH")
    
                st.markdown("### Step 4 — Time-invariance test")
                xv=safe_custom_expr(cx1,t)
                xdv=safe_custom_expr(cx1,t-ct0)
                tp1=custom_apply(cs,t,xdv)
                yv=custom_apply(cs,t,xv)
                tp2=custom_apply(cs,t-ct0,xdv)
                st.latex(r"T\{x(t-t_0)\}\stackrel{?}{=}y(t-t_0)")
                st.markdown("#### Path 1 — Delay the input first, then apply the system")
                s1,s2=st.columns(2,gap="large")
                with s1: small_plot([(xv,"x(t)",C_INPUT,"-",2.5)],"Original input")
                with s2: small_plot([(xv,"previous: x",C_INPUT,"--",1.7),(xdv,"new: delayed x",C_RESULT,"-",2.7)],"Delayed input")
                st.markdown("##### Final — Apply the system")
                _,sc1,_=st.columns([1,1.65,1])
                with sc1: small_plot([(xdv,"previous: delayed x",C_RESULT,"--",1.7),(tp1,"new: Path 1",C_RESULT,"-",2.7)],"Path 1 final output")
    
                st.markdown("#### Path 2 — Apply the system first, then delay the output")
                s3,s4=st.columns(2,gap="large")
                with s3: small_plot([(xv,"x(t)",C_INPUT,"-",2.5)],"Original input")
                with s4: small_plot([(xv,"previous: x",C_INPUT,"--",1.7),(yv,"new: y(t)",C_PATH2,"-",2.7)],"System output")
                st.markdown("##### Final — Delay the output")
                _,sc2,_=st.columns([1,1.65,1])
                with sc2: small_plot([(yv,"previous: y(t)",C_PATH2,"--",1.7),(tp2,"new: Path 2",C_RESULT,"-",2.7)],"Path 2 final output")
                terr=float(np.max(np.abs(tp1-tp2)))
                st.markdown("#### Compare the two paths")
                custom_compare_plot(tp1,tp2,"MATCH" if terr<=1e-6 else "MISMATCH")
            except Exception as e:
                st.error(f"Could not evaluate the custom expression: {e}")
    
    
    # ---------- Mini Exam: 50-question internal bank ----------
    def quiz_system_eval(kind, z, xf, p=1.0):
        x = xf(z)
        if kind == "gain": return p*x
        if kind == "delay": return xf(z-p)
        if kind == "advance": return xf(z+p)
        if kind == "two_shift": return 2*xf(z-p)-xf(z+1)
        if kind == "derivative": return p*np.gradient(x, z)
        if kind == "derivative_delay": return np.gradient(xf(z-p), z)
        if kind == "square": return p*x**2
        if kind == "abs": return p*np.abs(x)
        if kind == "sinx": return np.sin(p*x)
        if kind == "offset": return p*x+1
        if kind == "time_gain": return (z+p)*x
        if kind == "sin_time_gain": return np.abs(np.sin(p*z))*x
        if kind == "gate": return x*(z>=p).astype(float)
        if kind == "reverse": return xf(-z)
        if kind == "reverse_mix": return xf(-z)+p*x
        if kind == "time_scale": return xf(p*z)
        if kind == "time_square": return xf(z**2)
        raise ValueError("Unknown quiz system")
    
    def make_quiz_bank():
        B=[]
        sigs=["Unit step u(t)","sin(t)","cos(2t)","Gaussian exp(-t²)","Triangular pulse"]
        def add(label,kind,p,truth,why,i,a,b,t0):
            B.append({"system":label,"kind":kind,"p":p,"input":sigs[i%len(sigs)],
                      "a":a,"b":b,"t0":t0,"truth":truth,"why":why})
    
        for i,k in enumerate([2,3,-1,0.5,4]):
            add(f"y(t) = {k}x(t)","gain",k,True,"Constant gain is linear and time-invariant.",i,2,-1,1+i*0.25)
    
        add("y(t) = x(t - 1)","delay",1,True,"A fixed delay is linear and time-invariant.",0,2,1,1)
        add("y(t) = x(t - 2)","delay",2,True,"A fixed delay is linear and time-invariant.",1,-2,1,1.5)
        add("y(t) = x(t + 1)","advance",1,True,"A fixed advance is linear and time-invariant.",2,1,2,2)
        add("y(t) = x(t + 2)","advance",2,True,"A fixed advance is linear and time-invariant.",3,2,-1,1)
        add("y(t) = 2x(t - 1) - x(t + 1)","two_shift",1,True,"A constant linear combination of fixed shifts is LTI.",4,2,1,2)
    
        for i,k in enumerate([1,2,-1,0.5,3]):
            add(f"y(t) = {k} dx(t)/dt","derivative",k,True,"Differentiation with constant scaling is linear and time-invariant.",i,1+i%2,1,1.25)
    
        for i,k in enumerate([1,2,0.5,3,-1]):
            add(f"y(t) = {k}[x(t)]^2","square",k,False,"Squaring the input breaks linearity, although the rule is time-invariant.",i,2,1,1)
    
        add("y(t) = |x(t)|","abs",1,False,"Absolute value is nonlinear but time-invariant.",0,2,1,1)
        add("y(t) = 2|x(t)|","abs",2,False,"Absolute value breaks linearity.",1,1,-2,1.5)
        add("y(t) = sin[x(t)]","sinx",1,False,"sin[x(t)] is nonlinear but time-invariant.",2,2,1,2)
        add("y(t) = sin[2x(t)]","sinx",2,False,"The sine nonlinearity breaks superposition.",3,-1,2,1)
        add("y(t) = 3x(t) + 1","offset",3,False,"The additive constant breaks linearity; T{0} is not zero.",4,2,1,2)
    
        for i,pv in enumerate([0,1,-1,2,0.5]):
            add(f"y(t) = (t {pv:+g})x(t)","time_gain",pv,False,"The explicit time-dependent coefficient makes the system time-varying.",i,2,1,1+i*0.25)
    
        for i,k in enumerate([1,2,3,0.5,4]):
            add(f"y(t) = |sin({k}t)| x(t)","sin_time_gain",k,False,"Multiplication by a nonconstant function of time is linear but time-varying.",i,1,2,1.5)
    
        for i,pv in enumerate([0,1,-1,2,-2]):
            add(f"y(t) = x(t)u(t {(-pv):+g})","gate",pv,False,"A gate tied to absolute time makes the system time-varying.",i,2,-1,1)
    
        add("y(t) = x(-t)","reverse",1,False,"Time reversal is linear but not time-invariant.",0,2,1,1)
        add("y(t) = x(-t) + 2x(t)","reverse_mix",2,False,"The time-reversal term makes the system time-varying.",1,1,2,1.5)
        add("y(t) = x(2t)","time_scale",2,False,"Time scaling is linear but not time-invariant.",2,2,-1,1)
        add("y(t) = x(0.5t)","time_scale",0.5,False,"Time scaling is linear but not time-invariant.",3,1,2,2)
        add("y(t) = x(t^2)","time_square",1,False,"The nonlinear time transformation t^2 is not time-invariant.",4,2,1,1)
    
        add("y(t) = d[x(t-1)]/dt","derivative_delay",1,True,"A fixed delay followed by differentiation is LTI.",0,2,1,1.5)
        add("y(t) = d[x(t-2)]/dt","derivative_delay",2,True,"A fixed delay followed by differentiation is LTI.",1,-1,2,1)
        add("y(t) = 2x(t-2) - x(t+1)","two_shift",2,True,"A constant linear combination of fixed shifts is LTI.",2,2,1,2)
        add("y(t) = -2x(t) + 1","offset",-2,False,"The additive constant makes the system nonlinear.",3,1,-1,1)
        add("y(t) = x(-t) - x(t)","reverse_mix",-1,False,"Although linear, the time-reversal term makes it time-varying.",4,2,1,2)
    
        return B
    
    QUIZ_BANK = make_quiz_bank()
    assert len(QUIZ_BANK) == 50
    
    
    with quiz_tab:
        st.header("Mini Exam — LTI Classification")
        st.write("Each exam contains **10 random questions** selected from an internal bank of **50 exercises**.")
    
        if "exam_questions" not in st.session_state:
            rng = np.random.default_rng()
            st.session_state.exam_questions = rng.choice(len(QUIZ_BANK), size=10, replace=False).tolist()
            st.session_state.exam_version = 1
            st.session_state.exam_graded = False
    
        if st.button("Generate New Exam", key="new_exam"):
            rng = np.random.default_rng()
            st.session_state.exam_questions = rng.choice(len(QUIZ_BANK), size=10, replace=False).tolist()
            st.session_state.exam_version = st.session_state.get("exam_version",1) + 1
            st.session_state.exam_graded = False
            st.session_state.exam_submitted_answers = []
            st.rerun()
    
        selected = [QUIZ_BANK[i] for i in st.session_state.exam_questions]
        answers = []
        ver = st.session_state.exam_version
    
        for i,q in enumerate(selected):
            if st.session_state.get("exam_graded", False) and len(st.session_state.get("exam_submitted_answers", [])) == 10:
                submitted = st.session_state.exam_submitted_answers[i]
                correct_label = "LTI" if q["truth"] else "Not LTI"
                is_correct = submitted == correct_label
                qcol, result_col = st.columns([4.5, 1.2])
                with qcol:
                    st.markdown(f"### {i+1}. `{q['system']}`")
                with result_col:
                    if is_correct:
                        st.success("✓ Correct")
                    else:
                        st.error("✗ Incorrect")
            else:
                st.markdown(f"### {i+1}. `{q['system']}`")
    
            st.caption(f"x(t) = {q['input']}   |   a = {fmt_num(q['a'])}, b = {fmt_num(q['b'])}, t₀ = {fmt_num(q['t0'])}")
            answers.append(st.radio("Classification", ["LTI","Not LTI"], horizontal=True, index=None, key=f"exam_{ver}_{i}"))
            st.divider()
    
        if st.button("Grade exam", type="primary", key=f"grade_exam_{ver}"):
            if any(a is None for a in answers):
                st.warning("Please answer all 10 questions before grading.")
            else:
                st.session_state.exam_score = sum(a == ("LTI" if q["truth"] else "Not LTI") for a,q in zip(answers,selected))
                st.session_state.exam_submitted_answers = list(answers)
                st.session_state.exam_graded = True
                st.rerun()
    
        if st.session_state.get("exam_graded", False):
            st.markdown(f"## Score: {st.session_state.exam_score}/10")
            st.markdown("## Review solutions")
            st.write("Open a question to review the solution.")
    
            for i,q in enumerate(selected):
                with st.expander(f"Question {i+1} — Show correct result and graph"):
                    st.markdown("### Question")
                    st.markdown(f"**System:** `{q['system']}`")
                    st.markdown(f"**Input:** `x(t) = {q['input']}`")
                    st.markdown(f"**Parameters:**  a = `{fmt_num(q['a'])}`, b = `{fmt_num(q['b'])}`, t₀ = `{fmt_num(q['t0'])}`")
                    st.markdown("**Classify the system as LTI or Not LTI.**")
                    st.divider()
                    st.markdown(f"**Correct answer: {'LTI' if q['truth'] else 'Not LTI'}**")
                    st.write(q["why"])
    
                    qx1 = lambda z,name=q["input"]: get_signal(name,z)
                    qx2 = lambda z: get_signal("cos(2t)",z)
                    qa,qb,qt = q["a"],q["b"],q["t0"]
                    qcomb = lambda z: qa*qx1(z)+qb*qx2(z)
    
                    qlp1 = quiz_system_eval(q["kind"],t,qcomb,q["p"])
                    qlp2 = qa*quiz_system_eval(q["kind"],t,qx1,q["p"]) + qb*quiz_system_eval(q["kind"],t,qx2,q["p"])
                    qxd = lambda z: qx1(z-qt)
                    qtp1 = quiz_system_eval(q["kind"],t,qxd,q["p"])
                    qtp2 = quiz_system_eval(q["kind"],t-qt,qx1,q["p"])
    
                    g1,g2 = st.columns(2,gap="large")
                    with g1:
                        fig,ax = plt.subplots(figsize=(4.8,2.45))
                        ax.plot(t,qlp1,color=C_RESULT,linewidth=2.5,label="Path 1")
                        ax.plot(t,qlp2,"--",color=C_PATH2,linewidth=2,label="Path 2")
                        ax.set_title("Linearity: "+("MATCH" if np.max(np.abs(qlp1-qlp2))<=1e-5 else "MISMATCH"))
                        ax.grid(True,alpha=.3); ax.legend(fontsize=8); ax.set_xlim(-6,6); fig.tight_layout()
                        st.pyplot(fig,clear_figure=True,use_container_width=True)
                    with g2:
                        fig,ax = plt.subplots(figsize=(4.8,2.45))
                        ax.plot(t,qtp1,color=C_RESULT,linewidth=2.5,label="Path 1")
                        ax.plot(t,qtp2,"--",color=C_PATH2,linewidth=2,label="Path 2")
                        ax.set_title("Time invariance: "+("MATCH" if np.max(np.abs(qtp1-qtp2))<=1e-5 else "MISMATCH"))
                        ax.grid(True,alpha=.3); ax.legend(fontsize=8); ax.set_xlim(-6,6); fig.tight_layout()
                        st.pyplot(fig,clear_figure=True,use_container_width=True)
    
