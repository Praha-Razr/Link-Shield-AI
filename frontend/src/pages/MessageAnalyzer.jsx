import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  MessageSquareWarning,
  Send,
  AlertOctagon,
  AlertTriangle,
  Globe,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  Copy,
  ArrowRight,
  Sparkles,
  Fingerprint,
  Info,
} from 'lucide-react';
import RiskBadge from '../components/RiskBadge';
import IndicatorList from '../components/IndicatorList';
import IdentifierChips from '../components/IdentifierChips';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';
import CitizenNextSteps from '../components/CitizenNextSteps';
import AISecondOpinionCard from '../components/AISecondOpinionCard';
import { api } from '../services/api';
import { useRole } from '../context/RoleContext';
import { useI18n } from '../i18n/I18nContext';

const SAMPLE_TEMPLATES = [
  {
    label: 'Fake KYC Threat (EN)',
    text: 'URGENT NOTICE: Your SBI account has been suspended immediately due to pending KYC verification. Update KYC within 24 hours at http://demo-scam.test/kyc or your account will be blocked today. Contact officer at +91 90000 00001.',
  },
  {
    label: 'Hindi Account Block (HI)',
    text: 'अंतिम चेतावनी: आपका बैंक खाता बंद कर दिया जाएगा। तुरंत केवाईसी अपडेट करें। आधार कार्ड सत्यापन हेतु तुरंत संपर्क करें +91 90000 00004।',
  },
  {
    label: 'Hinglish Task Job (Hinglish)',
    text: 'Part time job opportunity: Ghar baithe kamaye daily 2500 per day by like karke paise kamaye. Task complete karein aur turant daily payment pao. Registration charge ke liye UPI par bhejo: work.daily@demoupi.',
  },
  {
    label: 'Genuine Bank Alert (Safe)',
    text: 'Dear customer, Rs 450.00 has been debited from your a/c XX4019 on 22-Nov-2026 19:40 for UPI purchase at Metro Supermarket. Available balance: INR 18,240.50. Bank of Baroda.',
  },
];

export default function MessageAnalyzer() {
  const { isCitizen } = useRole();
  const { t, lang } = useI18n();
  const isHi = isCitizen && lang === 'hi';
  const [content, setContent] = useState('');
  const [subject, setSubject] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [copiedEvidence, setCopiedEvidence] = useState(false);

  const handleAnalyze = async (e) => {
    e?.preventDefault();
    if (!content.trim()) {
      setError(isHi ? t('msg.err_empty') : 'Please paste or type a suspicious message to analyze.');
      return;
    }
    if (content.length > 50000) {
      setError(isHi ? t('msg.err_max_len') : 'Content exceeds maximum length of 50,000 characters.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const res = await api.analyzeMessage(content.trim(), subject.trim() || undefined);
      setResult(res);
    } catch (err) {
      setError(err.message || 'Analysis failed. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (sampleText) => {
    setContent(sampleText);
    setResult(null);
    setError(null);
  };

  const copyHash = (hash) => {
    navigator.clipboard?.writeText(hash);
    setCopiedEvidence(true);
    setTimeout(() => setCopiedEvidence(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="pb-2 border-b border-slate-200">
        <h1 className="text-xl md:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <MessageSquareWarning className="w-6 h-6 text-electric-500" />
          <span>{isHi ? t('msg.title') : 'Scam Message & Threat Analyser'}</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          {isCitizen
            ? (isHi ? t('msg.citizen_desc') : 'Paste any suspicious SMS, WhatsApp, or Telegram message to verify if it is a scam before clicking or paying.')
            : 'Multi-factor message inspection, entity extraction, phishing domain analysis and evidence hashing.'}
        </p>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {/* Input Form Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 space-y-4">
        {/* Sample Loaders */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-cyan-500" /> {isHi ? t('msg.templates_label') : 'Quick Templates:'}
          </span>
          {SAMPLE_TEMPLATES.map((tmpl, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => loadSample(tmpl.text)}
              className="text-[11px] px-2.5 py-1 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium transition-colors border border-slate-200"
            >
              {tmpl.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleAnalyze} className="space-y-3">
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="message-input" className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                {isHi ? t('msg.input_label') : 'Raw Message Content'} <span className="text-rose-500">*</span>
              </label>
              <span className="text-[11px] font-mono text-slate-400">
                {content.length}/50,000 {isHi ? t('msg.chars') : 'chars'}
              </span>
            </div>
            <textarea
              id="message-input"
              rows={5}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={isHi ? t('msg.placeholder') : 'Paste suspicious SMS, WhatsApp message, Telegram task offer, or electricity notice here...'}
              className="w-full p-3.5 text-xs font-mono rounded-lg border border-slate-300 focus:border-electric-500 focus:ring-2 focus:ring-electric-500/20 focus:outline-hidden transition-all bg-slate-50/50"
            />
            {isCitizen && (
              <p className="text-[11px] text-amber-700 bg-amber-50 border border-amber-200/80 rounded-lg px-3 py-1.5 flex items-center gap-1.5 mt-2">
                <Info className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                <span>{isHi ? t('privacy.note') : 'Avoid pasting personal details like OTPs, passwords or account numbers.'}</span>
              </p>
            )}
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-1">
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder={isHi ? t('msg.subject_placeholder') : 'Case Subject / Tag (Optional)'}
              className="px-3 py-2 text-xs rounded-lg border border-slate-300 focus:border-electric-500 focus:outline-hidden bg-white max-w-sm"
            />

            <button
              type="submit"
              disabled={loading || !content.trim()}
              className="px-6 py-2.5 bg-electric-500 hover:bg-electric-600 disabled:bg-slate-300 text-white font-bold rounded-lg shadow-xs text-xs flex items-center justify-center gap-2 transition-all cursor-pointer"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" message="" />
                  <span>{isHi ? t('msg.evaluating') : 'Evaluating Risk Factors...'}</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>{isHi ? t('msg.analyse_btn') : 'ANALYSE MESSAGE'}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Analysis Results */}
      {result && (
        <div className="space-y-5 animate-in fade-in duration-200">
          {/* HIGH RISK WARNING BANNER */}
          {result.risk_level === 'HIGH' && (
            <div className="p-4 rounded-xl border border-rose-300 bg-rose-50/90 text-rose-900 shadow-xs flex items-start gap-3.5">
              <div className="p-2 rounded-lg bg-rose-200/60 text-rose-700 flex-shrink-0 mt-0.5">
                <AlertOctagon className="w-6 h-6 animate-pulse" />
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-black uppercase tracking-wide text-rose-800">
                  {isHi ? t('banner.high_title') : 'Critical Threat Warning: Do Not Click Links or Transfer Funds'}
                </h3>
                <p className="text-xs text-rose-700 leading-relaxed font-medium">
                  {isHi ? t('banner.high_body') : 'Do not click links, do not pay or share OTP, PIN or passwords. Report this incident immediately on cybercrime.gov.in or call 1930. This communication matches known fraudulent patterns.'}
                </p>
              </div>
            </div>
          )}

          {/* MEDIUM RISK WARNING BANNER */}
          {result.risk_level === 'MEDIUM' && (
            <div className="p-4 rounded-xl border border-amber-300 bg-amber-50/90 text-amber-900 shadow-xs flex items-start gap-3.5">
              <div className="p-2 rounded-lg bg-amber-200/60 text-amber-700 flex-shrink-0 mt-0.5">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-black uppercase tracking-wide text-amber-800">
                  {isHi ? t('banner.medium_title') : 'Suspicious: Be Careful'}
                </h3>
                <p className="text-xs text-amber-800 leading-relaxed font-medium">
                  {isHi ? t('banner.medium_body') : 'Do not click links or share details yet. Verify through the official app/website or by calling a number you already know (such as the one printed on your card). If unsure, report on cybercrime.gov.in or call 1930.'}
                </p>
              </div>
            </div>
          )}

          {/* LOW RISK ADVISORY NOTE */}
          {result.risk_level === 'LOW' && (
            <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/80 text-emerald-900 shadow-xs flex items-start gap-3.5">
              <div className="p-2 rounded-lg bg-emerald-200/60 text-emerald-700 flex-shrink-0 mt-0.5">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-bold text-emerald-900">
                  {isHi ? t('banner.low_title') : 'No scam signs found by our automated checks.'}
                </h3>
                <p className="text-xs text-emerald-800 leading-relaxed font-medium">
                  {isHi ? t('banner.low_body') : 'As a precaution, open links through the official app or website, never share your OTP, PIN or password, and if this message asks for money or personal details, confirm with the sender using a number you already know. Low risk does not guarantee safety. Automated results are not proof.'}
                </p>
              </div>
            </div>
          )}

          {/* Extracted URL Status Pills (Requirement 5) */}
          {result.verified_links && result.verified_links.length > 0 && (
            <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-2xs space-y-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                {isHi ? t('msg.detected_links') : 'Detected Links in Message'} ({result.verified_links.length}):
              </span>
              <div className="flex flex-wrap gap-2">
                {result.verified_links.map((link, idx) => {
                  const isOfficial = link.is_official;
                  const isLowMsg = result.risk_level === 'LOW';
                  const pillLabel = isOfficial && isHi ? t('banner.verified_official_badge') : link.label;

                  if (isLowMsg) {
                    return (
                      <span
                        key={idx}
                        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
                          isOfficial
                            ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                            : 'bg-slate-100 text-slate-700 border-slate-200'
                        }`}
                      >
                        {isOfficial ? (
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                        ) : (
                          <Globe className="w-3.5 h-3.5 text-slate-500" />
                        )}
                        <span>{pillLabel}</span>
                      </span>
                    );
                  }

                  // Medium or High message: keep focus on risk
                  return (
                    <span
                      key={idx}
                      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
                        isOfficial
                          ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                          : 'bg-rose-50 text-rose-800 border-rose-300'
                      }`}
                    >
                      {isOfficial ? (
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                      ) : (
                        <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
                      )}
                      <span>{pillLabel}</span>
                    </span>
                  );
                })}
              </div>
            </div>
          )}

          {/* Result Overview Header Card */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-slate-400">
                    CASE {result.case_id}
                  </span>
                  <RiskBadge level={result.risk_level} score={result.risk_score} size="md" />
                </div>
                <h2 className="text-base font-bold text-slate-900 mt-1">
                  {result.subject}
                </h2>
              </div>

              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 rounded text-xs font-semibold bg-slate-100 text-slate-700 uppercase tracking-wider">
                  {result.category.replace(/_/g, ' ')}
                </span>
                <span className="px-2 py-1 rounded text-xs font-mono font-medium bg-slate-100 text-slate-500 uppercase">
                  LANG: {result.language}
                </span>
                <Link
                  to={`/cases?open=${result.case_id}`}
                  target="_self"
                  className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-md flex items-center gap-1 shadow-2xs"
                >
                  <span>Open Case</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            {/* Risk Score Gauge / Bar */}
            <div>
              <div className="flex items-center justify-between text-xs font-bold mb-1.5">
                <span className="text-slate-600 uppercase tracking-wider text-[11px]">
                  {isHi ? t('msg.aggregated_score') : 'Aggregated Risk Score'}
                </span>
                <span className="font-mono text-sm font-extrabold text-slate-900">
                  {result.risk_score} / 100
                </span>
              </div>
              <div className="w-full h-3 rounded-full bg-slate-100 overflow-hidden p-0.5 border border-slate-200">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    result.risk_level === 'HIGH'
                      ? 'bg-rose-500'
                      : result.risk_level === 'MEDIUM'
                      ? 'bg-amber-500'
                      : 'bg-emerald-500'
                  }`}
                  style={{ width: `${Math.max(5, result.risk_score)}%` }}
                />
              </div>
            </div>
          </div>

          {/* Citizen "What to do next" guidance box */}
          {isCitizen && <CitizenNextSteps riskLevel={result.risk_level} />}

          {/* AI Second Opinion Card */}
          {result.ai_second_opinion && (
            <AISecondOpinionCard opinion={result.ai_second_opinion} />
          )}

          {/* Indicators & Extracted Identifiers Columns */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Left: Flagged Indicators */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 space-y-3">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Explainable Risk Indicators ({result.indicators?.length || 0})
              </h3>
              <IndicatorList indicators={result.indicators} />
            </div>

            {/* Right: Extracted Identifiers & Actionable Guidance */}
            <div className="space-y-5">
              {/* Identifiers */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 space-y-3">
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Extracted Operational Identifiers
                </h3>
                <IdentifierChips identifiers={result.extracted_identifiers} />
              </div>

              {/* Actionable Recommendations */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 space-y-2.5">
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-electric-500" />
                  Recommended Action Steps
                </h3>
                <ul className="space-y-1.5 text-xs text-slate-700">
                  {result.safety_recommendations?.map((rec, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 flex-shrink-0" />
                      <span className="leading-relaxed">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Evidence Hash Card */}
              {result.evidence && (
                <div className="bg-slate-100/70 rounded-xl border border-slate-200 p-4 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-600 uppercase text-[10px] tracking-wider flex items-center gap-1">
                      <Fingerprint className="w-3.5 h-3.5 text-slate-500" /> Content Evidence Hash (SHA-256)
                    </span>
                    <button
                      onClick={() => copyHash(result.evidence.content_sha256)}
                      className="text-[11px] font-semibold text-electric-600 hover:text-electric-700 flex items-center gap-1"
                    >
                      <Copy className="w-3 h-3" />
                      <span>{copiedEvidence ? 'Copied!' : 'Copy'}</span>
                    </button>
                  </div>
                  <p className="font-mono text-[11px] text-slate-700 break-all select-all bg-white p-2 rounded border border-slate-200">
                    {result.evidence.content_sha256}
                  </p>
                  <p className="text-[10px] text-slate-400">
                    UTC Timestamp: {result.evidence.timestamp_utc}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
