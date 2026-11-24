import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { RoleProvider, useRole } from './context/RoleContext';
import { I18nProvider, useI18n } from './i18n/I18nContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import MessageAnalyzer from './pages/MessageAnalyzer';
import UrlScanner from './pages/UrlScanner';
import WebsiteAnalyzer from './pages/WebsiteAnalyzer';
import ScamGraph from './pages/ScamGraph';
import ThreatHeatlist from './pages/ThreatHeatlist';
import CaseManagement from './pages/CaseManagement';
import Reports from './pages/Reports';
import Assistant from './pages/Assistant';
import SplashScreen from './components/auth/SplashScreen';
import AuthPortal from './components/auth/AuthPortal';

class GlobalErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error('LinkShield GlobalErrorBoundary caught error:', error, errorInfo);
  }
  handleBackToLogin = () => {
    try {
      sessionStorage.removeItem('linkshield_token');
      sessionStorage.removeItem('linkshield_user');
    } catch {}
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };
  handleReload = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };
  render() {
    if (this.state.hasError) {
      const isHi = typeof window !== 'undefined' && localStorage.getItem('linkshield_lang') === 'hi';
      return (
        <div className="min-h-screen bg-[#070D1E] text-slate-100 flex flex-col items-center justify-center p-6 select-none font-sans">
          <div className="p-8 bg-[#0C152B] border border-slate-800 rounded-2xl shadow-2xl max-w-lg w-full text-center">
            <div className="w-14 h-14 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center mx-auto mb-4 font-bold text-2xl">
              !
            </div>
            <h2 className="text-xl font-bold text-white mb-2">
              {isHi ? 'कुछ गलत हो गया' : 'Something went wrong'}
            </h2>
            <p className="text-xs text-slate-400 mb-6 leading-relaxed">
              {isHi
                ? 'एक अनपेक्षित त्रुटि हुई है। आप लॉगिन स्क्रीन पर वापस जा सकते हैं या पेज पुनः लोड कर सकते हैं।'
                : 'An unexpected application error occurred. You can return to login or reload the page.'}
            </p>
            {this.state.error?.message && (
              <div className="p-3 mb-6 rounded-lg bg-slate-900 border border-slate-800 text-[11px] font-mono text-rose-300 text-left overflow-x-auto">
                {this.state.error.message}
              </div>
            )}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                type="button"
                onClick={this.handleBackToLogin}
                className="px-5 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold transition-all cursor-pointer shadow-lg shadow-cyan-600/20"
              >
                {isHi ? 'लॉगिन पर वापस जाएं' : 'Back to Login'}
              </button>
              <button
                type="button"
                onClick={this.handleReload}
                className="px-5 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-all cursor-pointer border border-slate-700"
              >
                {isHi ? 'पेज पुनः लोड करें' : 'Reload Application'}
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { isCitizen } = useRole();
  const { t, lang } = useI18n();
  const location = useLocation();
  const navigate = useNavigate();

  // Dynamic Browser Tab Titles
  useEffect(() => {
    let title = 'LinkShield AI - Cyber Crime Intelligence';
    if (isCitizen && lang === 'hi') {
      const hiTitleMap = {
        '/': 'LINKSHIELD AI - ठगी से बचाव',
        '/analyze/message': 'LINKSHIELD AI - संदेश जांच',
        '/analyze/url': 'LINKSHIELD AI - वेबसाइट लिंक जांच',
        '/analyze/website': 'LINKSHIELD AI - वेबसाइट और ऐप जांच',
      };
      title = hiTitleMap[location.pathname] || 'LINKSHIELD AI - नागरिक सुरक्षा';
    } else {
      const titleMap = {
        '/': isCitizen ? 'LinkShield AI - Scam Awareness' : 'LinkShield AI - Threat Intelligence Dashboard',
        '/analyze/message': 'LinkShield AI - Message Analyser',
        '/analyze/url': 'LinkShield AI - URL Scanner',
        '/analyze/website': 'LinkShield AI - Website Analyser',
        '/intelligence/graph': 'LinkShield AI - Scam Campaign Intelligence Graph',
        '/intelligence/heatlist': 'LinkShield AI - Threat Surveillance Heat-list',
        '/cases': 'LinkShield AI - Case Management Dossiers',
        '/reports': 'LinkShield AI - Official Investigation Reports',
        '/assistant': 'LinkShield AI - Cyber Cop Intelligence Assistant',
      };
      title = titleMap[location.pathname] || 'LinkShield AI - Cyber Crime Intelligence';
    }
    document.title = title;
  }, [location.pathname, isCitizen, lang]);

  // Global Keyboard Shortcuts: '/' focuses primary search, 'Esc' closes open drawers/modals
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Don't hijack if user is inside an input/textarea
      const targetTag = e.target.tagName.toLowerCase();
      const isInput = targetTag === 'input' || targetTag === 'textarea' || e.target.isContentEditable;

      if (e.key === '/' && !isInput) {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="text"], input[type="search"]');
        if (searchInput) {
          searchInput.focus();
          searchInput.select?.();
        }
      } else if (e.key === 'Escape') {
        // If drawer is open on /cases, close it by navigating back or clearing query params
        if (location.pathname === '/cases' && location.search.includes('open=')) {
          navigate('/cases', { replace: true });
        }
        if (document.activeElement) {
          document.activeElement.blur();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [location.pathname, location.search, navigate]);

  // If switched to Citizen while on an Officer-only page,
  // smoothly redirect to the home page in the same tab
  useEffect(() => {
    const officerOnlyPaths = [
      '/cases',
      '/reports',
      '/intelligence/graph',
      '/intelligence/heatlist',
      '/assistant',
    ];
    if (isCitizen && officerOnlyPaths.some((p) => location.pathname.startsWith(p))) {
      navigate('/', { replace: true });
    }
  }, [isCitizen, location.pathname, navigate]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
      {/* Sidebar for Desktop & Mobile Drawer */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Area */}
      <div className="lg:pl-72 flex flex-col flex-1 min-w-0">
        <Navbar onToggleSidebar={() => setSidebarOpen((prev) => !prev)} />

        <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <GlobalErrorBoundary key={location.pathname}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/analyze/message" element={<MessageAnalyzer />} />
              <Route path="/analyze/url" element={<UrlScanner />} />
              <Route path="/analyze/website" element={<WebsiteAnalyzer />} />
              <Route
                path="/intelligence/graph"
                element={isCitizen ? <Navigate to="/" replace /> : <ScamGraph />}
              />
              <Route
                path="/intelligence/heatlist"
                element={isCitizen ? <Navigate to="/" replace /> : <ThreatHeatlist />}
              />
              <Route
                path="/cases"
                element={isCitizen ? <Navigate to="/" replace /> : <CaseManagement />}
              />
              <Route
                path="/reports"
                element={isCitizen ? <Navigate to="/" replace /> : <Reports />}
              />
              <Route
                path="/assistant"
                element={isCitizen ? <Navigate to="/" replace /> : <Assistant />}
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </GlobalErrorBoundary>
        </main>

        {/* Global Footer Disclaimer */}
        <footer className="mt-auto py-3 px-4 md:px-6 border-t border-slate-200/80 bg-white/80 backdrop-blur-xs text-[11px] text-slate-500">
          <div className="flex flex-col sm:flex-row items-center justify-between max-w-7xl w-full mx-auto gap-2">
            <div>
              <span className="font-semibold text-slate-700">LINKSHIELD AI</span> &bull; {isCitizen && lang === 'hi' ? t('footer.disclaimer').replace('LINKSHIELD AI • ', '') : 'Demo data is synthetic. Findings require human verification before action.'}
            </div>
            <div className="hidden lg:flex items-center gap-2 text-slate-500 font-mono text-[10px]">
              <span className="px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200">{t('footer.focus')}</span>
              <span className="px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200">{t('footer.close')}</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

function RootApp() {
  const { isAuthenticated, loading } = useRole();
  const [splashDone, setSplashDone] = useState(() => {
    return typeof window !== 'undefined' && sessionStorage.getItem('linkshield_splash_shown') === 'true';
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-[#070D1E] flex flex-col items-center justify-center text-slate-400 gap-3">
        <div className="w-8 h-8 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
        <span className="text-xs font-mono tracking-wider">CHECKING CREDENTIALS...</span>
      </div>
    );
  }

  if (!isAuthenticated) {
    if (!splashDone) {
      return (
        <SplashScreen
          onComplete={() => {
            sessionStorage.setItem('linkshield_splash_shown', 'true');
            setSplashDone(true);
          }}
        />
      );
    }
    return <AuthPortal />;
  }

  return <AppLayout />;
}

export default function App() {
  return (
    <GlobalErrorBoundary>
      <BrowserRouter>
        <I18nProvider>
          <RoleProvider>
            <RootApp />
          </RoleProvider>
        </I18nProvider>
      </BrowserRouter>
    </GlobalErrorBoundary>
  );
}
