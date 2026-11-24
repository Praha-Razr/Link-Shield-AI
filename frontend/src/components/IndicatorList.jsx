import React from 'react';
import { AlertTriangle, Info, CheckCircle2 } from 'lucide-react';
import { useI18n } from '../i18n/I18nContext';

export default function IndicatorList({ indicators = [], className = '' }) {
  const { t, translateIndicator } = useI18n();

  if (!indicators || indicators.length === 0) {
    return (
      <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-sm flex items-center gap-2">
        <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
        <span>{t('msg.no_adverse')}</span>
      </div>
    );
  }

  return (
    <div className={`space-y-2.5 ${className}`}>
      {indicators.map((rawInd, idx) => {
        const ind = translateIndicator(rawInd);
        const isNegative = ind.points < 0;
        const isInformational = ind.points === 0;
        
        let pillColor = 'bg-rose-100 text-rose-800 border-rose-200';
        let cardBg = 'bg-white border-slate-200 hover:border-slate-300';
        let Icon = AlertTriangle;
        let iconColor = 'text-rose-500';

        if (isNegative) {
          pillColor = 'bg-emerald-100 text-emerald-800 border-emerald-200';
          cardBg = 'bg-emerald-50/40 border-emerald-100';
          Icon = CheckCircle2;
          iconColor = 'text-emerald-500';
        } else if (isInformational) {
          pillColor = 'bg-blue-100 text-blue-800 border-blue-200';
          cardBg = 'bg-blue-50/30 border-blue-100';
          Icon = Info;
          iconColor = 'text-blue-500';
        } else if (ind.points <= 15) {
          pillColor = 'bg-amber-100 text-amber-800 border-amber-200';
          Icon = AlertTriangle;
          iconColor = 'text-amber-500';
        }

        return (
          <div
            key={idx}
            className={`p-3.5 rounded-lg border shadow-xs transition-all ${cardBg}`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-2.5">
                <Icon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${iconColor}`} />
                <div>
                  <h4 className="text-sm font-semibold text-slate-800 leading-tight">
                    {ind.name}
                  </h4>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                    {ind.explanation}
                  </p>
                </div>
              </div>
              <span
                className={`flex-shrink-0 px-2 py-0.5 rounded text-xs font-mono font-bold border ${pillColor}`}
              >
                {ind.points > 0 ? `+${ind.points}` : ind.points} pts
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
