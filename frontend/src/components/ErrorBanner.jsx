import React from 'react';
import { AlertCircle, X } from 'lucide-react';

export default function ErrorBanner({ message, onDismiss, className = '' }) {
  if (!message) return null;

  return (
    <div
      className={`p-3.5 rounded-lg border border-rose-200 bg-rose-50 text-rose-800 text-xs flex items-start justify-between gap-2 shadow-xs ${className}`}
    >
      <div className="flex items-start gap-2">
        <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5 flex-shrink-0" />
        <span className="font-medium leading-relaxed">{message}</span>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-rose-500 hover:text-rose-800 p-0.5 rounded transition-colors"
          title="Dismiss"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}
