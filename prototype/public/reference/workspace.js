(async()=>{
'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
try{for(const file of ['location','intake','intake-map','intake-ui','result-adapter','result-ui','climate-history','workspace-pages'])await import('./'+file+'.js');}
catch{$('#main').textContent='Field tools could not load. Please reload. / জমির তথ্যের সেবা লোড হয়নি। আবার লোড করুন।';return;}
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const navItems=[['overview','◫','Your results'],['profile','⌖','Set up your field'],['rotations','⇄','Rotation plans'],['compare','⊞','Compare plans'],['simulator','⌁','What-if studio'],['climate','◷','Climate insights'],['saved','♡','Saved plan'],['methodology','◎','Data & methodology']];
const moreRoutes=new Set(['compare','simulator','climate','saved','methodology']);
let route='profile',lastRoute=null,moreOpen=false,lastFocus=null,toastTimer,results;
const intake=window.STS_INTAKE_UI({render,onSubmit:submitted=>{results.invalidate();navigate(submitted?'overview':'profile');if(submitted)void results.submit(intake.getSubmission());},toast});
results=window.STS_RESULT_UI.create({adapter:window.STS_RESULT_ADAPTER.create({endpoints:window.STS_RESULT_ENDPOINTS||{}}),render,navigate,toast,getSubmission:()=>intake.getSubmission(),downloadInputs:()=>intake.download()});
function toast(message){$('#toast').textContent=message;$('#toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').classList.remove('show'),3500);}
const mobile=()=>window.matchMedia('(max-width:800px)').matches;
function syncMobile(){
 const active=navItems.find(n=>n[0]===route)||navItems[1];$('#mobile-crumb').textContent=active[2];
 $$('#mobile-tabbar [data-tab]').forEach(a=>{a.classList.toggle('is-active',a.dataset.tab===route);if(a.dataset.tab===route)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 const more=$('#mobile-more-open');more.classList.toggle('is-active',moreRoutes.has(route));if(moreRoutes.has(route))more.setAttribute('aria-current','page');else more.removeAttribute('aria-current');
 $('#mobile-more-nav').innerHTML=navItems.filter(([id])=>moreRoutes.has(id)).map(([id,icon,label])=>`<a href="#${id}" ${route===id?'class="is-active" aria-current="page"':''}><span aria-hidden="true">${icon}</span>${label}</a>`).join('');
}
function focusables(el){return [...el.querySelectorAll('a[href],button:not([disabled]),select:not([disabled]),input:not([disabled]),[tabindex="0"]')].filter(e=>e.getClientRects().length&&!e.closest('[hidden]'));}
function closeMore({restoreFocus=true}={}){if(!moreOpen)return;moreOpen=false;$('#mobile-more-sheet').hidden=true;$('#mobile-more-backdrop').hidden=true;$('#mobile-more-open').setAttribute('aria-expanded','false');document.body.classList.remove('mobile-more-open');if(restoreFocus)lastFocus?.focus({preventScroll:true});}
function openMore(){if(!mobile()||moreOpen)return;lastFocus=document.activeElement;moreOpen=true;syncMobile();$('#mobile-more-sheet').hidden=false;$('#mobile-more-backdrop').hidden=false;$('#mobile-more-open').setAttribute('aria-expanded','true');document.body.classList.add('mobile-more-open');$('#mobile-more-close').focus();}
function render(){
 intake.beforeRender();route=location.hash.slice(1)||(intake.hasSubmission()?'overview':'profile');if(!navItems.some(n=>n[0]===route)){route='profile';history.replaceState(null,'','#profile');}
 const bn=document.documentElement.lang==='bn',language=bn?'bn':'en';
 $('#nav').innerHTML=navItems.map(([id,icon,label])=>`<a href="#${id}" class="${route===id?'active':''}" ${route===id?'aria-current="page"':''}><span>${icon}</span>${label}</a>`).join('');$('#crumb').textContent=navItems.find(n=>n[0]===route)[2];
 $('.field-switch small').textContent=bn?'আপনার জমির তথ্য':'YOUR FIELD INPUTS';
 if(intake.hasSubmission()&&!results.getData())void results.restore(intake.getSubmission());
 const report=results.getData()?.response;
 const status=report?.data_mode==='local_evidence'?(bn?'স্থানীয় প্রমাণের রিপোর্ট':'Local evidence report'):(bn?'জমির তথ্য':'Field inputs');$$('.demo-dot').forEach(el=>el.textContent=status);
 $$('[data-action="export"]').forEach(button=>{button.textContent=route==='saved'?(bn?'সংরক্ষিত কপি রপ্তানি':'Export saved snapshot'):report?(bn?'রিপোর্ট রপ্তানি':'Export report'):(bn?'তথ্য রপ্তানি':'Export inputs');button.disabled=route==='saved'?!results.getSaved():!intake.hasSubmission()||report?.status==='loading';});
 syncMobile();$('#main').innerHTML=route==='profile'?intake.form():route==='overview'?results.renderGenuine(intake.getSubmission(),language):results.renderRoute(route,intake.getSubmission(),language);intake.afterRender();
 $('#sidebar').classList.remove('open');$('#menu').setAttribute('aria-expanded','false');
 if(lastRoute!==route){window.scrollTo({top:0,left:0,behavior:'auto'});const heading=$('#main h1');if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});}lastRoute=route;}
}
function navigate(id){closeMore({restoreFocus:false});if(location.hash==='#'+id)render();else location.hash=id;}
function themeLabel(){const dark=document.body.classList.contains('dark'),bn=document.documentElement.lang==='bn';const label=bn?(dark?'লাইট মোড চালু করুন':'ডার্ক মোড চালু করুন'):(dark?'Switch to light mode':'Switch to dark mode');for(const id of ['theme','mobile-theme']){const button=$('#'+id);if(button){button.setAttribute('aria-label',label);if(id==='mobile-theme')button.textContent=label;}}}
try{document.body.classList.toggle('dark',localStorage.getItem('sts-studio-theme')==='dark');}catch{}themeLabel();
for(const id of ['theme','mobile-theme'])$('#'+id)?.addEventListener('click',()=>{document.body.classList.toggle('dark');try{localStorage.setItem('sts-studio-theme',document.body.classList.contains('dark')?'dark':'light');}catch{}themeLabel();});
$('#menu').addEventListener('click',()=>{if(mobile())return;const open=$('#sidebar').classList.toggle('open');$('#menu').setAttribute('aria-expanded',String(open));});
$('#mobile-more-open').addEventListener('click',()=>moreOpen?closeMore():openMore());$('#mobile-more-close').addEventListener('click',()=>closeMore());$('#mobile-more-backdrop').addEventListener('click',()=>closeMore());$('#mobile-more-nav').addEventListener('click',e=>{if(e.target.closest('a'))closeMore({restoreFocus:false});});
document.addEventListener('keydown',e=>{if(!moreOpen)return;if(e.key==='Escape'){e.preventDefault();closeMore();return;}if(e.key!=='Tab')return;const items=focusables($('#mobile-more-sheet')),first=items[0],last=items.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}});
document.addEventListener('click',e=>{const button=e.target.closest('button');if(!button)return;if(results.handleClick(button))return;if(button.dataset.route){navigate(button.dataset.route);return;}switch(button.dataset.action){case 'new-field':closeMore({restoreFocus:false});intake.newDraft();results.invalidate();navigate('profile');break;case 'print':window.print();break;case 'export':closeMore({restoreFocus:false});if(route==='saved')results.handleClick({dataset:{resultAction:'download-saved'}});else if(results.getData()?.response?.data_mode==='local_evidence')results.downloadReceipt();else intake.download();break;}});
document.addEventListener('change',e=>results.handleChange(e.target));
document.addEventListener('sts-language-change',()=>{render();themeLabel();});window.addEventListener('hashchange',()=>{closeMore({restoreFocus:false});render();});window.addEventListener('resize',()=>{if(!mobile())closeMore({restoreFocus:false});});
render();
})();
