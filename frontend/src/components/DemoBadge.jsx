import React from 'react';
import { Database } from 'lucide-react';

export default function DemoBadge({ className = '' }) {
  return (
    <span
      title="Synthetic Demo Record"
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase bg-amber-100 text-amber-900 border border-amber-300 ${className}`}
    >
      <Database className="w-3 h-3 text-amber-600" />
      <span>DEMO DATA</span>
    </span>
  );
}
