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
  const t = (language, en, bn) => language === 'bn' ? bn : en;

  const OPERATION_LEGEND = [
    ['preparation', 'Preparation', 'প্রস্তুতি'],
    ['sowing', 'Sowing', 'বপন/রোপণ'],
    ['growth', 'Growth', 'বৃদ্ধি'],
    ['maturity', 'Maturity', 'পরিপক্বতা'],
    ['harvest', 'Harvest', 'ফসল তোলা'],
    ['clearance', 'Clearance', 'জমি খালি'],
    ['transition', 'Transition', 'স্থানান্তর']
  ];

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

  function districtLabel(location, language = 'en') {
    if (!location) return t(language, 'Not supplied', 'দেওয়া হয়নি');
    if (location.district_label) return text(location.district_label, language);
    const id = location.district_id || '';
    return id.replace(/^bd-district-/, '').replaceAll('-', ' ') || t(language, 'Not supplied', 'দেওয়া হয়নি');
  }

  function historySummary(history, language = 'en') {
    if (!history) return t(language, 'Not supplied', 'দেওয়া হয়নি');
    if (history.summary) return text(history.summary, language);
    if (history.state === 'first_cultivation') return t(language, 'First cultivation', 'প্রথম চাষ');
    if (Array.isArray(history.entries) && history.entries.length) {
      return history.entries.map(entry => human(entry.crop_id || 'crop')).join(' · ');
    }
    return human(history.state || 'not supplied');
  }

  function baselineSummary(baseline, language = 'en') {
    if (!baseline) return t(language, 'Not supplied', 'দেওয়া হয়নি');
    if (baseline.summary) return text(baseline.summary, language);
    if (baseline.state === 'no_established_rotation') return t(language, 'No established rotation', 'নির্ধারিত আবর্তন নেই');
    if (Array.isArray(baseline.segments) && baseline.segments.length) {
      return baseline.segments.map(segment => segment.kind === 'fallow' ? t(language, 'fallow', 'পতিত') : human(segment.crop_id || 'crop')).join(' → ');
    }
    return human(baseline.state || 'not supplied');
  }

  function infoChip(label, value, note = '') {
    return `<div class="result-chip"><small>${esc(label)}</small><b>${esc(value)}</b>${note ? `<span>${esc(note)}</span>` : ''}</div>`;
  }

  function statusRow(label, value, explanation = '') {
    return `<div class="status-row"><span>${esc(label)}</span>${badge(value, value)}${explanation ? `<p>${esc(explanation)}</p>` : ''}</div>`;
  }

  function genuineSummary(request, language = 'en') {
    if (!request) {
      return unavailableCard(
        t(language, 'No submitted field yet', 'এখনও জমা দেওয়া জমি নেই'),
        t(language, 'Complete the six field questions before requesting a result.', 'ফলাফল চাওয়ার আগে ছয়টি প্রশ্নের উত্তর দিন।'),
        `<button type="button" class="primary" data-result-action="edit-inputs">${t(language, 'Set up field', 'জমির তথ্য দিন')}</button>`
      );
    }
    const location = request.location || {};
    const current = request.current || {};
    const availability = request.availability || {};
    const cropName = current.state === 'fallow' ? t(language, 'Fallow', 'পতিত') : human(current.crop_id || t(language, 'Not supplied', 'দেওয়া হয়নি'));
    const available = `${formatDate(availability.start)}${availability.kind === 'window' ? ` – ${formatDate(availability.end)}` : ''}`;
    return `<section class="result-card result-summary-card" aria-labelledby="field-summary-title">
      <div class="result-summary-top">
        <div>
          <p class="result-eyebrow">01 · ${t(language, 'FIELD SUMMARY', 'জমির সারাংশ')}</p>
          <h2 id="field-summary-title">${esc(cropName)}</h2>
          <p class="result-summary-meta">${esc(districtLabel(location, language))} · ${esc(human(location.selection_method || 'unknown'))} · ${t(language, 'not scientific coverage', 'বৈজ্ঞানিক কভারেজ নয়')}</p>
        </div>
        <div class="result-summary-status">${badge('unavailable', t(language, 'Planning Unavailable', 'পরিকল্পনা অনুপলব্ধ'))}<span>${esc(available)}</span></div>
      </div>
      <div class="result-chip-row">
        ${infoChip(t(language, 'Current crop', 'বর্তমান ফসল'), cropName, current.sown_on ? formatDate(current.sown_on) : t(language, 'Planting date not supplied', 'রোপণের তারিখ দেওয়া হয়নি'))}
        ${infoChip(t(language, 'Field available', 'জমি খালি হবে'), available, human(availability.basis || 'unknown basis'))}
        ${infoChip(t(language, 'Water access', 'পানির সুবিধা'), human(request.irrigation?.access || 'not supplied'))}
        ${infoChip(t(language, 'Priority', 'অগ্রাধিকার'), human(request.priority || 'not supplied'))}
      </div>
      <details class="result-expand">
        <summary>${t(language, 'View full profile', 'সম্পূর্ণ তথ্য')}</summary>
        <div class="result-expand__grid">
          ${infoChip(t(language, 'History', 'আগের ফসল'), historySummary(request.crop_history, language), t(language, 'Farmer-reported input', 'কৃষকের দেওয়া তথ্য'))}
          ${infoChip(t(language, 'Usual practice', 'সাধারণ পরিকল্পনা'), baselineSummary(request.baseline, language), t(language, 'Assessed input, not a recommendation', 'মূল্যায়নের ইনপুট, সুপারিশ নয়'))}
        </div>
        <div class="result-freshness"><span>●</span><b>${t(language, 'Inputs preserved', 'ইনপুট সংরক্ষিত')}</b><span>${t(language, 'No scientific result is connected', 'কোনো বৈজ্ঞানিক ফলাফল সংযুক্ত নেই')}</span></div>
      </details>
      <div class="result-actions"><button type="button" data-result-action="edit-inputs">${t(language, 'Edit inputs', 'তথ্য সম্পাদনা')}</button><button type="button" data-result-action="download-inputs">${t(language, 'Download input JSON', 'ইনপুট JSON ডাউনলোড')}</button></div>
    </section>`;
  }

  function fieldSummary(data, language) {
    const request = data.request;
    const response = data.response;
    const cropName = text(request.current.label, language);
    const period = `${formatDate(request.availability.start)} – ${formatDate(request.availability.end)}`;
    const comparison = response.comparison_period ? `${response.comparison_period.start} → ${response.comparison_period.end}` : period;
    return `<section class="result-card result-summary-card" aria-labelledby="field-summary-title">
      <div class="result-summary-top">
        <div>
          <p class="result-eyebrow">01 · ${t(language, 'FIELD SUMMARY', 'জমির সারাংশ')}</p>
          <h2 id="field-summary-title">${esc(cropName)}</h2>
          <p class="result-summary-meta">${esc(text(request.location.district_label, language))} · ${esc(human(request.location.selection_method))} · ${t(language, 'not scientific coverage', 'বৈজ্ঞানিক কভারেজ নয়')}</p>
        </div>
        <div class="result-summary-status">${badge(response.status, response.status)}<span>${esc(comparison)}</span></div>
      </div>
      <div class="result-chip-row">
        ${infoChip(t(language, 'Current crop', 'বর্তমান ফসল'), cropName, request.current.sown_on ? formatDate(request.current.sown_on) : t(language, 'Planting date not supplied', 'রোপণের তারিখ দেওয়া হয়নি'))}
        ${infoChip(t(language, 'Field available', 'জমি খালি হবে'), period, human(request.availability.basis))}
        ${infoChip(t(language, 'Water access', 'পানির সুবিধা'), human(request.irrigation.access))}
        ${infoChip(t(language, 'Priority', 'অগ্রাধিকার'), human(request.priority))}
      </div>
      <details class="result-expand">
        <summary>${t(language, 'View full profile', 'সম্পূর্ণ তথ্য')}</summary>
        <div class="result-expand__grid">
          ${infoChip(t(language, 'History', 'আগের ফসল'), text(request.crop_history.summary, language), t(language, 'Separate example input', 'কৃষকের দেওয়া নমুনা তথ্য'))}
          ${infoChip(t(language, 'Usual practice', 'সাধারণ পরিকল্পনা'), text(request.baseline.summary, language), t(language, 'Assessed, not recommended', 'পর্যালোচনা করা হয়েছে, সুপারিশ নয়'))}
        </div>
        <div class="result-freshness"><span>●</span><b>${t(language, 'Example result', 'নমুনা ফলাফল')}</b><span>${t(language, 'No real API or climate package loaded', 'কোনো বাস্তব API বা জলবায়ু প্যাকেজ লোড হয়নি')}</span></div>
      </details>
      <div class="result-actions"><button type="button" data-result-action="edit-inputs">${t(language, 'Edit inputs', 'তথ্য সম্পাদনা')}</button></div>
    </section>`;
  }

  function vulnerability(assessment, language) {
    const checks = assessment?.checks || [];
    const stage = assessment?.stage ? human(assessment.stage) : t(language, 'unknown', 'জানা নেই');
    const period = assessment?.assessment_period || t(language, 'not established', 'নির্ধারিত নয়');
    const statusLabel = assessment?.status === 'incomplete'
      ? t(language, 'Assessment incomplete', 'মূল্যায়ন অসম্পূর্ণ')
      : assessment?.status === 'complete'
        ? t(language, 'Assessment ready', 'মূল্যায়ন প্রস্তুত')
        : (assessment?.status || 'unavailable');
    const leadTitle = assessment?.status === 'incomplete'
      ? t(language, 'Insufficient Data', 'পর্যাপ্ত তথ্য নেই')
      : assessment?.status === 'complete'
        ? t(language, 'Exposure checked for this crop', 'এই ফসলের প্রভাব যাচাই হয়েছে')
        : human(assessment?.status || 'unavailable');
    return `<section class="result-card" aria-labelledby="vulnerability-title">
      <div class="result-section-heading">
        <div><p class="result-eyebrow">02 · ${t(language, 'CURRENT CROP', 'বর্তমান ফসল')}</p><h2 id="vulnerability-title">${t(language, 'Historical exposure assessment', 'ঐতিহাসিক প্রভাব মূল্যায়ন')}</h2></div>
        ${badge(assessment?.status || 'unavailable', statusLabel)}
      </div>
      <div class="assessment-strip">
        <span class="assessment-strip__icon" aria-hidden="true">◎</span>
        <div>
          <b>${esc(leadTitle)}</b>
          <p>${esc(text(assessment?.crop_label, language) || t(language, 'Not supplied', 'দেওয়া হয়নি'))} · ${t(language, 'Stage', 'পর্যায়')}: ${esc(stage)} · ${t(language, 'Assessment period', 'মূল্যায়নের সময়')}: ${esc(period)}</p>
        </div>
      </div>
      <div class="check-grid">${checks.map(check => `<article class="check-tile check-tile--${esc(check.outcome)}"><div class="check-tile__head">${badge(check.outcome)}<h3>${esc(text(check.label, language))}</h3></div><p>${esc(check.missing_information || check.limitation || '')}</p></article>`).join('')}</div>
      <p class="result-limit"><b>${t(language, 'Limit:', 'সীমা:')}</b> ${esc(assessment?.limitation || 'Not assessed.')}</p>
    </section>`;
  }

  function planCrops(plan, language) {
    if (plan.role === 'baseline') {
      return (plan.segments || []).map(item => `<li><b>${esc(text(item.label, language))}</b><span>${esc(item.period || '')}</span></li>`).join('');
    }
    return (plan.steps || []).map((item, index) => `<li><span>${String(index + 1).padStart(2, '0')}</span><b>${esc(text(item.crop_label, language))}</b><small>${esc(item.field_clearance_window?.latest || '')}</small></li>`).join('');
  }

  function indicatorRows(plan) {
    return (plan.indicators || []).map(item => statusRow(item.label, item.value || item.status, item.explanation || '')).join('');
  }

  function comparison(response, language, selectedPlan) {
    const plans = [response.baseline_assessment, ...(response.alternatives || [])].filter(Boolean);
    const missingSecond = (response.alternatives || []).length < 2;
    const periodLine = `${response.comparison_period?.start || ''} → ${response.comparison_period?.end || ''} · ${response.comparison_period?.explanation || ''}${response.comparison_period?.policy_id ? ` · ${response.comparison_period.policy_id}${response.comparison_period.policy_version ? ` ${response.comparison_period.policy_version}` : ''}` : ''}`;
    return `<section class="result-card result-comparison" aria-labelledby="comparison-title">
      <div class="result-section-heading">
        <div>
          <p class="result-eyebrow">03 · ${t(language, 'PLAN COMPARISON', 'পরিকল্পনা তুলনা')}</p>
          <h2 id="comparison-title">${t(language, 'Three positions on one shared horizon', 'একই সময়সীমায় তিনটি কৌশল')}</h2>
          <p>${esc(periodLine)}</p>
        </div>
        ${badge(response.status, response.status)}
      </div>
      <div class="plan-comparison-grid">${plans.map(plan => {
        const role = plan.role === 'baseline' ? t(language, 'BASELINE', 'মূল পরিকল্পনা') : t(language, 'FUTURE ALTERNATIVE', 'ভবিষ্যৎ বিকল্প');
        return `<article class="plan-card ${plan.plan_id === selectedPlan ? 'is-selected' : ''}">
          <div class="plan-card__head">
            <div><small>${esc(role)}</small><h3>${esc(text(plan.label, language))}</h3></div>
            ${badge(plan.feasibility, plan.feasibility)}
          </div>
          <p class="plan-card__period">${t(language, 'Completes', 'শেষ')} <b>${esc(plan.completion_date || 'Unknown')}</b> · ${plan.role === 'baseline' ? t(language, 'Flexible segments', 'নমনীয় অংশ') : `${(plan.steps || []).length}/3 ${t(language, 'future steps', 'ধাপ')}`}</p>
          <ul class="plan-crops plan-crops--compact">${planCrops(plan, language)}</ul>
          <div class="status-stack">${indicatorRows(plan)}</div>
          <details class="result-expand plan-card__details">
            <summary>${t(language, 'View details', 'বিস্তারিত দেখুন')}</summary>
            <div class="status-stack status-stack--muted">${(plan.indicators || []).map(item => `<p><b>${esc(item.label)}</b>: ${esc(item.explanation || '')}${item.unit ? ` (${esc(item.unit)})` : ''}</p>`).join('')}</div>
          </details>
          ${plan.role !== 'baseline' ? `<button type="button" data-result-plan="${esc(plan.plan_id)}" aria-pressed="${plan.plan_id === selectedPlan}">${t(language, 'View operations timeline', 'টাইমলাইন দেখুন')}</button>` : ''}
        </article>`;
      }).join('')}${missingSecond ? `<article class="plan-card plan-card--missing"><span aria-hidden="true">＋</span><h3>${t(language, 'Second alternative unavailable', 'দ্বিতীয় বিকল্প অনুপলব্ধ')}</h3><p>${t(language, 'No distinct supported plan was supplied, so no filler or clone is shown.', 'সমর্থিত পৃথক পরিকল্পনা না থাকায় কোনো নকল পরিকল্পনা যোগ করা হয়নি।')}</p></article>` : ''}</div>
    </section>`;
  }

  function operationLegend(language) {
    return `<ul class="ops-legend" aria-label="${t(language, 'Operation legend', 'কার্যক্রমের ব্যাখ্যা')}">${OPERATION_LEGEND.map(([type, en, bn]) => `<li><i class="operation operation--${type}" aria-hidden="true"></i><span>${esc(language === 'bn' ? bn : en)}</span></li>`).join('')}</ul>`;
  }

  function operationTimeline(plan, language) {
    if (!plan) return unavailableCard('Timeline unavailable', 'Select a complete alternative with operations.');
    const operations = (plan.steps || []).flatMap(step => (step.operations || []).map(operation => ({ ...operation, crop: text(step.crop_label, language), step: step.step_id })));
    return `<section class="result-card" aria-labelledby="timeline-title">
      <div class="result-section-heading">
        <div>
          <p class="result-eyebrow">04 · ${t(language, 'OPERATIONS TIMELINE', 'সময়ের ধাপ')}</p>
          <h2 id="timeline-title">${esc(text(plan.label, language))}</h2>
          <p>${t(language, 'Maturity, harvest and field clearance remain distinct.', 'পরিপক্বতা, ফসল তোলা ও জমি খালি হওয়া আলাদা রাখা হয়েছে।')}</p>
        </div>
        ${badge(plan.status)}
      </div>
      ${operationLegend(language)}
      <div class="operations-track" role="img" aria-label="Example chronological operations timeline">${(plan.steps || []).map((step, index) => `<article>
        <div class="operations-track__head"><h3>${esc(text(step.crop_label, language))}</h3><span>${index + 1}</span></div>
        <div class="operations-track__bar">${(step.operations || []).map(operation => `<span title="${esc(`${human(operation.type)}: ${operation.start_window.earliest} to ${operation.start_window.latest}`)}" class="operation operation--${esc(operation.type)}"></span>`).join('')}</div>
        <small>${esc(step.operations?.[0]?.start_window?.earliest || '')} → ${esc(step.field_clearance_window?.latest || '')}</small>
      </article>`).join('')}</div>
      <details class="result-expand timeline-table">
        <summary>${t(language, 'Comparison details / accessible table', 'তুলনার বিস্তারিত / অ্যাক্সেসিবল টেবিল')}</summary>
        <div class="table-scroll"><table><thead><tr><th>Crop</th><th>Operation</th><th>Earliest</th><th>Latest</th><th>Note</th></tr></thead><tbody>${operations.map(item => `<tr><td>${esc(item.crop)}</td><td>${esc(human(item.type))}</td><td>${esc(item.start_window.earliest)}</td><td>${esc(item.start_window.latest)}</td><td>${esc(item.detail || '')}</td></tr>`).join('')}</tbody></table></div>
      </details>
      ${(plan.unallocated_intervals || []).map(item => `<p class="result-limit"><b>Unallocated:</b> ${esc(item.start)} → ${esc(item.end)}. No land-cover meaning is inferred.</p>`).join('')}
    </section>`;
  }

  function chart(series, language) {
    const values = series.values || [];
    const months = language === 'bn'
      ? ['জা', 'ফে', 'মা', 'এ', 'মে', 'জুন', 'জু', 'আ', 'সে', 'অ', 'ন', 'ডি']
      : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const min = Math.min(...values), max = Math.max(...values), range = max - min || 1;
    const points = values.map((value, index) => `${40 + index * 46},${168 - ((value - min) / range) * 118}`).join(' ');
    return `<svg class="result-chart" viewBox="0 0 600 210" role="img" aria-label="${esc(series.label)}">
      <title>${esc(series.label)} · ${esc(series.unit)}</title>
      ${[48, 88, 128, 168].map(y => `<line x1="40" x2="576" y1="${y}" y2="${y}"/>`).join('')}
      <polyline points="${points}"/>
      ${values.map((value, index) => `<circle tabindex="0" cx="${40 + index * 46}" cy="${168 - ((value - min) / range) * 118}" r="4.5"><title>${months[index]}: ${value} ${esc(series.unit)}</title></circle>`).join('')}
      ${months.map((month, index) => `<text x="${40 + index * 46}" y="198" text-anchor="middle">${esc(month)}</text>`).join('')}
    </svg>`;
  }

  function climatePanel(climate, language, metric) {
    if (!climate || climate.status !== 'complete') {
      return `<section class="result-card" aria-labelledby="climate-title"><p class="result-eyebrow">05 · ${t(language, 'CLIMATE HISTORY', 'জলবায়ু ইতিহাস')}</p>${unavailableCard(t(language, 'Historical climate unavailable', 'ঐতিহাসিক জলবায়ু অনুপলব্ধ'), climate?.reason || 'No prepared chart/history payload was supplied.')}</section>`;
    }
    const selected = climate.series.find(series => series.key === metric) || climate.series[0];
    const stats = (climate.comparison?.statistics || []).map(stat => `<li><b>${esc(human(stat.metric))} · ${esc(stat.window)}</b>: ${esc(String(stat.earlier_mean))} → ${esc(String(stat.recent_mean))} ${esc(stat.unit)} (Δ ${esc(String(stat.delta))})</li>`).join('');
    return `<section class="result-card" aria-labelledby="climate-title">
      <div class="result-section-heading">
        <div>
          <p class="result-eyebrow">05 · ${t(language, 'HISTORICAL WEATHER', 'ঐতিহাসিক আবহাওয়া')}</p>
          <h2 id="climate-title">${t(language, 'Regional context, not a field measurement', 'আঞ্চলিক প্রেক্ষাপট, জমির মাপ নয়')}</h2>
        </div>
        ${badge('fixture', 'Example data')}
      </div>
      <div class="chart-tabs" role="group" aria-label="Climate metric">${climate.series.map(series => `<button type="button" data-result-metric="${esc(series.key)}" aria-pressed="${series.key === selected.key}">${esc(series.key === 'precipitation' ? t(language, 'Rainfall', 'বৃষ্টিপাত') : t(language, 'Temperature', 'তাপমাত্রা'))}</button>`).join('')}</div>
      <div class="chart-header"><div><small>${esc(selected.statistic)}</small><h3>${esc(selected.label)}</h3></div><b>${esc(selected.unit)}</b></div>
      <div class="chart-frame">${chart(selected, language)}</div>
      <div class="chart-meta">
        <span>${esc(climate.period.start)} → ${esc(climate.period.end)}</span>
        <span>${esc(climate.time_standard)}</span>
        <span>${esc(climate.missingness)}</span>
        <span>${esc(climate.comparison.earlier)} → ${esc(climate.comparison.recent)}</span>
      </div>
      <p class="chart-finding">${esc(climate.comparison.finding)}</p>
      ${stats ? `<ul class="chart-stats">${stats}</ul>` : ''}
      <p class="result-limit"><b>${t(language, 'Note:', 'নোট:')}</b> ${t(language, 'Monthly mean daily maximum is not the absolute monthly maximum. Grid support is regional context, not a farm boundary average.', 'মাসিক গড় দৈনিক সর্বোচ্চ তাপমাত্রা মাসের পরম সর্বোচ্চ নয়। গ্রিড মান আঞ্চলিক প্রেক্ষাপট, জমির সীমার গড় নয়।')} ${esc((climate.limitations || []).join(' '))}</p>
    </section>`;
  }

  function evidencePanel(response, language) {
    return `<section class="result-card" aria-labelledby="evidence-title">
      <div class="result-section-heading">
        <div>
          <p class="result-eyebrow">06 · ${t(language, 'REASONS & EVIDENCE', 'কারণ ও প্রমাণ')}</p>
          <h2 id="evidence-title">${t(language, 'Why, why not, and what is missing', 'কেন, কেন নয়, কী তথ্য দরকার')}</h2>
        </div>
      </div>
      <div class="evidence-list">${(response.checks || []).map(check => `<article class="evidence-card evidence-card--${esc(check.outcome)}">
        <div class="evidence-card__head">${badge(check.outcome)}<h3>${esc(text(check.label, language))}</h3></div>
        <p class="evidence-card__lead">${esc(check.missing_information || check.limitation || human(check.outcome))}</p>
        <details class="result-expand">
          <summary>${t(language, 'View technical evidence', 'কারিগরি বিস্তারিত')}</summary>
          <dl>
            <dt>Crop / stage</dt><dd>${esc(human(check.crop_id || 'not supplied'))} · ${esc(human(check.stage || 'not supplied'))}</dd>
            <dt>Period</dt><dd>${esc(check.period || 'Not supplied')}</dd>
            <dt>Rule</dt><dd><code>${esc(check.rule_id || 'Not supplied')}</code></dd>
            <dt>Sources</dt><dd>${esc((check.source_ids || []).join(', ') || 'No source attached')}</dd>
            <dt>Missing / limit</dt><dd>${esc(check.missing_information || check.limitation || 'None supplied')}</dd>
          </dl>
        </details>
      </article>`).join('')}</div>
      <details class="result-expand source-drawer">
        <summary>${t(language, 'Sources and methods drawer', 'উৎস ও পদ্ধতির বিবরণ')}</summary>
        ${(response.sources || []).map(source => `<article><h3>${esc(source.provider)}</h3><dl><dt>Dataset/version</dt><dd>${esc(source.product_version)}</dd><dt>Period</dt><dd>${esc(source.period)}</dd><dt>Spatial support</dt><dd>${esc(source.spatial_support)}</dd><dt>QA</dt><dd>${esc(source.qa)}</dd></dl><a href="${esc(source.url)}" target="_blank" rel="noopener">Official documentation ↗</a></article>`).join('')}
        <p><b>Versions:</b> contract ${esc(response.versions?.contract || 'unknown')} · catalogue ${esc(response.versions?.catalogue || 'unknown')} · method ${esc(response.versions?.method || 'unknown')}</p>
      </details>
    </section>`;
  }

  function toolsPanel(response, language) {
    return `<section class="result-tools-section" aria-label="Tools and data">
      <div class="result-section-heading result-section-heading--plain">
        <div>
          <p class="result-eyebrow">07 · ${t(language, 'TOOLS & DATA', 'টুলস ও তথ্য')}</p>
          <h2>${t(language, 'Checks, replay and export', 'যাচাই, পুনরায় পরীক্ষা ও রপ্তানি')}</h2>
        </div>
      </div>
      <div class="result-tools">
        <article class="result-card">
          <p class="result-eyebrow">07A · ${t(language, 'INTENDED-CROP CHECK', 'প্রস্তাবিত ফসল যাচাই')}</p>
          <h3>${t(language, 'Check a crop with the same engine', 'একই নিয়মে ফসল যাচাই')}</h3>
          <div class="result-form-row">
            <label>${t(language, 'Crop', 'ফসল')}<select id="intended-crop"><option value="">${t(language, 'Choose crop', 'ফসল বেছে নিন')}</option><option value="mustard">Mustard</option><option value="mungbean">Mungbean</option><option value="rice">Rice</option></select></label>
            <label>${t(language, 'Planting date', 'রোপণের তারিখ')}<input id="intended-date" type="date"></label>
          </div>
          <button type="button" data-result-action="intended-check">${t(language, 'Check availability', 'উপলব্ধতা যাচাই')}</button>
          <p class="result-limit" id="intended-status">${esc(response.intended_crop_assessment?.reason || 'Unavailable')}</p>
        </article>
        <article class="result-card">
          <p class="result-eyebrow">07B · ${t(language, 'HISTORICAL REPLAY', 'ঐতিহাসিক পুনরায় পরীক্ষা')}</p>
          <h3>${t(language, 'Same field, documented historical period', 'একই জমি, নথিভুক্ত সময়কাল')}</h3>
          <p>${esc(response.historical_replay?.reason || 'No replay payload supplied.')}</p>
          <button type="button" data-result-action="replay" disabled>${t(language, 'Replay unavailable', 'পুনরায় পরীক্ষা অনুপলব্ধ')}</button>
          <p class="result-limit">No browser-made drought multiplier or future-weather slider is used.</p>
        </article>
      </div>
    </section>`;
  }

  function receiptPanel(data, language) {
    return `<section class="result-card result-receipt" aria-labelledby="receipt-title">
      <div>
        <p class="result-eyebrow">08 · ${t(language, 'PRINT & JSON RECEIPT', 'প্রিন্ট ও JSON')}</p>
        <h2 id="receipt-title">${t(language, 'Keep the same example result', 'এই নমুনার একই তথ্য রাখুন')}</h2>
        <p>${t(language, 'The export preserves the fixture label, statuses, limitations and source metadata.', 'রপ্তানিতে নমুনা লেবেল, অবস্থা, সীমাবদ্ধতা ও উৎস থাকবে।')}</p>
        <p class="receipt-note"><b>Fingerprints:</b> not supplied. No identifier is invented by the frontend.</p>
      </div>
      <div class="result-actions result-actions--end">
        <button type="button" class="primary" data-result-action="download-receipt">${t(language, 'Download example JSON', 'নমুনা JSON ডাউনলোড')}</button>
        <button type="button" data-result-action="print">${t(language, 'Print result', 'প্রিন্ট করুন')}</button>
      </div>
    </section>`;
  }

  function fixturePicker(active, language) {
    const options = [
      ['complete-comparison', 'Complete comparison'], ['incomplete-one-alternative', 'Incomplete · one alternative'],
      ['missing-climate', 'Missing climate'], ['invalid-input', 'Invalid input'],
      ['service-unavailable', 'Unavailable service'], ['recoverable-error', 'Recoverable error']
    ];
    return `<aside class="fixture-banner" role="note"><div><b>${t(language, 'DEVELOPMENT FIXTURE · NOT SCIENTIFIC ADVICE', 'ডেভেলপমেন্ট ফিক্সচার · বৈজ্ঞানিক পরামর্শ নয়')}</b><span>${t(language, 'Separate example inputs; your submitted field answers are not used.', 'আলাদা নমুনা ইনপুট; আপনার জমির উত্তর ব্যবহার করা হচ্ছে না।')}</span></div><label>${t(language, 'Preview state', 'অবস্থা দেখুন')}<select data-result-fixture>${options.map(([id, label]) => `<option value="${id}" ${id === active ? 'selected' : ''}>${label}</option>`).join('')}</select></label><button type="button" data-result-action="exit-fixture">${t(language, 'Return to field inputs', 'জমির তথ্যে ফিরুন')}</button></aside>`;
  }

  function create(options) {
    const adapter = options.adapter;
    const rerender = options.render;
    const navigate = options.navigate;
    const toast = options.toast;
    const downloadInputs = options.downloadInputs;
    const enterFixtureMode = options.enterFixtureMode;
    const leaveFixtureMode = options.leaveFixtureMode;
    let data = null;
    let selectedPlan = null;
    let climateMetric = 'precipitation';

    async function activateFixture(id) {
      const firstActivation = !data;
      enterFixtureMode?.();
      adapter.enableFixture(id, true);
      const result = await adapter.requestPlanning({ fixture: true });
      if (result.state === 'stale') return;
      data = { fixture_id: result.fixture_id, fixture_label: result.fixture_label, fixture_description: result.fixture_description, request: result.request, response: result.response };
      selectedPlan = data.response.alternatives?.find(planHasThreeSteps)?.plan_id || null;
      rerender();
      if (firstActivation && typeof window !== 'undefined') window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
    }
    function deactivateFixture() { data = null; selectedPlan = null; adapter.disableFixture(); leaveFixtureMode?.(); }
    function invalidate() { data = null; selectedPlan = null; adapter.disableFixture(); leaveFixtureMode?.(); }
    function isFixture() { return Boolean(data); }

    function renderFixture(language = 'en', options = {}) {
      if (!data) return '';
      const showFixtureBanner = options.showFixtureBanner !== false;
      const banner = showFixtureBanner ? fixturePicker(data.fixture_id, language) : '';
      const response = data.response;
      if (!['complete', 'incomplete'].includes(response.status)) {
        const title = response.status === 'invalid_input' ? 'Example invalid input' : response.status === 'error' ? 'Example recoverable error' : 'Example service unavailable';
        return `<div class="result-page" data-no-translate>${banner}${unavailableCard(title, response.reason || response.errors?.[0]?.label || 'No result is available.', response.recoverable ? '<button type="button" data-result-action="retry">Retry real service</button>' : '')}</div>`;
      }
      const plan = response.alternatives?.find(item => item.plan_id === selectedPlan) || response.alternatives?.[0];
      return `<div class="result-page" data-no-translate>${banner}
        <section class="result-page-intro" aria-label="Result workspace">
          <div>
            <p class="result-eyebrow">SOIL TO STARS · RESULT WORKSPACE</p>
            <h1>${t(language, 'Your field decision, with the evidence beside it.', 'আপনার জমির সিদ্ধান্ত, প্রমাণসহ')}</h1>
            <p>${t(language, 'Plans, timing, reasons and unknowns stay together.', 'পরিকল্পনা, সময়, কারণ ও অজানা তথ্য এক জায়গায়।')}</p>
          </div>
          <div class="result-page-intro__status">${badge(response.status)}<span>${esc(response.coverage?.label || '')}</span></div>
        </section>
        ${fieldSummary(data, language)}${vulnerability(response.current_crop_assessment, language)}${comparison(response, language, selectedPlan)}${operationTimeline(plan, language)}${climatePanel(response.climate, language, climateMetric)}${evidencePanel(response, language)}${toolsPanel(response, language)}${receiptPanel(data, language)}
      </div>`;
    }

    function renderGenuine(request, language = 'en') {
      return `<div class="result-page" data-no-translate>
        <section class="result-page-intro" aria-label="Result workspace">
          <div>
            <p class="result-eyebrow">SOIL TO STARS · RESULT WORKSPACE</p>
            <h1>${t(language, 'Your field inputs are ready.', 'আপনার জমির তথ্য প্রস্তুত।')}</h1>
            <p>${t(language, 'The scientific planning service is not connected yet. Your answers remain preserved.', 'বৈজ্ঞানিক পরিকল্পনা সেবা এখনও সংযুক্ত নয়। আপনার উত্তর সংরক্ষিত আছে।')}</p>
          </div>
          ${badge('unavailable')}
        </section>
        ${genuineSummary(request, language)}
        ${unavailableCard(
          t(language, 'Planning and evidence unavailable', 'পরিকল্পনা ও প্রমাণ অনুপলব্ধ'),
          t(language, 'No backend comparison, current-crop assessment, climate history, intended-crop check or replay payload is connected. A demo will never open automatically after this failure.', 'কোনো ব্যাকএন্ড তুলনা, বর্তমান ফসল মূল্যায়ন, জলবায়ু ইতিহাস, প্রস্তাবিত ফসল যাচাই বা পুনরায় পরীক্ষা সংযুক্ত নেই। ব্যর্থতার পর ডেমো স্বয়ংক্রিয়ভাবে খুলবে না।'),
          `<button type="button" data-result-action="open-fixture">${t(language, 'Open isolated development fixture', 'আলাদা ডেভেলপমেন্ট ফিক্সচার খুলুন')}</button>`
        )}
      </div>`;
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
