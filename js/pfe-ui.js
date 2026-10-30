window.EE207PFELab=(function(){
const E=window.EE207PFE;
const examples=[
['1. Distinct real poles','(5*s+7)/((s+1)*(s+2))'],
['2. Repeated real pole','(2*s+3)/(s+1)^2'],
['3. Complex-conjugate poles','(s+2)/(s^2+2*s+5)'],
['4. Real and complex poles','(2*s+5)/((s+1)*(s^2+2*s+5))'],
['5. Repeated complex poles','(s+1)/(s^2+2*s+5)^2'],
['6. Improper rational function','(s^3+2*s^2+3*s+1)/(s^2+3*s+2)'],
['7. Pole at the origin','(3*s+2)/(s^2*(s+1))'],
['8. Mixed repeated factors','(2*s+1)/((s+1)^2*(s^2+4))'],
['Distinct real poles (I)','6/(s^2+6*s+8)'],
['Distinct real poles (II)','(s^2+17*s+20)/(s*(s^2+6*s+5))'],
['Repeated real poles','(s+2)^2/(s*(s+1)^3)'],
['Polynomial division','(6*s^3+4*s^2+8*s+6)/(s^2+2*s+1)'],
['Equal-degree rational function','(s^2+3*s+2)/(s^2+2*s+1)']];
const esc=x=>String(x).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const fmt=(x,n=4)=>{if(Math.abs(x)<.00005)return'0';return (+x.toFixed(n)).toString()};
const complex=a=>Math.abs(a.im)<.00005?fmt(a.re):`${fmt(a.re)}${a.im<0?'-':'+'}${fmt(Math.abs(a.im))}j`;
const poly=p=>{let terms=[];for(let i=p.length-1;i>=0;i--){let a=p[i];if(Math.abs(a)<1e-7)continue;let sign=a<0?'-':'+',v=Math.abs(a),coef=i&&Math.abs(v-1)<1e-7?'':fmt(v),term=coef+(i===0?'':i===1?'s':`s^{${i}}`);terms.push({sign,term})}return terms.length?terms.map((t,i)=>(i===0?(t.sign==='-'?'-':''):t.sign)+t.term).join(''):'0'};
const math=x=>`<div class="math">${x}</div>`;
const pole=p=>Math.abs(p.im)<.00005?`(${fmt(p.re)})`:`(${fmt(p.re)}${p.im<0?'-':'+'}j${fmt(Math.abs(p.im))})`;
const den=t=>{let p=t.p;let factor=Math.abs(p.im)<.00005?(p.re<0?`(s+${fmt(-p.re)})`:p.re>0?`(s-${fmt(p.re)})`:'s'):`(s-${pole(p)})`;return factor+(t.k>1?'^{'+t.k+'}':'')};
const factorial=n=>{let x=1;for(let i=2;i<=n;i++)x*=i;return x};
const ctex=c=>Math.abs(c.im)<.00005?fmt(c.re):`(${fmt(c.re)}${c.im<0?'-':'+'}j${fmt(Math.abs(c.im))})`;
const frac=t=>`\\frac{${ctex(t.c)}}{${den(t)}}`;
// Blackboard-style coefficient matching: clear the denominators, match
// polynomial powers, and display the numerical coefficient values.
const C=(re=0,im=0)=>({re,im});
const ca=(a,b)=>C(a.re+b.re,a.im+b.im);
const cs=(a,b)=>C(a.re-b.re,a.im-b.im);
const cm=(a,b)=>C(a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re);
const cdiv=(arr,p)=>{let n=arr.length-1,quot=Array(n);quot[n-1]=arr[n];for(let i=n-2;i>=0;i--)quot[i]=ca(arr[i+1],cm(p,quot[i+1]));return {q:quot,r:ca(arr[0],cm(p,quot[0]))}};
const coefficientWork=m=>{
  const terms=m.terms, variables=[], used=new Set();
  const quotient=(t)=>{let q=m.d.map(v=>C(v));for(let k=0;k<t.k;k++)q=cdiv(q,t.p).q;return q};
  const same=(a,b)=>Math.abs(a-b)<.0005;
  const almostReal=z=>Math.abs(z.im)<.005;
  const letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const realPoly=arr=>arr.map(z=>Math.abs(z.re)<.00001?0:z.re);
  const combine=(a,b,op)=>Array.from({length:Math.max(a.length,b.length)},(_,i)=>op(a[i]||C(),b[i]||C()));
  for(let i=0;i<terms.length;i++){
    if(used.has(i))continue;
    const t=terms[i],q=quotient(t);
    if(almostReal(t.p)){
      used.add(i);variables.push({name:letters[variables.length]||`A_{${variables.length+1}}`,basis:realPoly(q),value:t.c.re});
    }else{
      const j=terms.findIndex((v,k)=>k!==i&&!used.has(k)&&v.k===t.k&&same(v.p.re,t.p.re)&&same(v.p.im,-t.p.im));
      if(j<0)return '<p class="bad">Unable to pair complex poles for coefficient matching.</p>';
      used.add(i);used.add(j);const qq=quotient(terms[j]);
      const sum=combine(q,qq,ca),diff=combine(q,qq,(u,v)=>cm(C(0,1),cs(u,v)));
      const first=letters[variables.length]||`A_{${variables.length+1}}`;
      variables.push({name:first,basis:realPoly(sum),value:t.c.re});
      const second=letters[variables.length]||`A_{${variables.length+1}}`;
      variables.push({name:second,basis:realPoly(diff),value:t.c.im});
    }
  }
  if(!variables.length)return math('R(s)=0');
  const degree=Math.max(m.rem.length,...variables.map(v=>v.basis.length));
  const termPoly=(arr)=>poly(arr);
  const rhs=variables.map(v=>`${v.name}\\left(${termPoly(v.basis)}\\right)`).join('+').replace(/\+\-/g,'-');
  const lines=[`<div class="pfe-coefficient-title">Clear the denominators</div>`,math(`${poly(m.rem)}=${rhs}`),`<div class="pfe-coefficient-title">Match coefficients of equal powers of s</div>`];
  const eq=[];
  for(let k=degree-1;k>=0;k--){
    const parts=[];
    variables.forEach(v=>{const x=v.basis[k]||0;if(Math.abs(x)<.0001)return;const coeff=fmt(Math.abs(x),3),part=(Math.abs(Math.abs(x)-1)<.0001?'':coeff)+v.name;parts.push({sign:x<0?'-':'+',part})});
    const target=m.rem[k]||0;
    if(!parts.length){if(Math.abs(target)>.0001)eq.push(`${fmt(target,3)}=0`);continue}
    let expression=parts.map((x,i)=>(i===0?(x.sign==='-'?'-':''):x.sign)+x.part).join('');
    eq.push(`${fmt(target,3)}=${expression}`);
  }
  // Show the independent coefficient equations. Avoid repeated 0=0 rows.
  lines.push(...eq.slice(0,Math.min(7,eq.length)).map(x=>math(x)));
  lines.push('<div class="pfe-coefficient-title">Solve for the coefficients</div>');
  lines.push(...variables.map(v=>math(`${v.name}=${fmt(v.value,4)}`)));
  if(terms.some(t=>Math.abs(t.p.im)>.0005))lines.push('<p class="hint">For conjugate poles, the real-valued coefficient equations are grouped together.</p>');
  return lines.join('');
};

const form=t=>`\\frac{A_{${t.idx}}}{${den(t)}}`;
const groupInfo=m=>m.groups.map(g=>`<div class="pfe-pole-item"><b>${esc(complex(g.p))}</b><span>Multiplicity ${g.m}</span></div>`).join('');
function plot(id,curves,xmin,xmax,ylabel){let cv=document.getElementById(id);if(!cv)return;let W=Math.max(320,cv.clientWidth),H=cv.clientHeight||225,d=Math.min(window.devicePixelRatio||1,1.5);cv.width=W*d;cv.height=H*d;let q=cv.getContext('2d');q.setTransform(d,0,0,d,0,0);q.clearRect(0,0,W,H);let vals=curves.flatMap(c=>c.y.filter(Number.isFinite)),mag=Math.max(1,...vals.map(Math.abs)),L=52,R=15,T=20,B=34,sx=x=>L+(x-xmin)/(xmax-xmin)*(W-L-R),sy=y=>(H-B+T)/2-y/mag*(H-B-T)*.43;q.strokeStyle='rgba(170,180,195,.35)';q.beginPath();q.moveTo(L,sy(0));q.lineTo(W-R,sy(0));if(xmin<0&&xmax>0){q.moveTo(sx(0),T);q.lineTo(sx(0),H-B)}q.stroke();q.font='10px Arial';q.fillStyle='#aab0bb';for(let i=0;i<=6;i++){let x=xmin+i*(xmax-xmin)/6;q.fillText(fmt(x,1),sx(x)-9,H-11)}[-mag,0,mag].forEach(y=>q.fillText(fmt(y,1),3,sy(y)+3));q.fillText(ylabel,5,12);curves.forEach(c=>{q.strokeStyle=c.color;q.lineWidth=2;q.beginPath();c.y.forEach((y,i)=>{let x=xmin+i*(xmax-xmin)/(c.y.length-1);i?q.lineTo(sx(x),sy(y)):q.moveTo(sx(x),sy(y))});q.stroke()})}
function splot(m){let cv=document.getElementById('pfePoles');if(!cv)return;let W=Math.max(320,cv.clientWidth),H=cv.clientHeight||220,d=Math.min(window.devicePixelRatio||1,1.5);cv.width=W*d;cv.height=H*d;let q=cv.getContext('2d');q.setTransform(d,0,0,d,0,0);q.clearRect(0,0,W,H);let r=Math.max(3,...m.groups.map(g=>Math.max(Math.abs(g.p.re),Math.abs(g.p.im))))+1,L=42,R=14,T=16,B=30,sx=x=>L+(x+r)/(2*r)*(W-L-R),sy=y=>T+(r-y)/(2*r)*(H-T-B);q.strokeStyle='#666';q.beginPath();q.moveTo(L,sy(0));q.lineTo(W-R,sy(0));q.moveTo(sx(0),T);q.lineTo(sx(0),H-B);q.stroke();q.font='10px Arial';q.fillStyle='#aaa';for(let i=-2;i<=2;i++){let v=i*r/2;q.fillText(fmt(v,1),sx(v)-9,H-8);if(i)q.fillText(fmt(v,1),3,sy(v)+3)}q.fillText('Re{s}',W-48,sy(0)-7);q.fillText('Im{s}',sx(0)+7,12);m.groups.forEach(g=>{let x=sx(g.p.re),y=sy(g.p.im);q.strokeStyle='#ff4d57';q.lineWidth=2.5;q.beginPath();q.moveTo(x-6,y-6);q.lineTo(x+6,y+6);q.moveTo(x+6,y-6);q.lineTo(x-6,y+6);q.stroke();q.fillStyle='#ff4d57';q.fillText(g.m>1?'×'+g.m:'',x+8,y-8)})}
function inverse(m){let pieces=[];m.terms.forEach(t=>{if(t.p.im<-.00005)return;if(Math.abs(t.p.im)<.00005){pieces.push(`${ctex(t.c)}${t.k>1?`\\frac{t^{${t.k-1}}}{${(function f(n){let x=1;for(let i=2;i<=n;i++)x*=i;return x})(t.k-1)}}`:''}e^{${fmt(t.p.re)}t}`)}else{let partner=m.terms.find(u=>u.k===t.k&&Math.abs(u.p.re-t.p.re)<.01&&Math.abs(u.p.im+t.p.im)<.01);if(!partner)return;let fac=t.k>1?`\\frac{t^{${t.k-1}}}{${(function f(n){let x=1;for(let i=2;i<=n;i++)x*=i;return x})(t.k-1)}}`:'';pieces.push(`${fac}e^{${fmt(t.p.re)}t}\\left(${fmt(2*t.c.re)}\\cos(${fmt(t.p.im)}t)${t.c.im>0?'-':'+'}${fmt(2*Math.abs(t.c.im))}\\sin(${fmt(t.p.im)}t)\\right)`)}});return pieces.join('+').replace(/\+\-/g,'-')||'0'}
function render(b){b.innerHTML=`<h2 class="section-title">Partial Fractions Lab</h2><p class="muted">Classify the rational function, identify its poles, and follow the complete solution or build your own X(s).</p><div class="lab-layout pfe-v80-layout"><div class="pfe-v80-main"><article class="step-card pfe-classification"><div class="pfe-explore">FUNCTION CLASSIFICATION</div><h3>First, classify X(s)</h3><p>Let m = degree of the numerator and n = degree of the denominator.</p><div class="pfe-class-grid"><div><b>m &lt; n</b><span>Strictly proper — expand directly</span></div><div><b>m = n</b><span>Proper (equal degree) — divide first</span></div><div><b>m &gt; n</b><span>Improper — divide first</span></div></div><div id="pfeV81Classification" class="analysis-card"></div></article><article class="step-card"><div class="pfe-explore">POLE TYPES</div><h3>Four fundamental pole cases</h3><div class="pfe-class-grid pfe-case-buttons">${examples.slice(0,8).map((e,i)=>`<button type="button" class="pfe-case-button" data-pfe-case="${i}" aria-pressed="false">${esc(e[0].replace(/^\d+\.\s*/,''))}</button>`).join('')}</div></article><div id="pfeV80Steps" class="step-stack"></div><div class="dual-plot"><div class="plot-card"><h4>s-plane: poles ×</h4><canvas id="pfePoles"></canvas></div><div class="plot-card"><h4>Inverse Laplace response x(t), t ≥ 0</h4><canvas id="pfeTime"></canvas></div></div><div id="pfeV80Verify" class="analysis-card"></div></div><aside class="control-panel"><label>Examples / Build custom X(s)<select id="pfeV80Select"><option value="case">Selected pole case</option>${examples.slice(8).map((e,i)=>`<option value="${i+8}">${esc(e[0])}</option>`).join('')}<option value="custom">Build custom X(s)</option></select></label><label>Write X(s)<input id="pfeV80Expr" type="text" value="${esc(examples[0][1])}"></label><div id="pfeV80Preview" class="equation-live-preview"></div><button class="btn" id="pfeV80Solve">Calculate partial fractions</button><p class="hint">Accepts polynomial ratios, products, repeated factors, and powers. Example: (2*s+1)/((s+1)^2*(s^2+4)). Use * for multiplication. Delayed expressions containing exp(-T*s) are not rational and require the time-shifting property; this constructor does not accept them.</p><div id="pfeV80Status" role="status"></div></aside></div>`;
let sel=document.getElementById('pfeV80Select'),inp=document.getElementById('pfeV80Expr'),preview=document.getElementById('pfeV80Preview'),status=document.getElementById('pfeV80Status'),steps=document.getElementById('pfeV80Steps'),verification=document.getElementById('pfeV80Verify'),cards=[],model=null;
const show=()=>{steps.innerHTML=cards.join('');if(window.katex)steps.querySelectorAll('.math').forEach(e=>{try{katex.render(e.textContent,e,{throwOnError:false,displayMode:true})}catch(_){}})};
const card=(title,body)=>`<article class="step-card"><h3>${title}</h3>${body}</article>`;
function solve(){try{model=E.decompose(inp.value);let m=model,degreeN=m.n.length-1,degreeD=m.d.length-1,polyQ=poly(m.q),num=poly(m.n),denom=poly(m.d),hasPoly=m.q.some(x=>Math.abs(x)>1e-7),kind=m.groups.some(g=>g.m>1)?'Repeated factors':m.groups.some(g=>Math.abs(g.p.im)>1e-5)?'Complex-conjugate factors':'Distinct real factors';if(hasPoly)kind='Polynomial division before partial fractions';
let classification=degreeN<degreeD?'STRICTLY PROPER':degreeN===degreeD?'PROPER (EQUAL DEGREES)':'IMPROPER';
document.getElementById('pfeV81Classification').innerHTML=`<b class="pfe-class-result">m = ${degreeN}, n = ${degreeD} → ${classification}</b><p>${degreeN<degreeD?'No division needed: proceed to pole identification.':'Perform polynomial long division to obtain Q(s) + R(s)/D(s), where degree R < degree D.'}</p>`;
let list=m.terms.map((t,i)=>({...t,idx:i+1}));let symbolic=list.map(form).join('+')||'0',numeric=list.map(frac).join('+').replace(/\+\-/g,'-')||'0';let inverseText=inverse(m);let derivative=m.groups.some(g=>g.m>1),complexCase=m.groups.some(g=>Math.abs(g.p.im)>1e-5);
cards=[card('1. Original rational function',math(`X(s)=\\frac{${num}}{${denom}}`)),card('2. Polynomial division and poles',(hasPoly?math(`X(s)=${polyQ}+\\frac{${poly(m.rem)}}{${denom}}`):'')+`<p><b>Pole categories:</b> ${m.groups.some(g=>Math.abs(g.p.im)<1e-5&&g.m===1)?"distinct/simple real; ":""}${m.groups.some(g=>Math.abs(g.p.im)<1e-5&&g.m>1)?"repeated real; ":""}${m.groups.some(g=>Math.abs(g.p.im)>=1e-5&&g.m===1)?"distinct complex; ":""}${m.groups.some(g=>Math.abs(g.p.im)>=1e-5&&g.m>1)?"repeated complex; ":""}</p><p>Detected poles and multiplicities:</p><div class="pfe-poles-list">${groupInfo(m)}</div>`),card('3. Choose the expansion form',math(`X(s)=${hasPoly?polyQ+'+':''}${symbolic}`)),card('4. Find the coefficients',coefficientWork(m)),card('5. Final partial-fraction expansion',math(`X(s)=${hasPoly?polyQ+'+':''}${numeric}`)+''),card('6. Inverse Laplace transform',math(`${hasPoly?'x_{\\mathrm{regular}}(t)':'x(t)'}=\\left[${inverseText}\\right]u(t)`)+''),card('7. Verify the result',`<p class="${m.maxError<1e-6?'ok':'bad'}">Maximum relative residual: ${m.maxError.toExponential(2)}</p>`)];status.innerHTML='<p class="ok">Valid rational expression. Decomposition completed.</p>';show();verification.innerHTML=`<h3>Numerical verification</h3><p>Maximum relative residual: <b>${m.maxError.toExponential(2)}</b></p>`;splot(m);let t=Array.from({length:361},(_,i)=>i*8/360);plot('pfeTime',[{y:t.map(x=>Math.max(-1e6,Math.min(1e6,E.timeValue(m,x)))),color:'#4ed7cf'}],0,8,'x(t)');}catch(err){document.getElementById('pfeV81Classification').innerHTML='<p class="bad">Classification unavailable until X(s) is valid.</p>';status.innerHTML=`<p class="bad">${esc(err.message)}</p>`;steps.innerHTML=card('Check your expression',`<p>${esc(err.message)}</p><p>Examples: (2*s+3)/(s+1)^2, (s+2)/(s^2+2*s+5), (s^3+1)/(s^2+3*s+2).</p>`);verification.innerHTML='';cards=[];}}
const caseButtons=[...b.querySelectorAll('[data-pfe-case]')];const markCase=i=>caseButtons.forEach((btn,j)=>{let active=j===i;btn.classList.toggle('active',active);btn.setAttribute('aria-pressed',String(active))});caseButtons.forEach((btn,i)=>btn.addEventListener('click',()=>{sel.value='case';inp.value=examples[i][1];markCase(i);preview.textContent='X(s) = '+inp.value;solve()}));sel.onchange=()=>{markCase(-1);if(sel.value!=='custom'&&sel.value!=='case')inp.value=examples[+sel.value][1];preview.textContent='X(s) = '+inp.value;solve()};inp.oninput=()=>{markCase(-1);sel.value='custom';preview.textContent='X(s) = '+inp.value;status.textContent='Press Enter or Calculate to solve.'};inp.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();solve();inp.blur()}};document.getElementById('pfeV80Solve').onclick=solve;preview.textContent='X(s) = '+inp.value;markCase(0);solve();}
return{render,examples};})();
