/**
 * Demo result page: real workspace chrome + labelled mock result data.
 * Not scientific advice. Separate from genuine intake submissions.
 */
(async () => {
  'use strict';
  try {
    await import('./result-fixtures.js');
    await import('./result-adapter.js');
    await import('./result-ui.js');
  } catch {
    const main = document.getElementById('main');
    if (main) main.textContent = 'Result page could not load. Please reload. / ফলাফল পৃষ্ঠা লোড হয়নি। আবার লোড করুন।';
    return;
  }

  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const navItems = [
    ['overview', '◫', 'Your results', '/result-page'],
    ['profile', '⌖', 'Set up your field', '/workspace#profile'],
    ['rotations', '⇄', 'Rotation plans', '/workspace#rotations'],
    ['compare', '⊞', 'Compare plans', '/workspace#compare'],
    ['simulator', '⌁', 'What-if studio', '/workspace#simulator'],
    ['climate', '◷', 'Climate insights', '/workspace#climate'],
    ['saved', '♡', 'Saved plan', '/workspace#saved'],
    ['methodology', '◎', 'Data & methodology', '/workspace#methodology']
  ];

  let language = document.documentElement.lang === 'bn' ? 'bn' : 'en';
  let toastTimer;

  function toast(message) {
    const el = $('#toast');
    if (!el) return;
    el.textContent = message;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('show'), 3200);
  }

  function syncChrome() {
    const crumb = language === 'bn' ? 'ফলাফল' : 'Your results';
    if ($('#crumb')) $('#crumb').textContent = crumb;
    if ($('#mobile-crumb')) $('#mobile-crumb').textContent = crumb;
    $$('.demo-dot').forEach((el) => {
      el.textContent = language === 'bn' ? 'নমুনা ফলাফল · বৈজ্ঞানিক পরামর্শ নয়' : 'Illustrative result · not scientific advice';
    });
    if ($('#field-select')) $('#field-select').hidden = true;
    const fieldLabel = $('.field-switch small');
    if (fieldLabel) fieldLabel.textContent = language === 'bn' ? 'নমুনা ফলাফল' : 'DEMO RESULT';
    const newField = $('.field-switch button');
    if (newField) {
      newField.textContent = language === 'bn' ? '← জমির তথ্যে যান' : '← Go to field intake';
      newField.onclick = () => { window.location.href = '/workspace#profile'; };
    }
    if ($('#nav')) {
      $('#nav').innerHTML = navItems.map(([id, icon, label, href]) => {
        const active = id === 'overview';
        return `<a href="${href}" class="${active ? 'active' : ''}" ${active ? 'aria-current="page"' : ''}><span>${icon}</span>${label}</a>`;
      }).join('');
    }
    $$('#mobile-tabbar [data-tab]').forEach((link) => {
      const on = link.dataset.tab === 'overview';
      link.classList.toggle('is-active', on);
      if (on) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
      if (link.dataset.tab === 'overview') link.setAttribute('href', '/result-page');
      else if (link.dataset.tab === 'profile') link.setAttribute('href', '/workspace#profile');
      else if (link.dataset.tab === 'rotations') link.setAttribute('href', '/workspace#rotations');
    });
  }

  function paint() {
    language = document.documentElement.lang === 'bn' ? 'bn' : 'en';
    syncChrome();
    const main = $('#main');
    if (!main) return;
    main.innerHTML = resultsUI.renderFixture(language, { showFixtureBanner: false }) ||
      '<section class="result-card result-empty"><div><h2>Loading result…</h2></div></section>';
  }

  function goWorkspace(hash = 'profile') {
    window.location.href = `/workspace#${hash}`;
  }

  const adapter = window.STS_RESULT_ADAPTER.create();
  const resultsUI = window.STS_RESULT_UI.create({
    adapter,
    render: paint,
    navigate: (route) => goWorkspace(route === 'profile' ? 'profile' : 'overview'),
    toast,
    downloadInputs: () => toast('This demo page has no genuine intake download. Open Field Studio to export inputs.'),
    enterFixtureMode: () => {},
    leaveFixtureMode: () => {}
  });

  function syncThemeLabel() {
    const dark = document.body.classList.contains('dark');
    const label = dark ? 'Switch to light mode' : 'Switch to dark mode';
    const theme = $('#theme');
    const mobileTheme = $('#mobile-theme');
    if (theme) { theme.setAttribute('aria-label', label); theme.title = label; }
    if (mobileTheme) { mobileTheme.setAttribute('aria-label', label); mobileTheme.textContent = label; }
  }

  function toggleTheme() {
    document.body.classList.toggle('dark');
    syncThemeLabel();
    try { localStorage.setItem('sts-studio-theme', document.body.classList.contains('dark') ? 'dark' : 'light'); } catch {}
  }

  $('#theme')?.addEventListener('click', toggleTheme);
  $('#mobile-theme')?.addEventListener('click', toggleTheme);
  try { document.body.classList.toggle('dark', (localStorage.getItem('sts-studio-theme') || 'light') === 'dark'); } catch {}
  syncThemeLabel();

  $('#menu')?.addEventListener('click', () => {
    if (!window.matchMedia('(max-width:800px)').matches) {
      $('#sidebar')?.classList.toggle('open');
      $('#menu')?.setAttribute('aria-expanded', String($('#sidebar')?.classList.contains('open')));
    }
  });

  document.addEventListener('click', (event) => {
    const button = event.target.closest('button');
    if (!button) return;
    if (resultsUI.handleClick(button)) return;
    if (button.dataset.action === 'export') {
      resultsUI.downloadReceipt();
      return;
    }
    if (button.dataset.action === 'new-field') goWorkspace('profile');
  });

  document.addEventListener('change', (event) => {
    resultsUI.handleChange(event.target);
  });

  document.addEventListener('sts-language-change', () => {
    paint();
  });

  $$('[data-action="export"]').forEach((btn) => { btn.textContent = 'Export example ↗'; });

  await resultsUI.activateFixture('complete-comparison');
  paint();
})();
