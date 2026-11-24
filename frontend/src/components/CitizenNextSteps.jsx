import React from 'react';
import { AlertTriangle, ShieldAlert, ShieldCheck, PhoneCall, Info, CheckCircle2 } from 'lucide-react';
import { useI18n } from '../i18n/I18nContext';

export default function CitizenNextSteps({ riskLevel = 'HIGH' }) {
  const { t } = useI18n();
  const isHigh = riskLevel === 'HIGH';
  const isMedium = riskLevel === 'MEDIUM';

  if (isHigh) {
    return (
      <div className="bg-gradient-to-br from-rose-50/90 to-red-50/60 rounded-xl border border-rose-200 p-4 sm:p-5 shadow-xs space-y-3">
        <div className="flex items-center gap-2 text-rose-900">
          <ShieldAlert className="w-5 h-5 text-rose-600 shrink-0" />
          <h3 className="text-sm font-bold tracking-tight">{t('nextsteps.high_title')}</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div className="p-3 bg-white rounded-lg border border-rose-100 shadow-2xs flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-bold text-slate-800 block">{t('nextsteps.high_precautions_title')}</span>
              <p className="text-slate-600 leading-relaxed">
                {t('nextsteps.high_precautions_body')}
              </p>
            </div>
          </div>

          <div className="p-3 bg-white rounded-lg border border-rose-100 shadow-2xs flex items-start gap-2.5">
            <PhoneCall className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-bold text-slate-800 block">{t('nextsteps.high_report_title')}</span>
              <p className="text-slate-600 leading-relaxed">
                {t('nextsteps.high_report_body_prefix')}{' '}
                <a
                  href="https://cybercrime.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 underline font-semibold hover:text-blue-800"
                >
                  cybercrime.gov.in
                </a>{' '}
                {t('nextsteps.high_report_body_suffix')} <strong className="text-rose-700 font-bold">1930</strong>.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-start gap-2 text-[11px] text-slate-500 bg-white/80 rounded-lg p-2.5 border border-slate-200">
          <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
          <span className="leading-relaxed">
            <strong>Advisory:</strong> {t('nextsteps.high_advisory')}
          </span>
        </div>
      </div>
    );
  }

  if (isMedium) {
    return (
      <div className="bg-gradient-to-br from-amber-50/90 to-yellow-50/60 rounded-xl border border-amber-200 p-4 sm:p-5 shadow-xs space-y-3">
        <div className="flex items-center gap-2 text-amber-900">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
          <h3 className="text-sm font-bold tracking-tight">{t('nextsteps.med_title')}</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div className="p-3 bg-white rounded-lg border border-amber-100 shadow-2xs flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-bold text-slate-800 block">{t('nextsteps.med_precautions_title')}</span>
              <p className="text-slate-600 leading-relaxed">
                {t('nextsteps.med_precautions_body')}
              </p>
            </div>
          </div>

          <div className="p-3 bg-white rounded-lg border border-amber-100 shadow-2xs flex items-start gap-2.5">
            <PhoneCall className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-bold text-slate-800 block">{t('nextsteps.med_report_title')}</span>
              <p className="text-slate-600 leading-relaxed">
                {t('nextsteps.med_report_body_prefix')}{' '}
                <a
                  href="https://cybercrime.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 underline font-semibold hover:text-blue-800"
                >
                  cybercrime.gov.in
                </a>{' '}
                {t('nextsteps.med_report_body_suffix')} <strong className="text-amber-800 font-bold">1930</strong>.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-start gap-2 text-[11px] text-slate-500 bg-white/80 rounded-lg p-2.5 border border-slate-200">
          <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
          <span className="leading-relaxed">
            <strong>Advisory:</strong> {t('nextsteps.med_advisory')}
          </span>
        </div>
      </div>
    );
  }

  // LOW Risk
  return (
    <div className="bg-gradient-to-br from-emerald-50/80 to-slate-50/80 rounded-xl border border-emerald-200/80 p-4 sm:p-5 shadow-xs space-y-3">
      <div className="flex items-center gap-2 text-emerald-900">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
        <h3 className="text-sm font-bold tracking-tight">{t('nextsteps.low_title')}</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        <div className="p-3 bg-white rounded-lg border border-emerald-100 shadow-2xs flex items-start gap-2.5">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="font-bold text-slate-800 block">{t('nextsteps.low_precautions_title')}</span>
            <p className="text-slate-600 leading-relaxed">
              {t('nextsteps.low_precautions_body')}
            </p>
          </div>
        </div>

        <div className="p-3 bg-white rounded-lg border border-emerald-100 shadow-2xs flex items-start gap-2.5">
          <Info className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="font-bold text-slate-800 block">{t('nextsteps.low_confirm_title')}</span>
            <p className="text-slate-600 leading-relaxed">
              {t('nextsteps.low_confirm_body')}
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-start gap-2 text-[11px] text-slate-500 bg-white/80 rounded-lg p-2.5 border border-slate-200">
        <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
        <span className="leading-relaxed">
          <strong>Advisory:</strong> {t('nextsteps.low_advisory')}
        </span>
      </div>
    </div>
  );
}
