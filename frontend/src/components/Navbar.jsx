import React, { useState, useEffect } from 'react';
import { Menu, ShieldAlert, Shield, ShieldCheck, Activity, PhoneCall, LogOut, User as UserIcon } from 'lucide-react';
import { useRole } from '../context/RoleContext';
import { useI18n } from '../i18n/I18nContext';
import LanguageToggle from './LanguageToggle';
import { api } from '../services/api';

export default function Navbar({ onToggleSidebar }) {
  const { user, isOfficer, isCitizen, logout } = useRole();
  const { t, lang } = useI18n();
  const [backendOk, setBackendOk] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const checkHealth = async () => {
      try {
        const res = await api.getHealth();
        if (isMounted) setBackendOk(res.status === 'ok');
      } catch {
        if (isMounted) setBackendOk(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 25000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/95 backdrop-blur-xs border-b border-slate-200 px-4 md:px-6 flex items-center justify-between">
      {/* Left: Mobile hamburger */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 -ml-2 rounded-lg text-slate-600 hover:bg-slate-100 lg:hidden focus:outline-hidden"
          title="Toggle Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
          <span className="text-xs font-semibold text-slate-700 tracking-wide">
            {isCitizen && lang === 'hi' ? t('nav.network') : 'Cyber Threat Intelligence Network'}
          </span>
        </div>
      </div>

      {/* Right: Actions, Language Toggle, Role & Status */}
      <div className="flex items-center gap-2 md:gap-3">
        {/* Language Toggle (English | हिंदी) */}
        <LanguageToggle variant="light" />

        {/* National Helpline Badge */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-50 border border-rose-200 text-rose-800 text-[11px] font-bold">
          <PhoneCall className="w-3.5 h-3.5 text-rose-600" />
          <span>{isCitizen && lang === 'hi' ? t('nav.helpline') : 'CYBER HELPLINE: 1930'}</span>
        </div>

        {/* Backend Connectivity Status Dot */}
        <div
          title={
            backendOk === null
              ? 'Checking backend status...'
              : backendOk
              ? 'Backend API Connected (FastAPI)'
              : 'Backend Disconnected (http://localhost:8000)'
          }
          className="flex items-center gap-1.5 text-xs text-slate-500 font-mono px-2 py-1 rounded bg-slate-100 border border-slate-200"
        >
          <span
            className={`w-2 h-2 rounded-full ${
              backendOk === null
                ? 'bg-amber-400'
                : backendOk
                ? 'bg-emerald-500'
                : 'bg-rose-500'
            }`}
          />
          <span className="hidden sm:inline text-[11px]">
            {backendOk
              ? (isCitizen && lang === 'hi' ? t('nav.online') : 'API ONLINE')
              : (isCitizen && lang === 'hi' ? t('nav.offline') : 'API OFFLINE')}
          </span>
        </div>

        {/* User Profile & Role Badge */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
          <div className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
              isOfficer ? 'bg-blue-100 text-blue-800' : 'bg-emerald-100 text-emerald-800'
            }`}>
              <UserIcon className="w-4 h-4" />
            </div>
            <div className="hidden sm:block text-left">
              <div className="text-xs font-bold text-slate-800 leading-tight">
                {user?.display_name || user?.username || (isCitizen && lang === 'hi' ? 'नागरिक उपयोगकर्ता' : 'Authenticated User')}
              </div>
              <div className="flex items-center gap-1 mt-0.5">
                <span className={`inline-block px-1.5 py-0.2 rounded text-[9px] font-mono font-bold uppercase tracking-wider ${
                  isOfficer
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                }`}>
                  {isOfficer ? 'OFFICER' : (isCitizen && lang === 'hi' ? t('role.citizen') : 'CITIZEN')}
                </span>
              </div>
            </div>
          </div>

          {/* Logout Button */}
          <button
            type="button"
            onClick={logout}
            title={isCitizen && lang === 'hi' ? t('nav.logout') : 'Logout / Switch Role'}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer border border-slate-200 hover:border-rose-200 ml-1"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span className="hidden md:inline text-[11px]">
              {isCitizen && lang === 'hi' ? t('nav.logout') : 'Logout'}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
}
