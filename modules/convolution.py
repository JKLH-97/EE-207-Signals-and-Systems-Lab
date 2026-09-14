import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ---------- Visual language ----------
C_X = "tab:blue"
C_H = "tab:orange"
C_RESULT = "tab:green"
C_AUX = "tab:purple"

T = np.linspace(-6, 6, 2401)
DT = T[1] - T[0]

def unit_step(t):
    return (np.asarray(t) >= 0).astype(float)

def rect(t, width=2.0):
    return (np.abs(np.asarray(t)) <= width/2).astype(float)

def tri(t, width=2.0):
    return np.maximum(1 - np.abs(np.asarray(t))/(width/2), 0.0)

SIGNALS = {
    "Unit step u(t)": lambda t: unit_step(t),
    "Rectangular pulse": lambda t: rect(t, 2.0),
    "Wide rectangular pulse": lambda t: rect(t, 4.0),
    "Triangular pulse": lambda t: tri(t, 4.0),
    "Decaying exponential e^(-t)u(t)": lambda t: np.exp(-np.maximum(t,0))*unit_step(t),
    "Gaussian exp(-t²)": lambda t: np.exp(-t**2),
}

def sig(name, t):
    return np.asarray(SIGNALS[name](np.asarray(t)), dtype=float)

def conv_same(x, h):
    full = np.convolve(x, h, mode="full") * DT
    tfull = np.linspace(T[0]+T[0], T[-1]+T[-1], len(full))
    return np.interp(T, tfull, full)

def small_plot(series, title, xlabel="Time"):
    fig, ax = plt.subplots(figsize=(4.8, 2.45))
    for y,label,color,style,width in series:
        ax.plot(T,y,linestyle=style,color=color,linewidth=width,label=label)
    ax.set_title(title,fontsize=10)
    ax.set_xlabel(xlabel,fontsize=9); ax.set_ylabel("Amplitude",fontsize=9)
    ax.tick_params(labelsize=8); ax.grid(True,alpha=.3)
    ax.legend(fontsize=8); ax.set_xlim(-6,6); fig.tight_layout()
    st.pyplot(fig,clear_figure=True,use_container_width=True)

def centered_plot(series, title, xlabel="Time"):
    _, c, _ = st.columns([1,1.75,1], gap="large")
    with c:
        small_plot(series,title,xlabel)

def render_cover():
    banner = Path(__file__).resolve().parent.parent / "assets" / "convolution_banner.png"
    if banner.exists():
        st.markdown(
            """
            <style>
            .ee207-conv-cover-marker + div[data-testid="stImage"],
            .ee207-conv-cover-marker + div[data-testid="stImage"] > div {
                width:100% !important; max-width:none !important;
            }
            .ee207-conv-cover-marker + div[data-testid="stImage"] img {
                width:100% !important; max-width:none !important;
                height:auto !important; display:block !important;
                object-fit:contain !important;
            }
            </style>
            <div class="ee207-conv-cover-marker"></div>
            """,
            unsafe_allow_html=True,
        )
        st.image(str(banner), use_container_width=True)
    else:
        st.title("EE-207 : Convolution")
    st.caption("Signals and Systems | Understand convolution graphically through flip, shift, multiply, and integrate")

def render():
    render_cover()

    concept, graphical, explorer, properties, practice = st.tabs([
        "Concept", "Graphical Convolution Lab", "Convolution Explorer",
        "Properties", "Practice"
    ])

    with concept:
        st.subheader("What is convolution?")
        st.write("For an LTI system, the output is obtained by convolving the input signal with the impulse response.")
        st.latex(r"\boxed{y(t)=x(t)*h(t)=\int_{-\infty}^{\infty}x(\tau)h(t-\tau)\,d\tau}")
        st.write("The graphical method turns the integral into four visual operations:")
        c1,c2,c3,c4=st.columns(4)
        c1.markdown("### 1. Flip\n$h(\\tau)\\rightarrow h(-\\tau)$")
        c2.markdown("### 2. Shift\n$h(-\\tau)\\rightarrow h(t-\\tau)$")
        c3.markdown("### 3. Multiply\n$x(\\tau)h(t-\\tau)$")
        c4.markdown("### 4. Integrate\nArea $=y(t)$")
        st.divider()
        st.markdown("## Example")
        st.write("A good first experiment is the convolution of two rectangular pulses. As one pulse slides across the other, the overlap area grows, reaches a maximum, and then decreases.")
        a,b=st.columns(2,gap="large")
        with a:
            small_plot([(sig("Rectangular pulse",T),"x(t)",C_X,"-",2.6)],"Input x(t)")
        with b:
            small_plot([(sig("Wide rectangular pulse",T),"h(t)",C_H,"-",2.6)],"Impulse response h(t)")
        y=conv_same(sig("Rectangular pulse",T),sig("Wide rectangular pulse",T))
        centered_plot([(y,"y(t)=x*h",C_RESULT,"-",2.8)],"Convolution output")

    with graphical:
        st.header("Graphical Convolution Lab — Flip, Shift, Multiply, Integrate")
        st.markdown("### Step 1 — Choose the experiment")
        c1,c2=st.columns(2)
        with c1:
            xn=st.selectbox("Choose x(t)",list(SIGNALS),index=1,key="gc_x")
        with c2:
            hn=st.selectbox("Choose h(t)",list(SIGNALS),index=2,key="gc_h")
        tv=st.slider("Shift t", -5.0, 5.0, 0.0, 0.25, key="gc_t")
        if st.button("Confirm signals",type="primary",key="gc_confirm"):
            st.session_state.gc_cfg=(xn,hn,tv)
        if "gc_cfg" not in st.session_state:
            st.info("Choose x(t), h(t), and the shift t, then click **Confirm signals**.")
        else:
            xn,hn,_=st.session_state.gc_cfg
            # Keep slider live after confirmation.
            x_tau=sig(xn,T)
            h_tau=sig(hn,T)
            h_flip=sig(hn,-T)
            h_shift=sig(hn,tv-T)
            product=x_tau*h_shift
            area=float(np.trapz(product,T))
            y=conv_same(x_tau,h_tau)
            y_at=float(np.interp(tv,T,y))

            st.markdown("### Step 2 — Build the convolution graphically")
            st.latex(r"y(t)=\int_{-\infty}^{\infty}x(\tau)h(t-\tau)\,d\tau")
            p1,p2=st.columns(2,gap="large")
            with p1:
                st.markdown("#### 1 — Express the signals in τ")
                st.latex(r"x(t)\rightarrow x(\tau)")
                small_plot([(x_tau,"x(τ)",C_X,"-",2.6)],"x(τ)",xlabel="τ")
            with p2:
                st.markdown("#### 2 — Flip h(τ)")
                st.latex(r"h(\tau)\rightarrow h(-\tau)")
                small_plot([(h_tau,"previous: h(τ)",C_H,"--",1.7),(h_flip,"new: h(-τ)",C_H,"-",2.7)],"Flip",xlabel="τ")

            p3,p4=st.columns(2,gap="large")
            with p3:
                st.markdown("#### 3 — Shift the flipped signal")
                st.latex(rf"h(-\tau)\rightarrow h({tv:.2f}-\tau)")
                small_plot([(h_flip,"previous: h(-τ)",C_H,"--",1.7),(h_shift,"new: h(t-τ)",C_H,"-",2.7)],f"Shift: t = {tv:.2f}",xlabel="τ")
            with p4:
                st.markdown("#### 4 — Observe the overlap")
                st.latex(r"x(\tau)\quad\text{and}\quad h(t-\tau)")
                small_plot([(x_tau,"x(τ)",C_X,"-",2.5),(h_shift,"h(t-τ)",C_H,"-",2.5)],"Overlap",xlabel="τ")

            st.markdown("#### 5 — Multiply the overlapping signals")
            centered_plot([(product,"x(τ)h(t-τ)",C_RESULT,"-",2.8)],"Product",xlabel="τ")
            st.markdown("#### 6 — Integrate the product")
            st.latex(rf"\boxed{{y({tv:.2f})=\int x(\tau)h({tv:.2f}-\tau)d\tau\approx {area:.4f}}}")
            st.markdown("### Step 3 — Locate this value on the complete output")
            fig,ax=plt.subplots(figsize=(6.2,2.55))
            ax.plot(T,y,color=C_RESULT,linewidth=2.7,label="y(t)=x*h")
            ax.scatter([tv],[y_at],s=55,color=C_AUX,zorder=5,label=f"current t={tv:.2f}")
            ax.axvline(tv,linestyle="--",linewidth=1.4,color=C_AUX)
            ax.set_title("Complete convolution output"); ax.set_xlabel("Time t"); ax.set_ylabel("Amplitude")
            ax.grid(True,alpha=.3); ax.legend(); ax.set_xlim(-6,6); fig.tight_layout()
            _,cc,_=st.columns([1,1.75,1])
            with cc: st.pyplot(fig,clear_figure=True,use_container_width=True)
            st.success(f"Current overlap integral: y({tv:.2f}) ≈ {area:.4f}")

    with explorer:
        st.header("Convolution Explorer")
        st.write("Move the slider and watch the flipped impulse response slide across the input.")
        c1,c2=st.columns(2)
        with c1: ex=st.selectbox("Input x(t)",list(SIGNALS),index=1,key="ex_x")
        with c2: eh=st.selectbox("Impulse response h(t)",list(SIGNALS),index=1,key="ex_h")
        et=st.slider("Slide h(t-τ) using t",-5.0,5.0,0.0,0.1,key="ex_t")
        xv=sig(ex,T); hv=sig(eh,T); hs=sig(eh,et-T); prod=xv*hs; yy=conv_same(xv,hv)
        c3,c4=st.columns(2,gap="large")
        with c3:
            small_plot([(xv,"x(τ)",C_X,"-",2.5),(hs,"h(t-τ)",C_H,"-",2.5)],f"Sliding view: t={et:.2f}",xlabel="τ")
        with c4:
            small_plot([(prod,"product",C_RESULT,"-",2.7)],"Overlap product",xlabel="τ")
        fig,ax=plt.subplots(figsize=(6.2,2.55))
        ax.plot(T,yy,color=C_RESULT,linewidth=2.7,label="y(t)")
        ax.scatter([et],[np.interp(et,T,yy)],s=55,color=C_AUX,zorder=5,label="current output")
        ax.axvline(et,linestyle="--",color=C_AUX,linewidth=1.3)
        ax.set_title("Output built from overlap area"); ax.set_xlabel("Time t"); ax.set_ylabel("Amplitude")
        ax.grid(True,alpha=.3); ax.legend(); ax.set_xlim(-6,6); fig.tight_layout()
        _,cc,_=st.columns([1,1.75,1])
        with cc: st.pyplot(fig,clear_figure=True,use_container_width=True)

    with properties:
        st.header("Convolution Properties")
        st.write("Use these properties to simplify convolution before doing a long graphical or analytical calculation.")
        props=[
            ("Commutative",r"x(t)*h(t)=h(t)*x(t)","You may flip and shift whichever signal makes the graphical calculation easier."),
            ("Associative",r"[g(t)*h(t)]*x(t)=g(t)*[h(t)*x(t)]","The grouping of cascaded convolutions does not change the result."),
            ("Distributive",r"x(t)*[h_1(t)+h_2(t)]=x*h_1+x*h_2","Parallel contributions can be handled separately and then added."),
            ("Time shift",r"h(t-T_1)*x(t-T_2)=y(t-T_1-T_2)","Input/impulse-response delays add in the output."),
            ("Impulse",r"x(t)*\delta(t-T)=x(t-T)","Convolution with a shifted impulse shifts the signal."),
            ("Width",r"W_y=W_x+W_h","For finite-duration signals, output duration follows the sum of widths."),
            ("Area",r"A_y=A_xA_h","The area under the convolution equals the product of the input areas."),
            ("Step / Integration",r"x(t)*u(t)=\int_{-\infty}^{t}x(\tau)d\tau","A unit-step impulse response behaves as an ideal integrator."),
        ]
        for name,eq,desc in props:
            with st.expander(name):
                st.latex(eq); st.write(desc)

    with practice:
        st.header("Practice — Predict Before You Compute")
        st.write("Use the graphical intuition from the lab.")
        qs=[
            ("If x(t) and h(t) are interchanged, does y(t) change?","No","Convolution is commutative."),
            ("What operation produces h(-τ) from h(τ)?","Flip","Reverse the signal about τ=0."),
            ("After flipping h(τ), what produces h(t-τ)?","Shift","Shift the reversed signal by t."),
            ("What does the convolution integral measure graphically?","Overlap area","It integrates the product x(τ)h(t-τ)."),
            ("If two causal signals are convolved, is the result causal?","Yes","Causal convolved with causal is causal."),
        ]
        score=0
        for i,(q,ans,why) in enumerate(qs):
            st.markdown(f"### {i+1}. {q}")
            opts={
                0:["Yes","No"],
                1:["Flip","Shift","Scale"],
                2:["Flip","Shift","Differentiate"],
                3:["Overlap area","Peak only","Signal width only"],
                4:["Yes","No"],
            }[i]
            choice=st.radio("Answer",opts,index=None,horizontal=True,key=f"conv_q{i}")
            if st.button("Check",key=f"conv_check{i}"):
                if choice==ans: st.success("✓ Correct")
                else: st.error(f"✗ Incorrect — Correct answer: {ans}")
                st.write(why)

    st.divider()
    st.caption("EE-207 Convolution Module — Build intuition graphically, then connect the result to the convolution integral.")
