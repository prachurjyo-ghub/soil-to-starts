(() => {
  'use strict';
  const doc = document.documentElement;
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const THEME_KEY = 'soil-to-stars-theme-v1';
  const savedTheme = (() => { try { return localStorage.getItem(THEME_KEY); } catch { return null; } })();
  function setTheme(theme) {
    doc.dataset.theme = theme;
    $('#theme-toggle').setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    $('#theme-toggle').title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    try { localStorage.setItem(THEME_KEY, theme); } catch {}
  }
  setTheme(savedTheme || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
  $('#theme-toggle').addEventListener('click', () => setTheme(doc.dataset.theme === 'dark' ? 'light' : 'dark'));

  const menuButton = $('#menu-trigger');
  const mainNav = $('#primary-nav');
  function closeMenu() { mainNav.classList.remove('open'); menuButton.setAttribute('aria-expanded', 'false'); menuButton.setAttribute('aria-label', 'Open navigation'); }
  menuButton.addEventListener('click', () => {
    const isOpen = mainNav.classList.toggle('open');
    menuButton.setAttribute('aria-expanded', String(isOpen));
    menuButton.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
  });
  $$('#primary-nav a').forEach(a => a.addEventListener('click', closeMenu));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });

  const scenarios = {
    balanced: { temp:28, title:'A clear, warm season', indicator:'Balanced', color:'#f1dfa2' },
    wet: { temp:25, title:'Rainfall changes the picture', indicator:'Rainy', color:'#c8e0fc' },
    hot: { temp:35, title:'Warmer days, greater stress', indicator:'Hot', color:'#ffca9a' }
  };
  $$('.scenario').forEach(btn => btn.addEventListener('click', () => {
    const scenario = scenarios[btn.dataset.scenario];
    $$('.scenario').forEach(other => { other.classList.toggle('active', other === btn); other.setAttribute('aria-pressed', String(other === btn)); });
    $('#weather-temp').textContent = scenario.temp;
    $('#weather-label').textContent = scenario.title;
    $('#scenario-indicator').textContent = scenario.indicator;
    $('#weather-icon').style.color = scenario.color;
  }));

  const video = $('#hero-video');
  const videoToggle = $('#video-toggle');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const icon = $('#video-toggle-icon');
  const motionText = $('#video-toggle-text');
  const setVideoLabel = () => {
    const paused = video.paused;
    icon.textContent = paused ? '▶' : 'Ⅱ';
    motionText.textContent = paused ? 'Play motion' : 'Pause motion';
    videoToggle.setAttribute('aria-label', paused ? 'Play background motion' : 'Pause background motion');
  };
  let userPaused = reducedMotion.matches;
  let heroVisible = true;
  video.muted = true;
  const syncPlayback = () => {
    if (userPaused || !heroVisible || document.hidden) video.pause();
    else video.play().catch(() => { setVideoLabel(); });
  };
  video.addEventListener('play', setVideoLabel);
  video.addEventListener('pause', setVideoLabel);
  videoToggle.addEventListener('click', () => {
    userPaused = !video.paused;
    syncPlayback();
    setVideoLabel();
  });
  document.addEventListener('visibilitychange', syncPlayback);
  reducedMotion.addEventListener('change', event => {
    userPaused = event.matches;
    syncPlayback();
  });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      heroVisible = entries[0].isIntersecting;
      syncPlayback();
    }, { threshold: 0 }).observe(document.querySelector('.hero'));
  }
  syncPlayback();
  setVideoLabel();

  const factors = ['water', 'soil', 'climate', 'stability'];
  const presets = {
    water: { water:40, soil:25, climate:20, stability:15 },
    soil: { water:10, soil:45, climate:25, stability:20 },
    balanced: { water:25, soil:25, climate:25, stability:25 },
    climate: { water:15, soil:20, climate:45, stability:20 }
  };
  const rotations = [
    { id:'a', crops:['Rice','Lentil','Maize'], values:{ water:45,soil:80,climate:65,stability:75 }, reason:'A rotation with a useful legume stage and a stronger soil-health score.' },
    { id:'b', crops:['Maize','Lentil','Mustard'], values:{ water:85,soil:65,climate:78,stability:55 }, reason:'This example benefits from lower water demand and strong climate-fit scores.' },
    { id:'c', crops:['Rice','Mungbean','Vegetables'], values:{ water:35,soil:65,climate:55,stability:70 }, reason:'A diverse sequence with a different water-demand trade-off.' }
  ];
  let weights = {...presets.water};
  function roundedPercentages(raw) {
    const total = factors.reduce((s,k) => s+Number(raw[k]),0);
    if (!total) return {...presets.balanced};
    const exact = factors.map(k => 100 * raw[k] / total);
    const ints = exact.map(x => Math.floor(x));
    let remaining = 100 - ints.reduce((s,x) => s+x,0);
    const order = [...factors.keys()].sort((a,b) => (exact[b]-ints[b])-(exact[a]-ints[a]));
    for (let i=0;i<remaining;i++) ints[order[i]]++;
    return Object.fromEntries(factors.map((k,i) => [k,ints[i]]));
  }
  function render(updateSliders = false) {
    const pct = roundedPercentages(weights);
    for(const f of factors) {
      $(`#${f}-out`).textContent = pct[f] + '%';
      if (updateSliders) $(`#${f}-range`).value = weights[f];
      $(`#${f}-range`).style.setProperty('--fill', pct[f] + '%');
    }
    const ranked = rotations.map(r => ({...r, score:factors.reduce((s,f) => s + r.values[f]*pct[f]/100,0)})).sort((a,b) => b.score-a.score);
    $('#ranked-options').innerHTML = ranked.map((r,i) => `
      <div class="rank-option ${i===0?'first':''}">
        <span class="rank-order">0${i+1}</span>
        <div><div class="rank-name">${r.crops.join(' → ')}</div><div class="rank-crops"><span>${i===0?'Leading example':'Alternative'}</span><i></i><span>Three-season rotation</span></div></div>
        <span class="rank-score">${r.score.toFixed(1)}<small>DEMO SCORE</small></span>
      </div>`).join('');
    const winner = ranked[0];
    const lead = ranked[0].score - ranked[1].score;
    const isClose = lead < 3;
    $('#winner-explanation').innerHTML = `<strong>${isClose ? 'A close call — explore the trade-offs.' : 'Why this option moves to the top:'}</strong> ${winner.reason} ${isClose?'The first two sample scores are close, so small priority changes can alter the ranking.':'Try another priority preset and watch the order change.'}`;
  }
  function choosePreset(name) {
    weights = {...presets[name]};
    $$('.preset').forEach(btn => { const active = btn.dataset.preset === name; btn.classList.toggle('active', active); btn.setAttribute('aria-pressed',String(active)); });
    render(true);
  }
  $$('.preset').forEach(btn => btn.addEventListener('click', () => choosePreset(btn.dataset.preset)));
  factors.forEach(f => $(`#${f}-range`).addEventListener('input', e => {
    weights[f] = Number(e.target.value);
    $$('.preset').forEach(btn => { btn.classList.remove('active'); btn.setAttribute('aria-pressed','false'); });
    render();
  }));
  $('#reset-priorities').addEventListener('click', () => choosePreset('water'));
  render(true);

  const fieldDialog = $('#field-dialog');
  const openFieldDialog = () => { if(!fieldDialog.open) fieldDialog.showModal(); };
  $('#start-field').addEventListener('click', openFieldDialog);
  $('#closing-start').addEventListener('click', openFieldDialog);
  $('#dialog-close').addEventListener('click', () => fieldDialog.close());
  fieldDialog.addEventListener('click', e => { if(e.target === fieldDialog) fieldDialog.close(); });
  $('#field-form').addEventListener('submit', e => {
    e.preventDefault();
    const p = $('#priority-choice').value;
    const w = $('#water-choice').value;
    try {
      const saved = JSON.parse(localStorage.getItem('sts-studio-v1') || 'null');
      const weights = {water:[45,15,15,10,5,10],soil:[10,45,15,10,10,10],climate:[15,15,45,10,5,10],balanced:[20,20,20,15,10,15]}[p];
      const water = w === 'rainfed' ? 'Rain-fed' : w === 'reliable' ? 'Reliable' : 'Limited';
      if (saved?.fields?.length) {
        const field = saved.fields.find(f => f.id === saved.current) || saved.fields[0];
        field.water = water; field.weights = weights;
        localStorage.setItem('sts-studio-v1', JSON.stringify(saved));
      } else {
        localStorage.setItem('sts-studio-onboarding', JSON.stringify({water,weights}));
      }
    } catch {}
    window.location.href = '/workspace#profile';
  });

  if ('IntersectionObserver' in window && !reducedMotion.matches) {
    const io = new IntersectionObserver(entries => entries.forEach(entry => {if(entry.isIntersecting) { entry.target.classList.add('is-visible'); io.unobserve(entry.target); }}), {threshold:0.12});
    $$('.reveal').forEach(el => io.observe(el));
  } else { $$('.reveal').forEach(el => el.classList.add('is-visible')); }
})();
