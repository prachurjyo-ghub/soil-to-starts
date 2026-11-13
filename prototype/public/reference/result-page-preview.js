/**
 * Local HTML preview bootstrap for reference/result-page.html.
 * Uses workspace chrome + labelled mock fixtures. Not a live app route.
 */
(function () {
  'use strict';

  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const navItems = [
    ['overview', '◫', 'Your results', 'result-page.html'],
    ['profile', '⌖', 'Set up your field', 'workspace-preview.html'],
    ['rotations', '⇄', 'Rotation plans', 'workspace-preview.html'],
    ['compare', '⊞', 'Compare plans', 'workspace-preview.html'],
    ['simulator', '⌁', 'What-if studio', 'workspace-preview.html'],
    ['climate', '◷', 'Climate insights', 'workspace-preview.html'],
    ['saved', '♡', 'Saved plan', 'workspace-preview.html'],
    ['methodology', '◎', 'Data & methodology', 'workspace-preview.html']
  ];

  let language = document.documentElement.lang === 'bn' ? 'bn' : 'en';
  let toastTimer;
  let resultsUI;

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
    if ($('#nav')) {
      $('#nav').innerHTML = navItems.map(([id, icon, label, href]) => {
        const active = id === 'overview';
        return `<a href="${href}" class="${active ? 'active' : ''}" ${active ? 'aria-current="page"' : ''}><span>${icon}</span>${label}</a>`;
      }).join('');
    }
    if ($('#mobile-more-nav')) {
      $('#mobile-more-nav').innerHTML = navItems
        .filter(([id]) => !['overview', 'profile', 'rotations'].includes(id))
        .map(([id, icon, label, href]) => `<a href="${href}"><span aria-hidden="true">${icon}</span>${label}</a>`)
        .join('');
    }
  }

  function paint() {
    language = document.documentElement.lang === 'bn' ? 'bn' : 'en';
    syncChrome();
    const main = $('#main');
    if (!main || !resultsUI) return;
    main.innerHTML = resultsUI.renderFixture(language, { showFixtureBanner: false }) ||
      '<section class="result-card result-empty"><div><h2>Loading mock result…</h2></div></section>';
  }

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

  function openMore() {
    const sheet = $('#mobile-more-sheet');
    const backdrop = $('#mobile-more-backdrop');
    const openBtn = $('#mobile-more-open');
    if (!sheet || !backdrop || !openBtn) return;
    document.body.classList.add('mobile-more-open');
    sheet.hidden = false;
    backdrop.hidden = false;
    openBtn.setAttribute('aria-expanded', 'true');
  }

  function closeMore() {
    const sheet = $('#mobile-more-sheet');
    const backdrop = $('#mobile-more-backdrop');
    const openBtn = $('#mobile-more-open');
    document.body.classList.remove('mobile-more-open');
    if (sheet) sheet.hidden = true;
    if (backdrop) backdrop.hidden = true;
    if (openBtn) openBtn.setAttribute('aria-expanded', 'false');
  }

  async function start() {
    if (!window.STS_RESULT_ADAPTER || !window.STS_RESULT_UI) {
      const main = $('#main');
      if (main) main.textContent = 'Result scripts failed to load. Open this HTML from the prototype/reference folder.';
      return;
    }

    const adapter = window.STS_RESULT_ADAPTER.create();
    resultsUI = window.STS_RESULT_UI.create({
      adapter,
      render: paint,
      navigate: () => { window.location.href = 'workspace-preview.html'; },
      toast,
      downloadInputs: () => toast('This local preview has no genuine intake download.'),
      enterFixtureMode: () => {},
      leaveFixtureMode: () => {}
    });

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
    $('#mobile-more-open')?.addEventListener('click', () => {
      const sheet = $('#mobile-more-sheet');
      if (sheet && !sheet.hidden) closeMore();
      else openMore();
    });
    $('#mobile-more-close')?.addEventListener('click', closeMore);
    $('#mobile-more-backdrop')?.addEventListener('click', closeMore);

    document.addEventListener('click', (event) => {
      const button = event.target.closest('button');
      if (!button) return;
      if (resultsUI.handleClick(button)) return;
      if (button.dataset.action === 'export') {
        resultsUI.downloadReceipt();
        return;
      }
      if (button.dataset.action === 'open-workspace') {
        window.location.href = 'workspace-preview.html';
      }
    });

    document.addEventListener('change', (event) => {
      resultsUI.handleChange(event.target);
    });

    document.addEventListener('sts-language-change', paint);

    await resultsUI.activateFixture('complete-comparison');
    paint();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => { void start(); });
  else void start();
})();
