/* EE-207 — Convolution chapter. Client-side only. */
window.Convolution=(()=>{
 const tabs=[['concept','Concept'],['live','Live Convolution Lab'],['step','Step-by-Step'],['properties','Properties'],['exam','Test']];
 const C={blue:'#4c8dff',cyan:'#4ed7cf',red:'#ff5a5f',gold:'#f0c95a',purple:'#b38cff',green:'#58d68d',orange:'#ff9f43'};
 const state={tab:'concept',playing:false,raf:null,t:-6,speed:1,last:0,exam:null};
 const dt=.025, grid=Array.from({length:481},(_,i)=>-6+i*dt);
 const sigs={
  rect:{label:'Causal rectangular pulse',tex:'u(t)-u(t-2)',fn:t=>(t>=0&&t<=2?1:0)},
  wide:{label:'Wide rectangular pulse',tex:'u(t+2)-u(t-2)',fn:t=>(t>=-2&&t<=2?1:0)},
  step:{label:'Unit step',tex:'u(t)',fn:t=>t>=0?1:0},
  decay:{label:'Causal exponential',tex:'e^{-t}u(t)',fn:t=>t>=0?Math.exp(-t):0},
  tri:{label:'Triangular pulse',tex:'\\operatorname{tri}(t)',fn:t=>Math.max(0,1-Math.abs(t))},
  sin:{label:'Windowed sine',tex:'\\sin(t)[u(t+\\pi)-u(t-\\pi)]',fn:t=>Math.abs(t)<=Math.PI?Math.sin(t):0},
  gauss:{label:'Gaussian',tex:'e^{-t^2}',fn:t=>Math.exp(-t*t)}
 };
 const examples=[
  ['Pulse ∗ Pulse → triangle','rect','rect'],
  ['Step ∗ Decay → 1 − e⁻ᵗ','step','decay'],
  ['Pulse ∗ Decay → RC charge/discharge','rect','decay'],
  ['Wide pulse ∗ triangular pulse','wide','tri'],
  ['Gaussian ∗ Gaussian','gauss','gauss'],
  ['Windowed sine ∗ pulse','sin','rect']
 ];
 function math(tex,cls=''){return `<div class="math ${cls}" data-tex="${encodeURIComponent(tex)}"></div>`}
 function typeset(root=document){root.querySelectorAll('.math[data-tex]').forEach(el=>{try{katex.render(decodeURIComponent(el.dataset.tex),el,{displayMode:true,throwOnError:false})}catch(e){el.textContent=decodeURIComponent(el.dataset.tex)}})}
 function opts(obj,sel){return Object.entries(obj).map(([k,v])=>`<option value="${k}" ${k===sel?'selected':''}>${v.label}</option>`).join('')}
 function render(){
  stop();
  const c=document.getElementById('convolution'); if(!c)return;
  c.innerHTML=`<div class="chapter-shell"><header class="chapter-header"><div class="chapter-title-block"><span class="chapter-number">CHAPTER 02</span><h1>CONVOLUTION</h1><p>Build intuition for the convolution integral through visualization, animation, and practice.</p></div></header><nav class="chapter-tabs">${tabs.map(([id,l])=>`<button class="chapter-tab ${state.tab===id?'active':''}" data-ctab="${id}">${l}</button>`).join('')}</nav><div class="chapter-content" id="convContent"></div></div>`;
  c.querySelectorAll('[data-ctab]').forEach(b=>b.onclick=()=>{state.tab=b.dataset.ctab;render()});
  ({concept:renderConcept,live:renderLive,step:renderStep,properties:renderProperties,exam:renderExam}[state.tab]||renderConcept)(document.getElementById('convContent'));typeset(c);
 }
 function renderConcept(c){
  c.innerHTML=`<h2 class="section-title">What is convolution?</h2><div class="conv-concept-grid"><article class="panel"><h3>Convolution integral</h3>${math('y(t)=x(t)*h(t)=\\int_{-\\infty}^{\\infty}x(\\tau)h(t-\\tau)\\,d\\tau','conv-concept-eq')}<p>For an LTI system, the output is obtained by convolving the input with the impulse response.</p></article><article class="panel"><h3>Graphical idea</h3><div class="conv-steps"><span>1. Flip</span><span>2. Shift</span><span>3. Multiply</span><span>4. Integrate</span></div><p>At each value of t, the overlap integral produces one point of y(t).</p></article></div><section class="conv-example conv-example-click" id="convConceptExample" role="button" tabindex="0"><div class="conv-example-open">OPEN IN LIVE LAB →</div><h2>Example — graphical convolution</h2><p>Use two causal rectangular pulses:</p>${math('x(t)=u(t)-u(t-2),\\qquad h(t)=u(t)-u(t-2)','conv-lab-eq')}<div class="conv-four-steps"><div><b>Flip</b>${math('h(\\tau)\\rightarrow h(-\\tau)','conv-small-eq')}</div><div><b>Shift</b>${math('h(-\\tau)\\rightarrow h(t-\\tau)','conv-small-eq')}</div><div><b>Multiply</b>${math('x(\\tau)h(t-\\tau)','conv-small-eq')}</div><div><b>Integrate</b>${math('y(t)=\\int x(\\tau)h(t-\\tau)d\\tau','conv-small-eq')}</div></div><p>The result is a triangular waveform because the overlap length grows, reaches a maximum, and then decreases.</p></section>`;const open=()=>{state.liveExample=0;state.tab='live';render()};document.getElementById('convConceptExample').onclick=open;document.getElementById('convConceptExample').onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();open()}};
 }
 function selectorHTML(prefix,withExamples=true){
  const ex=prefix==='lv'&&state.liveExample!=null;return `<div class="conv-mode-row"><label><input type="radio" name="${prefix}mode" value="choose" ${ex?'':'checked'}> Choose signals</label>${withExamples?`<label><input type="radio" name="${prefix}mode" value="example" ${ex?'checked':''}> Try an example</label>`:''}<label><input type="radio" name="${prefix}mode" value="custom"> Build custom signals</label></div><div id="${prefix}selector"></div>`;
 }
 function signalEditor(prefix,mode){
  if(mode==='choose')return `<div class="controls"><div class="control"><label>x(t)</label><select id="${prefix}x">${opts(sigs,'rect')}</select></div><div class="control"><label>h(t)</label><select id="${prefix}h">${opts(sigs,'rect')}</select></div></div>`;
  if(mode==='example')return `<div class="control"><label>Choose an example</label><select id="${prefix}example">${examples.map((e,i)=>`<option value="${i}" ${prefix==='lv'&&state.liveExample===i?'selected':''}>${e[0]}</option>`).join('')}</select></div>`;
  return `<div class="custom-help">Use <b>t</b> as the time variable. Supported forms include u(t), rect(t), tri(t), exp(-t)*u(t), sin(t), cos(t), constants, +, -, *, /, and parentheses.</div><div class="controls"><div class="control"><label>x(t) =</label><input id="${prefix}xexpr" value="u(t)-u(t-2)"><div class="live-equation" id="${prefix}xprev"></div></div><div class="control"><label>h(t) =</label><input id="${prefix}hexpr" value="exp(-t)*u(t)"><div class="live-equation" id="${prefix}hprev"></div></div></div>`;
 }
 function evalExpr(expr,t){
  const u=z=>z>=0?1:0,rect=z=>Math.abs(z)<=.5?1:0,tri=z=>Math.max(0,1-Math.abs(z));
  const sin=Math.sin,cos=Math.cos,exp=Math.exp,sqrt=Math.sqrt,abs=Math.abs,pi=Math.PI;
  let e=String(expr).replace(/\^/g,'**');
  return Function('t','u','rect','tri','sin','cos','exp','sqrt','abs','pi',`return (${e})`)(t,u,rect,tri,sin,cos,exp,sqrt,abs,pi);
 }
 function exprTex(e){return String(e).replace(/\*/g,'\\,').replace(/exp\(([^()]*)\)/g,'e^{$1}').replace(/sin\(/g,'\\sin(').replace(/cos\(/g,'\\cos(').replace(/\^2/g,'^{2}');}
 function getFns(prefix,mode){
  if(mode==='choose'){const x=sigs[document.getElementById(prefix+'x').value],h=sigs[document.getElementById(prefix+'h').value];return {x:x.fn,h:h.fn,xt:x.tex,ht:h.tex};}
  if(mode==='example'){const e=examples[+document.getElementById(prefix+'example').value],x=sigs[e[1]],h=sigs[e[2]];return{x:x.fn,h:h.fn,xt:x.tex,ht:h.tex};}
  const xe=document.getElementById(prefix+'xexpr').value,he=document.getElementById(prefix+'hexpr').value;
  return{x:t=>evalExpr(xe,t),h:t=>evalExpr(he,t),xt:exprTex(xe),ht:exprTex(he)};
 }
 function convolutionAt(x,h,t){let s=0;for(const tau of grid)s+=x(tau)*h(t-tau)*dt;return s}
 function convCurve(x,h){return grid.map(t=>convolutionAt(x,h,t))}
 function bindSelector(prefix,after,withExamples=true){
  let mode=document.querySelector(`input[name="${prefix}mode"]:checked`)?.value||'choose',box=document.getElementById(prefix+'selector');
  const rebuild=()=>{box.innerHTML=signalEditor(prefix,mode); if(mode==='custom'){const prev=()=>{document.getElementById(prefix+'xprev').innerHTML=math(`x(t)=${exprTex(document.getElementById(prefix+'xexpr').value)}`);document.getElementById(prefix+'hprev').innerHTML=math(`h(t)=${exprTex(document.getElementById(prefix+'hexpr').value)}`);typeset(box)};['xexpr','hexpr'].forEach(k=>document.getElementById(prefix+k).oninput=prev);prev()} box.querySelectorAll('select,input').forEach(el=>el.addEventListener('change',after));after();};
  document.querySelectorAll(`input[name="${prefix}mode"]`).forEach(r=>r.onchange=()=>{mode=r.value;rebuild()}); rebuild(); return()=>({mode,...getFns(prefix,mode)});
 }
 function renderLive(c){
  c.innerHTML=`<h2 class="section-title">Live Convolution Lab</h2><p class="muted">Watch h(t−τ) slide across x(τ) and see the convolution output build in real time.</p><div class="conv-live-layout"><div class="conv-live-main"><div id="lvSignals"></div><div class="conv-live-grid"><div class="plot-card"><h4>1. Slide and overlap</h4><canvas id="cv1"></canvas></div><div class="plot-card"><h4>2. Multiply and integrate</h4><canvas id="cv2"></canvas></div><div class="plot-card"><h4>3. Output y(t)</h4><canvas id="cv3"></canvas></div></div><div class="conv-metrics"><div><span>Current time</span><strong id="mTime">-6.00 s</strong></div><div><span>Overlap integral</span><strong id="mInt">0.0000</strong></div><div><span>Current y(t)</span><strong id="mY">0.0000</strong></div></div><div id="liveEq"></div></div><aside class="control-panel conv-live-controls">${selectorHTML('lv')}<div class="live-toolbar"><button class="btn" id="play">Play</button><button class="btn secondary" id="pause">Pause</button><button class="btn secondary" id="reset">Reset</button><label>Speed<select id="speed"><option>.5</option><option selected>1</option><option>1.5</option><option>2</option></select></label><label>Current t<input id="timeSlider" type="range" min="-6" max="6" step=".05" value="-6"></label><div class="conv-exact-time"><span>Time</span><input id="timeInput" type="number" value="-6" step=".05"></div><strong id="timeValue">-6.00 s</strong></div></aside></div>`;
  let getter=()=>null,curve=[],cached=null,liveGrid=Array.from({length:161},(_,i)=>-6+i*12/160),framePending=false,lastEquationTime=-999;

  /* Static work is done only when the selected signals change. */
  const updateAll=()=>{try{
    const f=getter();if(!f)return;
    cached=f;
    curve=convCurve(f.x,f.h);
    document.getElementById('lvSignals').innerHTML=`<div class="signals-used"><h3>Signals used in the simulation</h3><div>${math(`x(t)=${f.xt}`)}${math(`h(t)=${f.ht}`)}</div></div>`;
    typeset(document.getElementById('lvSignals'));
    drawFull();
  }catch(e){}};
  getter=bindSelector('lv',updateAll,true);
  const slider=document.getElementById('timeSlider');

  function updateText(t,yi,forceEquation=false){
    document.getElementById('timeValue').textContent=t.toFixed(2)+' s';
    const ti=document.getElementById('timeInput');if(ti&&document.activeElement!==ti)ti.value=t.toFixed(2);
    document.getElementById('mTime').textContent=t.toFixed(2)+' s';
    document.getElementById('mInt').textContent=yi.toFixed(4);
    document.getElementById('mY').textContent=yi.toFixed(4);
    /* KaTeX is deliberately throttled during animation. */
    if(forceEquation || Math.abs(t-lastEquationTime)>=.30){
      lastEquationTime=t;
      const eq=document.getElementById('liveEq');
      eq.innerHTML=math(`y(${t.toFixed(2)})=\\int_{-\\infty}^{\\infty}x(\\tau)h(${t.toFixed(2)}-\\tau)\\,d\\tau=${yi.toFixed(4)}`,'conv-result-eq');
      typeset(eq);
    }
  }

  function fastConvolutionAt(f,t){
    let sum=0,step=12/(liveGrid.length-1);
    for(const tau of liveGrid)sum+=f.x(tau)*f.h(t-tau)*step;
    return sum;
  }

  function drawFast(){drawFastAt(+slider.value);}
  function drawFastAt(t){
    if(!cached)return;
    state.t=t;
    const f=cached,yi=fastConvolutionAt(f,t);
    const xA=liveGrid.map(f.x),hA=liveGrid.map(tau=>f.h(t-tau)),pA=xA.map((v,k)=>v*hA[k]);
    updateText(t,yi,false);
    fastPlotConv('cv1',[[xA,'x(τ)',C.blue],[hA,'h(t−τ)',C.orange]]);
    fastPlotConv('cv2',[[pA,'x(τ)h(t−τ)',C.red]]);
    /* y(t) is precomputed once; only the moving marker changes. */
    plotArrays('cv3',[[curve,'y(t)',C.cyan]],-6,6,t);
  }

  function scheduleFast(){
    if(framePending)return;
    framePending=true;
    requestAnimationFrame(()=>{framePending=false;drawFast()});
  }

  function drawFull(){
    const f=cached||getter();if(!f)return;
    const t=+slider.value;state.t=t;
    const prod=tau=>f.x(tau)*f.h(t-tau),yi=convolutionAt(f.x,f.h,t);
    updateText(t,yi,true);
    plotFns('cv1',[[f.x,'x(τ)',C.blue],[tau=>f.h(t-tau),'h(t−τ)',C.orange]],-6,6);
    plotFns('cv2',[[prod,'x(τ)h(t−τ)',C.red]],-6,6);
    plotArrays('cv3',[[curve,'y(t)',C.cyan]],-6,6,t);
  }

  function fastPlotConv(id,series){
    const cv=document.getElementById(id);if(!cv)return;
    const d=Math.min(devicePixelRatio||1,1.5),w=Math.max(280,cv.clientWidth),h=cv.clientHeight||180;
    if(cv.width!==Math.round(w*d)||cv.height!==Math.round(h*d)){cv.width=Math.round(w*d);cv.height=Math.round(h*d);}
    const q=cv.getContext('2d');q.setTransform(d,0,0,d,0,0);q.clearRect(0,0,w,h);
    const vals=series.flatMap(s=>s[0]).filter(Number.isFinite),m=Math.max(1,Math.min(30,Math.max(...vals.map(Math.abs))||1));
    const L=42,R=10,Tp=12,B=28,sx=x=>L+(x+6)/12*(w-L-R),sy=y=>(h-B)/2-y/m*((h-B-Tp)*.4);
    q.strokeStyle='rgba(160,165,175,.18)';q.lineWidth=1;
    for(let x=-6;x<=6;x+=2){q.beginPath();q.moveTo(sx(x),Tp);q.lineTo(sx(x),h-B);q.stroke()}
    q.strokeStyle='rgba(220,225,230,.55)';q.beginPath();q.moveTo(L,sy(0));q.lineTo(w-R,sy(0));q.moveTo(sx(0),Tp);q.lineTo(sx(0),h-B);q.stroke();
    series.forEach(([a,l,col],j)=>{q.strokeStyle=col;q.lineWidth=2;q.setLineDash(j===1?[6,4]:[]);q.beginPath();a.forEach((y,k)=>{const xx=sx(liveGrid[k]),yy=sy(y);k?q.lineTo(xx,yy):q.moveTo(xx,yy)});q.stroke();q.setLineDash([]);q.fillStyle=col;q.font='11px Arial';q.fillText(l,L+8+j*110,Tp+12)});
  }

  slider.oninput=scheduleFast;
  slider.onchange=drawFull;
  const timeInput=document.getElementById('timeInput');
  const setExactTime=()=>{
    const v=Number(timeInput.value);if(!Number.isFinite(v))return;
    stop();slider.value=Math.max(-6,Math.min(6,v));drawFull();
  };
  timeInput.addEventListener('change',setExactTime);
  timeInput.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();setExactTime();timeInput.blur();}});
  document.getElementById('speed').onchange=e=>state.speed=+e.target.value;
  document.getElementById('reset').onclick=()=>{stop();slider.value=-6;drawFull()};
  document.getElementById('pause').onclick=()=>{stop();drawFull()};
  document.getElementById('play').onclick=()=>{
    if(state.playing)return;
    if(+slider.value>=5.999)slider.value=-6;
    state.playing=true;
    state.last=performance.now();
    let simTime=+slider.value;
    let lastDraw=0;
    const tick=now=>{
      if(!state.playing)return;
      const elapsed=Math.min(.08,(now-state.last)/1000);
      state.last=now;
      simTime+=elapsed*state.speed;
      if(simTime>=6)simTime=-6+(simTime-6);
      /* Keep the simulation clock independent from the range step.
         This prevents 1x from being repeatedly rounded back to the
         same slider value. 30 fps is more than enough for a smooth plot. */
      if(now-lastDraw>=33){
        lastDraw=now;
        slider.value=simTime.toFixed(3);
        drawFastAt(simTime);
      }
      if(state.playing)state.raf=requestAnimationFrame(tick);
    };
    state.raf=requestAnimationFrame(tick);
  };
  updateAll();
 }
 function stop(){state.playing=false;if(state.raf)cancelAnimationFrame(state.raf);state.raf=null}
 function tauTex(tex){return String(tex).replace(/\bt\b/g,'\\tau');}
 function flipTex(tex){return String(tex).replace(/\bt\b/g,'(-\\tau)');}
 function shiftSignalTex(tex,t){const arg=t<0?`(${t.toFixed(2)}+\\tau)`:`(${t.toFixed(2)}-\\tau)`;return String(tex).replace(/\bt\b/g,arg);}
 function renderStep(c){
  c.innerHTML=`<h2 class="section-title">Step-by-Step</h2><p class="muted">Freeze the convolution at one value of t and inspect each graphical operation.</p><div class="conv-step-layout"><div class="conv-step-main"><div id="stSignals"></div><div class="conv-four-grid"><div class="plot-card"><h4>1. Original signals</h4><div id="seq1" class="step-equation"></div><canvas id="s1"></canvas></div><div class="plot-card"><h4>2. Flip h(τ) → h(−τ)</h4><div id="seq2" class="step-equation"></div><canvas id="s2"></canvas></div><div class="plot-card"><h4>3. Shift → h(t−τ)</h4><div id="seq3" class="step-equation"></div><canvas id="s3"></canvas></div><div class="plot-card"><h4>4. Multiply and integrate</h4><div id="seq4" class="step-equation"></div><canvas id="s4"></canvas></div></div><div id="stResult"></div></div><aside class="control-panel conv-step-controls">${selectorHTML('st',false)}<div class="control step-time"><label>Choose t = <span id="stv">0.00</span></label><input id="stt" type="range" min="-6" max="6" step=".05" value="0"><div class="conv-exact-time"><span>Time</span><input id="stExact" type="number" value="0" step=".05"></div></div></aside></div>`;
  let getter=()=>null;const draw=()=>{try{const f=getter();if(!f)return;const t=+document.getElementById('stt').value,yi=convolutionAt(f.x,f.h,t);document.getElementById('stv').textContent=t.toFixed(2);const ex=document.getElementById('stExact');if(ex&&document.activeElement!==ex)ex.value=t.toFixed(2);document.getElementById('stSignals').innerHTML=`<div class="signals-used">${math(`x(t)=${f.xt},\\qquad h(t)=${f.ht}`)}</div>`;document.getElementById('stResult').innerHTML=`<div class="result-equations"><h4>Final value</h4>${math(`y(${t.toFixed(2)})=\\int_{-\\infty}^{\\infty}x(\\tau)h(${t.toFixed(2)}-\\tau)\\,d\\tau=${yi.toFixed(4)}`)}</div>`;
  document.getElementById('seq1').innerHTML=math(`x(\\tau)=${tauTex(f.xt)},\\qquad h(\\tau)=${tauTex(f.ht)}`,'conv-small-eq');
  document.getElementById('seq2').innerHTML=math(`h(\\tau)=${tauTex(f.ht)}\\;\\longrightarrow\\;h(-\\tau)=${flipTex(f.ht)}`,'conv-small-eq');
  document.getElementById('seq3').innerHTML=math(`h(-\\tau)\\;\\longrightarrow\\;h(t-\\tau),\\qquad t=${t.toFixed(2)}`,'conv-small-eq')+math(`h(${t.toFixed(2)}-\\tau)=${shiftSignalTex(f.ht,t)}`,'conv-small-eq');
  document.getElementById('seq4').innerHTML=math(`p(\\tau)=x(\\tau)h(${t.toFixed(2)}-\\tau)`,'conv-small-eq')+math(`y(${t.toFixed(2)})=\\int_{-\\infty}^{\\infty}p(\\tau)\\,d\\tau=${yi.toFixed(4)}`,'conv-small-eq');
  typeset(c);plotFns('s1',[[f.x,'x(τ)',C.blue],[f.h,'h(τ)',C.green]],-6,6);plotFns('s2',[[tau=>f.h(-tau),'h(−τ)',C.orange]],-6,6);plotFns('s3',[[f.x,'x(τ)',C.blue],[tau=>f.h(t-tau),'h(t−τ)',C.orange]],-6,6);plotFns('s4',[[tau=>f.x(tau)*f.h(t-tau),'product',C.red]],-6,6)}catch(e){}};
  getter=bindSelector('st',draw,false);document.getElementById('stt').oninput=draw;
  const stExact=document.getElementById('stExact');
  const setStepExact=()=>{const v=Number(stExact.value);if(!Number.isFinite(v))return;document.getElementById('stt').value=Math.max(-6,Math.min(6,v));draw();};
  stExact.addEventListener('change',setStepExact);stExact.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();setStepExact();stExact.blur();}});draw();
 }
 function renderProperties(c){
  stop();
  const cards=[
    ['Commutative','x(t)*h(t)=h(t)*x(t)','Swap the two signals. The convolution output does not change.','comm'],
    ['Associative','[x(t)*h(t)]*g(t)=x(t)*[h(t)*g(t)]','Change the grouping of three signals. Both paths end at the same output.','assoc'],
    ['Distributive','x(t)*[h_1(t)+h_2(t)]=x(t)*h_1(t)+x(t)*h_2(t)','Add before convolution or convolve separately and add afterward.','dist'],
    ['Time shift','h(t-T_1)*x(t-T_2)=y(t-T_1-T_2)','Shifting the two input signals shifts the output by the sum of the two delays.','shift'],
    ['Convolution with impulse','x(t)*\\delta(t-T)=x(t-T)','A moving impulse acts like a copy-and-shift operator.','impulse'],
    ['Area','\\int y(t)dt=\\left[\\int x(t)dt\\right]\\left[\\int h(t)dt\\right]','The total area of the output equals the product of the two input areas.','area'],
    ['Convolution with step','x(t)*u(t)=\\int_{-\\infty}^{t}x(\\tau)d\\tau','Convolution with a step accumulates the input: it behaves as an integrator.','step'],
    ['Differentiation','\\frac{d}{dt}y(t)=x(t)*\\frac{d}{dt}h(t)','Differentiate after convolution or differentiate one signal before convolution. The final results agree.','diff']
  ];
  const visual=k=>{
    if(k==='comm')return `<div class="prop-conv-story"><div class="conv-story-path"><b>PATH A — x*h</b><div class="story-mini"><span>x(τ)</span><canvas id="commAx"></canvas><span>h(t−τ) sliding</span><canvas id="commAh"></canvas></div><div class="story-stage">Output y(t) being formed</div><canvas id="commAy"></canvas></div><div class="property-equals">=</div><div class="conv-story-path"><b>PATH B — h*x</b><div class="story-mini"><span>h(τ)</span><canvas id="commBx"></canvas><span>x(t−τ) sliding</span><canvas id="commBh"></canvas></div><div class="story-stage">Output y(t) being formed</div><canvas id="commBy"></canvas></div></div><div class="prop-check">✓ Both constructions form the same y(t)</div>`;
    if(k==='assoc')return `<div class="prop-conv-story"><div class="conv-story-path"><b>PATH A — (x*h)*g</b><div class="story-mini"><span>x*h</span><canvas id="assocA1"></canvas><span>g(t−τ) sliding</span><canvas id="assocAg"></canvas></div><div class="story-stage">Output being formed</div><canvas id="assocA2"></canvas></div><div class="property-equals">=</div><div class="conv-story-path"><b>PATH B — x*(h*g)</b><div class="story-mini"><span>x(τ)</span><canvas id="assocBx"></canvas><span>(h*g)(t−τ) sliding</span><canvas id="assocB1"></canvas></div><div class="story-stage">Output being formed</div><canvas id="assocB2"></canvas></div></div><div class="prop-check">✓ Both groupings form the same final output</div>`;
    if(k==='dist')return `<div class="prop-conv-story"><div class="conv-story-path"><b>PATH A — x*(h₁+h₂)</b><div class="story-mini"><span>x(τ)</span><canvas id="distAx"></canvas><span>(h₁+h₂)(t−τ) sliding</span><canvas id="distA1"></canvas></div><div class="story-stage">Convolution output being formed</div><canvas id="distA2"></canvas></div><div class="property-equals">=</div><div class="conv-story-path"><b>PATH B — x*h₁ + x*h₂</b><div class="story-mini"><span>x(τ) with h₁(t−τ)</span><canvas id="distB1a"></canvas><span>x(τ) with h₂(t−τ)</span><canvas id="distB1b"></canvas></div><div class="story-stage">Sum of both convolution outputs being formed</div><canvas id="distB2"></canvas></div></div><div class="prop-check">✓ Both paths form the same final output</div>`;
    if(k==='shift')return `<div class="prop-conv-story"><div class="conv-story-path"><b>INPUT SHIFTS</b><div class="story-mini"><span>x(t−T₂)</span><canvas id="shiftX"></canvas><span>h(t−T₁)</span><canvas id="shiftH"></canvas></div><div class="story-stage">Convolve the shifted signals</div><canvas id="shiftConv"></canvas></div><div class="property-equals">=</div><div class="conv-story-path"><b>OUTPUT SHIFT</b><div class="story-stage">First x*h = y(t)</div><canvas id="shiftBase"></canvas><div class="story-stage">Then shift y by T₁+T₂</div><canvas id="shiftMoved"></canvas></div></div><div class="prop-explanation-live" id="shiftText"></div>`;
    if(k==='impulse')return `<div class="prop-conv-story"><div class="conv-story-path"><b>CONVOLUTION VIEW</b><div class="story-stage">① Original x(τ)</div><canvas id="impulseX"></canvas><div class="story-stage">② δ(t−τ−T) slides across x(τ)</div><canvas id="impulseIn"></canvas><div class="story-stage">③ It selects x(t−T)</div><canvas id="impulseConv"></canvas></div><div class="property-equals">→</div><div class="conv-story-path"><b>OUTPUT</b><div class="story-stage">As t moves, the selected values trace a shifted copy</div><canvas id="impulseOut"></canvas><div class="prop-check">x(t)*δ(t−T) = x(t−T)</div></div></div><div class="prop-explanation-live" id="impulseText"></div>`;
    if(k==='area')return `<div class="prop-three"><div><b>x(t)</b><canvas id="areaX"></canvas><span id="areaXn"></span></div><div><b>h(t)</b><canvas id="areaH"></canvas><span id="areaHn"></span></div><div><b>y(t)=x*h</b><canvas id="areaY"></canvas><span id="areaYn"></span></div></div><div class="prop-check" id="areaCheck"></div>`;
    if(k==='step')return `<div class="prop-three"><div><b>Input x(t)</b><canvas id="stepX"></canvas></div><div><b>Step u(t)</b><canvas id="stepU"></canvas></div><div><b>Accumulated output</b><canvas id="stepY"></canvas></div></div><div class="prop-progress"><span id="stepText"></span></div>`;
    return `<div class="prop-conv-story"><div class="conv-story-path"><b>PATH A</b><div class="story-mini"><span>x(t)</span><canvas id="diffAx"></canvas><span>h(t)</span><canvas id="diffAh"></canvas></div><div class="story-stage">① Convolve x*h = y(t)</div><canvas id="diffA1"></canvas><div class="story-stage">② Differentiate y(t)</div><canvas id="diffA2"></canvas></div><div class="property-equals">=</div><div class="conv-story-path"><b>PATH B</b><div class="story-mini"><span>x(t)</span><canvas id="diffBx"></canvas><span>dh(t)/dt</span><canvas id="diffBh"></canvas></div><div class="story-stage">① Differentiate h(t)</div><canvas id="diffB1"></canvas><div class="story-stage">② Convolve x*(dh/dt)</div><canvas id="diffB2"></canvas></div></div><div class="prop-check">✓ Same final result</div>`;
  };
  c.innerHTML=`<div class="properties-heading"><div><h2 class="section-title">Properties</h2><p class="muted">Follow each visual story to see what the property means.</p></div><div class="property-global-controls"><button class="btn" id="propPlay">Play</button><button class="btn secondary" id="propStop">Stop</button></div></div><div class="property-learning-grid">${cards.map((p,i)=>`<article class="property-card didactic-property"><span class="module-number">${String(i+1).padStart(2,'0')}</span><h3>${p[0]}</h3>${math(p[1],'conv-property-eq')}<p>${p[2]}</p>${visual(p[3])}</article>`).join('')}</div>`;
  typeset(c);

  const pg=Array.from({length:161},(_,i)=>-6+i*12/160),ds=12/160;
  const x=sigs.rect.fn,h=sigs.decay.fn,g=sigs.tri.fn,h2=sigs.tri.fn;
  const conv=(f,q,t)=>{let sum=0;for(const tau of pg)sum+=f(tau)*q(t-tau)*ds;return sum};
  const curve=(f,q)=>pg.map(t=>conv(f,q,t));
  const interp=(a,t)=>{const z=(t+6)/12*160,i=Math.floor(z),r=z-i;if(i<0||i>=160)return 0;return a[i]*(1-r)+a[i+1]*r};
  const xh=curve(x,h),hx=curve(h,x),hg=curve(h,g),assocL=pg.map(t=>conv(z=>interp(xh,z),g,t)),assocR=pg.map(t=>conv(x,z=>interp(hg,z),t));
  const sumh=t=>h(t)+h2(t),distL=curve(x,sumh),xh2=curve(x,h2),distR=xh.map((v,i)=>v+xh2[i]);
  const xx=curve(x,sigs.rect.fn),stepY=curve(x,sigs.step.fn);
  const xd=sigs.gauss.fn,hd=t=>Math.exp(-.5*t*t),dhd=t=>-t*Math.exp(-.5*t*t),yd=curve(xd,hd),diffR=curve(xd,dhd),diffL=yd.map((v,i,a)=>i===0?(a[1]-v)/ds:i===160?(v-a[i-1])/ds:(a[i+1]-a[i-1])/(2*ds));
  const area=a=>a.reduce((q,v)=>q+v*ds,0),ax=pg.map(x),ah=pg.map(h),areaX=area(ax),areaH=area(ah),areaY=area(xh);

  function plot(id,a,col=C.cyan,marker=null,fillTo=null,showTimeNumbers=false){
    const cv=document.getElementById(id);if(!cv)return;const d=Math.min(devicePixelRatio||1,1.5),w=Math.max(180,cv.clientWidth),H=cv.clientHeight||112;if(cv.width!==Math.round(w*d)||cv.height!==Math.round(H*d)){cv.width=Math.round(w*d);cv.height=Math.round(H*d)}
    const q=cv.getContext('2d');q.setTransform(d,0,0,d,0,0);q.clearRect(0,0,w,H);const m=Math.max(1,Math.max(...a.map(v=>Math.abs(v)||0))),L=23,R=6,T=7,B=17,sx=t=>L+(t+6)/12*(w-L-R),sy=y=>(H-B)/2-y/m*((H-B-T)*.38);
    q.strokeStyle='rgba(170,175,185,.22)';q.lineWidth=1;q.beginPath();q.moveTo(L,sy(0));q.lineTo(w-R,sy(0));q.moveTo(sx(0),T);q.lineTo(sx(0),H-B);q.stroke();if(showTimeNumbers){q.fillStyle='#8f929b';q.font='9px Arial';[-6,-4,-2,0,2,4,6].forEach(v=>q.fillText(String(v),sx(v)-4,H-4));q.fillStyle='#c7c9cf';q.fillText('t',w-10,sy(0)-4);}
    if(fillTo!==null){q.fillStyle='rgba(78,215,207,.12)';q.beginPath();q.moveTo(sx(-6),sy(0));a.forEach((y,k)=>{if(pg[k]<=fillTo)q.lineTo(sx(pg[k]),sy(y))});q.lineTo(sx(Math.min(6,fillTo)),sy(0));q.closePath();q.fill()}
    q.strokeStyle=col;q.lineWidth=1.8;q.beginPath();a.forEach((y,k)=>{const X=sx(pg[k]),Y=sy(y);k?q.lineTo(X,Y):q.moveTo(X,Y)});q.stroke();
    if(marker!==null){q.strokeStyle=C.gold;q.setLineDash([3,3]);q.beginPath();q.moveTo(sx(marker),T);q.lineTo(sx(marker),H-B);q.stroke();q.setLineDash([])}
  }
  function plotMulti(id,series,marker=null){const cv=document.getElementById(id);if(!cv)return;const d=Math.min(devicePixelRatio||1,1.5),w=Math.max(180,cv.clientWidth),H=cv.clientHeight||112;if(cv.width!==Math.round(w*d)||cv.height!==Math.round(H*d)){cv.width=Math.round(w*d);cv.height=Math.round(H*d)}const q=cv.getContext('2d');q.setTransform(d,0,0,d,0,0);q.clearRect(0,0,w,H);const vals=series.flatMap(s=>s[0]),m=Math.max(1,Math.max(...vals.map(v=>Math.abs(v)||0))),L=23,R=6,T=7,B=17,sx=t=>L+(t+6)/12*(w-L-R),sy=y=>(H-B)/2-y/m*((H-B-T)*.38);q.strokeStyle='rgba(170,175,185,.22)';q.lineWidth=1;q.beginPath();q.moveTo(L,sy(0));q.lineTo(w-R,sy(0));q.moveTo(sx(0),T);q.lineTo(sx(0),H-B);q.stroke();series.forEach(([arr,col])=>{q.strokeStyle=col;q.lineWidth=1.7;q.beginPath();arr.forEach((y,k)=>{const X=sx(pg[k]),Y=sy(y);k?q.lineTo(X,Y):q.moveTo(X,Y)});q.stroke()});if(marker!==null){q.strokeStyle=C.gold;q.setLineDash([3,3]);q.beginPath();q.moveTo(sx(marker),T);q.lineTo(sx(marker),H-B);q.stroke();q.setLineDash([])}}
  function impulsePlot(id,T0){const cv=document.getElementById(id);if(!cv)return;const d=Math.min(devicePixelRatio||1,1.5),w=Math.max(180,cv.clientWidth),H=cv.clientHeight||112;if(cv.width!==Math.round(w*d)||cv.height!==Math.round(H*d)){cv.width=Math.round(w*d);cv.height=Math.round(H*d)}const q=cv.getContext('2d');q.setTransform(d,0,0,d,0,0);q.clearRect(0,0,w,H);const L=23,R=6,Tp=7,B=17,sx=t=>L+(t+6)/12*(w-L-R),base=(H-B)/2;q.strokeStyle='rgba(170,175,185,.22)';q.lineWidth=1;q.beginPath();q.moveTo(L,base);q.lineTo(w-R,base);q.moveTo(sx(0),Tp);q.lineTo(sx(0),H-B);q.stroke();const top=base-36;q.strokeStyle=C.gold;q.fillStyle=C.gold;q.lineWidth=2;q.beginPath();q.moveTo(sx(T0),base);q.lineTo(sx(T0),top);q.stroke();q.beginPath();q.arc(sx(T0),top,3,0,Math.PI*2);q.fill();}
  const err=(a,b)=>Math.max(...a.map((v,i)=>Math.abs(v-b[i])));
  document.getElementById('areaXn').textContent=`Area x ≈ ${areaX.toFixed(2)}`;document.getElementById('areaHn').textContent=`Area h ≈ ${areaH.toFixed(2)}`;document.getElementById('areaYn').textContent=`Area y ≈ ${areaY.toFixed(2)}`;document.getElementById('areaCheck').textContent=`✓ ${areaX.toFixed(2)} × ${areaH.toFixed(2)} ≈ ${areaY.toFixed(2)}`;

  let running=true,raf=0,last=performance.now(),phase=0;
  const partialCurve=(full,t)=>full.map((v,i)=>pg[i]<=t?v:0);
  function draw(){
    const tau=-4+phase*10;
    const xTau=pg.map(x),hTau=pg.map(h),hSlide=pg.map(z=>h(tau-z)),xSlide=pg.map(z=>x(tau-z));
    plot('commAx',xTau,C.blue);plot('commAh',hSlide,C.green,tau);plot('commAy',partialCurve(xh,tau),C.cyan,tau);
    plot('commBx',hTau,C.green);plot('commBh',xSlide,C.blue,tau);plot('commBy',partialCurve(hx,tau),C.cyan,tau);
    const gSlide=pg.map(z=>g(tau-z)),hgSlide=pg.map(z=>interp(hg,tau-z));
    plot('assocA1',xh,C.blue);plot('assocAg',gSlide,C.green,tau);plot('assocA2',partialCurve(assocL,tau),C.cyan,tau);
    plot('assocBx',xTau,C.blue);plot('assocB1',hgSlide,C.green,tau);plot('assocB2',partialCurve(assocR,tau),C.cyan,tau);
    const sumSlide=pg.map(z=>sumh(tau-z)),h1Slide=pg.map(z=>h(tau-z)),h2Slide=pg.map(z=>h2(tau-z));
    plot('distAx',xTau,C.blue);plot('distA1',sumSlide,C.green,tau);plot('distA2',partialCurve(distL,tau),C.cyan,tau);
    plotMulti('distB1a',[[xTau,C.blue],[h1Slide,C.green]],tau);plotMulti('distB1b',[[xTau,C.blue],[h2Slide,C.orange]],tau);plot('distB2',partialCurve(distR,tau),C.cyan,tau);

    /* 4 — Time shift: show shifted inputs, their convolution, and shifted output. */
    const shift=phase*3,T1=shift*.45,T2=shift*.55,total=T1+T2;
    const sxA=pg.map(t=>x(t-T2)),shA=pg.map(t=>sigs.rect.fn(t-T1));
    const shiftedConv=pg.map(t=>conv(z=>x(z-T2),z=>sigs.rect.fn(z-T1),t));
    const shifted=pg.map(t=>interp(xx,t-total));
    plot('shiftX',sxA,C.blue,null,null,true);plot('shiftH',shA,C.green,null,null,true);plot('shiftConv',shiftedConv,C.cyan,null,null,true);
    plot('shiftBase',xx,C.blue,null,null,true);plot('shiftMoved',shifted,C.cyan,null,null,true);
    document.getElementById('shiftText').textContent=`T₁ = ${T1.toFixed(2)}, T₂ = ${T2.toFixed(2)} → both constructions shift y(t) by ${total.toFixed(2)}.`;

    /* 5 — Impulse: show x(τ), moving delta, the sampled product, and shifted copy. */
    const impT=-3+phase*6,impOut=pg.map(t=>x(t-impT));
    plot('impulseX',xTau,C.blue,tau-impT);impulsePlot('impulseIn',tau-impT);
    const samplePos=tau-impT,sampleVal=x(samplePos),sampleProd=pg.map(z=>Math.abs(z-samplePos)<ds*.7?sampleVal:0);
    plot('impulseConv',xTau,C.blue,samplePos);plot('impulseOut',impOut,C.cyan,tau);
    document.getElementById('impulseText').textContent=`For this frame: τ = t−T = ${samplePos.toFixed(2)}. The impulse selects x(${samplePos.toFixed(2)}) = ${sampleVal.toFixed(2)}. Repeating this for every t traces x(t−T).`;

    /* 6 and 7 intentionally preserved. */
    plot('areaX',ax,C.blue,null,6);plot('areaH',ah,C.green,null,6);plot('areaY',xh,C.cyan,null,6);
    const scan=-3+phase*7;plot('stepX',ax,C.blue,scan,scan);plot('stepU',pg.map(sigs.step.fn),C.green);const partial=stepY.map((v,i)=>pg[i]<=scan?v:NaN);plot('stepY',partial.map(v=>Number.isFinite(v)?v:0),C.cyan,scan);document.getElementById('stepText').textContent=`Accumulating x(τ) up to t = ${scan.toFixed(2)} builds y(t).`;

    /* 8 — Differentiation: expose both complete paths. */
    const xdArr=pg.map(xd),hdArr=pg.map(hd),dhdArr=pg.map(dhd);
    plot('diffAx',xdArr,C.blue);plot('diffAh',hdArr,C.green);
    plot('diffA1',yd,C.blue);plot('diffA2',diffL,C.cyan,tau);
    plot('diffBx',xdArr,C.blue);plot('diffBh',dhdArr,C.green);
    plot('diffB1',dhdArr,C.green);plot('diffB2',diffR,C.cyan,tau);
  }
  function tick(now){if(!running)return;const e=Math.min(.08,(now-last)/1000);last=now;phase=(phase+e*.1)%1;draw();raf=requestAnimationFrame(tick)}
  document.getElementById('propPlay').onclick=()=>{if(running)return;running=true;last=performance.now();raf=requestAnimationFrame(tick)};
  document.getElementById('propStop').onclick=()=>{running=false;if(raf)cancelAnimationFrame(raf);raf=0};
  draw();raf=requestAnimationFrame(tick);
 }
 function bank(){
  const B=[],add=(q,choices,answer,why,tex='',graph=null,category='conceptual')=>B.push({q,choices,answer,why,tex,graph,category});
  add('Which expression defines continuous-time convolution?',['y(t)=x(t)h(t)','y(t)=∫x(τ)h(t−τ)dτ','y(t)=x(t)+h(t)','y(t)=dx(t)/dt'],'y(t)=∫x(τ)h(t−τ)dτ','Convolution integrates the product of x(τ) and h(t−τ).','y(t)=\\int_{-\\infty}^{\\infty}x(\\tau)h(t-\\tau)\\,d\\tau');
  add('For the signals below, what is the shape of y(t)=x(t)*h(t)?',['Triangular pulse','Impulse','Sinusoid','Constant for all t'],'Triangular pulse','The overlap of two equal rectangular pulses grows linearly and then decreases linearly.','x(t)=u(t)-u(t-2),\\qquad h(t)=u(t)-u(t-2)');
  add('Which signal is obtained after the flip operation?',['h(τ)','h(−τ)','h(t+τ)','−h(τ)'],'h(−τ)','Graphical convolution first reflects h(τ) about τ=0.','h(\\tau)\\longrightarrow h(-\\tau)');
  add('After flipping h(τ), which expression is shifted across x(τ)?',['h(t−τ)','h(t+τ)','x(t−τ)','h(τ−t)'],'h(t−τ)','The flipped signal h(−τ) is shifted by t to obtain h(t−τ).','h(-\\tau)\\longrightarrow h(t-\\tau)');
  add('At a fixed value t=t₀, which integral gives the corresponding output sample?',['∫x(τ)h(t₀−τ)dτ','∫x(t₀)h(τ)dτ','x(t₀)h(t₀)','∫x(τ)+h(τ)dτ'],'∫x(τ)h(t₀−τ)dτ','The overlap integral at t₀ produces the single value y(t₀).','y(t_0)=\\int_{-\\infty}^{\\infty}x(\\tau)h(t_0-\\tau)\\,d\\tau');
  add('Which equation represents the commutative property?',['x*h=h*x','(x*h)*g=x*(h*g)','x*(h₁+h₂)=x*h₁+x*h₂','x*δ=x'],'x*h=h*x','The input and impulse response can be interchanged without changing the convolution.','x(t)*h(t)=h(t)*x(t)');
  add('Which equation represents the associative property?',['x*h=h*x','[x*h]*g=x*[h*g]','x*(h₁+h₂)=x*h₁+x*h₂','x*u=x'],'[x*h]*g=x*[h*g]','The grouping of three convolutions can be changed.','[x(t)*h(t)]*g(t)=x(t)*[h(t)*g(t)]');
  add('Which equation represents the distributive property?',['x*(h₁+h₂)=x*h₁+x*h₂','x*h=h*x','x*δ=x','x*u=u'],'x*(h₁+h₂)=x*h₁+x*h₂','Convolution distributes over addition.','x(t)*[h_1(t)+h_2(t)]=x(t)*h_1(t)+x(t)*h_2(t)');
  add('What is the convolution with a shifted impulse?',['x(t−T)','x(t+T)','δ(t−T)','0'],'x(t−T)','A shifted impulse shifts x(t) by the same amount.','x(t)*\\delta(t-T)=x(t-T)');
  add('What does convolution with the unit step do?',['Integrates x(t)','Differentiates x(t)','Squares x(t)','Reverses x(t)'],'Integrates x(t)','A unit-step impulse response acts as an ideal integrator.','x(t)*u(t)=\\int_{-\\infty}^{t}x(\\tau)\\,d\\tau');
  add('If both signals are causal, which statement is correct?',['Their convolution is causal','Their convolution is always periodic','Their convolution is zero','Their convolution is noncausal'],'Their convolution is causal','Causal convolved with causal remains causal.','x(t)=0,\\ h(t)=0\\ \\text{for }t<0\\quad\\Longrightarrow\\quad y(t)=0\\ \\text{for }t<0');
  add('For two unit-height causal pulses of width 2, what is the maximum value of y(t)?',['1','2','3','4'],'2','At maximum overlap, the product has unit height over a length of 2.','x(t)=h(t)=u(t)-u(t-2)');
  add('For finite-duration signals of widths 2 and 3, what is the output support width?',['1','2','3','5'],'5','For continuous-time convolution the support widths add.','W_y=W_x+W_h=2+3');
  add('Which equation gives the area property?',['A_y=A_xA_h','A_y=A_x+A_h','A_y=A_x-A_h','A_y=1'],'A_y=A_xA_h','The area under the output is the product of the areas of x and h.','\\int y(t)dt=\\left[\\int x(t)dt\\right]\\left[\\int h(t)dt\\right]');
  add('Which derivative relation is valid for convolution?',['dy/dt=x*dh/dt','dy/dt=x+h','dy/dt=xh','dy/dt=h/x'],'dy/dt=x*dh/dt','Differentiation may be transferred through the convolution operation.','\\frac{d}{dt}y(t)=x(t)*\\frac{d}{dt}h(t)');
  const pulseWidths=[[1,1],[1,2],[2,2],[2,3],[3,1],[3,2],[3,3],[4,1],[4,2],[4,3]];
  pulseWidths.forEach(([w1,w2])=>add(`Two finite rectangular pulses have widths ${w1} and ${w2}. What is the support width of their convolution?`,[String(Math.abs(w1-w2)),String(w1+w2),String(w1*w2),'1'],String(w1+w2),'For finite continuous-time pulses, convolution support widths add.',`W_y=W_x+W_h=${w1}+${w2}=${w1+w2}`));
  [1,2,3,4,5].forEach(T=>add(`What is the result of convolution with an impulse delayed by T=${T}?`,[`x(t-${T})`,`x(t+${T})`,`x(${T}t)`,'0'],`x(t-${T})`,'The impulse-shift property shifts x(t) by the impulse delay.',`x(t)*\\delta(t-${T})=x(t-${T})`));
  [1,2,3,4,5].forEach(A=>add(`If the area of x(t) is ${A} and the area of h(t) is 2, what is the area of y(t)=x*h?`,[String(A),String(A+2),String(2*A),String(A*A)],String(2*A),'Use the convolution area property.',`A_y=A_xA_h=${A}(2)=${2*A}`));
  [1,2,3,4,5].forEach(k=>add(`For h(t)=${k}δ(t), what is y(t)=x(t)*h(t)?`,[`${k}x(t)`,`x(t-${k})`,`x(t)+${k}`,'0'],`${k}x(t)`,'Scaling an impulse scales the signal under convolution.',`x(t)*${k}\\delta(t)=${k}x(t)`));
  const extra=[
   ['What is the integration variable in the convolution integral?',['τ','t only','ω','s'],'τ','τ is the dummy variable of integration.','y(t)=\\int x(\\tau)h(t-\\tau)d\\tau'],
   ['Which operation follows shifting in graphical convolution?',['Multiply the overlapping signals','Differentiate both signals','Reverse x again','Take a Fourier transform'],'Multiply the overlapping signals','After flip and shift, x(τ) and h(t−τ) are multiplied pointwise.','x(\\tau)h(t-\\tau)'],
   ['Which operation follows multiplication in graphical convolution?',['Integrate over τ','Flip again','Differentiate','Scale t'],'Integrate over τ','Integration of the product produces y(t).','y(t)=\\int x(\\tau)h(t-\\tau)d\\tau'],
   ['What is x(t)*δ(t)?',['x(t)','δ(t)','0','x(−t)'],'x(t)','The unit impulse is the identity element of convolution.','x(t)*\\delta(t)=x(t)'],
   ['If h(t)=u(t), the corresponding LTI system behaves as:',['An ideal integrator','An ideal differentiator','A time reverser','A multiplier'],'An ideal integrator','Convolution with u(t) accumulates the input.','y(t)=\\int_{-\\infty}^{t}x(\\tau)d\\tau']
  ];
  extra.forEach(e=>add(...e));
  while(B.length<50){const T=B.length-39;add(`For a shifted impulse δ(t-${T}), which signal appears at the output?`,[`x(t-${T})`,`x(t+${T})`,`x(t)`,'0'],`x(t-${T})`,'Use the convolution-with-impulse property.',`x(t)*\\delta(t-${T})=x(t-${T})`)}
  add('From the graph, what is the convolution of the two unit-width rectangular pulses?',['A triangular pulse','A rectangular pulse','An impulse','A sinusoid'],'A triangular pulse','The overlap length grows linearly and then decreases.','', 'rectRect','graph');
  add('The plotted output rises linearly and then stays constant. Which pair is consistent with it?',['rectangular pulse * unit step','impulse * impulse','sine * sine','Gaussian * impulse'],'rectangular pulse * unit step','Convolving a finite rectangular pulse with u(t) accumulates its area.','', 'rectStep','graph');
  add('The graph shows a smooth bell-shaped output from two bell-shaped inputs. Which property/example is represented?',['Gaussian * Gaussian','step * step','rect * impulse','sine * impulse'],'Gaussian * Gaussian','The convolution of two Gaussians is another Gaussian with a larger spread.','', 'gauss','graph');
  add('At the marked shift, the two rectangular pulses have no overlap. What is y(t)?',['0','1','2','infinite'],'0','With no overlap, the product is zero everywhere, so its integral is zero.','', 'noOverlap','graph');
  add('At maximum overlap of two unit-height width-2 pulses, what value does the graph reach?',['2','1','4','0'],'2','The product has height 1 over an overlap length of 2.','', 'triPeak','graph');
  add('Which output graph corresponds to x(t)*δ(t−1)?',['x(t) shifted right by 1','x(t) shifted left by 1','x(t) reversed','zero'],'x(t) shifted right by 1','A delayed impulse shifts the signal by the same delay.','', 'shift','graph');
  return B.slice(0,56);

 }
 function drawTestGraph(id,type){const cv=document.getElementById(id);if(!cv)return;let N=241,tt=Array.from({length:N},(_,i)=>-3+i*6/(N-1)),series=[];if(type==='rectRect'||type==='triPeak')series=[tt.map(t=>t<0||t>4?0:t<=2?t:4-t)];else if(type==='rectStep')series=[tt.map(t=>t<0?0:t<2?t:2)];else if(type==='gauss')series=[tt.map(t=>Math.exp(-t*t/2))];else if(type==='noOverlap')series=[tt.map(()=>0)];else if(type==='shift')series=[tt.map(t=>Math.abs(t-1)<=.8?1:0)];const d=Math.min(devicePixelRatio||1,1.5),W=Math.max(320,cv.clientWidth),H=150;cv.width=W*d;cv.height=H*d;let q=cv.getContext('2d');q.setTransform(d,0,0,d,0,0);q.clearRect(0,0,W,H);let L=38,R=10,T=10,B=25,sx=x=>L+(x+3)/6*(W-L-R),sy=y=>H-B-y/2.3*(H-B-T);q.strokeStyle='#555';q.beginPath();q.moveTo(L,H-B);q.lineTo(W-R,H-B);q.moveTo(sx(0),T);q.lineTo(sx(0),H-B);q.stroke();q.fillStyle='#999';q.font='9px Arial';[-3,-2,-1,0,1,2,3].forEach(x=>q.fillText(String(x),sx(x)-3,H-8));q.strokeStyle=C.cyan;q.lineWidth=2.2;q.beginPath();series[0].forEach((y,i)=>{let x=tt[i],xx=sx(x),yy=sy(y);i?q.lineTo(xx,yy):q.moveTo(xx,yy)});q.stroke()}
  function renderExam(c){if(!state.exam)newExam();c.innerHTML=`<div class="exam-toolbar"><div><h2 class="section-title">Convolution Test</h2><p class="muted">10 questions are selected from an internal bank of 50 questions.</p><div id="cscore"></div></div><button class="btn" id="cnew">Generate new test</button></div><div id="cquestions">${state.exam.map((q,i)=>`<article class="exam-card"><div class="question-category">${q.graph?'GRAPH INTERPRETATION':i<3?'CONCEPTUAL':i<6?'EQUATION / CALCULATION':'APPLICATION'}</div>${q.graph?`<div class="test-graph-card"><canvas id="convQGraph${i}"></canvas></div>`:''}<h3>${i+1}. ${q.q}</h3>${q.tex?math(q.tex,'conv-test-eq'):''}<div class="answers">${q.choices.map((a,j)=>`<label class="answer"><input type="radio" name="cq${i}" value="${a}"><span>${String.fromCharCode(65+j)}. ${a}</span></label>`).join('')}</div><div id="cf${i}"></div></article>`).join('')}</div><button class="btn" id="cgrade">Grade test</button>`;
  typeset(c);state.exam.forEach((q,i)=>{if(q.graph)drawTestGraph('convQGraph'+i,q.graph)});
  document.getElementById('cnew').onclick=()=>{newExam();renderExam(c)};
  document.getElementById('cgrade').onclick=()=>{let sc=0;state.exam.forEach((q,i)=>{const a=document.querySelector(`input[name=cq${i}]:checked`)?.value,ok=a===q.answer;if(ok)sc++;document.getElementById('cf'+i).innerHTML=`<div class="feedback ${ok?'correct':'incorrect'}"><b>${ok?'✓ CORRECT':'✗ INCORRECT'}</b><br>Your answer: ${a||'No answer'}<br>Correct answer: <b>${q.answer}</b><br>${q.why}</div>`});document.getElementById('cscore').innerHTML=`<p class="score">Score: ${sc}/10</p>`;window.scrollTo({top:document.getElementById('cscore').getBoundingClientRect().top+scrollY-20,behavior:'smooth'})};}
 function newExam(){const b=bank().slice(),graphs=b.filter(q=>q.graph),others=b.filter(q=>!q.graph),r=[];while(r.length<2&&graphs.length)r.push(graphs.splice(Math.floor(Math.random()*graphs.length),1)[0]);while(r.length<10&&others.length)r.push(others.splice(Math.floor(Math.random()*others.length),1)[0]);state.exam=r.sort(()=>Math.random()-.5)}
 function plotFns(id,series,xmin=-6,xmax=6){plotArrays(id,series.map(([fn,l,c])=>[grid.map(fn),l,c]),xmin,xmax)}
 function plotArrays(id,series,xmin=-6,xmax=6,marker=null){
  const cv=document.getElementById(id);if(!cv)return;const d=devicePixelRatio||1,w=Math.max(280,cv.clientWidth),h=cv.clientHeight||180;cv.width=w*d;cv.height=h*d;const q=cv.getContext('2d');q.setTransform(d,0,0,d,0,0);q.clearRect(0,0,w,h);const vals=series.flatMap(s=>s[0]).filter(Number.isFinite),m=Math.max(1,Math.min(30,Math.max(...vals.map(Math.abs))||1));const L=42,R=10,T=12,B=28,sx=x=>L+(x-xmin)/(xmax-xmin)*(w-L-R),sy=y=>(h-B)/2-y/m*((h-B-T)*.4);q.strokeStyle='rgba(160,165,175,.23)';q.lineWidth=1;for(let x=-6;x<=6;x+=2){q.beginPath();q.moveTo(sx(x),T);q.lineTo(sx(x),h-B);q.stroke()}q.strokeStyle='rgba(220,225,230,.55)';q.beginPath();q.moveTo(L,sy(0));q.lineTo(w-R,sy(0));q.moveTo(sx(0),T);q.lineTo(sx(0),h-B);q.stroke();series.forEach(([a,l,c],j)=>{q.strokeStyle=c;q.lineWidth=2;q.setLineDash(j===1?[6,4]:[]);q.beginPath();a.forEach((y,i)=>{const x=sx(grid[i]);if(i===0)q.moveTo(x,sy(y));else q.lineTo(x,sy(y))});q.stroke();q.setLineDash([]);q.fillStyle=c;q.font='11px Arial';q.fillText(l,L+8+j*110,T+12)});if(marker!=null){q.strokeStyle=C.gold;q.setLineDash([4,4]);q.beginPath();q.moveTo(sx(marker),T);q.lineTo(sx(marker),h-B);q.stroke();q.setLineDash([])}q.fillStyle='#a7abb4';q.font='10px Arial';q.fillText('t',w-R-8,sy(0)-5);q.fillText('y',sx(0)+6,T+10);
 }
 return{render};
})();