(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.STS_RESULT_FIXTURES = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const source = {
    source_id: 'synthetic-power-shape',
    provider: 'NASA POWER (shape reference only)',
    product_version: 'synthetic-development-fixture',
    url: 'https://power.larc.nasa.gov/docs/services/api/temporal/daily/',
    period: '2001–2025',
    spatial_support: 'Synthetic regional-context example; not a farm measurement or district average',
    qa: 'Values below are authored UI-test data, not observations',
    limitations: ['No scientific payload was loaded from the local climate package.']
  };

  const labels = {
    rice: { en: 'Rice', bn: 'ধান' }, mustard: { en: 'Mustard', bn: 'সরিষা' },
    mungbean: { en: 'Mungbean', bn: 'মুগ' }, maize: { en: 'Maize', bn: 'ভুট্টা' },
    lentil: { en: 'Lentil', bn: 'মসুর' }, sesame: { en: 'Sesame', bn: 'তিল' },
    fallow: { en: 'Fallow', bn: 'পতিত' }
  };

  function operation(type, start, end, certainty, detail) {
    return { type, start_window: { earliest: start, latest: end }, certainty, detail };
  }

  function step(id, cropId, start, sowEnd, matureStart, harvestEnd, clearEnd) {
    return {
      step_id: id, crop_id: cropId, crop_label: labels[cropId], status: 'complete',
      operations: [
        operation('preparation', start, start, 'example', 'Preparation window supplied by the fixture.'),
        operation('sowing', start, sowEnd, 'example', 'Sowing or transplanting window.'),
        operation('growth', sowEnd, matureStart, 'example', 'Growth period; crop stages require sourced rules.'),
        operation('maturity', matureStart, matureStart, 'example', 'Maturity is distinct from final harvest.'),
        operation('harvest', matureStart, harvestEnd, 'example', 'Harvest window.'),
        operation('clearance', harvestEnd, clearEnd, 'example', 'Collection/removal and field clearance.'),
        operation('transition', clearEnd, clearEnd, 'example', 'Transition boundary; no arbitrary gap added.')
      ],
      maturity_window: { earliest: matureStart, latest: matureStart },
      final_harvest_window: { earliest: matureStart, latest: harvestEnd },
      field_clearance_window: { earliest: harvestEnd, latest: clearEnd }
    };
  }

  const indicators = [
    ['historical_climate_fit', 'Historical climate fit', 'supported', 'Example category only; no suitability calculation was performed.'],
    ['water_compatibility', 'Water compatibility', 'caution', 'Limited irrigation needs a reviewed crop-stage rule.'],
    ['rotation_compatibility', 'Rotation compatibility', 'supported', 'Example sequence check; not agronomic approval.'],
    ['timing_feasibility', 'Timing feasibility', 'supported', 'Example windows fit the fixture horizon.']
  ].map(([key, label, value, explanation]) => ({ key, label, status: value === 'supported' ? 'complete' : 'incomplete', value, unit: 'category', explanation }));

  const baseline = {
    plan_id: 'baseline-example', role: 'baseline', label: { en: 'Your usual practice', bn: 'আপনার সাধারণ চাষপদ্ধতি' },
    status: 'complete', feasibility: 'infeasible', completion_date: '2027-09-20',
    segments: [
      { kind: 'crop', crop_id: 'rice', label: labels.rice, period: '2026-11–2027-03' },
      { kind: 'fallow', crop_id: null, label: labels.fallow, period: '2027-04–2027-05' },
      { kind: 'crop', crop_id: 'rice', label: labels.rice, period: '2027-06–2027-09' }
    ],
    indicators: indicators.map((item, index) => index === 2 ? { ...item, status: 'incomplete', value: 'conflict', explanation: 'The synthetic baseline carries a repeated-family conflict for layout testing.' } : item),
    reason_ids: ['synthetic-repeat-conflict'], unallocated_intervals: []
  };

  const alternativeA = {
    plan_id: 'alternative-a-example', role: 'alternative', label: { en: 'Alternative A', bn: 'বিকল্প A' },
    status: 'complete', feasibility: 'feasible', completion_date: '2027-09-12', rank: null,
    steps: [
      step('a-1', 'mustard', '2026-11-20', '2026-11-28', '2027-02-10', '2027-02-18', '2027-02-22'),
      step('a-2', 'mungbean', '2027-02-23', '2027-03-03', '2027-05-22', '2027-05-28', '2027-06-01'),
      step('a-3', 'rice', '2027-06-02', '2027-06-12', '2027-08-28', '2027-09-08', '2027-09-12')
    ],
    indicators, reason_ids: ['synthetic-timing-supported', 'synthetic-water-caution'],
    unallocated_intervals: [{ start: '2027-09-13', end: '2027-09-30', classification: 'unallocated' }]
  };

  const alternativeB = {
    plan_id: 'alternative-b-example', role: 'alternative', label: { en: 'Alternative B', bn: 'বিকল্প B' },
    status: 'complete', feasibility: 'feasible', completion_date: '2027-09-24', rank: null,
    steps: [
      step('b-1', 'lentil', '2026-11-20', '2026-11-30', '2027-02-14', '2027-02-21', '2027-02-25'),
      step('b-2', 'sesame', '2027-02-26', '2027-03-06', '2027-05-30', '2027-06-05', '2027-06-09'),
      step('b-3', 'maize', '2027-06-10', '2027-06-18', '2027-09-05', '2027-09-18', '2027-09-24')
    ],
    indicators: indicators.map((item, index) => index === 1 ? { ...item, value: 'unknown', status: 'incomplete', explanation: 'Example water requirement is deliberately unresolved.' } : item),
    reason_ids: ['synthetic-water-unknown'], unallocated_intervals: []
  };

  const checks = [
    { check_id: 'check-calendar-a', outcome: 'pass', label: { en: 'Example calendar window aligns', bn: 'নমুনা ক্যালেন্ডারের সময় মেলে' }, crop_id: 'mustard', stage: 'sowing', period: '2026-11-20–2026-11-28', rule_id: 'synthetic-calendar-rule', source_ids: ['synthetic-calendar-source'], evidence_ids: ['synthetic-calendar-evidence'], limitation: 'Shape-only fixture; no reviewed crop rule.' },
    { check_id: 'check-water-a', outcome: 'caution', label: { en: 'Water detail needs review', bn: 'পানির তথ্য পর্যালোচনা প্রয়োজন' }, crop_id: 'rice', stage: 'growth', period: '2027-06–2027-09', rule_id: 'synthetic-water-rule', source_ids: ['synthetic-rule-source'], evidence_ids: [], missing_information: 'Stage-specific water requirement and seasonal availability.' },
    { check_id: 'check-soil-a', outcome: 'unknown', label: { en: 'Essential soil condition not reported', bn: 'প্রয়োজনীয় মাটির তথ্য দেওয়া হয়নি' }, crop_id: 'lentil', stage: null, period: null, rule_id: 'synthetic-soil-rule', source_ids: ['synthetic-rule-source'], evidence_ids: [], missing_information: 'A reviewed field observation relevant to this rule.' },
    { check_id: 'check-repeat-baseline', outcome: 'fail', label: { en: 'Example repeated-family conflict', bn: 'নমুনা একই গোত্রের পুনরাবৃত্তির দ্বন্দ্ব' }, crop_id: 'rice', stage: 'sequence', period: 'comparison horizon', rule_id: 'synthetic-repeat-rule', source_ids: ['synthetic-rule-source'], evidence_ids: ['synthetic-rule-evidence'], limitation: 'Used only to test an assessed infeasible baseline.' }
  ];

  const climate = {
    status: 'complete', data_class: 'development_fixture', metric: 'monthly', time_standard: 'LST',
    location_label: 'Synthetic regional context (not district coverage)',
    period: { start: '2001-01-01', end: '2025-12-31' }, missingness: '0 values in this 12-point authored example',
    series: [
      { key: 'precipitation', label: 'Monthly rainfall total', unit: 'mm/month', statistic: 'sum of authored daily-rate examples', values: [8, 16, 41, 102, 188, 312, 346, 301, 249, 136, 38, 12] },
      { key: 'temperature', label: 'Monthly mean daily maximum temperature', unit: '°C', statistic: 'mean of authored daily maxima; not the absolute monthly maximum', values: [25.2, 28.1, 32.4, 35.3, 34.7, 33.1, 32.5, 32.2, 32.0, 30.8, 28.4, 25.7] }
    ],
    comparison: { earlier: '2001–2012', recent: '2013–2025', finding: 'No reviewed shift finding is supplied by this fixture.', statistics: [] },
    sources: [source], limitations: source.limitations
  };

  const input = {
    schema_version: 'farmer-intake.example-01', fixture: true,
    location: { district_id: 'bd-district-example', district_label: { en: 'Example district selection', bn: 'নমুনা জেলা নির্বাচন' }, selection_method: 'district_search', coordinates: null },
    current: { state: 'growing', crop_id: 'rice', label: labels.rice, sown_on: null },
    availability: { kind: 'window', start: '2026-11-15', end: '2026-11-20', basis: 'farmer_estimate' },
    crop_history: { state: 'entries', summary: { en: 'Rice · previous season', bn: 'ধান · আগের মৌসুম' } },
    baseline: { state: 'sequence', summary: { en: 'Rice → fallow → rice (example)', bn: 'ধান → পতিত → ধান (নমুনা)' } },
    irrigation: { access: 'limited', seasonal_limitations: 'seasonal' }, priority: 'balanced'
  };

  const currentCrop = {
    status: 'incomplete', crop_id: 'rice', crop_label: labels.rice, planting_date: null, stage: null,
    assessment_period: 'Not established', evidence_used: [],
    checks: [
      { outcome: 'unknown', label: { en: 'Heat exposure not assessed', bn: 'তাপের প্রভাব মূল্যায়ন করা হয়নি' }, missing_information: 'Planting/transplanting date, stage rule and reviewed temperature requirement.' },
      { outcome: 'unknown', label: { en: 'Rainfall and water exposure not assessed', bn: 'বৃষ্টি ও পানির প্রভাব মূল্যায়ন করা হয়নি' }, missing_information: 'Crop stage, assessment period and reviewed water rule.' }
    ],
    limitation: 'Historical exposure only when supported; no live monitoring, diagnosis or forecast.'
  };

  const intendedCrop = {
    status: 'unavailable', proposed_crop_id: null, planting_period: null, checks: [],
    reason: 'No same-engine intended-crop endpoint is connected. Fixture UI accepts an example selection but does not score it.'
  };
  const replay = {
    status: 'unavailable', scenario_id: null, periods: null, changed_checks: [],
    reason: 'No reviewed historical replay payload is connected; chart values are not modified in the browser.'
  };

  const base = {
    fixture_id: 'complete-comparison', fixture_label: 'DEVELOPMENT FIXTURE · NOT SCIENTIFIC ADVICE',
    fixture_description: 'Authored values test layout, states, exports and accessibility. They are not NASA observations or crop recommendations.',
    request: input,
    response: {
      schema_version: 'rotation-comparison.ui-fixture-01', status: 'complete', data_mode: 'development_fixture',
      generated_at: '2026-11-13T00:00:00Z', input_fingerprint: null, result_fingerprint: null,
      coverage: { status: 'unavailable', label: 'Synthetic UI coverage only', reason_ids: ['development_fixture'] },
      comparison_period: { status: 'complete', start: '2026-11-20', end: '2027-09-30', policy_id: 'synthetic-period-policy', policy_version: 'shape-only', explanation: 'Example common horizon for layout testing only.' },
      current_crop_assessment: currentCrop, baseline_assessment: baseline,
      alternatives: [alternativeA, alternativeB], checks, climate,
      intended_crop_assessment: intendedCrop, historical_replay: replay,
      ranking: { status: 'unavailable', selected_plan_id: null },
      versions: { contract: 'ui-fixture-01', catalogue: 'synthetic', method: 'synthetic' },
      sources: [source], limitations: ['Development fixture only.', 'No backend, reviewed crop rules or scientific recommendation is connected.']
    }
  };

  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function fixture(id) {
    const value = clone(base);
    value.fixture_id = id;
    if (id === 'incomplete-one-alternative') {
      value.response.status = 'incomplete';
      value.response.alternatives = [value.response.alternatives[0]];
      value.response.limitations.unshift('A second distinct supported alternative is missing; no filler plan is shown.');
    } else if (id === 'missing-climate') {
      value.response.status = 'incomplete';
      value.response.climate = { status: 'unavailable', data_class: 'development_fixture', reason: 'Climate payload intentionally omitted for state testing.', sources: [], limitations: ['No values loaded.'] };
    } else if (id === 'invalid-input') {
      value.response = { schema_version: 'rotation-comparison.ui-fixture-01', status: 'invalid_input', data_mode: 'development_fixture', errors: [{ input_path: '/availability', reason_id: 'example_invalid_window', label: 'Example invalid availability window.' }], limitations: ['Development fixture only.'] };
    } else if (id === 'service-unavailable') {
      value.response = { schema_version: 'rotation-comparison.ui-fixture-01', status: 'unavailable', data_mode: 'development_fixture', reason: 'Example service/evidence unavailable state.', limitations: ['No successful result fallback was opened.'] };
    } else if (id === 'recoverable-error') {
      value.response = { schema_version: 'rotation-comparison.ui-fixture-01', status: 'error', recoverable: true, data_mode: 'development_fixture', reason: 'Example recoverable transport error. Inputs remain preserved.', limitations: ['Retry never activates a successful fixture automatically.'] };
    }
    return value;
  }

  const ids = ['complete-comparison', 'incomplete-one-alternative', 'missing-climate', 'invalid-input', 'service-unavailable', 'recoverable-error'];
  return { ids, fixture, labels };
});
