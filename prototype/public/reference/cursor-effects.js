(() => {
  'use strict';

  const finePointer = matchMedia('(hover: hover) and (pointer: fine)');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  if (!finePointer.matches || reducedMotion.matches) return;

  const root = document.documentElement;
  const aura = document.createElement('span');
  aura.className = 'cursor-fx-aura';
  aura.setAttribute('aria-hidden', 'true');
  document.body.append(aura);

  let x = -100;
  let y = -100;
  let loadingTimer;

  const enabled = () => root.classList.contains('nature-cursor');
  const setPosition = (nextX, nextY) => {
    x = nextX;
    y = nextY;
    aura.style.setProperty('--cursor-x', `${x}px`);
    aura.style.setProperty('--cursor-y', `${y}px`);
  };

  const setLoading = (duration = 700) => {
    if (!enabled()) return;
    clearTimeout(loadingTimer);
    aura.classList.add('is-loading', 'is-visible');
    loadingTimer = setTimeout(() => aura.classList.remove('is-loading'), duration);
  };

  const bloom = (event) => {
    if (!enabled() || event.button !== 0) return;
    const burst = document.createElement('span');
    burst.className = 'cursor-fx-bloom';
    burst.setAttribute('aria-hidden', 'true');
    burst.style.setProperty('--click-x', `${event.clientX}px`);
    burst.style.setProperty('--click-y', `${event.clientY}px`);
    burst.innerHTML = '<i></i><i></i><i></i>';
    document.body.append(burst);
    burst.addEventListener('animationend', () => burst.remove(), { once: true });
  };

  document.addEventListener('pointermove', (event) => {
    setPosition(event.clientX, event.clientY);
    aura.classList.toggle('is-visible', enabled());
    aura.classList.toggle('is-interactive', Boolean(event.target.closest('a,button,input,select,summary,[role="tab"]')));
  }, { passive: true });

  document.addEventListener('pointerleave', () => aura.classList.remove('is-visible'));
  document.addEventListener('pointerdown', bloom, { passive: true });
  document.addEventListener('submit', () => setLoading(1050), true);
  window.addEventListener('hashchange', () => setLoading(420));

  document.addEventListener('click', (event) => {
    const action = event.target.closest('a,button');
    if (!action || action.matches('.cursor-control,[disabled]')) return;
    const isNavigation = action.matches('a[href], [data-route], [data-action="export"]');
    if (isNavigation) setLoading(action.matches('[data-route]') ? 420 : 850);
  }, true);

  new MutationObserver(() => {
    if (!enabled()) aura.classList.remove('is-visible', 'is-interactive', 'is-loading');
  }).observe(root, { attributes: true, attributeFilter: ['class'] });

  window.STS_CURSOR_FX = { loading: setLoading };
})();
