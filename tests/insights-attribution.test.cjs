const { test } = require('node:test');
const assert = require('node:assert/strict');
const { campaignParameters, attributedLink } = require('../landing-page/insights-attribution.js');

test('all campaign keys survive the landing to signup link, including encoded click IDs', () => {
  const search = '?utm_source=google&utm_medium=cpc&utm_campaign=launch&utm_term=planilhas&utm_content=hero&gclid=synthetic%2Bclick%26id&email=private';
  const campaign = campaignParameters(search, {});
  const url = new URL(attributedLink('https://base-exata-insights.netlify.app/cadastro?plan=free#form', campaign));
  for (const key of Object.keys(campaign)) assert.equal(url.searchParams.get(key), campaign[key]);
  assert.equal(Object.keys(campaign).length, 6);
  assert.equal(url.searchParams.has('email'), false);
  assert.equal(url.searchParams.get('plan'), 'free');
  assert.equal(url.hash, '#form');
});

test('current campaign wins over saved attribution and saved content is used on later pages', () => {
  assert.deepEqual(campaignParameters('?utm_source=google', { utm_source: 'old', utm_content: 'saved', gclid: 12 }), { utm_source: 'google', utm_content: 'saved' });
  assert.deepEqual(campaignParameters('', { utm_source: '(direct)', utm_medium: '(none)' }), {});
});

test('only exact SaaS origin is changed, and repeat clicks do not duplicate parameters', () => {
  const other = 'https://base-exata-insights.netlify.app.attacker.example/login';
  assert.equal(attributedLink(other, { gclid: 'synthetic' }), other);
  const once = attributedLink('https://base-exata-insights.netlify.app/login', { gclid: 'synthetic' });
  assert.equal(attributedLink(once, { gclid: 'synthetic' }), once);
});
