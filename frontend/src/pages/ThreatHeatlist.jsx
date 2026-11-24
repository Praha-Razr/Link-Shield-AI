import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Flame,
  Search,
  RefreshCw,
  ExternalLink,
  Phone,
  AtSign,
  Globe,
  Mail,
  AlertTriangle,
  Info,
  Calendar,
  ArrowUpDown,
  BarChart3,
  Copy,
  Check,
  ShieldAlert,
  FolderOpen,
  X,
  Clock,
  ChevronRight
} from 'lucide-react';
import { api } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import DemoBadge from '../components/DemoBadge';
import EmptyState from '../components/EmptyState';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';

const TABS = [
  { key: 'domain', label: 'Domains', icon: Globe, color: '#2563EB', bg: 'bg-blue-50 text-blue-700 border-blue-200' },
  { key: 'phone', label: 'Phones', icon: Phone, color: '#059669', bg: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  { key: 'upi', label: 'UPI IDs', icon: AtSign, color: '#7C3AED', bg: 'bg-purple-50 text-purple-700 border-purple-200' },
  { key: 'email', label: 'Emails', icon: Mail, color: '#D97706', bg: 'bg-amber-50 text-amber-700 border-amber-200' },
];

export default function ThreatHeatlist() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('domain');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('frequency'); // 'frequency' | 'last_seen'
  const [includeDemo, setIncludeDemo] = useState(true);

  // Summary items for the 4 top cards
  const [summaryData, setSummaryData] = useState({
    domain: null,
    phone: null,
    upi: null,
    email: null,
  });

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Copy state tracker
  const [copiedVal, setCopiedVal] = useState(null);

  // Selected identifier for "View cases" drawer
  const [inspectItem, setInspectItem] = useState(null);

  // Fetch summary top cards across all 4 categories
  const fetchSummaryCards = useCallback(async () => {
    try {
      const results = await Promise.all(
        TABS.map((t) =>
          api.getHeatlist({
            type: t.key,
            include_demo: includeDemo,
            limit: 1,
          })
        )
      );

      setSummaryData({
        domain: results[0]?.items?.[0] || null,
        phone: results[1]?.items?.[0] || null,
        upi: results[2]?.items?.[0] || null,
        email: results[3]?.items?.[0] || null,
      });
    } catch (e) {
      console.warn('Could not load summary cards:', e);
    }
  }, [includeDemo]);

  // Fetch heatlist data for active tab
  const fetchHeatlist = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getHeatlist({
        type: activeTab,
        include_demo: includeDemo,
        limit: 100,
      });
      setItems(data.items || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch threat heat-list data.');
    } finally {
      setLoading(false);
    }
  }, [activeTab, includeDemo]);

  useEffect(() => {
    fetchSummaryCards();
  }, [fetchSummaryCards]);

  useEffect(() => {
    fetchHeatlist();
  }, [fetchHeatlist]);

  // Handle copy value
  const handleCopy = (val) => {
    navigator.clipboard?.writeText(val);
    setCopiedVal(val);
    setTimeout(() => setCopiedVal(null), 2000);
  };

  // Helper to get highest risk string
  const getHighestRisk = (riskSummary) => {
    if (!riskSummary) return 'LOW';
    if (riskSummary.HIGH && riskSummary.HIGH > 0) return 'HIGH';
    if (riskSummary.MEDIUM && riskSummary.MEDIUM > 0) return 'MEDIUM';
    return 'LOW';
  };

  // Filter and sort items
  const processedItems = useMemo(() => {
    let list = [...items];

    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      list = list.filter((item) => item.value.toLowerCase().includes(q));
    }

    if (sortBy === 'frequency') {
      list.sort((a, b) => b.distinct_case_count - a.distinct_case_count);
    } else if (sortBy === 'last_seen') {
      list.sort((a, b) => new Date(b.latest_seen || 0) - new Date(a.latest_seen || 0));
    }

    return list;
  }, [items, searchTerm, sortBy]);

  // Top count for mini frequency bar calculation
  const maxCasesCount = useMemo(() => {
    if (processedItems.length === 0) return 1;
    return Math.max(...processedItems.map((i) => i.distinct_case_count), 1);
  }, [processedItems]);

  // Horizontal bar chart data for top 10 items in current tab
  const chartData = useMemo(() => {
    return processedItems.slice(0, 10).map((item, idx) => ({
      rank: `#${idx + 1}`,
      name: item.value.length > 20 ? item.value.substring(0, 18) + '...' : item.value,
      fullValue: item.value,
      cases: item.distinct_case_count,
      highestRisk: getHighestRisk(item.risk_summary),
      riskSummary: item.risk_summary,
    }));
  }, [processedItems]);

  const activeTabMeta = TABS.find((t) => t.key === activeTab) || TABS[0];
  const CurrentIcon = activeTabMeta.icon;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Flame className="w-6 h-6 text-rose-500" />
            Threat Heat-List & Criminal Infrastructure Registry
          </h1>
          <p className="text-slate-600 text-sm mt-1">
            Real-time ranked surveillance of repeatedly reported domains, phone numbers, UPI handles, and emails.
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            fetchSummaryCards();
            fetchHeatlist();
          }}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-semibold shadow-xs transition-colors self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* TOP SUMMARY CARDS: Most Reported Domain, Phone, UPI ID, Email */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {TABS.map((tab) => {
          const item = summaryData[tab.key];
          const Icon = tab.icon;
          const isSelectedTab = activeTab === tab.key;
          const riskLevel = item ? getHighestRisk(item.risk_summary) : 'LOW';

          return (
            <div
              key={tab.key}
              onClick={() => {
                setActiveTab(tab.key);
                setSearchTerm('');
              }}
              className={`p-4 rounded-xl border transition-all cursor-pointer shadow-xs relative overflow-hidden ${
                isSelectedTab
                  ? 'bg-white border-blue-500 ring-2 ring-blue-500/20'
                  : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Icon className="w-4 h-4" style={{ color: tab.color }} />
                  Top {tab.label.slice(0, -1)}
                </span>
                {item && <RiskBadge level={riskLevel} showScore={false} size="xs" />}
              </div>

              {item ? (
                <>
                  <div
                    className="font-mono text-sm font-bold text-slate-900 truncate"
                    title={item.value}
                  >
                    {item.value}
                  </div>
                  <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-100 text-xs">
                    <span className="font-semibold text-slate-700">
                      {item.distinct_case_count} distinct cases
                    </span>
                    <span className="text-[11px] text-blue-600 font-medium hover:underline flex items-center gap-0.5">
                      View tab <ChevronRight className="w-3 h-3" />
                    </span>
                  </div>
                </>
              ) : (
                <div className="text-xs text-slate-400 italic py-2">
                  No reported {tab.label.toLowerCase()} recorded yet
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Statutory Guidance Notice (Rule 7) */}
      <div className="p-3.5 rounded-xl bg-blue-50/70 border border-blue-200 text-blue-900 text-xs flex items-start gap-2.5 shadow-2xs">
        <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
        <div>
          <strong>Investigative Caution:</strong> Identifiers listed below represent infrastructure <em>frequently reported</em> across analyzed cases. Repeated reporting does not by itself prove criminal wrongdoing; findings must be independently verified by a human investigator before initiating legal or takedown proceedings.
        </div>
      </div>

      {/* Tabs & Controls Toolbar */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Identifier Type Tabs */}
        <div className="flex border-b border-slate-200 bg-slate-50/70 gap-1 px-3 pt-2 overflow-x-auto">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                type="button"
                onClick={() => {
                  setActiveTab(tab.key);
                  setSearchTerm('');
                }}
                className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold border-b-2 transition-colors whitespace-nowrap cursor-pointer rounded-t-lg ${
                  isActive
                    ? 'border-blue-600 text-blue-700 bg-white shadow-2xs'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
                }`}
              >
                <Icon className="w-4 h-4" style={{ color: isActive ? tab.color : undefined }} />
                <span>{tab.label}</span>
                {summaryData[tab.key] && (
                  <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] bg-slate-100 text-slate-600 font-mono">
                    {summaryData[tab.key].distinct_case_count} max
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Filters Toolbar */}
        <div className="p-4 bg-white border-b border-slate-100 flex flex-wrap items-center justify-between gap-4 text-xs">
          {/* Search Box */}
          <div className="relative flex-1 min-w-[220px] max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <Search className="w-4 h-4" />
            </div>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={`Filter ${activeTabMeta.label.toLowerCase()}...`}
              className="w-full pl-9 pr-8 py-2 rounded-lg border border-slate-300 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            />
            {searchTerm && (
              <button
                type="button"
                onClick={() => setSearchTerm('')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 cursor-pointer"
              >
                &times;
              </button>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-4">
            {/* Sort Dropdown */}
            <div className="flex items-center gap-1.5">
              <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
              <span className="font-semibold text-slate-700">Sort:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg border border-slate-300 text-xs bg-white text-slate-800 focus:ring-2 focus:ring-blue-500"
              >
                <option value="frequency">Report Frequency (High to Low)</option>
                <option value="last_seen">Recently Reported (Newest First)</option>
              </select>
            </div>

            {/* Include Demo Toggle */}
            <label className="flex items-center gap-2 cursor-pointer font-medium text-slate-700 select-none">
              <input
                type="checkbox"
                checked={includeDemo}
                onChange={(e) => setIncludeDemo(e.target.checked)}
                className="rounded border-slate-300 text-primary-600 focus:ring-primary-500 h-4 w-4"
              />
              <span>Include Demo Data</span>
            </label>
          </div>
        </div>

        {/* Tab Content: Side-by-Side (Chart on Left, Table on Right) */}
        <div className="p-4 sm:p-6 bg-slate-50/50">
          {loading ? (
            <div className="py-20 text-center">
              <LoadingSpinner size="lg" message={`Loading threat registry for ${activeTabMeta.label}...`} />
            </div>
          ) : error ? (
            <ErrorBanner message={error} />
          ) : processedItems.length === 0 ? (
            <div className="bg-white rounded-xl p-8 border border-slate-200">
              <EmptyState
                icon={CurrentIcon}
                title={`No ${activeTabMeta.label} Found`}
                description={
                  searchTerm
                    ? `No ${activeTabMeta.label.toLowerCase()} matching "${searchTerm}". Try resetting your search filter.`
                    : `No repeated ${activeTabMeta.label.toLowerCase()} currently meet the reporting threshold.`
                }
              />
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              {/* LEFT COLUMN: Modern Ranked Threat Visualizer (NO black box popup, NO #1, 2, 3 confusion!) */}
              <div className="lg:col-span-5 bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
                      <BarChart3 className="w-4 h-4 text-primary-600" />
                      <span>Top 10 Frequent {activeTabMeta.label}</span>
                    </h3>
                    <span className="text-[10px] text-slate-400 font-mono uppercase font-bold">
                      Click to Inspect
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mb-3">
                    Entities ranked by count of independent victim cases reported.
                  </p>
                </div>

                {/* Ranked Frequency Cards List */}
                <div className="space-y-2 overflow-y-auto max-h-[380px] pr-1">
                  {processedItems.slice(0, 10).map((item, idx) => {
                    const rank = idx + 1;
                    const riskLevel = getHighestRisk(item.risk_summary);
                    const pct = Math.round((item.distinct_case_count / maxCasesCount) * 100);
                    const isSelected = inspectItem?.value === item.value;

                    return (
                      <div
                        key={item.value || idx}
                        onClick={() => setInspectItem(item)}
                        className={`group p-2.5 rounded-lg border transition-all cursor-pointer flex flex-col gap-1.5 ${
                          isSelected
                            ? 'bg-blue-50/80 border-blue-400 ring-1 ring-blue-400/40'
                            : 'bg-white hover:bg-slate-50 border-slate-200/80 hover:border-slate-300 shadow-2xs'
                        }`}
                      >
                        {/* Header: Rank + Value + Cases Pill */}
                        <div className="flex items-center justify-between gap-2 text-xs">
                          <div className="flex items-center gap-1.5 min-w-0">
                            <span
                              className={`w-5 h-5 rounded-full flex items-center justify-center font-mono text-[10px] font-bold shrink-0 ${
                                rank === 1
                                  ? 'bg-rose-500 text-white'
                                  : rank <= 3
                                  ? 'bg-amber-500 text-white'
                                  : 'bg-slate-200 text-slate-700'
                              }`}
                            >
                              #{rank}
                            </span>
                            <span
                              className="font-mono font-bold text-slate-900 truncate text-[11px] group-hover:text-blue-600"
                              title={item.value}
                            >
                              {item.value}
                            </span>
                          </div>

                          <div className="flex items-center gap-1.5 shrink-0">
                            <span className="font-mono font-bold text-slate-800 text-xs">
                              {item.distinct_case_count} {item.distinct_case_count === 1 ? 'case' : 'cases'}
                            </span>
                            <RiskBadge level={riskLevel} showScore={false} size="xs" />
                          </div>
                        </div>

                        {/* Visual Gradient Progress Bar */}
                        <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-300"
                            style={{
                              width: `${Math.max(pct, 6)}%`,
                              backgroundColor:
                                rank === 1 ? '#EF4444' : rank <= 3 ? '#F59E0B' : activeTabMeta.color,
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Footer Legend */}
                <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-rose-500" /> #1 Critical
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-amber-500" /> Top 3
                    </span>
                  </div>
                  <span className="font-mono text-[10px]">Direct values • No popups</span>
                </div>
              </div>

              {/* RIGHT COLUMN: Clean Ranked Registry Table */}
              <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden flex flex-col">
                <div className="p-4 border-b border-slate-100 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs uppercase tracking-wider text-slate-800">
                      Ranked Registry
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-slate-100 text-slate-600">
                      {processedItems.length} entities
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-400">Click row or action to inspect</span>
                </div>

                <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 sticky top-0 z-10">
                      <tr>
                        <th className="py-2.5 px-3 w-12 text-center">Rank</th>
                        <th className="py-2.5 px-3">Identifier Value</th>
                        <th className="py-2.5 px-3">Frequency</th>
                        <th className="py-2.5 px-3">Risk Level</th>
                        <th className="py-2.5 px-3">Last Reported</th>
                        <th className="py-2.5 px-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {processedItems.map((item, idx) => {
                        const rank = idx + 1;
                        const riskLevel = getHighestRisk(item.risk_summary);
                        const pctOfMax = Math.round((item.distinct_case_count / maxCasesCount) * 100);
                        const isCopied = copiedVal === item.value;

                        return (
                          <tr
                            key={item.identifier_id || `${item.value}-${idx}`}
                            className="hover:bg-slate-50/80 transition-colors"
                          >
                            {/* Rank */}
                            <td className="py-3 px-3 text-center whitespace-nowrap">
                              <span
                                className={`inline-flex items-center justify-center w-6 h-6 rounded-full font-mono text-[11px] font-bold ${
                                  rank === 1
                                    ? 'bg-rose-100 text-rose-700 ring-1 ring-rose-300'
                                    : rank === 2
                                    ? 'bg-amber-100 text-amber-700'
                                    : rank === 3
                                    ? 'bg-amber-50 text-amber-600'
                                    : 'bg-slate-100 text-slate-600'
                                }`}
                              >
                                #{rank}
                              </span>
                            </td>

                            {/* Value with copy */}
                            <td className="py-3 px-3">
                              <div className="flex items-center gap-1.5 max-w-[240px]">
                                <span
                                  className="font-mono font-bold text-slate-900 truncate"
                                  title={item.value}
                                >
                                  {item.value}
                                </span>
                                <button
                                  type="button"
                                  onClick={() => handleCopy(item.value)}
                                  className="p-1 rounded text-slate-400 hover:text-slate-600 hover:bg-slate-100 cursor-pointer"
                                  title="Copy to clipboard"
                                >
                                  {isCopied ? (
                                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                                  ) : (
                                    <Copy className="w-3.5 h-3.5" />
                                  )}
                                </button>
                              </div>
                            </td>

                            {/* Mini Frequency Bar & Count */}
                            <td className="py-3 px-3 whitespace-nowrap">
                              <div className="flex items-center gap-2">
                                <div className="w-16 h-2 bg-slate-100 rounded-full overflow-hidden">
                                  <div
                                    className="h-full rounded-full"
                                    style={{
                                      width: `${pctOfMax}%`,
                                      backgroundColor:
                                        rank === 1 ? '#EF4444' : rank < 4 ? '#F59E0B' : activeTabMeta.color,
                                    }}
                                  />
                                </div>
                                <span className="font-mono font-bold text-slate-800 text-[11px]">
                                  {item.distinct_case_count}
                                </span>
                              </div>
                            </td>

                            {/* Risk Level */}
                            <td className="py-3 px-3 whitespace-nowrap">
                              <RiskBadge level={riskLevel} showScore={false} size="xs" />
                            </td>

                            {/* Last Reported */}
                            <td className="py-3 px-3 whitespace-nowrap text-slate-500 text-[11px]">
                              {item.latest_seen
                                ? new Date(item.latest_seen).toLocaleDateString()
                                : 'Recent'}
                            </td>

                            {/* Action: View Cases */}
                            <td className="py-3 px-3 text-right whitespace-nowrap">
                              <button
                                type="button"
                                onClick={() => setInspectItem(item)}
                                className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold text-[11px] transition-colors cursor-pointer"
                                title={`Inspect all ${item.distinct_case_count} connected cases`}
                              >
                                <FolderOpen className="w-3 h-3" />
                                <span>View Cases</span>
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                <div className="p-3 bg-slate-50 border-t border-slate-100 text-[11px] text-slate-500 flex items-center justify-between">
                  <span>Showing top {processedItems.length} entries</span>
                  <span className="font-mono text-[10px]">Filter &amp; order updated live</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* INSPECT CONNECTED CASES DRAWER */}
      {inspectItem && (
        <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/60 backdrop-blur-xs flex justify-end">
          <div className="w-full max-w-lg bg-white h-full shadow-2xl flex flex-col transform transition-transform duration-200">
            {/* Header */}
            <div className="p-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
              <div className="flex items-center gap-2">
                <CurrentIcon className="w-5 h-5 text-cyan-400" />
                <div>
                  <div className="font-mono text-xs uppercase tracking-wider text-slate-400">
                    {activeTabMeta.label.slice(0, -1)} Dossier
                  </div>
                  <div className="font-mono text-sm font-bold text-white truncate max-w-xs">
                    {inspectItem.value}
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setInspectItem(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Body */}
            <div className="flex-1 overflow-y-auto p-5 space-y-5">
              {/* Summary Stats */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="text-[10px] font-bold uppercase text-slate-500">Connected Cases</div>
                  <div className="text-xl font-bold font-mono text-slate-900 mt-0.5">
                    {inspectItem.distinct_case_count}
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="text-[10px] font-bold uppercase text-slate-500">Assessed Threat</div>
                  <div className="mt-1">
                    <RiskBadge level={getHighestRisk(inspectItem.risk_summary)} showScore={false} size="sm" />
                  </div>
                </div>
              </div>

              {/* Risk Breakdown */}
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
                <div className="text-[10px] font-bold uppercase text-slate-600">Risk Distribution</div>
                <div className="flex items-center gap-4 text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-red-500" />
                    <span>High Risk: {inspectItem.risk_summary?.HIGH || 0}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                    <span>Medium Risk: {inspectItem.risk_summary?.MEDIUM || 0}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                    <span>Low Risk: {inspectItem.risk_summary?.LOW || 0}</span>
                  </div>
                </div>
              </div>

              {/* Connected Cases List */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                    Linked Case Records ({inspectItem.case_ids?.length || 0})
                  </h4>
                  <span className="text-[11px] text-slate-500">Click to open case</span>
                </div>

                <div className="space-y-2">
                  {(inspectItem.case_ids || []).map((cid) => (
                    <div
                      key={cid}
                      onClick={() => {
                        setInspectItem(null);
                        navigate(`/cases?open=${cid}`);
                      }}
                      className="p-3 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50/40 transition-colors cursor-pointer flex items-center justify-between"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-xs text-blue-700">{cid}</span>
                          {cid.startsWith('DEMO') && <DemoBadge />}
                        </div>
                        <div className="text-[11px] text-slate-500">
                          Shares infrastructure with {inspectItem.value}
                        </div>
                      </div>
                      <span className="text-xs font-bold text-blue-600 flex items-center gap-1 hover:underline">
                        Open <ChevronRight className="w-3.5 h-3.5" />
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex justify-between items-center">
              <Link
                to={`/cases?q=${encodeURIComponent(inspectItem.value)}`}
                className="text-xs font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1"
              >
                <span>Filter all cases in Case Management</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </Link>
              <button
                type="button"
                onClick={() => setInspectItem(null)}
                className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-100 cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
