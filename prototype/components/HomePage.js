"use client";

import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import {
  FiArrowDown, FiArrowUpRight, FiBarChart2, FiCheck, FiCloudRain,
  FiDroplet, FiGlobe, FiInfo, FiMapPin, FiMenu, FiPause, FiPlay,
  FiRadio, FiSun, FiThermometer, FiX,
} from "react-icons/fi";
import { PiLeaf, PiPlant } from "react-icons/pi";
import Brand from "./Brand";
import Reveal from "./Reveal";
import ThemeLanguage from "./ThemeLanguage";

const scenarios = {
  balanced: { temp: 28, label: "A clear, warm season", indicator: "Balanced", icon: FiSun },
  wet: { temp: 25, label: "Rain moving through", indicator: "Wet", icon: FiCloudRain },
  hot: { temp: 34, label: "Heat building", indicator: "Hot", icon: FiThermometer },
};

const rotations = [
  { name: "Maize → Mungbean → Mustard", crop: "MAIZE · MUNGBEAN · MUSTARD", values: { water: 86, soil: 91, climate: 78, stability: 84 } },
  { name: "Sesame → Rice → Lentil", crop: "SESAME · RICE · LENTIL", values: { water: 67, soil: 88, climate: 91, stability: 78 } },
  { name: "Jute → Vegetables → Wheat", crop: "JUTE · VEGETABLES · WHEAT", values: { water: 78, soil: 72, climate: 84, stability: 91 } },
];

const presets = {
  water: { water: 50, soil: 20, climate: 15, stability: 15 },
  soil: { water: 15, soil: 50, climate: 20, stability: 15 },
  balanced: { water: 25, soil: 25, climate: 25, stability: 25 },
  climate: { water: 20, soil: 15, climate: 50, stability: 15 },
};

export default function HomePage() {
  const router = useRouter();
  const [menu, setMenu] = useState(false);
  const [scenario, setScenario] = useState("balanced");
  const [playing, setPlaying] = useState(true);
  const [weights, setWeights] = useState(presets.water);
  const [preset, setPreset] = useState("water");
  const [layer, setLayer] = useState("rain");
  const [dialog, setDialog] = useState(false);
  const video = useRef(null);
  const currentScenario = scenarios[scenario];
  const WeatherIcon = currentScenario.icon;

  useEffect(() => {
    if (!video.current) return;
    if (playing) video.current.play().catch(() => setPlaying(false));
    else video.current.pause();
  }, [playing]);

  function choosePreset(name) {
    setPreset(name);
    setWeights(presets[name]);
  }

  const total = Object.values(weights).reduce((a, b) => a + b, 0) || 1;
  const ranked = rotations.map((rotation) => ({
    ...rotation,
    score: Object.entries(rotation.values).reduce((sum, [key, value]) => sum + value * weights[key] / total, 0),
  })).sort((a, b) => b.score - a.score);

  function submitField(event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    localStorage.setItem("sts-starter", JSON.stringify(data));
    router.push("/workspace#profile");
  }

  return (
    <div className="site-page">
      <a className="skip-link" href="#main">Skip to content</a>
      <header className="site-header">
        <div className="container header-inner">
          <Brand />
          <nav className={`main-nav ${menu ? "open" : ""}`} aria-label="Main navigation">
            <a href="#approach" onClick={() => setMenu(false)}>Our approach</a>
            <a href="#simulator" onClick={() => setMenu(false)}>Explore possibilities</a>
            <a href="#evidence" onClick={() => setMenu(false)}>The science</a>
            <Link className="mobile-workspace-link" href="/workspace">Open workspace <FiArrowUpRight /></Link>
          </nav>
          <div className="header-actions">
            <ThemeLanguage />
            <Link className="button button-dark header-cta" href="/workspace">Open workspace <FiArrowUpRight /></Link>
            <button className="menu-button" onClick={() => setMenu(!menu)} aria-expanded={menu} aria-label="Toggle navigation">{menu ? <FiX /> : <FiMenu />}</button>
          </div>
        </div>
      </header>

      <main id="main">
        <section className="hero">
          <div className="hero-media" aria-hidden="true">
            <video ref={video} muted loop playsInline autoPlay poster="/assets/field-landscape.webp"><source src="/assets/farmland-smooth.mp4" type="video/mp4" /></video>
            <div className="hero-grade" />
          </div>
          <div className="container hero-content">
            <div className="hero-copy hero-enter">
              <div className="eyebrow"><PiPlant /> GROUNDED IN EARTH. GUIDED BY DATA. <i /></div>
              <h1>The sky holds<br />the <em>insight.</em><br />Your field holds<br />the <span>future.</span></h1>
              <p>Satellite observations meet the knowledge of the people who farm the land. Explore smarter crop choices, one season at a time.</p>
              <div className="hero-buttons">
                <button className="button button-lime button-large" onClick={() => setDialog(true)}>Explore your field <FiArrowUpRight /></button>
                <a className="button button-glass button-large" href="#approach"><span className="play-dot"><FiPlay /></span> Discover how it works</a>
              </div>
              <small className="hero-note"><i /> A transparent, research-led prototype for Bangladesh</small>
            </div>

            <aside className="observer hero-enter delay" aria-label="Interactive illustrative climate preview">
              <div className="observer-top"><span><i /> FIELD INTELLIGENCE / DEMO</span><b>01 — 03</b></div>
              <div className="observer-location">RAJSHAHI, BANGLADESH <FiMapPin /></div>
              <div className="observer-weather">
                <div><small>Example daytime temperature</small><strong>{currentScenario.temp}<sup>°C</sup></strong><p>{currentScenario.label}</p></div>
                <WeatherIcon className="weather-icon" />
              </div>
              <div className="mini-chart">
                <div><span>Illustrative seasonal pattern</span><b>{currentScenario.indicator}</b></div>
                <svg viewBox="0 0 345 64" preserveAspectRatio="none"><path className="chart-fill" d="M0 55L0 38C30 26 54 46 83 27S140 12 172 32S223 44 258 21S311 33 345 12L345 64L0 64Z"/><path d="M0 38C30 26 54 46 83 27S140 12 172 32S223 44 258 21S311 33 345 12"/></svg>
              </div>
              <small className="observer-caption">SEE HOW CONDITIONS CAN CHANGE</small>
              <div className="scenario-tabs">
                {[['balanced', 'Clear skies'], ['wet', 'Rainy day'], ['hot', 'Hot day']].map(([key, label]) => <button className={scenario === key ? "active" : ""} onClick={() => setScenario(key)} key={key}>{label}</button>)}
              </div>
              <p className="observer-disclaimer"><FiInfo /> Interactive examples only — not live weather or measured field conditions.</p>
            </aside>
          </div>
          <div className="container hero-bottom">
            <a href="#approach"><FiArrowDown /> SCROLL TO SEE THE BIGGER PICTURE</a>
            <div><span><b>01</b> Observe climate</span><i /><span><b>02</b> Understand your field</span><i /><span><b>03</b> Plan ahead</span></div>
            <button onClick={() => setPlaying(!playing)}>{playing ? <FiPause /> : <FiPlay />} {playing ? "Pause motion" : "Play motion"}</button>
          </div>
        </section>

        <section className="section approach" id="approach">
          <div className="container">
            <Reveal><SectionLine number="01 / THE IDEA" label="SCIENCE MEETS THE SOIL" /></Reveal>
            <Reveal className="split-heading"><div><p className="kicker">MORE THAN A WEATHER REPORT</p><h2>Good farming starts<br />with <em>better questions.</em></h2></div><p>What grew here before? How dependable is the rain? Which crops fit the next season? The best decisions consider the whole picture—not a single number.</p></Reveal>
            <div className="journey-grid">
              <Reveal delay={0}><JourneyCard number="01" tag="FROM ABOVE" image="/assets/field-landscape.webp" category="OBSERVE THE ENVIRONMENT" title={<>See the patterns<br />you cannot see.</>} copy="Understand the regional conditions behind your next growing season." href="/workspace#climate" icon={<FiRadio />} /></Reveal>
              <Reveal delay={100}><JourneyCard number="02" tag="ON THE GROUND" image="/assets/mustard-detail.jpg" category="BRING IN LOCAL EXPERIENCE" title={<>Start with what<br />farmers know.</>} copy="Your soil, crop history, and water access give the bigger picture its meaning." href="/workspace#profile" icon={<PiPlant />} /></Reveal>
              <Reveal delay={200}><JourneyCard number="03" tag="WHAT COMES NEXT" category="PLAN ACROSS SEASONS" title={<>Compare the<br />road ahead.</>} copy="Explore full rotations and understand what each option gives—and gives up." href="/workspace#rotations" icon={<FiBarChart2 />} sequence /></Reveal>
            </div>
          </div>
        </section>

        <section className="section simulator" id="simulator">
          <div className="sim-glow" />
          <div className="container">
            <Reveal><SectionLine number="02 / INTERACTIVE DEMO" label="EVERY FARM HAS ITS PRIORITIES" light /></Reveal>
            <Reveal className="split-heading sim-heading"><div><p className="kicker lime">MAKE A CHANGE. SEE THE DIFFERENCE.</p><h2>One field.<br /><em>Different futures.</em></h2></div><p>There&apos;s no universal “best” crop rotation. Change what matters to you and see how the example rankings respond.</p></Reveal>
            <div className="sim-layout">
              <Reveal className="priority-panel">
                <div className="panel-top"><span>YOUR PRIORITIES</span><b>ILLUSTRATIVE ENGINE</b></div>
                <h3>What matters most<br />for your next seasons?</h3>
                <div className="preset-tabs">{[['water','Save water'],['soil','Build soil'],['balanced','Balanced'],['climate','Resilience']].map(([key,label]) => <button className={preset === key ? "active" : ""} onClick={() => choosePreset(key)} key={key}>{label}</button>)}</div>
                <div className="sliders">{[['water','Water conservation'],['soil','Soil health'],['climate','Climate resilience'],['stability','Year-to-year stability']].map(([key,label]) => <label key={key}><span>{label}<output>{weights[key]}%</output></span><input type="range" min="1" max="100" value={weights[key]} onChange={event => { setPreset(""); setWeights({...weights, [key]: Number(event.target.value)}) }} /></label>)}</div>
                <div className="panel-foot"><span>WEIGHTS NORMALIZE TO 100%</span><button onClick={() => choosePreset("water")}>Reset ↺</button></div>
              </Reveal>
              <Reveal className="results-panel" delay={120}>
                <div className="results-head"><div><span><i /> INSTANT COMPARISON</span><h3>How the options stack up</h3></div><b>RAJSHAHI · SAMPLE FIELD</b></div>
                <div className="ranked-list">{ranked.map((item,index) => <div className={`ranked-item ${index === 0 ? "winner" : ""}`} key={item.name}><div className="rank-number">0{index+1}</div><div className="rank-copy"><small>{index === 0 ? "LEADING EXAMPLE" : "ALTERNATIVE"}</small><strong>{item.name}</strong><span>{item.crop}</span><div className="score-track"><i style={{ width: `${item.score}%` }} /></div></div><b className="rank-score">{item.score.toFixed(1)}<small>/100</small></b></div>)}</div>
                <div className="winner-note"><PiLeaf /><p><b>Why this option moves to the top:</b><br />{ranked[0].values.soil > 85 ? "A useful legume stage and a strong soil-health score." : "This sequence follows the priorities you selected."}</p></div>
                <p className="disclaimer"><FiInfo /> Scores are illustrative mathematical examples, not agricultural recommendations.</p>
              </Reveal>
            </div>
            <div className="sim-bottom"><span>DESIGNED TO EXPLAIN THE “WHY,” NOT PRETEND TO KNOW EVERYTHING.</span><Link href="/workspace">Explore the full prototype <FiArrowUpRight /></Link></div>
          </div>
        </section>

        <section className="section evidence" id="evidence">
          <div className="container">
            <Reveal><SectionLine number="03 / THE EVIDENCE" label="TRANSPARENCY IS PART OF THE DESIGN" /></Reveal>
            <div className="evidence-grid">
              <Reveal className="evidence-copy"><p className="kicker">NOT MAGIC. NOT GUESSWORK.</p><h2>From distant orbit<br />to <em>down-to-earth</em><br />decisions.</h2><p>Environmental observations reveal regional trends. Your field knowledge adds context. Clear rules connect the two—so each example suggestion comes with a reason, not a mystery.</p><Link className="text-link" href="/workspace#methodology">Explore the data methodology <FiArrowUpRight /></Link></Reveal>
              <Reveal className="atlas" delay={100}>
                <div className="atlas-head"><span>FIELD SIGNALS / EXPLAINED</span><b>ILLUSTRATIVE VIEW</b></div>
                <div className="atlas-photo"><Image src="/assets/mustard-landscape.jpg" alt="Mustard field landscape" fill sizes="(max-width: 768px) 100vw, 50vw" unoptimized /><div className="field-shape" /><FiRadio className="satellite-icon" /><span>24.37° N / 88.60° E<small>EXAMPLE FIELD FOOTPRINT</small></span><b>Your field<small>Local knowledge at the center</small></b></div>
                <div className="atlas-tabs">{[['rain','Rainfall'],['soil','Soil context'],['crop','Crop knowledge']].map(([key,label]) => <button onClick={() => setLayer(key)} className={layer === key ? "active" : ""} key={key}>{label}</button>)}</div>
                <div className="atlas-readout"><span>{layer === 'rain' ? '01' : layer === 'soil' ? '02' : '03'}</span><div><b>{layer === 'rain' ? 'Look for patterns, not promises.' : layer === 'soil' ? 'Your soil tells its own story.' : 'Connect one season to the next.'}</b><p>{layer === 'rain' ? 'Regional rainfall history adds context to water decisions.' : layer === 'soil' ? 'Texture, drainage, and measured pH help narrow feasible options.' : 'Crop families and planting windows connect context to a plan.'}</p></div></div>
              </Reveal>
            </div>
            <Reveal className="evidence-values">{["Real observations are labeled by source and coverage.","Unknown soil measurements remain unknown.","Options show constraints, trade-offs, and uncertainty."].map((text,index) => <div key={text}><strong>0{index+1}</strong><span>{text}</span><FiCheck /></div>)}</Reveal>
          </div>
        </section>

        <section className="closing">
          <div className="closing-art"><div className="stars" /><div className="hill hill-one"/><div className="hill hill-two"/><div className="hill hill-three"/></div>
          <div className="container closing-layout"><div><span>A WIDER VIEW. A MORE THOUGHTFUL SEASON.</span><h2>Look up.<br /><em>Plan ahead.</em></h2><p>The sky holds the patterns.<br />You know the land. Bring them together.</p></div><div className="closing-card"><small>YOUR NEXT CHAPTER</small><b>One field.<br />Many possibilities.</b><span>Set up your field in four simple steps.</span><button className="button button-lime button-large" onClick={() => setDialog(true)}>Start exploring <FiArrowUpRight /></button></div></div>
        </section>
      </main>

      <footer className="site-footer"><div className="container"><Brand /><p>Connecting Earth observations with everyday farming.<small>Independent research prototype · Bangladesh pilot</small></p><nav><a href="#approach">Approach</a><a href="#simulator">Interactive demo</a><Link href="/workspace">Workspace</Link><span>© 2026 Soil to Stars</span></nav></div></footer>

      {dialog && <div className="modal-backdrop" onMouseDown={event => event.target === event.currentTarget && setDialog(false)}><form className="field-modal" onSubmit={submitField}><div className="modal-top"><span className="kicker">A GOOD PLACE TO BEGIN</span><button type="button" onClick={() => setDialog(false)} aria-label="Close"><FiX /></button></div><h2>Tell us a little<br />about your <em>field.</em></h2><p>Set your starting preferences, then complete your field profile in the workspace. Your answers are saved in this browser.</p><label>Pilot region<select name="region"><option>Rajshahi, Bangladesh</option></select></label><label>Water availability<select name="water"><option value="Limited">Sometimes available</option><option value="Rain-fed">Rain-fed only</option><option value="Reliable">Reliable irrigation</option></select></label><label>Main planning priority<select name="priority"><option value="water">Save water</option><option value="soil">Improve soil health</option><option value="climate">Climate resilience</option><option value="balanced">Balanced</option></select></label><button className="button button-dark modal-submit">Continue to field setup <FiArrowUpRight /></button><small className="modal-note">PROTOTYPE ONLY · NO ACCOUNT NEEDED</small></form></div>}
    </div>
  );
}

function SectionLine({ number, label, light = false }) {
  return <div className={`section-line ${light ? "light" : ""}`}><strong>{number}</strong><i /><span>{label}</span></div>;
}

function JourneyCard({ number, tag, image, category, title, copy, href, icon, sequence }) {
  return <article className="journey-card"><div className={`journey-media ${sequence ? "sequence" : ""}`}>{image && <Image src={image} alt="" fill sizes="(max-width: 768px) 100vw, 33vw" unoptimized />}<div className="media-grade"/><div className="journey-media-top"><span>{number} / {tag}</span><b>ILLUSTRATIVE</b></div>{sequence ? <div className="season-stack"><div><span>01 / KHARIF I</span><b>Maize 🌽</b></div><div><span>02 / KHARIF II</span><b>Mungbean 🌱</b></div><div><span>03 / RABI</span><b>Mustard 🌼</b></div></div> : <div className="media-icon">{icon}</div>}</div><div className="journey-copy"><span>{category}</span><h3>{title}</h3><p>{copy}</p><Link href={href}>Explore the patterns <FiArrowUpRight /></Link></div></article>;
}
