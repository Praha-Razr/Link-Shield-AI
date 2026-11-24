import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AppWindow,
  Globe,
  Upload,
  Search,
  FileCode,
  ShieldAlert,
  ShieldCheck,
  CheckCircle,
  AlertTriangle,
  ArrowRight,
  Hash,
  Clock,
  Layers,
  Lock,
  Unlock,
  Radio,
  FileText,
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

const SAMPLE_WEBSITES = [
  {
    label: 'Fake High-ROI Investment',
    note: 'Guaranteed 300% return, deposit to UPI / Crypto',
    type: 'html',
    html: `<!DOCTYPE html>
<html>
<head><title>Apex Daily Wealth - Guaranteed Double Returns</title></head>
<body>
  <h1>Double Your Investment in 24 Hours!</h1>
  <p>Guaranteed 100% daily returns with zero risk. Join the exclusive multi-level referral network and earn passive income!</p>
  <p>Send registration deposit to UPI: apex.wealth@demoupi or BTC: 1SyntheticBtcFakeAddressForDemo99</p>
  <p>Customer Support Helpline: +91 98765 00111 | Email: support@apex-invest.test</p>
  <a href="tel:+919876500111">Call Us</a>
</body>
</html>`
  },
  {
    label: 'Fake Instant Loan App Portal',
    note: 'Instant approval, no collateral, processing fee to personal account',
    type: 'html',
    html: `<!DOCTYPE html>
<html>
<head><title>KwikCash - Instant 5 Lakh Loan Pre-Approved</title></head>
<body>
  <h1>Pre-Approved Instant Personal Loan</h1>
  <p>Instant loan disbursed in 10 minutes without CIBIL score or income documents. Urgent processing fee required.</p>
  <p>Deposit mandatory processing fee of Rs. 2,499 to Account No 918273645102 IFSC SBIN0001234</p>
  <p>WhatsApp officer: +91 98765 00222 | loan-desk@kwikcash-portal.test</p>
</body>
</html>`
  },
  {
    label: 'Illegal Betting Promotion',
    note: 'Betting bonus, daily predictions, VIP Telegram group',
    type: 'html',
    html: `<!DOCTYPE html>
<html>
<head><title>BetKing99 - Online Casino & Match Satta</title></head>
<body>
  <h1>Welcome to BetKing99 - 100% Satta Deposit Bonus</h1>
  <p>Play live Teen Patti, roulette and cricket betting. Instant withdrawal to bank account or UPI!</p>
  <p>Deposit funds to UPI: betking99.pay@demoupi | Telegram admin: @betking_official</p>
  <p>Helpline: +91 98765 00333</p>
</body>
</html>`
  },
  {
    label: 'Genuine Educational Portal',
    note: 'Static informational portal, no financial demands',
    type: 'html',
    html: `<!DOCTYPE html>
<html>
<head><title>Cyber Safety Awareness Mission</title></head>
<body>
  <h1>National Cyber Crime Awareness Portal</h1>
  <p>Learn how to protect yourself from phishing, fake investment schemes, and impersonation scams.</p>
  <p>For cyber crime reporting, call the national helpline 1930 or visit cybercrime.gov.in.</p>
  <p>Official Contact: contact@cybercrime.gov.in</p>
</body>
</html>`
  }
];

export default function WebsiteAnalyzer() {
  const { isCitizen } = useRole();
  const { t, lang } = useI18n();
  const [activeTab, setActiveTab] = useState('url'); // 'url' | 'upload'
  const [url, setUrl] = useState('');
  const [subject, setSubject] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleUrlSubmit = async (e) => {
    if (e) e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed) {
      setError(t('web.err_empty'));
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.analyzeWebsite({
        url: trimmed,
        subject: subject.trim() || undefined
      });
      setResult(data);
    } catch (err) {
      setError(err.message || 'Website analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUploadSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!selectedFile) {
      setError('Please select an HTML (.html, .htm) or text file to upload.');
      return;
    }

    // Client-side file validation
    const validExtensions = ['.html', '.htm', '.txt'];
    const fileNameLower = selectedFile.name.toLowerCase();
    const isValidExt = validExtensions.some((ext) => fileNameLower.endsWith(ext));
    if (!isValidExt) {
      setError('Invalid file type. Only static .html, .htm, or .txt files are permitted.');
      return;
    }

    if (selectedFile.size > 1024 * 1024) {
      setError('File is too large. Maximum allowed file size is 1 MB.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (subject.trim()) {
        formData.append('subject', subject.trim());
      }

      const data = await api.analyzeWebsite(formData);
      setResult(data);
    } catch (err) {
      setError(err.message || 'HTML file analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSample = (sample) => {
    setError(null);
    setResult(null);
    setActiveTab('upload');
    setSubject(sample.label);

    // Create a virtual File object from sample HTML string
    const blob = new Blob([sample.html], { type: 'text/html' });
    const file = new File([blob], `${sample.label.toLowerCase().replace(/\s+/g, '_')}.html`, {
      type: 'text/html'
    });
    setSelectedFile(file);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <AppWindow className="w-6 h-6 text-primary-600" />
          {isCitizen ? t('web.title') : 'Fraudulent Website & Fake App Analyser'}
        </h1>
        <p className="text-slate-600 text-sm mt-1">
          {isCitizen ? t('web.citizen_desc') : 'Perform safe, static DOM and source inspection for fake investment portals, loan apps, Ponzi schemes, and illegal betting sites. Scripts are never executed.'}
        </p>
      </div>

      {/* Input Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        {/* Tab Switcher: Live Safe Fetch vs HTML File Upload */}
        <div className="flex border-b border-slate-200 pb-2 gap-4">
          <button
            type="button"
            onClick={() => setActiveTab('url')}
            className={`flex items-center gap-2 pb-2 text-sm font-semibold transition-colors border-b-2 cursor-pointer ${
              activeTab === 'url'
                ? 'border-blue-600 text-blue-700'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Globe className="w-4 h-4" />
            <span>{isCitizen && lang === 'hi' ? 'वेबसाइट लिंक' : 'Target Live URL'}</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('upload')}
            className={`flex items-center gap-2 pb-2 text-sm font-semibold transition-colors border-b-2 cursor-pointer ${
              activeTab === 'upload'
                ? 'border-blue-600 text-blue-700'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Upload className="w-4 h-4" />
            <span>{isCitizen && lang === 'hi' ? 'HTML फ़ाइल अपलोड (.html / .txt, अधिकतम 1MB)' : 'Upload Saved HTML (.html / .txt, max 1MB)'}</span>
          </button>
        </div>

        {/* Tab 1: Live Safe Fetch */}
        {activeTab === 'url' && (
          <form onSubmit={handleUrlSubmit} className="space-y-4">
            <div>
              <label htmlFor="target-url" className="block text-sm font-semibold text-slate-800 mb-1">
                {isCitizen ? t('web.url_label') : 'Target Website URL'} <span className="text-rose-500">*</span>
              </label>
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                <div className="relative flex-1">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <Globe className="w-5 h-5" />
                  </div>
                  <input
                    id="target-url"
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder={isCitizen ? t('web.url_placeholder') : "https://fake-investment-portal.test or http://betting-site.test"}
                    className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-300 text-slate-800 text-sm font-mono placeholder:font-sans focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
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
                      <span>{isCitizen ? t('web.analysing') : 'Fetching & Analyzing...'}</span>
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4" />
                      <span>{isCitizen ? t('web.analyse_btn') : 'Analyse Website'}</span>
                    </>
                  )}
                </button>
              </div>
              <p className="text-[11px] text-slate-500 mt-1.5 flex items-center gap-1">
                <Lock className="w-3 h-3 text-emerald-600" />
                Protected against SSRF. Private/loopback IPs blocked. Max 5 redirect hops.
              </p>
              {isCitizen && (
                <p className="text-[11px] text-amber-700 bg-amber-50 border border-amber-200/80 rounded-lg px-3 py-1.5 flex items-center gap-1.5 mt-2">
                  <Info className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                  <span>{t('privacy.note')}</span>
                </p>
              )}
            </div>

            <div>
              <label htmlFor="url-subject" className="block text-xs font-medium text-slate-600 mb-1">
                Investigation Reference / Subject (Optional)
              </label>
              <input
                id="url-subject"
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="e.g. Complaint FIR 412/26 - Suspected Investment Fraud"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </form>
        )}

        {/* Tab 2: HTML File Upload */}
        {activeTab === 'upload' && (
          <form onSubmit={handleFileUploadSubmit} className="space-y-4">
            <div>
              <label htmlFor="file-upload" className="block text-sm font-semibold text-slate-800 mb-1">
                {isCitizen ? t('web.html_label') : 'Select Saved Website Source File (.html, .htm, .txt)'} <span className="text-rose-500">*</span>
              </label>
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                <input
                  id="file-upload"
                  type="file"
                  accept=".html,.htm,.txt"
                  onChange={(e) => setSelectedFile(e.target.files[0] || null)}
                  className="w-full text-sm text-slate-700 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200 border border-slate-300 rounded-lg p-1 bg-white"
                />
                <button
                  type="submit"
                  disabled={loading || !selectedFile}
                  className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold text-sm shadow-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0 cursor-pointer"
                >
                  {loading ? (
                    <>
                      <LoadingSpinner size="sm" />
                      <span>{isCitizen ? t('web.analysing') : 'Inspecting DOM...'}</span>
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4" />
                      <span>{isCitizen ? t('web.analyse_btn') : 'Inspect HTML'}</span>
                    </>
                  )}
                </button>
              </div>
              {selectedFile && (
                <div className="mt-2 text-xs text-slate-600 flex items-center gap-2">
                  <FileCode className="w-4 h-4 text-primary-600" />
                  <span>
                    Selected: <strong>{selectedFile.name}</strong> ({(selectedFile.size / 1024).toFixed(1)} KB)
                  </span>
                </div>
              )}
              {isCitizen && (
                <p className="text-[11px] text-amber-700 bg-amber-50 border border-amber-200/80 rounded-lg px-3 py-1.5 flex items-center gap-1.5 mt-2">
                  <Info className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                  <span>{t('privacy.note')}</span>
                </p>
              )}
            </div>

            <div>
              <label htmlFor="file-subject" className="block text-xs font-medium text-slate-600 mb-1">
                Investigation Reference / Subject (Optional)
              </label>
              <input
                id="file-subject"
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="e.g. Seized offline HTML snapshot - Fake Trading App"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </form>
        )}

        {/* Quick Samples Section */}
        <div className="pt-2 border-t border-slate-100">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-2">
            Or Load A Representative Scam / Genuine HTML Sample:
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2">
            {SAMPLE_WEBSITES.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectSample(sample)}
                className="p-2.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-left transition-colors cursor-pointer"
              >
                <div className="font-semibold text-xs text-slate-800">{sample.label}</div>
                <div className="text-[11px] text-slate-500 line-clamp-2 mt-0.5">{sample.note}</div>
              </button>
            ))}
          </div>
        </div>

        {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}
      </div>

      {/* Analysis Results Display */}
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

          {/* Top Dossier Overview Card */}
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
                <h2 className="text-lg font-bold text-slate-900 mt-2 break-all">
                  {result.subject}
                </h2>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-xs text-slate-500">
                    {isCitizen && lang === 'hi' ? 'कुल जोखिम स्कोर' : 'Threat Score'}
                  </div>
                  <div className="text-3xl font-extrabold text-slate-900">
                    {result.risk_score}<span className="text-sm font-normal text-slate-400">/100</span>
                  </div>
                </div>
                {!isCitizen && (
                  <Link
                    to={`/cases?open=${result.case_id}`}
                    target="_self"
                    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition-colors"
                  >
                    <span>Open Dossier</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                )}
              </div>
            </div>

            {/* Evidence & Hash Info */}
            <div className="mt-4 pt-2 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-600">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="font-semibold text-slate-700 block mb-1">Evidence Integrity SHA-256:</span>
                <span className="font-mono text-slate-900 break-all select-all">
                  {result.evidence?.content_sha256}
                </span>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="font-semibold text-slate-700 block mb-1">Capture & Forensic Metadata:</span>
                <div>Logged: {new Date(result.evidence?.timestamp_utc).toLocaleString()}</div>
                <div>Payload Size: {result.evidence?.char_count} characters parsed</div>
              </div>
            </div>

            {/* Domain Age & Safe Browsing Diagnostics */}
            {result.live_checks?.domain_age && (
              <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3 flex items-center gap-1.5">
                  <Radio className="w-4 h-4 text-primary-600" />
                  Domain Diagnostics & Registry Data
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="flex justify-between items-center p-2.5 rounded-lg bg-white border border-slate-200">
                    <span className="text-slate-600 font-medium">Domain Age (RDAP):</span>
                    <span
                      className={`font-medium px-2 py-0.5 rounded text-[11px] ${
                        result.live_checks.domain_age.status === 'Available'
                          ? (result.live_checks.domain_age.age_days < 30
                              ? 'bg-rose-100 text-rose-800 border border-rose-200 font-bold'
                              : result.live_checks.domain_age.age_days < 90
                              ? 'bg-amber-100 text-amber-800 border border-amber-200 font-bold'
                              : 'bg-emerald-100 text-emerald-800 border border-emerald-200')
                          : 'bg-slate-100 text-slate-600'
                      }`}
                      title={result.live_checks.domain_age.reason || ''}
                    >
                      {result.live_checks.domain_age.formatted || result.live_checks.domain_age.status}
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-2.5 rounded-lg bg-white border border-slate-200">
                    <span className="text-slate-600 font-medium">Google Safe Browsing:</span>
                    <span
                      className={`font-medium px-2 py-0.5 rounded text-[11px] ${
                        result.live_checks.safe_browsing?.matched
                          ? 'bg-rose-100 text-rose-800 border border-rose-200 font-bold'
                          : result.live_checks.safe_browsing?.status === 'Clean'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {result.live_checks.safe_browsing?.status || 'Not available (not configured)'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Citizen "What to do next" guidance box */}
          {isCitizen && <CitizenNextSteps riskLevel={result.risk_level} />}

          {/* AI Second Opinion Card */}
          {result.ai_second_opinion && (
            <AISecondOpinionCard opinion={result.ai_second_opinion} />
          )}

          {/* Triggered Indicators */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 mb-4 flex items-center justify-between">
              <span>Detected Fraud Indicators ({result.indicators?.length || 0})</span>
              <span className="text-xs text-slate-500 font-normal">Forensic Explanations</span>
            </h3>
            <IndicatorList indicators={result.indicators || []} />
          </div>

          {/* Extracted Network & Financial Identifiers */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 mb-4 flex items-center justify-between">
              <span>Extracted Network & Financial Identifiers ({result.extracted_identifiers?.length || 0})</span>
              <span className="text-xs text-slate-500 font-normal">Click chips to copy</span>
            </h3>
            <IdentifierChips identifiers={result.extracted_identifiers || []} />
          </div>

          {/* Safe Evidence Excerpt (Escaped, Raw Scripts Never Rendered) */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4 text-primary-600" />
              <span>Safe Visible Evidence Excerpt (Scripts Stripped)</span>
            </h3>
            <p className="text-xs text-slate-500 mb-3">
              Rendered strictly as sanitized, escaped plain text. No scripts or third-party stylesheets are executed.
            </p>
            <pre className="p-4 rounded-lg bg-slate-50 border border-slate-200 font-mono text-xs text-slate-800 whitespace-pre-wrap max-h-60 overflow-y-auto select-all">
              {result.evidence?.excerpt || result.raw_content}
            </pre>
          </div>

          {/* Safety Recommendations */}
          {result.safety_recommendations && result.safety_recommendations.length > 0 && (
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
              <h3 className="text-base font-bold text-slate-900 mb-3 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                <span>Protective Directives & Human Action Steps</span>
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
        </div>
      )}
    </div>
  );
}
