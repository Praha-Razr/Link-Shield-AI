import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  Download,
  Search,
  Filter,
  RefreshCw,
  Clock,
  ShieldAlert,
  ShieldCheck,
  CheckCircle,
  FileCheck,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import DemoBadge from '../components/DemoBadge';
import EmptyState from '../components/EmptyState';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';

export default function Reports() {
  const [q, setQ] = useState('');
  const [risk, setRisk] = useState('ALL');
  const [includeDemo, setIncludeDemo] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const [cases, setCases] = useState([]);
  const [totalCases, setTotalCases] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Downloading state tracker { [caseId]: boolean }
  const [downloading, setDownloading] = useState({});
  const [pdfError, setPdfError] = useState(null);

  const fetchCases = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getCases({
        q: q.trim() || undefined,
        risk: risk !== 'ALL' ? risk : undefined,
        include_demo: includeDemo,
        page,
        page_size: pageSize
      });
      setCases(data.cases || []);
      setTotalCases(data.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to load report repository.');
    } finally {
      setLoading(false);
    }
  }, [q, risk, includeDemo, page, pageSize]);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  const handleDownloadPdf = async (caseId) => {
    setDownloading((prev) => ({ ...prev, [caseId]: true }));
    setPdfError(null);
    try {
      await api.downloadCasePdf(caseId);
    } catch (err) {
      setPdfError(`Failed to generate PDF report for case ${caseId}: ${err.message}`);
    } finally {
      setDownloading((prev) => ({ ...prev, [caseId]: false }));
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <FileText className="w-6 h-6 text-primary-600" />
            Investigation PDF Reports & Evidence Export
          </h1>
          <p className="text-slate-600 text-sm mt-1">
            Generate and export official, court-ready cyber crime investigation dossiers with cryptographic hashes and indicator breakdowns.
          </p>
        </div>

        <button
          type="button"
          onClick={fetchCases}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-semibold shadow-xs transition-colors self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {pdfError && (
        <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800 flex items-start justify-between gap-2 shadow-xs">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span className="font-medium">{pdfError}</span>
          </div>
          <button
            type="button"
            onClick={() => setPdfError(null)}
            className="text-rose-500 hover:text-rose-800 font-bold px-1 cursor-pointer"
          >
            &times;
          </button>
        </div>
      )}

      {/* Report Info Banner */}
      <div className="p-4 rounded-xl bg-slate-900 text-white shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 font-mono text-xs text-cyan-400 font-bold">
            <FileCheck className="w-4 h-4" />
            <span>REPORTLAB FORENSIC ENGINE v3.0 ACTIVE</span>
          </div>
          <p className="text-xs text-slate-300">
            PDF dossiers include dual timestamps (UTC &amp; IST), SHA-256 evidence verification, Devanagari Unicode support, indicator point tallies, and cross-case campaign links.
          </p>
        </div>
        <div className="text-xs text-slate-400 border-l border-slate-700 pl-4">
          <div className="font-semibold text-slate-200">LINKSHIELD AI</div>
          <div className="font-mono text-cyan-300">Official Forensic Dossier</div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="relative flex-1 min-w-[220px] max-w-md">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={q}
            onChange={(e) => {
              setQ(e.target.value);
              setPage(1);
            }}
            placeholder="Search by case ID (e.g. LS-0032, DEMO-001) or subject..."
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={risk}
            onChange={(e) => {
              setRisk(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="HIGH">High Risk Only</option>
            <option value="MEDIUM">Medium Risk Only</option>
            <option value="LOW">Low Risk Only</option>
          </select>

          <label className="flex items-center gap-1.5 font-medium text-slate-700 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={includeDemo}
              onChange={(e) => {
                setIncludeDemo(e.target.checked);
                setPage(1);
              }}
              className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
            />
            <span>Include Demo Cases</span>
          </label>
        </div>
      </div>

      {error && <ErrorBanner message={error} />}

      {/* Cases & PDF Generation Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center">
            <LoadingSpinner size="md" message="Loading cases for report export..." />
          </div>
        ) : cases.length === 0 ? (
          <div className="p-8">
            <EmptyState
              title="No cases found"
              description="No investigation cases match your filters. Reset search or load the demo dataset to generate sample PDFs."
              actionText="Reset Filters"
              onAction={() => {
                setQ('');
                setRisk('ALL');
                setIncludeDemo(true);
              }}
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 uppercase font-bold text-slate-600 text-[10px] tracking-wider">
                <tr>
                  <th className="py-3 px-4">Case ID</th>
                  <th className="py-3 px-4">Incident Subject</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Risk Level</th>
                  <th className="py-3 px-4">Score</th>
                  <th className="py-3 px-4">Captured Date</th>
                  <th className="py-3 px-4 text-right">Generate & Download</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {cases.map((c) => {
                  const isBusy = downloading[c.id];
                  return (
                    <tr key={c.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4 whitespace-nowrap font-mono font-bold text-slate-900">
                        <div className="flex items-center gap-1.5">
                          <span>{c.id}</span>
                          {c.is_demo && <DemoBadge />}
                        </div>
                      </td>
                      <td className="py-3 px-4 max-w-xs truncate font-medium text-slate-800">
                        {c.subject || '(No subject recorded)'}
                      </td>
                      <td className="py-3 px-4 uppercase text-[10px] font-semibold text-slate-600">
                        <span className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200">
                          {c.input_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <RiskBadge level={c.risk_level} score={c.risk_score} showScore={false} size="xs" />
                      </td>
                      <td className="py-3 px-4 font-mono font-bold text-slate-800">
                        {c.risk_score}/100
                      </td>
                      <td className="py-3 px-4 text-slate-500 whitespace-nowrap">
                        {new Date(c.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4 text-right whitespace-nowrap">
                        <button
                          type="button"
                          onClick={() => handleDownloadPdf(c.id)}
                          disabled={isBusy}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold text-xs shadow-xs transition-colors disabled:opacity-50 cursor-pointer"
                        >
                          <Download className={`w-3.5 h-3.5 ${isBusy ? 'animate-bounce' : ''}`} />
                          <span>{isBusy ? 'Generating PDF...' : 'Download PDF'}</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        <div className="p-3 bg-slate-50 border-t border-slate-200 text-[11px] text-slate-500 flex justify-between items-center">
          <span>Showing {cases.length} of {totalCases} available cases</span>
          <span>PDF generation runs on-demand via ReportLab</span>
        </div>
      </div>
    </div>
  );
}
