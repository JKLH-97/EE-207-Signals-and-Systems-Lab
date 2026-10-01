document.addEventListener('DOMContentLoaded',()=>{
 const tabs=[...document.querySelectorAll('.nav-tab')], pages=[...document.querySelectorAll('.page')], cards=[...document.querySelectorAll('.module-card.available')];
 const sidebar=document.getElementById('sidebar'), toggle=document.getElementById('sidebarToggle');
 function setSidebar(collapsed){document.body.classList.toggle('sidebar-collapsed',collapsed);toggle.textContent=collapsed?'›':'‹';try{localStorage.setItem('ee207-sidebar',collapsed?'1':'0')}catch(e){}}
 toggle.addEventListener('click',()=>setSidebar(!document.body.classList.contains('sidebar-collapsed')));
 try{setSidebar(localStorage.getItem('ee207-sidebar')==='1')}catch(e){setSidebar(false)}
 function openPage(id){const p=document.getElementById(id);if(!p)return;pages.forEach(x=>x.classList.remove('active'));tabs.forEach(x=>x.classList.remove('active'));p.classList.add('active');document.querySelector(`.nav-tab[data-page="${id}"]`)?.classList.add('active');if(id==='lti'&&window.LTI)LTI.render();try{localStorage.setItem('ee207-current-page',id)}catch(e){} window.scrollTo({top:0,behavior:'smooth'});}
 tabs.forEach(b=>b.addEventListener('click',()=>openPage(b.dataset.page)));cards.forEach(c=>{c.tabIndex=0;c.addEventListener('click',()=>openPage(c.dataset.open));c.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openPage(c.dataset.open)}})});
 window.addEventListener('ee207:navigate',e=>e.detail?.page&&openPage(e.detail.page));let saved='home';try{saved=localStorage.getItem('ee207-current-page')||'home'}catch(e){}openPage(document.getElementById(saved)?saved:'home');
});
