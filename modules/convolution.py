import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt
import time

C_X = "tab:blue"
C_H = "tab:orange"
C_RESULT = "tab:green"
C_AUX = "tab:purple"

LIVE_CONVOLUTION_HTML = '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Convolution — flip, slide, multiply, integrate</title>\n<style>\n:root{\n  --bg:#08131c;\n  --panel:#0d1f2c;\n  --panel-edge:#17364a;\n  --ink:#d3e3ee;\n  --ink-dim:#7593a8;\n  --ch-x:#45d0e8;\n  --ch-h:#ffc23d;\n  --ch-p:#ff6f9c;\n  --ch-y:#6ede83;\n  --sans:\'Barlow Semi Condensed\',ui-sans-serif,\'Helvetica Neue\',Arial,sans-serif;\n  --mono:\'IBM Plex Mono\',ui-monospace,Menlo,monospace;\n}\n*{box-sizing:border-box;margin:0;padding:0}\nhtml,body{height:100%}\nbody{\n  background:var(--bg);color:var(--ink);font-family:var(--sans);\n  font-size:17px;line-height:1.45;-webkit-font-smoothing:antialiased;\n}\n.wrap{\n  max-width:1500px;margin:0 auto;padding:22px 26px 40px;\n  display:grid;grid-template-columns:1fr 300px;gap:26px;align-items:start;\n}\nheader{grid-column:1/-1;display:flex;align-items:baseline;gap:20px;flex-wrap:wrap;\n  border-bottom:1px solid var(--panel-edge);padding-bottom:12px;margin-bottom:2px}\nh1{font-size:31px;font-weight:600;letter-spacing:.005em}\n.formula{font-family:var(--mono);font-size:16px;color:var(--ink-dim)}\n.formula b{color:var(--ch-y);font-weight:500}\nfooter{grid-column:1/-1;display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px 24px;\n  border-top:1px solid var(--panel-edge);padding-top:12px;margin-top:8px;\n  font-size:15px;color:var(--ink-dim);letter-spacing:.01em}\nfooter em{font-style:normal;color:#5a7488}\n\n/* ---- plot stack ---- */\n.stack{display:flex;flex-direction:column;gap:10px}\n.plot{background:var(--panel);border:1px solid var(--panel-edge);border-radius:3px;position:relative;overflow:hidden}\n.plot canvas{display:block;width:100%}\n.plot .cap{position:absolute;top:9px;left:14px;font-size:16px;font-weight:500;pointer-events:none;\n  text-shadow:0 0 8px var(--panel),0 0 8px var(--panel)}\n.plot .note{position:absolute;top:9px;right:14px;font-family:var(--mono);font-size:14px;color:var(--ink-dim);\n  pointer-events:none;text-align:right;text-shadow:0 0 8px var(--panel),0 0 8px var(--panel)}\n.k-x{color:var(--ch-x)} .k-h{color:var(--ch-h)} .k-p{color:var(--ch-p)} .k-y{color:var(--ch-y)}\n\n/* ---- transport ---- */\n.transport{margin-top:14px;background:var(--panel);border:1px solid var(--panel-edge);border-radius:3px;\n  padding:14px 18px 16px;display:grid;grid-template-columns:auto 1fr auto;gap:18px;align-items:center}\n.tval{font-family:var(--mono);font-size:26px;font-weight:500;color:var(--ch-h);min-width:118px}\n.tval span{font-size:15px;color:var(--ink-dim)}\ninput[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:26px;background:transparent;cursor:grab}\ninput[type=range]:active{cursor:grabbing}\ninput[type=range]::-webkit-slider-runnable-track{height:4px;background:var(--panel-edge);border-radius:2px}\ninput[type=range]::-moz-range-track{height:4px;background:var(--panel-edge);border-radius:2px}\ninput[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:20px;height:20px;border-radius:50%;\n  background:var(--ch-h);margin-top:-8px;border:3px solid var(--panel)}\ninput[type=range]::-moz-range-thumb{width:20px;height:20px;border-radius:50%;background:var(--ch-h);border:3px solid var(--panel)}\ninput[type=range]:focus-visible{outline:2px solid var(--ch-x);outline-offset:4px;border-radius:3px}\n.btnrow{display:flex;gap:8px}\nbutton{font-family:var(--sans);font-size:16px;color:var(--ink);background:#123044;border:1px solid var(--panel-edge);\n  border-radius:3px;padding:7px 15px;cursor:pointer;transition:background .12s}\nbutton:hover{background:#1a4460}\nbutton:focus-visible{outline:2px solid var(--ch-x);outline-offset:2px}\nbutton.go{background:var(--ch-y);border-color:var(--ch-y);color:#052611;font-weight:600;min-width:82px}\nbutton.go:hover{background:#84e79a}\n\n/* ---- side rail ---- */\n.rail{display:flex;flex-direction:column;gap:16px}\n.card{background:var(--panel);border:1px solid var(--panel-edge);border-radius:3px;padding:14px 15px 16px}\n.card h2{font-size:17px;font-weight:600;margin-bottom:9px}\n.card h2 i{font-style:normal;font-family:var(--mono);font-size:16px}\n.picks{display:grid;grid-template-columns:1fr 1fr;gap:6px}\n.picks button{padding:7px 4px;font-size:15px;width:100%}\n.picks button.wide{grid-column:1/-1}\n.card.hx h2 i{color:var(--ch-x)}\n.card.hh h2 i{color:var(--ch-h)}\n.hx .picks button[aria-pressed=true]{background:#0f4d5c;border-color:var(--ch-x);color:#fff}\n.hh .picks button[aria-pressed=true]{background:#5a4408;border-color:var(--ch-h);color:#fff}\n.toggle{width:100%;margin-top:8px;font-size:15px;padding:7px 10px}\n.toggle[aria-pressed=true]{background:#5a4408;border-color:var(--ch-h);color:#fff}\n\n.custom{margin-top:9px}\n.custom input{width:100%;font-family:var(--mono);font-size:15px;padding:8px 10px;background:var(--bg);\n  color:var(--ink);border:1px solid var(--panel-edge);border-radius:3px}\n.custom input:focus-visible{outline:2px solid var(--ch-x);outline-offset:1px}\n.hh .custom input:focus-visible{outline-color:var(--ch-h)}\n.custom input.bad{border-color:var(--ch-p)}\n.custom .err{color:#ff8fb1;font-size:14px;min-height:20px;margin-top:4px;line-height:1.4}\n.custom .help{color:var(--ink-dim);font-size:13.5px;line-height:1.5}\n.custom .help code{font-family:var(--mono);color:var(--ink);white-space:nowrap}\n\n.readout{font-family:var(--mono);font-size:15px;line-height:1.85}\n.readout div{display:flex;justify-content:space-between;gap:10px}\n.readout .lab{color:var(--ink-dim);flex-shrink:0}\n.readout span:last-child{text-align:right}\n.pairs{display:flex;flex-direction:column;gap:6px}\n.pairs button{text-align:left;font-size:15px;padding:7px 11px}\n.hint{font-size:15px;color:var(--ink-dim);line-height:1.5}\nkbd{font-family:var(--mono);font-size:13px;background:#123044;border:1px solid var(--panel-edge);border-radius:3px;padding:1px 5px}\n\n@media (max-width:1080px){\n  .wrap{grid-template-columns:1fr}\n  .rail{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}\n}\n@media (max-width:560px){\n  body{font-size:16px}\n  .wrap{padding:16px 14px 30px}\n  h1{font-size:25px}\n  .transport{grid-template-columns:1fr;gap:10px}\n  .tval{min-width:0}\n}\n\n/* EE-207 compact adaptation: same engine, simplified classroom layout */\nbody{background:#0e1117;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;font-size:14px;overflow:hidden}\n.wrap{max-width:none;width:100%;padding:4px 6px 6px;display:flex;flex-direction:column;gap:7px}\nheader,footer{display:none!important}\n.rail{order:1;display:grid!important;grid-template-columns:1fr 1fr;gap:8px}\n.stack{order:2;gap:6px}\n.rail .card{padding:8px 10px 9px;border-radius:7px}\n.rail .card:nth-child(n+3){display:none!important}\n.card h2{font-size:14px;margin-bottom:5px}.card h2 i{font-size:13px}\n.picks{grid-template-columns:repeat(4,1fr);gap:4px}.picks button{font-size:12px;padding:4px 3px}\n.picks button.wide,.custom,.toggle{display:none!important}\n.plot{border-radius:7px}.plot .cap{top:5px;left:9px;font-size:12px}.plot .note{top:5px;right:9px;font-size:11px}\n.transport{margin-top:2px;padding:7px 10px 8px;gap:10px;border-radius:7px;grid-template-columns:90px 1fr auto}\n.tval{font-size:18px;min-width:80px}.tval span{font-size:12px}.btnrow{gap:5px}\nbutton{font-size:12px;padding:5px 9px}button.go{min-width:62px}\n@media(max-width:800px){.rail{grid-template-columns:1fr}.picks{grid-template-columns:repeat(3,1fr)}}\n\n</style>\n</head>\n<body>\n<div class="wrap">\n\n<header>\n  <h1>Convolution, one slice at a time</h1>\n  <div class="formula"><b>y(t)</b> = &#8747; x(&tau;)&#183;h(t&minus;&tau;) d&tau;</div>\n</header>\n\n<main class="stack">\n  <div class="plot">\n    <canvas id="cA"></canvas>\n    <div class="cap"><span class="k-x">x(&tau;)</span> held still &nbsp;&#183;&nbsp; <span class="k-h">h(t&minus;&tau;)</span> flipped and slid</div>\n    <div class="note" id="noteA"></div>\n  </div>\n  <div class="plot">\n    <canvas id="cB"></canvas>\n    <div class="cap"><span class="k-p">x(&tau;)&#183;h(t&minus;&tau;)</span> — the shaded area is one output value</div>\n    <div class="note" id="noteB"></div>\n  </div>\n  <div class="plot">\n    <canvas id="cC"></canvas>\n    <div class="cap"><span class="k-y">y(t)</span> — that area, plotted against t</div>\n    <div class="note" id="noteC"></div>\n  </div>\n\n  <div class="transport">\n    <div class="tval"><span>t =</span> <b id="tOut">0.00</b></div>\n    <input id="tSlide" type="range" min="-4" max="8" step="0.02" value="0" aria-label="Slide h across x">\n    <div class="btnrow">\n      <button class="go" id="play">Play</button>\n      <button id="speed" title="Playback speed">1×</button>\n      <button id="rew">Reset</button>\n    </div>\n  </div>\n</main>\n\n<aside class="rail">\n  <div class="card hx">\n    <h2>Input <i>x(t)</i></h2>\n    <div class="picks" id="pickX"></div>\n    <div class="custom" id="customX" hidden>\n      <input id="exprX" type="text" spellcheck="false" autocomplete="off" aria-label="Expression for x(t)">\n      <div class="err" id="errX"></div>\n      <div class="help"><code>u(t)</code> step &nbsp; <code>r(t)</code> ramp &nbsp; <code>delta(t)</code> impulse<br>\n        also <code>exp sin cos pi e ^</code> &nbsp; shift with <code>(t-2)</code></div>\n    </div>\n  </div>\n  <div class="card hh">\n    <h2>Impulse response <i>h(t)</i></h2>\n    <div class="picks" id="pickH"></div>\n    <div class="custom" id="customH" hidden>\n      <input id="exprH" type="text" spellcheck="false" autocomplete="off" aria-label="Expression for h(t)">\n      <div class="err" id="errH"></div>\n      <div class="help"><code>u(t)</code> step &nbsp; <code>r(t)</code> ramp &nbsp; <code>delta(t)</code> impulse<br>\n        also <code>exp sin cos pi e ^</code> &nbsp; shift with <code>(t-2)</code></div>\n    </div>\n    <button class="toggle" id="ghost" aria-pressed="false">Show h(&tau;) before the flip</button>\n  </div>\n  <div class="card">\n    <h2>Live values</h2>\n    <div class="readout">\n      <div><span class="lab">overlap</span><span id="rOv">none</span></div>\n      <div><span class="lab">width</span><span id="rW">0.00</span></div>\n      <div><span class="lab">y(t)</span><span id="rY" style="color:var(--ch-y)">0.000</span></div>\n      <div><span class="lab">max y shown</span><span id="rPk">0.000</span></div>\n    </div>\n  </div>\n  <div class="card">\n    <h2>Worth showing</h2>\n    <div class="pairs" id="presets"></div>\n  </div>\n  <div class="card">\n    <h2>Keys</h2>\n    <p class="hint"><kbd>space</kbd> play or pause &nbsp; <kbd>&larr;</kbd><kbd>&rarr;</kbd> nudge t &nbsp; <kbd>R</kbd> reset</p>\n  </div>\n</aside>\n\n<footer>\n  <span>KFUPM &nbsp;&#183;&nbsp; EE207 &nbsp;&#183;&nbsp; Term 261</span>\n  <span>Dr. Motaz Alfarraj <em>(made with Claude)</em></span>\n</footer>\n\n</div>\n\n<script>\n"use strict";\n\n/* =====================================================================\n   Expression language:  u, r, delta  (+ exp sin cos abs sqrt sgn, pi, e, ^)\n   Impulse terms are extracted exactly so they can be drawn as arrows and\n   convolved analytically instead of as tall numeric spikes.\n   ===================================================================== */\nconst FUNCS = {\n  u:    v => v>=0 ? 1 : 0,\n  r:    v => v>0  ? v : 0,\n  exp:  Math.exp, sin: Math.sin, cos: Math.cos, abs: Math.abs,\n  sqrt: v => Math.sqrt(Math.max(0,v)),\n  sgn:  v => v>0 ? 1 : (v<0 ? -1 : 0)\n};\nconst DELTA_NAMES = new Set(["delta","d","δ","dirac","impulse"]);\nconst CONSTS = { pi:Math.PI, e:Math.E };\n\nfunction tokenize(src){\n  const toks=[]; let i=0;\n  while(i<src.length){\n    const c=src[i];\n    if(/\\s/.test(c)){ i++; continue; }\n    if(/[0-9.]/.test(c)){\n      const m=src.slice(i).match(/^(\\d+\\.?\\d*|\\.\\d+)([eE][+-]?\\d+)?/);\n      if(!m) throw new Error(`Bad number near "${src.slice(i,i+4)}"`);\n      toks.push({t:"num",v:parseFloat(m[0])}); i+=m[0].length; continue;\n    }\n    if(/[A-Za-zδ_]/.test(c)){\n      const m=src.slice(i).match(/^[A-Za-zδ_][A-Za-z0-9_]*/);\n      toks.push({t:"id",v:m[0]}); i+=m[0].length; continue;\n    }\n    if("+-*/^(),".includes(c)){ toks.push({t:c}); i++; continue; }\n    if(c==="·"||c==="×"){ toks.push({t:"*"}); i++; continue; }\n    if(c==="−"){ toks.push({t:"-"}); i++; continue; }\n    throw new Error(`Unexpected character "${c}"`);\n  }\n  return toks;\n}\n\nfunction parse(src){\n  const toks=tokenize(src); let p=0;\n  const peek=()=>toks[p], next=()=>toks[p++];\n  const show=k=> k ? (k.t==="num"?k.v:(k.v||k.t)) : "end of expression";\n  const expect=t=>{ const k=next(); if(!k||k.t!==t) throw new Error(`Expected "${t}" but found ${show(k)}`); };\n\n  function expr(){\n    let a=term();\n    while(peek()&&(peek().t==="+"||peek().t==="-")){ const op=next().t; a={type:"bin",op,a,b:term()}; }\n    return a;\n  }\n  function term(){\n    let a=factor();\n    for(;;){\n      const k=peek(); if(!k) break;\n      if(k.t==="*"||k.t==="/"){ next(); a={type:"bin",op:k.t,a,b:factor()}; }\n      else if(k.t==="num"||k.t==="id"||k.t==="("){ a={type:"bin",op:"*",a,b:factor()}; }   // 2u(t), u(t)u(2-t)\n      else break;\n    }\n    return a;\n  }\n  function factor(){\n    const k=peek();\n    if(k&&(k.t==="-"||k.t==="+")){ next(); const a=factor(); return k.t==="-"?{type:"neg",a}:a; }\n    return power();\n  }\n  function power(){\n    const a=atom();\n    if(peek()&&peek().t==="^"){ next(); return {type:"bin",op:"^",a,b:factor()}; }\n    return a;\n  }\n  function atom(){\n    const k=next();\n    if(!k) throw new Error("Expression ends too early");\n    if(k.t==="num") return {type:"num",v:k.v};\n    if(k.t==="("){ const a=expr(); expect(")"); return a; }\n    if(k.t==="id"){\n      const name=k.v;\n      if(name==="t") return {type:"t"};\n      if(name in CONSTS) return {type:"num",v:CONSTS[name]};\n      const isDelta=DELTA_NAMES.has(name), isFn=name in FUNCS;\n      if(!isDelta&&!isFn) throw new Error(`Unknown name "${name}" — try u, r, delta, exp, sin, cos`);\n      if(!peek()||peek().t!=="(") throw new Error(`"${name}" needs an argument, e.g. ${name}(t-1)`);\n      next(); const arg=expr(); expect(")");\n      return isDelta ? {type:"delta",arg} : {type:"call",fn:name,arg};\n    }\n    throw new Error(`Unexpected "${show(k)}"`);\n  }\n  const ast=expr();\n  if(p<toks.length) throw new Error(`Unexpected "${show(toks[p])}"`);\n  return ast;\n}\n\nfunction ev(n,t,dfn){\n  switch(n.type){\n    case "num":   return n.v;\n    case "t":     return t;\n    case "neg":   return -ev(n.a,t,dfn);\n    case "call":  return FUNCS[n.fn](ev(n.arg,t,dfn));\n    case "delta": return dfn(n,t);\n    case "bin": {\n      const a=ev(n.a,t,dfn), b=ev(n.b,t,dfn);\n      switch(n.op){\n        case "+": return a+b;  case "-": return a-b;  case "*": return a*b;\n        case "/": return b===0 ? 0 : a/b;\n        case "^": return Math.pow(a,b);\n      }\n    }\n  }\n  return 0;\n}\n\n// delta may only be scaled and summed — never inside a function, exponent, or denominator\nfunction checkDeltas(n,forbidden){\n  if(n.type==="delta"){\n    if(forbidden) throw new Error("delta(…) can be scaled and added, but not placed inside a function, exponent, or denominator");\n    checkDeltas(n.arg,true); return;\n  }\n  if(n.type==="call") return checkDeltas(n.arg,true);\n  if(n.type==="neg")  return checkDeltas(n.a,forbidden);\n  if(n.type==="bin"){\n    if(n.op==="^"){ checkDeltas(n.a,true); checkDeltas(n.b,true); return; }\n    checkDeltas(n.a,forbidden); checkDeltas(n.b,forbidden||n.op==="/");\n  }\n}\n\nfunction compile(src){\n  if(!src.trim()) throw new Error("Type an expression in t");\n  const ast=parse(src);\n  checkDeltas(ast,false);\n  const deltas=[];\n  (function walk(n){ if(n.type==="delta") deltas.push(n); for(const k of ["a","b","arg"]) if(n[k]) walk(n[k]); })(ast);\n\n  const off=()=>0;\n  const smooth=t=>{ const v=ev(ast,t,off); return Number.isFinite(v)?v:0; };\n\n  const found=[];\n  for(const d of deltas){\n    const g=v=>ev(d.arg,v,off);\n    const b=g(0), a=g(1)-b;\n    if(Math.abs(g(2)-(2*a+b))>1e-9) throw new Error("The argument of delta(…) must be linear in t, like delta(2t-1)");\n    if(Math.abs(a)<1e-12) throw new Error("delta(…) needs t in its argument, like delta(t-1)");\n    const loc=-b/a;\n    const only=node=> node===d ? 1 : 0;\n    const coeff=ev(ast,loc,only)-smooth(loc);          // whatever multiplies this impulse, sampled at its location\n    const area=coeff/Math.abs(a);                       // δ(at+b) = δ(t+b/a)/|a|\n    if(Math.abs(area)>1e-12) found.push({loc,area});\n  }\n  const impulses=[];                                    // merge impulses that land on the same spot\n  found.sort((p,q)=>p.loc-q.loc).forEach(im=>{\n    const last=impulses[impulses.length-1];\n    if(last && Math.abs(last.loc-im.loc)<1e-9) last.area+=im.area; else impulses.push({...im});\n  });\n  return {smooth, impulses:impulses.filter(im=>Math.abs(im.area)>1e-12)};\n}\n\n/* ===== built-in signals share the compiled shape ================== */\nconst SIGNALS = {\n  rect : {name:"Pulse",    smooth:t=>(t>=0&&t<1)?1:0,                    impulses:[], tex:"u(t) − u(t−1)"},\n  tri  : {name:"Triangle", smooth:t=>t>=0&&t<=1?t:(t>1&&t<=2?2-t:0),      impulses:[], tex:"r(t) − 2r(t−1) + r(t−2)"},\n  exp  : {name:"Decay",    smooth:t=>t>=0?Math.exp(-t):0,                 impulses:[], tex:"e^(−t) u(t)"},\n  step : {name:"Step",     smooth:t=>t>=0?1:0,                            impulses:[], tex:"u(t)"},\n  ramp : {name:"Ramp",     smooth:t=>(t>=0&&t<=2)?t/2:0,                  impulses:[], tex:"½ r(t), cut off at t = 2"},\n  imp  : {name:"Impulse",  smooth:()=>0, impulses:[{loc:0,area:1}],        tex:"δ(t)"}\n};\nconst custom = {\n  x:{ expr:"2u(t+2) + r(t+1) - u(t-1) - 2r(t-2) + r(t-4)", sig:null },\n  h:{ expr:"delta(t) + 0.5delta(t-2)", sig:null }\n};\nfor(const w of ["x","h"]) custom[w].sig = compile(custom[w].expr);\n\nlet xKey="rect", hKey="rect", tNow=-4, playing=false, raf=null;\nlet showGhost=false, speed=1;\nconst SPEEDS=[0.5,1,2];\nconst reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;\nconst sigOf = w => (w==="x"?xKey:hKey)==="custom" ? custom[w].sig : SIGNALS[w==="x"?xKey:hKey];\n\n/* ===== numerical grids ============================================ */\nconst TAU0=-8, TAU1=14, DT=0.005;\nconst NT = Math.round((TAU1-TAU0)/DT);\nconst TAU = new Float64Array(NT);\nfor(let i=0;i<NT;i++) TAU[i]=TAU0+(i+0.5)*DT;          // midpoint rule: exact on pulse edges\n\nconst T0=-4, T1=8, TSTEP=0.02;\nconst NY = Math.round((T1-T0)/TSTEP)+1;\nconst TG = new Float64Array(NY), YG = new Float64Array(NY);\nconst VIEW0=-4, VIEW1=8;\n\n// h(t_k − τ_i) always lands on one fixed lattice, so sample h once and index into it\nconst R = Math.round(TSTEP/DT), OFF = NT-1, HG_LEN = R*(NY-1)+NT;\nconst BASE = (T0-TAU0) - 0.5*DT;\nconst xArr = new Float64Array(NT), hG = new Float64Array(HG_LEN);\n\nlet scA, scB, scC, yImp=[], yPeak=1, flatX=false, flatH=false;\n\nfunction niceTop(v){\n  for(const c of [0.5,1,1.5,2,3,4,5,6,8,10,15,20,30,50,100]) if(c>=v*0.999) return c;\n  return Math.ceil(v);\n}\nfunction scaleFor(lo,hi){\n  let top = hi> 1e-9 ?  niceTop(hi)  : 0;\n  let bot = lo<-1e-9 ? -niceTop(-lo) : 0;\n  if(top===0&&bot===0) top=1;\n  const span=top-bot;\n  const ticks=[0]; if(top>0) ticks.push(top/2,top); if(bot<0) ticks.push(bot/2,bot);\n  return {vmin:bot-0.12*span, vmax:top+0.18*span, ticks, top, bot};\n}\n\nfunction rebuild(){\n  const X=sigOf("x"), H=sigOf("h"), xs=X.smooth, hs=H.smooth;\n  let xmin=0,xmax=0,hmin=0,hmax=0;\n  for(let i=0;i<NT;i++){ const v=xs(TAU[i]); xArr[i]=v; if(v<xmin)xmin=v; if(v>xmax)xmax=v; }\n  for(let j=0;j<HG_LEN;j++){ const v=hs(BASE+DT*(j-OFF)); hG[j]=v; if(v<hmin)hmin=v; if(v>hmax)hmax=v; }\n  flatX = xmin===0&&xmax===0; flatH = hmin===0&&hmax===0;\n\n  let pmin=0,pmax=0;\n  for(let k=0;k<NY;k++){\n    const t=T0+k*TSTEP; TG[k]=t;\n    let s=0; const b=R*k+OFF;\n    for(let i=0;i<NT;i++){\n      const xv=xArr[i];\n      if(xv!==0){ const p=xv*hG[b-i]; s+=p; if(p<pmin)pmin=p; if(p>pmax)pmax=p; }\n    }\n    s*=DT;\n    for(const im of X.impulses) s+=im.area*hs(t-im.loc);     // δ in x samples h\n    for(const im of H.impulses) s+=im.area*xs(t-im.loc);     // δ in h samples x\n    YG[k]=s;\n  }\n  const pairs=[];                                              // δ ⊛ δ → δ in y\n  for(const a of X.impulses) for(const b of H.impulses) pairs.push({loc:a.loc+b.loc, area:a.area*b.area});\n  yImp=[]; pairs.sort((p,q)=>p.loc-q.loc).forEach(im=>{\n    const last=yImp[yImp.length-1];\n    if(last&&Math.abs(last.loc-im.loc)<1e-9) last.area+=im.area; else yImp.push({...im});\n  });\n\n  // vertical scales are fixed for the whole sweep so frames stay comparable\n  let aLo=Math.min(xmin,hmin), aHi=Math.max(xmax,hmax);\n  for(const im of [...X.impulses,...H.impulses]){ aLo=Math.min(aLo,im.area); aHi=Math.max(aHi,im.area); }\n  scA=scaleFor(aLo,aHi);\n\n  for(const im of X.impulses){ pmin=Math.min(pmin,im.area*hmin,im.area*hmax); pmax=Math.max(pmax,im.area*hmin,im.area*hmax); }\n  for(const im of H.impulses){ pmin=Math.min(pmin,im.area*xmin,im.area*xmax); pmax=Math.max(pmax,im.area*xmin,im.area*xmax); }\n  scB=scaleFor(pmin,pmax);\n\n  let ymin=0,ymax=0;\n  for(let k=0;k<NY;k++){ if(YG[k]<ymin)ymin=YG[k]; if(YG[k]>ymax)ymax=YG[k]; }\n  for(const im of yImp){ ymin=Math.min(ymin,im.area); ymax=Math.max(ymax,im.area); }\n  scC=scaleFor(ymin,ymax);\n  yPeak=Math.max(-ymin,ymax);\n  document.getElementById("rPk").textContent=yPeak.toFixed(3);\n  drawAll();\n}\nconst yAt = t => YG[Math.min(NY-1,Math.max(0,Math.round((t-T0)/TSTEP)))];\n\n/* ===== canvas plumbing ============================================ */\nfunction setup(cv,h){\n  const dpr=window.devicePixelRatio||1, w=cv.parentNode.clientWidth;\n  cv.width=w*dpr; cv.height=h*dpr; cv.style.height=h+"px";\n  const g=cv.getContext("2d"); g.setTransform(dpr,0,0,dpr,0,0); g.clearRect(0,0,w,h);\n  return {g,w,h};\n}\nconst PAD={l:48,r:38,t:34,b:24};\nfunction mapper(w,h,sc){\n  const L=PAD.l, R=w-PAD.r, T=PAD.t, B=h-PAD.b;\n  return { X:v=>L+(v-VIEW0)/(VIEW1-VIEW0)*(R-L), Y:v=>B-(v-sc.vmin)/(sc.vmax-sc.vmin)*(B-T), L,R,T,B };\n}\nconst fmt = v => { const s=v.toFixed(2); return s.replace(/\\.?0+$/,"").replace(/^-0$/,"0"); };\nfunction axisLetter(g,m,ch){\n  g.fillStyle="#7593a8"; g.font="italic 14px \'IBM Plex Mono\',monospace";\n  g.textAlign="left"; g.textBaseline="top"; g.fillText(ch,m.R+16,m.B+4);\n}\nfunction grid(g,m,sc,mark){\n  g.lineWidth=1;\n  for(let v=Math.ceil(VIEW0);v<=VIEW1;v++){\n    const x=Math.round(m.X(v))+.5;\n    g.strokeStyle = v===0 ? "rgba(122,164,190,.34)" : "rgba(122,164,190,.10)";\n    g.beginPath(); g.moveTo(x,m.T); g.lineTo(x,m.B); g.stroke();\n  }\n  g.strokeStyle="rgba(122,164,190,.10)";\n  sc.ticks.forEach(v=>{ const y=Math.round(m.Y(v))+.5; g.beginPath(); g.moveTo(m.L,y); g.lineTo(m.R,y); g.stroke(); });\n  const y0=Math.round(m.Y(0))+.5;\n  g.strokeStyle="rgba(122,164,190,.45)"; g.beginPath(); g.moveTo(m.L,y0); g.lineTo(m.R,y0); g.stroke();\n\n  // the moving "t" marker on the horizontal axis\n  let markX=null, markHalf=0, markText="";\n  if(mark && mark.v>=VIEW0 && mark.v<=VIEW1){\n    markX=m.X(mark.v); markText=mark.label;\n    g.font="600 13px \'IBM Plex Mono\',monospace";\n    markHalf=g.measureText(markText).width/2;\n  }\n\n  g.fillStyle="#7593a8"; g.font="13px \'IBM Plex Mono\',monospace";\n  g.textAlign="center"; g.textBaseline="top";\n  for(let v=Math.ceil(VIEW0);v<=VIEW1;v+=2){\n    if(v===0) continue;\n    if(markX!==null && Math.abs(m.X(v)-markX) < markHalf+14) continue;   // yield to the t marker\n    g.fillText(String(v),m.X(v),m.B+5);\n  }\n  g.textAlign="right"; g.textBaseline="middle";\n  sc.ticks.forEach(v=>{ if(v!==0) g.fillText(fmt(v),m.L-7,m.Y(v)); });\n\n  if(markX!==null){\n    const X=Math.round(markX)+.5;\n    g.strokeStyle="rgba(255,194,61,.42)"; g.lineWidth=1; g.setLineDash([2,5]);\n    g.beginPath(); g.moveTo(X,m.T); g.lineTo(X,m.B); g.stroke(); g.setLineDash([]);\n    g.fillStyle="#ffc23d";\n    g.beginPath(); g.moveTo(markX,m.B+1); g.lineTo(markX-5,m.B+8); g.lineTo(markX+5,m.B+8); g.closePath(); g.fill();\n    g.font="600 13px \'IBM Plex Mono\',monospace"; g.textAlign="center"; g.textBaseline="top";\n    const tx=Math.min(m.R-markHalf, Math.max(m.L+markHalf, markX));            // keep the text inside the panel\n    g.fillText(markText,tx,m.B+9);\n  }\n}\nfunction trace(g,m,sc,fn,color,width){\n  g.strokeStyle=color; g.lineWidth=width; g.lineJoin="round"; g.lineCap="round"; g.beginPath();\n  const px=Math.max(1,Math.round(m.R-m.L));\n  for(let i=0;i<=px;i++){\n    const v=Math.max(sc.vmin,Math.min(sc.vmax,fn(VIEW0+(i/px)*(VIEW1-VIEW0))));\n    i?g.lineTo(m.L+i,m.Y(v)):g.moveTo(m.L+i,m.Y(v));\n  }\n  g.stroke();\n}\nfunction fillUnder(g,m,sc,fn,color){\n  g.fillStyle=color; g.beginPath(); g.moveTo(m.L,m.Y(0));\n  const px=Math.max(1,Math.round(m.R-m.L));\n  for(let i=0;i<=px;i++){\n    const v=Math.max(sc.vmin,Math.min(sc.vmax,fn(VIEW0+(i/px)*(VIEW1-VIEW0))));\n    g.lineTo(m.L+i,m.Y(v));\n  }\n  g.lineTo(m.R,m.Y(0)); g.closePath(); g.fill();\n}\n// arrow length in data units: the true area, clamped to stay inside the panel and stay visible\nfunction arrowLen(area,sc){\n  const cap = area>=0 ? sc.vmax*0.94 : -sc.vmin*0.94;\n  const mag = Math.max(0.12*(sc.top-sc.bot), Math.min(Math.abs(area),cap));\n  return (area<0?-1:1)*mag;\n}\nfunction arrow(g,m,sc,xv,area,color,label){\n  if(xv<VIEW0||xv>VIEW1) return;\n  const X=m.X(xv), Y0=m.Y(0), Y1=m.Y(arrowLen(area,sc)), s=Y1<Y0?1:-1;\n  g.strokeStyle=color; g.fillStyle=color; g.lineWidth=2.5;\n  g.beginPath(); g.moveTo(X,Y0); g.lineTo(X,Y1+s*9); g.stroke();\n  g.beginPath(); g.moveTo(X,Y1); g.lineTo(X-6,Y1+s*11); g.lineTo(X+6,Y1+s*11); g.closePath(); g.fill();\n  if(label){\n    g.font="13px \'IBM Plex Mono\',monospace"; g.textBaseline="middle";\n    const right = X < m.R-70; g.textAlign = right?"left":"right";\n    g.fillText(label, X+(right?10:-10), Y1+s*6);\n  }\n}\nfunction drawSig(g,m,sc,sig,arg,pos,color,width,fill,flat,labelArrows){\n  if(!flat){\n    if(fill) fillUnder(g,m,sc,v=>sig.smooth(arg(v)),fill);\n    trace(g,m,sc,v=>sig.smooth(arg(v)),color,width);\n  }\n  for(const im of sig.impulses) arrow(g,m,sc,pos(im.loc),im.area,color,labelArrows?"("+fmt(im.area)+")":"");\n}\n\n/* ===== where the product lives ==================================== */\nfunction overlap(t){\n  const hs=sigOf("h").smooth; let lo=Infinity, hi=-Infinity;\n  for(let i=0;i<NT;i++){\n    if(xArr[i]!==0 && hs(t-TAU[i])!==0){ if(TAU[i]<lo) lo=TAU[i]; if(TAU[i]>hi) hi=TAU[i]; }\n  }\n  return lo===Infinity ? null : [lo,hi];\n}\nfunction productImpulses(t){\n  const X=sigOf("x"), H=sigOf("h"), out=[];\n  for(const im of X.impulses){ const a=im.area*H.smooth(t-im.loc); if(Math.abs(a)>1e-9) out.push({loc:im.loc,area:a}); }\n  for(const im of H.impulses){ const a=im.area*X.smooth(t-im.loc); if(Math.abs(a)>1e-9) out.push({loc:t-im.loc,area:a}); }\n  return out;\n}\n\n/* ===== the three panels =========================================== */\nconst w0=()=>document.querySelector(".stack").clientWidth;\nconst tMark=()=>({v:tNow, label:"t = "+fmt(tNow)});\n\nfunction drawA(){\n  const {g,w,h}=setup(document.getElementById("cA"),132);\n  const m=mapper(w,h,scA);\n  const X=sigOf("x"), H=sigOf("h");\n\n  const ov=overlap(tNow);\n  grid(g,m,scA,tMark());\n  if(ov){                                     // band = limits of integration\n    g.fillStyle="rgba(255,111,156,.13)";\n    g.fillRect(m.X(ov[0]),m.T,Math.max(1.5,m.X(ov[1])-m.X(ov[0])),m.B-m.T);\n    g.strokeStyle="rgba(255,111,156,.5)"; g.lineWidth=1; g.setLineDash([3,4]);\n    [ov[0],ov[1]].forEach(v=>{ const x=Math.round(m.X(v))+.5; g.beginPath(); g.moveTo(x,m.T); g.lineTo(x,m.B); g.stroke(); });\n    g.setLineDash([]);\n  }\n\n  drawSig(g,m,scA,X,v=>v,l=>l,"#45d0e8",2.6,"rgba(69,208,232,.14)",flatX,true);\n\n  if(showGhost){\n    g.save(); g.setLineDash([5,5]); g.globalAlpha=.5;\n    drawSig(g,m,scA,H,v=>v,l=>l,"#ffc23d",1.8,null,flatH,false);\n    g.restore();\n    g.fillStyle="rgba(255,194,61,.7)"; g.font="13px \'IBM Plex Mono\',monospace";\n    g.textAlign="left"; g.textBaseline="top"; g.fillText("h(τ) before flip ┄",m.L+6,m.T+2);\n  }\n  drawSig(g,m,scA,H,v=>tNow-v,l=>tNow-l,"#ffc23d",2.6,null,flatH,true);\n  axisLetter(g,m,"τ");\n}\n\nfunction drawB(){\n  const {g,w,h}=setup(document.getElementById("cB"),104);\n  const m=mapper(w,h,scB); grid(g,m,scB,tMark());\n  const xs=sigOf("x").smooth, hs=sigOf("h").smooth;\n  if(!flatX&&!flatH){\n    const prod=v=>xs(v)*hs(tNow-v);\n    fillUnder(g,m,scB,prod,"rgba(255,111,156,.30)");\n    trace(g,m,scB,prod,"#ff6f9c",2.4);\n  }\n  for(const im of productImpulses(tNow)) arrow(g,m,scB,im.loc,im.area,"#ff6f9c","area "+fmt(im.area));\n  axisLetter(g,m,"τ");\n}\n\nfunction drawC(){\n  const {g,w,h}=setup(document.getElementById("cC"),122);\n  const m=mapper(w,h,scC); grid(g,m,scC,tMark());\n\n  g.strokeStyle="rgba(110,222,131,.26)"; g.lineWidth=1.8; g.beginPath();      // the destination, faint\n  for(let k=0;k<NY;k++){ const X=m.X(TG[k]), Y=m.Y(YG[k]); k?g.lineTo(X,Y):g.moveTo(X,Y); }\n  g.stroke();\n\n  const kNow=Math.min(NY-1,Math.max(0,Math.round((tNow-T0)/TSTEP)));\n  g.fillStyle="rgba(110,222,131,.16)"; g.beginPath(); g.moveTo(m.X(TG[0]),m.Y(0));\n  for(let k=0;k<=kNow;k++) g.lineTo(m.X(TG[k]),m.Y(YG[k]));\n  g.lineTo(m.X(TG[kNow]),m.Y(0)); g.closePath(); g.fill();\n\n  g.strokeStyle="#6ede83"; g.lineWidth=2.8; g.lineJoin="round"; g.beginPath();\n  for(let k=0;k<=kNow;k++){ const X=m.X(TG[k]), Y=m.Y(YG[k]); k?g.lineTo(X,Y):g.moveTo(X,Y); }\n  g.stroke();\n\n  for(const im of yImp){\n    if(im.loc<=tNow) arrow(g,m,scC,im.loc,im.area,"#6ede83","("+fmt(im.area)+")");\n    else { g.save(); g.globalAlpha=.3; arrow(g,m,scC,im.loc,im.area,"#6ede83",""); g.restore(); }\n  }\n\n  const X=m.X(tNow), Y=m.Y(YG[kNow]);\n  g.fillStyle="#6ede83"; g.beginPath(); g.arc(X,Y,5.5,0,7); g.fill();\n  g.strokeStyle="#0d1f2c"; g.lineWidth=2; g.stroke();\n  axisLetter(g,m,"t");\n}\n\nfunction drawAll(){\n  drawA(); drawB(); drawC();\n  const ov=overlap(tNow), pts=productImpulses(tNow), y=yAt(tNow);\n  document.getElementById("tOut").textContent=tNow.toFixed(2);\n  let ovText="none", wText="0.00";\n  if(ov){ ovText="["+ov[0].toFixed(2)+", "+ov[1].toFixed(2)+"]"; wText=(ov[1]-ov[0]).toFixed(2); }\n  if(pts.length){\n    const at="τ = "+pts.map(p=>p.loc.toFixed(2)).join(", ");\n    ovText = ov ? ovText+" + "+at : at+" only";\n    if(!ov) wText="0 (impulse)";\n  }\n  document.getElementById("rOv").textContent=ovText;\n  document.getElementById("rW").textContent=wText;\n  document.getElementById("rY").textContent=y.toFixed(3);\n  document.getElementById("noteA").textContent = (ov||pts.length) ? "they overlap" : "no overlap → y = 0";\n  document.getElementById("noteB").textContent = "area = "+y.toFixed(3);\n  document.getElementById("noteC").textContent = "y("+tNow.toFixed(2)+") = "+y.toFixed(3);\n}\n\n/* ===== controls =================================================== */\nconst slide=document.getElementById("tSlide");\nslide.addEventListener("input",e=>{ tNow=+e.target.value; stop(); drawAll(); });\n\nconst ids = w => ({ pick:w==="x"?"pickX":"pickH", box:w==="x"?"customX":"customH",\n                    inp:w==="x"?"exprX":"exprH", err:w==="x"?"errX":"errH" });\nfunction buildPicks(w){\n  const cur=w==="x"?xKey:hKey, box=document.getElementById(ids(w).pick); box.innerHTML="";\n  Object.entries(SIGNALS).forEach(([k,s])=>{\n    const b=document.createElement("button");\n    b.textContent=s.name; b.title=s.tex; b.setAttribute("aria-pressed",k===cur);\n    b.onclick=()=>setKey(w,k); box.appendChild(b);\n  });\n  const c=document.createElement("button");\n  c.textContent="Custom expression"; c.className="wide"; c.setAttribute("aria-pressed",cur==="custom");\n  c.onclick=()=>setKey(w,"custom"); box.appendChild(c);\n  document.getElementById(ids(w).box).hidden = cur!=="custom";\n}\nfunction setKey(w,k){\n  if(w==="x") xKey=k; else hKey=k;\n  buildPicks("x"); buildPicks("h"); rebuild();\n  if(k==="custom") document.getElementById(ids(w).inp).focus();\n}\nfunction wireExpr(w){\n  const inp=document.getElementById(ids(w).inp), err=document.getElementById(ids(w).err);\n  inp.value=custom[w].expr; let tm=null;\n  inp.addEventListener("input",()=>{\n    clearTimeout(tm);\n    tm=setTimeout(()=>{\n      try{\n        const sig=compile(inp.value); sig.name="Custom"; sig.tex=inp.value;\n        custom[w].sig=sig; custom[w].expr=inp.value;\n        err.textContent=""; inp.classList.remove("bad");\n        if((w==="x"?xKey:hKey)==="custom") rebuild();\n      }catch(e){ err.textContent=e.message; inp.classList.add("bad"); }\n    },140);\n  });\n}\nwireExpr("x"); wireExpr("h");\nbuildPicks("x"); buildPicks("h");\n// EE-207: compact controls above the synchronized plots.\nconst eeRail=document.querySelector(".rail"), eeStack=document.querySelector(".stack");\nif(eeRail&&eeStack) eeStack.parentNode.insertBefore(eeRail,eeStack);\n\nconst ghostBtn=document.getElementById("ghost");\nghostBtn.onclick=()=>{ showGhost=!showGhost; ghostBtn.setAttribute("aria-pressed",showGhost); drawAll(); };\nconst speedBtn=document.getElementById("speed");\nspeedBtn.onclick=()=>{ speed=SPEEDS[(SPEEDS.indexOf(speed)+1)%SPEEDS.length]; speedBtn.textContent=speed+"×"; };\n\nconst PRESETS=[\n  ["Pulse ⊛ Pulse → triangle","rect","rect"],\n  ["Step ⊛ Decay → 1 − e⁻ᵗ","step","exp"],\n  ["Pulse ⊛ Decay → RC charge, discharge","rect","exp"],\n  ["Pulse ⊛ Impulse → unchanged","rect","imp"],\n  ["Pulse ⊛ echo δ(t) + ½δ(t−2)","rect",{custom:"delta(t) + 0.5delta(t-2)"}],\n  ["Quiz waveform ⊛ Decay",{custom:"2u(t+2) + r(t+1) - u(t-1) - 2r(t-2) + r(t-4)"},"exp"]\n];\nfunction applySpec(w,spec){\n  if(typeof spec==="string"){ if(w==="x") xKey=spec; else hKey=spec; return; }\n  custom[w].expr=spec.custom; custom[w].sig=compile(spec.custom);\n  const inp=document.getElementById(ids(w).inp);\n  inp.value=spec.custom; inp.classList.remove("bad");\n  document.getElementById(ids(w).err).textContent="";\n  if(w==="x") xKey="custom"; else hKey="custom";\n}\nconst pbox=document.getElementById("presets");\nPRESETS.forEach(([label,xs,hs])=>{\n  const btn=document.createElement("button"); btn.textContent=label;\n  btn.onclick=()=>{ applySpec("x",xs); applySpec("h",hs); buildPicks("x"); buildPicks("h");\n                    tNow=T0; slide.value=T0; rebuild(); if(!reduceMotion) play(); };\n  pbox.appendChild(btn);\n});\n\n/* ===== animation ================================================== */\nconst playBtn=document.getElementById("play"); let last=0;\nfunction tick(ts){\n  if(!playing) return;\n  if(!last) last=ts;\n  const dt=Math.min(0.05,(ts-last)/1000); last=ts;\n  tNow+=dt*2.2*speed;\n  if(tNow>T1){ tNow=T1; stop(); }\n  slide.value=tNow; drawAll();\n  if(playing) raf=requestAnimationFrame(tick);\n}\nfunction play(){\n  if(tNow>=T1-0.01){ tNow=T0; slide.value=T0; }\n  playing=true; last=0; playBtn.textContent="Pause"; raf=requestAnimationFrame(tick);\n}\nfunction stop(){ playing=false; playBtn.textContent="Play"; if(raf) cancelAnimationFrame(raf); raf=null; }\nplayBtn.onclick=()=> playing?stop():play();\ndocument.getElementById("rew").onclick=()=>{ stop(); tNow=T0; slide.value=T0; drawAll(); };\n\naddEventListener("keydown",e=>{\n  const tg=e.target;\n  if(tg.tagName==="INPUT"&&tg.type==="text") return;                       // typing an expression\n  if(tg.tagName==="BUTTON"&&(e.key===" "||e.key==="Enter")) return;          // let buttons click\n  const nudge=d=>{ stop(); tNow=Math.min(T1,Math.max(T0,tNow+d)); slide.value=tNow; drawAll(); };\n  if(e.key===" "){ e.preventDefault(); playing?stop():play(); }\n  else if(e.key==="ArrowRight"){ e.preventDefault(); nudge(e.shiftKey?0.5:0.1); }\n  else if(e.key==="ArrowLeft"){ e.preventDefault(); nudge(e.shiftKey?-0.5:-0.1); }\n  else if(e.key==="r"||e.key==="R"){ stop(); tNow=T0; slide.value=T0; drawAll(); }\n});\n\nlet rt=null;\nnew ResizeObserver(()=>{ clearTimeout(rt); rt=setTimeout(drawAll,60); }).observe(document.querySelector(".stack"));\n\nrebuild();\n</script>\n</body>\n</html>\n'

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
    ax.set_title(title,fontsize=9,fontweight="bold")
    ax.set_xlabel(xlabel,fontsize=8); ax.set_ylabel("Amplitude",fontsize=8)
    ax.tick_params(labelsize=7); ax.grid(True,alpha=.28); ax.set_xlim(-6,6)

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
    fig,ax=plt.subplots(figsize=(4.2,1.75))
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
        st.markdown("## Worked example — graphical convolution")
        st.write("We use two simple causal rectangular pulses so each operation can be followed clearly.")
        c1,c2=st.columns(2)
        with c1:
            st.latex(r"x(t)=u(t)-u(t-2)")
            st.write("x(t)=1 for 0≤t≤2")
        with c2:
            st.latex(r"h(t)=u(t)-u(t-3)")
            st.write("h(t)=1 for 0≤t≤3")

        xex=rect_causal(TAU,2.0)
        hex_=rect_causal(TAU,3.0)
        tex=2.0
        hflip=rect_causal(-TAU,3.0)
        hshift=rect_causal(tex-TAU,3.0)
        prod=xex*hshift
        area=float(np.trapezoid(prod,TAU))

        r1,r2=st.columns(2,gap="large")
        with r1:
            st.markdown("#### Step 1 — Flip")
            st.latex(r"h(\tau)\rightarrow h(-\tau)")
            step_plot([(hex_,r"$h(\tau)$",C_H,"--",1.5),(hflip,r"$h(-\tau)$",C_H,"-",2.3)],"Flip h(τ)")
        with r2:
            st.markdown("#### Step 2 — Shift")
            st.latex(r"h(-\tau)\rightarrow h(2-\tau)")
            step_plot([(hflip,r"$h(-\tau)$",C_H,"--",1.5),(hshift,r"$h(2-\tau)$",C_H,"-",2.3)],"Shift to t = 2")

        r3,r4=st.columns(2,gap="large")
        with r3:
            st.markdown("#### Step 3 — Overlay")
            st.latex(r"x(\tau)\quad\text{with}\quad h(2-\tau)")
            step_plot([(xex,r"$x(\tau)$",C_X,"-",2.3),(hshift,r"$h(2-\tau)$",C_H,"-",2.3)],"Overlap at t = 2")
        with r4:
            st.markdown("#### Step 4 — Multiply")
            st.latex(r"x(\tau)h(2-\tau)")
            step_plot([(prod,r"$x(\tau)h(2-\tau)$",C_RESULT,"-",2.5)],"Product")

        st.markdown("#### Step 5 — Integrate")
        st.latex(r"y(2)=\int_{-\infty}^{\infty}x(\tau)h(2-\tau)\,d\tau")
        st.latex(rf"\boxed{{y(2)={area:.2f}}}")
        st.success("At t = 2, the two unit-height pulses overlap over a width of 2, so y(2)=2.")

    with live:
        st.header("Live Convolution Lab")
        st.write("This is the real-time convolution engine adapted to the EE-207 layout. Choose x(t) and h(t), then press Play and watch all three synchronized plots change together.")
        st.latex(r"y(t)=\int_{-\infty}^{\infty}x(\tau)h(t-\tau)\,d\tau")
        components.html(LIVE_CONVOLUTION_HTML, height=650, scrolling=False)

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
