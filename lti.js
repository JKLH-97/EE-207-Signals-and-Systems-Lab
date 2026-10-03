const LTI = (() => {
  const state = { tab: 'concept', prefill: null, exam: null };
  const tabs = [['concept','Concept'],['linearity','Linearity Lab'],['time','Time-Invariance Lab'],['lti','LTI Lab'],['grapher','System Grapher'],['exam','Test']];
  const signals = {
    step:{label:'Unit step',tex:'u(t)',fn:t=>t>=0?1:0},
    sin:{label:'Sine',tex:'\\sin(t)',fn:t=>Math.sin(t)},
    cos2:{label:'Cosine',tex:'\\cos(2t)',fn:t=>Math.cos(2*t)},
    gauss:{label:'Gaussian',tex:'e^{-t^2}',fn:t=>Math.exp(-t*t)},
    rect:{label:'Rectangular pulse',tex:'\\operatorname{rect}(t/2)',fn:t=>Math.abs(t)<=1?1:0},
    tri:{label:'Triangular pulse',tex:'\\max(1-|t|,0)',fn:t=>Math.max(1-Math.abs(t),0)},
    decay:{label:'Decaying exponential',tex:'e^{-t}u(t)',fn:t=>t>=0?Math.exp(-t):0}
  };
  const systems = {
    gain:{label:'y(t) = 3x(t)',tex:'3x(t)',linear:true,ti:true,apply:(t,x)=>3*x(t)},
    offset:{label:'y(t) = 3x(t) + 1',tex:'3x(t)+1',linear:false,ti:true,apply:(t,x)=>3*x(t)+1},
    timegain:{label:'y(t) = t x(t)',tex:'t\\,x(t)',linear:true,ti:false,apply:(t,x)=>t*x(t)},
    reverse:{label:'y(t) = x(-t)',tex:'x(-t)',linear:true,ti:false,apply:(t,x)=>x(-t)},
    gate:{label:'y(t) = x(t)u(t)',tex:'x(t)u(t)',linear:true,ti:false,apply:(t,x)=>x(t)*(t>=0?1:0)},
    sinx:{label:'y(t) = sin[x(t)]',tex:'\\sin(x(t))',linear:false,ti:true,apply:(t,x)=>Math.sin(x(t))},
    delay:{label:'y(t) = x(t - 1)',tex:'x(t-1)',linear:true,ti:true,apply:(t,x)=>x(t-1)},
    square:{label:'y(t) = x²(t)',tex:'x^2(t)',linear:false,ti:true,apply:(t,x)=>x(t)**2},
    scale2:{label:'y(t) = 2x(t)',tex:'2x(t)',linear:true,ti:true,apply:(t,x)=>2*x(t)},
    customLTI:{label:'y(t) = 3 d/dt x(t-1) + 2x(t+2)',tex:'3\\frac{d}{dt}x(t-1)+2x(t+2)',linear:true,ti:true,apply:(t,x)=>3*deriv(x,t-1)+2*x(t+2)},
    reverseMix:{label:'y(t) = x(-t) + 2x(t)',tex:'x(-t)+2x(t)',linear:true,ti:false,apply:(t,x)=>x(-t)+2*x(t)},
    twoShift:{label:'y(t) = 2x(t-1) - x(t+2)',tex:'2x(t-1)-x(t+2)',linear:true,ti:true,apply:(t,x)=>2*x(t-1)-x(t+2)}
  };
  const T=Array.from({length:601},(_,i)=>-6+i*12/600);
  const C={blue:'#3b82f6',orange:'#f97316',green:'#22c55e',purple:'#a855f7',red:'#ef4444',cyan:'#06b6d4',gold:'#eab308',pink:'#ec4899',lime:'#84cc16',white:'#e5e7eb'};
  const deriv=(x,t)=>{const h=.003;return (x(t+h)-x(t-h))/(2*h)};
  const esc=s=>String(s).replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));
  const math=tex=>`<div class="math">${window.katex?katex.renderToString(tex,{throwOnError:false,displayMode:true}):esc(tex)}</div>`;
  const sub=s=>s.replace(/x1/g,'x₁').replace(/x2/g,'x₂').replace(/t0/g,'t₀');
  const options=(obj,selected)=>Object.entries(obj).map(([k,v])=>`<option value="${k}" ${k===selected?'selected':''}>${v.label}</option>`).join('');
  const fmt=n=>Number(n.toFixed(2)).toString();
  const signedTerm=(coef,body,first=false)=>{const n=Number(coef),a=Math.abs(n),mag=fmt(a),term=`${mag}[${body}]`;if(first)return n<0?`-${term}`:term;return n<0?`-${term}`:`+${term}`;};
  const comboTexFn=(a,x1,b,x2)=>`${signedTerm(a,x1,true)}${signedTerm(b,x2,false)}`;
  const sumTex=(a,x1,b,x2)=>`${signedTerm(a,x1,true)}${signedTerm(b,x2,false)}`;
  const shiftArg=(t0)=>{const n=Number(t0);return n<0?`t+${fmt(Math.abs(n))}`:`t-${fmt(n)}`;};
  const shiftTex=(tex,t0)=>String(tex).replace(/\bt\b/g,`(${shiftArg(t0)})`);
  const val=id=>document.getElementById(id).value;
  const text=(id,s)=>document.getElementById(id).textContent=s;
  const maxErr=(a,b)=>a.reduce((m,v,i)=>Math.max(m,Math.abs(v-b[i])),0);
  function eqLinearity(){return `<div class="lab-theory-equation">${math('T\\{a x₁(t)+b x₂(t)\\}=aT\\{x₁(t)\\}+bT\\{x₂(t)\\}')}</div>`;}
  function eqTI(){return `<div class="lab-theory-equation">${math('T\\{x(t-t₀)\\}=y(t-t₀),\\qquad y(t)=T\\{x(t)\\}')}</div>`;}
  function render(){const root=document.getElementById('lti');if(!root)return;root.innerHTML=`<div class="chapter-shell"><header class="chapter-header"><div class="chapter-title-block"><span class="chapter-number">CHAPTER 01</span><h1>LTI Systems</h1><p>Explore linearity and time invariance graphically and interactively.</p></div></header><nav class="chapter-tabs">${tabs.map(([id,l])=>`<button class="chapter-tab ${state.tab===id?'active':''}" data-tab="${id}">${l}</button>`).join('')}</nav><div class="chapter-content" id="ltiContent"></div></div>`;root.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{state.tab=b.dataset.tab;render()});renderTab();}
  function renderTab(){const c=document.getElementById('ltiContent');({concept:renderConcept,linearity:renderLinearity,time:renderTime,lti:renderLTILab,grapher:renderGrapher,exam:renderExam}[state.tab]||renderConcept)(c);}
  function renderConcept(c){const ex=[['scale2','Linear and time-invariant.'],['offset','The constant offset breaks linearity.'],['square','Scaling the input exposes nonlinearity.'],['delay','A fixed delay is LTI.'],['timegain','Explicit dependence on time breaks time invariance.'],['reverse','Time reversal is linear but time-varying.'],['twoShift','A linear combination of fixed shifts is LTI.'],['customLTI','Derivative plus fixed shifts remains LTI.'],['reverseMix','The reversal term makes the system time-varying.']];c.innerHTML=`<h2 class="section-title">What makes a system LTI?</h2><div class="grid2"><article class="panel"><h3>1. Linearity</h3><div class="math-concept">${math('T\\{a x₁(t)+b x₂(t)\\}=aT\\{x₁(t)\\}+bT\\{x₂(t)\\}')}</div><p>The order of combining/scaling and applying the system must not matter.</p></article><article class="panel"><h3>2. Time Invariance</h3><div class="math-concept">${math('T\\{x(t-t₀)\\}=y(t-t₀),\\qquad y(t)=T\\{x(t)\\}')}</div><p>The order of delaying and applying the system must not matter.</p></article></div><section class="requirement"><div class="eyebrow">LTI REQUIREMENT</div><div class="math-requirement">${math('\\mathrm{LTI}=\\mathrm{Linear}\\;\\mathbf{AND}\\;\\mathrm{Time\\! - \\!Invariant}')}</div></section><div class="eyebrow">EXPLORE</div><h2 class="section-title">Examples</h2><p class="muted">Click any example to open it directly in the LTI Lab.</p><div class="example-grid">${ex.map(([k,d],i)=>`<article class="example-card" data-example="${k}"><span class="module-number">${String(i+1).padStart(2,'0')}</span>${math(`y(t)=${systems[k].tex}`)}<p>${d}</p></article>`).join('')}</div>`;c.querySelectorAll('[data-example]').forEach(card=>card.onclick=()=>{state.prefill=card.dataset.example;state.tab='lti';render()});}
  function experimentIntro(type){return '';}
  function renderLinearity(c){
    c.innerHTML=`<h2 class="section-title">Linearity Lab</h2>${eqLinearity()}<p class="lab-prompt">Choose your experiment and investigate both superposition paths side by side.</p><div class="three-column-lab"><section class="lab-path-column"><div id="linPath1"></div></section><section class="lab-path-column"><div id="linPath2"></div></section><aside class="lab-side-controls"><h3>Experiment</h3><div class="control"><label>System</label><select id="sys">${options(systems,'gain')}</select></div><div class="control"><label>x₁(t)</label><select id="x1">${options(signals,'step')}</select></div><div class="control"><label>x₂(t)</label><select id="x2">${options(signals,'sin')}</select></div><div class="control"><label>a = <span class="range-value" id="av">2</span></label><input id="a" type="range" min="-5" max="5" step=".25" value="2"></div><div class="control"><label>b = <span class="range-value" id="bv">1</span></label><input id="b" type="range" min="-5" max="5" step=".25" value="1"></div><div id="linSub"></div></aside></div><div id="linFinal"></div>`;
    ['sys','x1','x2','a','b'].forEach(id=>document.getElementById(id).oninput=update);update();
    function update(){
      const sk=val('sys'),s1=val('x1'),s2=val('x2'),a=+val('a'),b=+val('b'),x1=signals[s1].fn,x2=signals[s2].fn,sys=systems[sk];text('av',fmt(a));text('bv',fmt(b));
      const combo=t=>a*x1(t)+b*x2(t),p1=T.map(t=>sys.apply(t,combo)),p2=T.map(t=>a*sys.apply(t,x1)+b*sys.apply(t,x2)),ct=comboTexFn(a,signals[s1].tex,b,signals[s2].tex),analysis=predefinedLinearityAnalysis(sk,a,b,s1,s2),selectedPass=analysis.selectedErr<1e-5;
      document.getElementById('linSub').innerHTML=`<div class="substitution-block compact"><h4>Current equations</h4>${math(`T\\{${ct}\\}\\;\\stackrel{?}{=}\\;${signedTerm(a,`T\\{${signals[s1].tex}\\}`,true)}${signedTerm(b,`T\\{${signals[s2].tex}\\}`,false)}`)}${math(`T\\{x(t)\\}=${systems[sk].tex}`)}</div>`;
      document.getElementById('linPath1').innerHTML=path1HTML(a,b,s1,s2,sk);
      document.getElementById('linPath2').innerHTML=path2HTML(a,b,s1,s2,sk);
      document.getElementById('linFinal').innerHTML=`<section class="final-comparison compact-final"><h3>Final comparison</h3>${math(`y_{P1}(t)\\;\\stackrel{?}{=}\\;y_{P2}(t)`)}<div class="plot-card wide-plot"><canvas id="lp7"></canvas></div><div class="analysis-note"><b>Selected experiment:</b> ${selectedPass?'Both paths match for these particular inputs and coefficients.':'The two paths differ, so this experiment is a counterexample to linearity.'}</div><div class="zero-test"><h4>Necessary zero-input test</h4>${math(`T\\{0\\}\\;\\stackrel{?}{=}\\;0`)}<p>${analysis.t0err<1e-5?'This necessary condition is satisfied.':'Here T{0} is not zero, so the system cannot be linear.'}</p></div><div class="analysis-reason">${analysis.reason}</div><div class="status-banner ${analysis.linear?'match':'mismatch'}">${analysis.linear?'The system is LINEAR':'The system is NONLINEAR'}</div></section>`;
      plot('lp1',[[x1,'x₁(t)',C.blue],[t=>a*x1(t),`${fmt(a)}x₁(t)`,C.red]]);plot('lp2',[[x2,'x₂(t)',C.green],[t=>b*x2(t),`${fmt(b)}x₂(t)`,C.purple]]);plot('lp3',[[combo,'v(t)',C.gold]]);plotArray('lp4',[[p1,'yP1(t)',C.cyan]]);plot('lp5',[[t=>sys.apply(t,x1),'T{x₁}',C.blue],[t=>a*sys.apply(t,x1),`${fmt(a)}T{x₁}`,C.red]]);plot('lp6',[[t=>sys.apply(t,x2),'T{x₂}',C.green],[t=>b*sys.apply(t,x2),`${fmt(b)}T{x₂}`,C.purple]]);plotArray('lp8',[[p2,'yP2(t)',C.gold]]);plotArray('lp7',[[p1,'yP1(t)',C.cyan],[p2,'yP2(t)',C.gold]],true);
    }
  }
  function path1HTML(a,b,s1,s2,sk){const ct=comboTexFn(a,signals[s1].tex,b,signals[s2].tex);return `<section class="path-section"><h3 class="step-heading">Path 1 — Scale and add the inputs first, then apply the system</h3><div class="path-lead-equation">${math(`y_{P1}(t)=T\\{${ct}\\}`)}</div><div class="plot-grid"><div class="plot-card"><h4>Step 1 — Scale x₁(t)</h4>${math(`${fmt(a)}x_1(t)=${fmt(a)}[${signals[s1].tex}]`)}<canvas id="lp1"></canvas></div><div class="plot-card"><h4>Step 2 — Scale x₂(t)</h4>${math(`${fmt(b)}x_2(t)=${fmt(b)}[${signals[s2].tex}]`)}<canvas id="lp2"></canvas></div><div class="plot-card"><h4>Step 3 — Add the scaled inputs</h4>${math(`v(t)=${ct}`)}<canvas id="lp3"></canvas></div><div class="plot-card"><h4>Step 4 — Apply the system to v(t)</h4>${math(`y_{P1}(t)=T\\{v(t)\\},\\quad T\\{x(t)\\}=${systems[sk].tex}`)}<canvas id="lp4"></canvas></div></div><div class="path-result">${math(`\\boxed{y_{P1}(t)=T\\{${ct}\\}}`)}</div></section>`;}
  function path2HTML(a,b,s1,s2,sk){const rhs=`${signedTerm(a,`T\\{${signals[s1].tex}\\}`,true)}${signedTerm(b,`T\\{${signals[s2].tex}\\}`,false)}`;return `<section class="path-section"><h3 class="step-heading">Path 2 — Apply the system first, then scale and add the outputs</h3><div class="path-lead-equation">${math(`y_{P2}(t)=${rhs}`)}</div><div class="plot-grid"><div class="plot-card"><h4>Step 1 — Apply T{·} to x₁(t), then scale</h4>${math(`${fmt(a)}T\\{${signals[s1].tex}\\},\\quad T\\{x(t)\\}=${systems[sk].tex}`)}<canvas id="lp5"></canvas></div><div class="plot-card"><h4>Step 2 — Apply T{·} to x₂(t), then scale</h4>${math(`${fmt(b)}T\\{${signals[s2].tex}\\},\\quad T\\{x(t)\\}=${systems[sk].tex}`)}<canvas id="lp6"></canvas></div><div class="plot-card wide-plot"><h4>Step 3 — Add the two scaled outputs</h4>${math(`y_{P2}(t)=${rhs}`)}<canvas id="lp8"></canvas></div></div><div class="path-result">${math(`\\boxed{y_{P2}(t)=${rhs}}`)}</div></section>`;}
  function renderTime(c){
    c.innerHTML=`<h2 class="section-title">Time-Invariance Lab</h2>${eqTI()}<p class="lab-prompt">Choose your experiment and compare both time-shift paths side by side.</p><div class="three-column-lab"><section class="lab-path-column"><div id="tiPath1"></div></section><section class="lab-path-column"><div id="tiPath2"></div></section><aside class="lab-side-controls"><h3>Experiment</h3><div class="control"><label>System</label><select id="sys">${options(systems,'gain')}</select></div><div class="control"><label>x(t)</label><select id="x">${options(signals,'step')}</select></div><div class="control"><label>Delay t₀ = <span class="range-value" id="tv">2</span></label><input id="t0" type="range" min="-5" max="5" step=".25" value="2"></div><div id="tiSub"></div></aside></div><div id="tiFinal"></div>`;
    ['sys','x','t0'].forEach(id=>document.getElementById(id).oninput=update);update();
    function update(){
      const sk=val('sys'),sys=systems[sk],sig=val('x'),x=signals[sig].fn,t0=+val('t0');text('tv',fmt(t0));
      const xd=t=>x(t-t0),y=t=>sys.apply(t,x),p1=T.map(t=>sys.apply(t,xd)),p2=T.map(t=>y(t-t0)),analysis=predefinedTIAnalysis(sk,sig,t0),arg=shiftArg(t0),shifted=shiftTex(signals[sig].tex,t0);
      document.getElementById('tiSub').innerHTML=`<div class="substitution-block compact"><h4>Current equations</h4>${math(`x(t)=${signals[sig].tex}`)}${math(`T\\{x(t)\\}=${systems[sk].tex}`)}${math(`t_0=${fmt(t0)}`)}</div>`;
      document.getElementById('tiPath1').innerHTML=`<section class="path-section dashboard-path"><h3 class="step-heading">Path 1 — Delay the input first, then apply the system</h3><div class="path-lead-equation">${math(`y_{P1}(t)=T\\{x(${arg})\\}`)}</div><div class="plot-card"><h4>Step 1 — Delay x(t)</h4>${math(`x(${arg})=${shifted}`)}<canvas id="tp1"></canvas></div><div class="plot-card"><h4>Step 2 — Apply the system</h4>${math(`y_{P1}(t)=T\\{x(${arg})\\}`)}<canvas id="tp2"></canvas></div><div class="path-result">${math(`\\boxed{y_{P1}(t)=T\\{x(${arg})\\}}`)}</div></section>`;
      document.getElementById('tiPath2').innerHTML=`<section class="path-section dashboard-path"><h3 class="step-heading">Path 2 — Apply the system first, then delay the output</h3><div class="path-lead-equation">${math(`y(t)=T\\{x(t)\\},\\qquad y_{P2}(t)=y(${arg})`)}</div><div class="plot-card"><h4>Step 1 — Apply the system to x(t)</h4>${math(`y(t)=T\\{${signals[sig].tex}\\}`)}<canvas id="tp3"></canvas></div><div class="plot-card"><h4>Step 2 — Delay y(t)</h4>${math(`y_{P2}(t)=y(${arg})`)}<canvas id="tp4"></canvas></div><div class="path-result">${math(`\\boxed{y_{P2}(t)=y(${arg})}`)}</div></section>`;
      document.getElementById('tiFinal').innerHTML=`<section class="final-comparison compact-final"><h3>Final comparison</h3><div class="plot-card wide-plot"><canvas id="tp5"></canvas></div><div class="analysis-note"><b>Selected experiment:</b> ${analysis.selectedErr<1e-5?'Both paths match for this selected input and shift.':'The two paths differ, providing a counterexample.'}</div><div class="analysis-reason">${analysis.reason}</div><div class="status-banner ${analysis.ti?'match':'mismatch'}">${analysis.ti?'The system is TIME-INVARIANT':'The system is TIME-VARYING'}</div></section>`;
      plot('tp1',[[x,'x(t)',C.blue],[xd,`x(${arg})`,C.orange]]);plotArray('tp2',[[p1,'yP1(t)',C.red]]);plot('tp3',[[y,'y(t)',C.green]]);plotArray('tp4',[[p2,'yP2(t)',C.purple]]);plotArray('tp5',[[p1,'yP1(t)',C.red],[p2,'yP2(t)',C.purple]],true);
    }
  }
  function applyTex(sk,inputTex){
    const z=`\\left[${inputTex}\\right]`;
    const map={
      gain:`3${z}`,offset:`3${z}+1`,timegain:`t${z}`,reverse:`${z.replaceAll('t','-t')}`,
      gate:`${z}u(t)`,sinx:`\\sin${z}`,delay:`${z}\\big|_{t\\to t-1}`,square:`${z}^{2}`,
      scale2:`2${z}`,customLTI:`3\\frac{d}{dt}${z}\\big|_{t\\to t-1}+2${z}\\big|_{t\\to t+2}`,
      reverseMix:`${z.replaceAll('t','-t')}+2${z}`,twoShift:`2${z}\\big|_{t\\to t-1}-${z}\\big|_{t\\to t+2}`
    };
    return map[sk]||`T\\{${inputTex}\\}`;
  }
  function renderLTILab(c){
    const def=state.prefill||'gain';state.prefill=null;
    c.innerHTML=`<h2 class="section-title">LTI Lab</h2><p class="muted">Observe the linearity and time-invariance tests together.</p><div class="lti-dashboard"><div class="lti-visual-area"><div class="dual-test-grid"><section class="compact-test-panel"><h3>Linearity</h3>${eqLinearity()}<div class="plot-card"><h4>Inputs and combination</h4><canvas id="lc0"></canvas></div><div class="plot-card"><h4>Path outputs</h4><canvas id="lc1"></canvas></div><div id="linCompact"></div></section><section class="compact-test-panel"><h3>Time Invariance</h3>${eqTI()}<div class="plot-card"><h4>Original and delayed input</h4><canvas id="lc3"></canvas></div><div class="plot-card"><h4>Path outputs</h4><canvas id="lc2"></canvas></div><div id="tiCompact"></div></section></div><div id="ltiOverall"></div></div><aside class="lti-side-controls"><h3>Experiment</h3><div class="control"><label>System</label><select id="lsys">${options(systems,def)}</select></div><div class="control"><label>x₁(t)</label><select id="lx1">${options(signals,'step')}</select></div><div class="control"><label>x₂(t)</label><select id="lx2">${options(signals,'sin')}</select></div><div class="control"><label>a = <span id="lav" class="range-value">2</span></label><input id="la" type="range" min="-5" max="5" step=".25" value="2"></div><div class="control"><label>b = <span id="lbv" class="range-value">1</span></label><input id="lb" type="range" min="-5" max="5" step=".25" value="1"></div><div class="control"><label>t₀ = <span id="ltv" class="range-value">2</span></label><input id="lt0" type="range" min="-5" max="5" step=".25" value="2"></div></aside></div>`;
    ['lsys','lx1','lx2','la','lb','lt0'].forEach(id=>document.getElementById(id).oninput=update);update();
    function update(){
      const sk=val('lsys'),sys=systems[sk],s1=val('lx1'),s2=val('lx2'),x1=signals[s1].fn,x2=signals[s2].fn,a=+val('la'),b=+val('lb'),t0=+val('lt0');text('lav',fmt(a));text('lbv',fmt(b));text('ltv',fmt(t0));
      const combo=t=>a*x1(t)+b*x2(t),l1=T.map(t=>sys.apply(t,combo)),l2=T.map(t=>a*sys.apply(t,x1)+b*sys.apply(t,x2)),xd=t=>x1(t-t0),y=t=>sys.apply(t,x1),q1=T.map(t=>sys.apply(t,xd)),q2=T.map(t=>y(t-t0));
      const comboTex=comboTexFn(a,signals[s1].tex,b,signals[s2].tex),linLeft=applyTex(sk,comboTex),linRight=`${signedTerm(a,applyTex(sk,signals[s1].tex),true)}${signedTerm(b,applyTex(sk,signals[s2].tex),false)}`,delayedTex=shiftTex(signals[s1].tex,t0),tiLeft=applyTex(sk,delayedTex),tiRight=shiftTex(applyTex(sk,signals[s1].tex),t0);
      const laa=predefinedLinearityAnalysis(sk,a,b,s1,s2),tia=predefinedTIAnalysis(sk,s1,t0);
      document.getElementById('linCompact').innerHTML=`<div class="compact-equations">${math(`T\\{${comboTex}\\}\\;\\stackrel{?}{=}\\;${signedTerm(a,`T\\{${signals[s1].tex}\\}`,true)}${signedTerm(b,`T\\{${signals[s2].tex}\\}`,false)}`)}${math(`y_{P1}(t)=${linLeft}`)}${math(`y_{P2}(t)=${linRight}`)}</div><div class="analysis-note compact"><b>Selected experiment:</b> ${laa.selectedErr<1e-4?'passes':'fails'} the displayed equality.</div>${!sys.linear?`<div class="zero-test compact"><b>Analytical check:</b> ${laa.t0err>1e-5?'T{0} ≠ 0, so the system is nonlinear.':'Another valid superposition choice provides a counterexample.'}</div>`:''}<div class="status-banner ${sys.linear?'match':'mismatch'}">${sys.linear?'The system is LINEAR':'The system is NONLINEAR'}</div>`;
      document.getElementById('tiCompact').innerHTML=`<div class="compact-equations">${math(`T\\{x(${shiftArg(t0)})\\}\\;\\stackrel{?}{=}\\;y(${shiftArg(t0)})`)}${math(`y_{P1}(t)=${tiLeft}`)}${math(`y_{P2}(t)=${tiRight}`)}</div><div class="analysis-note compact"><b>Selected experiment:</b> ${tia.selectedErr<1e-4?'passes':'fails'} the displayed time-shift equality.</div><div class="status-banner ${sys.ti?'match':'mismatch'}">${sys.ti?'The system is TIME-INVARIANT':'The system is TIME-VARYING'}</div>`;
      document.getElementById('ltiOverall').innerHTML=`<div class="status-banner overall ${sys.linear&&sys.ti?'match':'mismatch'}">${sys.linear&&sys.ti?'The system is LTI':'The system is NOT LTI'}</div>`;
      plot('lc0',[[x1,'x₁',C.blue],[x2,'x₂',C.green],[combo,'ax₁+bx₂',C.gold]]);plotArray('lc1',[[l1,'yP1(t)',C.red],[l2,'yP2(t)',C.cyan]],true);plot('lc3',[[x1,'x(t)',C.blue],[xd,'x(t−t₀)',C.orange]]);plotArray('lc2',[[q1,'yP1(t)',C.red],[q2,'yP2(t)',C.purple]],true);
    }
  }
  function expressionToTex(expr,system=false){
    let z=String(expr).trim();
    z=z.replace(/²/g,'^2').replace(/³/g,'^3');
    z=z.replace(/dx\/dt/g,'§DERIV§').replace(/int\(x\)/g,'§INTEGRAL§');
    if(system) z=z.replace(/\bx\b/g,'x(t)');
    z=z.replace(/\*/g,'\\,').replace(/\bpi\b/g,'\\pi');
    z=z.replace(/sqrt\(([^()]*)\)/g,'\\sqrt{$1}');
    z=z.replace(/exp\(([^()]*)\)/g,'e^{$1}');
    z=z.replace(/sin\(([^()]*)\)/g,'\\sin($1)').replace(/cos\(([^()]*)\)/g,'\\cos($1)');
    z=z.replace(/abs\(([^()]*)\)/g,'\\left|$1\\right|');
    z=z.replace(/u\(([^()]*)\)/g,'u($1)');
    z=z.replace(/\^\(([^()]*)\)/g,'^{$1}').replace(/\^([0-9A-Za-z.+-]+)/g,'^{$1}');
    z=z.replace(/§DERIV§/g,'\\frac{d x(t)}{dt}').replace(/§INTEGRAL§/g,'\\int_{-\\infty}^{t}x(\\tau)\\,d\\tau');
    return z;
  }
  /* ---------------------------------------------------------
     SYSTEM GRAPHER CLASSIFICATION

     A finite numerical experiment can DISPROVE a property, but
     passing finitely many tests does not prove it.  For expressions
     in the supported EE-207 grammar we therefore combine:
       1) structural/analytical checks, and
       2) numerical counterexample searches.
     --------------------------------------------------------- */
  function numericalCounterexampleSearch(apply){
    const tests=[signals.step.fn,signals.sin.fn,signals.gauss.fn,signals.rect.fn,signals.decay.fn];
    const pairs=[[1,1],[2,.5],[-1,2],[.5,-1.5],[2,2],[-2,-3]];
    const zero=t=>0;
    let linErr=Math.max(...T.map(t=>Math.abs(apply(t,zero))));
    for(let i=0;i<tests.length-1;i++){
      for(const [a,b] of pairs){
        const x1=tests[i],x2=tests[i+1],mix=t=>a*x1(t)+b*x2(t);
        const l=T.map(t=>apply(t,mix));
        const r=T.map(t=>a*apply(t,x1)+b*apply(t,x2));
        linErr=Math.max(linErr,maxErr(l,r));
      }
    }
    let tiErr=0;
    for(const x of tests){
      for(const d of [1,-2,2.5,-3.25]){
        const xd=t=>x(t-d),y=t=>apply(t,x);
        const l=T.map(t=>apply(t,xd)),r=T.map(t=>y(t-d));
        tiErr=Math.max(tiErr,maxErr(l,r));
      }
    }
    return {linFail:linErr>1e-4,tiFail:tiErr>1e-4,linErr,tiErr};
  }

  function splitAdditiveTerms(expr){
    let s=expr.replace(/\s+/g,'').replace(/-/g,'+-');
    if(s.startsWith('+-'))s='-'+s.slice(2);
    return s.split('+').filter(Boolean);
  }

  function isNumericToken(s){return /^[-+]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(s);}

  function isLinearInputTerm(term){
    let z=term.replace(/^\+/,'');
    if(z.startsWith('-'))z=z.slice(1);
    // Supported linear input primitives. dxdt and intx represent
    // d x(t)/dt and the accumulated integral respectively.
    const primitive='(?:x|dxdt|intx)';
    if(new RegExp(`^${primitive}$`).test(z))return true;
    if(new RegExp(`^(?:\\d+(?:\\.\\d*)?|\\.\\d+)\\*${primitive}$`).test(z))return true;
    if(new RegExp(`^${primitive}\\*(?:\\d+(?:\\.\\d*)?|\\.\\d+)$`).test(z))return true;
    if(new RegExp(`^${primitive}\\/(?:\\d+(?:\\.\\d*)?|\\.\\d+)$`).test(z))return true;
    return false;
  }

  function analyticalClassifyExpression(expr,apply){
    const raw=String(expr).trim();
    const s=raw.replace(/\s+/g,'').replace(/\^/g,'**')
      .replace(/dx\/dt/g,'dxdt').replace(/int\(x\)/g,'intx');
    const num=numericalCounterexampleSearch(apply);
    const hasInput=/\b(?:x|dxdt|intx)\b/.test(s);
    const hasExplicitTime=/\bt\b/.test(s);
    const nonlinearFunction=/(?:sin|cos|exp|abs|sqrt)\([^)]*(?:\bx\b|\bdxdt\b|\bintx\b)[^)]*\)/.test(s);
    const nonlinearPower=/(?:\bx\b|\bdxdt\b|\bintx\b)\s*\*\*\s*(?!1(?:\D|$))/.test(s);
    const inputProduct=/(?:\bx\b|\bdxdt\b|\bintx\b)\s*\*\s*(?:\bx\b|\bdxdt\b|\bintx\b)/.test(s);
    const inputDenominator=/\/[^+\-]*(?:\bx\b|\bdxdt\b|\bintx\b)/.test(s);
    const terms=splitAdditiveTerms(s);
    const constants=terms.filter(t=>isNumericToken(t));
    const allTermsLinear=terms.length>0 && terms.every(t=>isNumericToken(t)||isLinearInputTerm(t));

    let linear=null,linearReason='';
    if(num.linFail){
      linear=false;
      linearReason='A counterexample was found: the superposition equality fails for at least one internal test.';
    }else if(constants.some(t=>Math.abs(Number(t))>1e-12)){
      linear=false;
      linearReason='The expression contains a nonzero additive constant, so T{0} ≠ 0.';
    }else if(nonlinearFunction||nonlinearPower||inputProduct||inputDenominator){
      linear=false;
      linearReason='The input appears inside a nonlinear operation, so superposition is not satisfied in general.';
    }else if(allTermsLinear && !hasExplicitTime){
      linear=true;
      linearReason='The expression is a linear combination of supported linear input operations with constant coefficients.';
    }else if(allTermsLinear && hasExplicitTime){
      // t is not an allowed constant coefficient in our proof grammar.
      linear=null;
      linearReason='The numerical tests pass, but this expression is outside the current analytical linearity proof grammar.';
    }else if(!hasInput){
      linear=false;
      linearReason='The output is not a homogeneous linear function of the input.';
    }else{
      linear=null;
      linearReason='No counterexample was found, but finite numerical tests alone cannot prove linearity for this expression.';
    }

    let ti=null,tiReason='';
    if(num.tiFail){
      ti=false;
      tiReason='A time-shift counterexample was found: delaying before and after the system gives different outputs.';
    }else if(!hasExplicitTime){
      ti=true;
      tiReason='The supported expression has no explicit dependence on absolute time; the numerical shift tests also agree.';
    }else{
      ti=null;
      tiReason='The expression contains explicit t. No finite numerical test can by itself prove time invariance; analytical classification is not asserted.';
    }

    return {linear,ti,linearReason,tiReason,...num};
  }

  function classificationWord(v,yes,no){return v===true?yes:v===false?no:'NOT PROVEN';}
  function predefinedLinearityAnalysis(sk,a,b,s1,s2){
    const sys=systems[sk],zero=t=>0,t0vals=T.map(t=>sys.apply(t,zero)),t0err=Math.max(...t0vals.map(Math.abs));
    const x1=signals[s1].fn,x2=signals[s2].fn,combo=t=>a*x1(t)+b*x2(t);
    const p1=T.map(t=>sys.apply(t,combo)),p2=T.map(t=>a*sys.apply(t,x1)+b*sys.apply(t,x2));
    const selectedErr=maxErr(p1,p2);
    let reason='';
    if(!sys.linear && t0err>1e-5){
      reason=`This selected experiment can pass for special coefficients, but that does not prove linearity. The system fails the necessary zero-input test T{0}=0, so it is nonlinear in general.`;
    }else if(!sys.linear){
      reason=`This selected experiment can pass for special inputs or coefficients. However, another valid superposition choice fails, so the system is nonlinear in general.`;
    }else{
      reason=`The system is analytically linear. It satisfies superposition for arbitrary valid inputs and coefficients, including the zero-input condition T{0}=0.`;
    }
    return {selectedErr,t0err,linear:sys.linear,reason};
  }
  function predefinedTIAnalysis(sk,sig,t0){
    const sys=systems[sk],x=signals[sig].fn,xd=t=>x(t-t0),y=t=>sys.apply(t,x);
    const p1=T.map(t=>sys.apply(t,xd)),p2=T.map(t=>y(t-t0)),selectedErr=maxErr(p1,p2);
    return {selectedErr,ti:sys.ti,reason:sys.ti
      ?`The system is analytically time-invariant: delaying the input and delaying the output produce the same result for arbitrary valid shifts.`
      :`This system is analytically time-varying. A particular numerical experiment may pass accidentally, but another valid time shift/input provides a counterexample.`};
  }

  function renderGrapher(c){
    c.innerHTML=`<h2 class="section-title">System Grapher — Build Your Own Experiment</h2><div class="grapher-dashboard"><div class="grapher-main"><div class="grapher-help">Use <b>t</b> for time and <b>x</b> for the current input. Supported functions: sin(), cos(), exp(), abs(), sqrt(), u(). For systems you may also use <b>dx/dt</b> and <b>int(x)</b>.</div><div id="gout"><div class="lab-placeholder"><span>INTERACTIVE GRAPHER</span><h2>Define your experiment</h2><p>The linearity and time-invariance views will appear side by side.</p></div></div></div><aside class="grapher-side-controls"><h3>Experiment</h3><div class="control"><label>System y(t) =</label><input id="gsys" type="text" value="3*x"><div class="live-equation" id="gsysPreview"></div></div><div class="control"><label>x₁(t) =</label><input id="gx1" type="text" value="u(t)"><div class="live-equation" id="gx1Preview"></div></div><div class="control"><label>x₂(t) =</label><input id="gx2" type="text" value="sin(t)"><div class="live-equation" id="gx2Preview"></div></div><div class="control"><label>a</label><input id="ga" type="number" value="2" step=".25"></div><div class="control"><label>b</label><input id="gb" type="number" value="1" step=".25"></div><div class="control"><label>t₀</label><input id="gt0" type="number" value="2" step=".25"></div><button class="btn" id="graphBtn">Graph experiment</button></aside></div>`;
    const preview=()=>{document.getElementById('gsysPreview').innerHTML=math(`y(t)=${expressionToTex(val('gsys'),true)}`);document.getElementById('gx1Preview').innerHTML=math(`x_1(t)=${expressionToTex(val('gx1'))}`);document.getElementById('gx2Preview').innerHTML=math(`x_2(t)=${expressionToTex(val('gx2'))}`);};
    ['gsys','gx1','gx2'].forEach(id=>document.getElementById(id).addEventListener('input',preview));preview();
    const runGraph=()=>{try{
      const se=val('gsys'),e1=val('gx1'),e2=val('gx2'),a=+val('ga'),b=+val('gb'),t0=+val('gt0'),x1=t=>evalSignal(e1,t),x2=t=>evalSignal(e2,t),apply=(t,xfn)=>evalSystem(se,t,xfn),combo=t=>a*x1(t)+b*x2(t),p1=T.map(t=>apply(t,combo)),p2=T.map(t=>a*apply(t,x1)+b*apply(t,x2)),xd=t=>x1(t-t0),y=t=>apply(t,x1),q1=T.map(t=>apply(t,xd)),q2=T.map(t=>y(t-t0)),le=maxErr(p1,p2),te=maxErr(q1,q2),classification=analyticalClassifyExpression(se,apply),isLTI=classification.linear===true&&classification.ti===true,knownLTI=classification.linear!==null&&classification.ti!==null;
      document.getElementById('gout').innerHTML=`<div class="dual-test-grid grapher-tests"><section class="compact-test-panel"><h3>Linearity</h3><div class="plot-card"><h4>Inputs and combination</h4><canvas id="gc0"></canvas></div><div class="plot-card"><h4>Path outputs</h4><canvas id="gc1"></canvas></div><div class="compact-equations">${math(`T\\{${comboTexFn(a,expressionToTex(e1),b,expressionToTex(e2))}\\}\\;\\stackrel{?}{=}\\;${signedTerm(a,`T\\{${expressionToTex(e1)}\\}`,true)}${signedTerm(b,`T\\{${expressionToTex(e2)}\\}`,false)}`)}${math(`y_{P1}(t)\\;\\stackrel{?}{=}\\;y_{P2}(t)`)}</div><div class="analysis-note compact"><b>Visual experiment:</b> ${le<1e-4?'passes for the selected inputs and coefficients; this alone does not prove linearity.':'fails and therefore provides a counterexample.'}</div><div class="status-banner ${classification.linear===true?'match':classification.linear===false?'mismatch':'uncertain'}">${classificationWord(classification.linear,'The system is LINEAR','The system is NONLINEAR')}</div><div class="analysis-reason">${classification.linearReason}</div></section><section class="compact-test-panel"><h3>Time Invariance</h3><div class="plot-card"><h4>Original and delayed input</h4><canvas id="gc3"></canvas></div><div class="plot-card"><h4>Path outputs</h4><canvas id="gc2"></canvas></div><div class="compact-equations">${math(`T\\{x(${shiftArg(t0)})\\}\\;\\stackrel{?}{=}\\;y(${shiftArg(t0)})`)}${math(`y_{P1}(t)\\;\\stackrel{?}{=}\\;y_{P2}(t)`)}</div><div class="analysis-note compact"><b>Visual experiment:</b> ${te<1e-4?'passes for the selected shift; this alone does not prove time invariance.':'fails and therefore provides a counterexample.'}</div><div class="status-banner ${classification.ti===true?'match':classification.ti===false?'mismatch':'uncertain'}">${classificationWord(classification.ti,'The system is TIME-INVARIANT','The system is TIME-VARYING')}</div><div class="analysis-reason">${classification.tiReason}</div></section></div><div class="status-banner overall ${knownLTI?(isLTI?'match':'mismatch'):'uncertain'}">${knownLTI?(isLTI?'The system is LTI':'The system is NOT LTI'):'LTI classification is NOT PROVEN for this expression'}</div>`;
      plot('gc0',[[x1,'x₁',C.blue],[x2,'x₂',C.green],[combo,'ax₁+bx₂',C.gold]]);plotArray('gc1',[[p1,'yP1(t)',C.red],[p2,'yP2(t)',C.cyan]],true);plot('gc3',[[x1,'x(t)',C.blue],[xd,'x(t−t₀)',C.orange]]);plotArray('gc2',[[q1,'yP1(t)',C.red],[q2,'yP2(t)',C.purple]],true);
    }catch(e){document.getElementById('gout').innerHTML=`<div class="status-banner mismatch">Check the expression format.</div>`;}};
    document.getElementById('graphBtn').onclick=runGraph;
    ['gsys','gx1','gx2','ga','gb','gt0'].forEach(id=>document.getElementById(id).addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();runGraph();}}));
    runGraph();
  }
  function buildBank(){const b=[];const add=(system,answer,why)=>b.push({system,answer,why});Object.values(systems).forEach(s=>add(s.label,s.linear&&s.ti?'LTI':s.linear?'Linear but time-varying':s.ti?'Nonlinear but time-invariant':'Neither linear nor time-invariant',explain(s)));[-4,-2,.5,4,7].forEach(k=>add(`y(t) = ${k}x(t)`,'LTI','A constant gain satisfies superposition and does not explicitly depend on time.'));[2,3,4,5].forEach(k=>add(`y(t) = x(t-${k})`,'LTI','A fixed delay is linear and time-invariant.'));['x²(t)','|x(t)|','sin(x(t))','x(t)+2','2x(t)+5'].forEach(q=>add(`y(t) = ${q}`,'Nonlinear but time-invariant','The pointwise nonlinear/offset operation breaks superposition but has no explicit dependence on time.'));['t x(t)','(t+2)x(t)','sin(t)x(t)','x(-t)','x(t)u(t)'].forEach(q=>add(`y(t) = ${q}`,'Linear but time-varying','The operation is linear in the input but changes under a time shift.'));for(let i=0;i<10;i++)add(`y(t) = ${i+1}x(t-${(i%3)+1}) - x(t+${(i%2)+1})`,'LTI','A linear combination of fixed shifts with constant coefficients is LTI.');for(let i=0;i<8;i++)add(`y(t) = x(t) + ${i+1}`,'Nonlinear but time-invariant','The nonzero additive constant violates T{0}=0.');while(b.length<50)add(`y(t) = ${b.length-20}x(t)`,'LTI','Constant gain is linear and time-invariant.');return b.slice(0,50);}
  function explain(s){if(s.linear&&s.ti)return 'It satisfies superposition and commutes with a time shift.';if(!s.linear&&s.ti)return 'It violates superposition, but the rule itself does not change with time.';if(s.linear&&!s.ti)return 'It is linear in the input, but a time shift changes the operation.';return 'It violates both required LTI properties.';}
  function renderExam(c){if(!state.exam)generateExam();c.innerHTML=`<div class="exam-toolbar"><div><h2 class="section-title" style="margin-bottom:4px">LTI Test</h2><p class="muted">10 questions are selected from an internal bank of 50 questions.</p><div id="score" class="score-top"></div></div><button class="btn" id="newExam">Generate new test</button></div><div id="questions">${state.exam.map((q,i)=>`<article class="exam-card"><h3>${i+1}. Classify the system:</h3>${math(expressionToTex(q.system,true))}<div class="answers">${['LTI','Linear but time-varying','Nonlinear but time-invariant','Neither linear nor time-invariant'].map(a=>`<label class="answer"><input type="radio" name="q${i}" value="${a}"> <span>${a}</span></label>`).join('')}</div><div id="fb${i}"></div></article>`).join('')}</div><button class="btn" id="grade">Grade test</button>`;document.getElementById('newExam').onclick=()=>{generateExam();renderExam(c)};document.getElementById('grade').onclick=()=>{let score=0;state.exam.forEach((q,i)=>{const a=document.querySelector(`input[name=q${i}]:checked`)?.value,ok=a===q.answer;if(ok)score++;document.getElementById(`fb${i}`).innerHTML=`<div class="feedback ${ok?'correct':'incorrect'}"><b>${ok?'✓ CORRECT':'✗ INCORRECT'}</b><br>Your answer: ${a||'No answer'}<br>Correct answer: <b>${q.answer}</b><br>${q.why}</div>`;});document.getElementById('score').innerHTML=`<p class="score">Score: ${score}/10</p>`;window.scrollTo({top:document.getElementById('score').getBoundingClientRect().top+window.scrollY-24,behavior:'smooth'});};}
  function generateExam(){const copy=[...buildBank()];state.exam=[];while(state.exam.length<10)state.exam.push(copy.splice(Math.floor(Math.random()*copy.length),1)[0]);}
  function plot(id,series){plotArray(id,series.map(([fn,l,c])=>[T.map(fn),l,c]));}
  function plotArray(id,series,dashedSecond=false){const canvas=document.getElementById(id);if(!canvas)return;const r=devicePixelRatio||1,w=Math.max(300,canvas.clientWidth),h=canvas.clientHeight||205;canvas.width=w*r;canvas.height=h*r;const q=canvas.getContext('2d');q.setTransform(r,0,0,r,0,0);q.clearRect(0,0,w,h);const vals=series.flatMap(s=>s[0]).filter(Number.isFinite),m=Math.max(1,Math.min(50,Math.max(...vals.map(Math.abs))||1));const L=48,R=14,TOP=15,BOT=31,sx=t=>L+(t+6)/12*(w-L-R),sy=y=>(h-BOT)/2-y/m*((h-BOT-TOP)*.38);q.strokeStyle='rgba(150,150,160,.25)';q.lineWidth=1;for(let t=-6;t<=6;t+=2){const x=sx(t);q.beginPath();q.moveTo(x,TOP);q.lineTo(x,h-BOT);q.stroke();q.fillStyle='#8f929b';q.font='10px Arial';q.fillText(t,x-5,h-15);}for(let y=-m;y<=m+.001;y+=m/2){const yy=sy(y);q.beginPath();q.moveTo(L,yy);q.lineTo(w-R,yy);q.stroke();q.fillStyle='#8f929b';q.fillText(fmt(y),4,yy+3);}q.strokeStyle='#a6a8b0';q.lineWidth=1.2;q.beginPath();q.moveTo(L,sy(0));q.lineTo(w-R,sy(0));q.stroke();q.beginPath();q.moveTo(sx(0),TOP);q.lineTo(sx(0),h-BOT);q.stroke();q.fillStyle='#c7c9cf';q.font='12px Arial';q.fillText('t',w-12,sy(0)-6);q.fillText('y',sx(0)+7,12);series.forEach((s,j)=>{q.strokeStyle=s[2];q.lineWidth=2.2;q.setLineDash(dashedSecond&&j===1?[6,4]:[]);q.beginPath();s[0].forEach((y,i)=>{const x=sx(T[i]),yy=sy(Math.max(-m*1.25,Math.min(m*1.25,y)));i?q.lineTo(x,yy):q.moveTo(x,yy);});q.stroke();q.setLineDash([]);});let lx=L+6;series.forEach(s=>{q.fillStyle=s[2];q.fillRect(lx,8,14,3);q.fillStyle='#c7c9cf';q.font='10px Arial';q.fillText(s[1],lx+19,12);lx+=Math.min(150,30+s[1].length*6);});}
  function evalSignal(expr,t){return safeEval(expr,{t});}function integralOf(x,t){const lo=-6;if(t<=lo)return 0;const n=160,h=(t-lo)/n;let sum=.5*(x(lo)+x(t));for(let i=1;i<n;i++)sum+=x(lo+i*h);return sum*h;}function evalSystem(expr,t,xfn){let s=expr.replace(/dx\/dt/g,'dxdt').replace(/int\(x\)/g,'intx');return safeEval(s,{t,x:xfn(t),dxdt:deriv(xfn,t),intx:integralOf(xfn,t)});}function safeEval(expr,vars){let s=expr.replaceAll('^','**');if(!/^[0-9A-Za-z_+\-*/().,\s*]+$/.test(s)||s.includes('__'))throw Error();const env={...vars,sin:Math.sin,cos:Math.cos,exp:Math.exp,abs:Math.abs,sqrt:Math.sqrt,u:z=>z>=0?1:0,pi:Math.PI};return Function(...Object.keys(env),`"use strict"; return (${s});`)(...Object.values(env));}
  return {render};
})();
window.LTI=LTI;
