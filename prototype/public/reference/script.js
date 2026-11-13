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

  const openWorkspace = () => { window.location.href = '/workspace#profile'; };
  $('#start-field').addEventListener('click', openWorkspace);
  $('#closing-start').addEventListener('click', openWorkspace);

  if ('IntersectionObserver' in window && !reducedMotion.matches) {
    const io = new IntersectionObserver(entries => entries.forEach(entry => {if(entry.isIntersecting) { entry.target.classList.add('is-visible'); io.unobserve(entry.target); }}), {threshold:0.12});
    $$('.reveal').forEach(el => io.observe(el));
  } else { $$('.reveal').forEach(el => el.classList.add('is-visible')); }
})();
