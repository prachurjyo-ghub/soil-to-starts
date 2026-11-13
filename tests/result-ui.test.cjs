const test = require('node:test');
const assert = require('node:assert/strict');

const fixtures = require('../prototype/public/reference/result-fixtures.js');
const adapterApi = require('../prototype/public/reference/result-adapter.js');
const uiApi = require('../prototype/public/reference/result-ui.js');

test('fixture mode requires an explicit action', () => {
  const adapter = adapterApi.create({ fetchImpl: null });
  assert.throws(() => adapter.enableFixture('complete-comparison'), /explicit user action/);
  assert.throws(() => adapter.enableFixture('missing-fixture', true), /Unknown fixture/);
});

test('genuine planning request stays unavailable without an endpoint', async () => {
  const adapter = adapterApi.create({ fetchImpl: null });
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
  const adapter = adapterApi.create({ fetchImpl: null });
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
  const adapter = adapterApi.create({ fetchImpl, endpoints: { planning: '/api/planning' } });
  const pending = adapter.requestPlanning({ request_id: 'old' });
  adapter.invalidate();
  resolveFetch({ ok: true, status: 200, json: async () => ({ status: 'complete' }) });
  const result = await pending;
  assert.equal(result.state, 'stale');
  assert.equal(result.ignored, true);
});
