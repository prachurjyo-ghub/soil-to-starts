(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.STS_RESULT_UI = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const esc = value => String(value ?? '').replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
  const text = (value, language = 'en') => typeof value === 'object' && value ? (value[language] || value.en || '') : String(value ?? '');
  const human = value => String(value ?? '').replaceAll('_', ' ').replace(/\b\w/g, character => character.toUpperCase());
  const formatDate = value => {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return 'Not supplied';
    const date = new Date(`${value}T00:00:00Z`);
    return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value ? new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(date) : 'Not supplied';
  };
  const planHasThreeSteps = plan => plan?.status === 'complete' && Array.isArray(plan.steps) && plan.steps.length === 3;
  const t = (language, en, bn) => language === 'bn' ? bn : en;
  const sourceUrl = value => /^https?:\/\//i.test(String(value || '')) ? value : '#';

  const OPERATION_LEGEND = [
    ['preparation', 'Preparation', 'প্রস্তুতি'],
    ['sowing', 'Sowing', 'বপন/রোপণ'],
    ['growth', 'Growth', 'বৃদ্ধি'],
    ['maturity', 'Maturity', 'পরিপক্বতা'],
    ['harvest', 'Harvest', 'ফসল তোলা'],
    ['clearance', 'Clearance', 'জমি খালি'],
    ['transition', 'Transition', 'স্থানান্তর']
  ];

  function isExample(data) { return Boolean(data?.fixture_id) || data?.response?.data_mode === 'development_fixture'; }

  function receipt(data) {
    const fixture = isExample(data);
    return {
      receipt_type: fixture ? 'development_fixture_example' : data?.response?.analysis_mode==='source_evidence_report' ? 'local_evidence_report' : 'scientific_result',
      fixture,
      warning: fixture ? 'Example export. Not scientific advice or NASA observations.' : undefined,
      request: data?.request || null,
      response: data?.response || null
    };
  }

  function badge(status, label = status) {
    return `<span class="result-badge result-badge--${esc(status || 'unknown')}">${esc(human(label ?? 'unknown'))}</span>`;
  }

  function unavailableCard(title, reason, action = '') {
    return `<section class="result-card result-empty" aria-label="${esc(title)}"><span class="result-empty__icon" aria-hidden="true">◎</span><div><p class="result-eyebrow">RESULT STATUS</p><h2>${esc(title)}</h2><p>${esc(reason)}</p>${action}</div></section>`;
  }

  function districtLabel(location, language = 'en') {
    if (!location) return t(language, 'Not supplied', 'দেওয়া হয়নি');
    if (location.district_label) return text(location.district_label, language);
    const id = location.district_id || '';
    const district=globalThis.STS_INTAKE?.districts?.find(d=>d.id===id);
    if(district)return language==='bn'?district.bn:district.en;
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

  function genuineSummary(request, language = 'en', status = 'unavailable') {
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
        <div class="result-summary-status">${badge('complete',t(language,'Inputs validated','ইনপুট যাচাই হয়েছে'))}<span>${esc(available)}</span></div>
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
        <div class="result-freshness"><span>●</span><b>${t(language, 'Inputs preserved', 'ইনপুট সংরক্ষিত')}</b><span>${status === 'unavailable' ? t(language, 'No scientific result is connected', 'কোনো বৈজ্ঞানিক ফলাফল সংযুক্ত নেই') : t(language, 'Result follows the supplied service response', 'সরবরাহ করা সেবার প্রতিক্রিয়া অনুযায়ী ফলাফল')}</span></div>
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

  function warningExposure(exposure,language){
    if(!exposure||exposure.status==='unavailable')return `<p class="result-limit">${t(language,'Observed warning comparison unavailable','পর্যবেক্ষিত সতর্কতার তুলনা অনুপলব্ধ')}: ${esc(human(exposure?.reason||'no matching source reference'))}</p>`;
    return `<section class="warning-observations"><h3>${t(language,'Observed weather against published warning levels','প্রকাশিত সতর্কতা সীমার সঙ্গে পর্যবেক্ষিত আবহাওয়া')}</h3><p>${esc(exposure.start)} → ${esc(exposure.end)} · NASA POWER · LST · ${esc(exposure.grid_id)}</p><p>${esc(exposure.meaning)}</p><div class="result-chip-row">${exposure.indicators.map(i=>infoChip(i.label,i.exceedance_days===null?'Incomplete':`${i.exceedance_days} days`,`${i.valid_days}/${i.expected_days} observed days; ${i.missing_days} missing`)).join('')}</div><details><summary>${t(language,'Source and exceedance dates','উৎস ও সীমা অতিক্রমের তারিখ')}</summary><a href="${esc(sourceUrl(exposure.reference.source_url))}" target="_blank" rel="noopener">BAMIS ${esc(exposure.reference.section)} · page ${esc(exposure.reference.page)}</a>${exposure.indicators.map(i=>`<p><b>${esc(i.label)}</b>: ${esc(i.dates.join(', ')||'No observed exceedances')}. ${i.missing_days?'Missing days prevent a complete count.':''}</p>`).join('')}<p>${esc(exposure.reference.limitations.join(' '))}</p><code>${esc(exposure.reference.source_sha256)}</code></details></section>`;
  }

  function fieldInputsUsed(language, context) {
    return `<section class="result-card"><h2>${t(language, 'How your answers shape this report', 'আপনার উত্তর কীভাবে রিপোর্ট বদলায়')}</h2>
      <p>${context?.current_crop_calendars?.length
        ? esc(context.region_label) + ' · ' + context.current_crop_calendars.length + ' ' + t(language, 'matching crop calendar records', 'মিলে যাওয়া ফসলের ক্যালেন্ডার')
        : t(language, 'The local library has no matching calendar for this crop and region.', 'এই ফসল ও অঞ্চলের ক্যালেন্ডার স্থানীয় তথ্যভান্ডারে নেই।')}</p>
      <ul>
        <li>${t(language, 'District selects the local NASA weather grid and crop calendar region. Some districts share a grid.', 'জেলা অনুযায়ী নাসার আবহাওয়া গ্রিড ও ফসলের ক্যালেন্ডার অঞ্চল বেছে নেওয়া হয়। কয়েকটি জেলার গ্রিড একই।')}</li>
        <li>${t(language, 'Crop selects matching calendar records. Planting and field-ready dates determine the days checked in the weather archive.', 'ফসল অনুযায়ী ক্যালেন্ডার মেলে। রোপণ ও জমি প্রস্তুতের তারিখ অনুযায়ী আবহাওয়ার দিন বেছে নেওয়া হয়।')}</li>
        <li>${t(language, 'Your crop history, usual crops, irrigation and priority are saved in the field profile. Irrigation and priority currently do not change the calculations or rank crops.', 'ফসলের ইতিহাস, প্রচলিত ফসল, সেচ ও অগ্রাধিকার জমির তথ্যে থাকে। সেচ ও অগ্রাধিকার এখন হিসাব বা ফসলের ক্রম বদলায় না।')}</li>
      </ul></section>`;
  }

  function cropWeather(window, language) {
    if (!window || !Object.hasOwn(window, 'latest_observed')) return '';
    if (window.status !== 'available') {
      const message = window.start && window.latest_observed && window.start > window.latest_observed
        ? t(language, 'Your planting date is after the latest complete NASA data for this district.', 'আপনার রোপণের তারিখ এই জেলার সর্বশেষ পূর্ণ নাসা তথ্যের পরে।')
        : t(language, 'There are no complete cached observations in the reported crop window.', 'জানানো ফসলের সময়ে পূর্ণ সংরক্ষিত পর্যবেক্ষণ নেই।');
      return `<p>${message} ${window.latest_observed ? esc(window.latest_observed) + ' · ' : ''}<a href="#climate">${t(language, 'View district weather history', 'জেলার আবহাওয়ার ইতিহাস দেখুন')}</a></p>`;
    }
    return `<p><b>${t(language, 'Observed weather during your crop window', 'ফসলের সময়ে পর্যবেক্ষিত আবহাওয়া')}</b> · ${esc(window.start)} → ${esc(window.end)} · NASA POWER</p>
      <ul>${[['T2M_MAX','Highest daily temperature','সর্বোচ্চ দৈনিক তাপমাত্রা'],['T2M_MIN','Lowest daily temperature','সর্বনিম্ন দৈনিক তাপমাত্রা'],['PRECTOTCORR','Total rainfall','মোট বৃষ্টি']].map(([key,en,bn])=>{
        const metric=window.metrics[key];
        return `<li>${t(language,en,bn)} · ${Number.isFinite(metric.value)?esc(metric.value.toFixed(1)+' '+metric.unit):t(language,'Incomplete observations','অসম্পূর্ণ পর্যবেক্ষণ')}</li>`;
      }).join('')}</ul>`;
  }

  function vulnerability(assessment, language, occupancy) {
    const checks = assessment?.checks || [];
    const stage = assessment?.stage ? human(assessment.stage) : t(language, 'unknown', 'জানা নেই');
    const suppliedPeriod = assessment?.assessment_period;
    const period = suppliedPeriod && typeof suppliedPeriod === 'object' ? `${suppliedPeriod.start || '—'} → ${suppliedPeriod.end || '—'}` : (suppliedPeriod || t(language, 'not established', 'নির্ধারিত নয়'));
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
      ${cropWeather(occupancy, language)}
      ${warningExposure(assessment?.observed_warning_exposure,language)}
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
    return (plan.indicators || []).map(item => statusRow(item.label, item.value ?? item.status, item.explanation || '')).join('');
  }

  function comparison(response, language, selectedPlan, reportHref = '#rotations') {
    const plans = [response.baseline_assessment, ...(response.alternatives || [])].filter(Boolean);
    const missingSecond = (response.alternatives || []).length < 2;
    if (response.data_mode === 'local_evidence' && !(response.alternatives || []).length) {
      const baseline = response.baseline_assessment;
      const catalogue = response.evidence_profile?.crop_context?.regional_catalogue || [];
      return `<section class="result-card" aria-labelledby="reported-plan-title">
        <h2 id="reported-plan-title">${t(language, 'Your usual crop order', 'আপনার সাধারণ ফসলের ক্রম')}</h2>
        ${baseline?.segments?.length
          ? `<p>${t(language, 'From the answers you entered.', 'আপনার দেওয়া উত্তর থেকে।')}</p><ol class="plan-crops">${planCrops(baseline, language)}</ol>`
          : `<p>${t(language, 'You haven’t entered a usual crop order. If you have one, you can add it in your field setup.', 'আপনি সাধারণ ফসলের ক্রম দেননি। জানা থাকলে জমির তথ্যে যোগ করতে পারেন।')}</p>`}
        <div class="result-actions"><button type="button" data-result-action="edit-inputs">${t(language, 'Edit field answers', 'জমির তথ্য বদলান')}</button>
          ${reportHref === '#overview' ? `<a href="#overview">${t(language, 'See your weather and crop report', 'আবহাওয়া ও ফসলের রিপোর্ট দেখুন')}</a>` : ''}
        </div>
        <p class="result-limit">${t(language, 'We need verified local planting and harvest guidance to suggest a new crop order for this field.', 'এই জমির জন্য নতুন ফসলের ক্রম সাজাতে স্থানীয় রোপণ ও ফসল তোলার যাচাই করা তথ্য দরকার।')}</p>
        ${reportHref === '#overview' && catalogue.length ? `<details class="result-expand">
          <summary>${t(language, 'See crop calendars collected for your area', 'আপনার এলাকার সংগৃহীত ফসলের ক্যালেন্ডার দেখুন')}</summary>
          <p>${t(language, 'These are reference calendars. Ask a local agriculture officer which dates and crops suit your field.', 'এগুলো তথ্যসূত্রের ক্যালেন্ডার। আপনার জমির জন্য উপযুক্ত ফসল ও তারিখ স্থানীয় কৃষি কর্মকর্তার কাছে জেনে নিন।')}</p>
          <ul>${catalogue.map(crop => `<li>${esc(crop.crop_label)}${crop.seasons?.length ? ` · ${esc(crop.seasons.join(', '))}` : ''}</li>`).join('')}</ul>
        </details>` : ''}
      </section>`;
    }
    const periodLine = `${response.comparison_period?.start ? response.comparison_period.start+' → '+response.comparison_period.end+' · ' : ''}${response.comparison_period?.explanation || ''}${response.comparison_period?.policy_id ? ` · ${response.comparison_period.policy_id}${response.comparison_period.policy_version ? ` ${response.comparison_period.policy_version}` : ''}` : ''}`;
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
          <p class="plan-card__period">${plan.completion_date ? t(language, 'Completes', 'শেষ') : t(language,'Completion date','শেষ হওয়ার তারিখ')} <b>${esc(plan.completion_date || t(language,'not established','নির্ধারিত নয়'))}</b> · ${plan.role === 'baseline' ? t(language, 'Flexible segments', 'নমনীয় অংশ') : `${(plan.steps || []).length}/3 ${t(language, 'future steps', 'ধাপ')}`}</p>
          <ul class="plan-crops plan-crops--compact">${planCrops(plan, language)}</ul>
          <div class="status-stack">${indicatorRows(plan)}</div>
          <details class="result-expand plan-card__details">
            <summary>${t(language, 'View details', 'বিস্তারিত দেখুন')}</summary>
            <div class="status-stack status-stack--muted">${(plan.indicators || []).map(item => `<p><b>${esc(item.label)}</b>: ${esc(item.explanation || '')}${item.unit ? ` (${esc(item.unit)})` : ''}</p>`).join('')}</div>
          </details>
          ${plan.role !== 'baseline' ? `<button type="button" data-result-plan="${esc(plan.plan_id)}" aria-pressed="${plan.plan_id === selectedPlan}">${t(language, 'View operations timeline', 'টাইমলাইন দেখুন')}</button><button type="button" data-result-save="${esc(plan.plan_id)}">${t(language, 'Save plan snapshot', 'পরিকল্পনার কপি সংরক্ষণ')}</button>` : ''}
        </article>`;
      }).join('')}${missingSecond && !(response.alternatives||[]).length ? `<article class="plan-card plan-card--missing"><h3>${t(language,'First alternative unavailable','প্রথম বিকল্প অনুপলব্ধ')}</h3><p>${t(language,'No supported three-step alternative is ready. See the missing rule definitions below.','সমর্থিত তিন ধাপের বিকল্প প্রস্তুত নয়। নিচে অনুপস্থিত নিয়মের সংজ্ঞা দেখুন।')}</p></article>` : ''}${missingSecond ? `<article class="plan-card plan-card--missing"><span aria-hidden="true">＋</span><h3>${t(language, 'Second alternative unavailable', 'দ্বিতীয় বিকল্প অনুপলব্ধ')}</h3><p>${t(language, 'No distinct supported plan was supplied, so no filler or clone is shown.', 'সমর্থিত পৃথক পরিকল্পনা না থাকায় কোনো নকল পরিকল্পনা যোগ করা হয়নি।')}</p></article>` : ''}</div>
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

  function chart(series, language = 'en') {
    const values = Array.isArray(series?.values) ? series.values : [];
    const valid = values.filter(value => typeof value === 'number' && Number.isFinite(value));
    if (!valid.length) return `<p class="result-limit">${t(language, 'No usable observations supplied. Missing values are not zero.', 'ব্যবহারযোগ্য তথ্য নেই। অনুপস্থিত মান শূন্য নয়।')}</p>`;
    const labels = Array.isArray(series.dates) && series.dates.length === values.length ? series.dates : (Array.isArray(series.labels) && series.labels.length === values.length ? series.labels : values.map((_, i) => String(i + 1)));
    let min = Math.min(...valid), max = Math.max(...valid);
    const pad = max === min ? Math.max(1, Math.abs(min) * .05) : (max - min) * .05;
    min -= pad; max += pad;
    const x = i => values.length === 1 ? 310 : 58 + i * 512 / (values.length - 1);
    const y = value => 170 - (value - min) / (max - min) * 125;
    let path = '', gap = true;
    const usable = value => typeof value === 'number' && Number.isFinite(value);
    values.forEach((value, i) => { if (!usable(value)) { gap = true; return; } path += `${gap ? 'M' : 'L'}${x(i).toFixed(2)},${y(value).toFixed(2)} `; gap = false; });
    const stride = Math.max(1, Math.ceil(values.length / 6));
    return `<svg class="result-chart" viewBox="0 0 610 225" role="img" aria-label="${esc(series.label)} · ${esc(series.unit)}">
      <title>${esc(series.label)} · ${esc(series.unit)}; ${t(language, 'gaps are missing observations', 'ফাঁক মানে অনুপস্থিত তথ্য')}</title>
      ${[0,1,2,3].map(i => { const value = min + (max - min) * i / 3; return `<line x1="58" x2="570" y1="${y(value)}" y2="${y(value)}"/><text x="51" y="${y(value) + 4}" text-anchor="end">${esc(value.toFixed(1))}</text>`; }).join('')}
      <path d="${path}" fill="none" stroke="currentColor" stroke-width="2.5"/>
      ${values.map((value, i) => usable(value) ? `<circle cx="${x(i)}" cy="${y(value)}" r="3"><title>${esc(labels[i])}: ${esc(value)} ${esc(series.unit)}</title></circle>` : '').join('')}
      ${labels.map((label, i) => i % stride === 0 || i === labels.length - 1 ? `<text x="${x(i)}" y="203" text-anchor="middle">${esc(label)}</text>` : '').join('')}
    </svg><details class="result-expand"><summary>${t(language, 'View chart values', 'চার্টের মান দেখুন')}</summary><div class="table-scroll"><table><thead><tr><th>${t(language, 'Date / supplied order', 'তারিখ / সরবরাহের ক্রম')}</th><th>${esc(series.unit)}</th></tr></thead><tbody>${values.map((value,i) => `<tr><td>${esc(labels[i])}</td><td>${usable(value) ? esc(value) : t(language, 'Missing', 'অনুপস্থিত')}</td></tr>`).join('')}</tbody></table></div></details>`;
  }

  function climatePanel(climate, language, metric, fixture = true) {
    if (!climate || !['complete', 'incomplete'].includes(climate.status) || !Array.isArray(climate.series) || !climate.series.some(series => series && typeof series.key === 'string' && Array.isArray(series.values))) {
      return `<section class="result-card" aria-label="Historical climate"><p class="result-eyebrow">05 · ${t(language, 'CLIMATE HISTORY', 'জলবায়ু ইতিহাস')}</p>${unavailableCard(t(language, 'Historical climate unavailable', 'ঐতিহাসিক জলবায়ু অনুপলব্ধ'), climate?.reason || 'No prepared chart/history payload was supplied.')}</section>`;
    }
    const availableSeries = climate.series.filter(series => series && typeof series.key === 'string' && Array.isArray(series.values));
    const selected = availableSeries.find(series => series.key === metric) || availableSeries[0];
    const stats = (climate.comparison?.statistics || []).map(stat => `<li><b>${esc(human(stat.metric))} · ${esc(stat.window)}</b>: ${esc(String(stat.earlier_mean))} → ${esc(String(stat.recent_mean))} ${esc(stat.unit)} (Δ ${esc(String(stat.delta ?? stat.difference ?? 'Not supplied'))})</li>`).join('');
    return `<section class="result-card" aria-labelledby="climate-title">
      <div class="result-section-heading">
        <div>
          <p class="result-eyebrow">05 · ${t(language, 'HISTORICAL WEATHER', 'ঐতিহাসিক আবহাওয়া')}</p>
          <h2 id="climate-title">${t(language, 'Regional context, not a field measurement', 'আঞ্চলিক প্রেক্ষাপট, জমির মাপ নয়')}</h2>
        </div>
        ${badge(fixture ? 'fixture' : climate.status, fixture ? t(language, 'Example data', 'নমুনা তথ্য') : t(language, 'Supplied historical evidence', 'সরবরাহ করা ঐতিহাসিক প্রমাণ'))}
      </div>
      <div class="chart-tabs" role="group" aria-label="Climate metric">${availableSeries.map(series => `<button type="button" data-result-metric="${esc(series.key)}" aria-pressed="${series.key === selected.key}">${esc(series.key === 'precipitation' ? t(language, 'Rainfall', 'বৃষ্টিপাত') : t(language, 'Temperature', 'তাপমাত্রা'))}</button>`).join('')}</div>
      <div class="chart-header"><div><small>${esc(selected.statistic)}</small><h3>${esc(selected.label)}</h3></div><b>${esc(selected.unit)}</b></div>
      <div class="chart-frame">${chart(selected, language)}</div>
      <div class="chart-meta">
        <span>${esc(climate.period.start)} → ${esc(climate.period.end)}</span>
        <span>${esc(climate.time_standard)}</span>
        <span>${esc(climate.missingness)}</span>
        <span>${esc(climate.comparison?.earlier || t(language, 'Not supplied', 'দেওয়া হয়নি'))} → ${esc(climate.comparison?.recent || t(language, 'Not supplied', 'দেওয়া হয়নি'))}</span>
      </div>
      <p class="chart-finding">${esc(climate.comparison?.finding || t(language, 'Not supplied', 'দেওয়া হয়নি'))}</p>
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
        ${(response.sources || []).map(source => `<article><h3>${esc(source.provider)}</h3><dl><dt>Dataset/version</dt><dd>${esc(source.product_version)}</dd><dt>Period</dt><dd>${esc(source.period)}</dd><dt>Spatial support</dt><dd>${esc(source.spatial_support)}</dd><dt>QA</dt><dd>${esc(source.qa)}</dd></dl><a href="${esc(sourceUrl(source.url))}" target="_blank" rel="noopener">Official documentation ↗</a></article>`).join('')}
        <p><b>Versions:</b> contract ${esc(response.versions?.contract || 'unknown')} · catalogue ${esc(response.versions?.catalogue || 'unknown')} · method ${esc(response.versions?.method || 'unknown')}</p>
      </details>
    </section>`;
  }

  function evidenceProfile(response, language) {
    const p=response.evidence_profile;
    if(!p)return '';
    const context=p.crop_context,counts=p.counts;
    return `<section class="result-card" aria-labelledby="local-evidence-title"><p class="result-eyebrow">${t(language,'YOUR LOCAL DATA PIPELINE','আপনার স্থানীয় তথ্য প্রক্রিয়া')}</p><h2 id="local-evidence-title">${t(language,'Your inputs and evidence are connected','আপনার ইনপুট ও প্রমাণ সংযুক্ত হয়েছে')}</h2><p>${t(language,'This report uses your saved field inputs, the matching BAMIS source region and archived NASA POWER weather. Evidence is available; crop plans remain incomplete until the required rules are defined.','এই রিপোর্টে সংরক্ষিত জমির তথ্য, সংশ্লিষ্ট বামিস উৎসের অঞ্চল ও নাসা পাওয়ারের আবহাওয়া ব্যবহার করা হয়েছে। প্রমাণ পাওয়া গেছে; প্রয়োজনীয় নিয়ম নির্ধারিত না হওয়া পর্যন্ত ফসল পরিকল্পনা অসম্পূর্ণ থাকবে।')}</p>
      <div class="result-chip-row">${infoChip('Crop evidence',counts.crops+' labels / '+counts.calendars+' calendars')}${infoChip('Source entries',counts.calendar_entries)}${infoChip('Daily NASA rows',counts.weather_daily??0,'42 representative points; no field averaging')}${infoChip('BAMIS region',context.region_label,context.scientific_applicability)}${infoChip('Active reviewed rules',p.active_reviewed_rules)}</div>
      <p>${t(language,'Storage','সংরক্ষণ')}: ${esc(p.storage)} · ${t(language,'Report ID','রিপোর্ট আইডি')}: <code>${esc(response.result_id||'—')}</code></p>
      <details class="result-expand"><summary>${t(language,'How each input is used','প্রতিটি ইনপুটের ব্যবহার')}</summary>${(p.input_usage||[]).map(i=>`<p><code>${esc(i.field)}</code> — ${esc(i.usage)}</p>`).join('')}</details>
      <details class="result-expand"><summary>${t(language,'Current crop: matched source calendars','বর্তমান ফসল: মিলে যাওয়া উৎস ক্যালেন্ডার')} (${context.current_crop_calendars.length})</summary>${context.current_crop_calendars.length?context.current_crop_calendars.map(c=>`<article><h3>${esc(c.season_label)} · ${esc(c.rice_system_label||'system not established')}</h3><p><code>${esc(c.calendar_id)}</code> · ${esc(c.source_id)} · page ${esc(c.source_page)}</p><p>Printed life span: ${esc(c.printed_life_span.min)}–${esc(c.printed_life_span.max)} days. Origin/end events: unresolved; not a field-clearance duration.</p>${c.example_source_column?`<p>Source stage: ${esc(c.example_source_column.growth_stage)} · printed month ${esc(c.example_source_column.printed_month)} · printed week ${esc(c.example_source_column.printed_week)}. No calendar dates inferred.</p><p>Printed normals (not tolerance thresholds): ${esc(JSON.stringify(c.example_source_column.printed_weather_normals))}</p>`:''}</article>`).join(''):`<p>${t(language,'No matching crop calendar was collected for this region. No other region was substituted.','এই অঞ্চলে মিলে যাওয়া ফসলের ক্যালেন্ডার সংগ্রহ করা হয়নি। অন্য অঞ্চল বসানো হয়নি।')}</p>`}</details>
      <details class="result-expand"><summary>${t(language,'Regional crop evidence inventory — not recommendations','আঞ্চলিক ফসলের প্রমাণের তালিকা — পরামর্শ নয়')}</summary><div class="table-scroll"><table><thead><tr><th>Crop</th><th>Source calendars</th><th>Printed seasons</th><th>Decision status</th></tr></thead><tbody>${context.regional_catalogue.map(c=>`<tr><td>${esc(c.crop_label)}</td><td>${c.calendar_count}</td><td>${esc(c.seasons.join(', ')||'Not collected')}</td><td>Not assessed</td></tr>`).join('')}</tbody></table></div></details>
      <details class="result-expand"><summary>${t(language,'How crop and NASA metrics are joined','ফসল ও নাসার পরিমাপক যেভাবে যুক্ত হয়')}</summary><div class="table-scroll"><table><thead><tr><th>BAMIS field</th><th>NASA parameter</th><th>Comparable now?</th><th>Missing definition</th></tr></thead><tbody>${p.metric_bridge.map(m=>`<tr><td>${esc(m.bamis_field)}</td><td>${esc(m.nasa_parameter||'No direct counterpart')}</td><td>${m.evaluable_now?'Yes':'No'}</td><td>${esc(m.missing_information)}</td></tr>`).join('')}</tbody></table></div></details>
      <details class="result-expand"><summary>${t(language,'Weather over your reported field-occupancy dates','আপনার জানানো জমি ব্যবহারের সময়ের আবহাওয়া')}</summary><p>${t(language,'This is a reported-date context, not a reviewed crop stage. Only locally cached dates are calculated; missing days or future dates are not replaced by forecasts.','এটি জানানো তারিখের প্রেক্ষাপট, পর্যালোচিত ফসলের পর্যায় নয়। শুধু স্থানীয়ভাবে সংরক্ষিত তারিখের হিসাব হয়; অনুপস্থিত বা ভবিষ্যৎ তারিখে পূর্বাভাস বসানো হয় না।')}</p><pre>${esc(JSON.stringify(response.climate.reported_occupancy_window,null,2))}</pre></details><details class="result-expand"><summary>${t(language,'Model and training status','মডেল ও প্রশিক্ষণের অবস্থা')}</summary><p>${esc(p.model.regression_readiness)}</p><p>${esc(p.model.tuning)}</p></details>
    </section>`;
  }

  function trialReplay(replay, language) {
    if (replay?.status !== 'historical_case_available') return '';
    const metrics = [
      ['T2M_MAX', 'Highest daily maximum (°C)', 'সর্বোচ্চ দৈনিক তাপমাত্রা (°C)'],
      ['T2M_MIN', 'Lowest daily minimum (°C)', 'সর্বনিম্ন দৈনিক তাপমাত্রা (°C)'],
      ['PRECTOTCORR', 'Total rain (mm)', 'মোট বৃষ্টি (মিমি)']
    ];
    return `<section class="result-card" aria-label="${t(language, 'Historical rotation comparison', 'ঐতিহাসিক ফসল আবর্তন তুলনা')}">
      <h2>${t(language, 'What farmers tried in Bogura', 'বগুড়ায় কৃষকেরা যা চাষ করেছিলেন')}</h2>
      <p>${t(language, 'Published field study · 2015–16', 'প্রকাশিত মাঠ গবেষণা · ২০১৫–১৬')}</p>
      <div class="result-chip-row" style="margin-block:1rem">
      ${replay.patterns.map(pattern => {
        const control = pattern.role === 'trial_control';
        const names = {'Mustard':'সরিষা','Boro rice':'বোরো ধান','Transplanted Aus rice':'রোপা আউশ ধান','Mungbean':'মুগ ডাল'};
        const crops = pattern.crops.map(crop => language === 'bn' ? names[crop.crop] || crop.crop : crop.crop);
        const sequence = control ? t(language, 'Fallow → Boro rice → Fallow', 'পতিত → বোরো ধান → পতিত') : crops.join(' → ');
        return infoChip(control ? t(language, 'Usual practice in the trial', 'পরীক্ষায় প্রচলিত চাষ') : t(language, 'Other crops tested', 'পরীক্ষায় অন্য ফসল'), sequence);
      }).join('')}
      </div>
      <p class="result-limit">${t(language, 'These crops were grown at the research site. For records matched to your district and crop, open your field report.', 'এই ফসলগুলো গবেষণার জমিতে চাষ করা হয়েছিল। আপনার জেলা ও ফসলের তথ্য দেখতে জমির রিপোর্ট খুলুন।')} <a href="#overview">${t(language, 'Open field report', 'জমির রিপোর্ট খুলুন')}</a></p>
      <details class="result-expand"><summary>${t(language, 'See planting dates, harvest dates and weather', 'রোপণ, ফসল তোলা ও আবহাওয়া দেখুন')}</summary>
      <p>${esc(replay.site)} · ${esc(formatDate(replay.horizon.start))} → ${esc(formatDate(replay.horizon.end))} · NASA POWER · ${esc(replay.grid_id)}</p>
      ${replay.patterns.map(pattern => `<article>
        <h3>${esc(pattern.id)}</h3>
        ${pattern.notes ? `<p>${esc(pattern.notes)}</p>` : ''}
        <div class="table-scroll"><table><thead><tr>
          <th scope="col">${t(language, 'Crop / variety', 'ফসল / জাত')}</th>
          <th scope="col">${t(language, 'Field dates', 'জমির তারিখ')}</th>
          ${metrics.map(([, en, bn]) => `<th scope="col">${t(language, en, bn)}</th>`).join('')}
        </tr></thead><tbody>${pattern.crops.map(crop => `<tr>
          <th scope="row">${esc(crop.crop)} · ${esc(crop.variety)}</th>
          <td>${esc(crop.event)} ${esc(formatDate(crop.start))} → ${esc(crop.harvest ? formatDate(crop.harvest) : t(language, 'Harvest unresolved', 'ফসল তোলার তারিখ অমীমাংসিত'))}</td>
          ${metrics.map(([key]) => `<td>${Number.isFinite(crop.weather[key]?.value) ? esc(crop.weather[key].value.toFixed(1)) : t(language, 'Unavailable', 'অনুপলব্ধ')}</td>`).join('')}
        </tr>`).join('')}</tbody></table></div>
      </article>`).join('')}
      <p><a href="${esc(sourceUrl(replay.source_url))}" target="_blank" rel="noopener">${esc(replay.citation)}</a></p>
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
            <label>${t(language, 'Crop', 'ফসল')}<select id="intended-crop"><option value="">${t(language, 'Choose crop', 'ফসল বেছে নিন')}</option>${(globalThis.STS_INTAKE?.crops||[]).map(c=>`<option value="${esc(c.id)}">${esc(language==='bn'?c.bn:c.en)}</option>`).join('')}</select></label>
            <label>${t(language, 'Planting date', 'রোপণের তারিখ')}<input id="intended-date" type="date"></label>
          </div>
          <button type="button" data-result-action="intended-check">${t(language, 'Check collected evidence', 'সংগৃহীত প্রমাণ দেখুন')}</button>
          <p class="result-limit" id="intended-status">${esc(response.intended_crop_assessment?.reason || 'Unavailable')}</p>
        </article>
      </div>
    </section>`;
  }

  function receiptPanel(data, language) {
    const example = isExample(data);
    return `<section class="result-card result-receipt" aria-labelledby="receipt-title">
      <div>
        <p class="result-eyebrow">08 · ${t(language, 'PRINT & JSON RECEIPT', 'প্রিন্ট ও JSON')}</p>
        <h2 id="receipt-title">${example ? t(language, 'Keep the same example result', 'এই নমুনার একই তথ্য রাখুন') : t(language, 'Keep your result and evidence', 'ফলাফল ও প্রমাণ সংরক্ষণ করুন')}</h2>
        <p>${example ? t(language, 'The export preserves the fixture label, statuses, limitations and source metadata.', 'রপ্তানিতে নমুনা লেবেল, অবস্থা, সীমাবদ্ধতা ও উৎস থাকবে।') : t(language, 'Export preserves the supplied result, statuses, sources and limitations.', 'রপ্তানিতে সরবরাহ করা ফলাফল, অবস্থা, উৎস ও সীমা থাকবে।')}</p>
        <p class="receipt-note"><b>Fingerprints:</b> ${esc(data.response.result_fingerprint ?? data.response.fingerprints?.result ?? 'Not supplied; no identifier invented')}.</p>
      </div>
      <div class="result-actions result-actions--end">
        <button type="button" class="primary" data-result-action="download-receipt">${example ? t(language, 'Download example JSON', 'নমুনা JSON ডাউনলোড') : t(language, 'Download result JSON', 'ফলাফলের JSON ডাউনলোড')}</button>
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
    let genuine = null;
    let viewGeneration = 0;
    let selectedPlan = null;
    let climateMetric = 'precipitation';
    let weatherBundle = null, weatherLoading = false, weatherError = false, weatherDistrict = null, weatherMetric = 'T2M';
    let scenario = null;
    let publicTrial = null;
    let trialOpen = false;
    let trialState = 'idle';
    function loadPublicTrial() {
      if (trialState !== 'idle') return;
      trialState = 'loading';
      fetch('/data/bogura-trial.json')
        .then(response => {
          if (!response.ok) throw new Error('Trial unavailable');
          return response.json();
        })
        .then(trial => {
          if (trial.status !== 'historical_case_available') throw new Error('Invalid trial');
          publicTrial = trial;
          trialState = 'ready';
        })
        .catch(() => { trialState = 'error'; })
        .finally(rerender);
    }

    function trialPanel(language) {
      const toggle = `<button type="button" data-result-action="toggle-trial" aria-expanded="${trialOpen}" aria-controls="rotation-study">${trialOpen
        ? t(language, 'Hide example', 'উদাহরণ লুকান')
        : t(language, 'See an example from a field study', 'মাঠ গবেষণার একটি উদাহরণ দেখুন')}</button>`;
      return `<section class="result-card">${toggle}<div id="rotation-study"${trialOpen ? '' : ' hidden'}>${trialOpen ? trialContent(language) : ''}</div></section>`;
    }

    function trialContent(language) {
      if (publicTrial) return trialReplay(publicTrial, language);
      if (trialState === 'error') {
        return unavailableCard(
          t(language, 'Historical trial could not load', 'ঐতিহাসিক মাঠপরীক্ষা লোড হয়নি'),
          t(language, 'Try loading it again.', 'আবার লোড করার চেষ্টা করুন।'),
          `<button data-result-action="retry-trial">${t(language, 'Retry', 'আবার চেষ্টা করুন')}</button>`
        );
      }
      return `<p role="status">${t(language, 'Loading historical trial…', 'ঐতিহাসিক মাঠপরীক্ষা লোড হচ্ছে…')}</p>`;
    }
    let restoring=false;
    let restored=false;
    let snapshot = null;
    try { const item=JSON.parse(localStorage.getItem('sts-plan-snapshot-v1')); if(item?.version===1&&!item.example&&!isExample(item.data)&&item.data?.request&&['complete','incomplete'].includes(item.data?.response?.status)&&Array.isArray(item.data.response.alternatives)&&(item.plan_id==='evidence-report'&&item.data.response.analysis_mode==='source_evidence_report'||item.data.response.alternatives.some(p=>p.plan_id===item.plan_id&&planHasThreeSteps(p))))snapshot=item; } catch {}
    function saveSnapshot(planId) {
      const active=data||genuine;
      const plan=planId==='evidence-report'&&!isExample(active)&&active?.response?.report_status==='complete'?{label:'Field evidence report'}:active?.response?.alternatives?.find(p=>p.plan_id===planId&&planHasThreeSteps(p));
      if(!plan)return;
      snapshot={version:1,plan_id:planId,label:text(plan.label),saved_at:new Date().toISOString(),example:isExample(active),data:JSON.parse(JSON.stringify(active))};
      try {localStorage.setItem('sts-plan-snapshot-v1',JSON.stringify(snapshot));toast('Plan snapshot saved in this browser.');} catch {toast('Snapshot kept for this session; browser storage is unavailable.');}
      navigate('saved');
    }
    function renderRoute(route,request,language='en') {
      if(route==='climate'&&!weatherBundle&&!weatherLoading&&!weatherError){weatherLoading=true;globalThis.STS_CLIMATE_HISTORY.load().then(bundle=>{weatherBundle=bundle;weatherLoading=false;rerender();}).catch(()=>{weatherError=true;weatherLoading=false;rerender();});}
      const active=data||(genuine&&JSON.stringify(genuine.request)===JSON.stringify(request)?genuine:null);
      let html=globalThis.STS_WORKSPACE_PAGES.render(route,{ui:{chart,comparison,trialPanel,evidencePanel,evidenceProfile,operationTimeline,genuineSummary},language,active,request,selectedPlan,metric:weatherMetric,weather:globalThis.STS_CLIMATE_HISTORY,bundle:weatherBundle,district:weatherDistrict??request?.location?.district_id,saved:snapshot,scenario});
      if(route==='climate'&&weatherError)html=html.replace(/<p role="status">[\s\S]*?<\/p>/,'<p role="alert">Local weather history could not load. / স্থানীয় আবহাওয়ার তথ্য লোড হয়নি।</p><button data-result-action="retry-weather">Retry / আবার চেষ্টা করুন</button>');
      return html;
    }
    async function runScenario() {
      if(data){toast('Example inputs cannot be submitted to the real service. Use your own field inputs.');return;}
      const original=options.getSubmission?.();
      if(!original)return;
      const request=JSON.parse(JSON.stringify(original));
      request.irrigation={...request.irrigation,access:document.getElementById('whatif-water').value};
      request.priority=document.getElementById('whatif-priority').value;
      const limits=document.getElementById('whatif-seasonal-limitations').value;
      const seasons=[...document.querySelectorAll('[data-whatif-season]:checked')].map(el=>el.value);
      request.irrigation.seasonal_limitations=request.irrigation.access==='rainfed'?'not_applicable':limits;
      request.irrigation.limited_seasons=request.irrigation.access!=='rainfed'&&limits==='seasonal'?seasons:[];
      if(request.irrigation.access!=='rainfed'&&(!['none','seasonal'].includes(limits)||limits==='seasonal'&&!seasons.length)){
        scenario={request,state:'invalid_input',response:{status:'invalid_input',reason:'Choose seasonal irrigation limits and, when applicable, at least one limited season. / মৌসুমি সেচের সীমা এবং প্রযোজ্য হলে অন্তত একটি মৌসুম বেছে নিন।'}};rerender();return;
      }
      scenario={request,state:'loading'};rerender();
      const token=viewGeneration;
      // A scenario never runs through the fixture transport or changes original inputs.
      const service=globalThis.STS_RESULT_ADAPTER.create({endpoints:globalThis.STS_RESULT_ENDPOINTS||{}});
      const result=await service.requestPlanning({...request,request_kind:'scenario'});
      if(token!==viewGeneration)return;
      scenario={request,state:result.state,response:result.response};rerender();
    }

    async function activateFixture(id) {
      viewGeneration += 1;
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
    function deactivateFixture() { viewGeneration += 1; data = null; selectedPlan = null; adapter.disableFixture(); leaveFixtureMode?.(); }
    function invalidate() { viewGeneration += 1; scenario=null; weatherDistrict=null; genuine = null; data = null; selectedPlan = null; adapter.disableFixture(); leaveFixtureMode?.(); }
    function isFixture() { return Boolean(data); }

    function renderData(data, language = 'en', options = {}) {
      if (!data) return '';
      const example = isExample(data);
      const showFixtureBanner = example && options.showFixtureBanner !== false;
      const banner = showFixtureBanner ? fixturePicker(data.fixture_id, language) : '';
      const response = data.response;
      if (!['complete', 'incomplete'].includes(response.status)) {
        const title = `${example ? t(language, 'Example: ', 'নমুনা: ') : ''}${response.status === 'invalid_input' ? t(language, 'Check your inputs', 'আপনার তথ্য যাচাই করুন') : response.status === 'error' ? t(language, 'Service request failed', 'সেবার অনুরোধ ব্যর্থ') : t(language, 'Planning unavailable', 'পরিকল্পনা অনুপলব্ধ')}`;
        return `<div class="result-page" data-no-translate>${banner}<header class="result-page-intro"><h1>${esc(title)}</h1></header>${!example ? genuineSummary(data.request, language, response.status) : ''}${unavailableCard(title, text(response.reason || response.errors?.[0]?.label, language) || t(language, 'No result is available.', 'কোনো ফলাফল পাওয়া যায়নি।'), response.recoverable ? '<button type="button" data-result-action="retry">Retry real service</button>' : '')}</div>`;
      }
      const plan = response.alternatives?.find(item => item.plan_id === selectedPlan) || response.alternatives?.[0];
      return `<div class="result-page" data-no-translate>${banner}
        <section class="result-page-intro" aria-label="Result workspace">
          <div>
            <p class="result-eyebrow">SOIL TO STARS · RESULT WORKSPACE</p>
            <h1>${t(language, 'Your field decision, with the evidence beside it.', 'আপনার জমির সিদ্ধান্ত, প্রমাণসহ')}</h1>
            <p>${t(language, 'Plans, timing, reasons and unknowns stay together.', 'পরিকল্পনা, সময়, কারণ ও অজানা তথ্য এক জায়গায়।')}</p>
          </div>
          <div class="result-page-intro__status">${badge(response.report_status==='complete'?'complete':response.status,response.report_status==='complete'?t(language,'Evidence report ready','প্রমাণের রিপোর্ট প্রস্তুত'):response.status)}<span>${esc(response.coverage?.label || '')}</span></div>
        </section>
        ${example ? fieldSummary(data, language) : genuineSummary(data.request, language, response.status)}${restored&&!example?`<p class="result-limit">${t(language,'Restored saved report; generated at','সংরক্ষিত রিপোর্ট দেখানো হচ্ছে; তৈরি হয়েছে')} ${esc(response.generated_at_utc||'—')}. ${t(language,'Generate a new report after changing inputs or source data.','ইনপুট বা উৎসের তথ্য বদলালে নতুন রিপোর্ট তৈরি করুন।')} <button data-result-action="request-planning">${t(language,'Generate fresh report','নতুন রিপোর্ট তৈরি করুন')}</button></p>`:''}${!example&&response.report_status==='complete'?`<div class="result-actions"><button data-result-save="evidence-report">${t(language,'Save evidence report','প্রমাণের রিপোর্ট সংরক্ষণ')}</button></div>`:''}${response.data_mode === 'local_evidence' ? fieldInputsUsed(language, response.evidence_profile?.crop_context) : ''}${vulnerability(response.current_crop_assessment, language, response.climate?.reported_occupancy_window)}${comparison(response, language, selectedPlan)}${plan || example ? operationTimeline(plan, language) : ''}${climatePanel(response.climate, language, climateMetric, example)}<details class="result-card result-expand"><summary>${t(language, 'Sources and technical details', 'উৎস ও কারিগরি বিবরণ')}</summary>${evidenceProfile(response, language)}${evidencePanel(response, language)}</details>${toolsPanel(response, language)}${receiptPanel(data, language)}
      </div>`;
    }

    function renderFixture(language = 'en', options = {}) { return renderData(data, language, options); }

    async function submit(request) {
      restored=false;
      adapter.disableFixture(); leaveFixtureMode?.(); data = null;
      const generation = ++viewGeneration;
      genuine = { request, state: 'loading', response: { status: 'loading', data_mode: 'unavailable' } };
      selectedPlan = null; rerender();
      const result = await adapter.requestPlanning(request);
      if (generation !== viewGeneration || result.ignored) return;
      genuine = { request, state: result.state, response: result.response || { status: 'error', reason: 'Invalid response.' } };
      selectedPlan = genuine.response.alternatives?.find(planHasThreeSteps)?.plan_id || null;
      if(genuine.response.result_id&&typeof window!=='undefined'){try{localStorage.setItem('sts-last-assessment-v1',JSON.stringify({id:genuine.response.result_id,intake:request}));}catch{}}
      rerender();
    }

    async function restore(request) {
      if(restoring||genuine||!request||typeof window==='undefined')return;
      let saved;try{saved=JSON.parse(localStorage.getItem('sts-last-assessment-v1'));}catch{return;}
      if(!saved?.id||!/^[-0-9a-f]{36}$/.test(saved.id)||JSON.stringify(saved.intake)!==JSON.stringify(request))return;
      restoring=true;const token=viewGeneration;
      try{const response=await fetch('/api/results/'+saved.id,{cache:'no-store'});if(!response.ok)return;const body=await response.json();
        const stable=v=>v&&typeof v==='object'?(Array.isArray(v)?v.map(stable):Object.fromEntries(Object.keys(v).sort().map(k=>[k,stable(v[k])]))):v;
        if(token===viewGeneration&&!genuine&&body.result?.data_mode==='local_evidence'&&JSON.stringify(stable(body.intake))===JSON.stringify(stable(request))){genuine={request,state:body.result.status,response:body.result};restored=true;rerender();}
      }catch{}finally{restoring=false;}
    }

    function renderGenuine(request, language = 'en') {
      if(!genuine&&!restoring)void restore(request);
      if (genuine && JSON.stringify(genuine.request) === JSON.stringify(request)) {
        if (genuine.state === 'loading') return `<div class="result-page" data-no-translate aria-busy="true">${genuineSummary(request, language, 'loading')}<p role="status">${t(language, 'Loading your assessment…', 'আপনার মূল্যায়ন লোড হচ্ছে…')}</p></div>`;
        return renderData(genuine, language) + (!['complete','incomplete'].includes(genuine.response.status) ? `<div class="result-page" data-no-translate>${vulnerability({status:'incomplete',crop_label:request?.current?.crop_id,checks:[{outcome:'unknown',label:{en:'Heat exposure — not assessed',bn:'তাপের প্রভাব — মূল্যায়ন হয়নি'},missing_information:t(language,'Planting date, crop stage and reviewed temperature limits are required.','রোপণের তারিখ, ফসলের পর্যায় ও পর্যালোচিত তাপমাত্রার সীমা প্রয়োজন।')},{outcome:'unknown',label:{en:'Rainfall / water exposure — not assessed',bn:'বৃষ্টি / পানির প্রভাব — মূল্যায়ন হয়নি'},missing_information:t(language,'Stage-specific water requirements and irrigation context are required.','পর্যায়ভিত্তিক পানির চাহিদা ও সেচের প্রেক্ষাপট প্রয়োজন।')}],limitation:t(language,'Exposure calculations require reviewed crop-stage rules and matching weather data. No live diagnosis is available.','প্রভাবের হিসাবের জন্য পর্যালোচিত ফসলের পর্যায়ের নিয়ম ও সংশ্লিষ্ট আবহাওয়া প্রয়োজন। সরাসরি রোগ নির্ণয় নেই।')},language)}<a href="#climate">${t(language,'Explore NASA weather history','নাসার আবহাওয়ার ইতিহাস দেখুন')} ↗</a></div>` : '');
      }
      return `<div class="result-page" data-no-translate>
        <section class="result-page-intro" aria-label="Result workspace">
          <div>
            <p class="result-eyebrow">SOIL TO STARS · RESULT WORKSPACE</p>
            <h1>${t(language, 'Your field inputs are ready.', 'আপনার জমির তথ্য প্রস্তুত।')}</h1>
            <p>${t(language, 'Your answers are preserved. Generate a local evidence report to connect them to the crop catalogue and NASA archive.', 'আপনার উত্তর সংরক্ষিত আছে। ফসলের তালিকা ও নাসার সংরক্ষিত তথ্যের সাথে যুক্ত করতে স্থানীয় রিপোর্ট তৈরি করুন।')}</p>
          </div>
          ${badge('unavailable')}
        </section>
        ${genuineSummary(request, language)}
        ${vulnerability({status:'incomplete',crop_label:request?.current?.crop_id||t(language,'No current crop supplied','বর্তমান ফসল দেওয়া হয়নি'),checks:[{outcome:'unknown',label:{en:'Heat exposure — not assessed',bn:'তাপের প্রভাব — মূল্যায়ন হয়নি'},missing_information:t(language,'Needs planting date, crop stage, reviewed crop threshold and a matching weather window.','রোপণের তারিখ, ফসলের পর্যায়, পর্যালোচিত সীমা ও সংশ্লিষ্ট আবহাওয়ার সময় প্রয়োজন।')},{outcome:'unknown',label:{en:'Rainfall / water exposure — not assessed',bn:'বৃষ্টি / পানির প্রভাব — মূল্যায়ন হয়নি'},missing_information:t(language,'Needs stage-specific water rules and irrigation context; historical rainfall alone cannot determine crop risk.','পর্যায়ভিত্তিক পানির নিয়ম ও সেচের প্রেক্ষাপট প্রয়োজন; শুধু ঐতিহাসিক বৃষ্টি দিয়ে ফসলের ঝুঁকি নির্ধারণ হয় না।')}],limitation:t(language,'Historical context is available in Climate insights. Crop exposure calculations are not connected; no live risk or diagnosis is claimed.','জলবায়ুর পাতায় ঐতিহাসিক প্রেক্ষাপট আছে। ফসলের প্রভাবের গণনা সংযুক্ত নয়; সরাসরি ঝুঁকি বা রোগ নির্ণয়ের দাবি করা হচ্ছে না।')}, language)}
        <p><a href="#climate">${t(language,'Explore real NASA weather history','নাসার প্রকৃত আবহাওয়ার ইতিহাস দেখুন')} ↗</a></p>
        ${unavailableCard(
          t(language, 'Generate your local report', 'আপনার স্থানীয় রিপোর্ট তৈরি করুন'),
          t(language, 'The local service saves your inputs and retrieves matching crop and weather evidence. Missing crop rules remain explicit; no demonstration data is substituted.', 'স্থানীয় সেবা আপনার ইনপুট সংরক্ষণ করে সংশ্লিষ্ট ফসল ও আবহাওয়ার প্রমাণ সংগ্রহ করে। অনুপস্থিত নিয়ম স্পষ্ট থাকে; নমুনা তথ্য বসানো হয় না।'),
          `${request ? `<button type="button" data-result-action="request-planning">${t(language, 'Generate local report', 'স্থানীয় রিপোর্ট তৈরি করুন')}</button>` : ''}`
        )}
      </div>`;
    }

    function downloadReceipt() {
      const active = data || genuine;
      if (!active || active.state === 'loading') return;
      const blob = new Blob([JSON.stringify(receipt(active), null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob), anchor = document.createElement('a');
      anchor.href = url; anchor.download = isExample(active) ? `soil-to-stars-${active.fixture_id}-example.json` : 'soil-to-stars-result.json'; anchor.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      toast(isExample(active) ? 'Example receipt downloaded with fixture labels.' : 'Result receipt downloaded with supplied evidence.');
    }

    function handleClick(button) {
      if(button.dataset.resultSave){saveSnapshot(button.dataset.resultSave);return true;}
      if(button.dataset.weatherMetric){weatherMetric=button.dataset.weatherMetric;rerender();return true;}
      if (button.dataset.resultMetric) { climateMetric = button.dataset.resultMetric; rerender(); return true; }
      if (button.dataset.resultPlan) { selectedPlan = button.dataset.resultPlan; rerender(); return true; }
      switch (button.dataset.resultAction) {
        case 'run-scenario': void runScenario(); return true;
        case 'reset-scenario': scenario=null; viewGeneration+=1; rerender(); return true;
        case 'toggle-trial':
          trialOpen = !trialOpen;
          if (trialOpen) loadPublicTrial();
          rerender();
          document.querySelector('[data-result-action="toggle-trial"]')?.focus();
          return true;
        case 'retry-trial': trialState='idle'; loadPublicTrial(); rerender(); return true;
        case 'retry-weather': weatherError=false; rerender(); return true;
        case 'download-saved': {
          if(!snapshot)return true;
          const url=URL.createObjectURL(new Blob([JSON.stringify(snapshot,null,2)],{type:'application/json'}));
          const a=document.createElement('a');a.href=url;a.download=snapshot.example?'soil-to-stars-saved-example.json':'soil-to-stars-saved-result.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);return true;
        }
        case 'remove-snapshot': snapshot=null;try{localStorage.removeItem('sts-plan-snapshot-v1');}catch{}rerender();return true;
        case 'edit-inputs': deactivateFixture(); navigate('profile'); return true;
        case 'exit-fixture': deactivateFixture(); navigate('profile'); return true;
        case 'download-inputs':
          if(typeof location!=='undefined'&&location.hash==='#saved'&&snapshot){
            const url=URL.createObjectURL(new Blob([JSON.stringify(snapshot.data.request,null,2)],{type:'application/json'}));
            const a=document.createElement('a');a.href=url;a.download='soil-to-stars-saved-inputs.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
          }else downloadInputs();
          return true;
        case 'download-receipt': downloadReceipt(); return true;
        case 'print': window.print(); return true;
        case 'intended-check': {
          const status = document.querySelector('#intended-status');
          if(status){
            const crop=document.querySelector('#intended-crop')?.value,day=document.querySelector('#intended-date')?.value;
            if(!crop||formatDate(day)==='Not supplied'){status.textContent='Choose a crop and a valid planting date. / ফসল ও সঠিক রোপণের তারিখ দিন।';return true;}
            const context=(genuine||data)?.response?.evidence_profile?.crop_context;
            const collected=context?.regional_catalogue?.find(c=>c.intake_crop_id===crop);
            status.textContent=`${collected?.crop_label||crop}: ${collected?.calendar_count||0} collected source calendar(s) for ${context?.region_label||'this source region'}. Requested planting date: ${day}. Planting feasibility remains unassessed: event-defined crop, soil/water and operation rules are unresolved. No score calculated.`;
          }
          return true;
        }
        case 'request-planning': if (options.getSubmission?.()) void submit(options.getSubmission()); return true;
        case 'retry': if (data) toast('No real endpoint is configured; fixture success was not activated.'); else if (genuine?.request) void submit(genuine.request); return true;
        default: return false;
      }
    }
    function handleChange(target) {
      if(target.id==='whatif-water'){const fields=document.getElementById('whatif-irrigation-fields');if(fields)fields.hidden=target.value==='rainfed';return true;}
      if(target.id==='whatif-seasonal-limitations'){const fields=document.getElementById('whatif-limited-seasons');if(fields)fields.hidden=target.value!=='seasonal';return true;}
      if(target.matches('[data-weather-district]')){weatherDistrict=target.value;rerender();return true;}
      if (target.matches('[data-result-fixture]')) { void activateFixture(target.value); return true; }
      if (target.matches('[data-result-metric]')) { climateMetric = target.dataset.resultMetric; rerender(); return true; }
      return false;
    }
    function setMetric(metric) { climateMetric = metric; rerender(); }

    return { restore, getSaved:()=>snapshot, renderRoute, submit, activateFixture, deactivateFixture, invalidate, isFixture, renderFixture, renderGenuine, handleClick, handleChange, setMetric, downloadReceipt, getData: () => data || genuine };
  }

  return { create, receipt, planHasThreeSteps, genuineSummary, chart, climatePanel, vulnerability, indicatorRows, formatDate };
});
