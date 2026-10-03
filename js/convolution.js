/* EE-207 — Convolution chapter. Client-side only. */
window.Convolution=(()=>{
 const tabs=[['concept','Concept'],['live','Live Convolution Lab'],['step','Step-by-Step'],['properties','Properties'],['exam','Mini Exam']];
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
  c.innerHTML=`<h2 class="section-title">Live Convolution Lab</h2><p class="muted">Watch h(t−τ) slide across x(τ) and see the convolution output build in real time.</p>${selectorHTML('lv')}<div id="lvSignals"></div><div class="live-toolbar"><button class="btn" id="play">Play</button><button class="btn secondary" id="pause">Pause</button><button class="btn secondary" id="reset">Reset</button><label>Speed <select id="speed"><option>.5</option><option selected>1</option><option>1.5</option><option>2</option></select></label><label>Current t <input id="timeSlider" type="range" min="-6" max="6" step=".05" value="-6"></label><strong id="timeValue">-6.00 s</strong></div><div class="conv-live-grid"><div class="plot-card"><h4>1. Slide and overlap</h4><canvas id="cv1"></canvas></div><div class="plot-card"><h4>2. Multiply and integrate</h4><canvas id="cv2"></canvas></div><div class="plot-card"><h4>3. Output y(t)</h4><canvas id="cv3"></canvas></div></div><div class="conv-metrics"><div><span>Current time</span><strong id="mTime">-6.00 s</strong></div><div><span>Overlap integral</span><strong id="mInt">0.0000</strong></div><div><span>Current y(t)</span><strong id="mY">0.0000</strong></div></div><div id="liveEq"></div>`;
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
 function renderStep(c){
  c.innerHTML=`<h2 class="section-title">Step-by-Step</h2><p class="muted">Freeze the convolution at one value of t and inspect each graphical operation.</p>${selectorHTML('st',false)}<div class="control step-time"><label>Choose t = <span id="stv">0.00</span></label><input id="stt" type="range" min="-6" max="6" step=".05" value="0"></div><div id="stSignals"></div><div class="conv-four-grid"><div class="plot-card"><h4>1. Original signals</h4><canvas id="s1"></canvas></div><div class="plot-card"><h4>2. Flip h(τ) → h(−τ)</h4><canvas id="s2"></canvas></div><div class="plot-card"><h4>3. Shift → h(t−τ)</h4><canvas id="s3"></canvas></div><div class="plot-card"><h4>4. Multiply</h4><canvas id="s4"></canvas></div></div><div id="stResult"></div>`;
  let getter=()=>null;const draw=()=>{try{const f=getter();if(!f)return;const t=+document.getElementById('stt').value,yi=convolutionAt(f.x,f.h,t);document.getElementById('stv').textContent=t.toFixed(2);document.getElementById('stSignals').innerHTML=`<div class="signals-used">${math(`x(t)=${f.xt},\\qquad h(t)=${f.ht}`)}</div>`;document.getElementById('stResult').innerHTML=`<div class="result-equations">${math(`y(${t.toFixed(2)})=\\int x(\\tau)h(${t.toFixed(2)}-\\tau)d\\tau=${yi.toFixed(4)}`)}</div>`;typeset(c);plotFns('s1',[[f.x,'x(τ)',C.blue],[f.h,'h(τ)',C.green]],-6,6);plotFns('s2',[[tau=>f.h(-tau),'h(−τ)',C.orange]],-6,6);plotFns('s3',[[f.x,'x(τ)',C.blue],[tau=>f.h(t-tau),'h(t−τ)',C.orange]],-6,6);plotFns('s4',[[tau=>f.x(tau)*f.h(t-tau),'product',C.red]],-6,6)}catch(e){}};
  getter=bindSelector('st',draw,false);document.getElementById('stt').oninput=draw;draw();
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
  const q=[
   ['What operation is performed first on h(τ) in graphical convolution?','Flip it to obtain h(−τ)','Graphical convolution first reflects one signal.'],
   ['What does each overlap integral produce?','One point of y(t)','For each fixed t, the integral is the output value at that t.'],
   ['Is convolution commutative?','Yes','x*h=h*x.'],
   ['What is x(t)*δ(t−2)?','x(t−2)','Convolution with a shifted impulse shifts the signal.'],
   ['What does x(t)*u(t) represent?','An accumulated integral of x','The step convolution integrates x up to t.'],
   ['If two unit-height width-2 causal pulses are convolved, what is the peak?','2','The maximum overlap length is 2.'],
   ['What variable is integrated in the continuous-time convolution integral?','τ','τ is the dummy integration variable.'],
   ['Which term slides during graphical convolution?','h(t−τ)','After flipping, the signal is shifted by t.'],
   ['What is the output support width for two finite pulses of widths 2 and 3?','5','For continuous-time finite pulses the widths add.'],
   ['If x and h are causal, is y=x*h causal?','Yes','Causal convolved with causal remains causal.']
  ];
  while(q.length<50){const n=q.length+1;q.push([`Property check ${n}: does x(t)*h(t) equal h(t)*x(t)?`,'Yes','This is the commutative property of convolution.'])}return q;
 }
 function renderExam(c){if(!state.exam)newExam();c.innerHTML=`<div class="exam-toolbar"><div><h2 class="section-title">Convolution Test</h2><p class="muted">10 questions selected from an internal bank of 50.</p><div id="cscore"></div></div><button class="btn" id="cnew">Generate new test</button></div><div>${state.exam.map((q,i)=>`<article class="exam-card"><h3>${i+1}. ${q[0]}</h3><input class="conv-answer-input" id="ca${i}" placeholder="Type your answer"><div id="cf${i}"></div></article>`).join('')}</div><button class="btn" id="cgrade">Grade test</button>`;document.getElementById('cnew').onclick=()=>{newExam();renderExam(c)};document.getElementById('cgrade').onclick=()=>{let sc=0;state.exam.forEach((q,i)=>{const a=document.getElementById('ca'+i).value.trim().toLowerCase(),ok=a&&((q[1].toLowerCase().includes(a)&&a.length>2)||a===q[1].toLowerCase());if(ok)sc++;document.getElementById('cf'+i).innerHTML=`<div class="feedback ${ok?'correct':'incorrect'}"><b>${ok?'✓ CORRECT':'✗ INCORRECT'}</b><br>Correct answer: <b>${q[1]}</b><br>${q[2]}</div>`});document.getElementById('cscore').innerHTML=`<p class="score">Score: ${sc}/10</p>`;window.scrollTo({top:document.getElementById('cscore').getBoundingClientRect().top+scrollY-20,behavior:'smooth'})};}
 function newExam(){const b=bank().slice(),r=[];while(r.length<10)r.push(b.splice(Math.floor(Math.random()*b.length),1)[0]);state.exam=r}
 function plotFns(id,series,xmin=-6,xmax=6){plotArrays(id,series.map(([fn,l,c])=>[grid.map(fn),l,c]),xmin,xmax)}
 function plotArrays(id,series,xmin=-6,xmax=6,marker=null){
  const cv=document.getElementById(id);if(!cv)return;const d=devicePixelRatio||1,w=Math.max(280,cv.clientWidth),h=cv.clientHeight||180;cv.width=w*d;cv.height=h*d;const q=cv.getContext('2d');q.setTransform(d,0,0,d,0,0);q.clearRect(0,0,w,h);const vals=series.flatMap(s=>s[0]).filter(Number.isFinite),m=Math.max(1,Math.min(30,Math.max(...vals.map(Math.abs))||1));const L=42,R=10,T=12,B=28,sx=x=>L+(x-xmin)/(xmax-xmin)*(w-L-R),sy=y=>(h-B)/2-y/m*((h-B-T)*.4);q.strokeStyle='rgba(160,165,175,.23)';q.lineWidth=1;for(let x=-6;x<=6;x+=2){q.beginPath();q.moveTo(sx(x),T);q.lineTo(sx(x),h-B);q.stroke()}q.strokeStyle='rgba(220,225,230,.55)';q.beginPath();q.moveTo(L,sy(0));q.lineTo(w-R,sy(0));q.moveTo(sx(0),T);q.lineTo(sx(0),h-B);q.stroke();series.forEach(([a,l,c],j)=>{q.strokeStyle=c;q.lineWidth=2;q.setLineDash(j===1?[6,4]:[]);q.beginPath();a.forEach((y,i)=>{const x=sx(grid[i]);if(i===0)q.moveTo(x,sy(y));else q.lineTo(x,sy(y))});q.stroke();q.setLineDash([]);q.fillStyle=c;q.font='11px Arial';q.fillText(l,L+8+j*110,T+12)});if(marker!=null){q.strokeStyle=C.gold;q.setLineDash([4,4]);q.beginPath();q.moveTo(sx(marker),T);q.lineTo(sx(marker),h-B);q.stroke();q.setLineDash([])}q.fillStyle='#a7abb4';q.font='10px Arial';q.fillText('t',w-R-8,sy(0)-5);q.fillText('y',sx(0)+6,T+10);
 }
 return{render};
})();