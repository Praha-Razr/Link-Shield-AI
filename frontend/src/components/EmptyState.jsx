import React from 'react';
import { Inbox } from 'lucide-react';

export default function EmptyState({
  title = 'No Records Found',
  description = 'No matching intelligence or case data found for this selection.',
  icon: Icon = Inbox,
  actionText,
  onAction,
  className = '',
}) {
  return (
    <div
      className={`p-8 md:p-12 text-center rounded-xl border border-dashed border-slate-300 bg-slate-50/60 flex flex-col items-center justify-center ${className}`}
    >
      <div className="p-4 rounded-full bg-slate-100 text-slate-400 mb-3">
        <Icon className="w-8 h-8" />
      </div>
      <h3 className="text-base font-bold text-slate-800">{title}</h3>
      <p className="text-xs text-slate-500 max-w-sm mt-1 mb-4 leading-relaxed">
        {description}
      </p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="px-4 py-2 text-xs font-semibold rounded-lg bg-electric-500 hover:bg-electric-600 text-white shadow-xs transition-all"
        >
          {actionText}
        </button>
      )}
    </div>
  );
}
