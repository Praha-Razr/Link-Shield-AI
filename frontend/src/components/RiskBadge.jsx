import React from 'react';
import { ShieldAlert, ShieldCheck, Shield } from 'lucide-react';
import { useI18n } from '../i18n/I18nContext';

export default function RiskBadge({ level = 'LOW', score = null, size = 'md', className = '' }) {
  const { lang, t } = useI18n();
  const normLevel = (level || 'LOW').toUpperCase();

  let styles = 'bg-emerald-50 text-emerald-700 border-emerald-300';
  let Icon = ShieldCheck;
  let dotColor = 'bg-emerald-500';

  if (normLevel === 'MEDIUM') {
    styles = 'bg-amber-50 text-amber-800 border-amber-300';
    Icon = Shield;
    dotColor = 'bg-amber-500';
  } else if (normLevel === 'HIGH') {
    styles = 'bg-rose-50 text-rose-800 border-rose-300 font-bold';
    Icon = ShieldAlert;
    dotColor = 'bg-rose-500 animate-pulse';
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3.5 py-1.5 gap-2 font-semibold',
  };

  const labelText = lang === 'hi'
    ? (normLevel === 'HIGH' ? t('risk.high') : normLevel === 'MEDIUM' ? t('risk.medium') : t('risk.low'))
    : `${normLevel} RISK`;

  return (
    <span
      className={`inline-flex items-center rounded-full border shadow-sm font-medium tracking-wide uppercase transition-all ${styles} ${sizeClasses[size] || sizeClasses.md} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
      <Icon className={size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5'} />
      <span>{labelText}</span>
      {score !== null && score !== undefined && (
        <span className="opacity-80 font-mono text-[11px] normal-case ml-0.5">
          ({score}/100)
        </span>
      )}
    </span>
  );
}
