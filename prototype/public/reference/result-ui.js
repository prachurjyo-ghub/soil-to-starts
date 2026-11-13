(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.STS_RESULT_UI = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const esc = value => String(value ?? '').replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
  const text = (value, language = 'en') => typeof value === 'object' && value ? (value[language] || value.en || '') : String(value ?? '');
  const human = value => String(value || '').replaceAll('_', ' ').replace(/\b\w/g, character => character.toUpperCase());
  const formatDate = value => value ? new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${value}T00:00:00Z`)) : 'Not supplied';
  const planHasThreeSteps = plan => plan?.status === 'complete' && Array.isArray(plan.steps) && plan.steps.length === 3;

  function receipt(fixture) {
    return {
      receipt_type: fixture ? 'development_fixture_example' : 'scientific_result',
      fixture: Boolean(fixture),
      warning: fixture ? 'Example export. Not scientific advice or NASA observations.' : undefined,
      request: fixture?.request || null,
      response: fixture?.response || null
    };
  }

  function badge(status, label = status) {
    return `<span class="result-badge result-badge--${esc(status || 'unknown')}">${esc(human(label || 'unknown'))}</span>`;
  }

  function unavailableCard(title, reason, action = '') {
    return `<section class="result-card result-empty" aria-labelledby="result-empty-title"><span class="result-empty__icon" aria-hidden="true">◎</span><div><p class="result-eyebrow">RESULT STATUS</p><h2 id="result-empty-title">${esc(title)}</h2><p>${esc(reason)}</p>${action}</div></section>`;
  }

  function genuineSummary(request) {
    if (!request) return unavailableCard('No submitted field yet', 'Complete the six field questions before requesting a result.', '<button type="button" class="primary" data-result-action="edit-inputs">Set up field</button>');
    const location = request.location || {};
    const current = request.current || {};
    const availability = request.availability || {};
    return `<section class="result-card result-field-summary" aria-labelledby="field-summary-title">
      <div class="result-section-heading"><div><p class="result-eyebrow">01 · FIELD SUMMARY</p><h2 id="field-summary-title">Your submitted field</h2></div>${badge('unavailable', 'Planning unavailable')}</div>
      <div class="result-summary-grid">
        <div><small>District and method</small><b>${esc(location.district_id || 'Not supplied')}</b><span>${esc(human(location.selection_method || 'unknown'))}</span></div>
        <div><small>Current crop</small><b>${esc(current.state === 'fallow' ? 'Fallow' : current.crop_id || 'Not supplied')}</b><span>${current.sown_on ? `Reported planting: ${esc(formatDate(current.sown_on))}` : 'Planting date not supplied'}</span></div>
        <div><small>Field available</small><b>${esc(formatDate(availability.start))}${availability.kind === 'window' ? ` – ${esc(formatDate(availability.end))}` : ''}</b><span>${esc(human(availability.basis || 'unknown basis'))}</span></div>
        <div><small>Water and priority</small><b>${esc(human(request.irrigation?.access || 'not supplied'))}</b><span>${esc(human(request.priority || 'not supplied'))}</span></div>
      </div>
      <div class="result-actions"><button type="button" data-result-action="edit-inputs">Edit inputs</button><button type="button" data-result-action="download-inputs">Download input JSON</button></div>
    </section>`;
  }

  function fieldSummary(data, language) {
    const request = data.request;
    const response = data.response;
    return `<section class="result-card result-field-summary" aria-labelledby="field-summary-title">
      <div class="result-section-heading"><div><p class="result-eyebrow">01 · ${language === 'bn' ? 'জমির সারাংশ' : 'FIELD SUMMARY'}</p><h2 id="field-summary-title">${language === 'bn' ? 'পরিকল্পনার প্রেক্ষাপট' : 'Planning context'}</h2></div>${badge(response.status, response.status)}</div>
      <div class="result-summary-grid">
        <div><small>${language === 'bn' ? 'জেলা ও পদ্ধতি' : 'District and method'}</small><b>${esc(text(request.location.district_label, language))}</b><span>${esc(human(request.location.selection_method))} · ${language === 'bn' ? 'বৈজ্ঞানিক কভারেজ নয়' : 'not scientific coverage'}</span></div>
        <div><small>${language === 'bn' ? 'বর্তমান ফসল' : 'Current crop'}</small><b>${esc(text(request.current.label, language))}</b><span>${request.current.sown_on ? esc(formatDate(request.current.sown_on)) : (language === 'bn' ? 'রোপণের তারিখ দেওয়া হয়নি' : 'Planting date not supplied')}</span></div>
        <div><small>${language === 'bn' ? 'জমি খালি হবে' : 'Field available'}</small><b>${esc(formatDate(request.availability.start))} – ${esc(formatDate(request.availability.end))}</b><span>${esc(human(request.availability.basis))}</span></div>
        <div><small>${language === 'bn' ? 'আগের ফসল' : 'History'}</small><b>${esc(text(request.crop_history.summary, language))}</b><span>${language === 'bn' ? 'কৃষকের দেওয়া নমুনা তথ্য' : 'Separate example input'}</span></div>
        <div><small>${language === 'bn' ? 'সাধারণ পরিকল্পনা' : 'Usual practice'}</small><b>${esc(text(request.baseline.summary, language))}</b><span>${language === 'bn' ? 'পর্যালোচনা করা হয়েছে, সুপারিশ নয়' : 'Assessed, not recommended'}</span></div>
        <div><small>${language === 'bn' ? 'পানি ও অগ্রাধিকার' : 'Water and priority'}</small><b>${esc(human(request.irrigation.access))}</b><span>${esc(human(request.priority))}</span></div>
      </div>
      <div class="result-freshness"><span>●</span><b>${language === 'bn' ? 'নমুনা ফলাফল' : 'Example result'}</b><span>${language === 'bn' ? 'কোনো বাস্তব API বা জলবায়ু প্যাকেজ লোড হয়নি' : 'No real API or climate package loaded'}</span></div>
      <div class="result-actions"><button type="button" data-result-action="edit-inputs">${language === 'bn' ? 'তথ্য সম্পাদনা' : 'Edit inputs'}</button></div>
    </section>`;
  }

  function vulnerability(assessment, language) {
    const checks = assessment?.checks || [];
    return `<section class="result-card" aria-labelledby="vulnerability-title">
      <div class="result-section-heading"><div><p class="result-eyebrow">02 · ${language === 'bn' ? 'বর্তমান ফসল' : 'CURRENT CROP'}</p><h2 id="vulnerability-title">${language === 'bn' ? 'ঐতিহাসিক প্রভাব মূল্যায়ন' : 'Historical exposure assessment'}</h2></div>${badge(assessment?.status || 'unavailable', assessment?.status === 'incomplete' ? (language === 'bn' ? 'মূল্যায়ন অসম্পূর্ণ' : 'Assessment incomplete') : assessment?.status)}</div>
      <div class="vulnerability-lead"><div class="crop-orbit" aria-hidden="true">◉</div><div><small>${language === 'bn' ? 'বর্তমান ফসল' : 'CROP IN THE FIELD'}</small><h3>${esc(text(assessment?.crop_label, language) || 'Not supplied')}</h3><p>${language === 'bn' ? 'পর্যায়: জানা নেই · মূল্যায়নের সময়: নির্ধারিত নয়' : 'Stage: unknown · Assessment period: not established'}</p></div></div>
      <div class="check-grid">${checks.map(check => `<article class="check-tile check-tile--${esc(check.outcome)}">${badge(check.outcome)}<h3>${esc(text(check.label, language))}</h3><p>${esc(check.missing_information || '')}</p></article>`).join('')}</div>
      <p class="result-limit"><b>${language === 'bn' ? 'সীমা:' : 'Limit:'}</b> ${esc(assessment?.limitation || 'Not assessed.')}</p>
    </section>`;
  }

  function indicatorCells(plan) {
    return (plan.indicators || []).map(item => `<div class="indicator-cell"><small>${esc(item.label)}</small>${badge(item.value || item.status)}<p>${esc(item.explanation || '')}</p>${item.unit ? `<span>${esc(item.unit)}</span>` : ''}</div>`).join('');
  }

  function planCrops(plan, language) {
    if (plan.role === 'baseline') return (plan.segments || []).map(item => `<li><b>${esc(text(item.label, language))}</b><span>${esc(item.period || '')}</span></li>`).join('');
    return (plan.steps || []).map((item, index) => `<li><span>${String(index + 1).padStart(2, '0')}</span><b>${esc(text(item.crop_label, language))}</b><small>${esc(item.field_clearance_window?.latest || '')}</small></li>`).join('');
  }

  function comparison(response, language, selectedPlan) {
    const plans = [response.baseline_assessment, ...(response.alternatives || [])].filter(Boolean);
    const missingSecond = (response.alternatives || []).length < 2;
    return `<section class="result-card result-comparison" aria-labelledby="comparison-title">
      <div class="result-section-heading"><div><p class="result-eyebrow">03 · ${language === 'bn' ? 'পরিকল্পনা তুলনা' : 'PLAN COMPARISON'}</p><h2 id="comparison-title">${language === 'bn' ? 'একই সময়সীমায় তিনটি কৌশল' : 'Three positions on one shared horizon'}</h2><p>${esc(response.comparison_period?.start || '')} → ${esc(response.comparison_period?.end || '')} · ${esc(response.comparison_period?.explanation || '')}</p></div>${badge(response.status, response.status)}</div>
      <div class="plan-comparison-grid">${plans.map(plan => `<article class="plan-card ${plan.plan_id === selectedPlan ? 'is-selected' : ''}">
        <div class="plan-card__head"><div><small>${esc(plan.role === 'baseline' ? (language === 'bn' ? 'মূল পরিকল্পনা' : 'BASELINE') : (language === 'bn' ? 'ভবিষ্যৎ বিকল্প' : 'FUTURE ALTERNATIVE'))}</small><h3>${esc(text(plan.label, language))}</h3></div>${badge(plan.feasibility, plan.feasibility)}</div>
        <ul class="plan-crops">${planCrops(plan, language)}</ul>
        <div class="plan-meta"><span>${language === 'bn' ? 'শেষ' : 'Completes'} <b>${esc(plan.completion_date || 'Unknown')}</b></span><span>${plan.role === 'baseline' ? (language === 'bn' ? 'নমনীয় অংশ' : 'Flexible segments') : `${(plan.steps || []).length}/3 ${language === 'bn' ? 'ধাপ' : 'future steps'}`}</span></div>
        <div class="indicator-grid">${indicatorCells(plan)}</div>
        ${plan.role !== 'baseline' ? `<button type="button" data-result-plan="${esc(plan.plan_id)}" aria-pressed="${plan.plan_id === selectedPlan}">${language === 'bn' ? 'টাইমলাইন দেখুন' : 'View operations timeline'}</button>` : ''}
      </article>`).join('')}${missingSecond ? `<article class="plan-card plan-card--missing"><span aria-hidden="true">＋</span><h3>${language === 'bn' ? 'দ্বিতীয় বিকল্প অনুপলব্ধ' : 'Second alternative unavailable'}</h3><p>${language === 'bn' ? 'সমর্থিত পৃথক পরিকল্পনা না থাকায় কোনো নকল পরিকল্পনা যোগ করা হয়নি।' : 'No distinct supported plan was supplied, so no filler or clone is shown.'}</p></article>` : ''}</div>
    </section>`;
  }

  function operationTimeline(plan, language) {
    if (!plan) return unavailableCard('Timeline unavailable', 'Select a complete alternative with operations.');
    const operations = (plan.steps || []).flatMap(step => (step.operations || []).map(operation => ({ ...operation, crop: text(step.crop_label, language), step: step.step_id })));
    return `<section class="result-card" aria-labelledby="timeline-title">
      <div class="result-section-heading"><div><p class="result-eyebrow">04 · ${language === 'bn' ? 'সময়ের ধাপ' : 'OPERATIONS TIMELINE'}</p><h2 id="timeline-title">${esc(text(plan.label, language))}</h2><p>${language === 'bn' ? 'পরিপক্বতা, ফসল তোলা ও জমি খালি হওয়া আলাদা রাখা হয়েছে।' : 'Maturity, harvest and field clearance remain distinct.'}</p></div>${badge(plan.status)}</div>
      <div class="operations-track" role="img" aria-label="Example chronological operations timeline">${(plan.steps || []).map((step, index) => `<article><span class="operations-track__number">${index + 1}</span><h3>${esc(text(step.crop_label, language))}</h3><div class="operations-track__bar">${(step.operations || []).map(operation => `<span title="${esc(`${human(operation.type)}: ${operation.start_window.earliest} to ${operation.start_window.latest}`)}" class="operation operation--${esc(operation.type)}"></span>`).join('')}</div><small>${esc(step.operations?.[0]?.start_window?.earliest || '')} → ${esc(step.field_clearance_window?.latest || '')}</small></article>`).join('')}</div>
      <details class="timeline-table"><summary>${language === 'bn' ? 'টেক্সট/টেবিল দেখুন' : 'Accessible text and table view'}</summary><div class="table-scroll"><table><thead><tr><th>Crop</th><th>Operation</th><th>Earliest</th><th>Latest</th><th>Note</th></tr></thead><tbody>${operations.map(item => `<tr><td>${esc(item.crop)}</td><td>${esc(human(item.type))}</td><td>${esc(item.start_window.earliest)}</td><td>${esc(item.start_window.latest)}</td><td>${esc(item.detail || '')}</td></tr>`).join('')}</tbody></table></div></details>
      ${(plan.unallocated_intervals || []).map(item => `<p class="result-limit"><b>Unallocated:</b> ${esc(item.start)} → ${esc(item.end)}. No land-cover meaning is inferred.</p>`).join('')}
    </section>`;
  }

  function chart(series) {
    const values = series.values || [];
    const min = Math.min(...values), max = Math.max(...values), range = max - min || 1;
    const points = values.map((value, index) => `${34 + index * 48},${150 - ((value - min) / range) * 112}`).join(' ');
    return `<svg class="result-chart" viewBox="0 0 600 190" role="img" aria-label="${esc(series.label)} example chart"><title>${esc(series.label)} · ${esc(series.unit)} · development fixture</title>${[38, 75, 112, 150].map(y => `<line x1="34" x2="570" y1="${y}" y2="${y}"/>`).join('')}<polyline points="${points}"/>${values.map((value, index) => `<circle tabindex="0" cx="${34 + index * 48}" cy="${150 - ((value - min) / range) * 112}" r="4"><title>${index + 1}: ${value} ${esc(series.unit)}</title></circle>`).join('')}</svg>`;
  }

  function climatePanel(climate, language, metric) {
    if (!climate || climate.status !== 'complete') return `<section aria-labelledby="climate-title"><p class="result-eyebrow">05 · CLIMATE HISTORY</p>${unavailableCard('Historical climate unavailable', climate?.reason || 'No prepared chart/history payload was supplied.')}</section>`;
    const selected = climate.series.find(series => series.key === metric) || climate.series[0];
    return `<section class="result-card" aria-labelledby="climate-title">
      <div class="result-section-heading"><div><p class="result-eyebrow">05 · ${language === 'bn' ? 'ঐতিহাসিক আবহাওয়া' : 'HISTORICAL WEATHER'}</p><h2 id="climate-title">${language === 'bn' ? 'আঞ্চলিক প্রেক্ষাপট, জমির মাপ নয়' : 'Regional context, not a field measurement'}</h2><p>${esc(climate.period.start)} → ${esc(climate.period.end)} · ${esc(climate.time_standard)} · ${esc(climate.missingness)}</p></div>${badge('fixture', 'Example data')}</div>
      <div class="chart-tabs" role="group" aria-label="Climate metric">${climate.series.map(series => `<button type="button" data-result-metric="${esc(series.key)}" aria-pressed="${series.key === selected.key}">${esc(series.key === 'precipitation' ? (language === 'bn' ? 'বৃষ্টিপাত' : 'Rainfall') : (language === 'bn' ? 'তাপমাত্রা' : 'Temperature'))}</button>`).join('')}</div>
      <div class="chart-header"><div><small>${esc(selected.statistic)}</small><h3>${esc(selected.label)}</h3></div><b>${esc(selected.unit)}</b></div>${chart(selected)}
      <div class="chart-months" aria-hidden="true">${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].map(month => `<span>${month}</span>`).join('')}</div>
      <div class="weather-shift"><div><small>Earlier period</small><b>${esc(climate.comparison.earlier)}</b></div><span aria-hidden="true">→</span><div><small>Recent period</small><b>${esc(climate.comparison.recent)}</b></div><p>${esc(climate.comparison.finding)}</p></div>
      <p class="result-limit"><b>Important:</b> Monthly mean daily maximum is not the absolute monthly maximum. District context is not a district-area average. ${esc(climate.limitations.join(' '))}</p>
    </section>`;
  }

  function evidencePanel(response, language) {
    return `<section class="result-card" aria-labelledby="evidence-title"><div class="result-section-heading"><div><p class="result-eyebrow">06 · ${language === 'bn' ? 'কারণ ও প্রমাণ' : 'REASONS & EVIDENCE'}</p><h2 id="evidence-title">${language === 'bn' ? 'কেন, কেন নয়, কী তথ্য দরকার' : 'Why, why not, and what is missing'}</h2></div></div>
      <div class="evidence-list">${(response.checks || []).map(check => `<article><div>${badge(check.outcome)}<h3>${esc(text(check.label, language))}</h3></div><dl><dt>Crop / stage</dt><dd>${esc(human(check.crop_id || 'not supplied'))} · ${esc(human(check.stage || 'not supplied'))}</dd><dt>Period</dt><dd>${esc(check.period || 'Not supplied')}</dd><dt>Rule</dt><dd><code>${esc(check.rule_id || 'Not supplied')}</code></dd><dt>Sources</dt><dd>${esc((check.source_ids || []).join(', ') || 'No source attached')}</dd><dt>Missing / limit</dt><dd>${esc(check.missing_information || check.limitation || 'None supplied')}</dd></dl></article>`).join('')}</div>
      <details class="source-drawer"><summary>${language === 'bn' ? 'উৎস ও পদ্ধতির বিবরণ' : 'Sources and methods drawer'}</summary>${(response.sources || []).map(source => `<article><h3>${esc(source.provider)}</h3><dl><dt>Dataset/version</dt><dd>${esc(source.product_version)}</dd><dt>Period</dt><dd>${esc(source.period)}</dd><dt>Spatial support</dt><dd>${esc(source.spatial_support)}</dd><dt>QA</dt><dd>${esc(source.qa)}</dd></dl><a href="${esc(source.url)}" target="_blank" rel="noopener">Official documentation ↗</a></article>`).join('')}<p><b>Versions:</b> contract ${esc(response.versions?.contract || 'unknown')} · catalogue ${esc(response.versions?.catalogue || 'unknown')} · method ${esc(response.versions?.method || 'unknown')}</p></details>
    </section>`;
  }

  function toolsPanel(response, language) {
    return `<section class="result-tools" aria-label="Intended crop and historical replay"><article class="result-card"><p class="result-eyebrow">07A · ${language === 'bn' ? 'প্রস্তাবিত ফসল যাচাই' : 'INTENDED-CROP CHECK'}</p><h2>${language === 'bn' ? 'একই নিয়মে ফসল যাচাই' : 'Check a crop with the same engine'}</h2><div class="result-form-row"><label>Crop<select id="intended-crop"><option value="">Choose crop</option><option value="mustard">Mustard</option><option value="mungbean">Mungbean</option><option value="rice">Rice</option></select></label><label>Planting date<input id="intended-date" type="date"></label></div><button type="button" data-result-action="intended-check">Check availability</button><p class="result-limit" id="intended-status">${esc(response.intended_crop_assessment?.reason || 'Unavailable')}</p></article>
      <article class="result-card"><p class="result-eyebrow">07B · ${language === 'bn' ? 'ঐতিহাসিক পুনরায় পরীক্ষা' : 'HISTORICAL REPLAY'}</p><h2>${language === 'bn' ? 'একই জমি, নথিভুক্ত সময়কাল' : 'Same field, documented historical period'}</h2><p>${esc(response.historical_replay?.reason || 'No replay payload supplied.')}</p><button type="button" data-result-action="replay" disabled>${language === 'bn' ? 'পুনরায় পরীক্ষা অনুপলব্ধ' : 'Replay unavailable'}</button><p class="result-limit">No browser-made drought multiplier or future-weather slider is used.</p></article></section>`;
  }

  function receiptPanel(data, language) {
    return `<section class="result-card result-receipt" aria-labelledby="receipt-title"><div><p class="result-eyebrow">08 · ${language === 'bn' ? 'প্রিন্ট ও JSON' : 'PRINT & JSON RECEIPT'}</p><h2 id="receipt-title">${language === 'bn' ? 'এই নমুনার একই তথ্য রাখুন' : 'Keep the same example result'}</h2><p>${language === 'bn' ? 'রপ্তানিতে নমুনা লেবেল, অবস্থা, সীমাবদ্ধতা ও উৎস থাকবে।' : 'The export preserves the fixture label, statuses, limitations and source metadata.'}</p></div><div class="result-actions"><button type="button" class="primary" data-result-action="download-receipt">${language === 'bn' ? 'নমুনা JSON ডাউনলোড' : 'Download example JSON'}</button><button type="button" data-result-action="print">${language === 'bn' ? 'প্রিন্ট করুন' : 'Print result'}</button></div><p><b>Fingerprints:</b> not supplied. No identifier is invented by the frontend.</p></section>`;
  }

  function fixturePicker(active, language) {
    const options = [
      ['complete-comparison', 'Complete comparison'], ['incomplete-one-alternative', 'Incomplete · one alternative'],
      ['missing-climate', 'Missing climate'], ['invalid-input', 'Invalid input'],
      ['service-unavailable', 'Unavailable service'], ['recoverable-error', 'Recoverable error']
    ];
    return `<aside class="fixture-banner" role="note"><div><b>${language === 'bn' ? 'ডেভেলপমেন্ট ফিক্সচার · বৈজ্ঞানিক পরামর্শ নয়' : 'DEVELOPMENT FIXTURE · NOT SCIENTIFIC ADVICE'}</b><span>${language === 'bn' ? 'আলাদা নমুনা ইনপুট; আপনার জমির উত্তর ব্যবহার করা হচ্ছে না।' : 'Separate example inputs; your submitted field answers are not used.'}</span></div><label>${language === 'bn' ? 'অবস্থা দেখুন' : 'Preview state'}<select data-result-fixture>${options.map(([id, label]) => `<option value="${id}" ${id === active ? 'selected' : ''}>${label}</option>`).join('')}</select></label><button type="button" data-result-action="exit-fixture">${language === 'bn' ? 'জমির তথ্যে ফিরুন' : 'Return to field inputs'}</button></aside>`;
  }

  function create(options) {
    const adapter = options.adapter;
    const rerender = options.render;
    const navigate = options.navigate;
    const toast = options.toast;
    const downloadInputs = options.downloadInputs;
    let data = null;
    let selectedPlan = null;
    let climateMetric = 'precipitation';

    async function activateFixture(id) {
      const firstActivation = !data;
      adapter.enableFixture(id, true);
      const result = await adapter.requestPlanning({ fixture: true });
      if (result.state === 'stale') return;
      data = { fixture_id: result.fixture_id, fixture_label: result.fixture_label, fixture_description: result.fixture_description, request: result.request, response: result.response };
      selectedPlan = data.response.alternatives?.find(planHasThreeSteps)?.plan_id || null;
      rerender();
      if (firstActivation && typeof window !== 'undefined') window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
    }
    function deactivateFixture() { data = null; selectedPlan = null; adapter.disableFixture(); }
    function invalidate() { data = null; selectedPlan = null; adapter.disableFixture(); }
    function isFixture() { return Boolean(data); }

    function renderFixture(language = 'en') {
      if (!data) return '';
      const response = data.response;
      if (!['complete', 'incomplete'].includes(response.status)) {
        const title = response.status === 'invalid_input' ? 'Example invalid input' : response.status === 'error' ? 'Example recoverable error' : 'Example service unavailable';
        return `<div class="result-page" data-no-translate>${fixturePicker(data.fixture_id, language)}${unavailableCard(title, response.reason || response.errors?.[0]?.label || 'No result is available.', response.recoverable ? '<button type="button" data-result-action="retry">Retry real service</button>' : '')}</div>`;
      }
      const plan = response.alternatives?.find(item => item.plan_id === selectedPlan) || response.alternatives?.[0];
      return `<div class="result-page" data-no-translate>${fixturePicker(data.fixture_id, language)}
        <header class="result-hero"><div><p class="result-eyebrow">SOIL TO STARS · RESULT WORKSPACE</p><h1>${language === 'bn' ? 'আপনার জমির সিদ্ধান্ত, প্রমাণসহ' : 'Your field decision, with the evidence beside it.'}</h1><p>${language === 'bn' ? 'পরিকল্পনা, সময়, কারণ ও অজানা তথ্য এক জায়গায়।' : 'Plans, timing, reasons and unknowns stay together.'}</p></div><div class="result-hero__status">${badge(response.status)}<span>${esc(response.coverage?.label || '')}</span></div></header>
        ${fieldSummary(data, language)}${vulnerability(response.current_crop_assessment, language)}${comparison(response, language, selectedPlan)}${operationTimeline(plan, language)}${climatePanel(response.climate, language, climateMetric)}${evidencePanel(response, language)}${toolsPanel(response, language)}${receiptPanel(data, language)}
      </div>`;
    }

    function renderGenuine(request) {
      return `<div class="result-page" data-no-translate><header class="result-hero"><div><p class="result-eyebrow">SOIL TO STARS · RESULT WORKSPACE</p><h1>Your field inputs are ready.</h1><p>The scientific planning service is not connected yet. Your answers remain preserved.</p></div>${badge('unavailable')}</header>${genuineSummary(request)}${unavailableCard('Planning and evidence unavailable', 'No backend comparison, current-crop assessment, climate history, intended-crop check or replay payload is connected. A demo will never open automatically after this failure.', '<button type="button" data-result-action="open-fixture">Open isolated development fixture</button>')}</div>`;
    }

    function downloadReceipt() {
      if (!data) return;
      const blob = new Blob([JSON.stringify(receipt(data), null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob), anchor = document.createElement('a');
      anchor.href = url; anchor.download = `soil-to-stars-${data.fixture_id}-example.json`; anchor.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      toast('Example receipt downloaded with fixture labels.');
    }

    function handleClick(button) {
      if (button.dataset.resultMetric) { climateMetric = button.dataset.resultMetric; rerender(); return true; }
      if (button.dataset.resultPlan) { selectedPlan = button.dataset.resultPlan; rerender(); return true; }
      switch (button.dataset.resultAction) {
        case 'edit-inputs': deactivateFixture(); navigate('profile'); return true;
        case 'open-fixture': void activateFixture('complete-comparison'); return true;
        case 'exit-fixture': deactivateFixture(); navigate('profile'); return true;
        case 'download-inputs': downloadInputs(); return true;
        case 'download-receipt': downloadReceipt(); return true;
        case 'print': window.print(); return true;
        case 'intended-check': {
          const status = document.querySelector('#intended-status');
          if (status) status.textContent = 'Unavailable: no same-engine endpoint is connected. No browser score was calculated.';
          return true;
        }
        case 'retry': toast('No real endpoint is configured; fixture success was not activated.'); return true;
        default: return false;
      }
    }
    function handleChange(target) {
      if (target.matches('[data-result-fixture]')) { void activateFixture(target.value); return true; }
      if (target.matches('[data-result-metric]')) { climateMetric = target.dataset.resultMetric; rerender(); return true; }
      return false;
    }
    function setMetric(metric) { climateMetric = metric; rerender(); }

    return { activateFixture, deactivateFixture, invalidate, isFixture, renderFixture, renderGenuine, handleClick, handleChange, setMetric, downloadReceipt, getData: () => data };
  }

  return { create, receipt, planHasThreeSteps, genuineSummary };
});
