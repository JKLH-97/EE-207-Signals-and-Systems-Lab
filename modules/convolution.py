import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt

C_X = "tab:blue"
C_H = "tab:orange"
C_RESULT = "tab:green"
T = np.linspace(-6,6,1601)

def u(t): return (np.asarray(t)>=0).astype(float)
def causal_rect(t,w):
    t=np.asarray(t); return ((t>=0)&(t<=w)).astype(float)

def header():
    st.markdown("""<div style="text-align:center;padding:2.1rem 0 1.2rem 0"><div style="font-family:Georgia,'Times New Roman',serif;font-size:clamp(2.8rem,5vw,4.9rem);font-weight:600;letter-spacing:.075em">CONVOLUTION</div><div style="width:92px;height:2px;margin:1.1rem auto .9rem;background:currentColor;opacity:.32"></div><div style="opacity:.68">Signals and Systems | Flip, shift, multiply, and integrate</div></div>""",unsafe_allow_html=True)

def mini(series,title):
    fig,ax=plt.subplots(figsize=(3.7,1.65))
    for y,label,color,ls in series: ax.plot(T,y,label=label,color=color,linestyle=ls,linewidth=2.1)
    ax.set_title(title,fontsize=9); ax.set_xlabel(r"$\tau$",fontsize=8); ax.set_ylabel("Amp.",fontsize=8); ax.tick_params(labelsize=7); ax.grid(True,alpha=.25); ax.set_xlim(-4,5); ax.legend(fontsize=7); fig.tight_layout()
    st.pyplot(fig,clear_figure=True,use_container_width=True)

def render():
    header()
    concept,live,steps,properties,practice=st.tabs(["Concept","Live Convolution Lab","Step-by-Step","Properties","Practice"])
    with concept:
        st.subheader("Graphical convolution — worked example")
        st.write("Use two simple causal pulses so every operation is visible.")
        a,b=st.columns(2)
        with a: st.latex(r"x(t)=u(t)-u(t-2)")
        with b: st.latex(r"h(t)=u(t)-u(t-3)")
        x=causal_rect(T,2); h=causal_rect(T,3); hf=causal_rect(-T,3); t0=2.0; hs=causal_rect(t0-T,3); p=x*hs
        st.markdown("### Step 1 — Flip")
        st.latex(r"h(\tau)\rightarrow h(-\tau)")
        c1,c2=st.columns(2)
        with c1: mini([(h,r"$h(\tau)$",C_H,"-")],"Before flip")
        with c2: mini([(hf,r"$h(-\tau)$",C_H,"-")],"After flip")
        st.markdown("### Step 2 — Shift")
        st.write("Choose one snapshot, t = 2.")
        st.latex(r"h(-\tau)\rightarrow h(2-\tau)")
        c1,c2=st.columns(2)
        with c1: mini([(hf,r"$h(-\tau)$",C_H,"--")],"Flipped signal")
        with c2: mini([(hs,r"$h(2-\tau)$",C_H,"-")],"Shifted signal")
        st.markdown("### Step 3 — Overlay")
        st.latex(r"x(\tau)\quad\text{and}\quad h(2-\tau)")
        c1,c2=st.columns([1,1])
        with c1: mini([(x,r"$x(\tau)$",C_X,"-"),(hs,r"$h(2-\tau)$",C_H,"-")],"Overlap")
        with c2:
            st.markdown("### Step 4 — Multiply")
            st.latex(r"x(\tau)h(2-\tau)")
            mini([(p,r"$x(\tau)h(2-\tau)$",C_RESULT,"-")],"Product")
        area=float(np.trapezoid(p,T))
        st.markdown("### Step 5 — Integrate")
        st.latex(r"y(2)=\int_{-\infty}^{\infty}x(\tau)h(2-\tau)d\tau")
        st.success(f"At t = 2, overlap width = 2 and height = 1, so y(2) = {area:.2f}.")
    with live:
        st.header("Live Convolution Lab")
        st.write("This animation runs directly in the browser. Press Play and watch all three synchronized views: overlap, product, and the output being built.")
        components.html(LIVE_HTML,height=720,scrolling=False)
    with steps:
        st.header("Step-by-Step")
        st.write("Use the worked example in Concept first. Then use the Live Convolution Lab to see the same operations continuously as t changes.")
        st.latex(r"h(\tau)\rightarrow h(-\tau)\rightarrow h(t-\tau)\rightarrow x(\tau)h(t-\tau)\rightarrow y(t)")
    with properties:
        st.header("Convolution Properties")
        props=[("Commutative",r"x*h=h*x"),("Associative",r"(g*h)*x=g*(h*x)"),("Distributive",r"x*(h_1+h_2)=x*h_1+x*h_2"),("Time shift",r"h(t-T_1)*x(t-T_2)=y(t-T_1-T_2)"),("Impulse",r"x(t)*\delta(t-T)=x(t-T)"),("Area",r"A_y=A_xA_h")]
        for n,e in props:
            with st.expander(n): st.latex(e)
    with practice:
        st.header("Practice")
        st.write("Predict the operation before revealing the answer.")
        qs=[("What is the first graphical operation applied to h(τ)?",["Flip","Shift","Integrate"],"Flip"),("What does the area under x(τ)h(t−τ) represent?",["One value of y(t)","Only signal width","The derivative"],"One value of y(t)"),("Does swapping x and h change the convolution?",["Yes","No"],"No")]
        for i,(q,opts,ans) in enumerate(qs):
            st.markdown(f"### {i+1}. {q}"); pick=st.radio("Answer",opts,index=None,horizontal=True,key=f"cvq{i}")
            if st.button("Check",key=f"cvc{i}"):
                st.success("✓ Correct") if pick==ans else st.error(f"✗ Correct answer: {ans}")

LIVE_HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Convolution — flip, slide, multiply, integrate</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#08131c;
  --panel:#0d1f2c;
  --panel-edge:#17364a;
  --ink:#d3e3ee;
  --ink-dim:#7593a8;
  --ch-x:#45d0e8;
  --ch-h:#ffc23d;
  --ch-p:#ff6f9c;
  --ch-y:#6ede83;
  --sans:'Barlow Semi Condensed',ui-sans-serif,'Helvetica Neue',Arial,sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{
  background:var(--bg);color:var(--ink);font-family:var(--sans);
  font-size:14px;line-height:1.35;-webkit-font-smoothing:antialiased;
}
.wrap{
  max-width:1500px;margin:0 auto;padding:10px 14px 18px;
  display:grid;grid-template-columns:1fr 250px;gap:14px;align-items:start;
}
header{grid-column:1/-1;display:flex;align-items:baseline;gap:20px;flex-wrap:wrap;
  border-bottom:1px solid var(--panel-edge);padding-bottom:12px;margin-bottom:2px}
h1{font-size:24px;font-weight:600;letter-spacing:.005em}
.formula{font-family:var(--mono);font-size:16px;color:var(--ink-dim)}
.formula b{color:var(--ch-y);font-weight:500}
footer{display:none;grid-column:1/-1;display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px 24px;
  border-top:1px solid var(--panel-edge);padding-top:12px;margin-top:8px;
  font-size:15px;color:var(--ink-dim);letter-spacing:.01em}
footer em{font-style:normal;color:#5a7488}

/* ---- plot stack ---- */
.stack{display:flex;flex-direction:column;gap:10px}
.plot{background:var(--panel);border:1px solid var(--panel-edge);border-radius:3px;position:relative;overflow:hidden}
.plot canvas{display:block;width:100%}
.plot .cap{position:absolute;top:9px;left:14px;font-size:16px;font-weight:500;pointer-events:none;
  text-shadow:0 0 8px var(--panel),0 0 8px var(--panel)}
.plot .note{position:absolute;top:9px;right:14px;font-family:var(--mono);font-size:14px;color:var(--ink-dim);
  pointer-events:none;text-align:right;text-shadow:0 0 8px var(--panel),0 0 8px var(--panel)}
.k-x{color:var(--ch-x)} .k-h{color:var(--ch-h)} .k-p{color:var(--ch-p)} .k-y{color:var(--ch-y)}

/* ---- transport ---- */
.transport{margin-top:7px;background:var(--panel);border:1px solid var(--panel-edge);border-radius:3px;
  padding:8px 12px 9px;display:grid;grid-template-columns:auto 1fr auto;gap:18px;align-items:center}
.tval{font-family:var(--mono);font-size:26px;font-weight:500;color:var(--ch-h);min-width:118px}
.tval span{font-size:15px;color:var(--ink-dim)}
input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:26px;background:transparent;cursor:grab}
input[type=range]:active{cursor:grabbing}
input[type=range]::-webkit-slider-runnable-track{height:4px;background:var(--panel-edge);border-radius:2px}
input[type=range]::-moz-range-track{height:4px;background:var(--panel-edge);border-radius:2px}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:20px;height:20px;border-radius:50%;
  background:var(--ch-h);margin-top:-8px;border:3px solid var(--panel)}
input[type=range]::-moz-range-thumb{width:20px;height:20px;border-radius:50%;background:var(--ch-h);border:3px solid var(--panel)}
input[type=range]:focus-visible{outline:2px solid var(--ch-x);outline-offset:4px;border-radius:3px}
.btnrow{display:flex;gap:8px}
button{font-family:var(--sans);font-size:16px;color:var(--ink);background:#123044;border:1px solid var(--panel-edge);
  border-radius:3px;padding:7px 15px;cursor:pointer;transition:background .12s}
button:hover{background:#1a4460}
button:focus-visible{outline:2px solid var(--ch-x);outline-offset:2px}
button.go{background:var(--ch-y);border-color:var(--ch-y);color:#052611;font-weight:600;min-width:82px}
button.go:hover{background:#84e79a}

/* ---- side rail ---- */
.rail{display:flex;flex-direction:column;gap:8px}
.card{background:var(--panel);border:1px solid var(--panel-edge);border-radius:3px;padding:9px 10px 10px}
.card h2{font-size:17px;font-weight:600;margin-bottom:9px}
.card h2 i{font-style:normal;font-family:var(--mono);font-size:16px}
.picks{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.picks button{padding:7px 4px;font-size:15px;width:100%}
.picks button.wide{grid-column:1/-1}
.card.hx h2 i{color:var(--ch-x)}
.card.hh h2 i{color:var(--ch-h)}
.hx .picks button[aria-pressed=true]{background:#0f4d5c;border-color:var(--ch-x);color:#fff}
.hh .picks button[aria-pressed=true]{background:#5a4408;border-color:var(--ch-h);color:#fff}
.toggle{width:100%;margin-top:8px;font-size:15px;padding:7px 10px}
.toggle[aria-pressed=true]{background:#5a4408;border-color:var(--ch-h);color:#fff}

.custom{margin-top:9px}
.custom input{width:100%;font-family:var(--mono);font-size:15px;padding:8px 10px;background:var(--bg);
  color:var(--ink);border:1px solid var(--panel-edge);border-radius:3px}
.custom input:focus-visible{outline:2px solid var(--ch-x);outline-offset:1px}
.hh .custom input:focus-visible{outline-color:var(--ch-h)}
.custom input.bad{border-color:var(--ch-p)}
.custom .err{color:#ff8fb1;font-size:14px;min-height:20px;margin-top:4px;line-height:1.4}
.custom .help{color:var(--ink-dim);font-size:13.5px;line-height:1.5}
.custom .help code{font-family:var(--mono);color:var(--ink);white-space:nowrap}

.readout{font-family:var(--mono);font-size:15px;line-height:1.85}
.readout div{display:flex;justify-content:space-between;gap:10px}
.readout .lab{color:var(--ink-dim);flex-shrink:0}
.readout span:last-child{text-align:right}
.pairs{display:flex;flex-direction:column;gap:6px}
.pairs button{text-align:left;font-size:15px;padding:7px 11px}
.hint{font-size:15px;color:var(--ink-dim);line-height:1.5}
kbd{font-family:var(--mono);font-size:13px;background:#123044;border:1px solid var(--panel-edge);border-radius:3px;padding:1px 5px}

@media (max-width:1080px){
  .wrap{grid-template-columns:1fr}
  .rail{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}
}
@media (max-width:560px){
  body{font-size:16px}
  .wrap{padding:16px 14px 30px}
  h1{font-size:25px}
  .transport{grid-template-columns:1fr;gap:10px}
  .tval{min-width:0}
}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>Convolution, one slice at a time</h1>
  <div class="formula"><b>y(t)</b> = &#8747; x(&tau;)&#183;h(t&minus;&tau;) d&tau;</div>
</header>

<main class="stack">
  <div class="plot">
    <canvas id="cA"></canvas>
    <div class="cap"><span class="k-x">x(&tau;)</span> held still &nbsp;&#183;&nbsp; <span class="k-h">h(t&minus;&tau;)</span> flipped and slid</div>
    <div class="note" id="noteA"></div>
  </div>
  <div class="plot">
    <canvas id="cB"></canvas>
    <div class="cap"><span class="k-p">x(&tau;)&#183;h(t&minus;&tau;)</span> — the shaded area is one output value</div>
    <div class="note" id="noteB"></div>
  </div>
  <div class="plot">
    <canvas id="cC"></canvas>
    <div class="cap"><span class="k-y">y(t)</span> — that area, plotted against t</div>
    <div class="note" id="noteC"></div>
  </div>

  <div class="transport">
    <div class="tval"><span>t =</span> <b id="tOut">0.00</b></div>
    <input id="tSlide" type="range" min="-4" max="8" step="0.02" value="0" aria-label="Slide h across x">
    <div class="btnrow">
      <button class="go" id="play">Play</button>
      <button id="speed" title="Playback speed">1×</button>
      <button id="rew">Reset</button>
    </div>
  </div>
</main>

<aside class="rail">
  <div class="card hx">
    <h2>Input <i>x(t)</i></h2>
    <div class="picks" id="pickX"></div>
    <div class="custom" id="customX" hidden>
      <input id="exprX" type="text" spellcheck="false" autocomplete="off" aria-label="Expression for x(t)">
      <div class="err" id="errX"></div>
      <div class="help"><code>u(t)</code> step &nbsp; <code>r(t)</code> ramp &nbsp; <code>delta(t)</code> impulse<br>
        also <code>exp sin cos pi e ^</code> &nbsp; shift with <code>(t-2)</code></div>
    </div>
  </div>
  <div class="card hh">
    <h2>Impulse response <i>h(t)</i></h2>
    <div class="picks" id="pickH"></div>
    <div class="custom" id="customH" hidden>
      <input id="exprH" type="text" spellcheck="false" autocomplete="off" aria-label="Expression for h(t)">
      <div class="err" id="errH"></div>
      <div class="help"><code>u(t)</code> step &nbsp; <code>r(t)</code> ramp &nbsp; <code>delta(t)</code> impulse<br>
        also <code>exp sin cos pi e ^</code> &nbsp; shift with <code>(t-2)</code></div>
    </div>
    <button class="toggle" id="ghost" aria-pressed="false">Show h(&tau;) before the flip</button>
  </div>
  <div class="card">
    <h2>Live values</h2>
    <div class="readout">
      <div><span class="lab">overlap</span><span id="rOv">none</span></div>
      <div><span class="lab">width</span><span id="rW">0.00</span></div>
      <div><span class="lab">y(t)</span><span id="rY" style="color:var(--ch-y)">0.000</span></div>
      <div><span class="lab">max y shown</span><span id="rPk">0.000</span></div>
    </div>
  </div>
  <div class="card">
    <h2>Worth showing</h2>
    <div class="pairs" id="presets"></div>
  </div>
  <div class="card">
    <h2>Keys</h2>
    <p class="hint"><kbd>space</kbd> play or pause &nbsp; <kbd>&larr;</kbd><kbd>&rarr;</kbd> nudge t &nbsp; <kbd>R</kbd> reset</p>
  </div>
</aside>

<footer>
  <span>KFUPM &nbsp;&#183;&nbsp; EE207 &nbsp;&#183;&nbsp; Term 261</span>
  <span>Dr. Motaz Alfarraj <em>(made with Claude)</em></span>
</footer>

</div>

<script>
"use strict";

/* =====================================================================
   Expression language:  u, r, delta  (+ exp sin cos abs sqrt sgn, pi, e, ^)
   Impulse terms are extracted exactly so they can be drawn as arrows and
   convolved analytically instead of as tall numeric spikes.
   ===================================================================== */
const FUNCS = {
  u:    v => v>=0 ? 1 : 0,
  r:    v => v>0  ? v : 0,
  exp:  Math.exp, sin: Math.sin, cos: Math.cos, abs: Math.abs,
  sqrt: v => Math.sqrt(Math.max(0,v)),
  sgn:  v => v>0 ? 1 : (v<0 ? -1 : 0)
};
const DELTA_NAMES = new Set(["delta","d","δ","dirac","impulse"]);
const CONSTS = { pi:Math.PI, e:Math.E };

function tokenize(src){
  const toks=[]; let i=0;
  while(i<src.length){
    const c=src[i];
    if(/\s/.test(c)){ i++; continue; }
    if(/[0-9.]/.test(c)){
      const m=src.slice(i).match(/^(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?/);
      if(!m) throw new Error(`Bad number near "${src.slice(i,i+4)}"`);
      toks.push({t:"num",v:parseFloat(m[0])}); i+=m[0].length; continue;
    }
    if(/[A-Za-zδ_]/.test(c)){
      const m=src.slice(i).match(/^[A-Za-zδ_][A-Za-z0-9_]*/);
      toks.push({t:"id",v:m[0]}); i+=m[0].length; continue;
    }
    if("+-*/^(),".includes(c)){ toks.push({t:c}); i++; continue; }
    if(c==="·"||c==="×"){ toks.push({t:"*"}); i++; continue; }
    if(c==="−"){ toks.push({t:"-"}); i++; continue; }
    throw new Error(`Unexpected character "${c}"`);
  }
  return toks;
}

function parse(src){
  const toks=tokenize(src); let p=0;
  const peek=()=>toks[p], next=()=>toks[p++];
  const show=k=> k ? (k.t==="num"?k.v:(k.v||k.t)) : "end of expression";
  const expect=t=>{ const k=next(); if(!k||k.t!==t) throw new Error(`Expected "${t}" but found ${show(k)}`); };

  function expr(){
    let a=term();
    while(peek()&&(peek().t==="+"||peek().t==="-")){ const op=next().t; a={type:"bin",op,a,b:term()}; }
    return a;
  }
  function term(){
    let a=factor();
    for(;;){
      const k=peek(); if(!k) break;
      if(k.t==="*"||k.t==="/"){ next(); a={type:"bin",op:k.t,a,b:factor()}; }
      else if(k.t==="num"||k.t==="id"||k.t==="("){ a={type:"bin",op:"*",a,b:factor()}; }   // 2u(t), u(t)u(2-t)
      else break;
    }
    return a;
  }
  function factor(){
    const k=peek();
    if(k&&(k.t==="-"||k.t==="+")){ next(); const a=factor(); return k.t==="-"?{type:"neg",a}:a; }
    return power();
  }
  function power(){
    const a=atom();
    if(peek()&&peek().t==="^"){ next(); return {type:"bin",op:"^",a,b:factor()}; }
    return a;
  }
  function atom(){
    const k=next();
    if(!k) throw new Error("Expression ends too early");
    if(k.t==="num") return {type:"num",v:k.v};
    if(k.t==="("){ const a=expr(); expect(")"); return a; }
    if(k.t==="id"){
      const name=k.v;
      if(name==="t") return {type:"t"};
      if(name in CONSTS) return {type:"num",v:CONSTS[name]};
      const isDelta=DELTA_NAMES.has(name), isFn=name in FUNCS;
      if(!isDelta&&!isFn) throw new Error(`Unknown name "${name}" — try u, r, delta, exp, sin, cos`);
      if(!peek()||peek().t!=="(") throw new Error(`"${name}" needs an argument, e.g. ${name}(t-1)`);
      next(); const arg=expr(); expect(")");
      return isDelta ? {type:"delta",arg} : {type:"call",fn:name,arg};
    }
    throw new Error(`Unexpected "${show(k)}"`);
  }
  const ast=expr();
  if(p<toks.length) throw new Error(`Unexpected "${show(toks[p])}"`);
  return ast;
}

function ev(n,t,dfn){
  switch(n.type){
    case "num":   return n.v;
    case "t":     return t;
    case "neg":   return -ev(n.a,t,dfn);
    case "call":  return FUNCS[n.fn](ev(n.arg,t,dfn));
    case "delta": return dfn(n,t);
    case "bin": {
      const a=ev(n.a,t,dfn), b=ev(n.b,t,dfn);
      switch(n.op){
        case "+": return a+b;  case "-": return a-b;  case "*": return a*b;
        case "/": return b===0 ? 0 : a/b;
        case "^": return Math.pow(a,b);
      }
    }
  }
  return 0;
}

// delta may only be scaled and summed — never inside a function, exponent, or denominator
function checkDeltas(n,forbidden){
  if(n.type==="delta"){
    if(forbidden) throw new Error("delta(…) can be scaled and added, but not placed inside a function, exponent, or denominator");
    checkDeltas(n.arg,true); return;
  }
  if(n.type==="call") return checkDeltas(n.arg,true);
  if(n.type==="neg")  return checkDeltas(n.a,forbidden);
  if(n.type==="bin"){
    if(n.op==="^"){ checkDeltas(n.a,true); checkDeltas(n.b,true); return; }
    checkDeltas(n.a,forbidden); checkDeltas(n.b,forbidden||n.op==="/");
  }
}

function compile(src){
  if(!src.trim()) throw new Error("Type an expression in t");
  const ast=parse(src);
  checkDeltas(ast,false);
  const deltas=[];
  (function walk(n){ if(n.type==="delta") deltas.push(n); for(const k of ["a","b","arg"]) if(n[k]) walk(n[k]); })(ast);

  const off=()=>0;
  const smooth=t=>{ const v=ev(ast,t,off); return Number.isFinite(v)?v:0; };

  const found=[];
  for(const d of deltas){
    const g=v=>ev(d.arg,v,off);
    const b=g(0), a=g(1)-b;
    if(Math.abs(g(2)-(2*a+b))>1e-9) throw new Error("The argument of delta(…) must be linear in t, like delta(2t-1)");
    if(Math.abs(a)<1e-12) throw new Error("delta(…) needs t in its argument, like delta(t-1)");
    const loc=-b/a;
    const only=node=> node===d ? 1 : 0;
    const coeff=ev(ast,loc,only)-smooth(loc);          // whatever multiplies this impulse, sampled at its location
    const area=coeff/Math.abs(a);                       // δ(at+b) = δ(t+b/a)/|a|
    if(Math.abs(area)>1e-12) found.push({loc,area});
  }
  const impulses=[];                                    // merge impulses that land on the same spot
  found.sort((p,q)=>p.loc-q.loc).forEach(im=>{
    const last=impulses[impulses.length-1];
    if(last && Math.abs(last.loc-im.loc)<1e-9) last.area+=im.area; else impulses.push({...im});
  });
  return {smooth, impulses:impulses.filter(im=>Math.abs(im.area)>1e-12)};
}

/* ===== built-in signals share the compiled shape ================== */
const SIGNALS = {
  rect : {name:"Pulse",    smooth:t=>(t>=0&&t<1)?1:0,                    impulses:[], tex:"u(t) − u(t−1)"},
  tri  : {name:"Triangle", smooth:t=>t>=0&&t<=1?t:(t>1&&t<=2?2-t:0),      impulses:[], tex:"r(t) − 2r(t−1) + r(t−2)"},
  exp  : {name:"Decay",    smooth:t=>t>=0?Math.exp(-t):0,                 impulses:[], tex:"e^(−t) u(t)"},
  step : {name:"Step",     smooth:t=>t>=0?1:0,                            impulses:[], tex:"u(t)"},
  ramp : {name:"Ramp",     smooth:t=>(t>=0&&t<=2)?t/2:0,                  impulses:[], tex:"½ r(t), cut off at t = 2"},
  imp  : {name:"Impulse",  smooth:()=>0, impulses:[{loc:0,area:1}],        tex:"δ(t)"}
};
const custom = {
  x:{ expr:"2u(t+2) + r(t+1) - u(t-1) - 2r(t-2) + r(t-4)", sig:null },
  h:{ expr:"delta(t) + 0.5delta(t-2)", sig:null }
};
for(const w of ["x","h"]) custom[w].sig = compile(custom[w].expr);

let xKey="rect", hKey="rect", tNow=0, playing=false, raf=null;
let showGhost=false, speed=1;
const SPEEDS=[0.5,1,2];
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
const sigOf = w => (w==="x"?xKey:hKey)==="custom" ? custom[w].sig : SIGNALS[w==="x"?xKey:hKey];

/* ===== numerical grids ============================================ */
const TAU0=-8, TAU1=14, DT=0.005;
const NT = Math.round((TAU1-TAU0)/DT);
const TAU = new Float64Array(NT);
for(let i=0;i<NT;i++) TAU[i]=TAU0+(i+0.5)*DT;          // midpoint rule: exact on pulse edges

const T0=-4, T1=8, TSTEP=0.02;
const NY = Math.round((T1-T0)/TSTEP)+1;
const TG = new Float64Array(NY), YG = new Float64Array(NY);
const VIEW0=-4, VIEW1=8;

// h(t_k − τ_i) always lands on one fixed lattice, so sample h once and index into it
const R = Math.round(TSTEP/DT), OFF = NT-1, HG_LEN = R*(NY-1)+NT;
const BASE = (T0-TAU0) - 0.5*DT;
const xArr = new Float64Array(NT), hG = new Float64Array(HG_LEN);

let scA, scB, scC, yImp=[], yPeak=1, flatX=false, flatH=false;

function niceTop(v){
  for(const c of [0.5,1,1.5,2,3,4,5,6,8,10,15,20,30,50,100]) if(c>=v*0.999) return c;
  return Math.ceil(v);
}
function scaleFor(lo,hi){
  let top = hi> 1e-9 ?  niceTop(hi)  : 0;
  let bot = lo<-1e-9 ? -niceTop(-lo) : 0;
  if(top===0&&bot===0) top=1;
  const span=top-bot;
  const ticks=[0]; if(top>0) ticks.push(top/2,top); if(bot<0) ticks.push(bot/2,bot);
  return {vmin:bot-0.12*span, vmax:top+0.18*span, ticks, top, bot};
}

function rebuild(){
  const X=sigOf("x"), H=sigOf("h"), xs=X.smooth, hs=H.smooth;
  let xmin=0,xmax=0,hmin=0,hmax=0;
  for(let i=0;i<NT;i++){ const v=xs(TAU[i]); xArr[i]=v; if(v<xmin)xmin=v; if(v>xmax)xmax=v; }
  for(let j=0;j<HG_LEN;j++){ const v=hs(BASE+DT*(j-OFF)); hG[j]=v; if(v<hmin)hmin=v; if(v>hmax)hmax=v; }
  flatX = xmin===0&&xmax===0; flatH = hmin===0&&hmax===0;

  let pmin=0,pmax=0;
  for(let k=0;k<NY;k++){
    const t=T0+k*TSTEP; TG[k]=t;
    let s=0; const b=R*k+OFF;
    for(let i=0;i<NT;i++){
      const xv=xArr[i];
      if(xv!==0){ const p=xv*hG[b-i]; s+=p; if(p<pmin)pmin=p; if(p>pmax)pmax=p; }
    }
    s*=DT;
    for(const im of X.impulses) s+=im.area*hs(t-im.loc);     // δ in x samples h
    for(const im of H.impulses) s+=im.area*xs(t-im.loc);     // δ in h samples x
    YG[k]=s;
  }
  const pairs=[];                                              // δ ⊛ δ → δ in y
  for(const a of X.impulses) for(const b of H.impulses) pairs.push({loc:a.loc+b.loc, area:a.area*b.area});
  yImp=[]; pairs.sort((p,q)=>p.loc-q.loc).forEach(im=>{
    const last=yImp[yImp.length-1];
    if(last&&Math.abs(last.loc-im.loc)<1e-9) last.area+=im.area; else yImp.push({...im});
  });

  // vertical scales are fixed for the whole sweep so frames stay comparable
  let aLo=Math.min(xmin,hmin), aHi=Math.max(xmax,hmax);
  for(const im of [...X.impulses,...H.impulses]){ aLo=Math.min(aLo,im.area); aHi=Math.max(aHi,im.area); }
  scA=scaleFor(aLo,aHi);

  for(const im of X.impulses){ pmin=Math.min(pmin,im.area*hmin,im.area*hmax); pmax=Math.max(pmax,im.area*hmin,im.area*hmax); }
  for(const im of H.impulses){ pmin=Math.min(pmin,im.area*xmin,im.area*xmax); pmax=Math.max(pmax,im.area*xmin,im.area*xmax); }
  scB=scaleFor(pmin,pmax);

  let ymin=0,ymax=0;
  for(let k=0;k<NY;k++){ if(YG[k]<ymin)ymin=YG[k]; if(YG[k]>ymax)ymax=YG[k]; }
  for(const im of yImp){ ymin=Math.min(ymin,im.area); ymax=Math.max(ymax,im.area); }
  scC=scaleFor(ymin,ymax);
  yPeak=Math.max(-ymin,ymax);
  document.getElementById("rPk").textContent=yPeak.toFixed(3);
  drawAll();
}
const yAt = t => YG[Math.min(NY-1,Math.max(0,Math.round((t-T0)/TSTEP)))];

/* ===== canvas plumbing ============================================ */
function setup(cv,h){
  const dpr=window.devicePixelRatio||1, w=cv.parentNode.clientWidth;
  cv.width=w*dpr; cv.height=h*dpr; cv.style.height=h+"px";
  const g=cv.getContext("2d"); g.setTransform(dpr,0,0,dpr,0,0); g.clearRect(0,0,w,h);
  return {g,w,h};
}
const PAD={l:48,r:38,t:34,b:24};
function mapper(w,h,sc){
  const L=PAD.l, R=w-PAD.r, T=PAD.t, B=h-PAD.b;
  return { X:v=>L+(v-VIEW0)/(VIEW1-VIEW0)*(R-L), Y:v=>B-(v-sc.vmin)/(sc.vmax-sc.vmin)*(B-T), L,R,T,B };
}
const fmt = v => { const s=v.toFixed(2); return s.replace(/\.?0+$/,"").replace(/^-0$/,"0"); };
function axisLetter(g,m,ch){
  g.fillStyle="#7593a8"; g.font="italic 14px 'IBM Plex Mono',monospace";
  g.textAlign="left"; g.textBaseline="top"; g.fillText(ch,m.R+16,m.B+4);
}
function grid(g,m,sc,mark){
  g.lineWidth=1;
  for(let v=Math.ceil(VIEW0);v<=VIEW1;v++){
    const x=Math.round(m.X(v))+.5;
    g.strokeStyle = v===0 ? "rgba(122,164,190,.34)" : "rgba(122,164,190,.10)";
    g.beginPath(); g.moveTo(x,m.T); g.lineTo(x,m.B); g.stroke();
  }
  g.strokeStyle="rgba(122,164,190,.10)";
  sc.ticks.forEach(v=>{ const y=Math.round(m.Y(v))+.5; g.beginPath(); g.moveTo(m.L,y); g.lineTo(m.R,y); g.stroke(); });
  const y0=Math.round(m.Y(0))+.5;
  g.strokeStyle="rgba(122,164,190,.45)"; g.beginPath(); g.moveTo(m.L,y0); g.lineTo(m.R,y0); g.stroke();

  // the moving "t" marker on the horizontal axis
  let markX=null, markHalf=0, markText="";
  if(mark && mark.v>=VIEW0 && mark.v<=VIEW1){
    markX=m.X(mark.v); markText=mark.label;
    g.font="600 13px 'IBM Plex Mono',monospace";
    markHalf=g.measureText(markText).width/2;
  }

  g.fillStyle="#7593a8"; g.font="13px 'IBM Plex Mono',monospace";
  g.textAlign="center"; g.textBaseline="top";
  for(let v=Math.ceil(VIEW0);v<=VIEW1;v+=2){
    if(v===0) continue;
    if(markX!==null && Math.abs(m.X(v)-markX) < markHalf+14) continue;   // yield to the t marker
    g.fillText(String(v),m.X(v),m.B+5);
  }
  g.textAlign="right"; g.textBaseline="middle";
  sc.ticks.forEach(v=>{ if(v!==0) g.fillText(fmt(v),m.L-7,m.Y(v)); });

  if(markX!==null){
    const X=Math.round(markX)+.5;
    g.strokeStyle="rgba(255,194,61,.42)"; g.lineWidth=1; g.setLineDash([2,5]);
    g.beginPath(); g.moveTo(X,m.T); g.lineTo(X,m.B); g.stroke(); g.setLineDash([]);
    g.fillStyle="#ffc23d";
    g.beginPath(); g.moveTo(markX,m.B+1); g.lineTo(markX-5,m.B+8); g.lineTo(markX+5,m.B+8); g.closePath(); g.fill();
    g.font="600 13px 'IBM Plex Mono',monospace"; g.textAlign="center"; g.textBaseline="top";
    const tx=Math.min(m.R-markHalf, Math.max(m.L+markHalf, markX));            // keep the text inside the panel
    g.fillText(markText,tx,m.B+9);
  }
}
function trace(g,m,sc,fn,color,width){
  g.strokeStyle=color; g.lineWidth=width; g.lineJoin="round"; g.lineCap="round"; g.beginPath();
  const px=Math.max(1,Math.round(m.R-m.L));
  for(let i=0;i<=px;i++){
    const v=Math.max(sc.vmin,Math.min(sc.vmax,fn(VIEW0+(i/px)*(VIEW1-VIEW0))));
    i?g.lineTo(m.L+i,m.Y(v)):g.moveTo(m.L+i,m.Y(v));
  }
  g.stroke();
}
function fillUnder(g,m,sc,fn,color){
  g.fillStyle=color; g.beginPath(); g.moveTo(m.L,m.Y(0));
  const px=Math.max(1,Math.round(m.R-m.L));
  for(let i=0;i<=px;i++){
    const v=Math.max(sc.vmin,Math.min(sc.vmax,fn(VIEW0+(i/px)*(VIEW1-VIEW0))));
    g.lineTo(m.L+i,m.Y(v));
  }
  g.lineTo(m.R,m.Y(0)); g.closePath(); g.fill();
}
// arrow length in data units: the true area, clamped to stay inside the panel and stay visible
function arrowLen(area,sc){
  const cap = area>=0 ? sc.vmax*0.94 : -sc.vmin*0.94;
  const mag = Math.max(0.12*(sc.top-sc.bot), Math.min(Math.abs(area),cap));
  return (area<0?-1:1)*mag;
}
function arrow(g,m,sc,xv,area,color,label){
  if(xv<VIEW0||xv>VIEW1) return;
  const X=m.X(xv), Y0=m.Y(0), Y1=m.Y(arrowLen(area,sc)), s=Y1<Y0?1:-1;
  g.strokeStyle=color; g.fillStyle=color; g.lineWidth=2.5;
  g.beginPath(); g.moveTo(X,Y0); g.lineTo(X,Y1+s*9); g.stroke();
  g.beginPath(); g.moveTo(X,Y1); g.lineTo(X-6,Y1+s*11); g.lineTo(X+6,Y1+s*11); g.closePath(); g.fill();
  if(label){
    g.font="13px 'IBM Plex Mono',monospace"; g.textBaseline="middle";
    const right = X < m.R-70; g.textAlign = right?"left":"right";
    g.fillText(label, X+(right?10:-10), Y1+s*6);
  }
}
function drawSig(g,m,sc,sig,arg,pos,color,width,fill,flat,labelArrows){
  if(!flat){
    if(fill) fillUnder(g,m,sc,v=>sig.smooth(arg(v)),fill);
    trace(g,m,sc,v=>sig.smooth(arg(v)),color,width);
  }
  for(const im of sig.impulses) arrow(g,m,sc,pos(im.loc),im.area,color,labelArrows?"("+fmt(im.area)+")":"");
}

/* ===== where the product lives ==================================== */
function overlap(t){
  const hs=sigOf("h").smooth; let lo=Infinity, hi=-Infinity;
  for(let i=0;i<NT;i++){
    if(xArr[i]!==0 && hs(t-TAU[i])!==0){ if(TAU[i]<lo) lo=TAU[i]; if(TAU[i]>hi) hi=TAU[i]; }
  }
  return lo===Infinity ? null : [lo,hi];
}
function productImpulses(t){
  const X=sigOf("x"), H=sigOf("h"), out=[];
  for(const im of X.impulses){ const a=im.area*H.smooth(t-im.loc); if(Math.abs(a)>1e-9) out.push({loc:im.loc,area:a}); }
  for(const im of H.impulses){ const a=im.area*X.smooth(t-im.loc); if(Math.abs(a)>1e-9) out.push({loc:t-im.loc,area:a}); }
  return out;
}

/* ===== the three panels =========================================== */
const w0=()=>document.querySelector(".stack").clientWidth;
const tMark=()=>({v:tNow, label:"t = "+fmt(tNow)});

function drawA(){
  const {g,w,h}=setup(document.getElementById("cA"),Math.min(135,Math.max(110,w0()*0.11)));
  const m=mapper(w,h,scA);
  const X=sigOf("x"), H=sigOf("h");

  const ov=overlap(tNow);
  grid(g,m,scA,tMark());
  if(ov){                                     // band = limits of integration
    g.fillStyle="rgba(255,111,156,.13)";
    g.fillRect(m.X(ov[0]),m.T,Math.max(1.5,m.X(ov[1])-m.X(ov[0])),m.B-m.T);
    g.strokeStyle="rgba(255,111,156,.5)"; g.lineWidth=1; g.setLineDash([3,4]);
    [ov[0],ov[1]].forEach(v=>{ const x=Math.round(m.X(v))+.5; g.beginPath(); g.moveTo(x,m.T); g.lineTo(x,m.B); g.stroke(); });
    g.setLineDash([]);
  }

  drawSig(g,m,scA,X,v=>v,l=>l,"#45d0e8",2.6,"rgba(69,208,232,.14)",flatX,true);

  if(showGhost){
    g.save(); g.setLineDash([5,5]); g.globalAlpha=.5;
    drawSig(g,m,scA,H,v=>v,l=>l,"#ffc23d",1.8,null,flatH,false);
    g.restore();
    g.fillStyle="rgba(255,194,61,.7)"; g.font="13px 'IBM Plex Mono',monospace";
    g.textAlign="left"; g.textBaseline="top"; g.fillText("h(τ) before flip ┄",m.L+6,m.T+2);
  }
  drawSig(g,m,scA,H,v=>tNow-v,l=>tNow-l,"#ffc23d",2.6,null,flatH,true);
  axisLetter(g,m,"τ");
}

function drawB(){
  const {g,w,h}=setup(document.getElementById("cB"),Math.min(105,Math.max(90,w0()*0.085)));
  const m=mapper(w,h,scB); grid(g,m,scB,tMark());
  const xs=sigOf("x").smooth, hs=sigOf("h").smooth;
  if(!flatX&&!flatH){
    const prod=v=>xs(v)*hs(tNow-v);
    fillUnder(g,m,scB,prod,"rgba(255,111,156,.30)");
    trace(g,m,scB,prod,"#ff6f9c",2.4);
  }
  for(const im of productImpulses(tNow)) arrow(g,m,scB,im.loc,im.area,"#ff6f9c","area "+fmt(im.area));
  axisLetter(g,m,"τ");
}

function drawC(){
  const {g,w,h}=setup(document.getElementById("cC"),Math.min(125,Math.max(100,w0()*0.10)));
  const m=mapper(w,h,scC); grid(g,m,scC,tMark());

  g.strokeStyle="rgba(110,222,131,.26)"; g.lineWidth=1.8; g.beginPath();      // the destination, faint
  for(let k=0;k<NY;k++){ const X=m.X(TG[k]), Y=m.Y(YG[k]); k?g.lineTo(X,Y):g.moveTo(X,Y); }
  g.stroke();

  const kNow=Math.min(NY-1,Math.max(0,Math.round((tNow-T0)/TSTEP)));
  g.fillStyle="rgba(110,222,131,.16)"; g.beginPath(); g.moveTo(m.X(TG[0]),m.Y(0));
  for(let k=0;k<=kNow;k++) g.lineTo(m.X(TG[k]),m.Y(YG[k]));
  g.lineTo(m.X(TG[kNow]),m.Y(0)); g.closePath(); g.fill();

  g.strokeStyle="#6ede83"; g.lineWidth=2.8; g.lineJoin="round"; g.beginPath();
  for(let k=0;k<=kNow;k++){ const X=m.X(TG[k]), Y=m.Y(YG[k]); k?g.lineTo(X,Y):g.moveTo(X,Y); }
  g.stroke();

  for(const im of yImp){
    if(im.loc<=tNow) arrow(g,m,scC,im.loc,im.area,"#6ede83","("+fmt(im.area)+")");
    else { g.save(); g.globalAlpha=.3; arrow(g,m,scC,im.loc,im.area,"#6ede83",""); g.restore(); }
  }

  const X=m.X(tNow), Y=m.Y(YG[kNow]);
  g.fillStyle="#6ede83"; g.beginPath(); g.arc(X,Y,5.5,0,7); g.fill();
  g.strokeStyle="#0d1f2c"; g.lineWidth=2; g.stroke();
  axisLetter(g,m,"t");
}

function drawAll(){
  drawA(); drawB(); drawC();
  const ov=overlap(tNow), pts=productImpulses(tNow), y=yAt(tNow);
  document.getElementById("tOut").textContent=tNow.toFixed(2);
  let ovText="none", wText="0.00";
  if(ov){ ovText="["+ov[0].toFixed(2)+", "+ov[1].toFixed(2)+"]"; wText=(ov[1]-ov[0]).toFixed(2); }
  if(pts.length){
    const at="τ = "+pts.map(p=>p.loc.toFixed(2)).join(", ");
    ovText = ov ? ovText+" + "+at : at+" only";
    if(!ov) wText="0 (impulse)";
  }
  document.getElementById("rOv").textContent=ovText;
  document.getElementById("rW").textContent=wText;
  document.getElementById("rY").textContent=y.toFixed(3);
  document.getElementById("noteA").textContent = (ov||pts.length) ? "they overlap" : "no overlap → y = 0";
  document.getElementById("noteB").textContent = "area = "+y.toFixed(3);
  document.getElementById("noteC").textContent = "y("+tNow.toFixed(2)+") = "+y.toFixed(3);
}

/* ===== controls =================================================== */
const slide=document.getElementById("tSlide");
slide.addEventListener("input",e=>{ tNow=+e.target.value; stop(); drawAll(); });

const ids = w => ({ pick:w==="x"?"pickX":"pickH", box:w==="x"?"customX":"customH",
                    inp:w==="x"?"exprX":"exprH", err:w==="x"?"errX":"errH" });
function buildPicks(w){
  const cur=w==="x"?xKey:hKey, box=document.getElementById(ids(w).pick); box.innerHTML="";
  Object.entries(SIGNALS).forEach(([k,s])=>{
    const b=document.createElement("button");
    b.textContent=s.name; b.title=s.tex; b.setAttribute("aria-pressed",k===cur);
    b.onclick=()=>setKey(w,k); box.appendChild(b);
  });
  const c=document.createElement("button");
  c.textContent="Custom expression"; c.className="wide"; c.setAttribute("aria-pressed",cur==="custom");
  c.onclick=()=>setKey(w,"custom"); box.appendChild(c);
  document.getElementById(ids(w).box).hidden = cur!=="custom";
}
function setKey(w,k){
  if(w==="x") xKey=k; else hKey=k;
  buildPicks("x"); buildPicks("h"); rebuild();
  if(k==="custom") document.getElementById(ids(w).inp).focus();
}
function wireExpr(w){
  const inp=document.getElementById(ids(w).inp), err=document.getElementById(ids(w).err);
  inp.value=custom[w].expr; let tm=null;
  inp.addEventListener("input",()=>{
    clearTimeout(tm);
    tm=setTimeout(()=>{
      try{
        const sig=compile(inp.value); sig.name="Custom"; sig.tex=inp.value;
        custom[w].sig=sig; custom[w].expr=inp.value;
        err.textContent=""; inp.classList.remove("bad");
        if((w==="x"?xKey:hKey)==="custom") rebuild();
      }catch(e){ err.textContent=e.message; inp.classList.add("bad"); }
    },140);
  });
}
wireExpr("x"); wireExpr("h");
buildPicks("x"); buildPicks("h");

const ghostBtn=document.getElementById("ghost");
ghostBtn.onclick=()=>{ showGhost=!showGhost; ghostBtn.setAttribute("aria-pressed",showGhost); drawAll(); };
const speedBtn=document.getElementById("speed");
speedBtn.onclick=()=>{ speed=SPEEDS[(SPEEDS.indexOf(speed)+1)%SPEEDS.length]; speedBtn.textContent=speed+"×"; };

const PRESETS=[
  ["Pulse ⊛ Pulse → triangle","rect","rect"],
  ["Step ⊛ Decay → 1 − e⁻ᵗ","step","exp"],
  ["Pulse ⊛ Decay → RC charge, discharge","rect","exp"],
  ["Pulse ⊛ Impulse → unchanged","rect","imp"],
  ["Pulse ⊛ echo δ(t) + ½δ(t−2)","rect",{custom:"delta(t) + 0.5delta(t-2)"}],
  ["Quiz waveform ⊛ Decay",{custom:"2u(t+2) + r(t+1) - u(t-1) - 2r(t-2) + r(t-4)"},"exp"]
];
function applySpec(w,spec){
  if(typeof spec==="string"){ if(w==="x") xKey=spec; else hKey=spec; return; }
  custom[w].expr=spec.custom; custom[w].sig=compile(spec.custom);
  const inp=document.getElementById(ids(w).inp);
  inp.value=spec.custom; inp.classList.remove("bad");
  document.getElementById(ids(w).err).textContent="";
  if(w==="x") xKey="custom"; else hKey="custom";
}
const pbox=document.getElementById("presets");
PRESETS.forEach(([label,xs,hs])=>{
  const btn=document.createElement("button"); btn.textContent=label;
  btn.onclick=()=>{ applySpec("x",xs); applySpec("h",hs); buildPicks("x"); buildPicks("h");
                    tNow=T0; slide.value=T0; rebuild(); if(!reduceMotion) play(); };
  pbox.appendChild(btn);
});

/* ===== animation ================================================== */
const playBtn=document.getElementById("play"); let last=0;
function tick(ts){
  if(!playing) return;
  if(!last) last=ts;
  const dt=Math.min(0.05,(ts-last)/1000); last=ts;
  tNow+=dt*2.2*speed;
  if(tNow>T1){ tNow=T1; stop(); }
  slide.value=tNow; drawAll();
  if(playing) raf=requestAnimationFrame(tick);
}
function play(){
  if(tNow>=T1-0.01){ tNow=T0; slide.value=T0; }
  playing=true; last=0; playBtn.textContent="Pause"; raf=requestAnimationFrame(tick);
}
function stop(){ playing=false; playBtn.textContent="Play"; if(raf) cancelAnimationFrame(raf); raf=null; }
playBtn.onclick=()=> playing?stop():play();
document.getElementById("rew").onclick=()=>{ stop(); tNow=T0; slide.value=T0; drawAll(); };

addEventListener("keydown",e=>{
  const tg=e.target;
  if(tg.tagName==="INPUT"&&tg.type==="text") return;                       // typing an expression
  if(tg.tagName==="BUTTON"&&(e.key===" "||e.key==="Enter")) return;          // let buttons click
  const nudge=d=>{ stop(); tNow=Math.min(T1,Math.max(T0,tNow+d)); slide.value=tNow; drawAll(); };
  if(e.key===" "){ e.preventDefault(); playing?stop():play(); }
  else if(e.key==="ArrowRight"){ e.preventDefault(); nudge(e.shiftKey?0.5:0.1); }
  else if(e.key==="ArrowLeft"){ e.preventDefault(); nudge(e.shiftKey?-0.5:-0.1); }
  else if(e.key==="r"||e.key==="R"){ stop(); tNow=T0; slide.value=T0; drawAll(); }
});

let rt=null;
new ResizeObserver(()=>{ clearTimeout(rt); rt=setTimeout(drawAll,60); }).observe(document.querySelector(".stack"));

rebuild();
</script>
</body>
</html>
'''
