import React from 'react';
import { Sparkles, AlertTriangle, ShieldCheck, Info, CheckCircle2 } from 'lucide-react';

export default function AISecondOpinionCard({ opinion }) {
  if (!opinion) return null;

  const {
    scam_likelihood,
    category,
    impersonated_brand,
    reasons = [],
    confidence,
    status = 'ok',
    disclaimer = 'AI opinion, verify manually',
    error
  } = opinion;

  return (
    <div className="bg-gradient-to-br from-slate-900 to-navy-950 text-white rounded-xl border border-cyan-500/30 p-5 shadow-sm space-y-3.5">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2.5 pb-2.5 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-300">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide">
              AI Second Opinion
            </h3>
            <span className="text-[10px] text-cyan-300/80 font-mono">
              Secondary Advisory Evaluation
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-cyan-950 text-cyan-300 border border-cyan-500/40">
            <Sparkles className="w-3 h-3 text-cyan-400" />
            AI-assisted
          </span>
          <span className="text-[10px] text-slate-400 italic hidden sm:inline">
            ({disclaimer})
          </span>
        </div>
      </div>

      {/* Body based on status */}
      {status === 'ok' ? (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            {/* Likelihood Badge */}
            <span
              className={`px-2.5 py-1 rounded-md font-bold uppercase tracking-wider text-[11px] border ${
                scam_likelihood === 'high'
                  ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                  : scam_likelihood === 'medium'
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
              }`}
            >
              Likelihood: {scam_likelihood}
            </span>

            {/* Confidence */}
            <span className="px-2.5 py-1 rounded-md font-mono bg-slate-800/80 text-slate-300 border border-slate-700">
              Confidence: {Math.round((confidence || 0) * 100)}%
            </span>

            {/* Category */}
            {category && (
              <span className="px-2.5 py-1 rounded-md font-semibold bg-slate-800/80 text-slate-200 border border-slate-700">
                Vector: {category.replace(/_/g, ' ')}
              </span>
            )}

            {/* Impersonated Brand */}
            {impersonated_brand && (
              <span className="px-2.5 py-1 rounded-md font-semibold bg-rose-950/60 text-rose-300 border border-rose-700/50">
                Target: {impersonated_brand}
              </span>
            )}
          </div>

          {/* Reasons List */}
          {reasons && reasons.length > 0 && (
            <div className="space-y-1.5 pt-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                Key Reasoning Signals:
              </span>
              <ul className="space-y-1">
                {reasons.map((r, i) => (
                  <li key={i} className="text-xs text-slate-200 flex items-start gap-2">
                    <span className="text-cyan-400 font-bold select-none">•</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : status === 'skipped' ? (
        <div className="flex items-center gap-2 p-2.5 rounded-lg bg-emerald-950/40 border border-emerald-800/40 text-emerald-300 text-xs">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
          <span>
            {reasons[0] || 'Verified genuine official domain: AI escalation bypassed.'}
          </span>
        </div>
      ) : (
        <div className="flex items-center gap-2 p-2.5 rounded-lg bg-amber-950/40 border border-amber-800/40 text-amber-300 text-xs">
          <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
          <span>{error || 'AI second opinion unavailable: engine offline or not configured'}</span>
        </div>
      )}

      {/* Mobile disclaimer footer */}
      <div className="text-[10px] text-slate-400 italic sm:hidden pt-1 border-t border-slate-800/60">
        Disclaimer: {disclaimer}
      </div>
    </div>
  );
}
