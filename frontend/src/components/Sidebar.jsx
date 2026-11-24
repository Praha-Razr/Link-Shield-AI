import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquareWarning,
  Globe2,
  FolderKanban,
  ShieldCheck,
  UserCheck,
  AppWindow,
  Network,
  Flame,
  FileText,
  Bot
} from 'lucide-react';
import Logo from './Logo';
import { useRole } from '../context/RoleContext';
import { useI18n } from '../i18n/I18nContext';

export default function Sidebar({ isOpen, onClose }) {
  const { isOfficer, isCitizen, user, role } = useRole();
  const { t, lang } = useI18n();
  const currentRole = role || user?.role || (isCitizen ? 'citizen' : 'officer');

  const officerNavItems = [
    {
      name: 'Dashboard',
      path: '/',
      icon: LayoutDashboard,
      desc: 'Metrics & threat summary',
    },
    {
      name: 'Message Analyser',
      path: '/analyze/message',
      icon: MessageSquareWarning,
      desc: 'SMS, WhatsApp & Telegram inspection',
    },
    {
      name: 'URL Scanner',
      path: '/analyze/url',
      icon: Globe2,
      desc: 'Static & structure link inspection',
    },
    {
      name: 'Website Analyser',
      path: '/analyze/website',
      icon: AppWindow,
      desc: 'DOM & source inspection for fake sites',
    },
    {
      name: 'Scam Graph',
      path: '/intelligence/graph',
      icon: Network,
      desc: 'Relationship & infrastructure network',
    },
    {
      name: 'Threat Heat-list',
      path: '/intelligence/heatlist',
      icon: Flame,
      desc: 'Frequently reported scam identifiers',
    },
    {
      name: 'Case Management',
      path: '/cases',
      icon: FolderKanban,
      desc: 'Investigative repository & notes',
    },
    {
      name: 'Cyber Cop Assistant',
      path: '/assistant',
      icon: Bot,
      desc: 'AI & rule-based case intelligence',
    },
    {
      name: 'Reports',
      path: '/reports',
      icon: FileText,
      desc: 'Export official PDF dossiers',
    },
  ];

  const citizenNavItems = [
    {
      name: lang === 'hi' ? t('sidebar.scam_awareness') : 'Scam Awareness',
      path: '/',
      icon: LayoutDashboard,
      desc: lang === 'hi' ? t('sidebar.scam_awareness_desc') : 'Aggregate statistics & citizen safety advisories',
    },
    {
      name: lang === 'hi' ? t('sidebar.message_analyser') : 'Message Analyser',
      path: '/analyze/message',
      icon: MessageSquareWarning,
      desc: lang === 'hi' ? t('sidebar.message_analyser_desc') : 'Check SMS or suspicious text',
    },
    {
      name: lang === 'hi' ? t('sidebar.url_scanner') : 'URL Scanner',
      path: '/analyze/url',
      icon: Globe2,
      desc: lang === 'hi' ? t('sidebar.url_scanner_desc') : 'Scan a suspicious link',
    },
    {
      name: lang === 'hi' ? t('sidebar.website_analyser') : 'Website Analyser',
      path: '/analyze/website',
      icon: AppWindow,
      desc: lang === 'hi' ? t('sidebar.website_analyser_desc') : 'Inspect suspicious portal or loan page',
    },
  ];

  const navItems = isCitizen ? citizenNavItems : officerNavItems;

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-navy-950/70 backdrop-blur-xs lg:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-72 bg-navy-900 border-r border-navy-800 flex flex-col transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-5 border-b border-navy-800/80 bg-navy-950/40">
          <Logo />
        </div>

        {/* Role Indicator Banner in Sidebar */}
        <div className="px-5 py-2.5 bg-navy-850/60 border-b border-navy-800/50 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs">
            {isOfficer ? (
              <>
                <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                <span className="font-semibold text-slate-200 uppercase tracking-wider text-[11px]">
                  Police Officer Mode
                </span>
              </>
            ) : (
              <>
                <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span className="font-semibold text-slate-200 uppercase tracking-wider text-[11px]">
                  {lang === 'hi' ? t('sidebar.citizen_mode') : 'Citizen Portal Mode'}
                </span>
              </>
            )}
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 p-3.5 space-y-1.5 overflow-y-auto">
          <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
            {isCitizen
              ? (lang === 'hi' ? t('sidebar.citizen_tools') : 'Citizen Safety Tools')
              : 'Investigation Workspaces'}
          </p>

          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={`${currentRole}-${item.path}`}
                to={item.path}
                target="_self"
                onClick={() => {
                  if (isOpen) onClose();
                }}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all group ${
                    isActive
                      ? 'bg-electric-500 text-white font-semibold shadow-xs shadow-electric-500/20'
                      : 'text-slate-300 hover:bg-navy-800 hover:text-white'
                  }`
                }
              >
                <Icon className="w-4 h-4 flex-shrink-0 opacity-80 group-hover:opacity-100" />
                <div className="flex-1 truncate">
                  <div className="leading-tight">{item.name}</div>
                  <div className="text-[10px] opacity-70 truncate font-normal">{item.desc}</div>
                </div>
              </NavLink>
            );
          })}
        </nav>

        {/* Footer info */}
        <div className="p-4 border-t border-navy-800/80 bg-navy-950/60 text-slate-400 text-[11px] leading-relaxed">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-slate-300">LINKSHIELD AI</span>
            <span className="font-mono text-cyan-400 font-bold">v1.0</span>
          </div>
          <p className="text-[10px] text-slate-400 mt-0.5">
            Enterprise Threat Defense Platform
          </p>
        </div>
      </aside>
    </>
  );
}
