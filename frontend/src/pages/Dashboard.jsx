import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  ShieldCheck,
  Shield,
  Layers,
  Phone,
  PhoneCall,
  Globe,
  Database,
  Trash2,
  RefreshCw,
  ArrowRight,
  TrendingUp,
  FileText,
  AlertTriangle,
  AlertOctagon,
  Briefcase,
  Zap,
  CreditCard,
  Coins,
  CheckCircle2,
  MessageSquareWarning,
  AppWindow,
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import StatCard from '../components/StatCard';
import RiskBadge from '../components/RiskBadge';
import DemoBadge from '../components/DemoBadge';
import EmptyState from '../components/EmptyState';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';
import { api } from '../services/api';
import { useRole } from '../context/RoleContext';
import { useI18n } from '../i18n/I18nContext';

const RISK_COLORS = {
  HIGH: '#ef4444',
  MEDIUM: '#f59e0b',
  LOW: '#10b981',
};

const CATEGORY_META = {
  fake_kyc: { label: 'Fake KYC / Bank Verification', icon: ShieldAlert, color: '#ef4444' },
  job_fraud: { label: 'Part-Time Job & Task Scam', icon: Briefcase, color: '#f59e0b' },
  investment_fraud: { label: 'Ponzi / High-Return Investment', icon: TrendingUp, color: '#ef4444' },
  electricity_scam: { label: 'Electricity Bill Extortion', icon: Zap, color: '#f97316' },
  brand_impersonation_url: { label: 'Brand Impersonation & Phishing', icon: Globe, color: '#dc2626' },
  loan_fraud: { label: 'Instant Loan / Advance Fee', icon: CreditCard, color: '#f59e0b' },
  phishing_link: { label: 'Credential Phishing Links', icon: AlertTriangle, color: '#ef4444' },
  general_analysis: { label: 'Suspicious Raw Analysis', icon: FileText, color: '#64748b' },
  blacklisted_domain: { label: 'Known Blacklisted Domains', icon: ShieldAlert, color: '#b91c1c' },
  blocked_destination: { label: 'Blocked / SSRF Destinations', icon: Shield, color: '#475569' },
  illegal_betting: { label: 'Illegal Betting & Online Satta', icon: Coins, color: '#8b5cf6' },
  parcel_scam: { label: 'Parcel Delivery / Fee Scam', icon: Layers, color: '#f59e0b' },
  mlm_fraud: { label: 'Multi-Level Referral Scheme', icon: TrendingUp, color: '#d97706' },
  genuine_service: { label: 'Verified Benign Notifications', icon: ShieldCheck, color: '#10b981' },
};

const CATEGORY_NAMES_HI = {
  fake_kyc: 'फर्जी बैंक KYC सत्यापन',
  job_fraud: 'पार्ट-टाइम जॉब व टास्क घोटाला',
  investment_fraud: 'पोंजी / भारी मुनाफे का निवेश घोटाला',
  electricity_scam: 'बिजली बिल काटने की धमकी',
  brand_impersonation_url: 'ब्रांड की नकल व फ़िशिंग वेबसाइट',
  loan_fraud: 'तुरंत लोन / प्रोसेसिंग फीस ठगी',
  phishing_link: 'फ़िशिंग लिंक (पासवर्ड चोरी)',
  general_analysis: 'संदिग्ध विश्लेषण',
  blacklisted_domain: 'काली सूची में दर्ज फर्जी डोमेन',
  blocked_destination: 'अवरुद्ध / खतरनाक लिंक',
  illegal_betting: 'अवैध सट्टेबाजी व ऑनलाइन गेमिंग',
  parcel_scam: 'पार्सल डिलीवरी / कस्टम शुल्क ठगी',
  mlm_fraud: 'रेफरल / मल्टी-लेवल मार्केटिंग स्कीम',
  genuine_service: 'सत्यापित सुरक्षित संदेश',
};

export default function Dashboard() {
  const { isCitizen } = useRole();
  const { t, lang } = useI18n();
  const [stats, setStats] = useState(null);
  const [recentCases, setRecentCases] = useState([]);
  const [heatlist, setHeatlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showClearModal, setShowClearModal] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState('threats'); // 'threats' | 'all'

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      if (isCitizen) {
        const awarenessData = await api.getPublicAwareness();
        const catMap = {};
        (awarenessData.categories || []).forEach((c) => {
          catMap[c.category] = c.count;
        });
        setStats({
          total_cases: awarenessData.total_cases,
          high_risk_cases: awarenessData.high_risk_count,
          medium_risk_cases: awarenessData.medium_risk_count,
          low_risk_cases: awarenessData.low_risk_count,
          cases_by_category: catMap,
          category_breakdown: catMap,
          top_threat_vectors: awarenessData.top_threat_vectors || [],
          safety_advisory: awarenessData.safety_advisory || '',
          real_cases: 0,
          demo_cases: 0,
        });
        setRecentCases([]);
        setHeatlist([]);
      } else {
        const [statsData, casesData, heatlistData] = await Promise.all([
          api.getDashboardStats(),
          api.getCases({ page: 1, page_size: 6, include_demo: true }),
          api.getHeatlist({ limit: 5, include_demo: true }),
        ]);
        setStats(statsData);
        setRecentCases(casesData.cases || []);
        setHeatlist(heatlistData.items || []);
      }
    } catch (err) {
      setError(err.message || 'Failed to connect to LinkShield backend API.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleLoadDemo = async () => {
    try {
      setActionLoading(true);
      await api.loadDemoData();
      await fetchDashboardData();
    } catch (err) {
      setError(err.message || 'Failed to load demo dataset.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleClearDemo = async () => {
    try {
      setActionLoading(true);
      await api.clearDemoData();
      setShowClearModal(false);
      await fetchDashboardData();
    } catch (err) {
      setError(err.message || 'Failed to clear demo data.');
    } finally {
      setActionLoading(false);
    }
  };

  const totalCases = stats?.total_cases || 0;
  const highRisk = stats?.high_risk_cases || 0;
  const mediumRisk = stats?.medium_risk_cases || 0;
  const lowRisk = stats?.low_risk_cases || 0;

  // Pie chart data: Risk Distribution
  const riskChartData = useMemo(() => [
    { name: isCitizen && lang === 'hi' ? 'उच्च जोखिम' : 'High Risk', value: highRisk, color: RISK_COLORS.HIGH },
    { name: isCitizen && lang === 'hi' ? 'मध्यम जोखिम' : 'Medium Risk', value: mediumRisk, color: RISK_COLORS.MEDIUM },
    { name: isCitizen && lang === 'hi' ? 'कम जोखिम' : 'Low Risk', value: lowRisk, color: RISK_COLORS.LOW },
  ].filter((d) => d.value > 0), [highRisk, mediumRisk, lowRisk, isCitizen, lang]);

  // Modernized Category Threat Data
  const allCategoryEntries = useMemo(() => {
    const rawCategories = stats?.cases_by_category || stats?.category_breakdown;
    if (!rawCategories) return [];
    return Object.entries(rawCategories)
      .map(([rawCat, count]) => {
        const meta = CATEGORY_META[rawCat] || {
          label: rawCat.replace(/_/g, ' ').toUpperCase(),
          icon: ShieldAlert,
          color: '#3b82f6',
        };
        const isGenuine = rawCat === 'genuine_service';
        const label = (isCitizen && lang === 'hi' && CATEGORY_NAMES_HI[rawCat]) ? CATEGORY_NAMES_HI[rawCat] : meta.label;
        return {
          raw: rawCat,
          label,
          icon: meta.icon,
          color: meta.color,
          count,
          isGenuine,
        };
      })
      .sort((a, b) => b.count - a.count);
  }, [stats, isCitizen, lang]);

  const displayedCategories = useMemo(() => {
    if (categoryFilter === 'threats') {
      const threats = allCategoryEntries.filter((c) => !c.isGenuine);
      return threats.length > 0 ? threats : allCategoryEntries;
    }
    return allCategoryEntries;
  }, [allCategoryEntries, categoryFilter]);

  const maxCatCount = useMemo(() => {
    if (displayedCategories.length === 0) return 1;
    return Math.max(...displayedCategories.map((c) => c.count), 1);
  }, [displayedCategories]);

  if (loading && !stats) {
    return (
      <div className="py-20">
        <LoadingSpinner message="Querying live SQLite database metrics..." size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header & Action Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl md:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>{isCitizen ? t('dash.title') : 'Threat Intelligence Dashboard'}</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            {isCitizen
              ? t('dash.subtitle')
              : 'Real-time telemetry and case analysis repository for cybercrime investigators'}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={fetchDashboardData}
            disabled={actionLoading}
            className="p-2 text-slate-600 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg shadow-2xs text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer"
            title="Refresh database metrics"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${actionLoading ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">{isCitizen ? t('dash.refresh') : 'Refresh'}</span>
          </button>

          {!isCitizen && (
            <>
              <button
                onClick={handleLoadDemo}
                disabled={actionLoading}
                className="px-3 py-2 bg-electric-500 hover:bg-electric-600 text-white rounded-lg shadow-xs text-xs font-semibold flex items-center gap-1.5 transition-all"
              >
                <Database className="w-3.5 h-3.5" />
                <span>Load Demo Data</span>
              </button>

              {stats?.demo_cases > 0 && (
                <button
                  onClick={() => setShowClearModal(true)}
                  disabled={actionLoading}
                  className="px-3 py-2 bg-white text-rose-700 border border-rose-300 hover:bg-rose-50 rounded-lg shadow-2xs text-xs font-semibold flex items-center gap-1.5 transition-all"
                >
                  <Trash2 className="w-3.5 h-3.5 text-rose-600" />
                  <span>Clear Demo</span>
                </button>
              )}
            </>
          )}
        </div>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {/* When no cases exist */}
      {totalCases === 0 ? (
        <EmptyState
          title="Database is Empty"
          description="No cyber cases or scam incidents have been submitted yet. Load the 44-record synthetic demo dataset to inspect live telemetry."
          actionText="Load 44-Record Synthetic Dataset"
          onAction={handleLoadDemo}
        />
      ) : (
        <>
          {/* Key Metric Stat Cards */}
          {isCitizen ? (
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3.5">
              <StatCard
                title={t('dash.total_reports')}
                value={totalCases}
                subtitle={t('dash.total_reports_sub')}
                icon={Layers}
                variant="default"
              />
              <StatCard
                title={t('dash.high_risk')}
                value={highRisk}
                subtitle={t('dash.high_risk_sub')}
                icon={ShieldAlert}
                variant="high"
              />
              <StatCard
                title={t('dash.medium_risk')}
                value={mediumRisk}
                subtitle={t('dash.medium_risk_sub')}
                icon={Shield}
                variant="medium"
              />
              <StatCard
                title={t('dash.low_risk')}
                value={lowRisk}
                subtitle={t('dash.low_risk_sub')}
                icon={ShieldCheck}
                variant="low"
              />
              <StatCard
                title={t('dash.scam_vectors')}
                value={allCategoryEntries.length}
                subtitle={t('dash.scam_vectors_sub')}
                icon={TrendingUp}
                variant="blue"
              />
              <StatCard
                title={t('dash.helpline_label')}
                value="1930"
                subtitle={t('dash.helpline_sub')}
                icon={PhoneCall}
                variant="cyan"
              />
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3.5">
              <StatCard
                title="Total Cases"
                value={totalCases}
                subtitle={`${stats?.real_cases || 0} real, ${stats?.demo_cases || 0} demo`}
                icon={Layers}
                variant="default"
              />
              <StatCard
                title="High Risk"
                value={highRisk}
                subtitle="Critical threat level"
                icon={ShieldAlert}
                variant="high"
              />
              <StatCard
                title="Medium Risk"
                value={mediumRisk}
                subtitle="Suspicious / review"
                icon={Shield}
                variant="medium"
              />
              <StatCard
                title="Low Risk"
                value={lowRisk}
                subtitle="Benign transactional"
                icon={ShieldCheck}
                variant="low"
              />
              <StatCard
                title="Extracted IDs"
                value={stats?.top_identifiers_count || 0}
                subtitle="Domains, phones, UPI"
                icon={Globe}
                variant="blue"
              />
              <StatCard
                title="Shared Hubs"
                value={stats?.total_shared_identifiers || 0}
                subtitle="Appears in >=2 cases"
                icon={TrendingUp}
                variant="cyan"
              />
            </div>
          )}

          {/* Visual Threat Telemetry Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Donut Chart: Risk Level Distribution with Center Stat */}
            <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                    {isCitizen ? t('dash.risk_breakdown') : 'Risk Classification Breakdown'}
                  </h3>
                  <span className="text-[10px] font-mono font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                    {totalCases} {isCitizen ? t('dash.total') : 'Total'}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5 mb-2">
                  {isCitizen ? t('dash.risk_breakdown_desc') : 'Distribution of evaluated threat severity scores'}
                </p>
              </div>

              {/* Chart with center scorecard */}
              <div className="relative flex items-center justify-center my-1">
                <div className="w-full h-[180px]">
                  <ResponsiveContainer width="100%" height={180}>
                    <PieChart>
                      <Pie
                        data={riskChartData}
                        innerRadius={54}
                        outerRadius={76}
                        paddingAngle={3}
                        dataKey="value"
                        stroke="#ffffff"
                        strokeWidth={2}
                      >
                        {riskChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#ffffff',
                          border: '1px solid #e2e8f0',
                          borderRadius: '10px',
                          color: '#0f172a',
                          fontSize: '12px',
                          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                        }}
                        formatter={(val, name) => [
                          `${val} ${isCitizen ? t('dash.cases') : 'cases'} (${Math.round((val / (totalCases || 1)) * 100)}%)`,
                          name,
                        ]}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Center Scorecard Text */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-2xl font-black text-slate-900 font-mono tracking-tight">
                    {totalCases}
                  </span>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    {isCitizen ? t('dash.cases') : 'Cases'}
                  </span>
                </div>
              </div>

              {/* Modernized Legend */}
              <div className="grid grid-cols-3 gap-2 pt-3 border-t border-slate-100 text-center">
                <div className="p-2 rounded-lg bg-rose-50/70 border border-rose-100">
                  <div className="flex items-center justify-center gap-1 text-[10px] font-bold text-rose-700 uppercase">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                    {isCitizen && lang === 'hi' ? 'उच्च' : 'High'}
                  </div>
                  <div className="font-mono text-sm font-black text-rose-800 mt-0.5">
                    {highRisk}
                  </div>
                  <div className="text-[10px] text-rose-600 font-semibold">
                    {Math.round((highRisk / (totalCases || 1)) * 100)}%
                  </div>
                </div>

                <div className="p-2 rounded-lg bg-amber-50/70 border border-amber-100">
                  <div className="flex items-center justify-center gap-1 text-[10px] font-bold text-amber-700 uppercase">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                    {isCitizen && lang === 'hi' ? 'मध्यम' : 'Medium'}
                  </div>
                  <div className="font-mono text-sm font-black text-amber-800 mt-0.5">
                    {mediumRisk}
                  </div>
                  <div className="text-[10px] text-amber-600 font-semibold">
                    {Math.round((mediumRisk / (totalCases || 1)) * 100)}%
                  </div>
                </div>

                <div className="p-2 rounded-lg bg-emerald-50/70 border border-emerald-100">
                  <div className="flex items-center justify-center gap-1 text-[10px] font-bold text-emerald-700 uppercase">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    {isCitizen && lang === 'hi' ? 'कम' : 'Low'}
                  </div>
                  <div className="font-mono text-sm font-black text-emerald-800 mt-0.5">
                    {lowRisk}
                  </div>
                  <div className="text-[10px] text-emerald-600 font-semibold">
                    {Math.round((lowRisk / (totalCases || 1)) * 100)}%
                  </div>
                </div>
              </div>
            </div>

            {/* Modernized Category Threat Spectrum (No Overlapping Labels!) */}
            <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-xs flex flex-col lg:col-span-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-1.5">
                    <span>{isCitizen ? t('dash.spectrum_title') : 'Scam Categories & Threat Breakdown'}</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {isCitizen ? t('dash.spectrum_desc') : 'Incident frequency grouped by scam type and deceptive pattern'}
                  </p>
                </div>

                {/* Filter Toggle */}
                <div className="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-50 text-[11px] self-start sm:self-auto">
                  <button
                    type="button"
                    onClick={() => setCategoryFilter('threats')}
                    className={`px-2.5 py-1 rounded-md font-semibold transition-all cursor-pointer ${
                      categoryFilter === 'threats'
                        ? 'bg-white text-blue-700 shadow-2xs'
                        : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    {isCitizen ? t('dash.filter_threats') : 'Scam Threats'} ({allCategoryEntries.filter((c) => !c.isGenuine).length})
                  </button>
                  <button
                    type="button"
                    onClick={() => setCategoryFilter('all')}
                    className={`px-2.5 py-1 rounded-md font-semibold transition-all cursor-pointer ${
                      categoryFilter === 'all'
                        ? 'bg-white text-blue-700 shadow-2xs'
                        : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    {isCitizen ? t('dash.filter_all') : 'All'} ({allCategoryEntries.length})
                  </button>
                </div>
              </div>

              {/* Ranked Horizontal Category Bars */}
              <div className="flex-1 space-y-2 overflow-y-auto max-h-[260px] pr-1">
                {displayedCategories.length === 0 ? (
                  <div className="h-44 flex flex-col items-center justify-center text-center p-4">
                    <ShieldAlert className="w-8 h-8 text-slate-300 mb-2" />
                    <p className="text-xs font-semibold text-slate-600">No scam categories recorded yet</p>
                    <p className="text-[11px] text-slate-400 mt-0.5">Scam incident patterns will appear here once reports are logged.</p>
                  </div>
                ) : (
                  displayedCategories.map((item, idx) => {
                  const Icon = item.icon;
                  const pct = Math.round((item.count / maxCatCount) * 100);

                  return (
                    <div
                      key={item.raw}
                      className="group p-2 rounded-lg border border-slate-100 hover:border-slate-300 hover:bg-slate-50/70 transition-all flex flex-col gap-1.5"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2 font-medium text-slate-800 truncate">
                          <span
                            className="p-1 rounded-md"
                            style={{ backgroundColor: `${item.color}15`, color: item.color }}
                          >
                            <Icon className="w-3.5 h-3.5 shrink-0" />
                          </span>
                          <span className="truncate font-semibold text-slate-800 text-[11px] sm:text-xs">
                            {item.label}
                          </span>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          <span className="font-mono font-bold text-slate-900 text-xs">
                            {item.count} {item.count === 1 ? 'case' : 'cases'}
                          </span>
                          <span className="text-[10px] text-slate-400 font-mono w-9 text-right">
                            {Math.round((item.count / (totalCases || 1)) * 100)}%
                          </span>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-500"
                          style={{
                            width: `${Math.max(pct, 5)}%`,
                            backgroundColor: item.color,
                          }}
                        />
                      </div>
                    </div>
                  );
                }))}
              </div>

              <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                <span>{isCitizen ? t('dash.ranked_by') : 'Ranked by verified complaint frequency'}</span>
                {isCitizen ? (
                  <span className="font-semibold text-slate-600">
                    {t('dash.concern_prompt')}
                  </span>
                ) : (
                  <Link
                    to="/cases"
                    className="font-semibold text-blue-600 hover:underline flex items-center gap-1"
                  >
                    Inspect in Case Management &rarr;
                  </Link>
                )}
              </div>
            </div>
          </div>

          {/* Bottom Section: Citizen Safety Advisories vs Officer Threat Registries */}
          {isCitizen ? (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              {/* Left: 4 Golden Cyber Hygiene Rules */}
              <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-xs space-y-3">
                <div className="flex items-center gap-2 text-slate-900 pb-2 border-b border-slate-100">
                  <ShieldCheck className="w-5 h-5 text-emerald-600" />
                  <h3 className="text-sm font-bold tracking-tight">{t('dash.rules_title')}</h3>
                </div>
                <ul className="space-y-3 text-xs text-slate-600">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>
                      <strong className="text-slate-800">{t('dash.rule1_title')}</strong> {t('dash.rule1_body')}
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>
                      <strong className="text-slate-800">{t('dash.rule2_title')}</strong> {t('dash.rule2_body')}
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>
                      <strong className="text-slate-800">{t('dash.rule3_title')}</strong> {t('dash.rule3_body')}
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>
                      <strong className="text-slate-800">{t('dash.rule4_title')}</strong> {t('dash.rule4_body')}
                    </span>
                  </li>
                </ul>
              </div>

              {/* Right: Active Scam Awareness Advisories & Quick Scanners */}
              <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-xs lg:col-span-2 space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
                    <AlertOctagon className="w-4 h-4 text-rose-600" />
                    <span>{t('dash.guidance_title')}</span>
                  </h3>
                  <span className="text-[10px] uppercase font-bold text-slate-400">{t('dash.public_advisory')}</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <Link
                    to="/analyze/message"
                    className="p-3.5 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50/50 transition-all flex flex-col justify-between group"
                  >
                    <div>
                      <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center mb-2">
                        <MessageSquareWarning className="w-4 h-4" />
                      </div>
                      <h4 className="text-xs font-bold text-slate-900 group-hover:text-blue-700">{t('dash.guide_msg_title')}</h4>
                      <p className="text-[11px] text-slate-500 mt-1">{t('dash.guide_msg_desc')}</p>
                    </div>
                    <span className="text-[11px] font-semibold text-blue-600 mt-3 flex items-center gap-1">{t('dash.guide_msg_action')}</span>
                  </Link>

                  <Link
                    to="/analyze/url"
                    className="p-3.5 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50/50 transition-all flex flex-col justify-between group"
                  >
                    <div>
                      <div className="w-8 h-8 rounded-lg bg-cyan-100 text-cyan-700 flex items-center justify-center mb-2">
                        <Globe className="w-4 h-4" />
                      </div>
                      <h4 className="text-xs font-bold text-slate-900 group-hover:text-blue-700">{t('dash.guide_link_title')}</h4>
                      <p className="text-[11px] text-slate-500 mt-1">{t('dash.guide_link_desc')}</p>
                    </div>
                    <span className="text-[11px] font-semibold text-blue-600 mt-3 flex items-center gap-1">{t('dash.guide_link_action')}</span>
                  </Link>

                  <Link
                    to="/analyze/website"
                    className="p-3.5 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50/50 transition-all flex flex-col justify-between group"
                  >
                    <div>
                      <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center mb-2">
                        <AppWindow className="w-4 h-4" />
                      </div>
                      <h4 className="text-xs font-bold text-slate-900 group-hover:text-blue-700">{t('dash.guide_web_title')}</h4>
                      <p className="text-[11px] text-slate-500 mt-1">{t('dash.guide_web_desc')}</p>
                    </div>
                    <span className="text-[11px] font-semibold text-blue-600 mt-3 flex items-center gap-1">{t('dash.guide_web_action')}</span>
                  </Link>
                </div>

                <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <PhoneCall className="w-4 h-4 text-rose-600 shrink-0" />
                    <span>{t('dash.victim_banner')}</span>
                  </div>
                  <a
                    href="https://cybercrime.gov.in"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-2.5 py-1 rounded bg-rose-600 hover:bg-rose-700 text-white font-bold text-[10px] uppercase tracking-wider shrink-0 transition-colors"
                  >
                    {t('dash.cybercrime_btn')}
                  </a>
                </div>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              {/* Left: Frequently Reported Identifiers (Top Hubs) */}
              <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-xs">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                    Frequently Reported Entities
                  </h3>
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold">
                    Top Hubs
                  </span>
                </div>
                <p className="text-xs text-slate-400 mb-4 leading-relaxed">
                  Identifiers repeatedly linked across independent scam cases.
                </p>

                {heatlist.length === 0 ? (
                  <p className="text-xs text-slate-400 italic">No repeated identifiers detected yet.</p>
                ) : (
                  <div className="space-y-2.5">
                    {heatlist.map((item) => (
                      <div
                        key={item.identifier_id}
                        className="p-3 rounded-lg border border-slate-100 bg-slate-50 flex items-center justify-between"
                      >
                        <div className="truncate mr-2">
                          <span className="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">
                            {item.type}
                          </span>
                          <span className="text-xs font-mono font-semibold text-slate-800 truncate block">
                            {item.value}
                          </span>
                        </div>
                        <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-electric-500/10 text-electric-600 border border-electric-500/20 whitespace-nowrap">
                          {item.distinct_case_count} cases
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Right: Recent Investigations Table */}
              <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-xs lg:col-span-2">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                    Recent Threat Submissions
                  </h3>
                  <Link
                    to="/cases"
                    target="_self"
                    className="text-xs font-semibold text-electric-500 hover:text-electric-600 flex items-center gap-1"
                  >
                    View All Cases
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] tracking-wider border-y border-slate-200">
                      <tr>
                        <th className="py-2.5 px-3">Case ID</th>
                        <th className="py-2.5 px-3">Subject / Incident</th>
                        <th className="py-2.5 px-3">Type</th>
                        <th className="py-2.5 px-3">Risk</th>
                        <th className="py-2.5 px-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {recentCases.map((c) => (
                        <tr key={c.id} className="hover:bg-slate-50/60 transition-colors">
                          <td className="py-2.5 px-3 font-mono font-bold text-slate-900 flex items-center gap-1.5">
                            <span>{c.id}</span>
                            {c.is_demo && <DemoBadge />}
                          </td>
                          <td className="py-2.5 px-3 text-slate-800 font-medium max-w-xs truncate">
                            {c.subject || 'Analysis Record'}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-100 text-slate-700">
                              {c.input_type}
                            </span>
                          </td>
                          <td className="py-2.5 px-3">
                            <RiskBadge level={c.risk_level} score={c.risk_score} size="sm" />
                          </td>
                          <td className="py-2.5 px-3 text-right">
                            <Link
                              to={`/cases?open=${c.id}`}
                              target="_self"
                              className="text-electric-500 hover:text-electric-600 font-semibold"
                            >
                              Inspect
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Confirmation Modal for Clearing Demo Data */}
      {showClearModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/70 backdrop-blur-xs">
          <div className="w-full max-w-md bg-white rounded-xl shadow-xl border border-slate-200 p-6 space-y-4 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center gap-3 text-rose-600">
              <div className="p-3 rounded-full bg-rose-100">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  Clear Synthetic Demo Data?
                </h3>
                <p className="text-xs text-slate-500">
                  This action requires explicit confirmation.
                </p>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              This will permanently delete all <strong>{stats?.demo_cases || 0}</strong> demo records
              and associated demo identifiers from the SQLite database. Any real, non-demo investigation cases
              you submitted will be safely preserved.
            </p>

            <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100">
              <button
                onClick={() => setShowClearModal(false)}
                className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleClearDemo}
                disabled={actionLoading}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-rose-600 hover:bg-rose-700 text-white shadow-xs transition-colors"
              >
                {actionLoading ? 'Deleting...' : 'Confirm Clear'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
