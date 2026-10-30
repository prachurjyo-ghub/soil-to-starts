/* Run: node --test tests/intake.test.cjs (Node built-ins; no added dependency). */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const D = require('../prototype/public/reference/intake.js');
const dated = (cropId,start,end) => ({cropId,timing:'dates',start,end});
function valid() {
  return {...D.blankDraft(),districtId:'bd-district-bagerhat',currentCrop:'rice',currentSownOn:'2026-07-01',
    availabilityType:'date',availableFrom:'2026-11-15',availabilityBasis:'expected',historyState:'entries',
    history:[dated('rice','2026-03-01','2026-06-15')],baselineState:'sequence',
    baseline:[dated('mustard','2026-11-16','2027-02-20'),dated('fallow','2027-02-21','2027-03-15')],
    water:'limited',seasonalLimits:'none',priority:'water'};
}
const check = draft => D.validateAndNormalize(draft);
const rejects = (draft,field) => {
  const result=check(draft);assert.equal(result.ok,false);assert.equal(result.request,null);
  assert.ok(result.errors.some(e=>e.field===field),JSON.stringify(result.errors));
};

test('verified directory has exactly 64 unique district identities in all eight divisions',()=>{
  assert.equal(D.districts.length,64);assert.equal(new Set(D.districts.map(d=>d.id)).size,64);
  assert.deepEqual(Object.fromEntries([...new Set(D.districts.map(d=>d.division))].sort().map(div=>[div,D.districts.filter(d=>d.division===div).length])),
    {Barishal:6,Chattogram:11,Dhaka:13,Khulna:10,Mymensingh:4,Rajshahi:8,Rangpur:8,Sylhet:4});
  assert.equal(D.directorySource.url,'https://bangladesh.gov.bd/views/district-list');
  assert.ok(D.districts.every(d=>d.bn&&d.en&&d.sourceId===D.directorySource.id));
  for(const district of D.districts)assert.equal(check({...valid(),districtId:district.id}).ok,true);
  for(const bad of ['dhaka','BD-13','other','bd-district-unknown','rajshahi'])rejects({...valid(),districtId:bad},'districtId');
});

test('every core response and location reject missing, whitespace, placeholders and malformed values',()=>{
  for(const field of ['districtId','currentCrop','availabilityType','availableFrom','availabilityBasis','historyState','baselineState','water','priority'])
    for(const value of [undefined,null,'','  ','unknown','any',"I don't know",'Select an answer',{},42])
      rejects({...valid(),[field]:value},field);
});

test('fresh draft has no demo coordinates, soil, crop, water or priority defaults',()=>{
  const d=D.blankDraft();assert.equal(d.currentCrop,'');assert.equal(d.water,'');assert.equal(d.priority,'');assert.equal(d.districtId,'');
  assert.equal('ph' in d,false);assert.equal('lat' in d,false);assert.equal('weights' in d,false);
  assert.equal(check(d).ok,false);
  assert.deepEqual(D.loadSaved({fields:[{region:'Rajshahi',water:'Reliable',weights:[100]}],current:'rajshahi'}).draft,d);
});

test('real dates reject overflow, non-leap days, year zero and malformed windows',()=>{
  for(const date of ['2026-02-29','2026-04-31','2026-13-01','2026-00-10','0000-01-01','15/11/2026','2026-1-01','2026-11-00'])rejects({...valid(),availableFrom:date},'availableFrom');
  assert.equal(D.validDate('2024-02-29'),true);
  rejects({...valid(),availabilityType:'window',availableTo:''},'availableTo');
  rejects({...valid(),availabilityType:'window',availableTo:'2026-11-14'},'availableTo');
  rejects({...valid(),currentSownOn:'2026-11-16'},'availableFrom');
  rejects({...valid(),currentSownOn:'invalid'},'currentSownOn');
});

test('estimated bounded availability normalizes without inventing a precise harvest',()=>{
  const d=valid();d.availabilityType='window';d.availableTo='2026-11-25';d.availabilityBasis='farmer_estimate';
  const r=check(d);assert.equal(r.ok,true);
  assert.deepEqual(r.request.availability,{kind:'window',start:'2026-11-15',end:'2026-11-25',basis:'farmer_estimate',applies_to:'after_harvest'});
});

test('equal previous and current crops are allowed and history remains separate from baseline',()=>{
  const r=check(valid());assert.equal(r.ok,true);
  assert.equal(r.request.current.crop_id,r.request.crop_history.entries[0].crop_id);
  assert.equal(r.request.baseline.segments[1].kind,'fallow');assert.equal(r.request.baseline.segments[1].crop_id,null);
  assert.equal(r.request.baseline.assessed,false);assert.equal(r.request.crop_history.rotation_risks_assessed,false);
});

test('legitimate empty, first-cultivation and no-baseline states stay distinct',()=>{
  const d={...valid(),currentCrop:'fallow',currentSownOn:'hidden stale value',historyState:'first_cultivation',baselineState:'no_established_rotation',water:'rainfed'};
  const r=check(d);assert.equal(r.ok,true);
  assert.deepEqual(r.request.current,{state:'fallow',crop_id:null,sown_on:null});
  assert.equal(r.request.availability.applies_to,'available_from');
  assert.deepEqual(r.request.crop_history.entries,[]);assert.deepEqual(r.request.baseline.segments,[]);
  assert.equal(r.request.planning.comparison_status,'unavailable');
});

test('dependent history and baseline controls must contain meaningful periods and identities',()=>{
  for(const key of ['history','baseline']) {
    rejects({...valid(),[key]:[]},key+'State');
    rejects({...valid(),[key]:[{...D.row()}]},key+'-0-cropId');
    rejects({...valid(),[key]:[null]},key+'-0-cropId');
    rejects({...valid(),[key]:[{cropId:'rice',timing:'season_year',seasonId:'unknown',year:'2026'}]},key+'-0-seasonId');
    rejects({...valid(),[key]:[{cropId:'rice',timing:'season_year',seasonId:'rabi',year:'  '}]},key+'-0-year');
    rejects({...valid(),[key]:[dated('rice','2026-12-01','2026-11-01')]},key+'-0-end');
  }
  rejects({...valid(),history:[dated('fallow','2026-03-01','2026-06-01')]},'history-0-cropId');
});

test('known crop-date contradictions and chronological overlap fail',()=>{
  rejects({...valid(),history:[dated('rice','2026-03-01','2026-07-02')]},'history-0-end');
  rejects({...valid(),currentSownOn:'',history:[dated('rice','2026-03-01','2026-11-16')]},'history-0-end');
  rejects({...valid(),baseline:[dated('rice','2026-11-14','2027-01-20')]},'baseline-0-start');
  rejects({...valid(),baseline:[dated('rice','2026-11-16','2027-01-20'),dated('rice','2027-01-10','2027-03-20')]},'baseline-1-start');
  const seasonal={cropId:'rice',timing:'season_year',seasonId:'rabi',year:'2026'};
  rejects({...valid(),baseline:[seasonal,{...seasonal}]},'baseline-1-seasonId');
  rejects({...valid(),baseline:[{...seasonal,year:'2027'},seasonal]},'baseline-1-seasonId');
  assert.equal(check({...valid(),baseline:[seasonal,{...seasonal,seasonId:'kharif_1',year:'2027'}]}).ok,true);
});

test('repeated baseline crops in different chronological periods are allowed',()=>{
  assert.equal(check({...valid(),baseline:[dated('rice','2026-11-16','2027-02-01'),dated('rice','2027-03-01','2027-06-01')]}).ok,true);
});

test('seasonal irrigation limitations require a real answer and applicable seasons',()=>{
  rejects({...valid(),seasonalLimits:''},'seasonalLimits');
  rejects({...valid(),seasonalLimits:'seasonal',limitedSeasons:[]},'limitedSeasons');
  rejects({...valid(),seasonalLimits:'seasonal',limitedSeasons:['any']},'limitedSeasons');
  rejects({...valid(),seasonalLimits:'seasonal',limitedSeasons:['rabi','rabi']},'limitedSeasons');
  const r=check({...valid(),seasonalLimits:'seasonal',limitedSeasons:['rabi','kharif_1']});
  assert.equal(r.ok,true);assert.deepEqual(r.request.irrigation.limited_seasons,['kharif_1','rabi']);
  assert.equal(check({...valid(),water:'rainfed',seasonalLimits:''}).ok,true);
});

test('normalization strips irrelevant/demo values and preserves provenance without scientific success',()=>{
  const d={...valid(),districtId:' bd-district-bagerhat ',priority:' water ',availableTo:'hidden',ph:6.5,lat:24.3745,weights:[45],saved:'Rice|Rice|Rice'};
  const r=check(d).request;assert.equal(r.schema_version,'farmer-intake.v2');
  assert.equal(r.location.level,'district');assert.equal(r.location.coordinates,null);
  assert.equal(r.location.provenance.kind,'farmer_selected_district');
  assert.equal(r.availability.end,r.availability.start);assert.equal(r.priority,'water');
  assert.deepEqual(r.planning,{status:'unavailable',reason:'scientific_api_not_connected',comparison_status:'unavailable'});
  for(const key of ['ph','lat','weights','saved','score','recommendations'])assert.equal(key in r,false);
  assert.equal(JSON.stringify(r).includes('24.3745'),false);
});

test('saved genuine answers are restored and revalidated; invalid or foreign storage is not a submission',()=>{
  const answers=valid(),s=D.loadSaved({version:1,draft:answers,submitted:{answers,request:{planning:{status:'complete'}}}});
  assert.equal(s.submitted.request.planning.status,'unavailable');assert.equal(s.draft.priority,'water');
  assert.equal(D.loadSaved({version:1,submitted:{answers:{priority:'balanced'}}}).submitted,null);
  assert.equal(D.loadSaved({version:999,draft:answers}).draft.priority,'');
  assert.equal(D.loadSaved({version:1,draft:{history:[null],priority:{}}}).draft.priority,'');
});

// Small event harness exercises the actual UI controller without a browser dependency.
function uiHarness(saved,language='en',withMap=false) {
  const listeners={},store=new Map(saved?[['sts-farmer-intake-v1',JSON.stringify(saved)]]:[]);
  let focused=null,focusOptions=null,submitted=null,renders=0;
  const document={documentElement:{lang:language},addEventListener:(event,fn)=>{listeners[event]=fn;},
    getElementById:id=>({focus:options=>{focused=id;focusOptions=options;}}),querySelectorAll:()=>[]};
  let mapCallbacks;
  const window={STS_INTAKE:D,STS_LOCATION:require('../prototype/public/reference/location.js')};
  if(withMap)window.STS_INTAKE_MAP={create:config=>{mapCallbacks=config;return {isReady:()=>true,updateMarker(){},destroy(){},beforeRender(){},afterRender(){},placeCenter(){}};},loadBoundaries:async()=>({index:withMap})};
  const context={window,document,structuredClone,localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v)}};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../prototype/public/reference/intake-ui.js'),'utf8'),context);
  const controller=window.STS_INTAKE_UI({render:()=>renders++,onSubmit:value=>submitted=value,onDemo:()=>{},toast:()=>{}});
  return {controller,document,store,get mapCallbacks(){return mapCallbacks;},click:button=>listeners.click({target:{closest:()=>button},preventDefault(){}}),get focused(){return focused;},get focusOptions(){return focusOptions;},get submitted(){return submitted;},get renders(){return renders;},
    submit:elements=>listeners.submit({target:{id:'farmer-intake-form',elements},preventDefault(){}})};
}
test('mounted UI controller shows all six questions in order with no preselected core answers',()=>{
  const h=uiHarness(),html=h.controller.form();
  const positions=[1,2,3,4,5,6].map(n=>html.indexOf('Q'+n+'.'));
  assert.ok(positions.every(p=>p>=0));assert.deepEqual([...positions].sort((a,b)=>a-b),positions);
  assert.ok(html.indexOf('Location · required')<positions[0]);
  assert.ok(html.includes('name="priority" required'));assert.ok(html.includes('name="districtId" required'));
  assert.equal(html.includes('selected'),false);assert.equal(html.includes('use demo estimates'),false);
  assert.equal(html.includes('name="ph"'),false);assert.equal(html.includes('name="organic"'),false);
  assert.equal(h.controller.hasSubmission(),false);
});
test('invalid submit preserves draft, renders accessible field errors and focuses the first invalid field',()=>{
  const h=uiHarness({version:1,draft:{...D.blankDraft(),currentCrop:'rice'}});
  h.submit([]);assert.equal(h.submitted,null);assert.equal(h.focused,'intake-districtId');
  assert.equal(h.focusOptions.preventScroll,false);
  const html=h.controller.form();assert.ok(html.includes('role="alert"'));assert.ok(html.includes('aria-invalid="true"'));
  assert.ok(html.includes('value="rice" selected'));assert.ok(html.includes('data-intake-error="districtId"'));
  assert.equal(html.includes('districtId:'),false);
});
test('live controls are re-read on submit; invalid edits never replace the last valid submission',()=>{
  const answers=valid(),h=uiHarness({version:1,draft:answers,submitted:{answers}});
  h.submit([{name:'priority',value:'unknown'}]);
  assert.equal(h.submitted,null);assert.equal(h.focused,'intake-priority');
  const stored=JSON.parse(h.store.get('sts-farmer-intake-v1'));
  assert.equal(stored.draft.priority,'unknown');assert.equal(stored.submitted.request.priority,'water');
});
test('live form submission uses shared validation, persists only valid answers and renders unavailable summary',()=>{
  const h=uiHarness({version:1,draft:valid()});h.submit([]);
  assert.equal(h.submitted,true);assert.equal(h.controller.hasSubmission(),true);
  const stored=JSON.parse(h.store.get('sts-farmer-intake-v1'));assert.equal(stored.submitted.request.planning.status,'unavailable');
  const summary=h.controller.summary();assert.ok(summary.includes('Planning unavailable'));assert.ok(summary.includes('Bagerhat'));
  assert.equal(summary.includes('/100'),false);assert.equal(summary.includes('spinner'),false);
  h.controller.newDraft();assert.ok(h.controller.summary().includes('separate unfinished draft'));assert.equal(h.controller.hasSubmission(),true);
});
test('English/Bangla render keeps IDs unchanged and escapes restored user text',()=>{
  const answers=valid();answers.availableFrom='\"><img src=x onerror=alert(1)>';
  const h=uiHarness({version:1,draft:answers},'bn'),html=h.controller.form();
  assert.ok(html.includes('প্রশ্ন ১।'));assert.ok(html.includes('প্রশ্ন ৬।'));assert.ok(html.includes('বাগেরহাট'));
  assert.ok(html.includes('value="bd-district-bagerhat" selected'));
  assert.equal(html.includes('<img src=x'),false);assert.ok(html.includes('&lt;img'));
});
test('actual UI submit handler requires pin confirmation and supports either method without stale data',()=>{
  const L=require('../prototype/public/reference/location.js'),collection=JSON.parse(fs.readFileSync(path.join(__dirname,'../prototype/public/reference/data/district-boundaries.v1.geojson')));
  const index=L.makeIndex(collection,D.districts.map(d=>d.id)),sample=require('./fixtures/district-interior-points.json').samples[0];
  const h=uiHarness({version:1,draft:valid(),submitted:{answers:valid()}},'bn',index);
  const button=(dataset,attr)=>({dataset,hasAttribute:name=>name===attr});
  h.click(button({locationMethod:'map_pin'}));h.mapCallbacks.onBoundaries(index);h.mapCallbacks.onPin(sample.point);
  h.submit([]);assert.equal(h.focused,'intake-mapPin');assert.equal(h.submitted,null);
  assert.ok(h.controller.form().includes('অবস্থান নিশ্চিত'));
  h.click(button({},'data-map-confirm'));h.submit([]);assert.equal(h.submitted,true);
  let saved=JSON.parse(h.store.get('sts-farmer-intake-v1'));assert.equal(saved.submitted.request.location.level,'point');assert.equal(saved.submitted.request.location.district_id,sample.district_id);
  h.click(button({locationMethod:'district_search'}));
  h.submit([{name:'districtId',value:'bd-district-sylhet'}]);saved=JSON.parse(h.store.get('sts-farmer-intake-v1'));
  assert.equal(saved.submitted.request.location.level,'district');assert.equal(saved.submitted.request.location.coordinates,null);
  assert.equal(saved.draft.mapPin,null);assert.equal(saved.draft.currentCrop,'rice');
});
