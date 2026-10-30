(function () {
  'use strict';
  const D = window.STS_INTAKE, L = window.STS_LOCATION;
  const esc = value => String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const copy = {
    mapMethod:['Choose on map','মানচিত্রে বেছে নিন'], districtMethod:['Search district by name','নাম দিয়ে জেলা খুঁজুন'],
    locationMethod:['Location selection method','অবস্থান বেছে নেওয়ার পদ্ধতি'], mapPin:['Field location on map','মানচিত্রে জমির অবস্থান'],
    mapLabel:['Field location map','জমির অবস্থানের মানচিত্র'], pinLabel:['Field pin. Drag or use arrow keys to move; confirm again after moving.','জমির পিন। টেনে বা অ্যারো কী দিয়ে সরান; সরানোর পর আবার নিশ্চিত করুন।'],
    zoomIn:['Zoom in','কাছে দেখুন'], zoomOut:['Zoom out','দূরে দেখুন'], touchMap:['Use two fingers to move the map','দুই আঙুল দিয়ে মানচিত্র সরান'], scrollMap:['Hold Ctrl or ⌘ to zoom with the scroll wheel','স্ক্রল দিয়ে জুম করতে Ctrl বা ⌘ চেপে রাখুন'],
    mapHelp:['Street/reference basemap, not satellite imagery. Zoom/pan and click or tap to place a pin; drag it to move. Keyboard: pan with arrow keys, place a pin at the map center, then confirm. Use two fingers to pan on touch screens.','এটি সড়ক/রেফারেন্স মানচিত্র, স্যাটেলাইটের ছবি নয়। জুম/সরিয়ে ক্লিক বা ট্যাপ করে পিন দিন, টেনে সরান। কিবোর্ডে অ্যারো কী দিয়ে মানচিত্র সরিয়ে কেন্দ্রে পিন দিন, তারপর নিশ্চিত করুন। টাচস্ক্রিনে দুই আঙুল দিয়ে মানচিত্র সরান।'],
    centerPin:['Place pin at map center','মানচিত্রের কেন্দ্রে পিন দিন'], confirmPin:['Confirm this location','এই অবস্থান নিশ্চিত করুন'], retryMap:['Retry map','মানচিত্র আবার চালু করুন'],
    map_loading:['Loading map and local district boundaries… District search remains available.','মানচিত্র ও স্থানীয় জেলার সীমানা লোড হচ্ছে… জেলা অনুসন্ধান ব্যবহার করতে পারেন।'],
    map_ready:['Map ready. Place or move a pin, then confirm it.','মানচিত্র প্রস্তুত। পিন দিন বা সরান, তারপর নিশ্চিত করুন।'],
    map_failed:['Map unavailable (WebGL, initialization or boundary loading). Your other answers are retained. Use district search or retry.','মানচিত্র অনুপলব্ধ (WebGL, চালু হওয়া বা সীমানা লোডে সমস্যা)। অন্য উত্তরগুলো রাখা আছে। জেলা অনুসন্ধান ব্যবহার করুন বা আবার চেষ্টা করুন।'],
    map_tiles_failed:['Some basemap tiles could not load. Your answers are retained; retry or use district search.','মানচিত্রের কিছু টাইল লোড হয়নি। উত্তরগুলো রাখা আছে; আবার চেষ্টা করুন বা জেলা অনুসন্ধান ব্যবহার করুন।'],
    pin_unconfirmed:['Pin placed · confirmation required','পিন দেওয়া হয়েছে · নিশ্চিত করা আবশ্যক'], pin_confirmed:['Confirmed map location','মানচিত্রের অবস্থান নিশ্চিত হয়েছে'],
    pointNote:['A farmer-selected pin is not a surveyed field boundary. Administrative geometry is approximate; a precise pin does not give NASA grids field-level resolution.','কৃষকের বেছে নেওয়া পিন জরিপ করা জমির সীমানা নয়। প্রশাসনিক সীমানা আনুমানিক; নির্দিষ্ট পিন দিলেও NASA গ্রিডের তথ্য জমির নির্দিষ্ট পরিমাপ হয়ে যায় না।'],
    pendingSaved:['Last submitted inputs are retained, but the saved pin needs local boundary rechecking. Edit the location or use district search if loading fails.','সর্বশেষ জমা দেওয়া তথ্য রাখা আছে, তবে সংরক্ষিত পিনের স্থানীয় সীমানা আবার যাচাই করা প্রয়োজন। লোড ব্যর্থ হলে অবস্থান সংশোধন করুন বা জেলা অনুসন্ধান ব্যবহার করুন।'],
    title:['Your knowledge is the starting point.','আপনার অভিজ্ঞতা দিয়েই শুরু।'],
    intro:['Choose a location on the map or select a district, then answer all six questions. Your answers stay in this browser.','মানচিত্রে অবস্থান বা জেলা বেছে ছয়টি প্রশ্নের উত্তর দিন। উত্তর এই ব্রাউজারেই থাকবে।'],
    draft:['Unfinished draft · not submitted or scientifically assessed.','অসমাপ্ত খসড়া · জমা দেওয়া বা বৈজ্ঞানিক মূল্যায়ন করা হয়নি।'],
    location:['Location · required','অবস্থান · আবশ্যক'], search:['Search districts in English or Bangla','ইংরেজি বা বাংলায় জেলা খুঁজুন'], district:['District','জেলা'],
    districtHelp:['All 64 districts are selectable. District search supplies district-level context, with no farm coordinates or scientific coverage implied.','৬৪টি জেলাই বেছে নেওয়া যায়। জেলা অনুসন্ধানে জেলাভিত্তিক প্রেক্ষাপট মেলে; জমির স্থানাঙ্ক বা বৈজ্ঞানিক পরামর্শের আওতা বোঝায় না।'],
    source:['District directory source: Bangladesh National Portal','জেলার তালিকার উৎস: বাংলাদেশ জাতীয় তথ্য বাতায়ন'], choose:['Select an answer','উত্তর বেছে নিন'],
    q1:['Q1. What crop is growing now?','প্রশ্ন ১। এখন কী ফসল হচ্ছে?'], currentCrop:['Current crop / field state','বর্তমান ফসল / জমির অবস্থা'],
    fallow:['Field currently empty/fallow','জমি বর্তমানে খালি/পতিত'], sown:['Current crop sowing date (optional, if known)','বর্তমান ফসল বপনের তারিখ (জানা থাকলে, ঐচ্ছিক)'],
    cropHelp:['These crop identities are supported for intake only. Regional suitability and variety rules still need review. If your crop is absent, keep a draft; do not choose a different crop as a guess.','এই ফসলগুলোর পরিচয় তথ্য গ্রহণে ব্যবহার করা হচ্ছে। অঞ্চলভিত্তিক উপযোগিতা ও জাতের নিয়ম পর্যালোচনা বাকি। আপনার ফসল তালিকায় না থাকলে খসড়া রাখুন; আন্দাজে অন্য ফসল বাছবেন না।'],
    q2:['Q2. When will the field be available after harvest?','প্রশ্ন ২। ফসল কাটার পর জমি কবে পাওয়া যাবে?'], availabilityType:['Date or bounded date window','নির্দিষ্ট তারিখ বা সীমাবদ্ধ তারিখের পরিসর'],
    date:['One date','একটি তারিখ'], window:['Date window','তারিখের পরিসর'], availableFrom:['Available-from date / earliest date','জমি পাওয়ার তারিখ / সম্ভাব্য প্রথম তারিখ'],
    emptyDate:['Empty field: available-from date / earliest date','খালি জমি: পাওয়ার তারিখ / সম্ভাব্য প্রথম তারিখ'], availableTo:['Latest available date','সম্ভাব্য শেষ তারিখ'],
    availabilityBasis:['How was this date determined?','তারিখটি কীভাবে নির্ধারণ করেছেন?'], expected:['Expected date from my crop schedule','আমার ফসলের সময়সূচি অনুযায়ী প্রত্যাশিত তারিখ'], estimate:['Farmer estimate','কৃষকের আনুমানিক তারিখ'],
    q3:['Q3. What crops did you grow previously?','প্রশ্ন ৩। আগে কী কী ফসল চাষ করেছেন?'], historyState:['Previous crop history','আগের ফসলের ইতিহাস'],
    historyEntries:['Enter previous crops, oldest first','আগের ফসল লিখুন, পুরোনোটি আগে'], first:['First cultivation / no previous crop history','প্রথম চাষ / আগের ফসলের ইতিহাস নেই'],
    firstNote:['Known absence of history does not establish absence of rotation risks.','আগের ফসলের ইতিহাস না থাকা আবর্তনের ঝুঁকি নেই—এমন প্রমাণ নয়।'],
    q4:['Q4. What would you normally grow next?','প্রশ্ন ৪। সাধারণত এরপর কী চাষ করতেন?'], baselineState:['Usual upcoming sequence (comparison baseline)','সাধারণ পরবর্তী ফসলক্রম (তুলনার ভিত্তি)'],
    sequence:['Enter my usual upcoming sequence','আমার সাধারণ পরবর্তী ফসলক্রম লিখব'], noRotation:['No established rotation','নির্ধারিত ফসল আবর্তন নেই'],
    baselineNote:['Past history and this usual future sequence are separate. Repeated crops and fallow are allowed. An absent baseline cannot support a complete three-strategy comparison.','আগের ইতিহাস ও সাধারণ পরবর্তী ফসলক্রম আলাদা। একই ফসল পুনরায় এবং পতিত সময় দেওয়া যায়। ভিত্তি না থাকলে তিনটি কৌশলের পূর্ণ তুলনা সম্ভব নয়।'],
    crop:['Crop','ফসল'], fallowSegment:['Fallow segment','পতিত সময়'], timing:['How will you describe this period?','সময়কাল কীভাবে জানাবেন?'],
    seasonYear:['Season and year','মৌসুম ও বছর'], dates:['Start and end dates','শুরু ও শেষের তারিখ'], season:['Season','মৌসুম'], year:['Season start year','মৌসুম শুরুর বছর'],
    start:['Start date','শুরুর তারিখ'], end:['End date','শেষের তারিখ'], seasonHelp:['Enter entries in chronological order. For Rabi, use its starting year (e.g. 2025 for Rabi 2025–26). Season labels are reporting context, not planting advice.','সময়ের ক্রমে লিখুন। রবির জন্য শুরুর বছর দিন (যেমন রবি ২০২৫–২৬ এর জন্য ২০২৫)। মৌসুমের নাম তথ্যের প্রেক্ষাপট, বপনের পরামর্শ নয়।'],
    add:['Add an entry','আরেকটি যোগ করুন'], remove:['Remove entry','সারিটি সরান'], entry:['Entry','সারি'],
    q5:['Q5. What water access do you have?','প্রশ্ন ৫। পানির কী সুবিধা আছে?'], water:['Water access','পানির সুবিধা'], rainfed:['Rainfed','বৃষ্টিনির্ভর'], limited:['Limited irrigation','সীমিত সেচ'], reliable:['Reliable irrigation','নির্ভরযোগ্য সেচ'],
    seasonalLimits:['Are there seasonal irrigation limitations?','মৌসুমভেদে সেচের সীমাবদ্ধতা আছে কি?'], none:['No seasonal limitations reported','মৌসুমি সীমাবদ্ধতা নেই বলে জানাচ্ছি'], seasonal:['Yes, in specific seasons','হ্যাঁ, নির্দিষ্ট মৌসুমে'],
    limitedSeasons:['Seasons with limited/unavailable irrigation (select at least one)','সেচ সীমিত/অনুপলব্ধ থাকে যে মৌসুমে (অন্তত একটি)'], waterHelp:['These are farmer-reported access categories, not irrigation volumes.','এগুলো কৃষকের জানানো পানির সুবিধার ধরন, সেচের পরিমাণ নয়।'],
    q6:['Q6. What matters most?','প্রশ্ন ৬। কোন বিষয়টি সবচেয়ে জরুরি?'], priority:['Your priority','আপনার অগ্রাধিকার'],
    waterPriority:['Save water','পানি সাশ্রয়'], soilPriority:['Soil protection / rotation diversity','মাটির সুরক্ষা / ফসল আবর্তনের বৈচিত্র্য'], balanced:['Balanced','ভারসাম্যপূর্ণ'],
    submit:['Save validated field inputs','যাচাই করা জমির তথ্য সংরক্ষণ করুন'], saveDraft:['Save unfinished draft','অসমাপ্ত খসড়া সংরক্ষণ করুন'],
    beforeSubmit:['Saving checks your answers only. Scientific planning is unavailable until the evidence, reviewed agronomy and API are connected.','সংরক্ষণের সময় শুধু আপনার উত্তর যাচাই হবে। তথ্য, পর্যালোচিত কৃষিবিধি ও API সংযুক্ত না হওয়া পর্যন্ত বৈজ্ঞানিক পরিকল্পনা অনুপলব্ধ।'],
    demo:['Open separate illustrative demo','আলাদা নমুনা ডেমো খুলুন'], unavailable:['Planning unavailable','পরিকল্পনা এখন অনুপলব্ধ'],
    unavailableHelp:['Your field inputs are validated, but no scientific API is connected. NASA evidence, reviewed agronomy and the rotation engine are still required. No recommendations or scores were generated.','জমির তথ্য যাচাই হয়েছে, তবে বৈজ্ঞানিক API সংযুক্ত নেই। NASA তথ্য, পর্যালোচিত কৃষিবিধি ও আবর্তন ইঞ্জিন প্রয়োজন। কোনো সুপারিশ বা স্কোর তৈরি হয়নি।'],
    summary:['Submitted field-input summary','জমা দেওয়া জমির তথ্যের সারাংশ'], noSummary:['No validated intake submitted yet.','এখনও যাচাই করা তথ্য জমা দেওয়া হয়নি।'],
    edit:['Continue / edit field inputs','জমির তথ্য দেওয়া / সংশোধন চালিয়ে যান'], different:['A separate unfinished draft is retained. The summary below is the last validated submission.','আলাদা অসমাপ্ত খসড়া রাখা আছে। নিচে সর্বশেষ যাচাই করে জমা দেওয়া তথ্যের সারাংশ।'],
    json:['Download field inputs (JSON)','জমির তথ্য নামান (JSON)'], errors:['Please correct these answers','এই উত্তরগুলো সংশোধন করুন'],
    storage:['Browser storage is unavailable. Answers remain in this session; download submitted inputs to keep a copy.','ব্রাউজারে সংরক্ষণ করা যাচ্ছে না। এই সেশনে উত্তর থাকবে; জমা দেওয়া তথ্য ডাউনলোড করে রাখুন।'],
    draftSaved:['Unfinished draft saved; it has not been submitted.','অসমাপ্ত খসড়া সংরক্ষিত; জমা দেওয়া হয়নি।']
  };
  const errorCopy = {
    location_method:['Choose map or district search.','মানচিত্র বা জেলা অনুসন্ধান বেছে নিন।'],
    map_pin:['Place a pin, then confirm the location; or use district search.','পিন দিয়ে অবস্থান নিশ্চিত করুন; অথবা জেলা অনুসন্ধান ব্যবহার করুন।'],
    point_invalid:['Invalid coordinates. Select a point on the map again.','স্থানাঙ্ক সঠিক নয়। মানচিত্রে আবার স্থান বেছে নিন।'],
    point_confirmation:['Confirm the current pin after placing or moving it.','পিন দেওয়া বা সরানোর পর বর্তমান অবস্থান নিশ্চিত করুন।'],
    point_unavailable:['Local boundaries could not be verified. Retry or use district search.','স্থানীয় সীমানা যাচাই করা যায়নি। আবার চেষ্টা করুন বা জেলা অনুসন্ধান ব্যবহার করুন।'],
    point_outside:['This point is outside the available Bangladesh district geometry. Move it or use district search.','এই বিন্দু উপলব্ধ বাংলাদেশের জেলার সীমানার বাইরে। সরান অথবা জেলা অনুসন্ধান ব্যবহার করুন।'],
    point_unresolved:['No containing district could be resolved here (possibly a coastline, gap or unmapped area). Move the pin or use district search.','এখানে কোন জেলার মধ্যে পড়ে তা নির্ধারিত হয়নি (উপকূল, ফাঁক বা সীমানায় বাদ পড়া এলাকা হতে পারে)। পিন সরান অথবা জেলা অনুসন্ধান ব্যবহার করুন।'],
    point_ambiguous:['This point is on a boundary or overlapping districts. Move it clearly inside a district or use district search.','এই বিন্দু সীমানায় বা একাধিক জেলার ওভারল্যাপে। জেলার ভেতরে স্পষ্ট স্থানে সরান বা জেলা অনুসন্ধান ব্যবহার করুন।'],
    district:['Choose a district from the verified directory.','যাচাই করা তালিকা থেকে জেলা বেছে নিন।'],
    current_crop:['Choose a supported crop or explicitly select empty/fallow.','তালিকার ফসল বা খালি/পতিত অবস্থা বেছে নিন।'],
    date:['Enter a real calendar date.','সঠিক ক্যালেন্ডারের তারিখ দিন।'], availability_type:['Choose one date or a bounded window.','একটি তারিখ বা সীমাবদ্ধ পরিসর বেছে নিন।'],
    window_order:['The end date must be on or after the start date.','শেষের তারিখ শুরুর তারিখের আগে হতে পারবে না।'],
    date_basis:['State whether this is expected from your schedule or a farmer estimate.','সময়সূচি অনুযায়ী প্রত্যাশিত নাকি কৃষকের অনুমান তা বেছে নিন।'],
    before_sowing:['Availability cannot be before the known current sowing date.','জানা বপনের তারিখের আগে জমি পাওয়ার তারিখ হতে পারে না।'],
    history:['Enter previous crops or explicitly select first cultivation.','আগের ফসল দিন অথবা প্রথম চাষ বেছে নিন।'],
    baseline:['Enter a usual sequence or explicitly select no established rotation.','সাধারণ ফসলক্রম দিন অথবা নির্ধারিত আবর্তন নেই বেছে নিন।'],
    entries:['Enter between 1 and 20 meaningful entries.','১ থেকে ২০টি অর্থবহ সারি দিন।'], crop:['Choose a crop (or a baseline fallow segment).','ফসল বেছে নিন (অথবা তুলনার ভিত্তিতে পতিত সময়)।'],
    season:['Choose a season.','মৌসুম বেছে নিন।'], year:['Enter a four-digit season start year (1000–9999).','মৌসুম শুরুর চার অঙ্কের বছর দিন (১০০০–৯৯৯৯)।'], timing:['Choose season/year or dates.','মৌসুম/বছর বা তারিখ বেছে নিন।'],
    entry_order:['Entries must be chronological, with no known date overlap or duplicate season.','সারিগুলো সময়ের ক্রমে দিন; জানা তারিখের ওভারল্যাপ বা একই মৌসুম পুনরাবৃত্তি গ্রহণযোগ্য নয়।'],
    history_after_availability:['Past history cannot end after field availability.','আগের ফসলের শেষ জমি পাওয়ার তারিখের পরে হতে পারে না।'],
    history_after_sowing:['Past history cannot end after the known current sowing date.','আগের ফসলের শেষ বর্তমান ফসলের জানা বপনের তারিখের পরে হতে পারে না।'],
    baseline_before_availability:['The usual future sequence cannot start before field availability.','সাধারণ পরবর্তী ফসলক্রম জমি পাওয়ার আগে শুরু হতে পারে না।'],
    water:['Choose Rainfed, Limited irrigation or Reliable irrigation.','বৃষ্টিনির্ভর, সীমিত সেচ বা নির্ভরযোগ্য সেচ বেছে নিন।'], seasonal_limits:['Answer whether seasonal irrigation limitations apply.','মৌসুমি সেচের সীমাবদ্ধতা আছে কি না জানান।'],
    limited_seasons:['Select at least one applicable season.','প্রযোজ্য অন্তত একটি মৌসুম বেছে নিন।'], priority:['Choose a priority; none is selected for you.','একটি অগ্রাধিকার বেছে নিন; কোনোটি আগে থেকে বাছাই করা নেই।']
  };
  window.STS_INTAKE_UI = function ({render,onSubmit,onDemo,toast}) {
    const storageKey = 'sts-farmer-intake-v1';
    let state, errors = [], storageOK = true, boundaryIndex=null, mapStatus='map_loading';
    try { state = D.loadSaved(JSON.parse(localStorage.getItem(storageKey))); } catch { state = D.loadSaved(null); }
    const bn = () => document.documentElement.lang === 'bn';
    const t = key => (copy[key] || [key,key])[bn()?1:0];
    const message = code => (errorCopy[code] || [code,code])[bn()?1:0];
    const name = item => item ? item[bn()?'bn':'en'] : '';
    function persist() {
      try {localStorage.setItem(storageKey,JSON.stringify({version:2,draft:state.draft,submitted:state.submitted||state.pendingSubmission}));storageOK=true;}
      catch {storageOK=false;}
    }
    const id = field => 'intake-' + field;
    function boundaryReady(index) {
      boundaryIndex=index;
      if(state.pendingSubmission){
        const checked=D.validateAndNormalize(state.pendingSubmission.answers,index);
        if(checked.ok){state.submitted={answers:state.pendingSubmission.answers,request:checked.request};state.pendingSubmission=null;persist();}
      }
      refreshMapStatus();
    }
    const maps=window.STS_INTAKE_MAP?.create({getDraft:()=>state.draft,onPin:point=>{L.placePin(state.draft,point);persist();refreshMapStatus();},
      onBoundaries:boundaryReady,onStatus:status=>{mapStatus=status;refreshMapStatus();},t});
    if(state.draft.locationMethod==='map_pin'||state.pendingSubmission){
      window.STS_INTAKE_MAP?.loadBoundaries().then(({index})=>{boundaryReady(index);render();}).catch(()=>{mapStatus='map_failed';refreshMapStatus();});
    }
    function pinResult(){const pin=state.draft.mapPin;return L.resolvePoint(pin?[pin.longitude,pin.latitude]:null,boundaryIndex);}
    function refreshMapStatus(){
      const status=document.getElementById('intake-map-status'),pin=state.draft.mapPin,result=pinResult();
      const confirmed=L.normalizeLocation(state.draft,boundaryIndex,D.districts,D.directorySource).location?.level==='point';
      if(status){
        let value=t(mapStatus);
        if(pin){
          value+=' '+(result.status==='resolved'?(confirmed?t('pin_confirmed'):t('pin_unconfirmed'))+' · '+name(D.districts.find(d=>d.id===result.districtId)):message('point_'+result.status));
          if(L.validPoint([pin.longitude,pin.latitude]))value+=' · '+pin.latitude.toFixed(5)+', '+pin.longitude.toFixed(5);
        }
        status.textContent=value;
      }
      const confirm=document.getElementById('intake-map-confirm'),center=document.getElementById('intake-map-center');
      if(confirm)confirm.disabled=!maps?.isReady()||result.status!=='resolved'||confirmed;
      if(center)center.disabled=!maps?.isReady();
    }
    function locationControls(){
      const d=state.draft;
      const methods=`<div role="group" aria-label="${t('locationMethod')}" id="${id('locationMethod')}" tabindex="-1" class="intake-location-methods"><button type="button" data-location-method="map_pin" aria-pressed="${d.locationMethod==='map_pin'}">${t('mapMethod')}</button><button type="button" data-location-method="district_search" aria-pressed="${d.locationMethod==='district_search'}">${t('districtMethod')}</button></div>${errorMarkup('locationMethod')}`;
      if(d.locationMethod!=='map_pin')return methods+`<div class="form-grid">${input('districtSearch',t('search'),'','search',false,'autocomplete="off"')}${select('districtId',t('district'),D.districts.map(item=>[item.id,`${name(item)} · ${item[bn()?'en':'bn']}`]),d.districtId)}</div><p id="district-match-count" class="help" role="status"></p><p class="help">${t('districtHelp')}</p><a href="${D.directorySource.url}" target="_blank" rel="noopener">${t('source')}</a>`;
      return methods+`<div id="${id('mapPin')}" tabindex="-1" aria-label="${t('mapPin')}" aria-describedby="${id('mapPin')}-error"><p class="help">${t('mapHelp')}</p><div id="intake-map-host" class="intake-map-host" role="region" aria-label="${t('mapLabel')}"></div><p class="help intake-map-credit"><a href="/reference/licenses/maplibre-gl.LICENSE.txt">MapLibre GL JS</a> &middot; <span>${esc(window.STS_MAP_CONFIG?.label||'OpenFreeMap Liberty')}</span> · ${window.STS_MAP_CONFIG?.isOpenFreeMap===false?'':'<a href="https://openfreemap.org/">OpenFreeMap</a>'} · ${window.STS_MAP_CONFIG?.isOpenFreeMap===false?'':'<a href="https://www.openstreetmap.org/copyright">© OpenStreetMap</a>'} · ${window.STS_MAP_CONFIG?.isOpenFreeMap===false?'':'<a href="https://openmaptiles.org/">© OpenMapTiles</a>'}<br><a href="https://www.geoboundaries.org/">geoBoundaries</a> · BBS / OCHA ROAP · <a href="${L.boundarySource.licenseUrl}">CC BY 3.0 IGO</a> · ${esc(L.boundarySource.version)}</p><p id="intake-map-status" role="status">${t(mapStatus)}</p>${errorMarkup('mapPin')}<div class="actions"><button type="button" data-map-center id="intake-map-center" disabled>${t('centerPin')}</button><button type="button" data-map-confirm id="intake-map-confirm" disabled>${t('confirmPin')}</button><button type="button" data-map-retry>${t('retryMap')}</button><button type="button" data-location-method="district_search">${t('districtMethod')}</button></div><p class="help">${t('pointNote')}</p></div>`;
    }
    function errorMarkup(field) {
      return `<p class="intake-error" id="${id(field)}-error">${errors.filter(e=>e.field===field).map(e=>esc(message(e.code))).join(' ')}</p>`;
    }
    function attrs(field, required = true) {
      return `id="${id(field)}" name="${esc(field)}" ${required?'required':''} aria-describedby="${id(field)}-error" ${errors.some(e=>e.field===field)?'aria-invalid="true"':''}`;
    }
    function select(field,label,items,value,required=true) {
      return `<div class="intake-control"><label for="${id(field)}">${esc(label)}</label><select ${attrs(field,required)}><option value="">${esc(t('choose'))}</option>${items.map(([v,label])=>`<option value="${esc(v)}" ${value===v?'selected':''}>${esc(label)}</option>`).join('')}</select>${errorMarkup(field)}</div>`;
    }
    function input(field,label,value,type='text',required=true,extra='') {
      return `<div class="intake-control"><label for="${id(field)}">${esc(label)}</label><input ${attrs(field,required)} type="${type}" value="${esc(value)}" ${extra}>${errorMarkup(field)}</div>`;
    }
    const choices = keys => keys.map(key=>[key,t(key)]);
    const cropChoices = () => D.crops.map(c=>[c.id,name(c)]);
    const seasonChoices = () => D.seasons.map(s=>[s.id,name(s)]);
    function rows(key) {
      return `<p class="help">${t('seasonHelp')}</p>${state.draft[key].map((r,i)=>{
        const prefix = key+'-'+i+'-';
        return `<fieldset class="intake-entry"><legend>${t('entry')} ${i+1}</legend><div class="form-grid">${select(prefix+'cropId',t('crop'),[...cropChoices(),...(key==='baseline'?[['fallow',t('fallowSegment')]]:[])],r.cropId)}${select(prefix+'timing',t('timing'),[['season_year',t('seasonYear')],['dates',t('dates')]],r.timing)}${r.timing==='dates'?input(prefix+'start',t('start'),r.start,'date')+input(prefix+'end',t('end'),r.end,'date'):select(prefix+'seasonId',t('season'),seasonChoices(),r.seasonId)+input(prefix+'year',t('year'),r.year,'text',true,'inputmode="numeric" pattern="[1-9][0-9]{3}" maxlength="4"')}</div><button type="button" data-intake-remove="${key}" data-index="${i}" aria-label="${t('remove')} ${i+1}">${t('remove')} ${i+1}</button></fieldset>`;
      }).join('')}<button type="button" data-intake-add="${key}" ${state.draft[key].length>=20?'disabled':''}>${t('add')}</button>`;
    }
    function form() {
      const d = state.draft;
      return `<section class="farmer-intake" data-no-translate aria-labelledby="intake-heading"><div class="page-heading"><div><div class="kicker">SOIL TO STARS</div><h1 id="intake-heading">${t('title')}</h1><p>${t('intro')}</p></div></div><p class="notice" id="intake-draft-status">${t('draft')}</p>${!storageOK?`<p role="status" class="notice">${t('storage')}</p>`:''}<form id="farmer-intake-form" class="card" novalidate>${errors.length?`<div class="intake-error-summary" role="alert" tabindex="-1"><h2>${t('errors')}</h2><ul>${errors.map(e=>`<li><a href="#${id(e.field)}" data-intake-error="${esc(e.field)}">${esc(fieldLabel(e.field))}: ${esc(message(e.code))}</a></li>`).join('')}</ul></div>`:''}
      <fieldset><legend>${t('location')}</legend>${locationControls()}</fieldset>
      <fieldset><legend>${t('q1')}</legend>${select('currentCrop',t('currentCrop'),[...cropChoices(),['fallow',t('fallow')]],d.currentCrop)}${d.currentCrop&&d.currentCrop!=='fallow'?input('currentSownOn',t('sown'),d.currentSownOn,'date',false):''}<p class="help">${t('cropHelp')}</p></fieldset>
      <fieldset><legend>${t('q2')}</legend><div class="form-grid">${select('availabilityType',t('availabilityType'),choices(['date','window']),d.availabilityType)}${input('availableFrom',t(d.currentCrop==='fallow'?'emptyDate':'availableFrom'),d.availableFrom,'date')}${d.availabilityType==='window'?input('availableTo',t('availableTo'),d.availableTo,'date'):''}${select('availabilityBasis',t('availabilityBasis'),[['expected',t('expected')],['farmer_estimate',t('estimate')]],d.availabilityBasis)}</div></fieldset>
      <fieldset><legend>${t('q3')}</legend>${select('historyState',t('historyState'),[['entries',t('historyEntries')],['first_cultivation',t('first')]],d.historyState)}${d.historyState==='entries'?rows('history'):''}<p class="help">${t('firstNote')}</p></fieldset>
      <fieldset><legend>${t('q4')}</legend>${select('baselineState',t('baselineState'),[['sequence',t('sequence')],['no_established_rotation',t('noRotation')]],d.baselineState)}${d.baselineState==='sequence'?rows('baseline'):''}<p class="help">${t('baselineNote')}</p></fieldset>
      <fieldset><legend>${t('q5')}</legend>${select('water',t('water'),choices(['rainfed','limited','reliable']),d.water)}${['limited','reliable'].includes(d.water)?select('seasonalLimits',t('seasonalLimits'),choices(['none','seasonal']),d.seasonalLimits):''}${['limited','reliable'].includes(d.water)&&d.seasonalLimits==='seasonal'?`<fieldset class="intake-seasons"><legend>${t('limitedSeasons')}</legend>${D.seasons.map((s,i)=>`<label for="${i===0?id('limitedSeasons'):id('limitedSeasons')+'-'+s.id}"><input type="checkbox" id="${i===0?id('limitedSeasons'):id('limitedSeasons')+'-'+s.id}" name="limitedSeasons" value="${s.id}" ${d.limitedSeasons.includes(s.id)?'checked':''} aria-describedby="${id('limitedSeasons')}-error" ${errors.some(e=>e.field==='limitedSeasons')?'aria-invalid="true"':''}> ${name(s)}</label>`).join('')}${errorMarkup('limitedSeasons')}</fieldset>`:''}<p class="help">${t('waterHelp')}</p></fieldset>
      <fieldset><legend>${t('q6')}</legend>${select('priority',t('priority'),[['water',t('waterPriority')],['soil_rotation',t('soilPriority')],['balanced',t('balanced')]],d.priority)}</fieldset>
      <div class="actions mt"><button type="submit" class="primary">${t('submit')}</button><button type="button" data-intake-draft>${t('saveDraft')}</button></div><p class="help">${t('beforeSubmit')}</p></form><div class="actions mt"><button type="button" data-intake-demo>${t('demo')}</button></div></section>`;
    }
    function period(p) {
      return p.kind==='dates'?`${esc(p.start)} → ${esc(p.end)}`:`${esc(name(D.seasons.find(s=>s.id===p.season_id)))} · ${p.year}`;
    }
    function summary() {
      const r = state.submitted?.request;
      const dirty = r && JSON.stringify(state.draft)!==JSON.stringify(state.submitted.answers);
      return `<section class="farmer-intake" data-no-translate><div class="page-heading"><div><div class="kicker">SOIL TO STARS</div><h1>${t('summary')}</h1></div></div><div class="notice" role="status"><h2>${t('unavailable')}</h2><p>${t('unavailableHelp')}</p></div>${!storageOK?`<p class="notice">${t('storage')}</p>`:''}${dirty?`<p class="notice">${t('different')}</p>`:''}${state.pendingSubmission?`<p class="notice" role="status">${t('pendingSaved')}</p>`:''}${r?`<div class="card mt intake-summary"><dl><dt>${t('district')}</dt><dd>${esc(name(D.districts.find(d=>d.id===r.location.district_id)))}${r.location.level==='point'?`<p>${t('pin_confirmed')} &middot; ${r.location.coordinates.latitude.toFixed(5)}, ${r.location.coordinates.longitude.toFixed(5)}</p><p class="help">${t('pointNote')} &middot; ${esc(r.location.provenance.boundary_version)}</p>`:`<p class="help">${t('districtHelp')}</p>`}</dd><dt>${t('q1')}</dt><dd>${r.current.state==='fallow'?t('fallow'):esc(name(D.crops.find(c=>c.id===r.current.crop_id)))}${r.current.sown_on?' · '+esc(r.current.sown_on):''}</dd><dt>${t('q2')}</dt><dd>${esc(r.availability.start)}${r.availability.kind==='window'?' → '+esc(r.availability.end):''} · ${t(r.availability.basis==='farmer_estimate'?'estimate':'expected')}</dd><dt>${t('q3')}</dt><dd>${r.crop_history.state==='first_cultivation'?t('first'):`<ol>${r.crop_history.entries.map(e=>`<li>${esc(name(D.crops.find(c=>c.id===e.crop_id)))} · ${period(e.period)}</li>`).join('')}</ol>`}</dd><dt>${t('q4')}</dt><dd>${r.baseline.state==='no_established_rotation'?t('noRotation'):`<ol>${r.baseline.segments.map(e=>`<li>${e.kind==='fallow'?t('fallowSegment'):esc(name(D.crops.find(c=>c.id===e.crop_id)))} · ${period(e.period)}</li>`).join('')}</ol>`}</dd><dt>${t('q5')}</dt><dd>${t(r.irrigation.access)}${r.irrigation.access==='rainfed'?'':' · '+t(r.irrigation.seasonal_limitations)}${r.irrigation.limited_seasons.length?' · '+r.irrigation.limited_seasons.map(s=>esc(name(D.seasons.find(i=>i.id===s)))).join(', '):''}</dd><dt>${t('q6')}</dt><dd>${t(r.priority==='water'?'waterPriority':r.priority==='soil_rotation'?'soilPriority':'balanced')}</dd></dl><p class="help">${t('districtHelp')}</p><p class="help">${t('firstNote')} ${t('baselineNote')}</p><div class="actions"><button type="button" data-intake-download>${t('json')}</button></div></div>`:`<p class="card mt">${t('noSummary')}</p>`}<div class="actions mt"><button class="primary" type="button" data-intake-edit>${t('edit')}</button><button type="button" data-intake-demo>${t('demo')}</button></div></section>`;
    }
    function fieldLabel(field) {
      const match = field.match(/^(history|baseline)-(\d+)-(.+)$/);
      return match?`${t(match[1]==='history'?'q3':'q4')} · ${t('entry')} ${Number(match[2])+1} · ${t(match[3]==='cropId'?'crop':match[3]==='seasonId'?'season':match[3])}`:t(({districtId:'district',currentSownOn:'sown'})[field]||field);
    }
    function redraw(focusId,preventScroll=true) {render();if(focusId)document.getElementById(focusId)?.focus({preventScroll});}
    function capture(target) {
      const field = target.name;
      if (field==='limitedSeasons') state.draft.limitedSeasons = [...document.querySelectorAll('#farmer-intake-form [name="limitedSeasons"]:checked')].map(el=>el.value);
      else {
        const match = field.match(/^(history|baseline)-(\d+)-(.+)$/);
        if (match) state.draft[match[1]][Number(match[2])][match[3]] = target.value;
        else if (Object.hasOwn(state.draft,field)) state.draft[field] = target.value;
      }
      persist();
    }
    document.addEventListener('input',e=>{
      if (!e.target.closest('#farmer-intake-form')) return;
      if (e.target.id===id('districtSearch')) {
        const query=e.target.value.trim().toLocaleLowerCase();
        const items=D.districts.filter(item=>[item.en,item.bn,item.id,item.division].some(s=>s.toLocaleLowerCase().includes(query)));
        const chosen = D.districts.find(item=>item.id===state.draft.districtId);
        if (chosen&&!items.includes(chosen)) items.unshift(chosen);
        document.getElementById(id('districtId')).innerHTML=`<option value="">${t('choose')}</option>`+items.map(item=>`<option value="${item.id}" ${item.id===state.draft.districtId?'selected':''}>${esc(name(item))} · ${esc(item[bn()?'en':'bn'])}</option>`).join('');
        document.getElementById('district-match-count').textContent=bn()?`${items.length}টি জেলা দেখানো হচ্ছে`:`${items.length} districts shown`;
      } else capture(e.target);
    });
    document.addEventListener('change',e=>{
      if (!e.target.closest('#farmer-intake-form')) return;
      capture(e.target);
      if (['currentCrop','availabilityType','historyState','baselineState','water','seasonalLimits'].includes(e.target.name)||e.target.name.endsWith('-timing')) redraw(e.target.id);
    });
    document.addEventListener('click',e=>{
      const button=e.target.closest('[data-intake-add],[data-intake-remove],[data-intake-draft],[data-intake-error],[data-intake-demo],[data-intake-download],[data-intake-edit],[data-location-method],[data-map-center],[data-map-confirm],[data-map-retry]');
      if(!button)return;
      if(button.dataset.locationMethod){L.switchMethod(state.draft,button.dataset.locationMethod);errors=errors.filter(e=>!['mapPin','districtId','locationMethod'].includes(e.field));persist();redraw(id('locationMethod'));return;}
      if(button.hasAttribute('data-map-center')){maps?.placeCenter();return;}
      if(button.hasAttribute('data-map-confirm')){if(maps?.isReady()){L.confirmPin(state.draft,boundaryIndex);persist();maps.updateMarker();refreshMapStatus();}return;}
      if(button.hasAttribute('data-map-retry')){maps?.destroy();redraw(id('mapPin'));return;}

      if(button.hasAttribute('data-intake-error')){e.preventDefault();document.getElementById(id(button.dataset.intakeError))?.focus();}
      if(button.dataset.intakeAdd){const key=button.dataset.intakeAdd;if(state.draft[key].length<20)state.draft[key].push(D.row());persist();redraw(id(key+'-'+(state.draft[key].length-1)+'-cropId'));}
      if(button.dataset.intakeRemove){const key=button.dataset.intakeRemove;state.draft[key].splice(Number(button.dataset.index),1);if(!state.draft[key].length)state.draft[key].push(D.row());persist();redraw(id(key+'-0-cropId'));}
      if(button.hasAttribute('data-intake-draft')){persist();toast(t(storageOK?'draftSaved':'storage'));}
      if(button.hasAttribute('data-intake-demo'))onDemo();
      if(button.hasAttribute('data-intake-edit'))onSubmit(false);
      if(button.hasAttribute('data-intake-download'))download();
    });
    document.addEventListener('submit',e=>{
      if(e.target.id!=='farmer-intake-form')return;
      e.preventDefault();
      // Read the live form as well as input/change events (autofill and programmatic consumers).
      for(const control of e.target.elements)if(control.name&&control.name!=='districtSearch')capture(control);
      const result=D.validateAndNormalize(state.draft,boundaryIndex);
      errors=result.errors;
      if(!result.ok){redraw(id(errors[0].field),false);return;}
      state.submitted={answers:structuredClone(state.draft),request:result.request};state.pendingSubmission=null;persist();onSubmit(true);
    });
    function download() {
      if(!state.submitted)return;
      const blob=new Blob([JSON.stringify(state.submitted.request,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
      a.href=url;a.download='soil-to-stars-field-inputs.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    }
    return {form,summary,download,beforeRender(){maps?.beforeRender();},afterRender(){void maps?.afterRender();refreshMapStatus();},hasSubmission:()=>!!state.submitted,newDraft(){state.draft=D.blankDraft();errors=[];persist();}};
  };
})();
