import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt

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

    fig, axes = plt.subplots(3, 1, figsize=(8.0, 3.75))
    fig.subplots_adjust(hspace=0.72, left=0.09, right=0.98, top=0.95, bottom=0.10)

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
    fig, ax = plt.subplots(figsize=(3.8, 1.45))
    for values, label, color, style, width in series:
        ax.plot(TAU, values, label=label, color=color, ls=style, lw=width)
    format_axes(ax, title, xlabel)
    ax.legend(fontsize=6.5, loc="upper right")
    fig.tight_layout(pad=0.65)
    st.pyplot(fig, clear_figure=False, use_container_width=True)
    plt.close(fig)

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
    st.write("The EE-207 controls and visual style stay the same, while the three plots are drawn in the browser for smooth real-time motion.")

    c1,c2=st.columns(2)
    live_names=["Rectangular pulse (centered)","Wide rectangular pulse","Causal rectangular pulse","Triangular pulse","Gaussian exp(-t^2)","Decaying exponential e^(-t)u(t)"]
    with c1:
        x_name=st.selectbox("Input x(t)",live_names,index=0,key="smooth_x")
    with c2:
        h_name=st.selectbox("Impulse response h(t)",live_names,index=1,key="smooth_h")

    ids={"Rectangular pulse (centered)":"rect2","Wide rectangular pulse":"rect4","Causal rectangular pulse":"causal2","Triangular pulse":"tri4","Gaussian exp(-t^2)":"gauss","Decaying exponential e^(-t)u(t)":"exp"}
    html=r'''<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}body{margin:0;background:transparent;color:#ddd;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
.ctrl{display:grid;grid-template-columns:90px 90px 90px 1fr 130px;gap:9px;align-items:end;margin:0 0 8px}
button,select{height:34px;border:1px solid rgba(140,140,140,.45);border-radius:7px;background:#262730;color:#eee;font:inherit}button{cursor:pointer}button:hover{border-color:#ff4b4b}.field label{display:block;font-size:11px;opacity:.65;margin-bottom:3px}input[type=range]{width:100%;accent-color:#ff4b4b}
.panel{border:1px solid rgba(130,130,130,.25);border-radius:9px;padding:3px 7px 1px;margin-bottom:6px;background:rgba(255,255,255,.015)}.ttl{font-size:12px;font-weight:600;margin:0 0 1px 3px}canvas{display:block;width:100%;height:110px}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:7px}.metric{border:1px solid rgba(130,130,130,.25);border-radius:8px;padding:6px 9px}.k{font-size:10px;opacity:.6}.v{font-size:17px;margin-top:1px}.eq{text-align:center;margin-top:7px;font-family:Georgia,"Times New Roman",serif;font-size:15px}@media(prefers-color-scheme:light){body{color:#222}button,select{background:white;color:#222}.panel,.metric{background:white}}
</style></head><body>
<div class="ctrl"><button id="reset">Reset</button><button id="play">Play</button><button id="pause">Pause</button><div class="field"><label>Current time t</label><input id="slider" type="range" min="-5" max="5" step="0.01" value="-5"></div><div class="field"><label>Speed</label><select id="speed"><option value="0.55">0.5x</option><option value="1.1" selected>1x</option><option value="1.65">1.5x</option><option value="2.2">2x</option></select></div></div>
<div class="panel"><div class="ttl">1. Slide and overlap - x(tau) and h(t-tau)</div><canvas id="c1"></canvas></div>
<div class="panel"><div class="ttl">2. Multiply and integrate - x(tau)h(t-tau)</div><canvas id="c2"></canvas></div>
<div class="panel"><div class="ttl">3. Build the output - y(t) = x(t) * h(t)</div><canvas id="c3"></canvas></div>
<div class="metrics"><div class="metric"><div class="k">Current time</div><div class="v" id="mt"></div></div><div class="metric"><div class="k">Overlap integral</div><div class="v" id="ma"></div></div><div class="metric"><div class="k">Current y(t)</div><div class="v" id="my"></div></div></div><div class="eq" id="eq"></div>
<script>
const XT='__X__',HT='__H__',BLUE='#1f77b4',ORANGE='#ff7f0e',GREEN='#2ca02c',RED='#d62728',PURPLE='#9467bd';const lo=-6,hi=6,N=601,dx=(hi-lo)/(N-1),g=Array.from({length:N},(_,i)=>lo+i*dx);
function f(k,x){if(k==='rect2')return Math.abs(x)<=1?1:0;if(k==='rect4')return Math.abs(x)<=2?1:0;if(k==='causal2')return x>=0&&x<=2?1:0;if(k==='tri4')return Math.max(1-Math.abs(x)/2,0);if(k==='gauss')return Math.exp(-x*x);if(k==='exp')return x>=0?Math.exp(-x):0;return 0}
const xv=g.map(x=>f(XT,x));const yv=g.map(t=>{let s=0;for(let i=0;i<N;i++)s+=xv[i]*f(HT,t-g[i]);return s*dx});
function near(t){return Math.max(0,Math.min(N-1,Math.round((t-lo)/dx)))}function sx(x,w){return 32+(x-lo)/(hi-lo)*(w-42)}function sy(y,h,m){return h/2-y/m*(h*.34)}
function cv(id){const c=document.getElementById(id),r=devicePixelRatio||1,w=Math.max(450,c.clientWidth),h=96;c.width=w*r;c.height=h*r;const q=c.getContext('2d');q.setTransform(r,0,0,r,0,0);return{q,w,h}}
function ax(o){let q=o.q,w=o.w,h=o.h;q.clearRect(0,0,w,h);q.strokeStyle='rgba(140,140,140,.23)';q.lineWidth=1;q.beginPath();q.moveTo(32,h/2);q.lineTo(w-10,h/2);q.stroke();q.fillStyle='rgba(140,140,140,.85)';q.font='9px Arial';for(let x=-6;x<=6;x+=2){let p=sx(x,w);q.beginPath();q.moveTo(p,8);q.lineTo(p,h-13);q.stroke();q.fillText(x,p-4,h-2)}}
function line(o,v,c,m,w=2,alpha=1){let q=o.q;q.globalAlpha=alpha;q.strokeStyle=c;q.lineWidth=w;q.beginPath();v.forEach((y,i)=>{let X=sx(g[i],o.w),Y=sy(y,o.h,m);if(i===0||!Number.isFinite(v[i-1]))q.moveTo(X,Y);else q.lineTo(X,Y)});q.stroke();q.globalAlpha=1}
let t=-5,run=false,last=0;const sl=document.getElementById('slider'),sp=document.getElementById('speed');
function draw(){const hs=g.map(z=>f(HT,t-z)),pr=xv.map((v,i)=>v*hs[i]);let area=pr.reduce((a,b)=>a+b,0)*dx,yn=yv[near(t)];let o1=cv('c1'),o2=cv('c2'),o3=cv('c3');let m1=Math.max(1.1,...xv.map(Math.abs),...hs.map(Math.abs));ax(o1);line(o1,xv,BLUE,m1,2.1);line(o1,hs,ORANGE,m1,2.1);let m2=Math.max(1.1,...pr.map(Math.abs));ax(o2);line(o2,pr,RED,m2,2.25);let m3=Math.max(1.1,...yv.map(Math.abs));ax(o3);line(o3,yv,GREEN,m3,1.4,.18);let k=near(t),part=yv.map((v,i)=>i<=k?v:NaN);line(o3,part,GREEN,m3,2.2);let X=sx(t,o3.w),Y=sy(yn,o3.h,m3);o3.q.fillStyle=PURPLE;o3.q.beginPath();o3.q.arc(X,Y,3.5,0,6.29);o3.q.fill();o3.q.strokeStyle=PURPLE;o3.q.setLineDash([3,3]);o3.q.beginPath();o3.q.moveTo(X,7);o3.q.lineTo(X,o3.h-12);o3.q.stroke();o3.q.setLineDash([]);document.getElementById('mt').textContent=t.toFixed(2)+' s';document.getElementById('ma').textContent=area.toFixed(4);document.getElementById('my').textContent=yn.toFixed(4);document.getElementById('eq').textContent='y('+t.toFixed(2)+') = integral x(tau) h('+t.toFixed(2)+'-tau) d tau = '+area.toFixed(4);sl.value=t}
function anim(ts){if(!run){last=0;return}if(!last)last=ts;let d=(ts-last)/1000;last=ts;t+=d*parseFloat(sp.value);if(t>=5){t=5;run=false;draw();setTimeout(()=>{t=0;last=0;draw();},300);return;}draw();requestAnimationFrame(anim)}
document.getElementById('play').onclick=()=>{if(!run){run=true;requestAnimationFrame(anim)}};document.getElementById('pause').onclick=()=>{run=false;last=0};document.getElementById('reset').onclick=()=>{run=false;last=0;t=0;draw()};sl.oninput=e=>{run=false;last=0;t=parseFloat(e.target.value);draw()};addEventListener('resize',draw);draw();
</script></body></html>'''
    html=html.replace('__X__',ids[x_name]).replace('__H__',ids[h_name])
    components.html(html,height=505,scrolling=False)

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
        fig, ax = plt.subplots(figsize=(4.5, 1.65))
        ax.plot(TAU, y, color=C_Y, lw=2.1, label="y(t)")
        ax.scatter([t_now], [np.interp(t_now, TAU, y)], s=30, color=C_NOW, zorder=5)
        ax.axvline(t_now, ls="--", color=C_NOW, lw=1.0)
        format_axes(ax, "Complete convolution output", "Time t")
        ax.legend(fontsize=6.5)
        fig.tight_layout(pad=0.7)
        st.pyplot(fig, clear_figure=False, use_container_width=True)
        plt.close(fig)

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
