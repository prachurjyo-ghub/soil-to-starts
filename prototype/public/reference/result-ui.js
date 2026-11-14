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
          <p class="result-summary-meta">${esc(districtLabel(location, language))} · ${location.selection_method === 'map_pin' ? t(language, 'Map pin', 'ম্যাপ পিন') : t(language, 'District weather grid', 'জেলার আবহাওয়া গ্রিড')}</p>
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
          <p class="result-summary-meta">${esc(text(request.location.district_label, language))} · ${esc(human(request.location.selection_method))}</p>
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

  const WARNING_LABELS_BN = {
    'hot-day': 'দিনের সর্বোচ্চ তাপমাত্রা ৩০°সে-এর বেশি',
    'cold-night': 'দিনের সর্বনিম্ন তাপমাত্রা ১০°সে-এর কম',
    'heavy-rain': 'দৈনিক বৃষ্টি ৫০ মিমির বেশি',
  };

  function warningIndicatorLabel(indicator, language) {
    return t(language, indicator.label, indicator.label_bn || WARNING_LABELS_BN[indicator.id] || indicator.label);
  }

  function warningUnavailable(reason, language) {
    if (reason?.startsWith('sowing_date_required')) {
      return t(language, 'Add the planting date to check weather for this crop.', 'এই ফসলের আবহাওয়া যাচাই করতে রোপণের তারিখ দিন।');
    }
    if (reason?.startsWith('crop_window_has_no_cached_observations')) {
      return t(language, 'The saved NASA weather archive has no observations for the crop dates you entered.', 'আপনার দেওয়া ফসলের তারিখের জন্য সংরক্ষিত নাসার আবহাওয়ার পর্যবেক্ষণ নেই।');
    }
    if (reason === 'daily_weather_not_installed') {
      return t(language, 'The daily NASA weather archive is not installed on this device.', 'এই ডিভাইসে নাসার দৈনিক আবহাওয়ার তথ্য ইনস্টল করা নেই।');
    }
    if (reason === 'no_complete_observed_weather') {
      return t(language, 'There are no complete daily observations in the saved NASA weather for this area.', 'এই এলাকার সংরক্ষিত নাসার আবহাওয়ায় পূর্ণ দৈনিক পর্যবেক্ষণ নেই।');
    }
    return t(language, 'The source library has no comparable warning for this crop and region.', 'এই ফসল ও অঞ্চলের জন্য তুলনাযোগ্য সতর্কতা সংগ্রহে নেই।');
  }

  function warningIndicatorChips(indicators, language) {
    return indicators.map(indicator => {
      const count = indicator.matching_days ?? indicator.exceedance_days;
      const value = Number.isInteger(count)
        ? `${count} ${t(language, 'days', 'দিন')}`
        : t(language, 'Incomplete observations', 'অসম্পূর্ণ পর্যবেক্ষণ');
      return infoChip(warningIndicatorLabel(indicator, language), value, `${indicator.valid_days}/${indicator.expected_days} ${t(language, 'days with data', 'দিনের তথ্য আছে')}`);
    }).join('');
  }

  function warningSource(exposure, language) {
    const reference = exposure.reference;
    return `<a href="${esc(sourceUrl(reference.source_url))}" target="_blank" rel="noopener">BAMIS · ${esc(reference.section)} · ${t(language, 'page', 'পৃষ্ঠা')} ${esc(reference.page)}</a>`;
  }

  function warningExposure(exposure, language) {
    if (!exposure) return '';
    if (exposure.status === 'unavailable') return `<p>${warningUnavailable(exposure.reason, language)}</p>`;
    return `<section class="warning-observations">
      <h3>${t(language, 'Daily weather compared with published warnings', 'প্রকাশিত সতর্কতার সঙ্গে দৈনিক আবহাওয়ার তুলনা')}</h3>
      <p>${esc(formatDate(exposure.start))} → ${esc(formatDate(exposure.end))} · NASA POWER</p>
      <div class="result-chip-row">${warningIndicatorChips(exposure.indicators, language)}</div>
      ${exposure.reference.id === 'bamis-chattogram-rabi-chilli-rain-p1' ? `<p>${t(language, 'The Rabi chilli calendar gives this rain range for flowering, fruiting and harvest. These counts cover the dates you entered. Your crop stage and field risk remain unknown.', 'রবি মরিচের ক্যালেন্ডারে ফুল, ফল ও ফসল তোলার পর্যায়ে এই বৃষ্টির পরিমাণ উল্লেখ আছে। গণনাটি আপনার দেওয়া তারিখের জন্য। ফসলের পর্যায় ও জমির ঝুঁকি অজানা।')}</p>` : ''}
      <details class="result-expand">
        <summary>${t(language, 'Source and matching dates', 'উৎস ও মিলে যাওয়া তারিখ')}</summary>
        ${warningSource(exposure, language)}
        ${exposure.indicators.map(i => `<p><b>${esc(warningIndicatorLabel(i, language))}</b> · ${esc(i.dates.join(', ') || t(language, 'No matching dates in the available observations', 'উপলব্ধ তথ্যে মিলে যাওয়া তারিখ নেই'))}</p>`).join('')}
        <p>${esc(exposure.meaning)} ${esc(exposure.reference.limitations.join(' '))}</p>
      </details>
    </section>`;
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

  function historicalDateReport(result, language, title, heading = 'h2') {
    if (!result) return '';
    if (result.status !== 'available') {
      const message = result.reason === 'window_exceeds_one_year'
        ? t(language, 'Use a date range of up to one year for this historical comparison.', 'অতীতের সঙ্গে তুলনার জন্য সর্বোচ্চ এক বছরের তারিখ বেছে নিন।')
        : t(language, 'There are no complete archive years for these dates in your district.', 'এই জেলার জন্য একই তারিখের পূর্ণ বছরের তথ্য নেই।');
      return unavailableCard(title, message, '<a href="#climate">' + t(language, 'View district weather history', 'জেলার আবহাওয়ার ইতিহাস দেখুন') + '</a>');
    }
    const fmt = (value, unit) => `${new Intl.NumberFormat(language === 'bn' ? 'bn-BD' : 'en', {maximumFractionDigits: 2}).format(value)} ${unit}`;
    return `<section class="result-card" aria-label="${esc(title)}">
      <${heading}>${esc(title)}</${heading}>
      <p>${esc(formatDate(result.start))} → ${esc(formatDate(result.end))} · NASA POWER · ${result.years_used} ${t(language, 'complete past years from the 2001–2025 archive', '২০০১–২০২৫ আর্কাইভের পূর্ণ বছরের তথ্য')}</p>
      <div class="result-chip-row">
        ${infoChip(t(language, 'Typical highest temperature', 'সাধারণ সর্বোচ্চ তাপমাত্রা'), fmt(result.median.high_c, '°C'))}
        ${infoChip(t(language, 'Typical lowest temperature', 'সাধারণ সর্বনিম্ন তাপমাত্রা'), fmt(result.median.low_c, '°C'))}
        ${infoChip(t(language, 'Typical total rain', 'সাধারণ মোট বৃষ্টি'), fmt(result.median.rain_mm, 'mm'))}
      </div>
      <p>${t(language, 'Typical means the middle value across past years for the same calendar dates. These are historical grid values. Future weather and crop suitability are unknown.', 'একই তারিখে অতীত বছরের মানগুলোর মাঝের মান দেখানো হয়েছে। এগুলো পুরোনো গ্রিড তথ্য। ভবিষ্যতের আবহাওয়া ও ফসলের উপযোগিতা অজানা।')}</p>
      <details class="result-expand"><summary>${t(language, 'See each year', 'প্রতি বছরের তথ্য দেখুন')}</summary>
        <div class="table-scroll"><table><thead><tr>
          <th scope="col">${t(language, 'Dates', 'তারিখ')}</th><th scope="col">${t(language, 'High (°C)', 'সর্বোচ্চ (°C)')}</th><th scope="col">${t(language, 'Low (°C)', 'সর্বনিম্ন (°C)')}</th><th scope="col">${t(language, 'Rain (mm)', 'বৃষ্টি (মিমি)')}</th>
        </tr></thead><tbody>${result.samples.map(row => `<tr><td>${esc(row.start)} → ${esc(row.end)}</td><td>${esc(row.high_c)}</td><td>${esc(row.low_c)}</td><td>${esc(row.rain_mm)}</td></tr>`).join('')}</tbody></table></div>
      </details>
    </section>`;
  }

  function calendarName(record, language) {
    const season = record.season === 'Unspecified' || !record.season
      ? t(language, 'Season unspecified', 'মৌসুম উল্লেখ নেই') : record.season;
    return record.rice_system && record.rice_system !== season ? record.rice_system + ' · ' + season : season;
  }

  function calendarDetails(crop, language) {
    const records = crop.calendars || (crop.seasons || []).map(season => ({season}));
    return `<ul class="calendar-records">${records.map(record => {
      const [min, max] = record.life_span_days || [];
      const duration = Number.isFinite(min) && Number.isFinite(max)
        ? `${min === max ? min : min + '–' + max} ${t(language, 'days printed in calendar', 'ক্যালেন্ডারে উল্লেখিত দিন')}`
        : t(language, 'Duration unavailable', 'সময়কাল পাওয়া যায়নি');
      const reference = record.source_id
        ? `<small>${esc(record.source_id)} · ${t(language, 'page', 'পৃষ্ঠা')} ${esc(record.source_page)}</small>` : '';
      return `<li><b>${esc(calendarName(record, language))}</b> · ${esc(duration)} ${reference}</li>`;
    }).join('')}</ul>`;
  }

  function regionalCalendarPanel(response, language, compare) {
    const context = response.evidence_profile?.crop_context;
    const crops = (context?.regional_catalogue || []).filter(crop => crop.calendar_count > 0);
    const title = compare ? t(language, 'Compare local crop calendars', 'স্থানীয় ফসলের ক্যালেন্ডার তুলনা') : t(language, 'Crop calendars for your area', 'আপনার এলাকার ফসলের ক্যালেন্ডার');
    if (!crops.length) return unavailableCard(title, t(language, 'No crop calendars were found for this region in the bundled records.', 'সংরক্ষিত তথ্যে এই অঞ্চলের ফসলের ক্যালেন্ডার পাওয়া যায়নি।'));
    const currentCalendarId = context.current_crop_calendars?.[0]?.calendar_id;
    const currentIndex = Math.max(0, crops.findIndex(crop => crop.calendar_ids?.includes(currentCalendarId)));
    const selected = [currentIndex, currentIndex === 0 && crops.length > 1 ? 1 : 0];
    const selectors = compare ? selected.map((initial, slot) => `<div>
      <label>${slot === 0 ? t(language, 'First crop', 'প্রথম ফসল') : t(language, 'Second crop', 'দ্বিতীয় ফসল')}
        <select data-calendar-choice aria-controls="calendar-choice-${slot}">${crops.map((crop, i) => `<option value="${i}"${i === initial ? ' selected' : ''}>${esc(crop.crop_label)}</option>`).join('')}</select>
      </label>
      <div id="calendar-choice-${slot}">${crops.map((crop, i) => `<div data-calendar-option${i === initial ? '' : ' hidden'}>${calendarDetails(crop, language)}</div>`).join('')}</div>
    </div>`).join('') : '';
    return `<section class="result-card">
      <h2>${esc(title)}</h2><p>${esc(context.region_label)} · BAMIS</p>
      <p>${t(language, 'Compare the seasons and crop lifespans printed in local records. Ask a local agriculture officer about exact planting and harvest dates for your field.', 'স্থানীয় নথিতে উল্লেখিত মৌসুম ও ফসলের জীবনকাল তুলনা করুন। আপনার জমির রোপণ ও ফসল তোলার সঠিক তারিখ স্থানীয় কৃষি কর্মকর্তার কাছে জেনে নিন।')}</p>
      ${compare ? `<div class="check-grid">${selectors}</div>` : `<ul class="crop-calendar-list" role="list">${crops.map(crop => `<li><h3>${esc(crop.crop_label)}</h3>${calendarDetails(crop, language)}</li>`).join('')}</ul>`}
      <p><a href="https://www.bamis.gov.bd/en/calendar" target="_blank" rel="noopener">${t(language, 'Open BAMIS source calendars', 'বামিসের মূল ক্যালেন্ডার দেখুন')}</a></p>
    </section>`;
  }

  function cropWeather(window, language) {
    if (!window || !Object.hasOwn(window, 'latest_observed')) return '';
    if (window.status !== 'available') {
      const message = window.start && window.latest_observed && window.start > window.latest_observed
        ? t(language, 'Your planting date is after the latest complete NASA data for this district.', 'আপনার রোপণের তারিখ এই জেলার সর্বশেষ পূর্ণ নাসা তথ্যের পরে।')
        : t(language, 'There are no complete cached observations in the reported crop window.', 'জানানো ফসলের সময়ে পূর্ণ সংরক্ষিত পর্যবেক্ষণ নেই।');
      return `<p>${message} ${window.latest_observed ? esc(window.latest_observed) + ' · ' : ''}<a href="#climate">${t(language, 'View district weather history', 'জেলার আবহাওয়ার ইতিহাস দেখুন')}</a></p>`;
    }
    return `<p><b>${t(language, 'Recorded weather since planting', 'ফসলের সময়ে পর্যবেক্ষিত আবহাওয়া')}</b> · ${esc(window.start)} → ${esc(window.end)} · NASA POWER</p>
      <ul>${[['T2M_MAX','Highest daily temperature','সর্বোচ্চ দৈনিক তাপমাত্রা'],['T2M_MIN','Lowest daily temperature','সর্বনিম্ন দৈনিক তাপমাত্রা'],['PRECTOTCORR','Total rainfall','মোট বৃষ্টি']].map(([key,en,bn])=>{
        const metric=window.metrics[key];
        return `<li>${t(language,en,bn)} · ${Number.isFinite(metric.value)?esc(metric.value.toFixed(1)+' '+(metric.unit === 'degC' ? '°C' : metric.unit)):t(language,'Incomplete observations','অসম্পূর্ণ পর্যবেক্ষণ')}</li>`;
      }).join('')}</ul>`;
  }

  function cropWeatherChanges(occupancy, reference, language) {
    if (reference?.status !== 'available') return '';
    const rows = [
      ['T2M_MAX', 'high_c', 'Hottest day', 'উষ্ণতম দিন', '°C'],
      ['PRECTOTCORR', 'rain_mm', 'Total rain', 'মোট বৃষ্টি', 'mm'],
    ];
    const fmt = value => new Intl.NumberFormat(language === 'bn' ? 'bn-BD' : 'en', {
      maximumFractionDigits: 1, signDisplay: 'exceptZero',
    }).format(value);
    const tiles = rows.map(([parameter, key, en, bn, unit]) => {
      const observed = occupancy?.metrics?.[parameter]?.value;
      const typical = reference.median[key];
      if (!Number.isFinite(observed) || !Number.isFinite(typical)) return '';
      const difference = Math.round((observed - typical) * 10) / 10;
      const action = key === 'high_c'
        ? t(language, 'Check current forecasts and look for wilting during hot spells.', 'গরমের সময় বর্তমান পূর্বাভাস দেখুন এবং গাছ ঢলে পড়ছে কি না পরীক্ষা করুন।')
        : difference > 0
          ? t(language, 'Check for standing water and check soil moisture before adding irrigation.', 'পানি জমেছে কি না দেখুন এবং সেচের আগে মাটির আর্দ্রতা পরীক্ষা করুন।')
          : t(language, 'Check moisture around the roots before deciding whether to irrigate.', 'সেচ দেওয়ার আগে শিকড়ের আশপাশের মাটির আর্দ্রতা পরীক্ষা করুন।');
      return infoChip(t(language, en, bn), fmt(difference) + ' ' + unit, action);
    }).join('');
    return tiles ? `<div class="crop-weather-check">
      <h3>${t(language, 'Compared with the same dates in past years', 'অতীতের একই তারিখের সঙ্গে তুলনা')}</h3>
      <div class="check-grid">${tiles}</div>
      <p>${reference.years_used} ${t(language, 'complete past windows. The differences describe regional weather. Crop stress and irrigation needs depend on what you observe in the field.', 'টি পূর্ণ অতীত সময়কাল। পার্থক্যগুলো এলাকার আবহাওয়া দেখায়। ফসলের চাপ ও সেচের প্রয়োজন জমিতে যা দেখছেন তার ওপর নির্ভর করে।')}</p>
      <a href="https://www.fao.org/4/X0490E/x0490e0e.htm" target="_blank" rel="noopener">${t(language, 'FAO guidance on soil moisture and irrigation', 'মাটির আর্দ্রতা ও সেচ নিয়ে এফএও নির্দেশনা')}</a>
    </div>` : '';
  }

  function vulnerability(assessment, language, occupancy, seasonalReference, observedReference) {
    const checks = assessment?.checks || [];
    const fallow = assessment?.status === 'not_applicable';
    const hasWeather = assessment?.status === 'complete' || [occupancy, seasonalReference].some(item => item?.status === 'available');
    const period = assessment?.assessment_period;
    const title = t(language, 'Current crop weather and risk checks', 'বর্তমান ফসলের আবহাওয়া ও ঝুঁকি যাচাই');
    const status = fallow ? t(language, 'No crop reported', 'বর্তমান ফসল নেই')
      : hasWeather ? t(language, 'Weather evidence ready', 'আবহাওয়ার তথ্য প্রস্তুত')
      : t(language, 'Crop dates need weather data', 'ফসলের তারিখের আবহাওয়ার তথ্য প্রয়োজন');
    return `<section class="result-card" aria-labelledby="vulnerability-title">
      <div class="result-section-heading">
        <div><h2 id="vulnerability-title">${title}</h2><p>${esc(text(assessment?.crop_label, language))}</p></div>
        ${badge(hasWeather ? 'complete' : 'unknown', status)}
      </div>
      ${fallow ? `<p><a href="#climate">${t(language, 'See your district weather history', 'জেলার আবহাওয়ার ইতিহাস দেখুন')}</a></p>` : `
        ${assessment?.stage ? `<p>${t(language, 'Reported stage', 'জানানো পর্যায়')} · ${esc(human(assessment.stage))}</p>` : ''}
        ${period?.start && period?.end && !assessment?.observed_warning_exposure?.start ? `<p>${esc(period.start)} → ${esc(period.end)}</p>` : ''}
        ${cropWeather(occupancy, language)}
        ${cropWeatherChanges(occupancy, observedReference, language)}
        ${historicalDateReport(seasonalReference, language, t(language, 'Past weather over the same crop dates', 'ফসলের একই তারিখে অতীতের আবহাওয়া'), 'h3')}
        ${warningExposure(assessment?.observed_warning_exposure, language)}
        ${checks.length ? `<p>${t(language, 'Check the crop, soil moisture and drainage before adjusting irrigation. A field risk rating needs crop-stage and soil information.', 'সেচ বদলানোর আগে ফসল, মাটির আর্দ্রতা ও পানি নিষ্কাশন দেখুন। জমির ঝুঁকি নির্ধারণে ফসলের পর্যায় ও মাটির তথ্য দরকার।')}</p><details class="result-expand">
          <summary>${t(language, 'What these records can tell you about crop risk', 'এই তথ্য থেকে ফসলের ঝুঁকি সম্পর্কে যা জানা যায়')}</summary>
          <p>${t(language, 'Heat and water risk need crop-stage limits, soil and irrigation evidence. Use the dates and weather above as context when you discuss this crop with a local agriculture officer.', 'তাপ ও পানির ঝুঁকি জানতে ফসলের পর্যায়ভিত্তিক সীমা, মাটি ও সেচের তথ্য দরকার। স্থানীয় কৃষি কর্মকর্তার সঙ্গে আলোচনায় উপরের তারিখ ও আবহাওয়ার তথ্য ব্যবহার করুন।')}</p>
          ${checks.filter(check => !['heat-rule', 'water-rule'].includes(check.check_id)).map(check => `<p><b>${esc(text(check.label, language))}</b> · ${esc(check.missing_information || check.limitation || '')}</p>`).join('')}
        </details>` : ''}
      `}
    </section>`;
  }

  function planCrops(plan, language) {
    if (plan.role === 'baseline') {
      return (plan.segments || []).map(item => {
        const weather = item.historical_weather;
        const seasonMonths = {kharif_1: t(language, 'March–June', 'মার্চ–জুন'), kharif_2: t(language, 'July–October', 'জুলাই–অক্টোবর'), rabi: t(language, 'November–February', 'নভেম্বর–ফেব্রুয়ারি')};
        const seasonNames = {
          kharif_1: t(language, 'Kharif I', 'খরিফ–১'),
          kharif_2: t(language, 'Kharif II', 'খরিফ–২'),
          rabi: t(language, 'Rabi', 'রবি')
        };
        const season = /^(kharif_1|kharif_2|rabi) · (\d{4})/.exec(item.period || '');
        const periodLabel = season
          ? `${seasonNames[season[1]]} ${season[2]}${season[1] === 'rabi' ? '–' + (Number(season[2]) + 1) : ''}`
          : item.period;
        const summary = weather?.status === 'available'
          ? `<small>${weather.years_used} ${t(language, 'past windows', 'অতীত সময়কাল')} · ${t(language, 'median high / low / total rain', 'সর্বোচ্চ / সর্বনিম্ন / মোট বৃষ্টির মাঝের মান')} · ${esc(weather.median.high_c)} °C / ${esc(weather.median.low_c)} °C / ${esc(weather.median.rain_mm)} mm</small>`
          : '';
        return `<li><b>${esc(text(item.label, language))}</b><span>${esc(periodLabel || '')}${season ? ' · ' + seasonMonths[season[1]] : ''}</span>${summary}</li>`;
      }).join('');
    }
    return (plan.steps || []).map((item, index) => `<li><span>${String(index + 1).padStart(2, '0')}</span><b>${esc(text(item.crop_label, language))}</b><small>${esc(item.field_clearance_window?.latest || '')}</small></li>`).join('');
  }

  function indicatorRows(plan) {
    return (plan.indicators || []).map(item => statusRow(item.label, item.value ?? item.status, item.explanation || '')).join('');
  }

  function calendarMonth(date, language) {
    return new Intl.DateTimeFormat(language === 'bn' ? 'bn-BD' : 'en', {
      month: 'short', year: 'numeric', timeZone: 'UTC',
    }).format(new Date(date + 'T00:00:00Z'));
  }

  function calendarRotations(result, baseline, language, reportHref) {
    if (!result) return reportedRotation(baseline, language, reportHref);
    const dateRange = step => `${calendarMonth(step.calendar_start, language)} – ${calendarMonth(step.calendar_end, language)}`;
    return `<section class="result-card" aria-labelledby="rotation-comparison-title">
      <h2 id="rotation-comparison-title">${t(language, 'Compare crop rotations', 'ফসল আবর্তন তুলনা করুন')}</h2>
      <p>${t(language, 'Planning period', 'পরিকল্পনার সময়কাল')} · ${esc(formatDate(result.start))} – ${esc(formatDate(result.end))}</p>
      <p>${t(language, 'Alternatives use three distinct crops with non-overlapping local calendar months. The first option favors an early start with a different crop. The next options favor different crop mixes. Confirm actual sowing, harvest, land preparation and water needs before following a sequence.', 'বিকল্পে স্থানীয় ক্যালেন্ডারে সময় না মেলা তিনটি ভিন্ন ফসল রয়েছে। প্রথম বিকল্পে অন্য ফসল ও আগে শুরু প্রাধান্য পায়। পরের বিকল্পে ভিন্ন ফসলের সমন্বয় প্রাধান্য পায়। অনুসরণের আগে বপন, ফসল তোলা, জমি প্রস্তুতি ও পানির প্রয়োজন যাচাই করুন।')}</p>
      <div class="plan-comparison-grid crop-option-grid rotation-alternative-grid">
        ${reportedRotation(baseline, language, reportHref)}
        ${result.sequences.map(({steps}, index) => `<article class="plan-card">
          <h3>${esc(t(language, 'Alternative', 'বিকল্প'))} ${String.fromCharCode(65 + index)}</h3>
          <ol class="calendar-rotation-steps">${steps.map(step => `<li>
            <strong>${esc(text(step.crop_label, language))}</strong>
            <span>${esc(dateRange(step))}</span>
            <span>${esc(calendarName(step, language))}</span>
          </li>`).join('')}</ol>
          <details class="result-expand"><summary>${t(language, 'Why these crops and dates?', 'এই ফসল ও তারিখ কেন?')}</summary>
            <ul>${steps.map((step, i) => `<li><b>${esc(text(step.crop_label, language))}</b> · ${i ? t(language, 'Its calendar opens after the previous crop’s printed months end.', 'আগের ফসলের উল্লেখিত মাস শেষ হওয়ার পর এর ক্যালেন্ডার শুরু।') : step.first_month_overlaps_field_ready ? t(language, 'The calendar opens in your field-ready month.', 'জমি প্রস্তুতের মাসে ক্যালেন্ডার শুরু।') : t(language, 'The calendar opens after your field-ready month.', 'জমি প্রস্তুতের মাসের পরে ক্যালেন্ডার শুরু।')}
              ${calendarDetails({calendars:[step]}, language)}</li>`).join('')}</ul>
            <a href="https://www.bamis.gov.bd/en/calendar" target="_blank" rel="noopener">BAMIS · ${esc(steps[0].region)}</a>
          </details>
        </article>`).join('')}
      </div>
      ${result.sequences.length < 3 ? `<p>${t(language, 'The local calendars support fewer than three distinct three-crop sequences within this period.', 'এই সময়কালে স্থানীয় ক্যালেন্ডারে তিনটি ভিন্ন তিন-ফসলের ক্রম পাওয়া যায়নি।')}</p>` : ''}
    </section>`;
  }

  function rotationOptions(options, language) {
    if (!Array.isArray(options)) return '';
    return `<section class="result-card" aria-labelledby="crop-options-title">
      <h2 id="crop-options-title">${t(language, 'Crop options for your next rotation', 'পরবর্তী আবর্তনের ফসলের বিকল্প')}</h2>
      <p>${t(language, 'These options use local seasonal calendars and your field-ready date. Different crops from your current crop are shown first, then earlier calendar starts. Each card is one possible next crop. Confirm planting dates and field suitability locally.', 'এই বিকল্পগুলো স্থানীয় ফসলের ক্যালেন্ডার ও জমি প্রস্তুতের তারিখ থেকে নেওয়া। প্রতিটি কার্ড একটি সম্ভাব্য পরবর্তী ফসল। স্থানীয়ভাবে রোপণের তারিখ ও জমির উপযোগিতা নিশ্চিত করুন।')}</p>
      ${options.length < 3 ? `<p>${t(language, 'Fewer than three local seasonal calendars have clear month ranges for distinct crops.', 'ভিন্ন ফসলের স্পষ্ট মাসের তথ্যসহ তিনটির কম স্থানীয় ক্যালেন্ডার পাওয়া গেছে।')}</p>` : ''}
      <div class="plan-comparison-grid crop-option-grid">${options.map(item => {
        const [min, max] = item.life_span_days;
        const duration = Number.isFinite(min) && Number.isFinite(max)
          ? (min === max ? min : min + '–' + max) + ' ' + t(language, 'days in the source', 'উৎসে উল্লেখিত দিন') : '';
        return `<article class="plan-card">
          <h3>${esc(text(item.crop_label, language))}</h3>
          <p><strong>${esc(calendarMonth(item.calendar_start, language))} – ${esc(calendarMonth(item.calendar_end, language))}</strong></p>
          <p>${esc(calendarName(item, language))}${duration ? ' · ' + esc(duration) : ''}</p>
          <p>${item.first_month_overlaps_field_ready
            ? t(language, 'The calendar begins in your field-ready month. Check the local planting window with an agriculture officer.', 'ক্যালেন্ডারটি জমি প্রস্তুতের মাসে শুরু।')
            : t(language, 'Its next calendar starts after your field-ready month.', 'জমি প্রস্তুতের মাসের পর এই ক্যালেন্ডারটির পরবর্তী শুরু।')}
            ${item.different_from_current ? t(language, 'It is a different crop from the one growing now.', 'বর্তমানে চাষ করা ফসল থেকে এটি আলাদা।') : ''}</p>
          <details class="result-expand"><summary>${t(language, 'Calendar source and timing', 'ক্যালেন্ডারের উৎস ও সময়')}</summary>
            <p>${t(language, 'This range covers the first and last printed months. The listed lifespan comes from the source and can differ from the full calendar span.', 'এই সময়সীমা ক্যালেন্ডারের প্রথম ও শেষ মাস দেখায়। উল্লেখিত জীবনকাল সম্পূর্ণ ক্যালেন্ডারের সময়সীমা থেকে আলাদা হতে পারে।')}</p>
            <a href="https://www.bamis.gov.bd/en/calendar" target="_blank" rel="noopener">BAMIS · ${esc(item.region)}</a> · ${esc(item.source_id)} · ${t(language, 'page', 'পৃষ্ঠা')} ${esc(item.source_page)}
          </details>
        </article>`;
      }).join('')}</div>
    </section>`;
  }

  function reportedRotation(baseline, language, reportHref) {
      return `<section class="result-card" aria-labelledby="reported-plan-title">
        <h2 id="reported-plan-title">${t(language, 'Your usual crop order', 'আপনার সাধারণ ফসলের ক্রম')}</h2>
        ${baseline?.segments?.length
          ? `<p>${t(language, 'The order comes from your answers. Weather summaries use the same calendar dates from past years.', 'ক্রমটি আপনার উত্তর থেকে নেওয়া হয়েছে। আবহাওয়ার তথ্য অতীতের একই তারিখ থেকে নেওয়া হয়েছে।')}</p><ol class="plan-crops">${planCrops(baseline, language)}</ol>`
          : `<p>${t(language, 'This report has no saved crop order. To add one, choose your usual next crops in Question 4 and save your field answers.', 'এই রিপোর্টে ফসলের ক্রম সংরক্ষিত নেই। ৪ নম্বর প্রশ্নে পরবর্তী ফসলগুলো বেছে নিয়ে জমির উত্তর সেভ করুন।')}</p>`}
        <div class="result-actions"><button type="button" data-result-action="edit-inputs">${t(language, 'Edit field answers', 'জমির তথ্য বদলান')}</button>
          ${reportHref === '#overview' ? `<a href="#overview">${t(language, 'See your weather and crop report', 'আবহাওয়া ও ফসলের রিপোর্ট দেখুন')}</a>` : ''}
        </div>
        <p class="result-meta">${t(language, 'We need verified local planting and harvest guidance to suggest a new crop order for this field.', 'এই জমির জন্য নতুন ফসলের ক্রম সাজাতে স্থানীয় রোপণ ও ফসল তোলার যাচাই করা তথ্য দরকার।')}</p>
      </section>`;
  }

  function comparison(response, language, selectedPlan, reportHref = '#rotations', compare = false) {
    const plans = [response.baseline_assessment, ...(response.alternatives || [])].filter(Boolean);
    const missingSecond = (response.alternatives || []).length < 2;
    if (response.data_mode === 'local_evidence' && !(response.alternatives || []).length) {
      return `${calendarRotations(response.calendar_rotation, response.baseline_assessment, language, reportHref)}${response.calendar_rotation?.sequences.length ? "" : rotationOptions(response.calendar_options, language)}${reportHref === '#overview'
        ? historicalDateReport(response.climate?.field_ready_season, language, t(language, 'Past weather around your field-ready dates', 'জমি প্রস্তুতের তারিখের অতীত আবহাওয়া')) + regionalCalendarPanel(response, language, compare)
        : `<p><a href="#rotations">${t(language, 'See your field-ready dates and local calendars', 'জমি প্রস্তুতের তারিখ ও স্থানীয় ক্যালেন্ডার দেখুন')}</a></p>`}`;
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

  function weatherEvidenceCard(check, exposure, language) {
    const heat = check.check_id === 'heat-rule';
    const parameters = heat ? ['T2M_MAX', 'T2M_MIN'] : ['PRECTOTCORR'];
    const indicators = (exposure?.indicators || []).filter(indicator => parameters.includes(indicator.parameter));
    const complete = indicators.length > 0 && indicators.every(indicator => indicator.status === 'complete');
    const hasReference = indicators.length > 0 && Boolean(exposure?.reference);
    const state = complete ? 'complete' : 'unknown';
    const title = heat ? t(language, 'Heat and cold checks', 'গরম ও ঠান্ডা যাচাই') : t(language, 'Rain and water checks', 'বৃষ্টি ও পানি যাচাই');
    const label = complete ? t(language, 'Weather compared', 'আবহাওয়া তুলনা করা হয়েছে')
      : hasReference ? t(language, 'Incomplete observations', 'অসম্পূর্ণ পর্যবেক্ষণ')
        : t(language, 'Comparison unavailable', 'তুলনা করা যায়নি');
    const unavailable = exposure?.status === 'unavailable' ? warningUnavailable(exposure.reason, language)
      : exposure?.reference ? (heat
        ? t(language, 'This calendar does not specify a temperature warning that can be matched to daily NASA data.', 'এই ক্যালেন্ডারে নাসার দৈনিক তথ্যের সঙ্গে মেলানোর মতো তাপমাত্রার সতর্কতা নেই।')
        : t(language, 'This calendar has no rainfall warning that can be matched to daily NASA data.', 'এই ক্যালেন্ডারে নাসার দৈনিক তথ্যের সঙ্গে মেলানোর মতো বৃষ্টির সতর্কতা নেই।'))
        : t(language, 'This report has no published warning comparison. Generate a fresh report to check available evidence.', 'এই রিপোর্টে প্রকাশিত সতর্কতার সঙ্গে তুলনা নেই। উপলব্ধ তথ্য যাচাই করতে নতুন রিপোর্ট তৈরি করুন।');
    const limitation = heat
      ? t(language, 'A crop heat-risk rating needs temperature limits for its growth stage. Regional weather alone cannot tell us if this crop was damaged.', 'তাপের ঝুঁকি জানতে ফসলের বৃদ্ধির পর্যায় অনুযায়ী তাপমাত্রার সীমা দরকার। এলাকার আবহাওয়া দিয়ে ফসলের ক্ষতি বোঝা যায় না।')
      : t(language, 'Rain totals do not tell us whether this field needs irrigation. That also depends on the crop’s stage, soil moisture, drainage and irrigation.', 'শুধু বৃষ্টির পরিমাণ দিয়ে সেচের প্রয়োজন বোঝা যায় না। তা ফসলের পর্যায়, মাটির আর্দ্রতা, পানি নিষ্কাশন ও সেচের ওপরও নির্ভর করে।');
    return `<article class="evidence-card evidence-card--${state}">
      <div class="evidence-card__head">${badge(state, label)}<h3>${title}</h3></div>
      ${hasReference ? `<p class="evidence-card__lead">${esc(formatDate(exposure.start))} → ${esc(formatDate(exposure.end))} · NASA POWER</p>
        <div class="result-chip-row">${warningIndicatorChips(indicators, language)}</div><p>${warningSource(exposure, language)}</p>`
        : `<p class="evidence-card__lead">${unavailable}</p>`}
      <p class="evidence-card__lead">${limitation}</p>
    </article>`;
  }

  function evidencePanel(response, language) {
    const assessment = response.current_crop_assessment;
    const localReport = response.data_mode === 'local_evidence';
    const isWeatherCheck = check => ['heat-rule', 'water-rule'].includes(check.check_id);
    const checks = (response.checks || []).filter(check => !localReport || assessment?.status !== 'not_applicable' || !isWeatherCheck(check));
    return `<section class="result-card" aria-labelledby="evidence-title">
      <div class="result-section-heading">
        <div>
          <p class="result-eyebrow">06 · ${t(language, 'REASONS & EVIDENCE', 'কারণ ও প্রমাণ')}</p>
          <h2 id="evidence-title">${t(language, 'Why, why not, and what is missing', 'কেন, কেন নয়, কী তথ্য দরকার')}</h2>
        </div>
      </div>
      <div class="evidence-list">${checks.map(check => localReport && isWeatherCheck(check)
        ? weatherEvidenceCard(check, assessment?.observed_warning_exposure, language)
        : `<article class="evidence-card evidence-card--${esc(check.outcome)}">
        <div class="evidence-card__head">${badge(check.outcome)}<h3>${esc(text(check.label, language))}</h3></div>
        <p class="evidence-card__lead">${esc(check.missing_information || check.limitation || human(check.outcome))}</p>
        <dl>
          ${check.crop_id || check.stage ? `<dt>${t(language, 'Crop / stage', 'ফসল / পর্যায়')}</dt><dd>${esc([check.crop_id, check.stage].filter(Boolean).map(human).join(' · '))}</dd>` : ''}
          ${check.period ? `<dt>${t(language, 'Period', 'সময়কাল')}</dt><dd>${esc(check.period)}</dd>` : ''}
          ${check.rule_id ? `<dt>${t(language, 'Rule', 'নিয়ম')}</dt><dd><code>${esc(check.rule_id)}</code></dd>` : ''}
          <dt>${t(language, 'Sources', 'উৎস')}</dt><dd>${esc((check.source_ids || []).join(', ') || t(language, 'Source unavailable', 'উৎস পাওয়া যায়নি'))}</dd>
          ${check.missing_information && check.limitation && check.limitation !== check.missing_information ? `<dt>${t(language, 'Limit', 'সীমা')}</dt><dd>${esc(check.limitation)}</dd>` : ''}
        </dl>
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
      const ready = document.getElementById('whatif-ready-date').value;
      if (!globalThis.STS_INTAKE.validDate(ready)) {
        document.getElementById('whatif-ready-date').reportValidity();
        return;
      }
      if (ready !== original.availability.end) {
        request.availability = {...request.availability, kind: 'date', start: ready, end: ready, basis: 'expected'};
        // Preserve the original rotation; its dates may precede the scenario.
        request.baseline = {...request.baseline, state: 'no_established_rotation', segments: []};
      }
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
      const token=++viewGeneration;
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
            <h1>${t(language, 'Your field report', 'আপনার জমির রিপোর্ট')}</h1>
            <p>${t(language, 'Review your next-crop options and the weather for your field dates.', 'আপনার তারিখের আবহাওয়া দেখুন ও এলাকার ফসলের ক্যালেন্ডার তুলনা করুন।')}</p>
            ${response.data_mode === 'local_evidence' ? `<button type="button" data-result-action="jump-to-crop-weather">${t(language, 'Jump to current crop weather and risk checks', 'বর্তমান ফসলের আবহাওয়া ও ঝুঁকি যাচাই দেখুন')}</button>` : ''}
          </div>
          <div class="result-page-intro__status">${badge(response.report_status==='complete'?'complete':response.status,response.report_status==='complete'?t(language,'Evidence report ready','প্রমাণের রিপোর্ট প্রস্তুত'):response.status)}<span>${response.data_mode === 'local_evidence' ? t(language, 'Historical NASA weather and regional crop records', 'নাসার অতীত আবহাওয়া ও আঞ্চলিক ফসলের তথ্য') : esc(response.coverage?.label || '')}</span></div>
        </section>
        ${comparison(response, language, selectedPlan)}
        ${vulnerability(response.current_crop_assessment, language, response.climate?.reported_occupancy_window, response.climate?.crop_season_reference, response.climate?.crop_observed_reference)}
        ${example ? fieldSummary(data, language) : genuineSummary(data.request, language, response.status)}${restored&&!example?`<p class="result-limit">${t(language,'Restored saved report; generated at','সংরক্ষিত রিপোর্ট দেখানো হচ্ছে; তৈরি হয়েছে')} ${esc(response.generated_at_utc||'—')}. ${t(language,'Generate a new report after changing inputs or source data.','ইনপুট বা উৎসের তথ্য বদলালে নতুন রিপোর্ট তৈরি করুন।')} <button data-result-action="request-planning">${t(language,'Generate fresh report','নতুন রিপোর্ট তৈরি করুন')}</button></p>`:''}${!example&&response.report_status==='complete'?`<div class="result-actions"><button data-result-save="evidence-report">${t(language,'Save evidence report','প্রমাণের রিপোর্ট সংরক্ষণ')}</button></div>`:''}${response.data_mode === 'local_evidence' ? historicalDateReport(response.climate?.field_ready_season, language, t(language, 'Past weather around your field-ready dates', 'জমি প্রস্তুতের তারিখের অতীত আবহাওয়া')) + fieldInputsUsed(language, response.evidence_profile?.crop_context) : ''}${plan || example ? operationTimeline(plan, language) : ''}${climatePanel(response.climate, language, climateMetric, example)}<details class="result-card result-expand"><summary>${t(language, 'Sources and technical details', 'উৎস ও কারিগরি বিবরণ')}</summary>${evidenceProfile(response, language)}${evidencePanel(response, language)}</details>${toolsPanel(response, language)}${receiptPanel(data, language)}
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
        if(token===viewGeneration&&!genuine&&body.result?.data_mode==='local_evidence'&&JSON.stringify(stable(body.intake))===JSON.stringify(stable(request))){
          if (body.refresh_required || !Object.hasOwn(body.result.climate || {}, 'field_ready_season')) { void submit(request); return; }
          genuine={request,state:body.result.status,response:body.result};restored=true;rerender();}
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
        case 'jump-to-crop-weather': {
          const heading = document.getElementById('vulnerability-title');
          if (heading) {
            heading.tabIndex = -1;
            heading.focus({preventScroll: true});
            heading.scrollIntoView({block: 'center'});
          }
          return true;
        }
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
      if (target.matches('[data-calendar-choice]')) {
        const records = document.getElementById(target.getAttribute('aria-controls'));
        records?.querySelectorAll('[data-calendar-option]').forEach((record, index) => {
          record.hidden = index !== Number(target.value);
        });
        return true;
      }
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
