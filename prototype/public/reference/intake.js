/* Shared by the mounted workspace and Node tests. No scientific calculations. */
(function (root, factory) {
  const api = factory(typeof module === 'object' && module.exports ? require('./location.js') : root.STS_LOCATION);
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.STS_INTAKE = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (L) {
  'use strict';
  const directorySource = Object.freeze({
    id: 'bd-national-portal-districts-2026-10-30',
    url: 'https://bangladesh.gov.bd/views/district-list',
    checkedOn: '2026-10-30',
    note: 'National Portal district membership and Bangla names; English display transliterations. Application IDs, not official geocodes. No coordinates or scientific coverage implied.'
  });
  const districtGroups = {
    Dhaka: [
      ['dhaka','Dhaka','ঢাকা'], ['faridpur','Faridpur','ফরিদপুর'], ['gazipur','Gazipur','গাজীপুর'],
      ['gopalganj','Gopalganj','গোপালগঞ্জ'], ['kishoreganj','Kishoreganj','কিশোরগঞ্জ'], ['madaripur','Madaripur','মাদারীপুর'],
      ['manikganj','Manikganj','মানিকগঞ্জ'], ['munshiganj','Munshiganj','মুন্সীগঞ্জ'], ['narayanganj','Narayanganj','নারায়ণগঞ্জ'],
      ['narsingdi','Narsingdi','নরসিংদী'], ['rajbari','Rajbari','রাজবাড়ী'], ['shariatpur','Shariatpur','শরীয়তপুর'], ['tangail','Tangail','টাঙ্গাইল']
    ],
    Khulna: [
      ['bagerhat','Bagerhat','বাগেরহাট'], ['chuadanga','Chuadanga','চুয়াডাঙ্গা'], ['jashore','Jashore','যশোর'],
      ['jhenaidah','Jhenaidah','ঝিনাইদহ'], ['khulna','Khulna','খুলনা'], ['kushtia','Kushtia','কুষ্টিয়া'],
      ['magura','Magura','মাগুরা'], ['meherpur','Meherpur','মেহেরপুর'], ['narail','Narail','নড়াইল'], ['satkhira','Satkhira','সাতক্ষীরা']
    ],
    Chattogram: [
      ['bandarban','Bandarban','বান্দরবান'], ['brahmanbaria','Brahmanbaria','ব্রাহ্মণবাড়িয়া'], ['chandpur','Chandpur','চাঁদপুর'],
      ['chattogram','Chattogram','চট্টগ্রাম'], ['cumilla','Cumilla','কুমিল্লা'], ['coxs-bazar',"Cox's Bazar",'কক্সবাজার'],
      ['feni','Feni','ফেনী'], ['khagrachhari','Khagrachhari','খাগড়াছড়ি'], ['lakshmipur','Lakshmipur','লক্ষ্মীপুর'],
      ['noakhali','Noakhali','নোয়াখালী'], ['rangamati','Rangamati','রাঙ্গামাটি পার্বত্য']
    ],
    Rajshahi: [
      ['bogura','Bogura','বগুড়া'], ['joypurhat','Joypurhat','জয়পুরহাট'], ['naogaon','Naogaon','নওগাঁ'], ['natore','Natore','নাটোর'],
      ['chapainawabganj','Chapainawabganj','চাঁপাইনবাবগঞ্জ'], ['pabna','Pabna','পাবনা'], ['rajshahi','Rajshahi','রাজশাহী'], ['sirajganj','Sirajganj','সিরাজগঞ্জ']
    ],
    Sylhet: [
      ['habiganj','Habiganj','হবিগঞ্জ'], ['moulvibazar','Moulvibazar','মৌলভীবাজার'], ['sunamganj','Sunamganj','সুনামগঞ্জ'], ['sylhet','Sylhet','সিলেট']
    ],
    Rangpur: [
      ['dinajpur','Dinajpur','দিনাজপুর'], ['gaibandha','Gaibandha','গাইবান্ধা'], ['kurigram','Kurigram','কুড়িগ্রাম'], ['lalmonirhat','Lalmonirhat','লালমনিরহাট'],
      ['nilphamari','Nilphamari','নীলফামারী'], ['panchagarh','Panchagarh','পঞ্চগড়'], ['rangpur','Rangpur','রংপুর'], ['thakurgaon','Thakurgaon','ঠাকুরগাঁও']
    ],
    Mymensingh: [
      ['jamalpur','Jamalpur','জামালপুর'], ['mymensingh','Mymensingh','ময়মনসিংহ'], ['netrokona','Netrokona','নেত্রকোণা'], ['sherpur','Sherpur','শেরপুর']
    ],
    Barishal: [
      ['barguna','Barguna','বরগুনা'], ['barishal','Barishal','বরিশাল'], ['bhola','Bhola','ভোলা'],
      ['jhalakathi','Jhalakathi','ঝালকাঠি'], ['patuakhali','Patuakhali','পটুয়াখালী'], ['pirojpur','Pirojpur','পিরোজপুর']
    ]
  };
  const districts = Object.freeze(Object.entries(districtGroups).flatMap(([division, rows]) =>
    rows.map(([slug,en,bn]) => Object.freeze({ id: 'bd-district-' + slug, en, bn, division, sourceId: directorySource.id }))
  ).sort((a,b) => a.en.localeCompare(b.en, 'en')));
  // Intake identities only: none of these records asserts regional suitability.
  const crops = Object.freeze([
    ['rice','Rice','ধান'], ['maize','Maize','ভুট্টা'], ['lentil','Lentil','মসুর'],
    ['mustard','Mustard','সরিষা'], ['mungbean','Mungbean','মুগ'], ['sesame','Sesame','তিল'], ['jute','Jute','পাট']
  ].map(([id,en,bn]) => Object.freeze({id,en,bn})));
  const seasons = Object.freeze([
    {id:'kharif_1',en:'Kharif I',bn:'খরিফ–১'}, {id:'kharif_2',en:'Kharif II',bn:'খরিফ–২'}, {id:'rabi',en:'Rabi',bn:'রবি'}
  ]);
  const text = value => typeof value === 'string' ? value.trim() : '';
  const has = (items, value) => items.some(item => item.id === text(value));
  const row = () => ({cropId:'', timing:'season_year', seasonId:'', year:'', start:'', end:''});
  function blankDraft() {
    return {locationMethod:'district_search',mapPin:null,districtId:'',currentCrop:'',currentSownOn:'',availabilityType:'',availableFrom:'',availableTo:'',availabilityBasis:'',
      historyState:'',history:[row()],baselineState:'',baseline:[row()],water:'',seasonalLimits:'',limitedSeasons:[],priority:''};
  }
  function restoreDraft(value) {
    const draft = blankDraft();
    if (!value || typeof value !== 'object') return draft;
    for (const key of Object.keys(draft)) {
      if (typeof draft[key] === 'string' && typeof value[key] === 'string') draft[key] = value[key].slice(0,200);
    }
    for (const key of ['history','baseline']) if (Array.isArray(value[key]) && value[key].length) {
      draft[key] = value[key].slice(0,20).map(item => Object.fromEntries(Object.keys(row()).map(k => [k,text(item?.[k]).slice(0,200)])));
    }
    if (value.mapPin && typeof value.mapPin === 'object') draft.mapPin = Object.fromEntries(['longitude','latitude','confirmed','districtId','boundaryVersion'].filter(k=>Object.hasOwn(value.mapPin,k)).map(k=>[k,value.mapPin[k]]));
    draft.limitedSeasons = Array.isArray(value.limitedSeasons) ? value.limitedSeasons.filter(v => typeof v === 'string').slice(0,3) : [];
    return draft;
  }
  function validDate(value) {
    const s = text(value);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(s) || s.slice(0,4) === '0000') return false;
    const date = new Date(s + 'T00:00:00Z');
    return Number.isFinite(date.getTime()) && date.toISOString().slice(0,10) === s;
  }
  // Ordering convention for reported seasons, not planting-window or crop-duration advice.
  // Rabi's year is the year the season starts (November); Jan/Feb belong to the preceding year.
  function dateSeasonKey(date) {
    const year = Number(date.slice(0,4)), month = Number(date.slice(5,7));
    return month < 3 ? (year-1)*3+2 : year*3+(month<7?0:month<11?1:2);
  }
  function validateAndNormalize(raw, boundaryIndex) {
    const d = raw && typeof raw === 'object' ? raw : {};
    const errors = [];
    const error = (field,code) => errors.push({field,code});
    const location = L.normalizeLocation(d,boundaryIndex,districts,directorySource);
    if (location.error) errors.push(location.error);
    if (!has(crops,d.currentCrop) && text(d.currentCrop) !== 'fallow') error('currentCrop','current_crop');
    if (text(d.currentCrop) !== 'fallow' && text(d.currentSownOn) && !validDate(d.currentSownOn)) error('currentSownOn','date');
    if (!['date','window'].includes(text(d.availabilityType))) error('availabilityType','availability_type');
    if (!validDate(d.availableFrom)) error('availableFrom','date');
    if (text(d.availabilityType) === 'window') {
      if (!validDate(d.availableTo)) error('availableTo','date');
      else if (validDate(d.availableFrom) && text(d.availableTo) < text(d.availableFrom)) error('availableTo','window_order');
    }
    if (!['expected','farmer_estimate'].includes(text(d.availabilityBasis))) error('availabilityBasis','date_basis');
    if (text(d.currentCrop) !== 'fallow' && validDate(d.currentSownOn) && validDate(d.availableFrom) && text(d.currentSownOn) > text(d.availableFrom)) error('availableFrom','before_sowing');
    function entries(key, allowFallow) {
      const items = Array.isArray(d[key]) ? d[key] : [];
      if (!items.length || items.length > 20) { error(key + 'State','entries'); return []; }
      let previous = null;
      return items.map((item,index) => {
        const r = item && typeof item === 'object' ? item : {}, prefix = key + '-' + index + '-';
        if (!has(crops,r.cropId) && !(allowFallow && text(r.cropId) === 'fallow')) error(prefix+'cropId','crop');
        const normalized = {kind: text(r.cropId) === 'fallow' ? 'fallow' : 'crop', crop_id: text(r.cropId) === 'fallow' ? null : text(r.cropId)};
        let startKey = null, endKey = null;
        if (text(r.timing) === 'dates') {
          if (!validDate(r.start)) error(prefix+'start','date');
          if (!validDate(r.end)) error(prefix+'end','date');
          if (validDate(r.start) && validDate(r.end)) {
            if (text(r.end) < text(r.start)) error(prefix+'end','window_order');
            startKey = dateSeasonKey(text(r.start)); endKey = dateSeasonKey(text(r.end));
            if (previous?.endDate && text(r.start) <= previous.endDate) error(prefix+'start','entry_order');
            if (validDate(d.availableFrom)) {
              if (key === 'history' && text(r.end) > text(d.availableFrom)) error(prefix+'end','history_after_availability');
              if (key === 'baseline' && text(r.start) < text(d.availableFrom)) error(prefix+'start','baseline_before_availability');
            }
            if (key === 'history' && text(d.currentCrop) !== 'fallow' && validDate(d.currentSownOn) && text(r.end) > text(d.currentSownOn)) error(prefix+'end','history_after_sowing');
          }
          normalized.period = {kind:'dates',start:text(r.start),end:text(r.end)};
        } else if (text(r.timing) === 'season_year') {
          if (!has(seasons,r.seasonId)) error(prefix+'seasonId','season');
          if (!/^[1-9]\d{3}$/.test(text(r.year))) error(prefix+'year','year');
          if (has(seasons,r.seasonId) && /^[1-9]\d{3}$/.test(text(r.year))) {
            startKey = endKey = Number(text(r.year))*3 + seasons.findIndex(s=>s.id===text(r.seasonId));
            if (validDate(d.availableFrom)) {
              if (key === 'history' && endKey > dateSeasonKey(text(d.availableFrom))) error(prefix+'seasonId','history_after_availability');
              if (key === 'baseline' && startKey < dateSeasonKey(text(d.availableFrom))) error(prefix+'seasonId','baseline_before_availability');
            }
            if (key === 'history' && text(d.currentCrop) !== 'fallow' && validDate(d.currentSownOn) && endKey > dateSeasonKey(text(d.currentSownOn))) error(prefix+'seasonId','history_after_sowing');
          }
          normalized.period = {kind:'season_year',season_id:text(r.seasonId),year:Number(text(r.year))};
        } else error(prefix+'timing','timing');
        if (startKey !== null && previous && (startKey < previous.endKey || (startKey === previous.endKey && !(text(r.timing)==='dates' && previous.endDate)))) error(prefix+(text(r.timing)==='dates'?'start':'seasonId'),'entry_order');
        previous = {endKey,endDate:text(r.timing)==='dates' && validDate(r.end) ? text(r.end) : null};
        return normalized;
      });
    }
    let history = [], baseline = [];
    if (text(d.historyState) === 'entries') history = entries('history',false);
    else if (text(d.historyState) !== 'first_cultivation') error('historyState','history');
    if (text(d.baselineState) === 'sequence') baseline = entries('baseline',true);
    else if (text(d.baselineState) !== 'no_established_rotation') error('baselineState','baseline');
    if (!['rainfed','limited','reliable'].includes(text(d.water))) error('water','water');
    let limitedSeasons = [];
    if (['limited','reliable'].includes(text(d.water))) {
      if (!['none','seasonal'].includes(text(d.seasonalLimits))) error('seasonalLimits','seasonal_limits');
      if (text(d.seasonalLimits) === 'seasonal') {
        const values = Array.isArray(d.limitedSeasons) ? d.limitedSeasons : [];
        if (!values.length || values.some(v=>!has(seasons,v)) || new Set(values).size !== values.length) error('limitedSeasons','limited_seasons');
        limitedSeasons = seasons.filter(s=>values.includes(s.id)).map(s=>s.id);
      }
    }
    if (!['water','soil_rotation','balanced'].includes(text(d.priority))) error('priority','priority');
    if (errors.length) return {ok:false,errors,request:null};
    return {ok:true,errors:[],request:{
      schema_version:'farmer-intake.v2',
      location:location.location,
      current:{state:text(d.currentCrop)==='fallow'?'fallow':'growing',crop_id:text(d.currentCrop)==='fallow'?null:text(d.currentCrop),
        sown_on:text(d.currentCrop)!=='fallow'&&text(d.currentSownOn)?text(d.currentSownOn):null},
      availability:{kind:text(d.availabilityType),start:text(d.availableFrom),end:text(d.availabilityType)==='window'?text(d.availableTo):text(d.availableFrom),
        basis:text(d.availabilityBasis),applies_to:text(d.currentCrop)==='fallow'?'available_from':'after_harvest'},
      crop_history:{state:text(d.historyState),entries:history,provenance:'farmer_reported',rotation_risks_assessed:false},
      baseline:{state:text(d.baselineState),segments:baseline,provenance:'farmer_reported',assessed:false},
      irrigation:{access:text(d.water),seasonal_limitations:text(d.water)==='rainfed'?'not_applicable':text(d.seasonalLimits),limited_seasons:limitedSeasons},
      priority:text(d.priority),
      planning:{status:'unavailable',reason:'scientific_api_not_connected',comparison_status:'unavailable'}
    }};
  }
  function loadSaved(value,boundaryIndex) {
    const result = {draft:blankDraft(),submitted:null,pendingSubmission:null};
    if (![1,2].includes(value?.version)) return result;
    const migrate = raw => {
      const draft=restoreDraft(raw);
      // v1 has genuine district answers only, regardless of incidental/legacy coordinate keys.
      if(value.version===1){draft.locationMethod='district_search';draft.mapPin=null;}
      return draft;
    };
    result.draft = migrate(value.draft);
    if (value.submitted?.answers) {
      const answers=migrate(value.submitted.answers),checked=validateAndNormalize(answers,boundaryIndex);
      if(checked.ok)result.submitted={answers,request:checked.request};
      else if(answers.locationMethod==='map_pin'&&checked.errors.every(e=>e.code==='point_unavailable'))result.pendingSubmission={answers};
    }
    return result;
  }
  return {directorySource,districts,crops,seasons,blankDraft,restoreDraft,validDate,validateAndNormalize,loadSaved,row};
});
