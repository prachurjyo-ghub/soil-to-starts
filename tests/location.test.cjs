const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const crypto=require('node:crypto');
const zlib=require('node:zlib');
const L=require('../prototype/public/reference/location.js');
const D=require('../prototype/public/reference/intake.js');
const bytes=fs.readFileSync(path.join(__dirname,'../prototype/public/reference/data/district-boundaries.v1.geojson'));
const collection=JSON.parse(bytes),index=L.makeIndex(collection,D.districts.map(d=>d.id));
const fixtures=require('./fixtures/district-interior-points.json');
const sample=fixtures.samples.find(s=>s.district_id==='bd-district-dhaka');
const square=(x,y,size)=>[[x,y],[x+size,y],[x+size,y+size],[x,y+size],[x,y]];
const feature=(id,geometry)=>({type:'Feature',properties:{district_id:id},geometry});
const polygon=rings=>({type:'Polygon',coordinates:rings});
function answers(){return {...D.blankDraft(),districtId:'bd-district-dhaka',currentCrop:'fallow',availabilityType:'date',availableFrom:'2026-11-15',availabilityBasis:'farmer_estimate',historyState:'first_cultivation',baselineState:'no_established_rotation',water:'rainfed',priority:'balanced'};}
function pointAnswers(){const d=answers();L.switchMethod(d,'map_pin');L.placePin(d,sample.point);L.confirmPin(d,index);return d;}

test('pinned source/license/checksums and all 64 exact boundary mappings agree',()=>{
  const manifest=require('../prototype/public/reference/data/district-boundaries.manifest.json');
  const mapping=require('../data/admin/bgd-adm2-mapping.json');
  const raw=zlib.gunzipSync(fs.readFileSync(path.join(__dirname,'../data/admin/bgd-adm2-source.geojson.gz')));
  const source=JSON.parse(raw);
  assert.equal(crypto.createHash('sha256').update(raw).digest('hex'),manifest.source_sha256);
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),L.boundarySource.sha256);
  assert.equal(manifest.processed_sha256,L.boundarySource.sha256);assert.equal(manifest.processed_bytes,bytes.length);
  assert.equal(manifest.license_url,'https://creativecommons.org/licenses/by/3.0/igo/');
  assert.equal(manifest.represented_year,'2020');assert.equal(collection.features.length,64);
  assert.equal(new Set(mapping.map(row=>row.district_id)).size,64);
  for(const row of mapping){const f=source.features.find(f=>f.properties.shapeID===row.source_shape_id);assert.ok(f);assert.equal(f.properties.shapeName,row.source_name);assert.ok(D.districts.some(d=>d.id===row.district_id));}
  assert.equal(mapping.find(row=>row.source_name==='Nawabganj').district_id,'bd-district-chapainawabganj');
  assert.equal(mapping.find(row=>row.source_name==='Brahamanbaria').district_id,'bd-district-brahmanbaria');
});
test('Polygon, holes, MultiPolygon and numerical border handling',()=>{
  const g=polygon([square(0,0,10),square(3,3,2)]);
  assert.equal(L.geometryRelation([1,1],g),'inside');assert.equal(L.geometryRelation([4,4],g),'outside');
  assert.equal(L.geometryRelation([3,4],g),'border');assert.equal(L.geometryRelation([0,5],g),'border');
  const multi={type:'MultiPolygon',coordinates:[[square(0,0,2)],[square(5,5,2)]]};
  assert.equal(L.geometryRelation([6,6],multi),'inside');assert.equal(L.geometryRelation([4,4],multi),'outside');
});
test('outside, unresolved holes/gaps, overlap and shared borders never snap to a district',()=>{
  const x=L.makeIndex({type:'FeatureCollection',features:[feature('a',polygon([square(0,0,10),square(2,2,2)])),feature('b',polygon([square(8,0,10)]))]});
  assert.equal(L.resolvePoint([1,1],x).districtId,'a');
  assert.equal(L.resolvePoint([9,1],x).status,'ambiguous');
  assert.equal(L.resolvePoint([3,3],x).status,'unresolved');
  assert.equal(L.resolvePoint([-1,1],x).status,'outside');
  assert.equal(L.resolvePoint([8,1],x).status,'ambiguous');
  assert.equal(L.resolvePoint([1,1],null).status,'unavailable');
});
test('invalid, non-finite and reversed longitude/latitude inputs are rejected',()=>{
  for(const p of [null,[],['90','24'],[90,NaN],[Infinity,24],[90,91],[181,24],[90,24,3]])assert.equal(L.resolvePoint(p,index).status,'invalid');
  assert.equal(L.resolvePoint([sample.point[1],sample.point[0]],index).status,'invalid');
});
test('64 independent source-derived interiors resolve and normalize to their explicit district IDs',()=>{
  assert.equal(fixtures.samples.length,64);assert.equal(fixtures.boundary_version,L.boundarySource.version);
  for(const f of fixtures.samples){
    const result=L.resolvePoint(f.point,index);assert.equal(result.status,'resolved',f.district_id);assert.equal(result.districtId,f.district_id);assert.equal(result.sourceShapeId,f.source_shape_id);
    const d=answers();L.switchMethod(d,'map_pin');L.placePin(d,f.point);
    assert.equal(D.validateAndNormalize(d,index).ok,false);L.confirmPin(d,index);
    const r=D.validateAndNormalize(d,index);assert.equal(r.ok,true);assert.equal(r.request.location.district_id,f.district_id);
    assert.deepEqual(r.request.location.coordinates,{longitude:f.point[0],latitude:f.point[1]});
    assert.equal(r.request.planning.status,'unavailable');
  }
});
test('new/moved pin needs confirmation and stale district, source version or geometry cannot pass',()=>{
  const d=pointAnswers();assert.equal(D.validateAndNormalize(d,index).ok,true);
  L.placePin(d,sample.point);assert.equal(d.mapPin.confirmed,false);assert.equal(D.validateAndNormalize(d,index).ok,false);
  L.confirmPin(d,index);d.mapPin.districtId='bd-district-khulna';assert.equal(D.validateAndNormalize(d,index).ok,false);
  L.confirmPin(d,index);d.mapPin.boundaryVersion='old';assert.equal(D.validateAndNormalize(d,index).ok,false);
  L.confirmPin(d,index);assert.equal(D.validateAndNormalize(d).ok,false);
});
test('method switching clears inactive coordinates/districts and district search needs no boundaries',()=>{
  const d=pointAnswers();L.switchMethod(d,'district_search');assert.equal(d.mapPin,null);assert.equal(d.districtId,'');
  assert.equal(D.validateAndNormalize(d,index).ok,false);d.districtId='bd-district-bagerhat';
  d.mapPin={longitude:99,latitude:1,confirmed:true};
  const r=D.validateAndNormalize(d);assert.equal(r.ok,true);assert.equal(r.request.location.coordinates,null);assert.equal(r.request.location.selection_method,'district_search');
  assert.equal(r.request.location.provenance.directory_version,D.directorySource.checkedOn);
  L.switchMethod(d,'map_pin');assert.equal(d.districtId,'');assert.equal(d.mapPin,null);assert.equal(d.currentCrop,'fallow');assert.equal(d.priority,'balanced');
});
test('genuine v1 district answers migrate to v2 without coordinates or demo defaults',()=>{
  const old=answers();delete old.locationMethod;old.mapPin={longitude:99,latitude:1,confirmed:true};
  const saved=D.loadSaved({version:1,draft:old,submitted:{answers:old}},index);
  assert.equal(saved.draft.locationMethod,'district_search');assert.equal(saved.draft.mapPin,null);
  assert.equal(saved.submitted.request.schema_version,'farmer-intake.v2');assert.equal(saved.submitted.request.location.coordinates,null);
  const pending=D.loadSaved({version:2,draft:pointAnswers(),submitted:{answers:pointAnswers()}});
  assert.equal(pending.submitted,null);assert.ok(pending.pendingSubmission);
  const restored=D.loadSaved({version:2,draft:pending.draft,submitted:pending.pendingSubmission},index);
  assert.equal(restored.submitted.request.location.level,'point');
});
test('boundary loader rejects missing/duplicate mappings and unsupported or broken rings',()=>{
  const c=structuredClone(collection);c.features.pop();assert.throws(()=>L.makeIndex(c,D.districts.map(d=>d.id)));
  const duplicate=structuredClone(collection);duplicate.features[1]=duplicate.features[0];assert.throws(()=>L.makeIndex(duplicate));
  assert.throws(()=>L.makeIndex({type:'FeatureCollection',features:[feature('a',{type:'Point',coordinates:[1,1]})]}));
  assert.throws(()=>L.makeIndex({type:'FeatureCollection',features:[feature('a',polygon([[[0,0],[1,0],[1,1],[0,1]]]))]}));
});

function mapHarness({webglFail=false,networkFail=false}={}){
  let currentHost,instances=0,removals=0,resizes=0,lastMap,options;
  const listeners={},statuses=[],d=answers();d.locationMethod='map_pin';
  const element=()=>({id:'intake-map-host',isConnected:true,remove(){this.isConnected=false;},replaceWith(node){this.isConnected=false;node.isConnected=true;currentHost=node;},setAttribute(){},addEventListener(){},classList:{toggle(){}}});
  currentHost=element();
  class MapMock{
    constructor(config){if(webglFail)throw Error('WebGL disabled');instances++;this.handlers={};lastMap=this;options=config;}
    on(type,fn){this.handlers[type]=fn;if(type==='load')queueMicrotask(fn);return this;}
    addControl(){} addSource(){} addLayer(){} fitBounds(){} jumpTo(){}
    getCenter(){return {lng:sample.point[0],lat:sample.point[1]};} getZoom(){return 6;}
    resize(){resizes++;}remove(){removals++;}project(){return {x:100,y:100};}unproject(){return this.getCenter();}
  }
  class MarkerMock{
    constructor({element}){this.el=element;}setLngLat(){return this;}addTo(){return this;}on(){return this;}remove(){}getElement(){return this.el;}
  }
  const document={getElementById:id=>id==='intake-map-host'?currentHost:null,createElement:element,addEventListener:(type,fn)=>listeners[type]=fn,removeEventListener:()=>{}};
  const window={STS_LOCATION:L,STS_INTAKE:D,STS_LOAD_MAPLIBRE:async()=>({Map:MapMock,Marker:MarkerMock,NavigationControl:class{},AttributionControl:class{}})};
  const fetch=async()=>{if(networkFail)throw Error('Offline');return {ok:true,arrayBuffer:async()=>bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength)};};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../prototype/public/reference/intake-map.js'),'utf8'),{window,document,fetch,crypto:crypto.webcrypto,TextDecoder,AbortSignal,setTimeout,clearTimeout,queueMicrotask});
  const manager=window.STS_INTAKE_MAP.create({getDraft:()=>d,onPin:p=>L.placePin(d,p),onBoundaries:()=>{},onStatus:s=>statuses.push(s),t:s=>s});
  return {manager,d,statuses,get options(){return options;},fire:type=>lastMap.handlers[type]?.(),get instances(){return instances;},get removals(){return removals;},get resizes(){return resizes;},newPlaceholder(){currentHost=element();}};
}
test('map rerenders reuse one instance/listeners and preserve pin/answers; leaving removes resources',async()=>{
  const h=mapHarness();await h.manager.afterRender();await new Promise(resolve=>setImmediate(resolve));
  assert.equal(h.d.mapPin,null);assert.equal(h.instances,1);assert.equal(h.manager.isReady(),true);
  assert.equal(h.options.hash,false);assert.equal(h.options.cooperativeGestures,true);assert.ok(h.options.locale['Map.Title']);
  h.manager.placeCenter();assert.equal(h.d.mapPin.confirmed,false);
  L.confirmPin(h.d,index);const before=structuredClone(h.d);
  h.manager.beforeRender();h.newPlaceholder();await h.manager.afterRender();
  assert.equal(h.instances,1);assert.equal(h.resizes,1);assert.deepEqual(h.d,before);
  h.manager.destroy();assert.equal(h.removals,1);
});
test('WebGL and boundary-network failure retain answers and leave district fallback independent',async()=>{
  for(const config of [{webglFail:true},{networkFail:true}]){
    const h=mapHarness(config),before=structuredClone(h.d);await h.manager.afterRender();
    assert.ok(h.statuses.includes('map_failed'));assert.deepEqual(h.d,before);
    L.switchMethod(h.d,'district_search');h.d.districtId='bd-district-dhaka';assert.equal(D.validateAndNormalize(h.d).ok,true);
    h.manager.destroy();
  }
});
test('tile errors and lost WebGL context surface fallback without destroying other answers',async()=>{
  const h=mapHarness();await h.manager.afterRender();await new Promise(resolve=>setImmediate(resolve));
  const before=structuredClone(h.d);h.fire('error');assert.ok(h.statuses.includes('map_tiles_failed'));assert.deepEqual(h.d,before);
  h.fire('webglcontextlost');assert.equal(h.manager.isReady(),false);assert.ok(h.statuses.includes('map_failed'));
  L.switchMethod(h.d,'district_search');h.d.districtId='bd-district-dhaka';assert.equal(D.validateAndNormalize(h.d).ok,true);
  h.manager.destroy();
});
