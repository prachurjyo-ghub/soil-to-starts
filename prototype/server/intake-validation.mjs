import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
const require=createRequire(path.join(process.cwd(),'package.json'));
const intake=require(path.join(process.cwd(),'public/reference/intake.js'));
const location=require(path.join(process.cwd(),'public/reference/location.js'));
let boundary;
export class InputError extends Error { constructor(message,errors=[]){super(message);this.errors=errors;} }
function index(){
 if(!boundary){const raw=fs.readFileSync(path.join(process.cwd(),'public/reference/data/district-boundaries.v1.geojson'));
 if(createHash('sha256').update(raw).digest('hex')!==location.boundarySource.sha256)throw new Error('Pinned administrative geometry changed');
 boundary=location.makeIndex(JSON.parse(raw),intake.districts.map(d=>d.id));
 }
 return boundary;
}
export function validateIntake(raw){
 if(!raw||Array.isArray(raw)||raw.schema_version!=='farmer-intake.v2')throw new InputError('Expected farmer-intake.v2');
 for(const group of ['location','current','availability','crop_history','baseline','irrigation'])if(!raw[group]||Array.isArray(raw[group])||typeof raw[group]!=='object')throw new InputError('Missing input group: '+group);
 const l=raw.location,c=raw.current,a=raw.availability;
 if(!['growing','fallow'].includes(c.state)||c.state==='fallow'&&c.crop_id!==null||c.state==='growing'&&!intake.crops.some(v=>v.id===c.crop_id))throw new InputError('Invalid current crop identity/state');
 if(l.country_code!=='BD'||!['district_search','map_pin'].includes(l.selection_method))throw new InputError('Invalid location');
 if(l.selection_method==='district_search'&&(l.coordinates!==null||l.level!=='district'))throw new InputError('District selection must not invent farm coordinates');
 if(l.selection_method==='map_pin'&&(!l.coordinates||l.level!=='point'||l.provenance?.boundary_version!==location.boundarySource.version))throw new InputError('Unconfirmed or unsupported map provenance');
 if(!['date','window'].includes(a.kind)||a.kind==='date'&&a.start!==a.end||a.applies_to!==(c.state==='fallow'?'available_from':'after_harvest'))throw new InputError('Invalid availability semantics');
 const h=raw.crop_history,b=raw.baseline;
 if(!Array.isArray(h.entries)||!Array.isArray(b.segments)||h.entries.length>20||b.segments.length>20)throw new InputError('Invalid crop history/baseline entries');
 if(h.state==='first_cultivation'&&h.entries.length||b.state==='no_established_rotation'&&b.segments.length)throw new InputError('Absence states cannot carry hidden crops');
 function entries(list,allowFallow){return list.map(item=>{
  if(!item||typeof item!=='object'||!item.period||!['crop',...(allowFallow?['fallow']:[])].includes(item.kind))throw new InputError('Invalid crop entry');
  if(item.kind==='fallow'&&item.crop_id!==null)throw new InputError('Fallow has no crop ID');
  const p=item.period;
  if(!['dates','season_year'].includes(p.kind)||p.kind==='season_year'&&!Number.isInteger(p.year))throw new InputError('Invalid period');
  return {cropId:item.kind==='fallow'?'fallow':item.crop_id,timing:p.kind,start:p.start,end:p.end,seasonId:p.season_id,year:p.kind==='season_year'?String(p.year):undefined};
 });}
 const draft={...intake.blankDraft(),locationMethod:l.selection_method,districtId:l.district_id,currentCrop:c.state==='fallow'?'fallow':c.crop_id,currentSownOn:c.sown_on||'',availabilityType:a.kind,availableFrom:a.start,availableTo:a.end,availabilityBasis:a.basis,historyState:h.state,history:entries(h.entries,false),baselineState:b.state,baseline:entries(b.segments,true),water:raw.irrigation.access,seasonalLimits:raw.irrigation.seasonal_limitations,limitedSeasons:raw.irrigation.limited_seasons,priority:raw.priority};
 let geo;
 if(l.selection_method==='map_pin'){
  const p=l.coordinates;geo=index();const resolved=location.resolvePoint([p.longitude,p.latitude],geo);
  if(resolved.status!=='resolved'||resolved.districtId!==l.district_id)throw new InputError('Map point and claimed district do not agree');
  draft.mapPin={...p,confirmed:true,districtId:l.district_id,boundaryVersion:l.provenance.boundary_version};
 }
 const result=intake.validateAndNormalize(draft,geo);
 if(!result.ok)throw new InputError('Please correct the field inputs.',result.errors);
 return result.request;
}
