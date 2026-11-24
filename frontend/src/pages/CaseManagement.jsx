import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  FolderKanban,
  Search,
  Filter,
  RefreshCw,
  ExternalLink,
  X,
  Save,
  Clock,
  Hash,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Link as LinkIcon,
  Copy,
  Check,
  FileText,
  UserCheck,
  Download,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import DemoBadge from '../components/DemoBadge';
import IndicatorList from '../components/IndicatorList';
import IdentifierChips from '../components/IdentifierChips';
import AISecondOpinionCard from '../components/AISecondOpinionCard';
import EmptyState from '../components/EmptyState';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';

export default function CaseManagement() {
  const [searchParams, setSearchParams] = useSearchParams();
  const openCaseIdFromUrl = searchParams.get('open');

  // Filters & Pagination state
  const [q, setQ] = useState('');
  const [risk, setRisk] = useState('ALL');
  const [inputType, setInputType] = useState('ALL');
  const [category, setCategory] = useState('ALL');
  const [includeDemo, setIncludeDemo] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);

  // Data state
  const [cases, setCases] = useState([]);
  const [totalCases, setTotalCases] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Drawer / Detail state
  const [selectedCaseId, setSelectedCaseId] = useState(openCaseIdFromUrl || null);
  const [caseDetail, setCaseDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [detailError, setDetailError] = useState(null);

  // Investigator notes editing state
  const [notes, setNotes] = useState('');
  const [savingNotes, setSavingNotes] = useState(false);
  const [notesSavedSuccess, setNotesSavedSuccess] = useState(false);

  // Copy state for hashes
  const [copiedHash, setCopiedHash] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [pdfError, setPdfError] = useState(null);

  const handleDownloadPdf = async (caseId) => {
    if (!caseId) return;
    setDownloadingPdf(true);
    setPdfError(null);
    try {
      await api.downloadCasePdf(caseId);
    } catch (err) {
      setPdfError(`Failed to generate PDF dossier for case ${caseId}: ${err.message}`);
    } finally {
      setDownloadingPdf(false);
    }
  };

  // Fetch list of cases
  const fetchCases = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getCases({
        q: q.trim() || undefined,
        risk: risk !== 'ALL' ? risk : undefined,
        input_type: inputType !== 'ALL' ? inputType : undefined,
        category: category !== 'ALL' ? category : undefined,
        include_demo: includeDemo,
        page,
        page_size: pageSize
      });
      setCases(data.cases || []);
      setTotalCases(data.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to load cases');
    } finally {
      setLoading(false);
    }
  }, [q, risk, inputType, category, includeDemo, page, pageSize]);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  // Handle URL open param
  useEffect(() => {
    if (openCaseIdFromUrl && openCaseIdFromUrl !== selectedCaseId) {
      setSelectedCaseId(openCaseIdFromUrl);
    }
  }, [openCaseIdFromUrl]);

  // Fetch case detail when selected
  useEffect(() => {
    if (!selectedCaseId) {
      setCaseDetail(null);
      return;
    }

    let isMounted = true;
    const fetchDetail = async () => {
      setLoadingDetail(true);
      setDetailError(null);
      setNotesSavedSuccess(false);
      try {
        const detail = await api.getCaseDetail(selectedCaseId);
        if (isMounted) {
          setCaseDetail(detail);
          setNotes(detail.investigator_notes || '');
        }
      } catch (err) {
        if (isMounted) {
          setDetailError(err.message || `Failed to load details for case ${selectedCaseId}`);
        }
      } finally {
        if (isMounted) {
          setLoadingDetail(false);
        }
      }
    };

    fetchDetail();
    return () => {
      isMounted = false;
    };
  }, [selectedCaseId]);

  const handleOpenDrawer = (caseId) => {
    setSelectedCaseId(caseId);
    setPdfError(null);
    setSearchParams({ open: caseId });
  };

  const handleCloseDrawer = () => {
    setSelectedCaseId(null);
    setCaseDetail(null);
    setPdfError(null);
    setSearchParams({});
  };

  const handleSaveNotes = async () => {
    if (!selectedCaseId) return;
    setSavingNotes(true);
    setNotesSavedSuccess(false);
    try {
      await api.updateCaseNotes(selectedCaseId, notes);
      setNotesSavedSuccess(true);
      setTimeout(() => setNotesSavedSuccess(false), 3000);
      // Update local case state
      setCaseDetail((prev) => (prev ? { ...prev, investigator_notes: notes } : prev));
    } catch (err) {
      alert(`Error saving notes: ${err.message}`);
    } finally {
      setSavingNotes(false);
    }
  };

  const handleCopyHash = (hash) => {
    if (!hash) return;
    navigator.clipboard.writeText(hash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  const handleResetFilters = () => {
    setQ('');
    setRisk('ALL');
    setInputType('ALL');
    setCategory('ALL');
    setIncludeDemo(true);
    setPage(1);
  };

  const totalPages = Math.ceil(totalCases / pageSize) || 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <FolderKanban className="w-6 h-6 text-primary-600" />
            Case Management & Investigation Dossiers
          </h1>
          <p className="text-slate-600 text-sm mt-1">
            Search, triage, cross-reference, and annotate scam reports and analyzed incidents.
          </p>
        </div>

        <button
          onClick={fetchCases}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-medium shadow-sm transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
          {/* Search box */}
          <div className="md:col-span-5 relative">
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
              placeholder="Search by case ID, subject, or message excerpt..."
              className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {/* Risk Filter */}
          <div className="md:col-span-2">
            <select
              value={risk}
              onChange={(e) => {
                setRisk(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
            >
              <option value="ALL">All Risk Levels</option>
              <option value="HIGH">High Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="LOW">Low Risk</option>
            </select>
          </div>

          {/* Input Type Filter */}
          <div className="md:col-span-2">
            <select
              value={inputType}
              onChange={(e) => {
                setInputType(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
            >
              <option value="ALL">All Input Types</option>
              <option value="message">Messages</option>
              <option value="url">URLs</option>
              <option value="website">Websites</option>
            </select>
          </div>

          {/* Include Demo toggle & Reset */}
          <div className="md:col-span-3 flex items-center justify-between gap-2">
            <label className="flex items-center gap-1.5 text-xs font-medium text-slate-700 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={includeDemo}
                onChange={(e) => {
                  setIncludeDemo(e.target.checked);
                  setPage(1);
                }}
                className="rounded border-slate-300 text-primary-600 focus:ring-primary-500"
              />
              <span>Include Demo Cases</span>
            </label>

            {(q || risk !== 'ALL' || inputType !== 'ALL' || !includeDemo) && (
              <button
                onClick={handleResetFilters}
                className="text-xs text-primary-600 hover:text-primary-800 font-semibold"
              >
                Reset Filters
              </button>
            )}
          </div>
        </div>
      </div>

      {error && <ErrorBanner message={error} />}

      {/* Cases Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center">
            <LoadingSpinner size="md" message="Loading cases from database..." />
          </div>
        ) : cases.length === 0 ? (
          <div className="p-8">
            <EmptyState
              title="No cases found"
              description="No investigation cases match your current filters. Try resetting search parameters or load the synthetic demo dataset."
              actionText="Reset Filters"
              onAction={handleResetFilters}
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 border-b border-slate-200 text-xs font-bold uppercase tracking-wider text-slate-600">
                <tr>
                  <th className="py-3 px-4">Case ID</th>
                  <th className="py-3 px-4">Subject</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Risk Level</th>
                  <th className="py-3 px-4">Score</th>
                  <th className="py-3 px-4">Identifiers</th>
                  <th className="py-3 px-4">Logged Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {cases.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => handleOpenDrawer(c.id)}
                    className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 whitespace-nowrap">
                      <div className="flex items-center gap-1.5 font-mono text-xs font-bold text-primary-700">
                        {c.id}
                        {c.is_demo && <DemoBadge />}
                      </div>
                    </td>
                    <td className="py-3 px-4 max-w-xs md:max-w-md truncate font-medium text-slate-800">
                      {c.subject || '(No subject recorded)'}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span className="capitalize text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                        {c.input_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <RiskBadge level={c.risk_level} score={c.risk_score} showScore={false} />
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap font-bold text-slate-800 text-xs">
                      {c.risk_score}/100
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap text-xs text-slate-600">
                      <span className="font-semibold text-slate-800">{c.identifier_count}</span> extracted
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap text-xs text-slate-500">
                      {new Date(c.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap text-right">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenDrawer(c.id);
                        }}
                        className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium border border-slate-200 transition-colors"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-600">
          <div>
            Showing <span className="font-semibold text-slate-900">{totalCases === 0 ? 0 : (page - 1) * pageSize + 1}</span> to{' '}
            <span className="font-semibold text-slate-900">{Math.min(page * pageSize, totalCases)}</span> of{' '}
            <span className="font-semibold text-slate-900">{totalCases}</span> total cases
          </div>

          <div className="flex items-center gap-2">
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setPage(1);
              }}
              className="px-2 py-1 rounded border border-slate-300 text-xs bg-white text-slate-700"
            >
              <option value={10}>10 per page</option>
              <option value={15}>15 per page</option>
              <option value={25}>25 per page</option>
              <option value={50}>50 per page</option>
            </select>

            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-1 rounded border border-slate-300 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-2 py-1 font-semibold text-slate-800">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-1 rounded border border-slate-300 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* CASE DETAIL DRAWER / MODAL */}
      {selectedCaseId && (
        <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/60 backdrop-blur-sm flex justify-end">
          <div className="w-full max-w-2xl bg-white h-full shadow-2xl flex flex-col transform transition-transform duration-300 ease-in-out">
            {/* Drawer Header */}
            <div className="p-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className="font-mono text-base font-bold text-cyan-400">{selectedCaseId}</span>
                {caseDetail?.is_demo && <DemoBadge />}
                {caseDetail && <RiskBadge level={caseDetail.risk_level} score={caseDetail.risk_score} />}
              </div>
              <div className="flex items-center gap-3">
                {caseDetail && (
                  <button
                    type="button"
                    onClick={() => handleDownloadPdf(caseDetail.id)}
                    disabled={downloadingPdf}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition-colors disabled:opacity-50 cursor-pointer shadow-xs"
                    title={`Export Official PDF Dossier for ${caseDetail.id}`}
                  >
                    <Download className={`w-3.5 h-3.5 ${downloadingPdf ? 'animate-bounce' : ''}`} />
                    <span>{downloadingPdf ? 'Generating PDF...' : 'Download PDF Dossier'}</span>
                  </button>
                )}
                <button
                  onClick={handleCloseDrawer}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
                  title="Close Drawer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Drawer Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {pdfError && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800 flex items-start justify-between gap-2 shadow-xs">
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
              {loadingDetail ? (
                <div className="py-20 text-center">
                  <LoadingSpinner size="lg" message="Loading case dossier & relationship intelligence..." />
                </div>
              ) : detailError ? (
                <ErrorBanner message={detailError} />
              ) : caseDetail ? (
                <>
                  {/* Case Title & Metadata */}
                  <div>
                    <h2 className="text-xl font-bold text-slate-900 break-words">{caseDetail.subject}</h2>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 mt-2">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        {new Date(caseDetail.created_at).toLocaleString()}
                      </span>
                      <span>•</span>
                      <span className="capitalize font-medium text-slate-700">Type: {caseDetail.input_type}</span>
                      <span>•</span>
                      <span>Category: {caseDetail.category.replace(/_/g, ' ')}</span>
                      <span>•</span>
                      <span>Status: <strong className="text-slate-800">{caseDetail.status}</strong></span>
                    </div>
                  </div>

                  {/* HIGH RISK WARNING */}
                  {caseDetail.risk_level === 'HIGH' && (
                    <div className="p-3.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-900 flex items-start gap-2.5 text-xs">
                      <ShieldAlert className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <strong>Flagged as High Risk:</strong> This case exhibits strong indicators consistent with scam, phishing, or financial fraud infrastructure.
                      </div>
                    </div>
                  )}

                  {/* AI Second Opinion Card */}
                  {caseDetail.ai_second_opinion && (
                    <AISecondOpinionCard opinion={caseDetail.ai_second_opinion} />
                  )}

                  {/* Indicator Breakdown */}
                  <div>
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 mb-3">
                      Triggered Risk Indicators ({caseDetail.indicators?.length || 0})
                    </h3>
                    <IndicatorList indicators={caseDetail.indicators || []} />
                  </div>

                  {/* Extracted Identifiers */}
                  <div>
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 mb-3">
                      Extracted Network Identifiers ({caseDetail.identifiers?.length || 0})
                    </h3>
                    <IdentifierChips identifiers={caseDetail.identifiers || []} />
                  </div>

                  {/* Related Cases: Shared Identifiers & Near-duplicates */}
                  <div>
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 mb-3 flex items-center gap-1.5">
                      <LinkIcon className="w-4 h-4 text-primary-600" />
                      Cross-Case Linkages & Intelligence
                    </h3>

                    {(!caseDetail.related_cases || caseDetail.related_cases.length === 0) &&
                    (!caseDetail.similarity_links || caseDetail.similarity_links.length === 0) ? (
                      <p className="text-xs text-slate-500 italic bg-slate-50 p-3 rounded-lg border border-slate-200">
                        No shared identifiers or duplicate content links found with other logged cases.
                      </p>
                    ) : (
                      <div className="space-y-3">
                        {/* Shared Identifiers */}
                        {caseDetail.related_cases && caseDetail.related_cases.length > 0 && (
                          <div className="space-y-2">
                            <span className="text-xs font-semibold text-slate-700">Cases sharing identifiers:</span>
                            {caseDetail.related_cases.map((rel) => (
                              <div
                                key={rel.case_id}
                                onClick={() => handleOpenDrawer(rel.case_id)}
                                className="p-3 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 transition-colors cursor-pointer flex items-center justify-between"
                              >
                                <div>
                                  <div className="flex items-center gap-2">
                                    <span className="font-mono text-xs font-bold text-primary-700">{rel.case_id}</span>
                                    {rel.risk_level && <RiskBadge level={rel.risk_level} showScore={false} />}
                                  </div>
                                  <div className="text-xs text-slate-700 font-medium truncate max-w-sm mt-1">
                                    {rel.subject || '(No subject)'}
                                  </div>
                                  <div className="text-[11px] text-slate-500 mt-0.5">
                                    Shared: {rel.shared_identifiers.join(', ')}
                                  </div>
                                </div>
                                <span className="text-xs text-primary-600 font-semibold">Inspect →</span>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Near Duplicate Content */}
                        {caseDetail.similarity_links && caseDetail.similarity_links.length > 0 && (
                          <div className="space-y-2 pt-2">
                            <span className="text-xs font-semibold text-slate-700">Near-Duplicate Content:</span>
                            {caseDetail.similarity_links.map((sim, sidx) => (
                              <div
                                key={sidx}
                                onClick={() => handleOpenDrawer(sim.case_id)}
                                className="p-3 rounded-lg bg-blue-50/50 hover:bg-blue-100/50 border border-blue-200 transition-colors cursor-pointer flex items-center justify-between"
                              >
                                <div>
                                  <div className="flex items-center gap-2">
                                    <span className="font-mono text-xs font-bold text-blue-700">{sim.case_id}</span>
                                    <span className="text-[11px] px-1.5 py-0.5 rounded bg-blue-200/60 text-blue-800 font-semibold">
                                      {Math.round(sim.similarity * 100)}% Match
                                    </span>
                                  </div>
                                  <div className="text-xs text-slate-700 font-medium truncate max-w-sm mt-1">
                                    {sim.subject || '(No subject)'}
                                  </div>
                                </div>
                                <span className="text-xs text-blue-600 font-semibold">Inspect →</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Investigator Notes (Editable & Persisted) */}
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
                    <div className="flex items-center justify-between">
                      <label htmlFor="notes-textarea" className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                        <FileText className="w-4 h-4 text-primary-600" />
                        Investigator Notes & Chain of Custody Remarks
                      </label>
                      {notesSavedSuccess && (
                        <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                          <Check className="w-3.5 h-3.5" /> Notes saved!
                        </span>
                      )}
                    </div>
                    <textarea
                      id="notes-textarea"
                      rows={4}
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="Add investigation remarks, police FIR/complaint number, or field notes..."
                      className="w-full p-2.5 rounded-lg border border-slate-300 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                    />
                    <div className="flex justify-end">
                      <button
                        type="button"
                        onClick={handleSaveNotes}
                        disabled={savingNotes}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-xs font-medium shadow-sm transition-colors disabled:opacity-50"
                      >
                        <Save className="w-3.5 h-3.5" />
                        <span>{savingNotes ? 'Saving...' : 'Save Notes'}</span>
                      </button>
                    </div>
                  </div>

                  {/* Evidence & Hash Details */}
                  <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-xs text-slate-600 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-700">Evidence SHA-256 Hash:</span>
                      <button
                        onClick={() => handleCopyHash(caseDetail.content_sha256)}
                        className="inline-flex items-center gap-1 text-[11px] text-primary-600 hover:text-primary-800 font-medium"
                      >
                        {copiedHash ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-600" />
                            <span className="text-emerald-600">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>Copy Hash</span>
                          </>
                        )}
                      </button>
                    </div>
                    <div className="font-mono text-[11px] text-slate-800 break-all bg-white p-2 rounded border border-slate-200 select-all">
                      {caseDetail.content_sha256}
                    </div>

                    <div className="pt-2">
                      <span className="font-semibold text-slate-700 block mb-1">Raw Evidence Content:</span>
                      <pre className="font-mono text-[11px] bg-white p-2 rounded border border-slate-200 whitespace-pre-wrap max-h-36 overflow-y-auto text-slate-800">
                        {caseDetail.raw_content}
                      </pre>
                    </div>
                  </div>
                </>
              ) : null}
            </div>

            {/* Drawer Footer */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex justify-end">
              <button
                type="button"
                onClick={handleCloseDrawer}
                className="px-4 py-2 rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs font-medium transition-colors"
              >
                Close Dossier
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}