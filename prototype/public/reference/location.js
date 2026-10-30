/* Administrative containment only. Uses GeoJSON [longitude, latitude]; no scientific coverage. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.STS_LOCATION=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const boundarySource=Object.freeze({id:'geoboundaries-bgd-adm2',version:'BGD-ADM2-16705992@9469f09-local1',
    sha256:'9503a358ddcb99714db5866ef049e7ddea0d5fd6e05a0d3719a6553b3953c01a',
    url:'https://www.geoboundaries.org/api/current/gbOpen/BGD/ADM2/',
    licenseUrl:'https://creativecommons.org/licenses/by/3.0/igo/'});
  const validPoint=p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite)&&Math.abs(p[0])<=180&&Math.abs(p[1])<=90;
  // A numerical segment tolerance (degrees), NOT a statement of dataset/survey accuracy.
  const EPSILON=1e-9;
  function ringRelation(point,ring){
    const [x,y]=point;let inside=false;
    for(let i=0,j=ring.length-1;i<ring.length;j=i++){
      const [ax,ay]=ring[j],[bx,by]=ring[i],dx=bx-ax,dy=by-ay,length2=dx*dx+dy*dy;
      const u=length2?Math.max(0,Math.min(1,((x-ax)*dx+(y-ay)*dy)/length2)):0;
      if((x-ax-u*dx)**2+(y-ay-u*dy)**2<=EPSILON**2)return 'border';
      if((ay>y)!==(by>y)&&x<(bx-ax)*(y-ay)/(by-ay)+ax)inside=!inside;
    }
    return inside?'inside':'outside';
  }
  function polygonRelation(point,rings){
    const outer=ringRelation(point,rings[0]);if(outer!=='inside')return outer;
    for(const hole of rings.slice(1)){const r=ringRelation(point,hole);if(r==='border')return r;if(r==='inside')return 'outside';}
    return 'inside';
  }
  function geometryRelation(point,geometry){
    const polygons=geometry.type==='Polygon'?[geometry.coordinates]:geometry.type==='MultiPolygon'?geometry.coordinates:[];
    let inside=false;
    for(const polygon of polygons){const r=polygonRelation(point,polygon);if(r==='border')return r;if(r==='inside')inside=true;}
    return inside?'inside':'outside';
  }
  function makeIndex(collection,expectedIds){
    if(collection?.type!=='FeatureCollection'||!Array.isArray(collection.features)||!collection.features.length)throw Error('Invalid boundary collection');
    const seen=new Set(),features=collection.features.map(feature=>{
      const districtId=feature.properties?.district_id,geometry=feature.geometry;
      if(typeof districtId!=='string'||seen.has(districtId)||!['Polygon','MultiPolygon'].includes(geometry?.type))throw Error('Invalid district mapping/geometry');
      seen.add(districtId);
      const polygons=geometry.type==='Polygon'?[geometry.coordinates]:geometry.coordinates;
      const bbox=[Infinity,Infinity,-Infinity,-Infinity];
      if(!polygons.length)throw Error('Empty geometry');
      for(const polygon of polygons){
        if(!polygon.length)throw Error('Missing outer ring');
        for(const ring of polygon){
          if(ring.length<4||ring[0][0]!==ring.at(-1)[0]||ring[0][1]!==ring.at(-1)[1])throw Error('Unclosed boundary ring');
          for(const point of ring){if(!validPoint(point))throw Error('Invalid boundary coordinate');bbox[0]=Math.min(bbox[0],point[0]);bbox[1]=Math.min(bbox[1],point[1]);bbox[2]=Math.max(bbox[2],point[0]);bbox[3]=Math.max(bbox[3],point[1]);}
        }
      }
      return {districtId,sourceShapeId:feature.properties.source_shape_id,geometry,bbox};
    });
    if(expectedIds&&(seen.size!==expectedIds.length||expectedIds.some(id=>!seen.has(id))))throw Error('Directory/boundary mismatch');
    return {version:collection.boundary_version,features,bbox:[Math.min(...features.map(f=>f.bbox[0])),Math.min(...features.map(f=>f.bbox[1])),Math.max(...features.map(f=>f.bbox[2])),Math.max(...features.map(f=>f.bbox[3]))]};
  }
  const inBox=(p,b)=>p[0]>=b[0]-EPSILON&&p[0]<=b[2]+EPSILON&&p[1]>=b[1]-EPSILON&&p[1]<=b[3]+EPSILON;
  function resolvePoint(point,index){
    if(!validPoint(point))return {status:'invalid'};
    if(!index?.features?.length)return {status:'unavailable'};
    if(!inBox(point,index.bbox))return {status:'outside'};
    const hits=[];
    for(const feature of index.features){
      if(!inBox(point,feature.bbox))continue;
      const relation=geometryRelation(point,feature.geometry);
      if(relation==='border')return {status:'ambiguous'};
      if(relation==='inside')hits.push(feature);
    }
    if(hits.length>1)return {status:'ambiguous'};
    return hits.length?{status:'resolved',districtId:hits[0].districtId,sourceShapeId:hits[0].sourceShapeId}:{status:'unresolved'};
  }
  function switchMethod(draft,method){
    if(!['district_search','map_pin'].includes(method))return;
    if(draft.locationMethod!==method){draft.locationMethod=method;draft.districtId='';draft.mapPin=null;}
  }
  function placePin(draft,point){
    draft.mapPin=validPoint(point)?{longitude:point[0],latitude:point[1],confirmed:false}:null;
    draft.districtId='';
  }
  function confirmPin(draft,index){
    if(index?.version!==boundarySource.version)return {status:'unavailable'};
    const pin=draft.mapPin,result=resolvePoint(pin?[pin.longitude,pin.latitude]:null,index);
    if(result.status==='resolved')draft.mapPin={...pin,confirmed:true,districtId:result.districtId,boundaryVersion:boundarySource.version};
    return result;
  }
  function normalizeLocation(draft,index,directory,source){
    const method=draft.locationMethod;
    if(!['district_search','map_pin'].includes(method))return {error:{field:'locationMethod',code:'location_method'}};
    if(method==='district_search'){
      const district=directory.find(d=>d.id===String(draft.districtId??'').trim());
      if(!district)return {error:{field:'districtId',code:'district'}};
      return {location:{country_code:'BD',district_id:district.id,level:'district',selection_method:'district_search',coordinates:null,
        provenance:{kind:'farmer_selected_district',directory_id:source.id,directory_version:source.checkedOn,source_url:source.url}}};
    }
    const pin=draft.mapPin,point=pin?[pin.longitude,pin.latitude]:null;
    if(!pin)return {error:{field:'mapPin',code:'map_pin'}};
    if(!validPoint(point))return {error:{field:'mapPin',code:'point_invalid'}};
    const result=resolvePoint(point,index);
    if(result.status!=='resolved')return {error:{field:'mapPin',code:'point_'+result.status}};
    if(pin.confirmed!==true||pin.boundaryVersion!==boundarySource.version||pin.districtId!==result.districtId||index.version!==boundarySource.version)return {error:{field:'mapPin',code:'point_confirmation'}};
    return {location:{country_code:'BD',district_id:result.districtId,level:'point',selection_method:'map_pin',coordinates:{latitude:pin.latitude,longitude:pin.longitude},
      provenance:{kind:'farmer_confirmed_map_pin',boundary_id:boundarySource.id,boundary_version:boundarySource.version,boundary_sha256:boundarySource.sha256,source_shape_id:result.sourceShapeId,source_url:boundarySource.url}}};
  }
  return {boundarySource,validPoint,ringRelation,geometryRelation,makeIndex,resolvePoint,switchMethod,placePin,confirmPin,normalizeLocation};
});
