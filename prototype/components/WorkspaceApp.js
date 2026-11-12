"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  FiActivity, FiArrowLeft, FiArrowRight, FiBarChart2, FiBookmark,
  FiCheck, FiChevronDown, FiCloudRain, FiDatabase, FiDownload,
  FiDroplet, FiGrid, FiInfo, FiLayers, FiMap, FiMenu, FiPlus,
  FiRefreshCw, FiSave, FiSliders, FiThermometer, FiX,
} from "react-icons/fi";
import { PiPlant } from "react-icons/pi";
import Brand from "./Brand";
import SkeletonPage from "./SkeletonPage";
import ThemeLanguage from "./ThemeLanguage";

const routes = [
  ["overview", "Your results", FiGrid], ["profile", "Set up your field", FiMap],
  ["rotations", "Rotation plans", PiPlant], ["compare", "Compare plans", FiBarChart2],
  ["simulator", "What-if studio", FiSliders], ["climate", "Climate insights", FiCloudRain],
  ["saved", "Saved plan", FiBookmark], ["methodology", "Data & methodology", FiDatabase],
];

const plans = [
  { id: "maize-mungbean-mustard", crops: ["Maize", "Mungbean", "Mustard"], score: 86.4, water: 91, soil: 89, climate: 82, stability: 83, note: "Lower water demand with a useful legume stage." },
  { id: "sesame-rice-lentil", crops: ["Sesame", "Rice", "Lentil"], score: 82.7, water: 67, soil: 91, climate: 88, stability: 85, note: "Strong soil score with a higher water-demand middle season." },
  { id: "jute-vegetables-wheat", crops: ["Jute", "Vegetables", "Wheat"], score: 79.8, water: 78, soil: 75, climate: 84, stability: 91, note: "A diverse sequence with stronger year-to-year stability." },
  { id: "rice-mustard-mungbean", crops: ["Rice", "Mustard", "Mungbean"], score: 77.2, water: 64, soil: 86, climate: 80, stability: 78, note: "A familiar sequence with a visible irrigation trade-off." },
];

const defaultField = { name: "Rajshahi North Field", region: "Rajshahi", size: 2.4, soil: "Loam", ph: 6.5, water: "Limited", drainage: "Moderate", history: ["Rice", "Mustard", "Mungbean"], priority: "Balanced" };

export default function WorkspaceApp() {
  const [route, setRoute] = useState("overview");
  const [mobileNav, setMobileNav] = useState(false);
  const [loading, setLoading] = useState(true);
  const [field, setField] = useState(defaultField);
  const [profileStep, setProfileStep] = useState(0);
  const [saved, setSaved] = useState(null);
  const [selected, setSelected] = useState([plans[0].id, plans[1].id]);
  const [toast, setToast] = useState("");
  const [dialogPlan, setDialogPlan] = useState(null);
  const [metric, setMetric] = useState("Rainfall");
  const [scenario, setScenario] = useState("Typical");
  const [simWeights, setSimWeights] = useState({ water: 30, soil: 25, climate: 25, stability: 20 });

  useEffect(() => {
    // Hydrate persisted client state at the existing loading boundary, in one callback.
    const timer = setTimeout(() => {
      const fromHash = window.location.hash.slice(1);
      if (routes.some(([key]) => key === fromHash)) setRoute(fromHash);
      try {
        const persisted = JSON.parse(localStorage.getItem("sts-workspace") || "null");
        const starter = JSON.parse(localStorage.getItem("sts-starter") || "null");
        if (persisted?.field) setField(persisted.field);
        else if (starter) setField((current) => ({ ...current, region: starter.region?.split(",")[0] || current.region, water: starter.water || current.water, priority: starter.priority || current.priority }));
        if (persisted?.saved) setSaved(persisted.saved);
      } catch {}
      setLoading(false);
    }, 700);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!loading) localStorage.setItem("sts-workspace", JSON.stringify({ field, saved }));
  }, [field, saved, loading]);

  const rankedPlans = useMemo(() => {
    const total = Object.values(simWeights).reduce((a, b) => a + b, 0);
    const penalty = scenario === "Dry" ? 5 : scenario === "Hot" ? 3 : 0;
    return plans.map((plan) => ({ ...plan, simScore: (["water", "soil", "climate", "stability"].reduce((sum, key) => sum + plan[key] * simWeights[key] / total, 0) - (scenario === "Dry" ? (100 - plan.water) / 8 : scenario === "Hot" ? (100 - plan.climate) / 10 : 0) - penalty / 4) })).sort((a,b) => b.simScore - a.simScore);
  }, [simWeights, scenario]);

  function navigate(next) {
    setLoading(true);
    setMobileNav(false);
    setRoute(next);
    window.history.replaceState(null, "", `#${next}`);
    window.scrollTo({ top: 0, behavior: "smooth" });
    setTimeout(() => setLoading(false), 420);
  }

  function notify(message) {
    setToast(message);
    setTimeout(() => setToast(""), 2600);
  }

  function savePlan(id) {
    setSaved(id);
    notify("Plan saved to this field.");
  }

  function exportPlan() {
    const payload = { prototype: true, dataClass: "illustrative", field, plan: plans.find((p) => p.id === saved) || plans[0], warning: "Not validated agricultural advice." };
    const href = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }));
    const anchor = document.createElement("a"); anchor.href = href; anchor.download = "soil-to-stars-plan.json"; anchor.click(); URL.revokeObjectURL(href);
    notify("Demo plan exported.");
  }

  return (
    <div className="workspace-page">
      <aside className={`workspace-sidebar ${mobileNav ? "open" : ""}`}>
        <div className="side-head"><Brand workspace /><button onClick={() => setMobileNav(false)} aria-label="Close navigation"><FiX /></button></div>
        <div className="field-switcher"><small>YOUR FIELD</small><button><span>{field.name}<b>{field.region} · {field.size} ha</b></span><FiChevronDown /></button><button className="add-field" onClick={() => { setField({...defaultField, name: "My new field"}); navigate("profile"); }}><FiPlus /> Add a field</button></div>
        <nav>{routes.map(([key,label,Icon]) => <button key={key} className={route === key ? "active" : ""} onClick={() => navigate(key)}><Icon /><span>{label}</span>{key === "saved" && saved && <i />}</button>)}</nav>
        <div className="side-bottom"><span><FiActivity /> EARTH OBSERVATION</span><p>A wider view.<br />A more thoughtful season.</p><Link href="/"><FiArrowLeft /> Back to homepage</Link></div>
      </aside>
      <div className="workspace-shell">
        <header className="workspace-header"><button className="workspace-menu" onClick={() => setMobileNav(true)}><FiMenu /></button><div className="breadcrumb">Workspace <span>/</span> <b>{routes.find(([key]) => key === route)?.[1]}</b></div><div className="workspace-actions"><span className="demo-status"><i /> Demo environment</span><ThemeLanguage compact /><button className="export-button" onClick={exportPlan}>Export plan <FiDownload /></button><span className="avatar">RF</span></div></header>
        <main className="workspace-main">{loading ? <WorkspaceContentSkeleton /> : <WorkspaceRoute route={route} field={field} setField={setField} profileStep={profileStep} setProfileStep={setProfileStep} plans={plans} rankedPlans={rankedPlans} selected={selected} setSelected={setSelected} saved={saved} savePlan={savePlan} navigate={navigate} notify={notify} setDialogPlan={setDialogPlan} metric={metric} setMetric={setMetric} scenario={scenario} setScenario={setScenario} simWeights={simWeights} setSimWeights={setSimWeights} />}</main>
        <footer className="workspace-footer"><b>SOIL TO STARS</b><span>Frontend prototype · All environmental values and crop traits are illustrative.</span></footer>
      </div>
      {toast && <div className="toast"><FiCheck /> {toast}</div>}
      {dialogPlan && <PlanDialog plan={dialogPlan} onClose={() => setDialogPlan(null)} onSave={() => { savePlan(dialogPlan.id); setDialogPlan(null); }} />}
    </div>
  );
}

function WorkspaceRoute(props) {
  switch (props.route) {
    case "profile": return <Profile {...props} />;
    case "rotations": return <Rotations {...props} />;
    case "compare": return <Compare {...props} />;
    case "simulator": return <Simulator {...props} />;
    case "climate": return <Climate {...props} />;
    case "saved": return <Saved {...props} />;
    case "methodology": return <Methodology />;
    default: return <Overview {...props} />;
  }
}

function PageTitle({ eyebrow, title, copy, action }) { return <div className="workspace-title"><div><span>{eyebrow}</span><h1>{title}</h1><p>{copy}</p></div>{action}</div>; }

function Overview({ field, plans, saved, navigate, setDialogPlan }) {
  const best = plans[0];
  return <><PageTitle eyebrow="YOUR PLANNING PATH" title={`Good morning. Your field is ready.`} copy="Start with field setup, explore the rotation options, then test a scenario before saving a plan." action={<button onClick={() => navigate("profile")} className="primary-button">Review field <FiArrowRight /></button>} /><div className="overview-hero"><div><span className="live-label"><i /> FIELD ANALYSIS COMPLETE</span><h2>{field.name}</h2><p>{field.region} · {field.size} hectares · {field.soil} soil</p><div className="field-metrics"><div><small>WATER ACCESS</small><b>{field.water}</b></div><div><small>SOIL pH</small><b>{field.ph}</b></div><div><small>DRAINAGE</small><b>{field.drainage}</b></div></div></div><div className="best-score"><small>LEADING DEMO SCORE</small><strong>{best.score}<span>/100</span></strong><button onClick={() => setDialogPlan(best)}>See why <FiArrowRight /></button></div></div><div className="dashboard-grid"><section className="dashboard-card wide"><div className="card-head"><div><span className="card-kicker">LEADING EXAMPLE</span><h2>{best.crops.join(" → ")}</h2></div><span className="tag">THREE SEASONS</span></div><SeasonTimeline crops={best.crops} /><div className="trait-grid"><Trait label="Water fit" value={best.water}/><Trait label="Soil health" value={best.soil}/><Trait label="Resilience" value={best.climate}/></div><div className="card-actions"><button onClick={() => setDialogPlan(best)}>Open plan</button><button onClick={() => navigate("rotations")}>See all options <FiArrowRight /></button></div></section><section className="dashboard-card"><span className="card-kicker">FIELD READINESS</span><h3>Most inputs are ready.</h3><div className="check-list"><span><FiCheck /> Location & field size</span><span><FiCheck /> Water access</span><span><FiCheck /> Crop history</span><span><FiInfo /> Soil values are demo estimates</span></div><button onClick={() => navigate("profile")}>Review inputs <FiArrowRight /></button></section><section className="dashboard-card dark-card"><span className="card-kicker">CLIMATE CONTEXT</span><FiCloudRain className="card-icon"/><h3>Seasonal timing matters.</h3><p>Explore illustrative rainfall and heat patterns behind the ranking.</p><button onClick={() => navigate("climate")}>Explore patterns <FiArrowRight /></button></section><section className="dashboard-card"><span className="card-kicker">SAVED PLAN</span><h3>{saved ? "Your choice is saved." : "Nothing saved yet."}</h3><p>{saved ? plans.find(p => p.id === saved)?.crops.join(" → ") : "Open a rotation and save it to keep the plan with this field."}</p><button onClick={() => navigate(saved ? "saved" : "rotations")}>{saved ? "Review saved plan" : "Choose a plan"} <FiArrowRight /></button></section></div></>;
}

function Profile({ field, setField, profileStep, setProfileStep, navigate, notify }) {
  const steps = ["Location", "Soil", "Water & history", "Priorities"];
  const update = (key, value) => setField({...field, [key]: value});
  return <><PageTitle eyebrow="YOUR FIELD INPUTS" title="Describe your field." copy="Use what you know. Unknown measurements can stay explicit or use clearly labeled demo estimates." /><div className="profile-layout"><aside className="step-list">{steps.map((label,index) => <button onClick={() => setProfileStep(index)} className={profileStep === index ? "active" : index < profileStep ? "done" : ""} key={label}><span>{index < profileStep ? <FiCheck /> : index+1}</span><div><b>{label}</b><small>{index === profileStep ? "IN PROGRESS" : index < profileStep ? "COMPLETE" : "UP NEXT"}</small></div></button>)}</aside><section className="form-card"><div className="form-progress"><span>STEP {profileStep+1} OF 4</span><i><b style={{width:`${(profileStep+1)*25}%`}}/></i></div>{profileStep === 0 && <><h2>Where is your field?</h2><p>Regional context helps align seasons and environmental signals.</p><div className="form-grid"><Field label="Field name"><input value={field.name} onChange={e => update("name",e.target.value)} /></Field><Field label="Pilot region"><select value={field.region} onChange={e => update("region",e.target.value)}><option>Rajshahi</option><option>Sylhet</option><option>Khulna</option></select></Field><Field label="Field size (hectares)"><input type="number" step="0.1" value={field.size} onChange={e => update("size",Number(e.target.value))}/></Field><div className="map-placeholder"><FiMapPinIcon /><span>24.37° N<br/>88.60° E</span></div></div></>}{profileStep === 1 && <><h2>What is the soil like?</h2><p>Measurements are helpful, but uncertainty should remain visible.</p><div className="form-grid"><Field label="Soil texture"><select value={field.soil} onChange={e => update("soil",e.target.value)}><option>Loam</option><option>Clay</option><option>Sandy loam</option><option>Unknown</option></select></Field><Field label="Measured pH"><input type="number" step="0.1" value={field.ph} onChange={e => update("ph",Number(e.target.value))}/></Field><Field label="Drainage"><select value={field.drainage} onChange={e => update("drainage",e.target.value)}><option>Good</option><option>Moderate</option><option>Poor</option></select></Field><button className="estimate-button" onClick={() => { setField({...field, soil:"Loam", ph:6.5, drainage:"Moderate"}); notify("Illustrative estimates applied."); }}><PiPlant /> Use demo estimates</button></div></>}{profileStep === 2 && <><h2>Water and crop history</h2><p>These constraints can change which rotations are feasible.</p><div className="form-grid"><Field label="Water availability"><select value={field.water} onChange={e => update("water",e.target.value)}><option>Rain-fed</option><option>Limited</option><option>Reliable</option></select></Field>{field.history.map((crop,index) => <Field label={`Previous season ${index+1}`} key={index}><select value={crop} onChange={e => {const history=[...field.history]; history[index]=e.target.value; update("history",history)}}><option>Rice</option><option>Mustard</option><option>Mungbean</option><option>Maize</option><option>Jute</option></select></Field>)}</div></>}{profileStep === 3 && <><h2>What matters most?</h2><p>The score reflects your priorities. It does not predict yield.</p><div className="priority-cards">{["Save water","Improve soil health","Climate resilience","Balanced"].map(item => <button className={field.priority === item ? "active" : ""} onClick={() => update("priority",item)} key={item}><FiDroplet/><b>{item}</b><span>{item === "Balanced" ? "Give each factor equal influence." : `Give more influence to ${item.toLowerCase()}.`}</span></button>)}</div></>}<div className="form-actions"><button disabled={profileStep===0} onClick={() => setProfileStep(profileStep-1)}><FiArrowLeft/> Back</button><button className="primary-button" onClick={() => profileStep < 3 ? setProfileStep(profileStep+1) : (notify("Field saved. Rankings updated."), navigate("overview"))}>{profileStep < 3 ? "Continue" : "Save field"} <FiArrowRight/></button></div></section></div></>;
}

function Rotations({ plans, selected, setSelected, savePlan, setDialogPlan, navigate }) { return <><PageTitle eyebrow="ROTATION PLANS" title="Compare the road ahead." copy="Every option shows its strengths and weak points. Scores are relative examples within this prototype." action={<button className="primary-button" onClick={() => navigate("compare")}>Compare selected ({selected.length}) <FiArrowRight/></button>} /><div className="plan-list">{plans.map((plan,index)=><article className={`plan-card ${index===0?"leading":""}`} key={plan.id}><div className="plan-rank"><small>0{index+1}</small><span>{index===0?"LEADING EXAMPLE":"ALTERNATIVE"}</span></div><div className="plan-main"><div className="plan-top"><div><h2>{plan.crops.join(" → ")}</h2><p>{plan.note}</p></div><strong>{plan.score}<span>/100</span></strong></div><SeasonTimeline crops={plan.crops}/><div className="mini-traits"><Trait label="Water" value={plan.water}/><Trait label="Soil" value={plan.soil}/><Trait label="Climate" value={plan.climate}/><Trait label="Stability" value={plan.stability}/></div><div className="card-actions"><label className="compare-check"><input type="checkbox" checked={selected.includes(plan.id)} onChange={() => setSelected(selected.includes(plan.id)?selected.filter(id=>id!==plan.id):selected.length<3?[...selected,plan.id]:selected)}/> Compare</label><button onClick={()=>setDialogPlan(plan)}>Why this option?</button><button className="primary-button" onClick={()=>savePlan(plan.id)}>Save plan <FiSave/></button></div></div></article>)}</div></> }

function Compare({ plans, selected, setSelected }) { const display=(selected.length?selected:[plans[0].id,plans[1].id]).map(id=>plans.find(p=>p.id===id)).filter(Boolean); return <><PageTitle eyebrow="COMPARE PLANS" title="See the trade-offs clearly." copy="A high overall score can still hide a weak criterion. Compare up to three options side by side." /><div className="compare-grid">{display.map((plan,index)=><article className="compare-card" key={plan.id}><div className="compare-head"><span>OPTION 0{index+1}</span><button onClick={()=>setSelected(selected.filter(id=>id!==plan.id))}><FiX/></button></div><strong className="compare-score">{plan.score}<small>/100</small></strong><h2>{plan.crops.join(" → ")}</h2><SeasonTimeline crops={plan.crops}/>{[["Water fit",plan.water],["Soil health",plan.soil],["Climate resilience",plan.climate],["Stability",plan.stability]].map(([label,value])=><Trait key={label} label={label} value={value}/>) }<div className="tradeoff"><FiInfo/><p>{plan.note}</p></div></article>)}{display.length<3&&<button className="add-compare" onClick={()=>{const next=plans.find(p=>!selected.includes(p.id)); if(next)setSelected([...selected,next.id])}}><FiPlus/><span>Add another plan</span></button>}</div></> }

function Simulator({ rankedPlans, scenario, setScenario, simWeights, setSimWeights, savePlan, setDialogPlan }) { return <><PageTitle eyebrow="WHAT-IF STUDIO" title="Small changes. Different possibilities." copy="Explore how priorities and climate stress scenarios reshape the example ranking." action={<button onClick={()=>{setScenario("Typical");setSimWeights({water:30,soil:25,climate:25,stability:20})}}><FiRefreshCw/> Reset scenario</button>} /><div className="sim-workspace"><section className="control-card"><span className="card-kicker">YOUR PLANNING CONTROLS</span><h2>What matters most?</h2>{Object.entries({water:"Water conservation",soil:"Soil health",climate:"Climate resilience",stability:"Year-to-year stability"}).map(([key,label])=><label className="weight-slider" key={key}><span>{label}<b>{simWeights[key]}%</b></span><input type="range" min="1" max="100" value={simWeights[key]} onChange={e=>setSimWeights({...simWeights,[key]:Number(e.target.value)})}/></label>)}<label className="select-label">Climate stress test<select value={scenario} onChange={e=>setScenario(e.target.value)}><option>Typical</option><option>Dry</option><option>Hot</option></select></label><div className="notice"><FiInfo/> Scenarios are comparisons, not forecasts.</div></section><section className="live-results"><div className="card-head"><div><span className="live-label"><i/> LIVE RANKING</span><h2>See priorities in action.</h2></div><span className="tag">CLIENT-SIDE DEMO</span></div>{rankedPlans.map((plan,index)=><div className={`live-rank ${index===0?"top":""}`} key={plan.id}><span>0{index+1}</span><div><b>{plan.crops.join(" → ")}</b><small>{index===0?"Leading under current scenario":"Alternative"}</small><i><b style={{width:`${plan.simScore}%`}}/></i></div><strong>{plan.simScore.toFixed(1)}</strong><button onClick={()=>setDialogPlan(plan)}>Details</button><button onClick={()=>savePlan(plan.id)}><FiSave/></button></div>)}</section></div></> }

function Climate({ metric, setMetric, navigate }) { const values={Rainfall:[18,26,35,58,92,172,248,220,145,72,30,20],Temperature:[24,27,31,34,35,33,31,31,31,29,26,23],"Soil moisture":[35,32,30,37,48,68,82,78,66,50,41,37]}; const data=values[metric]; return <><PageTitle eyebrow="ENVIRONMENTAL CONTEXT" title="Read the patterns behind the plan." copy="Explore illustrative seasonal patterns and historical variability for your active field." /><section className="chart-card"><div className="chart-header"><div><h2>Rajshahi · Environmental evidence preview</h2><span className="tag amber">ILLUSTRATIVE SERIES</span></div><div className="metric-tabs">{Object.keys(values).map(item=><button className={metric===item?"active":""} onClick={()=>setMetric(item)} key={item}>{item}</button>)}</div></div><div className="bar-chart">{data.map((value,index)=><div className="bar-column" key={index}><span>{value}</span><i style={{height:`${Math.max(14,value/Math.max(...data)*220)}px`}}/><small>{["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][index]}</small></div>)}</div><div className="notice"><FiInfo/> This chart demonstrates the evidence interface using mock values. A future backend would supply quality-controlled observations.</div></section><div className="insight-grid"><Insight icon={<FiCloudRain/>} tag="RAIN & WATER" title="Timing matters as much as totals." copy="Compare rainfall during each crop’s growth window, then assess irrigation access." action={()=>navigate("simulator")}/><Insight icon={<FiThermometer/>} tag="TEMPERATURE" title="Stress-test sensitive seasons." copy="Hot-year scenarios demonstrate how thermal stress can change a plan’s score." action={()=>navigate("simulator")}/><Insight icon={<FiLayers/>} tag="SPATIAL LIMITS" title="A region is larger than a field." copy="Satellite grids represent an area. Local measurements remain essential." action={()=>navigate("methodology")}/></div></> }

function Saved({ saved, plans, navigate, setDialogPlan }) { const plan=plans.find(p=>p.id===saved); if(!plan)return <EmptySaved navigate={navigate}/>; return <><PageTitle eyebrow="SAVED-FIELD PLAN" title="Your plan, kept with its context." copy="Review the choice, assumptions, and visible trade-offs before exporting." /><div className="saved-hero"><div><span className="tag">SAVED PLAN</span><h2>{plan.crops.join(" → ")}</h2><p>{plan.note}</p><SeasonTimeline crops={plan.crops}/></div><strong>{plan.score}<span>/100</span></strong></div><div className="dashboard-grid"><section className="dashboard-card wide"><h2>Why it fits your priorities</h2><div className="trait-grid"><Trait label="Water fit" value={plan.water}/><Trait label="Soil health" value={plan.soil}/><Trait label="Climate" value={plan.climate}/><Trait label="Stability" value={plan.stability}/></div><div className="notice"><FiInfo/> Scores support comparison only; they do not predict yield or guarantee suitability.</div><button onClick={()=>setDialogPlan(plan)}>Open full detail <FiArrowRight/></button></section><section className="dashboard-card"><span className="card-kicker">NEXT STEP</span><h3>Test the plan.</h3><p>Change water, priorities, or stress assumptions without overwriting the saved field.</p><button onClick={()=>navigate("simulator")}>Open What-if studio <FiArrowRight/></button></section></div></> }

function EmptySaved({navigate}) { return <div className="empty-state"><FiBookmark/><span>NO SAVED PLAN</span><h1>Keep one path close.</h1><p>Choose a rotation to save it with your field and return to it later.</p><button className="primary-button" onClick={()=>navigate("rotations")}>Explore rotations <FiArrowRight/></button></div> }

function Methodology() { return <><PageTitle eyebrow="TRANSPARENCY BY DESIGN" title="Know what’s behind every number." copy="The prototype shows the workflow. Scientific validation and live data integration remain future work." /><section className="pipeline-card"><span className="card-kicker">THE DECISION PIPELINE</span><div className="pipeline">{[["01 / CONTEXT","Your field & history","Location, soil, water, crops"],["02 / FEASIBILITY","Filter sequences","Season, water, pH demo rules"],["03 / PRIORITIES","Weight criteria","Normalized preferences"],["04 / EXPLANATION","Rank & compare","Scores, reasons, trade-offs"]].map(([step,title,copy])=><div key={step}><small>{step}</small><b>{title}</b><p>{copy}</p></div>)}</div></section><div className="method-grid"><section className="dashboard-card"><h2>Planned evidence sources</h2>{[["NASA POWER","Meteorological and solar context"],["GPM IMERG","Rainfall history and variability"],["SMAP","Regional soil-moisture context"],["MODIS / VIIRS","Vegetation greenness evidence"]].map(([name,copy])=><div className="data-source" key={name}><div><b>{name}</b><p>{copy}</p></div><span className="tag amber">NOT CONNECTED</span></div>)}</section><section className="dashboard-card"><h2>How to read the results</h2>{["What does the score mean?","Which rules exclude plans?","What about uncertainty?","Observed, derived, and scenario data","Privacy & saved data","Boundaries of this tool"].map((item,index)=><details open={index===0} key={item}><summary>{item}</summary><p>{index===0?"Each crop has four illustrative traits. We average traits across the sequence, normalize your weights to 100%, and sum their contributions. Scores do not predict yield.":"This demonstration keeps assumptions and limitations visible. Production decisions require validated data and local agricultural expertise."}</p></details>)}</section></div></> }

function SeasonTimeline({crops}) { return <div className="season-timeline">{crops.map((crop,index)=><div key={crop}><span>{["KHARIF I","KHARIF II","RABI"][index]}</span><b>{crop}</b><small>{["MAR — JUN","JUL — OCT","NOV — FEB"][index]}</small></div>)}</div> }
function Trait({label,value}) { return <div className="trait"><span>{label}<b>{value}</b></span><i><b style={{width:`${value}%`}}/></i></div> }
function Field({label,children}) { return <label className="form-field"><span>{label}</span>{children}</label> }
function FiMapPinIcon(){return <div className="map-pin"><FiMap/><i/></div>}
function Insight({icon,tag,title,copy,action}){return <article className="insight-card">{icon}<span>{tag}</span><h3>{title}</h3><p>{copy}</p><button onClick={action}>Explore <FiArrowRight/></button></article>}
function WorkspaceContentSkeleton(){return <div className="workspace-inner-skeleton"><div className="sk-line small skeleton-shimmer"/><div className="sk-line title skeleton-shimmer"/><div className="sk-line copy skeleton-shimmer"/><div className="sk-cards"><div className="skeleton-shimmer"/><div className="skeleton-shimmer"/><div className="skeleton-shimmer"/></div></div>}

function PlanDialog({plan,onClose,onSave}) { return <div className="modal-backdrop" onMouseDown={e=>e.target===e.currentTarget&&onClose()}><div className="plan-dialog"><div className="dialog-head"><span className="tag">ROTATION DETAIL / DEMO</span><button onClick={onClose}><FiX/></button></div><div className="dialog-title"><div><h1>{plan.crops.join(" → ")}</h1><p>Three seasons · Rajshahi North Field</p></div><strong>{plan.score}<small>/100</small></strong></div><SeasonTimeline crops={plan.crops}/><div className="dialog-grid"><div><h3>Criterion scores</h3><Trait label="Water fit" value={plan.water}/><Trait label="Soil health" value={plan.soil}/><Trait label="Climate resilience" value={plan.climate}/><Trait label="Stability" value={plan.stability}/></div><div><h3>Why this option?</h3><p>{plan.note}</p><div className="notice"><FiInfo/> Illustrative risk labels are based on mock traits, not an environmental risk model.</div></div></div><div className="dialog-actions"><button onClick={onClose}>Close</button><button className="primary-button" onClick={onSave}>Save this plan <FiSave/></button></div></div></div> }
