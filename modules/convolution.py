import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import random
import json
import re
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
    st.markdown("## Example — graphical convolution")
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
        "Choose the signals, load a ready-to-try example, or build your own x(t) and h(t). "
        "The three plots update smoothly in real time."
    )

    mode = st.radio(
        "How would you like to define the signals?",
        ["Choose signals", "Try an example", "Build custom signals"],
        horizontal=True,
        key="conv_live_mode",
    )

    base_signals = {
        "Rectangular pulse (centered)": {"id":"rect2", "label":"rect(t/2)"},
        "Wide rectangular pulse": {"id":"rect4", "label":"rect(t/4)"},
        "Causal rectangular pulse": {"id":"causal2", "label":"u(t)-u(t-2)"},
        "Triangular pulse": {"id":"tri4", "label":"tri(t/4)"},
        "Gaussian exp(-t²)": {"id":"gauss", "label":"e^{-t²}"},
        "Decaying exponential e^(-t)u(t)": {"id":"exp", "label":"e^{-t}u(t)"},
        "Unit step u(t)": {"id":"step", "label":"u(t)"},
        "Narrow impulse approximation": {"id":"impulse", "label":"δ(t)"},
        "Delayed impulse approximation δ(t-2)": {"id":"impulse2", "label":"δ(t-2)"},
        "Echo δ(t)+½δ(t-2)": {"id":"echo", "label":"δ(t)+0.5δ(t-2)"},
    }

    examples = {
        "Pulse * Pulse → triangular/trapezoidal output":
            ("Causal rectangular pulse", "Causal rectangular pulse"),
        "Step * Decay → RC charging response":
            ("Unit step u(t)", "Decaying exponential e^(-t)u(t)"),
        "Pulse * Decay → RC charge/discharge":
            ("Causal rectangular pulse", "Decaying exponential e^(-t)u(t)"),
        "Pulse * Impulse → pulse unchanged":
            ("Causal rectangular pulse", "Narrow impulse approximation"),
        "Pulse * Echo → original pulse + delayed echo":
            ("Causal rectangular pulse", "Echo δ(t)+½δ(t-2)"),
        "Gaussian * Gaussian → wider smooth pulse":
            ("Gaussian exp(-t²)", "Gaussian exp(-t²)"),
        "Triangle * Pulse → piecewise smooth output":
            ("Triangular pulse", "Causal rectangular pulse"),
        "Wide pulse * Narrow pulse → trapezoidal output":
            ("Wide rectangular pulse", "Causal rectangular pulse"),
    }

    custom = None
    x_display = ''
    h_display = ''
    sim_lo, sim_hi = -6.0, 6.0

    if mode == "Choose signals":
        c1, c2 = st.columns(2)
        names = list(base_signals.keys())
        with c1:
            x_name = st.selectbox("Input x(t)", names, index=0, key="smooth_x_v14")
        with c2:
            h_name = st.selectbox("Impulse response h(t)", names, index=1, key="smooth_h_v14")
        x_id, h_id = base_signals[x_name]["id"], base_signals[h_name]["id"]
        x_display = base_signals[x_name]["label"]
        h_display = base_signals[h_name]["label"]

    elif mode == "Try an example":
        st.markdown("### Examples to try")
        st.caption("Select an example and press Play to watch how the convolution is built.")
        ex_name = st.selectbox("Choose an example", list(examples.keys()), key="conv_example")
        x_name, h_name = examples[ex_name]
        x_id, h_id = base_signals[x_name]["id"], base_signals[h_name]["id"]
        x_display = base_signals[x_name]["label"]
        h_display = base_signals[h_name]["label"]
        e1, e2 = st.columns(2)
        with e1:
            st.markdown(f"**x(t):** `{base_signals[x_name]['label']}`")
        with e2:
            st.markdown(f"**h(t):** `{base_signals[h_name]['label']}`")

    else:
        st.markdown("### Write your own signals")
        st.write(
            "Enter each equation using `t` as the time variable. Supported forms include "
            "`u(t)`, `u(t-a)`, `rect(t)`, `tri(t)`, `exp(-a*t)*u(t)`, "
            "`sin(w*t)`, `cos(w*t)`, constants, +, -, *, /, and parentheses."
        )
        st.caption(
            "Examples:  `u(t)-u(t-2)`   |   `2*exp(-t)*u(t)`   |   "
            "`sin(2*t)`   |   `rect(t-1)`"
        )

        c1, c2 = st.columns(2)
        with c1:
            x_expr = st.text_input("x(t) =", value="u(t)-u(t-2)", key="custom_x_expr")
        with c2:
            h_expr = st.text_input("h(t) =", value="exp(-t)*u(t)", key="custom_h_expr")

        x_id, h_id = "expression", "expression"
        x_display, h_display = x_expr, h_expr
        custom = (1,0,1,1,0,1)

        # Adapt the simulation window to time shifts appearing in the equations.
        # Examples: u(t-10), rect(t+8), exp(-(t-12))*u(t-12).
        def _suggest_range(*exprs):
            vals = [0.0]
            for expr in exprs:
                # Capture numeric offsets written directly with t, such as t-10 or t+8.
                for sign, number in re.findall(r"t\s*([+-])\s*(\d+(?:\.\d+)?)", expr):
                    value = float(number)
                    vals.append(value if sign == "-" else -value)
            lo = min(-6.0, min(vals)-4.0)
            hi = max(6.0, max(vals)+4.0)
            return float(np.floor(lo)), float(np.ceil(hi))

        auto_lo, auto_hi = _suggest_range(x_expr, h_expr)
        sim_lo, sim_hi = auto_lo, auto_hi
        st.caption(
            f"Adaptive simulation window: {auto_lo:g} ≤ t ≤ {auto_hi:g}. "
            "It expands automatically when your equations contain larger time shifts."
        )

    st.markdown("### Signals used in the simulation")
    sx_col, sh_col = st.columns(2)
    with sx_col:
        st.markdown("**Input**")
        st.code(f"x(t) = {x_display}", language=None)
    with sh_col:
        st.markdown("**Impulse response**")
        st.code(f"h(t) = {h_display}", language=None)

    html = r'''<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}body{margin:0;background:transparent;color:#ddd;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
.ctrl{display:grid;grid-template-columns:90px 90px 90px 1fr 130px;gap:9px;align-items:end;margin:0 0 8px}
button,select{height:34px;border:1px solid rgba(140,140,140,.45);border-radius:7px;background:#262730;color:#eee;font:inherit}button{cursor:pointer}button:hover{border-color:#ff4b4b}.field label{display:block;font-size:11px;opacity:.65;margin-bottom:3px}input[type=range]{width:100%;accent-color:#ff4b4b}
.panel{border:1px solid rgba(130,130,130,.25);border-radius:9px;padding:3px 7px 1px;margin-bottom:6px;background:rgba(255,255,255,.015)}.ttl{font-size:12px;font-weight:600;margin:0 0 1px 3px}canvas{display:block;width:100%;height:110px}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:7px}.metric{border:1px solid rgba(130,130,130,.25);border-radius:8px;padding:6px 9px}.k{font-size:10px;opacity:.6}.v{font-size:17px;margin-top:1px}.eq{text-align:center;margin-top:7px;font-family:Georgia,"Times New Roman",serif;font-size:15px}@media(prefers-color-scheme:light){body{color:#222}button,select{background:white;color:#222}.panel,.metric{background:white}}
</style></head><body>
<div class="ctrl"><button id="reset">Reset</button><button id="play">Play</button><button id="pause">Pause</button><div class="field"><label>Current time t</label><input id="slider" type="range" min="__LO__" max="__HI__" step="0.01" value="__LO__"></div><div class="field"><label>Speed</label><select id="speed"><option value="0.55">0.5x</option><option value="1.1" selected>1x</option><option value="1.65">1.5x</option><option value="2.2">2x</option></select></div></div>
<div class="panel"><div class="ttl">1. Slide and overlap — x(τ) and h(t−τ)</div><canvas id="c1"></canvas></div>
<div class="panel"><div class="ttl">2. Multiply and integrate — x(τ)h(t−τ)</div><canvas id="c2"></canvas></div>
<div class="panel"><div class="ttl">3. Build the output — y(t) = x(t) * h(t)</div><canvas id="c3"></canvas></div>
<div class="metrics"><div class="metric"><div class="k">Current time</div><div class="v" id="mt"></div></div><div class="metric"><div class="k">Overlap integral</div><div class="v" id="ma"></div></div><div class="metric"><div class="k">Current y(t)</div><div class="v" id="my"></div></div></div><div class="eq" id="eq"></div>
<script>
const XT='__X__',HT='__H__',XEXPR=__XEXPR__,HEXPR=__HEXPR__,BLUE='#1f77b4',ORANGE='#ff7f0e',GREEN='#2ca02c',RED='#d62728',PURPLE='#9467bd';
const XAMP=__XA__,XSHIFT=__XS__,XP=__XP__,HAMP=__HA__,HSHIFT=__HS__,HP=__HP__;
const lo=__LO__,hi=__HI__,N=801,dx=(hi-lo)/(N-1),g=Array.from({length:N},(_,i)=>lo+i*dx);
function impulse(x,c=0){const s=.055;return Math.exp(-Math.pow((x-c)/s,2))/(s*Math.sqrt(Math.PI))}
function U(x){return x>=0?1:0}
function RECT(x){return Math.abs(x)<=0.5?1:0}
function TRI(x){return Math.max(1-Math.abs(x),0)}
function evalExpr(expr,t){
 let s=expr.toLowerCase().replace(/\s+/g,'');
 s=s.replace(/\^/g,'**');
 s=s.replace(/u\(/g,'U(').replace(/rect\(/g,'RECT(').replace(/tri\(/g,'TRI(');
 s=s.replace(/exp\(/g,'Math.exp(').replace(/sin\(/g,'Math.sin(').replace(/cos\(/g,'Math.cos(');
 s=s.replace(/sqrt\(/g,'Math.sqrt(').replace(/abs\(/g,'Math.abs(');
 if(!/^[0-9t+\-*/().,_a-zA-Z*]+$/.test(s)) return 0;
 try{return Function('t','U','RECT','TRI','return ('+s+')')(t,U,RECT,TRI)}catch(e){return 0}
}
function f(k,x,A=1,T=0,p=1){
 if(k==='expression')return 0;
 if(k==='rect2')return Math.abs(x)<=1?1:0;if(k==='rect4')return Math.abs(x)<=2?1:0;
 if(k==='causal2')return x>=0&&x<=2?1:0;if(k==='tri4')return Math.max(1-Math.abs(x)/2,0);
 if(k==='gauss')return Math.exp(-x*x);if(k==='exp')return x>=0?Math.exp(-x):0;
 if(k==='step')return x>=0?1:0;if(k==='impulse')return impulse(x,0);
 if(k==='impulse2')return impulse(x,2);if(k==='echo')return impulse(x,0)+.5*impulse(x,2);
 if(k==='custom_rect')return A*(Math.abs(x-T)<=p/2?1:0);
 if(k==='custom_tri')return A*Math.max(1-Math.abs(x-T)/(p/2),0);
 if(k==='custom_exp')return x>=T?A*Math.exp(-p*(x-T)):0;
 if(k==='custom_gauss')return A*Math.exp(-p*Math.pow(x-T,2));
 if(k==='custom_sin')return A*Math.sin(p*(x-T));return 0}
function fx(x){return XT==='expression'?evalExpr(XEXPR,x):f(XT,x,XAMP,XSHIFT,XP)}function fh(x){return HT==='expression'?evalExpr(HEXPR,x):f(HT,x,HAMP,HSHIFT,HP)}
const xv=g.map(x=>fx(x));const yv=g.map(t=>{let s=0;for(let i=0;i<N;i++)s+=xv[i]*fh(t-g[i]);return s*dx});
function near(t){return Math.max(0,Math.min(N-1,Math.round((t-lo)/dx)))}function sx(x,w){return 32+(x-lo)/(hi-lo)*(w-42)}function sy(y,h,m){return h/2-y/m*(h*.34)}
function cv(id){const c=document.getElementById(id),r=devicePixelRatio||1,w=Math.max(450,c.clientWidth),h=96;c.width=w*r;c.height=h*r;const q=c.getContext('2d');q.setTransform(r,0,0,r,0,0);return{q,w,h}}
function ax(o){let q=o.q,w=o.w,h=o.h;q.clearRect(0,0,w,h);q.strokeStyle='rgba(140,140,140,.23)';q.lineWidth=1;q.beginPath();q.moveTo(32,h/2);q.lineTo(w-10,h/2);q.stroke();q.fillStyle='rgba(140,140,140,.85)';q.font='9px Arial';let tick=(hi-lo)/6;for(let x=lo;x<=hi+tick*.1;x+=tick){let p=sx(x,w);q.beginPath();q.moveTo(p,8);q.lineTo(p,h-13);q.stroke();q.fillText(x.toFixed(Math.abs(tick)<1?1:0),p-7,h-2)}}
function line(o,v,c,m,w=2,alpha=1){let q=o.q;q.globalAlpha=alpha;q.strokeStyle=c;q.lineWidth=w;q.beginPath();v.forEach((y,i)=>{let X=sx(g[i],o.w),Y=sy(y,o.h,m);if(i===0||!Number.isFinite(v[i-1]))q.moveTo(X,Y);else q.lineTo(X,Y)});q.stroke();q.globalAlpha=1}
let t=lo,run=false,last=0;const sl=document.getElementById('slider'),sp=document.getElementById('speed');
function draw(){const hs=g.map(z=>fh(t-z)),pr=xv.map((v,i)=>v*hs[i]);let area=pr.reduce((a,b)=>a+b,0)*dx,yn=yv[near(t)];let o1=cv('c1'),o2=cv('c2'),o3=cv('c3');let m1=Math.max(1.1,...xv.map(Math.abs),...hs.map(Math.abs));ax(o1);line(o1,xv,BLUE,m1,2.1);line(o1,hs,ORANGE,m1,2.1);let m2=Math.max(1.1,...pr.map(Math.abs));ax(o2);line(o2,pr,RED,m2,2.25);let m3=Math.max(1.1,...yv.map(Math.abs));ax(o3);line(o3,yv,GREEN,m3,1.4,.18);let k=near(t),part=yv.map((v,i)=>i<=k?v:NaN);line(o3,part,GREEN,m3,2.2);let X=sx(t,o3.w),Y=sy(yn,o3.h,m3);o3.q.fillStyle=PURPLE;o3.q.beginPath();o3.q.arc(X,Y,3.5,0,6.29);o3.q.fill();o3.q.strokeStyle=PURPLE;o3.q.setLineDash([3,3]);o3.q.beginPath();o3.q.moveTo(X,7);o3.q.lineTo(X,o3.h-12);o3.q.stroke();o3.q.setLineDash([]);document.getElementById('mt').textContent=t.toFixed(2)+' s';document.getElementById('ma').textContent=area.toFixed(4);document.getElementById('my').textContent=yn.toFixed(4);document.getElementById('eq').textContent='y('+t.toFixed(2)+') = ∫ x(τ) h('+t.toFixed(2)+' − τ) dτ = '+area.toFixed(4);sl.value=t}
function anim(ts){if(!run){last=0;return}if(!last)last=ts;let d=(ts-last)/1000;last=ts;t+=d*parseFloat(sp.value);if(t>=hi){t=hi;run=false;draw();last=0;setTimeout(()=>{t=lo;draw();},250);return}draw();requestAnimationFrame(anim)}
document.getElementById('play').onclick=()=>{if(!run){run=true;requestAnimationFrame(anim)}};document.getElementById('pause').onclick=()=>{run=false;last=0};document.getElementById('reset').onclick=()=>{run=false;last=0;t=lo;draw()};sl.oninput=e=>{run=false;last=0;t=parseFloat(e.target.value);draw()};addEventListener('resize',draw);draw();
</script></body></html>'''

    vals = (1,0,1,1,0,1) if custom is None else custom
    xa,xs,xp,ha,hs,hp = vals
    x_expr_js = json.dumps(x_display if x_id == "expression" else "")
    h_expr_js = json.dumps(h_display if h_id == "expression" else "")
    html=(html.replace('__X__',x_id).replace('__H__',h_id)
              .replace('__XEXPR__',x_expr_js).replace('__HEXPR__',h_expr_js)
              .replace('__XA__',str(xa)).replace('__XS__',str(xs)).replace('__XP__',str(xp))
              .replace('__HA__',str(ha)).replace('__HS__',str(hs)).replace('__HP__',str(hp))
              .replace('__LO__',str(sim_lo)).replace('__HI__',str(sim_hi)))
    components.html(html,height=620,scrolling=False)

def render_step_by_step():
    st.header("Step-by-Step")
    st.write("Freeze the convolution at one value of t and inspect every graphical operation.")

    mode = st.radio(
        "How would you like to define the signals?",
        ["Choose signals", "Write my equations"],
        horizontal=True,
        key="sb_mode_v16",
    )

    if mode == "Choose signals":
        c1, c2 = st.columns(2)
        with c1:
            x_name = st.selectbox("Choose x(t)", list(SIGNALS), index=0, key="sb_x")
        with c2:
            h_name = st.selectbox("Choose h(t)", list(SIGNALS), index=1, key="sb_h")
        x_tau = sig(x_name, TAU)
        h_tau = sig(h_name, TAU)
        x_label, h_label = x_name, h_name
    else:
        st.write(
            "Use `t` as the time variable. Supported examples: "
            "`u(t)-u(t-2)`, `2*exp(-t)*u(t)`, `sin(2*t)`, `rect(t-1)`."
        )
        c1, c2 = st.columns(2)
        with c1:
            x_expr = st.text_input("x(t) =", "u(t)-u(t-2)", key="sb_x_expr")
        with c2:
            h_expr = st.text_input("h(t) =", "exp(-t)*u(t)", key="sb_h_expr")

        def _eval_np(expr, t):
            # Restricted numerical evaluator for the teaching expressions used here.
            env = {
                "t": t, "np": np,
                "u": lambda z: (np.asarray(z)>=0).astype(float),
                "rect": lambda z: (np.abs(np.asarray(z))<=0.5).astype(float),
                "tri": lambda z: np.maximum(1-np.abs(np.asarray(z)),0.0),
                "exp": np.exp, "sin": np.sin, "cos": np.cos,
                "sqrt": np.sqrt, "abs": np.abs,
            }
            safe = expr.replace("^","**")
            if not re.fullmatch(r"[0-9A-Za-z_+\\-*/().,\\s*]+", safe):
                raise ValueError("Unsupported characters")
            return np.asarray(eval(safe, {"__builtins__":{}}, env), dtype=float)

        try:
            x_tau = _eval_np(x_expr, TAU)
            h_tau = _eval_np(h_expr, TAU)
            if x_tau.ndim == 0: x_tau = np.full_like(TAU,float(x_tau))
            if h_tau.ndim == 0: h_tau = np.full_like(TAU,float(h_tau))
            x_label, h_label = x_expr, h_expr
        except Exception:
            st.error("Check the equation format. Use only the supported functions shown above.")
            return

    st.markdown("### Signals used")
    a,b=st.columns(2)
    with a: st.code(f"x(t) = {x_label}",language=None)
    with b: st.code(f"h(t) = {h_label}",language=None)

    t_now = st.slider("Choose t", -5.0, 5.0, 0.0, 0.25, key="sb_t")

    # Use interpolation so custom signals can be reversed and shifted numerically.
    h_flip = np.interp(-TAU, TAU, h_tau, left=0.0, right=0.0)
    h_shift = np.interp(t_now-TAU, TAU, h_tau, left=0.0, right=0.0)
    product = x_tau*h_shift
    area = float(np.trapezoid(product,TAU))
    full=np.convolve(x_tau,h_tau,mode="full")*DT
    tfull=np.linspace(TAU[0]+TAU[0],TAU[-1]+TAU[-1],len(full))
    y=np.interp(TAU,tfull,full)

    r1,r2=st.columns(2,gap="large")
    with r1:
        st.markdown("#### 1 — Flip")
        st.latex(r"h(\tau)\rightarrow h(-\tau)")
        mini_plot([(h_tau,r"$h(\tau)$",C_H,"--",1.4),
                   (h_flip,r"$h(-\tau)$",C_H,"-",2.1)],"Flip")
    with r2:
        st.markdown("#### 2 — Shift")
        st.latex(r"h(-\tau)\rightarrow h(t-\tau)")
        mini_plot([(h_flip,r"$h(-\tau)$",C_H,"--",1.4),
                   (h_shift,r"$h(t-\tau)$",C_H,"-",2.1)],f"Shift: t={t_now:.2f}")

    r3,r4=st.columns(2,gap="large")
    with r3:
        st.markdown("#### 3 — Overlay")
        mini_plot([(x_tau,r"$x(\tau)$",C_X,"-",2.1),
                   (h_shift,r"$h(t-\tau)$",C_H,"-",2.1)],"Overlap")
    with r4:
        st.markdown("#### 4 — Multiply")
        mini_plot([(product,r"$x(\tau)h(t-\tau)$",C_Y,"-",2.2)],"Product")

    st.markdown("#### 5 — Integrate")
    st.latex(rf"\boxed{{y({t_now:.2f})\approx {area:.4f}}}")

    _,center,_=st.columns([1,1.55,1])
    with center:
        fig,ax=plt.subplots(figsize=(4.5,1.65))
        ax.plot(TAU,y,color=C_Y,lw=2.1,label="y(t)")
        ax.scatter([t_now],[np.interp(t_now,TAU,y)],s=30,color=C_NOW,zorder=5)
        ax.axvline(t_now,ls="--",color=C_NOW,lw=1.0)
        format_axes(ax,"Complete convolution output","Time t")
        ax.legend(fontsize=6.5);fig.tight_layout(pad=.7)
        st.pyplot(fig,clear_figure=False,use_container_width=True)
        plt.close(fig)

def render_properties():
    st.header("Convolution Properties")
    st.write("Each property includes a numerical example showing how it is used.")

    props = [
        ("Commutative", r"x(t)*h(t)=h(t)*x(t)",
         "Interchanging x and h does not change the output.",
         r"x(t)=u(t)-u(t-2),\quad h(t)=u(t)-u(t-1)",
         r"x*h=h*x",
         "Both orders produce exactly the same convolution."),
        ("Associative", r"[g*h]*x=g*[h*x]",
         "The grouping of cascaded convolutions does not change the result.",
         r"x(t)=\delta(t),\quad g(t)=u(t),\quad h(t)=e^{-t}u(t)",
         r"[\delta*u]*h=u*h=\delta*[u*h]",
         "The impulse leaves the other signal unchanged, so both groupings agree."),
        ("Distributive", r"x*[h_1+h_2]=x*h_1+x*h_2",
         "Parallel contributions may be handled separately.",
         r"x(t)=u(t),\quad h_1(t)=\delta(t),\quad h_2(t)=\delta(t-2)",
         r"y(t)=u(t)+u(t-2)",
         "Convolve with each impulse separately and add the responses."),
        ("Causal", r"x,h\text{ causal}\Rightarrow y\text{ causal}",
         "Two causal signals produce a causal convolution.",
         r"x(t)=u(t)-u(t-1),\quad h(t)=e^{-t}u(t)",
         r"y(t)=0\quad\text{for }t<0",
         "Neither signal exists before t=0, so the convolution cannot begin before t=0."),
        ("Time shift", r"h(t-T_1)*x(t-T_2)=y(t-T_1-T_2)",
         "The delays add in the output.",
         r"T_1=2\,s,\quad T_2=3\,s",
         r"y_{\mathrm{shifted}}(t)=y(t-5)",
         "A 2-s delay plus a 3-s delay gives a 5-s output delay."),
        ("Impulse", r"x(t)*\delta(t-T)=x(t-T)",
         "A shifted impulse shifts the signal.",
         r"x(t)=u(t)-u(t-2),\quad T=3",
         r"x(t)*\delta(t-3)=u(t-3)-u(t-5)",
         "The pulse originally on [0,2] is shifted to [3,5]."),
        ("Area", r"A_y=A_xA_h",
         "The output area is the product of the input areas.",
         r"A_x=2,\quad A_h=3",
         r"A_y=(2)(3)=6",
         "The total area under the convolution is 6."),
        ("Step / Integration", r"x(t)*u(t)=\int_{-\infty}^{t}x(\tau)d\tau",
         "A unit-step impulse response performs integration.",
         r"x(t)=u(t)-u(t-2)",
         r"y(t)=\begin{cases}0&t<0\\t&0\le t<2\\2&t\ge2\end{cases}",
         "The output rises linearly from 0 to 2 and then remains at 2."),
    ]

    for name, eq, desc, example, result, explanation in props:
        with st.expander(name):
            st.latex(eq)
            st.write(desc)
            st.markdown("**Numerical example**")
            st.latex(example)
            st.markdown("**Result**")
            st.latex(result)
            st.caption(explanation)

def _conv_exam_bank():
    """Fixed internal bank of 50 convolution questions, from introductory to advanced."""
    Q=[]
    def add(prompt,options,answer,solution,level="Basic",graph=None):
        Q.append({
            "prompt":prompt,"options":options,"answer":answer,
            "solution":solution,"level":level,"graph":graph
        })

    # Fundamentals and graphical procedure (1-10)
    add("In graphical convolution, what operation converts h(τ) into h(−τ)?",
        ["Shift","Flip","Scale","Integrate"],"Flip",
        "Reflect h(τ) about τ=0 to obtain h(−τ).")
    add("After obtaining h(−τ), what operation produces h(t−τ)?",
        ["Differentiate","Shift","Scale","Integrate"],"Shift",
        "The reflected signal is shifted by t.")
    add("At a fixed t, what quantity gives y(t)?",
        ["Peak of x(τ)","Area of x(τ)h(t−τ)","Width of h(t)","Slope of x(t)"],
        "Area of x(τ)h(t−τ)",
        "The convolution integral is the area under x(τ)h(t−τ).")
    add("Which variable is the dummy integration variable in y(t)=∫x(τ)h(t−τ)dτ?",
        ["t","τ","h","x"],"τ","τ is integrated out; t remains as the output-time variable.")
    add("For an LTI system with impulse response h(t), the zero-state output to x(t) is:",
        ["x(t)+h(t)","x(t)h(t)","x(t)*h(t)","x(t)/h(t)"],"x(t)*h(t)",
        "The LTI zero-state response is the convolution of input and impulse response.")
    add("Which statement is true about graphical and analytical convolution?",
        ["They produce different outputs","They are complementary ways to evaluate the same convolution",
         "Graphical convolution works only for discrete time","Analytical convolution requires no integration"],
        "They are complementary ways to evaluate the same convolution",
        "Both evaluate the same convolution integral; one emphasizes visualization and the other algebra.")
    add("If x(τ) and h(t−τ) do not overlap at a particular t, then y(t) is:",
        ["1","∞","0","Undefined"],"0","The product is zero everywhere, so its integral is zero.")
    add("When the overlap between two nonnegative pulses increases, y(t) generally:",
        ["Decreases","Increases","Becomes negative","Must remain constant"],"Increases",
        "For nonnegative pulses, greater overlap gives a larger product area.")
    add("The symbol * between two signals denotes:",
        ["Ordinary multiplication","Convolution","Correlation only","Differentiation"],"Convolution",
        "In Signals and Systems, x*h denotes convolution.")
    add("Which expression is equivalent to x(t)*h(t)?",
        ["∫x(τ)h(t−τ)dτ","∫x(t)h(t)dτ","x(t)h(t)","x(t)+h(t)"],
        "∫x(τ)h(t−τ)dτ","This is the continuous-time convolution integral.")

    # Properties (11-25)
    add("Which convolution property states x*h = h*x?",
        ["Associative","Commutative","Distributive","Time-shift"],"Commutative",
        "Convolution is commutative: x(t)*h(t)=h(t)*x(t).")
    add("Which expression demonstrates associativity?",
        ["x*h=h*x","x*(h1+h2)=x*h1+x*h2","(x*h)*g=x*(h*g)","x*δ=x"],
        "(x*h)*g=x*(h*g)","Associativity allows regrouping cascaded convolutions.")
    add("Which expression demonstrates distributivity?",
        ["x*(h1+h2)=x*h1+x*h2","x*h=h*x","(x*h)*g=x*(h*g)","x*u=x"],
        "x*(h1+h2)=x*h1+x*h2","Convolution distributes over addition.")
    add("If x(t) and h(t) are both causal, x*h is:",
        ["Always anti-causal","Causal","Always periodic","Zero"],"Causal",
        "The convolution of two causal signals is causal.")
    add("For causal x and h, the convolution integral can be written with limits:",
        ["−∞ to ∞ only","0 to t","t to ∞","−t to t"],"0 to t",
        "For causal signals, nonzero overlap is restricted to 0≤τ≤t.")
    add("If y=x*h, then x(t−T1)*h(t−T2) equals:",
        ["y(t−T1−T2)","y(t−T1+T2)","y(t)","y(t−T1T2)"],
        "y(t−T1−T2)","The individual delays add in the convolution output.")
    add("x(t)*δ(t) equals:",
        ["0","δ(t)","x(t)","dx/dt"],"x(t)",
        "The unit impulse is the identity element for convolution.")
    add("x(t)*δ(t−T) equals:",
        ["x(t+T)","x(t−T)","Tx(t)","δ(t)"],"x(t−T)",
        "Convolution with a shifted impulse shifts x by the same amount.")
    add("x(t)*u(t) corresponds to:",
        ["Differentiation of x","Integration of x from −∞ to t","Time reversal","Scaling by t"],
        "Integration of x from −∞ to t",
        "A unit-step impulse response implements an ideal integrator.")
    add("For finite-duration signals, the output width is related to input widths by:",
        ["Wy=WxWh","Wy=Wx+Wh","Wy=Wx−Wh","Wy=max(Wx,Wh)"],
        "Wy=Wx+Wh","The convolution width property gives the sum of the two widths.")
    add("If Ax and Ah are the total areas under x and h, the area under y=x*h is:",
        ["Ax+Ah","Ax−Ah","AxAh","Ax/Ah"],"AxAh",
        "The area property of convolution states Ay=AxAh.")
    add("Two LTI systems with impulse responses h1 and h2 connected in series have equivalent impulse response:",
        ["h1+h2","h1h2","h1*h2","h1−h2"],"h1*h2",
        "Cascaded LTI systems combine by convolution of their impulse responses.")
    add("Two LTI systems in parallel have equivalent impulse response:",
        ["h1+h2","h1*h2","h1*h2 convolution only","h1/h2"],"h1+h2",
        "Parallel LTI branches add their impulse responses.")
    add("Why can x and h be interchanged during graphical convolution?",
        ["Because convolution is causal","Because convolution is commutative",
         "Because all signals are even","Because τ=t"],"Because convolution is commutative",
        "The commutative property lets us choose whichever signal is easier to flip and shift.")
    add("A delay in x of 2 s and a delay in h of 3 s produce an output delay of:",
        ["1 s","2 s","3 s","5 s"],"5 s",
        "By the time-shift property, delays add: 2+3=5 s.")

    # Rectangular-pulse calculations (26-38)
    add("x(t)=u(t)−u(t−2) and h(t)=u(t)−u(t−3). What is y(2)?",
        ["0","1","2","3"],"2",
        "At t=2, the unit-height pulses overlap over a width of 2, so y(2)=2.",
        "Intermediate",{"kind":"rect_pair","wx":2,"wh":3})
    add("For the same pulses x=u(t)−u(t−2), h=u(t)−u(t−3), the support of y(t) is:",
        ["0≤t≤2","0≤t≤3","0≤t≤5","−5≤t≤5"],"0≤t≤5",
        "The support duration is 2+3=5 s for these causal pulses.",
        "Intermediate",{"kind":"rect_pair","wx":2,"wh":3})
    add("Convolving two unit-height causal rectangular pulses of widths 1 s and 1 s produces which shape?",
        ["Rectangle","Triangle","Sinusoid","Impulse"],"Triangle",
        "Equal-width rectangles produce a triangular overlap-area function.",
        "Intermediate",{"kind":"rect_pair","wx":1,"wh":1})
    add("Two unit-height causal rectangles have widths 2 s and 4 s. What is the maximum convolution value?",
        ["1","2","4","6"],"2",
        "The maximum overlap width is the shorter width, 2 s; heights are both 1.",
        "Intermediate",{"kind":"rect_pair","wx":2,"wh":4})
    add("Two unit-height causal rectangles have widths 3 s and 5 s. What is the maximum y(t)?",
        ["3","5","8","15"],"3",
        "Maximum overlap equals the shorter width: min(3,5)=3.")
    add("A rectangle has amplitude 2 and width 3; another has amplitude 4 and width 1. Maximum convolution value is:",
        ["4","6","8","24"],"8",
        "Maximum overlap width is 1, and product height is 2×4=8, so peak area is 8.")
    add("Unit-height rectangles of widths 2 and 3 have total areas Ax=2 and Ah=3. Area under y is:",
        ["2","3","5","6"],"6","Ay=AxAh=2×3=6.")
    add("If x=u(t)−u(t−1) and h=u(t)−u(t−1), y(0.5) equals:",
        ["0","0.5","1","2"],"0.5",
        "At t=0.5, the overlap width is 0.5 and the product height is 1.")
    add("For x=u(t)−u(t−1) and h=u(t)−u(t−1), y(1) equals:",
        ["0","0.5","1","2"],"1",
        "At t=1 the two unit-height pulses fully overlap for width 1.")
    add("For x=u(t)−u(t−1) and h=u(t)−u(t−1), y(1.5) equals:",
        ["0","0.5","1","1.5"],"0.5",
        "After the peak, overlap decreases linearly; at t=1.5 the width is 0.5.")
    add("If two causal finite pulses have widths 2 s and 5 s, the convolution duration is:",
        ["2 s","3 s","5 s","7 s"],"7 s","The width property gives 2+5=7 s.")
    add("Two rectangles are both delayed: x starts at t=3 and h starts at t=1. Compared with their zero-start convolution, y starts:",
        ["1 s later","2 s later","4 s later","No delay"],"4 s later",
        "The time shifts add: 3+1=4 s.", "Advanced")
    add("For unit-height causal rectangles of widths 2 and 1, the convolution has:",
        ["Only a rising edge","Rise, flat region, fall","A sinusoidal shape","An impulse"],
        "Rise, flat region, fall",
        "Unequal rectangles create a trapezoidal overlap-area function: rise, full-overlap plateau, fall.",
        "Intermediate",{"kind":"rect_pair","wx":2,"wh":1})

    # Impulse, step, RC, and advanced reasoning (39-50)
    add("If x(t)=3δ(t−2) and h(t) is arbitrary, y(t)=x*h is:",
        ["h(t−2)","3h(t−2)","3h(t+2)","h(t)/3"],"3h(t−2)",
        "Scaling and shifting the impulse scales and shifts the impulse response.", "Advanced")
    add("If h(t)=δ(t−4), an LTI system acts as:",
        ["Differentiator","4× amplifier","4-second delay","Integrator"],"4-second delay",
        "y=x*δ(t−4)=x(t−4).")
    add("If h(t)=u(t), the LTI system acts as an ideal:",
        ["Differentiator","Integrator","Time reverser","Sampler"],"Integrator",
        "x*u is the running integral of x.")
    add("For an RC circuit with τc=0.5 s, the impulse response in the book example is:",
        ["e^(−t)u(t)","2e^(−2t)u(t)","0.5e^(−0.5t)u(t)","u(t−0.5)"],
        "2e^(−2t)u(t)",
        "For a first-order RC circuit h(t)=(1/τc)e^(−t/τc)u(t); with τc=0.5, h=2e^(−2t)u(t).",
        "Advanced")
    add("A 1-s unit rectangular pulse can be written as:",
        ["u(t)+u(t−1)","u(t)−u(t−1)","δ(t)−δ(t−1)","r(t)−r(t−1)"],
        "u(t)−u(t−1)","The two steps turn the pulse on at 0 and off at 1.")
    add("The convolution u(t)*u(t) is:",
        ["u(t)","δ(t)","t u(t)","e^(−t)u(t)"],"t u(t)",
        "For causal steps, ∫0^t 1 dτ=t, giving the unit ramp.", "Advanced")
    add("If x(t) is delayed by 3 s and h(t) is advanced by 1 s, the net shift of y is:",
        ["4 s delay","2 s delay","2 s advance","No shift"],"2 s delay",
        "The shifts add algebraically: +3+(−1)=+2 s.", "Advanced")
    add("A measured input signal is difficult to model analytically. Which convolution approach is a useful default?",
        ["Numerical integration","Only graphical construction","Only symbolic integration","No method works"],
        "Numerical integration",
        "Numerical convolution is especially useful for measured or difficult-to-model signals.")
    add("Which statement about the convolution integral assumes zero initial conditions?",
        ["The zero-state response y=x*h","The total response with arbitrary stored energy",
         "Only the step response","Only discrete-time systems"],"The zero-state response y=x*h",
        "The convolution integral gives the response due to the input under zero initial conditions.", "Advanced")
    add("If x and h each have unit area, what is the area of y=x*h?",
        ["0","1","2","Depends on delay"],"1","Ay=AxAh=1×1=1.")
    add("For h1 and h2 in series on one branch and h3 and h4 in series on another parallel branch, equivalent h is:",
        ["h1+h2+h3+h4","h1*h2+h3*h4","h1*h2 + h3*h4","h1h2h3h4"],
        "h1*h2 + h3*h4",
        "Series impulse responses convolve; parallel branch impulse responses add.", "Advanced")
    add("Which property is most useful for simplifying convolution of delayed rectangular pulses?",
        ["Time-shift property","Only differentiation","Periodicity","Odd symmetry only"],
        "Time-shift property",
        "Shift the pulses to simpler locations, convolve, then restore the combined delay.", "Advanced")
    add("If y=x*h and x is differentiated once before entering the same LTI system, the new output is:",
        ["y(t)","dy/dt","∫y dt","−y(t)"],"dy/dt",
        "Differentiation can be transferred through convolution: (dx/dt)*h=d(x*h)/dt.", "Advanced")

    # Keep the internal bank at exactly 50 questions without crashing the app
    # if the bank is edited later.
    if len(Q) > 50:
        Q = Q[:50]
    elif len(Q) < 50:
        # This should not normally be needed, but prevents the whole module
        # from failing if a future edit accidentally removes a question.
        while len(Q) < 50:
            n = len(Q) + 1
            add(
                f"Convolution review question {n}: Which expression defines continuous-time convolution?",
                ["∫x(τ)h(t−τ)dτ", "x(t)h(t)", "x(t)+h(t)", "dx(t)/dt"],
                "∫x(τ)h(t−τ)dτ",
                "Continuous-time convolution is y(t)=∫x(τ)h(t−τ)dτ.",
                "Basic",
            )
    return Q

def _draw_exam_graph(graph):
    if not graph:
        return
    if graph.get("kind")=="rect_pair":
        wx=float(graph["wx"]); wh=float(graph["wh"])
        tt=np.linspace(-1, max(wx,wh)+1, 600)
        xx=((tt>=0)&(tt<=wx)).astype(float)
        hh=((tt>=0)&(tt<=wh)).astype(float)
        fig,ax=plt.subplots(figsize=(5.2,1.8))
        ax.plot(tt,xx,color=C_X,lw=2.2,label="x(t)")
        ax.plot(tt,hh,color=C_H,lw=2.2,ls="--",label="h(t)")
        ax.set_title("Signals for this question",fontsize=9)
        ax.set_xlabel("Time t",fontsize=8); ax.set_ylabel("Amplitude",fontsize=8)
        ax.tick_params(labelsize=7); ax.grid(True,alpha=.25); ax.legend(fontsize=7)
        fig.tight_layout(pad=.7)
        _,c,_=st.columns([1,1.5,1])
        with c:
            st.pyplot(fig,clear_figure=False,use_container_width=True)
        plt.close(fig)

def render_mini_exam():
    st.header("Mini Exam — Convolution")
    st.write("Ten questions are selected randomly from an internal bank of 50 questions. The difficulty ranges from graphical fundamentals to convolution properties and analytical applications.")

    bank=_conv_exam_bank()

    if "conv_exam_ids" not in st.session_state:
        st.session_state.conv_exam_ids=random.sample(range(len(bank)),10)
        st.session_state.conv_exam_graded=False
        st.session_state.conv_exam_answers={}

    if st.button("Generate new exam",type="primary",key="conv_new_exam"):
        st.session_state.conv_exam_ids=random.sample(range(len(bank)),10)
        st.session_state.conv_exam_graded=False
        st.session_state.conv_exam_answers={}
        st.rerun()

    graded=st.session_state.conv_exam_graded
    score=0

    for pos,qid in enumerate(st.session_state.conv_exam_ids,1):
        q=bank[qid]
        current=st.session_state.conv_exam_answers.get(qid,None)
        correct=(current==q["answer"]) if graded else None

        if graded:
            mark="✓ CORRECT" if correct else "✗ INCORRECT"
            color="#21c55d" if correct else "#ff4b4b"
            st.markdown(
                f"""<div style="display:flex;justify-content:space-between;align-items:center;">
                <h3 style="margin-bottom:.25rem;">{pos}. {q["prompt"]}</h3>
                <strong style="color:{color};">{mark}</strong></div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"### {pos}. {q['prompt']}")

        _draw_exam_graph(q.get("graph"))

        # Keep the student's answer visible after grading.
        idx=None
        if current in q["options"]:
            idx=q["options"].index(current)
        choice=st.radio(
            "Select one answer",
            q["options"],
            index=idx,
            key=f"conv_exam_q_{qid}",
            disabled=graded,
        )
        if not graded and choice is not None:
            st.session_state.conv_exam_answers[qid]=choice
        if graded and correct:
            score+=1
        st.divider()

    if not graded:
        if st.button("Grade exam",type="primary",key="conv_grade"):
            # Store current widget values before grading.
            for qid in st.session_state.conv_exam_ids:
                key=f"conv_exam_q_{qid}"
                if key in st.session_state and st.session_state[key] is not None:
                    st.session_state.conv_exam_answers[qid]=st.session_state[key]
            st.session_state.conv_exam_graded=True
            st.rerun()
    else:
        # Recompute score from stored answers.
        score=sum(
            st.session_state.conv_exam_answers.get(qid)==bank[qid]["answer"]
            for qid in st.session_state.conv_exam_ids
        )
        st.markdown(f"# Score: {score}/10")
        st.markdown("## Review solutions")
        st.write("Open a question to review the solution.")

        for pos,qid in enumerate(st.session_state.conv_exam_ids,1):
            q=bank[qid]
            user_ans=st.session_state.conv_exam_answers.get(qid,"No answer")
            with st.expander(f"Question {pos} — Show correct answer and solution"):
                st.markdown(f"**Question:** {q['prompt']}")
                _draw_exam_graph(q.get("graph"))
                st.markdown(f"**Your answer:** {user_ans}")
                st.markdown(f"**Correct answer:** {q['answer']}")
                st.write(q["solution"])

def render():
    render_chapter_header(
        "CONVOLUTION",
        "Signals and Systems | Graphical intuition, real-time convolution, and step-by-step analysis",
    )

    concept, live, steps, properties, practice = st.tabs(
        ["Concept", "Live Convolution Lab", "Step-by-Step", "Properties", "Mini Exam"]
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
        render_mini_exam()

    st.divider()
    st.caption("EE-207 Convolution Module — Watch the process, then analyze it mathematically.")
