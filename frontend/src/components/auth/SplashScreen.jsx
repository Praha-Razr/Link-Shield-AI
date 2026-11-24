import React, { useState, useEffect } from 'react';
import { Shield } from 'lucide-react';
import { useI18n } from '../../i18n/I18nContext';
import LanguageToggle from '../LanguageToggle';

export default function SplashScreen({ onComplete }) {
  const { t, lang } = useI18n();
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const duration = 2000; // ~2 seconds
    const interval = 20;
    const step = 100 / (duration / interval);

    const timer = setInterval(() => {
      setProgress((prev) => {
        const next = prev + step;
        if (next >= 100) {
          clearInterval(timer);
          setTimeout(() => {
            onComplete();
          }, 150);
          return 100;
        }
        return next;
      });
    }, interval);

    return () => clearInterval(timer);
  }, [onComplete]);

  return (
    <div className="fixed inset-0 z-50 bg-[#070D1E] text-slate-100 flex flex-col items-center justify-center p-6 select-none overflow-hidden">
      {/* Language toggle at top right */}
      <div className="absolute top-6 right-6 z-20">
        <LanguageToggle variant="dark" />
      </div>

      {/* Background radial glow */}
      <div className="absolute w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute w-64 h-64 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none" />

      {/* Center Animated Shield & Branding */}
      <div className="relative z-10 flex flex-col items-center max-w-sm w-full text-center">
        {/* Animated Shield Logo */}
        <div className="relative mb-6">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-blue-700 via-indigo-600 to-cyan-500 p-0.5 shadow-2xl shadow-cyan-500/20 animate-pulse">
            <div className="w-full h-full bg-[#091124] rounded-[14px] flex items-center justify-center">
              <Shield className="w-10 h-10 text-cyan-400 drop-shadow-[0_0_12px_rgba(34,211,238,0.5)]" />
            </div>
          </div>
          {/* Subtle spinning accent ring */}
          <div className="absolute -inset-2 rounded-3xl border border-cyan-500/20 border-dashed animate-spin [animation-duration:15s] pointer-events-none" />
        </div>

        {/* Product Title */}
        <h1 className="text-3xl font-extrabold tracking-widest text-white mb-2 font-mono">
          LINKSHIELD <span className="text-cyan-400">AI</span>
        </h1>

        {/* Tagline */}
        <p className="text-xs font-semibold tracking-wider text-slate-400 uppercase mb-8">
          {lang === 'hi' ? 'जांचें • समझें • तफ्तीश करें • सुरक्षित रहें' : 'Detect • Explain • Investigate • Protect'}
        </p>

        {/* Progress Bar Container */}
        <div className="w-full bg-slate-900/90 rounded-full h-1.5 p-0.5 border border-slate-800 shadow-inner mb-3">
          <div
            className="bg-gradient-to-r from-blue-500 to-cyan-400 h-full rounded-full transition-all duration-75 ease-out shadow-sm shadow-cyan-400/50"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Status ticker */}
        <div className="flex items-center justify-between w-full text-[10px] text-slate-500 font-mono">
          <span>{lang === 'hi' ? 'सुरक्षा प्रणाली प्रारंभ हो रही है...' : 'INITIALIZING THREAT SUBSYSTEMS'}</span>
          <span>{Math.round(progress)}%</span>
        </div>

        {/* Skip button for rapid navigation */}
        <button
          onClick={onComplete}
          className="mt-8 text-[11px] text-slate-500 hover:text-cyan-400 transition-colors cursor-pointer underline decoration-dotted"
        >
          {lang === 'hi' ? 'सीधे पोर्टल पर जाएं →' : 'Skip to Portal →'}
        </button>
      </div>

      {/* Bottom Integrity Note */}
      <div className="absolute bottom-6 text-[10px] text-slate-600 font-mono text-center">
        LINKSHIELD AI &bull; {lang === 'hi' ? 'स्वायत्त साइबर खतरा जांच प्रणाली' : 'Autonomous Cyber Threat Detection Architecture'}
      </div>
    </div>
  );
}
