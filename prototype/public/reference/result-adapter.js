(function (root, factory) {
  const api = factory(typeof module === 'object' && module.exports ? require('./result-fixtures.js') : root.STS_RESULT_FIXTURES);
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.STS_RESULT_ADAPTER = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (fixtures) {
  'use strict';

  const STATES = Object.freeze(['idle', 'validating', 'loading', 'invalid_input', 'unavailable', 'incomplete', 'complete', 'error']);
  const ENDPOINTS = Object.freeze({
    planning: null, currentCrop: null, climate: null, intendedCrop: null, replay: null
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
    const fetchImpl = options.fetchImpl || (typeof fetch === 'function' ? fetch.bind(globalThis) : null);
    const endpoints = { ...ENDPOINTS, ...(options.endpoints || {}) };
    let generation = 0;
    let fixtureId = null;
    let controller = null;

    function invalidate() {
      generation += 1;
      controller?.abort();
      controller = null;
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
      const requestGeneration = ++generation;
      controller?.abort();
      controller = typeof AbortController === 'function' ? new AbortController() : null;

      if (fixtureId) {
        const item = fixtures.fixture(fixtureId);
        const result = { kind, state: stateFrom(item.response), request: item.request, response: item.response, fixture: true, fixture_id: item.fixture_id, fixture_label: item.fixture_label, fixture_description: item.fixture_description };
        return requestGeneration === generation ? result : { kind, state: 'stale', ignored: true };
      }

      const endpoint = endpoints[kind];
      if (!endpoint || !fetchImpl) return unavailable(kind, payload);
      try {
        const response = await fetchImpl(endpoint, {
          method: 'POST', headers: { 'content-type': 'application/json' },
          body: JSON.stringify(payload), signal: controller?.signal
        });
        const body = await response.json().catch(() => null);
        if (requestGeneration !== generation) return { kind, state: 'stale', ignored: true };
        if (!response.ok) {
          return { kind, state: response.status === 422 ? 'invalid_input' : 'error', request: payload, response: body || { status: 'error', reason: `HTTP ${response.status}` }, recoverable: response.status >= 500 };
        }
        return { kind, state: stateFrom(body), request: payload, response: body, fixture: false };
      } catch (error) {
        if (requestGeneration !== generation || error?.name === 'AbortError') return { kind, state: 'stale', ignored: true };
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
