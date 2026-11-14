const test = require('node:test');
const assert = require('node:assert/strict');

const fixtures = require('./fixtures/result-fixtures.cjs');
const adapterApi = require('../prototype/public/reference/result-adapter.js');
const uiApi = require('../prototype/public/reference/result-ui.js');
const testAdapter=(options={})=>adapterApi.create({...options,fixtures});

test('fixture mode requires an explicit action', () => {
  const adapter = testAdapter({ fetchImpl: null });
  assert.throws(() => adapter.enableFixture('complete-comparison'), /explicit user action/);
  assert.throws(() => adapter.enableFixture('missing-fixture', true), /Unknown fixture/);
});

test('genuine planning request stays unavailable without an endpoint', async () => {
  const adapter = testAdapter({ fetchImpl: null });
  const result = await adapter.requestPlanning({ schema_version: 'farmer-intake.v2' });
  assert.equal(result.state, 'unavailable');
  assert.equal(result.response.data_mode, 'unavailable');
  assert.match(result.response.limitations[0], /no fixture or legacy scorer/i);
});

test('complete fixture has baseline and two distinct three-step alternatives', () => {
  const item = fixtures.fixture('complete-comparison');
  assert.equal(item.response.status, 'complete');
  assert.equal(item.response.baseline_assessment.role, 'baseline');
  assert.equal(item.response.alternatives.length, 2);
  assert.equal(new Set(item.response.alternatives.map(plan => plan.plan_id)).size, 2);
  assert.ok(item.response.alternatives.every(uiApi.planHasThreeSteps));
  assert.equal(item.response.data_mode, 'development_fixture');
  assert.equal(item.response.input_fingerprint, null);
  assert.equal(item.response.result_fingerprint, null);
});

test('incomplete fixture keeps one complete alternative without filler', () => {
  const item = fixtures.fixture('incomplete-one-alternative');
  assert.equal(item.response.status, 'incomplete');
  assert.equal(item.response.alternatives.length, 1);
  assert.ok(uiApi.planHasThreeSteps(item.response.alternatives[0]));
  assert.match(item.response.limitations[0], /second distinct supported alternative is missing/i);
});

test('current crop with unknown stage remains unassessed', () => {
  const assessment = fixtures.fixture('complete-comparison').response.current_crop_assessment;
  assert.equal(assessment.status, 'incomplete');
  assert.equal(assessment.stage, null);
  assert.ok(assessment.checks.every(check => check.outcome === 'unknown'));
});

test('fixture receipt preserves example labels and has no invented fingerprint', () => {
  const item = fixtures.fixture('complete-comparison');
  const receipt = uiApi.receipt(item);
  assert.equal(receipt.fixture, true);
  assert.equal(receipt.receipt_type, 'development_fixture_example');
  assert.match(receipt.warning, /not scientific advice/i);
  assert.equal(receipt.response.result_fingerprint, null);
});

test('fixture state renders missing second alternative and scientific limits', async () => {
  const adapter = testAdapter({ fetchImpl: null });
  let renders = 0;
  const ui = uiApi.create({ adapter, render: () => { renders += 1; }, navigate: () => {}, toast: () => {}, downloadInputs: () => {} });
  await ui.activateFixture('incomplete-one-alternative');
  const html = ui.renderFixture('en');
  assert.match(html, /DEVELOPMENT FIXTURE/);
  assert.match(html, /Second alternative unavailable/);
  assert.match(html, /No real API or climate package loaded/);
  assert.ok(renders > 0);
});

test('invalidating a pending real request prevents stale overwrite', async () => {
  let resolveFetch;
  const fetchImpl = () => new Promise(resolve => { resolveFetch = resolve; });
  const adapter = testAdapter({ fetchImpl, endpoints: { planning: '/api/planning' } });
  const pending = adapter.requestPlanning({ request_id: 'old' });
  adapter.invalidate();
  resolveFetch({ ok: true, status: 200, json: async () => ({ status: 'complete' }) });
  const result = await pending;
  assert.equal(result.state, 'stale');
  assert.equal(result.ignored, true);
});

test('production UI cannot open test fixtures from a user action', () => {
  const adapter=adapterApi.create({fetchImpl:null});
  const ui=uiApi.create({adapter,render(){},navigate(){},toast(){},downloadInputs(){}});
  assert.equal(ui.handleClick({dataset:{resultAction:'open-fixture'}}),false);
  assert.doesNotMatch(ui.renderGenuine(null,'en'),/Open labelled example|open-fixture/);
});

test('genuine summary keeps history and usual practice without inventing coverage', () => {
  const html = uiApi.genuineSummary({
    location: { district_id: 'bd-district-bogura', selection_method: 'district_search' },
    current: { state: 'growing', crop_id: 'rice', sown_on: null },
    availability: { kind: 'date', start: '2026-11-15', basis: 'farmer_estimate' },
    crop_history: { state: 'entries', entries: [{ crop_id: 'mustard' }] },
    baseline: { state: 'sequence', segments: [{ kind: 'crop', crop_id: 'rice' }, { kind: 'fallow' }] },
    irrigation: { access: 'limited' },
    priority: 'balanced'
  }, 'en');
  assert.match(html, /bogura/i);
  assert.match(html, /Mustard/);
  assert.match(html, /Rice → fallow/);
  assert.match(html, /District weather grid/i);
  assert.match(html, /Inputs Validated/i);
});

test('climate and current-crop requests do not cancel a pending planning request', async () => {
  const pending = new Map();
  const adapter = testAdapter({ endpoints: { planning: '/plan', climate: '/climate' }, fetchImpl: (url, options) => new Promise(resolve => pending.set(url, { resolve, signal: options.signal })) });
  const planning = adapter.requestPlanning({ request_id: 'same-field' });
  const climate = adapter.requestClimate({ request_id: 'same-field' });
  assert.equal(pending.get('/plan').signal.aborted, false);
  pending.get('/climate').resolve({ ok: true, json: async () => ({ status: 'incomplete', series: [] }) });
  pending.get('/plan').resolve({ ok: true, json: async () => ({ status: 'incomplete', alternatives: [] }) });
  assert.equal((await climate).state, 'incomplete');
  assert.equal((await planning).state, 'incomplete');
});

test('a newer same-kind request invalidates only the prior request', async () => {
  const pending = [];
  const adapter = testAdapter({ endpoints: { climate: '/climate' }, fetchImpl: () => new Promise(resolve => pending.push(resolve)) });
  const old = adapter.requestClimate({ location: 'old' });
  const latest = adapter.requestClimate({ location: 'new' });
  pending[0]({ ok: true, json: async () => ({ status: 'complete' }) });
  pending[1]({ ok: true, json: async () => ({ status: 'complete' }) });
  assert.equal((await old).state, 'stale');
  assert.equal((await latest).state, 'complete');
});

test('genuine submission can render an actual response without fixture labels', async () => {
  const example = fixtures.fixture('complete-comparison');
  const response = structuredClone(example.response);
  response.data_mode = 'cache';
  response.result_fingerprint = 'supplied-result-identity';
  const adapter = testAdapter({ endpoints: { planning: '/plan' }, fetchImpl: async () => ({ ok: true, json: async () => response }) });
  let renders = 0;
  const ui = uiApi.create({ adapter, render: () => renders++, navigate: () => {}, toast: () => {} });
  await ui.submit(example.request);
  const html = ui.renderGenuine(example.request);
  assert.equal(ui.isFixture(), false);
  assert.ok(renders >= 2);
  assert.match(html, /Three positions/);
  assert.match(html, /Download result JSON/);
  assert.match(html, /supplied-result-identity/);
  assert.doesNotMatch(html, /DEVELOPMENT FIXTURE|No real API or climate package loaded|Example data/);
  const exported = uiApi.receipt(ui.getData());
  assert.equal(exported.fixture, false);
  assert.deepEqual(exported.request, example.request);
  assert.deepEqual(exported.response, response);
});

test('failed genuine service remains unavailable and does not open a fixture', async () => {
  const adapter = testAdapter({ endpoints: { planning: '/plan' }, fetchImpl: async () => { throw new Error('connection refused'); } });
  const ui = uiApi.create({ adapter, render: () => {}, navigate: () => {}, toast: () => {} });
  const request = fixtures.fixture('complete-comparison').request;
  await ui.submit(request);
  assert.equal(ui.isFixture(), false);
  assert.equal(ui.getData().state, 'error');
  assert.match(ui.renderGenuine(request), /Service request failed/);
  assert.doesNotMatch(ui.renderGenuine(request), /Three positions|DEVELOPMENT FIXTURE/);
});

test('invalidation prevents a late response from restoring an old field', async () => {
  let resolve;
  const adapter = testAdapter({ endpoints: { planning: '/plan' }, fetchImpl: () => new Promise(done => { resolve = done; }) });
  const ui = uiApi.create({ adapter, render: () => {}, navigate: () => {}, toast: () => {} });
  const request = fixtures.fixture('complete-comparison').request;
  const pending = ui.submit(request);
  ui.invalidate();
  resolve({ ok: true, json: async () => ({ status: 'incomplete' }) });
  await pending;
  assert.equal(ui.getData(), null);
});

test('genuine endpoint cannot promote development fixtures or incomplete plan shapes', async () => {
  for (const body of [fixtures.fixture('complete-comparison').response, { status: 'complete', alternatives: [] }, null]) {
    const adapter = testAdapter({ endpoints: { planning: '/plan' }, fetchImpl: async () => ({ ok: true, json: async () => body }) });
    assert.equal((await adapter.requestPlanning({})).state, 'error');
  }
});

test('chart uses supplied dates and splits gaps without treating null as zero', () => {
  const html = uiApi.chart({ label: 'Rainfall', unit: 'mm', dates: ['2001-01', '2001-02', '2001-03'], values: [0, null, 12] });
  assert.match(html, /2001-01/);
  assert.match(html, /Missing/);
  assert.equal((html.match(/<circle /g) || []).length, 2);
  assert.match(html, /d="M[^L]*M/);
  assert.doesNotMatch(html, /NaN|Infinity/);
});

test('chart handles empty, constant, singleton and longer series without leaving the viewport', () => {
  assert.match(uiApi.chart({ values: [] }), /No usable observations/);
  for (const values of [[0], [4, 4, 4], Array.from({ length: 25 }, (_, i) => i)]) {
    const html = uiApi.chart({ label: 'Data', unit: 'C', values });
    assert.doesNotMatch(html, /NaN|Infinity|undefined/);
    for (const [, x] of html.matchAll(/cx="([\d.]+)"/g)) assert.ok(Number(x) <= 570);
  }
});

test('zero indicators and supplied stage/period survive presentation', () => {
  assert.match(uiApi.indicatorRows({ indicators: [{ label: 'Exposure days', value: 0, status: 'complete' }] }), />0</);
  const html = uiApi.vulnerability({ status: 'complete', stage: 'flowering', assessment_period: { start: '2020-01-01', end: '2020-01-20' }, checks: [] }, 'en');
  assert.match(html, /Flowering/);
  assert.match(html, /2020-01-01 → 2020-01-20/);
  assert.doesNotMatch(html, /\[object Object\]/);
});

test('malformed dates and empty climate payloads remain readable', () => {
  assert.equal(uiApi.formatDate('not-a-date'), 'Not supplied');
  assert.equal(uiApi.formatDate('2027-02-30'), 'Not supplied');
  assert.match(uiApi.climatePanel({ status: 'complete', series: [] }, 'en'), /Historical climate unavailable/);
});


test('field evidence cards show only applicable BAMIS comparisons and explain gaps', async () => {
  const example = fixtures.fixture('complete-comparison');
  const response = structuredClone(example.response);
  response.status = 'incomplete';
  response.data_mode = 'local_evidence';
  response.checks = [
    { check_id: 'heat-rule', outcome: 'unknown', label: { en: 'Heat compatibility not scored' } },
    { check_id: 'water-rule', outcome: 'unknown', label: { en: 'Water compatibility not scored' } },
    { check_id: 'rotation', outcome: 'unknown', label: { en: 'Rotation compatibility not scored' } },
    { check_id: 'operations', outcome: 'unknown', source_ids: ['bamis-example-page'], label: { en: 'Crop timing is not yet executable' } },
  ];
  response.current_crop_assessment.checks = response.checks.slice(0, 2);
  const reference = { id: 'bamis-chattogram-rabi-chilli-rain-p1', source_url: 'https://www.bamis.gov.bd/', section: 'Weather Warning', page: 1, limitations: [] };
  const hot = { id: 'hot-day', parameter: 'T2M_MAX', label: 'Daily maximum above 30°C', status: 'complete', matching_days: 0, dates: [], valid_days: 2, expected_days: 2 };
  const cold = { id: 'cold-night', parameter: 'T2M_MIN', label: 'Daily minimum below 10°C', status: 'incomplete', matching_days: null, dates: [], valid_days: 1, expected_days: 2 };
  const rain = { parameter: 'PRECTOTCORR', label: 'Daily rainfall within 10–15 mm', status: 'complete', matching_days: 1, dates: ['2025-01-01'], valid_days: 2, expected_days: 2 };
  const adapter = testAdapter({ endpoints: { planning: '/plan' }, fetchImpl: async () => ({ ok: true, json: async () => response }) });
  const ui = uiApi.create({ adapter, render() {}, navigate() {}, toast() {} });
  async function renderEvidence(exposure, language = 'en') {
    response.current_crop_assessment.observed_warning_exposure = exposure;
    await ui.submit(example.request);
    return ui.renderGenuine(example.request, language).split('id="evidence-title"')[1];
  }
  const exposure = { start: '2025-01-01', end: '2025-01-02', status: 'incomplete', reference };
  let html = await renderEvidence({ ...exposure, indicators: [hot, cold, rain] });
  assert.match(html, /Incomplete Observations.*Heat and cold checks/);
  assert.match(html, />0 days</);
  assert.match(html, /1\/2 days with data/);
  assert.match(html, /Weather Compared.*Rain and water checks/);
  assert.match(html, /1 Jan 2025 → 2 Jan 2025 · NASA POWER/);
  assert.match(html, /BAMIS · Weather Warning · page 1/);
  assert.match(html, /Which crop should follow\?/);
  assert.match(html, /When can I plant and harvest\?/);
  assert.match(html, /<summary>Source IDs<\/summary><p>bamis-example-page<\/p>/);
  assert.doesNotMatch(html, /Source unavailable|not yet executable|Rotation compatibility not scored/);
  assert.match(html, />1 day</);
  assert.doesNotMatch(html, />1 days</);
  assert.match(html, /without assuming your chilli was at one of those stages/);

  html = await renderEvidence({ ...exposure, status: 'complete', indicators: [rain] });
  assert.match(html, /Comparison Unavailable.*Heat and cold checks/);
  assert.match(html, /does not specify a temperature warning that can be matched to daily NASA data/);
  assert.doesNotMatch(html, /Daily maximum above 30°C/);
  assert.match(html, /Weather Compared.*Rain and water checks/);

  const occupancy = {status: 'available', start: exposure.start, end: exposure.end, latest_observed: exposure.end, metrics: {
    T2M_MAX: {status: 'complete', value: 33.6, unit: 'degC'},
    T2M_MIN: {status: 'unknown', value: null, unit: 'degC'},
    PRECTOTCORR: {status: 'complete', value: 0, unit: 'mm'},
  }};
  response.climate.reported_occupancy_window = occupancy;
  html = await renderEvidence({ ...exposure, status: 'complete', indicators: [rain] });
  assert.match(html, /Weather Recorded.*Heat and cold checks/);
  assert.match(html, /Hottest daily high<\/small><b>33\.6 °C/);
  assert.doesNotMatch(html, /Coldest daily low/);
  assert.match(html, /does not specify a temperature warning/);
  assert.match(html, /Weather Compared.*Rain and water checks/);
  html = await renderEvidence({ status: 'unavailable', reason: 'no_source_verified_warning_reference_for_this_crop_and_source_region' });
  assert.match(html, /Total rain<\/small><b>0 mm/);
  assert.doesNotMatch(html, /Weather Compared/);
  response.climate.reported_occupancy_window = {status: 'unavailable'};

  html = await renderEvidence({ status: 'unavailable', reason: 'crop_window_has_no_cached_observations; future_weather_not_predicted' });
  assert.match(html, /archive has no observations for the crop dates you entered/);
  assert.doesNotMatch(html, /Weather Compared|>0 days</);

  html = await renderEvidence({ ...exposure, status: 'complete', indicators: [hot] }, 'bn');
  assert.match(html, /দিনের সর্বোচ্চ তাপমাত্রা ৩০°সে-এর বেশি/);

  response.current_crop_assessment.status = 'not_applicable';
  html = await renderEvidence({ status: 'unavailable', reason: 'no_current_crop' });
  assert.doesNotMatch(html, /Heat and cold checks|Rain and water checks/);
});
