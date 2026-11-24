import React from 'react';
import { Languages } from 'lucide-react';
import { useI18n } from '../i18n/I18nContext';

export default function LanguageToggle({ variant = 'light', className = '' }) {
  const { lang, setLang } = useI18n();

  const isDark = variant === 'dark';

  return (
    <div
      className={`inline-flex items-center gap-1 p-0.5 rounded-lg border text-xs font-semibold select-none transition-all ${
        isDark
          ? 'bg-slate-900/90 border-slate-700/80 text-slate-400'
          : 'bg-slate-100 border-slate-200 text-slate-600'
      } ${className}`}
      title="Switch Language / भाषा बदलें"
      role="group"
      aria-label="Language selection"
    >
      <div className="pl-1.5 pr-0.5 hidden sm:flex items-center text-slate-400">
        <Languages className="w-3.5 h-3.5" />
      </div>

      <button
        type="button"
        onClick={() => setLang('en')}
        className={`px-2 py-0.5 rounded-md transition-all cursor-pointer text-[11px] font-bold ${
          lang === 'en'
            ? isDark
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-xs'
              : 'bg-white text-slate-900 border border-slate-200/80 shadow-2xs font-extrabold'
            : isDark
            ? 'hover:text-slate-200 hover:bg-slate-800/60'
            : 'hover:text-slate-900 hover:bg-slate-200/60'
        }`}
        aria-pressed={lang === 'en'}
      >
        English
      </button>

      <button
        type="button"
        onClick={() => setLang('hi')}
        className={`px-2 py-0.5 rounded-md transition-all cursor-pointer text-[11px] font-bold font-sans ${
          lang === 'hi'
            ? isDark
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-xs'
              : 'bg-white text-slate-900 border border-slate-200/80 shadow-2xs font-extrabold'
            : isDark
            ? 'hover:text-slate-200 hover:bg-slate-800/60'
            : 'hover:text-slate-900 hover:bg-slate-200/60'
        }`}
        aria-pressed={lang === 'hi'}
      >
        हिंदी
      </button>
    </div>
  );
}
