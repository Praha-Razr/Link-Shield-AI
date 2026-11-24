import React from 'react';

export default function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'default',
  className = '',
}) {
  const variantStyles = {
    default: 'border-slate-200 bg-white text-slate-900',
    high: 'border-rose-200 bg-gradient-to-br from-white to-rose-50/40 text-rose-950',
    medium: 'border-amber-200 bg-gradient-to-br from-white to-amber-50/40 text-amber-950',
    low: 'border-emerald-200 bg-gradient-to-br from-white to-emerald-50/40 text-emerald-950',
    blue: 'border-blue-200 bg-gradient-to-br from-white to-blue-50/40 text-blue-950',
    cyan: 'border-cyan-200 bg-gradient-to-br from-white to-cyan-50/40 text-cyan-950',
  };

  const iconColors = {
    default: 'text-slate-600 bg-slate-100',
    high: 'text-rose-600 bg-rose-100',
    medium: 'text-amber-600 bg-amber-100',
    low: 'text-emerald-600 bg-emerald-100',
    blue: 'text-blue-600 bg-blue-100',
    cyan: 'text-cyan-600 bg-cyan-100',
  };

  return (
    <div
      className={`p-4 md:p-5 rounded-xl border shadow-xs transition-all hover:shadow-md ${variantStyles[variant] || variantStyles.default} ${className}`}
    >
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            {title}
          </p>
          <p className="text-2xl md:text-3xl font-black mt-1 font-mono tracking-tight">
            {value}
          </p>
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl flex-shrink-0 ${iconColors[variant] || iconColors.default}`}>
            <Icon className="w-5 h-5 md:w-6 md:h-6" />
          </div>
        )}
      </div>
      {subtitle && (
        <p className="text-xs text-slate-500 mt-2 font-medium">
          {subtitle}
        </p>
      )}
    </div>
  );
}
