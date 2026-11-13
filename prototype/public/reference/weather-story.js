(async function(){
'use strict';
const host=document.getElementById('weather-story-data');if(!host)return;
await import('./result-ui.js');await import('./climate-history.js');
let bundle=null,district='',metric='T2M',error=false;
const lang=()=>document.documentElement.lang==='bn'?'bn':'en';
function render(){
 host.innerHTML=error?'<p role="alert">Local weather history could not load. / আবহাওয়ার তথ্য লোড হয়নি।</p><button type="button" data-story-retry>Retry / আবার চেষ্টা করুন</button>':window.STS_CLIMATE_HISTORY.render(bundle,district,metric,lang(),window.STS_RESULT_UI.chart);
}
async function load(){error=false;render();try{bundle=await window.STS_CLIMATE_HISTORY.load();}catch{error=true;}render();}
host.addEventListener('change',e=>{if(e.target.matches('[data-weather-district]')){district=e.target.value;render();}});
host.addEventListener('click',e=>{const button=e.target.closest('button');if(!button)return;if(button.dataset.weatherMetric){metric=button.dataset.weatherMetric;render();}if(button.hasAttribute('data-story-retry'))void load();});
document.addEventListener('sts-language-change',render);
if('IntersectionObserver' in window){const story=document.getElementById('weather-story');const observer=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){story.dataset.chapter=e.target.dataset.weatherChapter;story.querySelectorAll('[data-weather-chapter]').forEach(ch=>ch.classList.toggle('is-current',ch===e.target));}},{rootMargin:'-20% 0px -30% 0px',threshold:0.15});story.querySelectorAll('[data-weather-chapter]').forEach(el=>observer.observe(el));}
void load();
})();
