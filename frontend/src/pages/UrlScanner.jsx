import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Globe,
  Search,
  AlertTriangle,
  CheckCircle,
  ExternalLink,
  ShieldAlert,
  ShieldCheck,
  Server,
  Lock,
  Unlock,
  Radio,
  FileText,
  Clock,
  ArrowRight,
  Info
} from 'lucide-react';
import { api } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import IndicatorList from '../components/IndicatorList';
import IdentifierChips from '../components/IdentifierChips';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';
import CitizenNextSteps from '../components/CitizenNextSteps';
import AISecondOpinionCard from '../components/AISecondOpinionCard';
import { useRole } from '../context/RoleContext';
import { useI18n } from '../i18n/I18nContext';

const SAMPLE_URLS = [
  {
    label: 'Fake SBI Look-alike',
    url: 'http://sbi-kyc-update.com/login?token=urgent',
    note: 'HTTP scheme, brand look-alike, KYC token'
  },
  {
    label: 'Synthetic Scam (.test)',
    url: 'https://demo-scam.test/verify-account',
    note: 'Known synthetic blacklist entry'
  },
  {
    label: 'Genuine Portal',
    url: 'https://india.gov.in',
    note: 'Secure HTTPS, official government domain'
  }
];

export default function UrlScanner() {
  const { isCitizen } = useRole();
  const { t, lang } = useI18n();
  const [url, setUrl] = useState('');
  const [subject, setSubject] = useState('');
  const [performLiveCheck, setPerformLiveCheck] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleScan = async (e) => {
    if (e) e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed) {
      setError(t('url.err_empty'));
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.analyzeUrl(trimmed, subject.trim() || undefined, performLiveCheck);
      setResult(data);
    } catch (err) {
      setError(err.message || 'An error occurred during URL scanning.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSample = (sampleUrl) => {
    setUrl(sampleUrl);
    setSubject(`Quick scan of ${sampleUrl}`);
    setError(null);
    setResult(null);
  };

  const parseUrlStructure = (rawUrl) => {
    try {
      const parsed = new URL(rawUrl.startsWith('http') ? rawUrl : `http://${rawUrl}`);
      const hostname = parsed.hostname;
      const isIp = /^(\d{1,3}\.){3}\d{1,3}$/.test(hostname);
      const isPunycode = hostname.includes('xn--');
      const hyphenCount = (hostname.match(/-/g) || []).length;
      const parts = hostname.split('.');
      const subdomainsCount = parts.length > 2 ? parts.length - 2 : 0;

      return {
        scheme: parsed.protocol.replace(':', ''),
        host: hostname,
        pathname: parsed.pathname || '/',
        search: parsed.search || '(none)',
        isIp,
        isPunycode,
        hyphenCount,
        subdomainsCount,
        valid: true
      };
    } catch {
      return {
        scheme: 'unknown',
        host: rawUrl,
        pathname: '/',
        search: '(none)',
        isIp: false,
        isPunycode: false,
        hyphenCount: 0,
        subdomainsCount: 0,
        valid: false
      };
    }
  };

  const structure = result ? parseUrlStructure(result.raw_content || url) : null;
  const liveChecks = result?.live_checks || {};
  const domainAge = liveChecks.domain_age || { status: 'Not available', reason: 'WHOIS registration lookup service is not configured' };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Globe className="w-6 h-6 text-primary-600" />
          {isCitizen ? t('url.title') : 'URL & Phishing Link Scanner'}
        </h1>
        <p className="text-slate-600 text-sm mt-1">
          {isCitizen ? t('url.citizen_desc') : 'Detect look-alike domains, IP-hosted portals, spoofed brand tokens, and phishing parameters.'}
        </p>
      </div>

      {/* Input Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <form onSubmit={handleScan} className="space-y-4">
          <div>
            <label htmlFor="url-input" className="block text-sm font-semibold text-slate-800 mb-1">
              {isCitizen ? t('url.input_label') : 'Target URL to Scan'} <span className="text-rose-500">*</span>
            </label>
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
              <div className="relative flex-1">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Globe className="w-5 h-5" />
                </div>
                <input
                  id="url-input"
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleScan(e);
                    }
                  }}
                  placeholder={isCitizen ? t('url.placeholder') : "https://example-kyc-verify.com/login or http://192.168.1.1..."}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-300 text-slate-800 text-sm font-mono placeholder:font-sans focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-xs"
                />
              </div>
              <button
                type="submit"
                disabled={loading || !url.trim()}
                className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold text-sm shadow-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0 cursor-pointer"
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>{isCitizen ? t('url.scanning') : 'Scanning URL...'}</span>
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    <span>{isCitizen ? t('url.scan_btn') : 'Scan URL'}</span>
                  </>
                )}
              </button>
            </div>
            {isCitizen && (
              <p className="text-[11px] text-amber-700 bg-amber-50 border border-amber-200/80 rounded-lg px-3 py-1.5 flex items-center gap-1.5 mt-2">
                <Info className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                <span>{t('privacy.note')}</span>
              </p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="subject-input" className="block text-xs font-medium text-slate-600 mb-1">
                Investigation Reference / Subject (Optional)
              </label>
              <input
                id="subject-input"
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="e.g. SMS link from +919876543210"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex flex-col justify-end">
              <label className="flex items-center gap-2 text-sm text-slate-700 select-none p-2 rounded-lg bg-slate-50 border border-slate-200 cursor-pointer hover:bg-slate-100 transition-colors">
                <input
                  type="checkbox"
                  checked={performLiveCheck}
                  onChange={(e) => setPerformLiveCheck(e.target.checked)}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4"
                />
                <div>
                  <span className="font-medium text-slate-800">Perform Safe Live Fetch</span>
                  <span className="text-xs text-slate-500 block">
                    Inspect HTTP headers & redirects with SSRF guard (5s timeout)
                  </span>
                </div>
              </label>
            </div>
          </div>

          {/* Quick Samples */}
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-2">
              Or Try A Sample Link:
            </span>
            <div className="flex flex-wrap gap-2">
              {SAMPLE_URLS.map((sample, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectSample(sample.url)}
                  className="text-xs px-3 py-1.5 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 transition-colors text-left"
                >
                  <span className="font-semibold">{sample.label}</span>
                  <span className="text-slate-500 ml-1">({sample.note})</span>
                </button>
              ))}
            </div>
          </div>

          {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}
        </form>
      </div>

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* VERIFIED OFFICIAL WEBSITE BADGE */}
          {result.verified_official?.is_verified && (
            <div className="p-4 rounded-xl border-2 border-emerald-400 bg-emerald-50 text-emerald-950 shadow-sm flex items-start gap-3.5">
              <div className="p-2 rounded-lg bg-emerald-200/80 text-emerald-800 flex-shrink-0 mt-0.5">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-600 text-white font-bold text-xs uppercase tracking-wide">
                  <span>{t('banner.verified_official_badge')}</span>
                </div>
                <h3 className="text-base font-bold text-emerald-900">
                  {lang === 'hi'
                    ? (result.verified_official.badge_title || `${result.verified_official.brand_name} आधिकारिक वेबसाइट`)
                    : (result.verified_official.badge_title || `${result.verified_official.brand_name} official website`)}
                </h3>
                <p className="text-xs text-emerald-800 leading-relaxed font-medium">
                  {lang === 'hi'
                    ? (result.verified_official.description || `यह ${result.verified_official.brand_name} का आधिकारिक डोमेन है। अपनी जानकारी केवल आधिकारिक वेबसाइट पर ही दर्ज करें।`)
                    : (result.verified_official.description || `This is the official domain of ${result.verified_official.brand_name}. Enter your credentials only on the official website.`)}
                </p>
              </div>
            </div>
          )}

          {/* HIGH RISK WARNING BANNER */}
          {result.risk_level === 'HIGH' && (
            <div className="p-4 rounded-xl bg-rose-50 border-2 border-rose-300 flex items-start gap-3 text-rose-900 shadow-sm animate-pulse-slow">
              <ShieldAlert className="w-6 h-6 text-rose-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-bold text-base">{t('banner.high_title')}</h3>
                <p className="text-xs text-rose-800 mt-1 leading-relaxed">
                  {t('banner.high_body')}
                </p>
              </div>
            </div>
          )}

          {/* MEDIUM RISK WARNING BANNER */}
          {result.risk_level === 'MEDIUM' && (
            <div className="p-4 rounded-xl bg-amber-50 border-2 border-amber-300 flex items-start gap-3 text-amber-900 shadow-sm">
              <AlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-bold text-base">{t('banner.medium_title')}</h3>
                <p className="text-xs text-amber-800 mt-1 leading-relaxed">
                  {t('banner.medium_body')}
                </p>
              </div>
            </div>
          )}

          {/* LOW RISK ADVISORY NOTE (when not verified official) */}
          {result.risk_level === 'LOW' && !result.verified_official?.is_verified && (
            <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/80 text-emerald-900 shadow-xs flex items-start gap-3">
              <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
              <div>
                <h3 className="font-bold text-sm text-emerald-900">{t('banner.low_title')}</h3>
                <p className="text-xs text-emerald-800 mt-1 leading-relaxed">
                  {t('banner.low_body')}
                </p>
              </div>
            </div>
          )}

          {/* Top Summary Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono uppercase bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
                    Case: {result.case_id}
                  </span>
                  <RiskBadge level={result.risk_level} score={result.risk_score} />
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                    Category: {result.category.replace(/_/g, ' ')}
                  </span>
                </div>
                <h2 className="text-lg font-bold text-slate-900 mt-2 break-all font-mono">
                  {result.subject || result.raw_content}
                </h2>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-xs text-slate-500">
                    {isCitizen && lang === 'hi' ? 'कुल जोखिम स्कोर' : 'Calculated Score'}
                  </div>
                  <div className="text-3xl font-extrabold text-slate-900">
                    {result.risk_score}<span className="text-sm font-normal text-slate-400">/100</span>
                  </div>
                </div>
                {!isCitizen && (
                  <Link
                    to={`/cases?open=${result.case_id}`}
                    target="_self"
                    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium border border-slate-200 transition-colors"
                  >
                    <span>Open Full Case</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                )}
              </div>
            </div>

            {/* Citizen "What to do next" guidance box */}
            {isCitizen && <CitizenNextSteps riskLevel={result.risk_level} />}

            {/* AI Second Opinion Card */}
            {result.ai_second_opinion && (
              <div className="mt-4">
                <AISecondOpinionCard opinion={result.ai_second_opinion} />
              </div>
            )}

            {/* Structural Findings & External Data Availability */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Structural Findings */}
              <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3 flex items-center gap-1.5">
                  <Server className="w-4 h-4 text-primary-600" />
                  URL Structural Analysis
                </h3>
                {structure && (
                  <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
                    <div>
                      <dt className="text-slate-500">Transport Scheme</dt>
                      <dd className="font-semibold text-slate-800 flex items-center gap-1">
                        {structure.scheme === 'https' ? (
                          <>
                            <Lock className="w-3.5 h-3.5 text-emerald-600" />
                            <span>HTTPS (Encrypted)</span>
                          </>
                        ) : (
                          <>
                            <Unlock className="w-3.5 h-3.5 text-amber-600" />
                            <span className="text-amber-700">HTTP (Unencrypted)</span>
                          </>
                        )}
                      </dd>
                    </div>

                    <div>
                      <dt className="text-slate-500">Host Type</dt>
                      <dd className="font-semibold text-slate-800">
                        {structure.isIp ? (
                          <span className="text-rose-600">Direct IP Address</span>
                        ) : (
                          <span>Domain Name</span>
                        )}
                      </dd>
                    </div>

                    <div>
                      <dt className="text-slate-500">Punycode / IDN</dt>
                      <dd className="font-semibold text-slate-800">
                        {structure.isPunycode ? (
                          <span className="text-rose-600 font-bold">Detected (xn--)</span>
                        ) : (
                          <span className="text-slate-600">None</span>
                        )}
                      </dd>
                    </div>

                    <div>
                      <dt className="text-slate-500">Hyphen Count</dt>
                      <dd className="font-semibold text-slate-800">
                        {structure.hyphenCount > 1 ? (
                          <span className="text-amber-600">{structure.hyphenCount} (High)</span>
                        ) : (
                          <span>{structure.hyphenCount}</span>
                        )}
                      </dd>
                    </div>

                    <div>
                      <dt className="text-slate-500">Subdomain Depth</dt>
                      <dd className="font-semibold text-slate-800">
                        {structure.subdomainsCount > 2 ? (
                          <span className="text-amber-600">{structure.subdomainsCount} levels</span>
                        ) : (
                          <span>{structure.subdomainsCount} levels</span>
                        )}
                      </dd>
                    </div>

                    <div>
                      <dt className="text-slate-500">Host Domain</dt>
                      <dd className="font-mono text-slate-800 truncate" title={structure.host}>
                        {structure.host}
                      </dd>
                    </div>
                  </dl>
                )}
              </div>

              {/* External Data & Live Diagnostics (Explicitly "Not available" when unconfigured per Rule 8) */}
              <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3 flex items-center gap-1.5">
                  <Radio className="w-4 h-4 text-primary-600" />
                  External Diagnostics & Network Status
                </h3>
                <dl className="grid grid-cols-1 gap-y-2 text-xs">
                  <div className="flex justify-between items-center py-1 border-b border-slate-200/60">
                    <dt className="text-slate-500 flex items-center gap-1">
                      <span>Domain Registration Age (RDAP)</span>
                      <Info className="w-3 h-3 text-slate-400" />
                    </dt>
                    <dd
                      className={`font-medium px-2 py-0.5 rounded text-[11px] ${
                        domainAge.status === 'Available'
                          ? (domainAge.age_days < 30
                              ? 'bg-rose-100 text-rose-800 border border-rose-200 font-bold'
                              : domainAge.age_days < 90
                              ? 'bg-amber-100 text-amber-800 border border-amber-200 font-bold'
                              : 'bg-emerald-100 text-emerald-800 border border-emerald-200')
                          : 'bg-slate-200/70 text-slate-600'
                      }`}
                      title={domainAge.reason || ''}
                    >
                      {domainAge.formatted || domainAge.status}
                    </dd>
                  </div>

                  <div className="flex justify-between items-center py-1 border-b border-slate-200/60">
                    <dt className="text-slate-500">Google Safe Browsing</dt>
                    <dd
                      className={`font-medium px-2 py-0.5 rounded text-[11px] ${
                        liveChecks.safe_browsing?.matched
                          ? 'bg-rose-100 text-rose-800 border border-rose-200 font-bold'
                          : liveChecks.safe_browsing?.status === 'Clean'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-slate-200/70 text-slate-600'
                      }`}
                    >
                      {liveChecks.safe_browsing?.status || 'Not available (not configured)'}
                    </dd>
                  </div>

                  <div className="flex justify-between items-center py-1 border-b border-slate-200/60">
                    <dt className="text-slate-500">Live Network Fetch</dt>
                    <dd className="font-medium text-slate-700">
                      {liveChecks.performed ? (
                        <span className={liveChecks.status === 'Success' ? 'text-emerald-700 font-semibold' : 'text-rose-700 font-semibold'}>
                          {liveChecks.status}
                        </span>
                      ) : (
                        <span className="text-slate-500 italic">Not performed (static scan)</span>
                      )}
                    </dd>
                  </div>

                  {liveChecks.resolved_ip && (
                    <div className="flex justify-between items-center py-1 border-b border-slate-200/60">
                      <dt className="text-slate-500">Resolved IP Address</dt>
                      <dd className="font-mono text-slate-800">{liveChecks.resolved_ip}</dd>
                    </div>
                  )}

                  {liveChecks.redirect_chain && liveChecks.redirect_chain.length > 0 && (
                    <div className="pt-1">
                      <dt className="text-slate-500 mb-1">Redirect Chain ({liveChecks.redirect_chain.length} hops)</dt>
                      <dd className="space-y-1">
                        {liveChecks.redirect_chain.map((hop, hidx) => (
                          <div key={hidx} className="font-mono text-[11px] text-slate-700 bg-white p-1 rounded border border-slate-200 truncate">
                            {hop.status_code} → {hop.url}
                          </div>
                        ))}
                      </dd>
                    </div>
                  )}

                  {liveChecks.error && (
                    <div className="p-2 rounded bg-rose-50 border border-rose-200 text-rose-700 text-[11px]">
                      <strong>Fetch Error / SSRF Guard:</strong> {liveChecks.error}
                    </div>
                  )}
                </dl>
              </div>
            </div>
          </div>

          {/* Indicators List */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 mb-4">
              Structural & Behavioral Indicators ({result.indicators?.length || 0})
            </h3>
            <IndicatorList indicators={result.indicators || []} />
          </div>

          {/* Extracted Identifiers */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 mb-4">
              Associated Identifiers ({result.extracted_identifiers?.length || 0})
            </h3>
            <IdentifierChips identifiers={result.extracted_identifiers || []} />
          </div>

          {/* Recommended Safety Actions */}
          {result.safety_recommendations && result.safety_recommendations.length > 0 && (
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
              <h3 className="text-base font-bold text-slate-900 mb-3 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                Recommended Protective Actions
              </h3>
              <ul className="space-y-2">
                {result.safety_recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 text-sm text-slate-700">
                    <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Evidence Details */}
          {result.evidence && (
            <div className="bg-slate-50 rounded-xl border border-slate-200 p-4 text-xs text-slate-600">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <span className="font-semibold text-slate-700">Evidence SHA-256: </span>
                  <span className="font-mono text-slate-800 select-all">{result.evidence.content_sha256}</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-700">Logged UTC: </span>
                  <span>{new Date(result.evidence.timestamp_utc).toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}