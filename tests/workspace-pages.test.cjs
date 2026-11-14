const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const fixtures=require('./fixtures/result-fixtures.cjs');
const adapter=require('../prototype/public/reference/result-adapter.js');
const ui=require('../prototype/public/reference/result-ui.js');
const pages=require('../prototype/public/reference/workspace-pages.js');
const weather=require('../prototype/public/reference/climate-history.js');
const bundle=JSON.parse(fs.readFileSync(path.join(__dirname,'../prototype/public/data/climate-history.json'),'utf8'));
function setup(extra={}){return ui.create({adapter:adapter.create({fetchImpl:null,fixtures}),render(){},navigate(){},toast(){},getSubmission(){return null;},...extra});}
test('sidebar routes render independent pages without a submitted field',()=>{
 const app=setup();for(const [route,title] of Object.entries({rotations:'Rotation plans',compare:'Compare plans',simulator:'What-if studio',saved:'Saved plan',methodology:'Data &amp; methodology'})){const html=app.renderRoute(route,null);assert.match(html,new RegExp(title));assert.doesNotMatch(html,/Priority-weighted score|LIVE RANKING/);}
 assert.match(app.renderRoute('saved',null),/No plan saved yet/);assert.match(app.renderRoute('methodology',null),/T2M/);
});
test('rotations and comparison use supplied results and preserve missing alternatives',async()=>{
 const app=setup();await app.activateFixture('incomplete-one-alternative');for(const route of ['compare','rotations']){const html=app.renderRoute(route,null);assert.match(html,/Second alternative unavailable/);assert.match(html,/Save plan snapshot/);assert.match(html,/NOT SCIENTIFIC ADVICE/);assert.doesNotMatch(html,/Priority-weighted score/);}
});
test('legacy example snapshots are never restored as product data',async()=>{
 const store=new Map();Object.defineProperty(global,'localStorage',{configurable:true,value:{getItem:k=>store.get(k),setItem:(k,v)=>store.set(k,v),removeItem:k=>store.delete(k)}});
 try{const app=setup();await app.activateFixture('complete-comparison');app.handleClick({dataset:{resultSave:app.getData().response.alternatives[0].plan_id}});assert.equal(JSON.parse(store.get('sts-plan-snapshot-v1')).example,true);assert.match(setup().renderRoute('saved',null),/No plan saved yet/);}finally{delete global.localStorage;}
});
test('corrupt saved storage does not break the page',()=>{
 Object.defineProperty(global,'localStorage',{configurable:true,value:{getItem:()=>'{bad'}});try{assert.match(setup().renderRoute('saved',null),/No plan saved yet/);}finally{delete global.localStorage;}
});
test('climate supports 64 districts and never chooses one silently',()=>{
 assert.equal(bundle.districts.length,64);assert.equal(new Set(bundle.districts.map(d=>d.id)).size,64);const html=weather.render(bundle,'');assert.equal((html.match(/<option/g)||[]).length,65);assert.doesNotMatch(html,/selected>/);assert.match(html,/No district is selected/);
});
test('weather comparisons preserve periods, units and actual source hashes',()=>{
 for(const param of ['T2M','PRECTOTCORR']){const d=bundle.districts[0],m=bundle.grids[d.grid].metrics[param],html=weather.render(bundle,d.id,param,'en',ui.chart);assert.match(html,/2001–2010/);assert.match(html,/2016–2025/);assert.match(html,/Archive SHA-256/);assert.match(html,/not a forecast/);assert.ok(html.includes(m.chart_sha256));assert.equal(m.annual.length,25);assert.equal(m.periods[0].valid_years,10);}
});
test('climate loads independently from planning and uses the selected district',async()=>{
 const old=global.STS_CLIMATE_HISTORY;global.STS_CLIMATE_HISTORY={...weather,load:async()=>bundle};try{const app=setup(),request={location:{district_id:bundle.districts[1].id}};app.renderRoute('climate',request);await new Promise(r=>setImmediate(r));const html=app.renderRoute('climate',request);assert.match(html,/How has the weather shifted/);assert.match(html,/Annual mean air temperature/);assert.doesNotMatch(html,/Planning and evidence unavailable/);}finally{global.STS_CLIMATE_HISTORY=old;}
});
test('current-crop vulnerability remains visible after an unavailable planning request',async()=>{
 const app=setup(),request={current:{crop_id:'rice'}};assert.match(app.renderGenuine(request),/Heat exposure — not assessed/);await app.submit(request);assert.match(app.renderGenuine(request),/Current crop weather and risk checks/);assert.doesNotMatch(app.renderGenuine(request),/High risk/);
});
test('what-if controls retain canonical IDs and do not modify original inputs',()=>{
 const request=fixtures.fixture('complete-comparison').request,original=JSON.stringify(request),html=pages.render('simulator',{ui,request,language:'en'});assert.match(html,/value="soil_rotation"/);assert.doesNotMatch(html,/Climate stress test|LIVE RANKING/);assert.equal(JSON.stringify(request),original);
});

test('published UI contains no mock dataset or fabricated ranking runtime',()=>{
 for(const file of ['workspace.js','script.js']){const source=fs.readFileSync(path.join(__dirname,'../prototype/public/reference',file),'utf8');assert.doesNotMatch(source,/result-fixtures|demoFields|const scenarios|LIVE RANKING|Math\.random/);}
 assert.equal(fs.existsSync(path.join(__dirname,'../prototype/public/reference/result-fixtures.js')),false);
});
test('seasonal chart includes all twelve months and accessible source values',()=>{
 const d=bundle.districts[0];const html=weather.render(bundle,d.id,'PRECTOTCORR','en',ui.chart);assert.match(html,/How the seasons changed/);assert.match(html,/mm\/month/);assert.equal((html.match(/class="season-month"/g)||[]).length,12);assert.match(html,/<caption>/);
});
test('field planning shows the reported order, while the historical study appears only in methodology', async () => {
 const request = fixtures.fixture('complete-comparison').request;
 const response = {
   status:'incomplete', data_mode:'local_evidence', alternatives:[],
   baseline_assessment:{role:'baseline',segments:[{label:{en:'Lentil',bn:'মসুর'},period:'2027-01-01 → 2027-03-01'}]},
   evidence_profile:{crop_context:{regional_catalogue:[{crop_label:'Mustard',calendar_count:1,seasons:['Rabi']}]}}
 };
 const app = setup({adapter:adapter.create({fetchImpl:async()=>({ok:true,json:async()=>response})})});
 await app.submit(request);
 const rotations = app.renderRoute('rotations', request);
 assert.match(rotations,/Your usual crop order/);
 assert.match(rotations,/Lentil.*2027-01-01/);
 assert.match(rotations,/Mustard/);
 assert.match(rotations,/Rabi/);
 assert.match(app.renderRoute('compare', request),/data-calendar-choice/);
 assert.match(rotations,/Edit field answers/);
 assert.doesNotMatch(rotations,/Bogura|field study|First alternative unavailable/);
 assert.match(app.renderRoute('rotations', request,'bn'),/আপনার সাধারণ ফসলের ক্রম/);
 assert.match(app.renderRoute('methodology', request),/See an example from a field study/);
 assert.doesNotMatch(app.renderRoute('methodology', request),/What farmers tried in Bogura/);
});
