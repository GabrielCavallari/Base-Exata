(function () {
  'use strict';
  const origin = 'https://base-exata-insights.netlify.app';
  const keys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid'];

  function campaignParameters(search, saved) {
    const query = new URLSearchParams(search);
    const result = {};
    for (const key of keys) {
      const value = query.get(key) || (saved && typeof saved[key] === 'string' ? saved[key] : '');
      if (value && !['(direct)', '(none)', '(not set)'].includes(value)) result[key] = value;
    }
    return result;
  }

  function attributedLink(href, campaign) {
    const target = new URL(href);
    if (target.origin !== origin) return href;
    for (const key of keys) {
      if (campaign[key]) target.searchParams.set(key, campaign[key]);
    }
    return target.href;
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { campaignParameters, attributedLink };
  }
  if (typeof document === 'undefined') return;

  function updateLinks() {
    let saved = {};
    try { saved = JSON.parse(sessionStorage.getItem('base_exata_utm') || '{}'); } catch { /* Storage may be blocked. */ }
    const campaign = campaignParameters(window.location.search, saved);
    for (const link of document.querySelectorAll('a[data-insights-link]')) {
      link.href = attributedLink(link.href, campaign);
    }
  }

  updateLinks();
  document.addEventListener('click', function (event) {
    if (event.target instanceof Element && event.target.closest('a[data-insights-link]')) updateLinks();
  }, true);
})();
