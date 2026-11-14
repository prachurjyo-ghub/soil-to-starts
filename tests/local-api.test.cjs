const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const intake=require('../prototype/public/reference/intake.js');
const location=require('../prototype/public/reference/location.js');
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'sts-local-api-'));process.env.STS_DB_PATH=path.join(temp,'api.sqlite3');
test.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
const modules=Promise.all([import('../prototype/server/local-api.mjs'),import('../prototype/server/intake-validation.mjs')]);
function input(){const result=intake.validateAndNormalize({...intake.blankDraft(),districtId:'bd-district-dhaka',currentCrop:'rice',availabilityType:'date',availableFrom:'2027-01-01',availabilityBasis:'expected',historyState:'first_cultivation',baselineState:'no_established_rotation',water:'rainfed',priority:'balanced'});assert.equal(result.ok,true);return result.request;}
function request(body,headers={}){return new Request('http://localhost:3000/api/plan',{method:'POST',headers:{'content-type':'application/json',host:'localhost:3000',origin:'http://localhost:3000',...headers},body:JSON.stringify(body)});}
test('shared server validator accepts all 64 district intake identities',async()=>{const [,v]=await modules;for(const d of intake.districts){const data=input();data.location.district_id=d.id;assert.equal(v.validateIntake(data).location.district_id,d.id);}});
test('server rejects forged dates, hidden crops and invalid unit/location semantics',async()=>{const [,v]=await modules;const bad=[];let r=input();r.availability.start='2027-02-30';r.availability.end=r.availability.start;bad.push(r);r=input();r.location.coordinates={latitude:23,longitude:90};bad.push(r);r=input();r.baseline.segments=[{kind:'crop',crop_id:'rice',period:{kind:'dates',start:'2027-01-01',end:'2027-01-02'}}];bad.push(r);r=input();r.irrigation.access='all';bad.push(r);for(const b of bad)assert.throws(()=>v.validateIntake(b));});
test('map pins are rechecked against pinned local geometry',async()=>{const [,v]=await modules;const collection=JSON.parse(fs.readFileSync(path.join(__dirname,'../prototype/public/reference/data/district-boundaries.v1.geojson'),'utf8'));const index=location.makeIndex(collection,intake.districts.map(d=>d.id));
 // Resolve a public district anchor using the same containment implementation.
 const draft={locationMethod:'map_pin',mapPin:{latitude:23.794,longitude:90.405,confirmed:false}};const resolved=location.confirmPin(draft,index);assert.equal(resolved.status,'resolved');const normalized=location.normalizeLocation(draft,index,intake.districts,intake.directorySource).location;const r=input();r.location=normalized;assert.equal(v.validateIntake(r).location.district_id,normalized.district_id);r.location.district_id='bd-district-bagerhat';assert.throws(()=>v.validateIntake(r));});
test('real local API persists input and returns source-backed incomplete output',async()=>{const [api]=await modules;const response=await api.post(request(input()),'plan');assert.equal(response.status,200);assert.equal(response.headers.get('cache-control'),'no-store');const report=await response.json();assert.equal(report.data_mode,'local_evidence');assert.equal(report.status,'incomplete');assert.equal(report.climate.status,'complete');assert.equal(report.evidence_profile.active_reviewed_rules,0);assert.equal(report.alternatives.length,0);const restored=await api.get(new Request('http://localhost:3000/api/results/'+report.result_id,{headers:{host:'localhost:3000'}}),'result',report.result_id);assert.equal(restored.status,200);assert.deepEqual((await restored.json()).result,report);});
test('invalid requests do not reach the persistence operation',async()=>{const [api]=await modules;const b=input();b.priority='unknown';const r=await api.post(request(b),'plan');assert.equal(r.status,422);assert.equal((await r.json()).status,'invalid_input');});
test('cross-origin and untrusted Host requests are rejected',async()=>{const [api]=await modules;assert.equal((await api.post(request(input(),{origin:'https://attacker.example'}),'plan')).status,403);assert.equal((await api.post(request(input(),{host:'attacker.example',origin:'https://attacker.example'}),'plan')).status,403);});
test('API rejects oversized and non-JSON bodies',async()=>{const [api]=await modules;assert.equal((await api.post(request(input(),{'content-type':'text/plain'}),'plan')).status,422);assert.equal((await api.post(request({payload:'a'.repeat(70000)}),'plan')).status,422);});
test('unknown capability IDs reveal no records or paths',async()=>{const [api]=await modules;const r=await api.get(new Request('http://localhost:3000/api/results/invalid',{headers:{host:'localhost:3000'}}),'result','invalid');assert.equal(r.status,404);assert.deepEqual(await r.json(),{status:'not_found'});});
test('all 30 intake labels have explicit source mappings without asserting suitability',async()=>{const [,v]=await modules;const registry=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/integration/crop_aliases.json'),'utf8'));assert.equal(intake.crops.length,30);assert.deepEqual(intake.crops.map(c=>c.id).sort(),registry.rows.map(r=>r.intake_id).sort());for(const c of intake.crops){const r=input();r.current.crop_id=c.id;assert.equal(v.validateIntake(r).current.crop_id,c.id);}assert.equal(registry.rows.find(r=>r.intake_id==='sesame').source_crop_id,null);});
test('actual Python report renders and exports without fixture values or undefined statistics',async()=>{const [api]=await modules;const report=await (await api.post(request(input()),'plan')).json();const ui=require('../prototype/public/reference/result-ui.js'),adapter=require('../prototype/public/reference/result-adapter.js');const view=ui.create({adapter:adapter.create({fetchImpl:async()=>({ok:true,json:async()=>report})}),render(){},navigate(){},toast(){},getSubmission:input});await view.submit(input());const html=view.renderGenuine(input());assert.match(html,/Your inputs and evidence are connected/);assert.match(html,/printed.*normal/i);assert.match(html,/Annual rainfall total|Annual mean 2m air temperature/);assert.doesNotMatch(html,/undefined|NaN|DEVELOPMENT FIXTURE/);assert.match(html,/Your usual crop order/);assert.match(html,/verified local planting and harvest guidance/);assert.doesNotMatch(html,/What farmers tried in Bogura/);assert.doesNotMatch(html,/Timeline unavailable|First alternative unavailable/);const receipt=ui.receipt(view.getData());assert.equal(receipt.fixture,false);assert.equal(receipt.response.persistence.storage,'local_sqlite');});
test('changing irrigation never silently supplies missing seasonal limitations',async()=>{const [api]=await modules;const scenario=input();scenario.request_kind='scenario';scenario.irrigation.access='reliable';assert.equal((await api.post(request(scenario),'plan')).status,422);scenario.irrigation.seasonal_limitations='none';const accepted=await api.post(request(scenario),'plan');assert.equal(accepted.status,200);assert.equal((await accepted.json()).data_mode,'local_evidence');});
test('real evidence reports save and restore without requiring invented alternatives',async()=>{
 const [api]=await modules,report=await(await api.post(request(input()),'plan')).json(),store=new Map();
 Object.defineProperty(global,'localStorage',{configurable:true,value:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v),removeItem:k=>store.delete(k)}});
 try{
 const ui=require('../prototype/public/reference/result-ui.js'),adapter=require('../prototype/public/reference/result-adapter.js');
 const make=()=>ui.create({adapter:adapter.create({fetchImpl:async()=>({ok:true,json:async()=>report})}),render(){},navigate(){},toast(){},getSubmission:input});
 const view=make();await view.submit(input());view.handleClick({dataset:{resultSave:'evidence-report'}});assert.equal(view.getSaved().example,false);assert.equal(view.getSaved().data.response.alternatives.length,0);assert.equal(make().getSaved().data.response.result_id,report.result_id);
 }finally{delete global.localStorage;}
});

test('a saved season-based rotation appears before field details and past seasons are rejected', async () => {
 const [api] = await modules;
 const body = input();
 body.baseline = {state:'sequence',segments:[{kind:'crop',crop_id:'brinjal',period:{kind:'season_year',season_id:'kharif_1',year:2025}}]};
 assert.equal((await api.post(request(body),'plan')).status,422);
 body.baseline.segments[0].period.year = 2027;
 const response = await api.post(request(body),'plan');
 assert.equal(response.status,200);
 const report = await response.json();
 assert.equal(report.baseline_assessment.segments[0].crop_id,'brinjal');
 const ui = require('../prototype/public/reference/result-ui.js');
 const adapter = require('../prototype/public/reference/result-adapter.js');
 const view = ui.create({adapter:adapter.create({fetchImpl:async()=>({ok:true,json:async()=>report})}),render(){},navigate(){},toast(){}});
 await view.submit(body);
 const html = view.renderGenuine(body);
 assert.match(html,/Brinjal<\/b><span>Kharif I 2027/);
 assert.ok(html.indexOf('Your usual crop order') < html.indexOf('field-summary-title'));
});

test('regional crop options are distinct and display source timing ahead of the reported order', async () => {
 const [api] = await modules;
 const body = input();
 const report = await (await api.post(request(body),'plan')).json();
 const options = report.calendar_options;
 assert.equal(options.length,3);
 assert.equal(new Set(options.map(option=>option.crop_id)).size,3);
 for (const option of options) {
   assert.equal(option.region,'Dhaka');
   assert.ok(option.calendar_start.slice(0,7)>=body.availability.end.slice(0,7));
   const crop = report.evidence_profile.crop_context.regional_catalogue.find(c=>c.crop_id===option.crop_id);
   assert.ok(crop.calendars.some(record=>record.id===option.id&&record.source_id===option.source_id));
 }
 const ui = require('../prototype/public/reference/result-ui.js');
 const adapter = require('../prototype/public/reference/result-adapter.js');
 const view = ui.create({adapter:adapter.create({fetchImpl:async()=>({ok:true,json:async()=>report})}),render(){},navigate(){},toast(){}});
 await view.submit(body);
 const html = view.renderGenuine(body);
 assert.ok(html.indexOf('Compare crop rotations') < html.indexOf('Your usual crop order'));
 assert.equal(report.calendar_rotation.sequences.length,2);
 for (const {steps} of report.calendar_rotation.sequences) {
   assert.equal(new Set(steps.map(step=>step.crop_id)).size,3);
   assert.ok(steps[0].calendar_start.slice(0,7)>=body.availability.end.slice(0,7));
   assert.ok(steps[2].calendar_end<=report.calendar_rotation.end);
   assert.ok(steps[0].calendar_end<steps[1].calendar_start && steps[1].calendar_end<steps[2].calendar_start);
 }
 assert.notDeepEqual(...report.calendar_rotation.sequences.map(plan=>plan.steps.map(step=>step.crop_id)));
 assert.match(html,/Alternative A/);
 assert.match(html,/Alternative B/);
 assert.deepEqual(report.alternatives,[]);
});
