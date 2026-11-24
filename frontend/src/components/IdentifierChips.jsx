import React from 'react';
import { Phone, Mail, Link, Globe, Landmark, Coins, Hash } from 'lucide-react';

const TYPE_CONFIG = {
  phone: {
    bg: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    icon: Phone,
    label: 'Phone',
  },
  upi: {
    bg: 'bg-purple-50 border-purple-200 text-purple-800',
    icon: Hash,
    label: 'UPI ID',
  },
  domain: {
    bg: 'bg-sky-50 border-sky-200 text-sky-800',
    icon: Globe,
    label: 'Domain',
  },
  url: {
    bg: 'bg-blue-50 border-blue-200 text-blue-800',
    icon: Link,
    label: 'URL',
  },
  email: {
    bg: 'bg-amber-50 border-amber-200 text-amber-800',
    icon: Mail,
    label: 'Email',
  },
  bank_account: {
    bg: 'bg-rose-50 border-rose-200 text-rose-800',
    icon: Landmark,
    label: 'Bank A/C',
  },
  crypto_wallet: {
    bg: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    icon: Coins,
    label: 'Crypto',
  },
};

export function IdentifierChip({ type, value, is_legitimate = false, onCopy, className = '' }) {
  const normType = (type || 'other').toLowerCase();
  const config = TYPE_CONFIG[normType] || {
    bg: 'bg-slate-100 border-slate-300 text-slate-800',
    icon: Hash,
    label: normType,
  };
  const Icon = config.icon;

  const handleCopy = (e) => {
    e.stopPropagation();
    navigator.clipboard?.writeText(value);
    if (onCopy) onCopy(value);
  };

  return (
    <div
      title={is_legitimate ? `Known legitimate service identifier: ${value}` : `Click to copy: ${value}`}
      onClick={handleCopy}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono font-medium border shadow-2xs transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer ${
        is_legitimate ? 'bg-emerald-50/70 border-emerald-300 text-emerald-900' : config.bg
      } ${className}`}
    >
      <Icon className="w-3.5 h-3.5 opacity-75 flex-shrink-0" />
      <span className="opacity-75 uppercase font-sans text-[10px] tracking-wider">{config.label}:</span>
      <span className="truncate max-w-[240px] font-semibold">{value}</span>
      {is_legitimate && (
        <span className="ml-1 px-1.5 py-0.5 rounded text-[9px] font-sans font-semibold uppercase bg-emerald-100 text-emerald-800 border border-emerald-200">
          Known Legitimate
        </span>
      )}
    </div>
  );
}

export default function IdentifierChips({ identifiers = [], limit = null, className = '' }) {
  if (!identifiers || identifiers.length === 0) {
    return <span className="text-xs text-slate-400 italic">No identifiers extracted</span>;
  }

  const items = limit ? identifiers.slice(0, limit) : identifiers;
  const remaining = limit && identifiers.length > limit ? identifiers.length - limit : 0;

  return (
    <div className={`flex flex-wrap items-center gap-1.5 ${className}`}>
      {items.map((item, idx) => (
        <IdentifierChip
          key={`${item.type}-${item.value}-${idx}`}
          type={item.type}
          value={item.value}
          is_legitimate={item.is_legitimate}
        />
      ))}
      {remaining > 0 && (
        <span className="text-[11px] px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-medium">
          +{remaining} more
        </span>
      )}
    </div>
  );
}
