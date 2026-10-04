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
  c.innerHTML=`<h2 class="section-title">What is convolution?</h2><div class="conv-concept-grid"><article class="panel"><h3>Convolution integral</h3>${math('y(t)=x(t)*h(t)=\\int_{-\\infty}^{\\infty}x(\\tau)h(t-\\tau)\\,d\\tau','conv-concept-eq')}<p>For an LTI system, the output is obtained by convolving the input with the impulse response.</p></article><article class="panel"><h3>Graphical idea</h3><div class="conv-steps"><span>1. Flip</span><span>2. Shift</span><span>3. Multiply</span><span>4. Integrate</span></div><p>At each value of t, the overlap integral produces one point of y(t).</p></article></div><section class="conv-example"><h2>Example — graphical convolution</h2><p>Use two causal rectangular pulses:</p>${math('x(t)=u(t)-u(t-2),\\qquad h(t)=u(t)-u(t-2)','conv-lab-eq')}<div class="conv-four-steps"><div><b>Flip</b>${math('h(\\tau)\\rightarrow h(-\\tau)','conv-small-eq')}</div><div><b>Shift</b>${math('h(-\\tau)\\rightarrow h(t-\\tau)','conv-small-eq')}</div><div><b>Multiply</b>${math('x(\\tau)h(t-\\tau)','conv-small-eq')}</div><div><b>Integrate</b>${math('y(t)=\\int x(\\tau)h(t-\\tau)d\\tau','conv-small-eq')}</div></div><p>The result is a triangular waveform because the overlap length grows, reaches a maximum, and then decreases.</p></section>`;
 }
 function selectorHTML(prefix,withExamples=true){
  return `<div class="conv-mode-row"><label><input type="radio" name="${prefix}mode" value="choose" checked> Choose signals</label>${withExamples?`<label><input type="radio" name="${prefix}mode" value="example"> Try an example</label>`:''}<label><input type="radio" name="${prefix}mode" value="custom"> Build custom signals</label></div><div id="${prefix}selector"></div>`;
 }
 function signalEditor(prefix,mode){
  if(mode==='choose')return `<div class="controls"><div class="control"><label>x(t)</label><select id="${prefix}x">${opts(sigs,'rect')}</select></div><div class="control"><label>h(t)</label><select id="${prefix}h">${opts(sigs,'rect')}</select></div></div>`;
  if(mode==='example')return `<div class="control"><label>Choose an example</label><select id="${prefix}example">${examples.map((e,i)=>`<option value="${i}">${e[0]}</option>`).join('')}</select></div>`;
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
  let mode='choose',box=document.getElementById(prefix+'selector');
  const rebuild=()=>{box.innerHTML=signalEditor(prefix,mode); if(mode==='custom'){const prev=()=>{document.getElementById(prefix+'xprev').innerHTML=math(`x(t)=${exprTex(document.getElementById(prefix+'xexpr').value)}`);document.getElementById(prefix+'hprev').innerHTML=math(`h(t)=${exprTex(document.getElementById(prefix+'hexpr').value)}`);typeset(box)};['xexpr','hexpr'].forEach(k=>document.getElementById(prefix+k).oninput=prev);prev()} box.querySelectorAll('select,input').forEach(el=>el.addEventListener('change',after));after();};
  document.querySelectorAll(`input[name="${prefix}mode"]`).forEach(r=>r.onchange=()=>{mode=r.value;rebuild()}); rebuild(); return()=>({mode,...getFns(prefix,mode)});
 }
 function renderLive(c){
  c.innerHTML=`<h2 class="section-title">Live Convolution Lab</h2><p class="muted">Watch h(t−τ) slide across x(τ) and see the convolution output build in real time.</p>${selectorHTML('lv')}<div id="lvSignals"></div><div class="live-toolbar"><button class="btn" id="play">Play</button><button class="btn secondary" id="pause">Pause</button><button class="btn secondary" id="reset">Reset</button><label>Speed <select id="speed"><option>.5</option><option selected>1</option><option>1.5</option><option>2</option></select></label><label>Current t <input id="timeSlider" type="range" min="-6" max="6" step=".05" value="-6"></label><div class="conv-exact-time"><span>Time</span><input id="timeInput" type="number" value="-6" step=".05"></div><strong id="timeValue">-6.00 s</strong></div><div class="conv-live-grid"><div class="plot-card"><h4>1. Slide and overlap</h4><canvas id="cv1"></canvas></div><div class="plot-card"><h4>2. Multiply and integrate</h4><canvas id="cv2"></canvas></div><div class="plot-card"><h4>3. Output y(t)</h4><canvas id="cv3"></canvas></div></div><div class="conv-metrics"><div><span>Current time</span><strong id="mTime">-6.00 s</strong></div><div><span>Overlap integral</span><strong id="mInt">0.0000</strong></div><div><span>Current y(t)</span><strong id="mY">0.0000</strong></div></div><div id="liveEq"></div>`;
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
  c.innerHTML=`<h2 class="section-title">Step-by-Step</h2><p class="muted">Freeze the convolution at one value of t and inspect each graphical operation.</p>${selectorHTML('st',false)}<div class="control step-time"><label>Choose t = <span id="stv">0.00</span></label><div class="step-time-row"><input id="stt" type="range" min="-6" max="6" step=".05" value="0"><div class="conv-exact-time"><span>Time</span><input id="stExact" type="number" value="0" step=".05"></div></div></div><div id="stSignals"></div><div class="conv-four-grid"><div class="plot-card"><h4>1. Original signals</h4><div id="seq1" class="step-equation"></div><canvas id="s1"></canvas></div><div class="plot-card"><h4>2. Flip h(τ) → h(−τ)</h4><div id="seq2" class="step-equation"></div><canvas id="s2"></canvas></div><div class="plot-card"><h4>3. Shift → h(t−τ)</h4><div id="seq3" class="step-equation"></div><canvas id="s3"></canvas></div><div class="plot-card"><h4>4. Multiply and integrate</h4><div id="seq4" class="step-equation"></div><canvas id="s4"></canvas></div></div><div id="stResult"></div>`;
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
  const props=[
   ['Commutative','x(t)*h(t)=h(t)*x(t)','Interchanging the input and impulse response does not change the output.','rect','decay'],
   ['Associative','[x(t)*h(t)]*g(t)=x(t)*[h(t)*g(t)]','Three convolutions may be grouped in either order.','rect','tri'],
   ['Distributive','x(t)*[h_1(t)+h_2(t)]=x(t)*h_1(t)+x(t)*h_2(t)','Convolution distributes over addition.','rect','decay'],
   ['Time shift','h(t-T_1)*x(t-T_2)=y(t-T_1-T_2)','Input/impulse-response shifts add in the output shift.','rect','rect'],
   ['Convolution with impulse','x(t)*\\delta(t-T)=x(t-T)','An impulse shifts a signal without changing its shape.','rect','rect'],
   ['Area','\\int y(t)dt=\\left[\\int x(t)dt\\right]\\left[\\int h(t)dt\\right]','The output area equals the product of the two input areas.','rect','decay'],
   ['Convolution with step','x(t)*u(t)=\\int_{-\\infty}^{t}x(\\tau)d\\tau','A unit-step impulse response acts as an ideal integrator.','rect','step'],
   ['Differentiation','\\frac{d}{dt}y(t)=x(t)*\\frac{d}{dt}h(t)','Differentiation can be transferred through convolution.','rect','decay']
  ];
  c.innerHTML=`<h2 class="section-title">Properties</h2><p class="muted">Use convolution properties to simplify calculations and interpret LTI systems.</p><div class="property-grid">${props.map((p,i)=>`<article class="property-card"><span class="module-number">${String(i+1).padStart(2,'0')}</span><h3>${p[0]}</h3>${math(p[1],'conv-property-eq')}<p>${p[2]}</p><h4>Example</h4><canvas id="pr${i}"></canvas></article>`).join('')}</div>`;typeset(c);props.forEach((p,i)=>{const x=sigs[p[3]].fn,h=sigs[p[4]].fn,y=convCurve(x,h);plotArrays('pr'+i,[[y,'example output',C.cyan]],-6,6)});
 }
 function bank(){
  const B=[],add=(q,choices,answer,why,tex='')=>B.push({q,choices,answer,why,tex});
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
  return B.slice(0,50);
 }
 function renderExam(c){if(!state.exam)newExam();c.innerHTML=`<div class="exam-toolbar"><div><h2 class="section-title">Convolution Test</h2><p class="muted">10 questions are selected from an internal bank of 50 questions.</p><div id="cscore"></div></div><button class="btn" id="cnew">Generate new test</button></div><div id="cquestions">${state.exam.map((q,i)=>`<article class="exam-card"><h3>${i+1}. ${q.q}</h3>${q.tex?math(q.tex,'conv-test-eq'):''}<div class="answers">${q.choices.map((a,j)=>`<label class="answer"><input type="radio" name="cq${i}" value="${a}"><span>${String.fromCharCode(65+j)}. ${a}</span></label>`).join('')}</div><div id="cf${i}"></div></article>`).join('')}</div><button class="btn" id="cgrade">Grade test</button>`;
  typeset(c);
  document.getElementById('cnew').onclick=()=>{newExam();renderExam(c)};
  document.getElementById('cgrade').onclick=()=>{let sc=0;state.exam.forEach((q,i)=>{const a=document.querySelector(`input[name=cq${i}]:checked`)?.value,ok=a===q.answer;if(ok)sc++;document.getElementById('cf'+i).innerHTML=`<div class="feedback ${ok?'correct':'incorrect'}"><b>${ok?'✓ CORRECT':'✗ INCORRECT'}</b><br>Your answer: ${a||'No answer'}<br>Correct answer: <b>${q.answer}</b><br>${q.why}</div>`});document.getElementById('cscore').innerHTML=`<p class="score">Score: ${sc}/10</p>`;window.scrollTo({top:document.getElementById('cscore').getBoundingClientRect().top+scrollY-20,behavior:'smooth'})};}
 function newExam(){const b=bank().slice(),r=[];while(r.length<10)r.push(b.splice(Math.floor(Math.random()*b.length),1)[0]);state.exam=r}
 function plotFns(id,series,xmin=-6,xmax=6){plotArrays(id,series.map(([fn,l,c])=>[grid.map(fn),l,c]),xmin,xmax)}
 function plotArrays(id,series,xmin=-6,xmax=6,marker=null){
  const cv=document.getElementById(id);if(!cv)return;const d=devicePixelRatio||1,w=Math.max(280,cv.clientWidth),h=cv.clientHeight||180;cv.width=w*d;cv.height=h*d;const q=cv.getContext('2d');q.setTransform(d,0,0,d,0,0);q.clearRect(0,0,w,h);const vals=series.flatMap(s=>s[0]).filter(Number.isFinite),m=Math.max(1,Math.min(30,Math.max(...vals.map(Math.abs))||1));const L=42,R=10,T=12,B=28,sx=x=>L+(x-xmin)/(xmax-xmin)*(w-L-R),sy=y=>(h-B)/2-y/m*((h-B-T)*.4);q.strokeStyle='rgba(160,165,175,.23)';q.lineWidth=1;for(let x=-6;x<=6;x+=2){q.beginPath();q.moveTo(sx(x),T);q.lineTo(sx(x),h-B);q.stroke()}q.strokeStyle='rgba(220,225,230,.55)';q.beginPath();q.moveTo(L,sy(0));q.lineTo(w-R,sy(0));q.moveTo(sx(0),T);q.lineTo(sx(0),h-B);q.stroke();series.forEach(([a,l,c],j)=>{q.strokeStyle=c;q.lineWidth=2;q.setLineDash(j===1?[6,4]:[]);q.beginPath();a.forEach((y,i)=>{const x=sx(grid[i]);if(i===0)q.moveTo(x,sy(y));else q.lineTo(x,sy(y))});q.stroke();q.setLineDash([]);q.fillStyle=c;q.font='11px Arial';q.fillText(l,L+8+j*110,T+12)});if(marker!=null){q.strokeStyle=C.gold;q.setLineDash([4,4]);q.beginPath();q.moveTo(sx(marker),T);q.lineTo(sx(marker),h-B);q.stroke();q.setLineDash([])}q.fillStyle='#a7abb4';q.font='10px Arial';q.fillText('t',w-R-8,sy(0)-5);q.fillText('y',sx(0)+6,T+10);
 }
 return{render};
})();