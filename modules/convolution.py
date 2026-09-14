import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

C_X = "tab:blue"
C_H = "tab:orange"
C_RESULT = "tab:green"
C_AUX = "tab:purple"

TAU = np.linspace(-6, 6, 1601)
DT = TAU[1] - TAU[0]

def unit_step(t):
    return (np.asarray(t) >= 0).astype(float)

def rect_centered(t, width=2.0):
    return (np.abs(np.asarray(t)) <= width/2).astype(float)

def rect_causal(t, width=2.0):
    t=np.asarray(t)
    return ((t>=0)&(t<=width)).astype(float)

def triangle_centered(t, width=4.0):
    return np.maximum(1-np.abs(np.asarray(t))/(width/2),0.0)

SIGNALS = {
    "Rectangular pulse (centered)": lambda t: rect_centered(t,2.0),
    "Wide rectangular pulse": lambda t: rect_centered(t,4.0),
    "Causal rectangular pulse": lambda t: rect_causal(t,2.0),
    "Triangular pulse": lambda t: triangle_centered(t,4.0),
    "Gaussian exp(-t²)": lambda t: np.exp(-np.asarray(t)**2),
    "Decaying exponential e^(-t)u(t)": lambda t: np.exp(-np.maximum(np.asarray(t),0))*unit_step(t),
    "Unit step u(t)": lambda t: unit_step(t),
}

def sig(name,t):
    return np.asarray(SIGNALS[name](np.asarray(t)),dtype=float)

def convolution_output(xname,hname):
    x=sig(xname,TAU); h=sig(hname,TAU)
    full=np.convolve(x,h,mode="full")*DT
    tfull=np.linspace(TAU[0]+TAU[0],TAU[-1]+TAU[-1],len(full))
    return np.interp(TAU,tfull,full)

def render_chapter_header(title, subtitle):
    st.markdown(
        f"""
        <div style="text-align:center; padding:2.35rem 0 1.45rem 0;">
            <div style="
                font-family:Georgia,'Times New Roman',serif;
                font-size:clamp(2.8rem,5vw,4.9rem);
                font-weight:600; letter-spacing:.075em; line-height:1.08;">
                {title}
            </div>
            <div style="width:92px;height:2px;margin:1.15rem auto .95rem auto;
                        background:currentColor;opacity:.32;"></div>
            <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
                        font-size:1rem;opacity:.68;">
                {subtitle}
            </div>
        </div>
        """, unsafe_allow_html=True)

def base_axes(ax,title,xlabel):
    ax.set_title(title,fontsize=10,fontweight="bold")
    ax.set_xlabel(xlabel,fontsize=9); ax.set_ylabel("Amplitude",fontsize=9)
    ax.tick_params(labelsize=8); ax.grid(True,alpha=.28); ax.set_xlim(-6,6)

def live_figure(xname,hname,tcur):
    x=sig(xname,TAU)
    hshift=sig(hname,tcur-TAU)
    prod=x*hshift
    y=convolution_output(xname,hname)
    ycur=float(np.interp(tcur,TAU,y))
    area=float(np.trapezoid(prod,TAU))

    fig=plt.figure(figsize=(10.5,7.2))
    gs=fig.add_gridspec(3,1,hspace=.52)

    ax1=fig.add_subplot(gs[0,0])
    ax1.plot(TAU,x,color=C_X,linewidth=2.5,label=r"$x(\tau)$")
    ax1.plot(TAU,hshift,color=C_H,linewidth=2.5,label=r"$h(t-\tau)$")
    overlap=(np.abs(x)>1e-10)&(np.abs(hshift)>1e-10)
    if np.any(overlap):
        ax1.fill_between(TAU,0,np.minimum(np.abs(x),np.abs(hshift)),
                         where=overlap,alpha=.16)
    base_axes(ax1,rf"1. Slide and overlap   —   t = {tcur:.2f}",r"$\tau$")
    ax1.legend(fontsize=8,loc="upper right")

    ax2=fig.add_subplot(gs[1,0])
    ax2.plot(TAU,prod,color=C_RESULT,linewidth=2.6,label=r"$x(\tau)h(t-\tau)$")
    ax2.fill_between(TAU,0,prod,alpha=.20)
    base_axes(ax2,rf"2. Multiply   —   overlap integral = {area:.4f}",r"$\tau$")
    ax2.legend(fontsize=8,loc="upper right")

    ax3=fig.add_subplot(gs[2,0])
    ax3.plot(TAU,y,color=C_RESULT,linewidth=2.7,label=r"$y(t)=x*h$")
    # Show the already swept portion more strongly and future portion faintly.
    past=TAU<=tcur
    ax3.plot(TAU[past],y[past],color=C_AUX,linewidth=3.0,label="built so far")
    ax3.scatter([tcur],[ycur],s=55,color=C_AUX,zorder=6,label="current y(t)")
    ax3.axvline(tcur,linestyle="--",linewidth=1.3,color=C_AUX)
    base_axes(ax3,"3. Build the convolution output","Time t")
    ax3.legend(fontsize=8,loc="upper right")

    fig.tight_layout()
    return fig,area,ycur

def step_plot(series,title,xlabel=r"$\tau$"):
    fig,ax=plt.subplots(figsize=(4.8,2.45))
    for y,label,color,style,width in series:
        ax.plot(TAU,y,label=label,color=color,linestyle=style,linewidth=width)
    base_axes(ax,title,xlabel); ax.legend(fontsize=8); fig.tight_layout()
    st.pyplot(fig,clear_figure=True,use_container_width=True)

def render():
    render_chapter_header(
        "CONVOLUTION",
        "Signals and Systems | See flip, shift, overlap, multiply, and integrate in real time",
    )

    concept, live, steps, properties, practice = st.tabs([
        "Concept", "Live Convolution Lab", "Step-by-Step", "Properties", "Practice"
    ])

    with concept:
        st.subheader("What is convolution?")
        st.write("For an LTI system, the output is the convolution of the input x(t) and the impulse response h(t).")
        st.latex(r"\boxed{y(t)=x(t)*h(t)=\int_{-\infty}^{\infty}x(\tau)h(t-\tau)\,d\tau}")
        st.write("Graphically, convolution is easier to understand as a sequence:")
        c1,c2,c3,c4=st.columns(4)
        c1.markdown("### 1. Flip\n$h(\\tau)\\to h(-\\tau)$")
        c2.markdown("### 2. Shift\n$h(-\\tau)\\to h(t-\\tau)$")
        c3.markdown("### 3. Multiply\n$x(\\tau)h(t-\\tau)$")
        c4.markdown("### 4. Integrate\n$y(t)=\\int(\\cdot)d\\tau$")
        st.divider()
        st.markdown("## Visual intuition")
        st.write("As the flipped impulse response slides across the input, the overlap changes. The integral of the product at each position becomes one point of the output y(t).")
        fig,_,_=live_figure("Rectangular pulse (centered)","Wide rectangular pulse",0.0)
        st.pyplot(fig,clear_figure=True,use_container_width=True)

    with live:
        st.header("Live Convolution Lab")
        st.write("Choose two signals, then move the slider or press Play. The three plots stay synchronized.")

        c1,c2=st.columns(2)
        with c1:
            xname=st.selectbox("Input x(t)",list(SIGNALS),index=0,key="live_x")
        with c2:
            hname=st.selectbox("Impulse response h(t)",list(SIGNALS),index=1,key="live_h")

        if "conv_t" not in st.session_state:
            st.session_state.conv_t=-5.0
        if "conv_play" not in st.session_state:
            st.session_state.conv_play=False

        b1,b2,b3,b4=st.columns([1,1,1,2])
        with b1:
            if st.button("↺ Reset",use_container_width=True,key="conv_reset"):
                st.session_state.conv_t=-5.0
                st.session_state.conv_play=False
                st.rerun()
        with b2:
            if st.button("▶ Play",use_container_width=True,key="conv_play_btn"):
                st.session_state.conv_play=True
        with b3:
            if st.button("⏸ Pause",use_container_width=True,key="conv_pause"):
                st.session_state.conv_play=False
        with b4:
            speed=st.select_slider("Speed",options=[0.5,1.0,2.0],value=1.0,key="conv_speed")

        tcur=st.slider("Current time t",-5.0,5.0,float(st.session_state.conv_t),0.1,key="conv_t_slider")
        st.session_state.conv_t=tcur

        fig,area,ycur=live_figure(xname,hname,tcur)
        st.pyplot(fig,clear_figure=True,use_container_width=True)

        m1,m2,m3=st.columns(3)
        m1.metric("Current t",f"{tcur:.2f}")
        m2.metric("Overlap integral",f"{area:.4f}")
        m3.metric("Current y(t)",f"{ycur:.4f}")

        st.latex(rf"y({tcur:.2f})=\int_{{-\infty}}^{{\infty}}x(\tau)h({tcur:.2f}-\tau)\,d\tau\approx {area:.4f}")

        if st.session_state.conv_play:
            if tcur < 5.0:
                st.session_state.conv_t=min(5.0,tcur+0.1*speed)
                # update widget state before rerun
                st.session_state.conv_t_slider=st.session_state.conv_t
                time.sleep(max(0.04,0.16/speed))
                st.rerun()
            else:
                st.session_state.conv_play=False
                st.success("Animation complete. Press Reset to run it again.")

    with steps:
        st.header("Step-by-Step — One Position at a Time")
        st.write("Freeze the convolution at one value of t and inspect every graphical operation.")
        c1,c2=st.columns(2)
        with c1: sx=st.selectbox("Choose x(t)",list(SIGNALS),index=0,key="step_x")
        with c2: sh=st.selectbox("Choose h(t)",list(SIGNALS),index=1,key="step_h")
        stime=st.slider("Choose t",-5.0,5.0,0.0,0.25,key="step_t")

        xv=sig(sx,TAU); hv=sig(sh,TAU); hflip=sig(sh,-TAU); hshift=sig(sh,stime-TAU)
        prod=xv*hshift; area=float(np.trapezoid(prod,TAU)); yy=convolution_output(sx,sh)

        st.latex(r"y(t)=\int_{-\infty}^{\infty}x(\tau)h(t-\tau)d\tau")
        r1,r2=st.columns(2,gap="large")
        with r1:
            st.markdown("#### 1 — Write the signals using τ")
            step_plot([(xv,r"$x(\tau)$",C_X,"-",2.6)],r"$x(\tau)$")
        with r2:
            st.markdown("#### 2 — Flip h(τ)")
            step_plot([(hv,r"$h(\tau)$",C_H,"--",1.7),(hflip,r"$h(-\tau)$",C_H,"-",2.7)],"Flip")

        r3,r4=st.columns(2,gap="large")
        with r3:
            st.markdown("#### 3 — Shift the flipped signal")
            step_plot([(hflip,r"$h(-\tau)$",C_H,"--",1.7),(hshift,r"$h(t-\tau)$",C_H,"-",2.7)],f"Shift to t={stime:.2f}")
        with r4:
            st.markdown("#### 4 — Overlay x(τ) and h(t−τ)")
            step_plot([(xv,r"$x(\tau)$",C_X,"-",2.5),(hshift,r"$h(t-\tau)$",C_H,"-",2.5)],"Overlap")

        st.markdown("#### 5 — Multiply")
        _,cc,_=st.columns([1,1.7,1])
        with cc:
            step_plot([(prod,r"$x(\tau)h(t-\tau)$",C_RESULT,"-",2.8)],"Product")
        st.markdown("#### 6 — Integrate")
        st.latex(rf"\boxed{{y({stime:.2f})\approx {area:.4f}}}")

        fig,ax=plt.subplots(figsize=(6.2,2.55))
        ax.plot(TAU,yy,color=C_RESULT,linewidth=2.7,label="y(t)")
        ax.scatter([stime],[np.interp(stime,TAU,yy)],s=55,color=C_AUX,zorder=5,label="current point")
        ax.axvline(stime,linestyle="--",color=C_AUX,linewidth=1.3)
        base_axes(ax,"Complete convolution output","Time t"); ax.legend(); fig.tight_layout()
        _,cc,_=st.columns([1,1.75,1])
        with cc: st.pyplot(fig,clear_figure=True,use_container_width=True)

    with properties:
        st.header("Convolution Properties")
        props=[
            ("Commutative",r"x(t)*h(t)=h(t)*x(t)","Interchanging x and h does not change the output."),
            ("Associative",r"[g*h]*x=g*[h*x]","The grouping of cascaded convolutions does not change the result."),
            ("Distributive",r"x*[h_1+h_2]=x*h_1+x*h_2","Parallel contributions may be convolved separately and added."),
            ("Causal * Causal",r"x(t),h(t)\text{ causal}\Rightarrow y(t)\text{ causal}","Two causal signals produce a causal convolution."),
            ("Time shift",r"h(t-T_1)*x(t-T_2)=y(t-T_1-T_2)","Delays add in the convolution output."),
            ("Impulse",r"x(t)*\delta(t-T)=x(t-T)","A shifted impulse shifts the signal."),
            ("Width",r"W_y=W_x+W_h","For finite-duration signals, convolution width follows the sum of widths."),
            ("Area",r"A_y=A_xA_h","The area of the convolution is the product of the two signal areas."),
            ("Step / Integration",r"x(t)*u(t)=\int_{-\infty}^{t}x(\tau)d\tau","Convolution with a unit step performs integration."),
        ]
        for name,eq,desc in props:
            with st.expander(name):
                st.latex(eq); st.write(desc)

    with practice:
        st.header("Practice — Predict Before You Compute")
        qs=[
            ("If x(t) and h(t) are interchanged, does y(t) change?",["Yes","No"],"No","Convolution is commutative."),
            ("What creates h(-τ) from h(τ)?",["Flip","Shift","Scale"],"Flip","Reverse h about τ=0."),
            ("What creates h(t-τ) after the flip?",["Flip","Shift","Differentiate"],"Shift","Slide the reversed signal by t."),
            ("Graphically, what determines y(t) at one position?",["Overlap integral","Peak only","Width only"],"Overlap integral","Integrate x(τ)h(t-τ)."),
            ("If x(t) and h(t) are causal, is x*h causal?",["Yes","No"],"Yes","Causal convolved with causal is causal."),
        ]
        for i,(q,opts,ans,why) in enumerate(qs):
            st.markdown(f"### {i+1}. {q}")
            choice=st.radio("Answer",opts,index=None,horizontal=True,key=f"conv_practice_{i}")
            if st.button("Check answer",key=f"conv_check_{i}"):
                if choice==ans: st.success("✓ Correct")
                else: st.error(f"✗ Incorrect — Correct answer: {ans}")
                st.write(why)

    st.divider()
    st.caption("EE-207 Convolution Module — Use the animation for intuition, then use the integral for analysis.")
