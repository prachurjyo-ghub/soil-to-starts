(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.STS_RESULT_ADAPTER = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const STATES = Object.freeze(['idle', 'validating', 'loading', 'invalid_input', 'unavailable', 'incomplete', 'complete', 'error']);
  const ENDPOINTS = Object.freeze({
    planning: '/api/plan', currentCrop: '/api/current-crop', climate: '/api/climate', intendedCrop: null, replay: null
  });

  function unavailable(kind, request) {
    return {
      kind, state: 'unavailable', request,
      response: {
        status: 'unavailable', data_mode: 'unavailable',
        reason: `The ${kind} service is not connected.`,
        limitations: ['A genuine submission is preserved, but no fixture or legacy scorer is used as a fallback.']
      }
    };
  }

  function stateFrom(response) {
    const status = response?.status;
    if (status === 'complete') return 'complete';
    if (status === 'incomplete') return 'incomplete';
    if (status === 'invalid_input') return 'invalid_input';
    if (status === 'unavailable') return 'unavailable';
    return 'error';
  }

  function create(options = {}) {
    const fixtures=options.fixtures || null;
    const fetchImpl = Object.hasOwn(options, 'fetchImpl') ? options.fetchImpl : (typeof fetch === 'function' ? fetch.bind(globalThis) : null);
    const endpoints = { ...ENDPOINTS, ...(options.endpoints || {}) };
    let generation = 0;
    let fixtureId = null;
    const channels = new Map();

    function invalidate() {
      generation += 1;
      for (const channel of channels.values()) channel.controller?.abort();
      channels.clear();
    }
    function disableFixture() { fixtureId = null; invalidate(); }
    function enableFixture(id, explicit = false) {
      if (!explicit) throw new Error('Fixture mode requires an explicit user action.');
      if (!fixtures?.ids?.includes(id)) throw new Error(`Unknown fixture: ${id}`);
      fixtureId = id;
      invalidate();
      return fixtureId;
    }
    function activeFixture() { return fixtureId; }

    async function request(kind, payload) {
      const requestGeneration = generation;
      channels.get(kind)?.controller?.abort();
      const channel = { controller: typeof AbortController === 'function' ? new AbortController() : null };
      channels.set(kind, channel);
      const isCurrent = () => requestGeneration === generation && channels.get(kind) === channel;

      if (fixtureId) {
        const item = fixtures.fixture(fixtureId);
        const result = { kind, state: stateFrom(item.response), request: item.request, response: item.response, fixture: true, fixture_id: item.fixture_id, fixture_label: item.fixture_label, fixture_description: item.fixture_description };
        return isCurrent() ? result : { kind, state: 'stale', ignored: true };
      }

      const endpoint = endpoints[kind];
      if (!endpoint || !fetchImpl) return unavailable(kind, payload);
      try {
        const response = await fetchImpl(endpoint, {
          method: 'POST', headers: { 'content-type': 'application/json' },
          body: JSON.stringify(payload), signal: channel.controller?.signal
        });
        const body = await response.json().catch(() => null);
        if (!isCurrent()) return { kind, state: 'stale', ignored: true };
        if (!response.ok) {
          return { kind, state: response.status === 422 ? 'invalid_input' : 'error', request: payload, response: body || { status: 'error', reason: `HTTP ${response.status}` }, recoverable: response.status >= 500 };
        }
        if (!body || typeof body !== 'object' || Array.isArray(body)) return { kind, state: 'error', request: payload, response: { status: 'error', reason: 'The service returned an invalid response.' }, recoverable: true };
        if (body.data_mode === 'development_fixture') return { kind, state: 'error', request: payload, response: { status: 'error', reason: 'A genuine request cannot return development-fixture data.' } };
        if (kind === 'planning' && body.status === 'complete') {
          const alternatives = body.alternatives;
          const valid = body.baseline_assessment && Array.isArray(alternatives) && alternatives.length >= 2
            && new Set(alternatives.map(plan => plan?.plan_id)).size === alternatives.length
            && alternatives.every(plan => plan?.plan_id && plan.status === 'complete' && Array.isArray(plan.steps) && plan.steps.length === 3);
          if (!valid) return { kind, state: 'error', request: payload, response: { status: 'error', reason: 'The service returned an inconsistent complete comparison. No missing crops or plans were filled in.' } };
        }
        return { kind, state: stateFrom(body), request: payload, response: body, fixture: false };
      } catch (error) {
        if (!isCurrent() || error?.name === 'AbortError') return { kind, state: 'stale', ignored: true };
        return { kind, state: 'error', request: payload, response: { status: 'error', reason: 'The service request failed.', limitations: [String(error?.message || error)] }, recoverable: true };
      }
    }

    return {
      states: STATES, endpoints: { ...endpoints }, invalidate, enableFixture, disableFixture, activeFixture,
      requestPlanning: payload => request('planning', payload),
      requestCurrentCrop: payload => request('currentCrop', payload),
      requestClimate: payload => request('climate', payload),
      checkIntendedCrop: payload => request('intendedCrop', payload),
      runReplay: payload => request('replay', payload)
    };
  }

  return { STATES, ENDPOINTS, create, stateFrom };
});
