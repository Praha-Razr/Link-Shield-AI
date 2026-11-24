import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bot,
  Send,
  Sparkles,
  ShieldAlert,
  Database,
  Trash2,
  Copy,
  Check,
  ExternalLink,
  Info,
  Layers,
  ArrowRight,
  HelpCircle,
  FileSearch,
  CheckCircle2,
  AlertTriangle,
  Flame,
  Radio
} from 'lucide-react';
import { api } from '../services/api';

const SUGGESTIONS = [
  {
    label: 'High Risk Case Reasoning',
    query: 'Why was case LS-0006 classified as high risk?',
    icon: ShieldAlert,
  },
  {
    label: 'Shared Scam Domains',
    query: 'Which domain appears in multiple cases?',
    icon: Layers,
  },
  {
    label: 'UPI Reports Ranking',
    query: 'Which UPI ID has the most reports?',
    icon: Flame,
  },
  {
    label: 'Campaign Linkage',
    query: 'Show all cases linked to demo-scam.test',
    icon: FileSearch,
  },
  {
    label: 'Investigation Summary',
    query: 'Summarise this investigation',
    icon: Bot,
  },
  {
    label: 'Website Case Indicators',
    query: 'What are the suspicious indicators in website case LS-0002?',
    icon: HelpCircle,
  },
  {
    label: 'Threat Statistics',
    query: 'How many high risk cases?',
    icon: Database,
  },
];

export default function Assistant() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        '**LINKSHIELD AI Investigation Assistant** ready.\n\nI provide **evidence-grounded analysis** directly backed by records in our investigative database. Every finding cites verified Case IDs and detected threat indicators.\n\nChoose an inquiry from the quick chips below or enter your investigative question.',
      case_ids: [],
      evidence_references: [],
      is_ai_assisted: false,
      mode: 'rule_based',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [useEnhanced, setUseEnhanced] = useState(true);
  const [assistantStatus, setAssistantStatus] = useState(null);
  const [statusLoading, setStatusLoading] = useState(true);
  const [copiedId, setCopiedId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    let mounted = true;
    api.getAssistantStatus()
      .then((data) => {
        if (mounted) {
          setAssistantStatus(data);
          setStatusLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setAssistantStatus({
            key_configured: false,
            model: 'offline',
            status: 'error',
            error: err.message || 'Unable to check status'
          });
          setStatusLoading(false);
        }
      });
    return () => { mounted = false; };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (queryText) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: textToSend.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Build last 6 turns for follow-up context
      const historyTurns = messages
        .filter((m) => m.id !== 'welcome' && m.id !== 'welcome-reset')
        .slice(-6)
        .map((m) => ({
          role: m.role === 'assistant' ? 'model' : 'user',
          content: m.content
        }));

      const res = await api.askAssistant(textToSend.trim(), useEnhanced, historyTurns);
      const assistantMsg = {
        id: `a-${Date.now()}`,
        role: 'assistant',
        content: res.answer,
        case_ids: res.case_ids || [],
        evidence_references: res.evidence_references || [],
        is_ai_assisted: res.is_ai_assisted || false,
        mode: res.mode || 'rule_based',
        fallback_reason: res.fallback_reason || null,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: `Error contacting intelligence engine: ${err.message || 'Unknown network error'}. Please verify backend service is active.`,
        case_ids: [],
        evidence_references: [],
        is_ai_assisted: false,
        mode: 'error',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: 'welcome-reset',
        role: 'assistant',
        content:
          'Investigation session reset. All questions are queried fresh against the real-time SQLite case repository.',
        case_ids: [],
        evidence_references: [],
        is_ai_assisted: false,
        mode: 'rule_based',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  const openCase = (caseId) => {
    navigate(`/cases?open=${encodeURIComponent(caseId)}`);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] max-w-6xl mx-auto">
      {/* Top Header & Engine Status */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-4 sm:p-5 mb-4 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-navy-900 to-blue-700 flex items-center justify-center text-white shadow-xs">
            <Bot className="w-6 h-6 text-cyan-300" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-slate-900">Cyber Cop Intelligence Assistant</h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase bg-blue-50 text-blue-700 border border-blue-200">
                Cybercrime Intelligence AI
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Deterministic offline database interrogation & optional Gemini synthesis
            </p>
          </div>
        </div>

        {/* Engine Controls: Live Status, Enhanced Toggle & Clear */}
        <div className="flex items-center flex-wrap gap-3">
          {/* Real Gemini Connection Status Pill */}
          {statusLoading ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
              <span className="w-2 h-2 rounded-full bg-slate-400 animate-pulse" />
              Checking Gemini status...
            </span>
          ) : assistantStatus?.status === 'ok' ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 shadow-2xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
              Gemini connected ({assistantStatus.model})
            </span>
          ) : (
            <span
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-900 border border-amber-200 shadow-2xs max-w-sm truncate"
              title={assistantStatus?.error || 'Offline rule engine'}
            >
              <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
              <span className="truncate">Basic mode: {assistantStatus?.error || 'Offline rule engine'}</span>
            </span>
          )}

          {/* Enhanced Mode Switch */}
          <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center gap-1.5">
              <Sparkles className={`w-3.5 h-3.5 ${useEnhanced ? 'text-cyan-600 animate-spin' : 'text-slate-400'}`} />
              <span className="text-xs font-semibold text-slate-700">Enhanced Mode</span>
            </div>
            <button
              type="button"
              onClick={() => setUseEnhanced((prev) => !prev)}
              className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-hidden ${
                useEnhanced ? 'bg-cyan-600' : 'bg-slate-300'
              }`}
              role="switch"
              aria-checked={useEnhanced}
              title={useEnhanced ? 'Enhanced Gemini reasoning active' : 'Rule-based deterministic offline mode active'}
            >
              <span
                aria-hidden="true"
                className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out ${
                  useEnhanced ? 'translate-x-4' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* Clear Session */}
          <button
            onClick={handleClearChat}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors"
            title="Reset conversation thread"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reset</span>
          </button>
        </div>
      </div>

      {/* Suggestion Chips Banner */}
      <div className="mb-3 overflow-x-auto pb-1 scrollbar-thin">
        <div className="flex items-center gap-2 min-w-max">
          <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider pl-1 pr-1 flex items-center gap-1">
            <Radio className="w-3 h-3 text-electric-500 animate-pulse" />
            Suggested:
          </span>
          {SUGGESTIONS.map((item, idx) => {
            const Icon = item.icon;
            return (
              <button
                key={idx}
                onClick={() => handleSend(item.query)}
                disabled={loading}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-white hover:bg-blue-50/70 border border-slate-200/90 hover:border-blue-300 text-slate-700 hover:text-blue-700 shadow-2xs transition-all cursor-pointer disabled:opacity-50"
              >
                <Icon className="w-3 h-3 text-blue-600 shrink-0" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Chat Thread Messages Box */}
      <div className="flex-1 bg-white rounded-2xl border border-slate-200/90 shadow-2xs overflow-y-auto p-4 sm:p-6 space-y-4">
        {messages.map((msg) => {
          const isUser = msg.role === 'user';
          return (
            <div
              key={msg.id}
              className={`flex gap-3 sm:gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              {!isUser && (
                <div className="w-9 h-9 rounded-xl bg-navy-900 text-white flex items-center justify-center shrink-0 shadow-2xs mt-1">
                  <Bot className="w-5 h-5 text-cyan-400" />
                </div>
              )}

              <div
                className={`max-w-3xl rounded-2xl p-4 sm:p-5 transition-all text-sm leading-relaxed ${
                  isUser
                    ? 'bg-blue-600 text-white shadow-xs rounded-tr-xs'
                    : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-tl-xs shadow-2xs'
                }`}
              >
                {/* Assistant Message Metadata Header */}
                {!isUser && (
                  <div className="flex items-center justify-between gap-3 mb-2.5 pb-2 border-b border-slate-200/80 text-xs">
                    <div className="flex items-center gap-2 flex-wrap">
                      {msg.is_ai_assisted ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-100 text-cyan-800 border border-cyan-200">
                          <Sparkles className="w-3 h-3 text-cyan-700" />
                          AI-assisted
                        </span>
                      ) : msg.mode === 'fallback' ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                          <AlertTriangle className="w-3 h-3 text-amber-600" />
                          Basic mode (fallback)
                        </span>
                      ) : msg.mode === 'error' ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
                          <AlertTriangle className="w-3 h-3 text-rose-600" />
                          Engine Notice
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3 text-emerald-700" />
                          Deterministic Database Verified
                        </span>
                      )}
                      <span className="text-[11px] text-slate-600">{msg.timestamp}</span>
                    </div>

                    <button
                      onClick={() => handleCopy(msg.content, msg.id)}
                      className="text-slate-600 hover:text-slate-700 p-1 rounded hover:bg-slate-200/60 transition-colors"
                      title="Copy response"
                    >
                      {copiedId === msg.id ? (
                        <Check className="w-3.5 h-3.5 text-emerald-600" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                )}

                {/* Fallback Warning Notice Banner */}
                {msg.fallback_reason && (
                  <div className="mb-3 px-3 py-2 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-xs flex items-center gap-2">
                    <Info className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                    <span>Basic mode reason: {msg.fallback_reason}</span>
                  </div>
                )}

                {/* Message Content Render */}
                <div className="whitespace-pre-line space-y-2">
                  {msg.content.split('\n\n').map((paragraph, pIdx) => {
                    // Quick markdown formatting for bold and lists
                    return (
                      <div key={pIdx} className="space-y-1">
                        {paragraph.split('\n').map((line, lIdx) => {
                          const isBullet = line.trim().startsWith('•') || line.trim().startsWith('-');
                          const isNumbered = /^\d+\.\s/.test(line.trim());
                          const cleanText = line.replace(/^[•\-]\s*/, '').replace(/^\d+\.\s*/, '');

                          return (
                            <p
                              key={lIdx}
                              className={`${
                                isBullet || isNumbered ? 'pl-4 relative flex items-start gap-1.5' : ''
                              }`}
                            >
                              {isBullet && (
                                <span className="text-blue-500 font-bold select-none">•</span>
                              )}
                              {isNumbered && (
                                <span className="text-blue-600 font-bold text-xs select-none">
                                  {line.match(/^\d+\./)[0]}
                                </span>
                              )}
                              <span>
                                {cleanText.split(/(\*\*.*?\*\*)/).map((seg, sIdx) => {
                                  if (seg.startsWith('**') && seg.endsWith('**')) {
                                    return (
                                      <strong
                                        key={sIdx}
                                        className={isUser ? 'font-bold' : 'font-semibold text-slate-900'}
                                      >
                                        {seg.slice(2, -2)}
                                      </strong>
                                    );
                                  }
                                  return seg;
                                })}
                              </span>
                            </p>
                          );
                        })}
                      </div>
                    );
                  })}
                </div>

                {/* Grounded Citation: Linked Case IDs */}
                {msg.case_ids && msg.case_ids.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-200/80">
                    <div className="text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <FileSearch className="w-3 h-3 text-blue-600" />
                      <span>Referenced Case Dossiers ({msg.case_ids.length})</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.case_ids.map((cid) => (
                        <button
                          key={cid}
                          onClick={() => openCase(cid)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-mono font-bold bg-white hover:bg-blue-600 hover:text-white border border-blue-200 text-blue-700 shadow-2xs transition-all cursor-pointer group"
                          title={`Open dossier ${cid} in Case Management`}
                        >
                          <span>{cid}</span>
                          <ExternalLink className="w-3 h-3 opacity-60 group-hover:opacity-100" />
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Evidence References Chips */}
                {msg.evidence_references && msg.evidence_references.length > 0 && (
                  <div className="mt-3">
                    <div className="text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                      <Database className="w-3 h-3 text-slate-500" />
                      <span>Extracted Evidence Artifacts</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {msg.evidence_references.map((ev, eIdx) => (
                        <span
                          key={eIdx}
                          className="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-200/70 text-slate-700 border border-slate-300"
                        >
                          {ev}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* User Message Timestamp */}
                {isUser && (
                  <div className="text-[10px] text-blue-100/80 text-right mt-1.5">
                    {msg.timestamp}
                  </div>
                )}
              </div>

              {isUser && (
                <div className="w-9 h-9 rounded-xl bg-blue-700 text-white flex items-center justify-center shrink-0 shadow-2xs mt-1">
                  <span className="font-bold text-xs">COP</span>
                </div>
              )}
            </div>
          );
        })}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex gap-3 items-center text-slate-500 text-xs py-2 pl-2">
            <div className="w-8 h-8 rounded-lg bg-navy-900 text-white flex items-center justify-center animate-pulse">
              <Bot className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-100 border border-slate-200">
              <span className="w-2 h-2 rounded-full bg-blue-600 animate-ping" />
              <span className="font-medium text-slate-700">
                {useEnhanced ? 'Synthesizing verified case evidence via Gemini...' : 'Querying SQLite threat intelligence engine...'}
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form Bar */}
      <div className="mt-3">
        <div className="relative bg-white rounded-2xl border border-slate-300 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 shadow-2xs transition-all flex items-center p-1.5">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            placeholder="Ask about cases, scam syndicates, UPI IDs, domains, or risk explanations..."
            className="flex-1 px-4 py-2.5 text-sm bg-transparent border-0 focus:outline-hidden text-slate-800 placeholder-slate-400"
          />

          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-slate-200 text-white disabled:text-slate-400 font-semibold text-xs flex items-center gap-1.5 shadow-xs transition-colors cursor-pointer disabled:cursor-not-allowed"
          >
            <span>Query</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
        <div className="flex items-center justify-between text-[11px] text-slate-600 px-3 pt-1.5">
          <span>Press Enter to query • All answers backed by verified SQLite case records</span>
          <span className="hidden sm:inline">Enterprise Intelligence Ready</span>
        </div>
      </div>
    </div>
  );
}
