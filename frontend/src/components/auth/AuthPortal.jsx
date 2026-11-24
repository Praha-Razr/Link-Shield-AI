import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Shield,
  ShieldCheck,
  UserCheck,
  ArrowLeft,
  Lock,
  User,
  KeyRound,
  AlertCircle,
  Eye,
  EyeOff,
  Sparkles,
  CheckCircle2
} from 'lucide-react';
import { useRole } from '../../context/RoleContext';
import { useI18n } from '../../i18n/I18nContext';
import LanguageToggle from '../LanguageToggle';

export default function AuthPortal() {
  const { login, register } = useRole();
  const { t, lang } = useI18n();
  const navigate = useNavigate();

  // Mode: null (role selection) | 'citizen' | 'officer'
  const [selectedRole, setSelectedRole] = useState(null);

  // For Citizen: 'login' | 'register'
  const [citizenMode, setCitizenMode] = useState('login');

  // Form Fields
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // States
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Reset form when switching roles
  const handleSelectRole = (role) => {
    setSelectedRole(role);
    setCitizenMode('login');
    setUsername('');
    setPassword('');
    setDisplayName('');
    setError(null);
    setSuccessMsg(null);
  };

  const handleBackToRoles = () => {
    setSelectedRole(null);
    setError(null);
    setSuccessMsg(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);

    const cleanUsername = username.trim();
    if (!cleanUsername) {
      setError(t('auth.err_username_required'));
      return;
    }
    if (!password) {
      setError(t('auth.err_password_required'));
      return;
    }

    if (selectedRole === 'citizen' && citizenMode === 'register') {
      if (!displayName.trim()) {
        setError(t('auth.err_name_required'));
        return;
      }
      if (password.length < 8) {
        setError(t('auth.err_password_len'));
        return;
      }
    }

    setLoading(true);
    try {
      if (selectedRole === 'citizen' && citizenMode === 'register') {
        await register(cleanUsername, password, displayName.trim());
      } else {
        await login(cleanUsername, password);
      }
      navigate('/', { replace: true });
    } catch (err) {
      setError(err.message || 'Authentication failed. Please verify your credentials.');
    } finally {
      setLoading(false);
    }
  };

  // Helper to prefill officer demo credentials
  const fillOfficerDemo = () => {
    setUsername('officer_sharma');
    setPassword('Officer@Shield2026');
    setError(null);
  };

  return (
    <div className="min-h-screen bg-[#070D1E] text-slate-100 flex flex-col justify-between p-4 sm:p-6 md:p-8 font-sans relative overflow-hidden">
      {/* Background Decorative Gradients */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Top Header / Brand */}
      <div className="relative z-10 max-w-5xl w-full mx-auto flex items-center justify-between py-2">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 via-indigo-600 to-cyan-500 p-0.5 shadow-lg shadow-cyan-500/20">
            <div className="w-full h-full bg-[#091124] rounded-[10px] flex items-center justify-center">
              <Shield className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="font-mono font-bold text-lg tracking-wider text-white">
              LINKSHIELD <span className="text-cyan-400">AI</span>
            </div>
            <div className="text-[10px] text-slate-400 font-mono tracking-widest uppercase">
              Cyber Threat Intelligence & Defense
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800 text-[11px] text-slate-400 font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>CYBER HELPLINE: 1930</span>
          </div>
          <LanguageToggle variant="dark" />
        </div>
      </div>

      {/* Main Container */}
      <div className="relative z-10 max-w-5xl w-full mx-auto my-auto py-8">
        {!selectedRole ? (
          /* ============================================================ */
          /* STEP 1: ROLE SELECTION CARDS                                 */
          /* ============================================================ */
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-block px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/60 text-cyan-400 text-xs font-mono font-semibold mb-4">
              SECURE ACCESS GATEWAY
            </div>
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-white tracking-tight mb-3">
              {t('role.select_title')}
            </h2>
            <p className="text-sm text-slate-400 max-w-lg mx-auto mb-10">
              {t('role.select_subtitle')}
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
              {/* Citizen Card */}
              <div
                onClick={() => handleSelectRole('citizen')}
                className="group p-6 sm:p-8 rounded-2xl bg-[#0C152B]/80 hover:bg-[#0E1A36] border border-slate-800 hover:border-emerald-500/50 transition-all duration-200 shadow-xl hover:shadow-emerald-500/10 cursor-pointer flex flex-col justify-between relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 rounded-full blur-2xl group-hover:bg-emerald-500/10 transition-colors pointer-events-none" />
                <div>
                  <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                    <UserCheck className="w-6 h-6" />
                  </div>
                  <div className="inline-block px-2.5 py-0.5 rounded-md bg-emerald-950/80 border border-emerald-800/60 text-emerald-300 text-[10px] font-mono font-semibold tracking-wider uppercase mb-2">
                    {lang === 'hi' ? 'नागरिक सुरक्षा' : 'Public Protection'}
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors">
                    {t('role.citizen_title')}
                  </h3>
                  <p className="text-xs text-slate-400 leading-relaxed mb-6">
                    {t('role.citizen_desc')}
                  </p>
                </div>

                <div className="flex items-center text-xs font-bold text-emerald-400 group-hover:translate-x-1 transition-transform">
                  <span>{t('role.citizen_action')} &rarr;</span>
                </div>
              </div>

              {/* Officer Card */}
              <div
                onClick={() => handleSelectRole('officer')}
                className="group p-6 sm:p-8 rounded-2xl bg-[#0C152B]/80 hover:bg-[#0E1A36] border border-slate-800 hover:border-cyan-500/50 transition-all duration-200 shadow-xl hover:shadow-cyan-500/10 cursor-pointer flex flex-col justify-between relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/5 rounded-full blur-2xl group-hover:bg-cyan-500/10 transition-colors pointer-events-none" />
                <div>
                  <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 text-cyan-400 flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                    <ShieldCheck className="w-6 h-6" />
                  </div>
                  <div className="inline-block px-2.5 py-0.5 rounded-md bg-cyan-950/80 border border-cyan-800/60 text-cyan-300 text-[10px] font-mono font-semibold tracking-wider uppercase mb-2">
                    Authorized Personnel Only
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2 group-hover:text-cyan-300 transition-colors">
                    {t('role.officer_title')}
                  </h3>
                  <p className="text-xs text-slate-400 leading-relaxed mb-6">
                    {t('role.officer_desc')}
                  </p>
                </div>

                <div className="flex items-center text-xs font-bold text-cyan-400 group-hover:translate-x-1 transition-transform">
                  <span>{t('role.officer_action')} &rarr;</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* ============================================================ */
          /* STEP 2: LOGIN / REGISTRATION FORM                            */
          /* ============================================================ */
          <div className="max-w-md mx-auto">
            {/* Back Button */}
            <button
              type="button"
              onClick={handleBackToRoles}
              className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors mb-6 cursor-pointer font-mono"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>{t('role.back_to_select')}</span>
            </button>

            {/* Form Card */}
            <div className="p-6 sm:p-8 rounded-2xl bg-[#0C152B]/90 border border-slate-800 shadow-2xl relative">
              {/* Header Badge & Title */}
              <div className="text-center mb-6">
                <div
                  className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-semibold mb-3 ${
                    selectedRole === 'officer'
                      ? 'bg-blue-950/80 border border-blue-800 text-cyan-400'
                      : 'bg-emerald-950/80 border border-emerald-800 text-emerald-400'
                  }`}
                >
                  {selectedRole === 'officer' ? (
                    <>
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>{lang === 'hi' ? 'साइबर सेल अधिकारी पोर्टल' : 'LAW ENFORCEMENT PORTAL'}</span>
                    </>
                  ) : (
                    <>
                      <UserCheck className="w-3.5 h-3.5" />
                      <span>{lang === 'hi' ? 'नागरिक सुरक्षा पोर्टल' : 'CITIZEN ACCESS PORTAL'}</span>
                    </>
                  )}
                </div>

                <h2 className="text-xl sm:text-2xl font-bold text-white">
                  {selectedRole === 'officer'
                    ? t('auth.officer_login_title')
                    : citizenMode === 'register'
                    ? t('auth.citizen_reg_title')
                    : t('auth.citizen_login_title')}
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  {selectedRole === 'officer'
                    ? t('auth.officer_login_desc')
                    : citizenMode === 'register'
                    ? t('auth.citizen_reg_desc')
                    : t('auth.citizen_login_desc')}
                </p>
              </div>

              {/* Citizen Toggle between Login & Register */}
              {selectedRole === 'citizen' && (
                <div className="flex bg-slate-900/90 p-1 rounded-lg border border-slate-800 mb-6">
                  <button
                    type="button"
                    onClick={() => {
                      setCitizenMode('login');
                      setError(null);
                    }}
                    className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-all cursor-pointer ${
                      citizenMode === 'login'
                        ? 'bg-emerald-600 text-white shadow-xs'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {t('auth.login_btn')}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setCitizenMode('register');
                      setError(null);
                    }}
                    className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-all cursor-pointer ${
                      citizenMode === 'register'
                        ? 'bg-emerald-600 text-white shadow-xs'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {t('auth.register_btn')}
                  </button>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="mb-4 p-3 rounded-lg bg-rose-950/50 border border-rose-800/80 text-rose-300 text-xs flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                  <span>{error}</span>
                </div>
              )}

              {/* Demo Credentials Box for Officer Mode */}
              {selectedRole === 'officer' && (
                <div className="mb-5 p-3 rounded-xl bg-blue-950/40 border border-blue-800/60 text-xs">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-semibold text-cyan-300 font-mono text-[11px] flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                      DEMO CREDENTIALS:
                    </span>
                    <button
                      type="button"
                      onClick={fillOfficerDemo}
                      className="text-[10px] font-mono text-cyan-400 hover:text-cyan-200 underline cursor-pointer"
                    >
                      Auto-fill
                    </button>
                  </div>
                  <div className="font-mono text-[11px] text-slate-300 space-y-0.5">
                    <div>User: <span className="text-white font-semibold">officer_sharma</span></div>
                    <div>Pass: <span className="text-white font-semibold">Officer@Shield2026</span></div>
                  </div>
                </div>
              )}

              {/* Form Fields */}
              <form onSubmit={handleSubmit} className="space-y-4">
                {selectedRole === 'citizen' && citizenMode === 'register' && (
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">
                      {t('auth.fullname')}
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        value={displayName}
                        onChange={(e) => setDisplayName(e.target.value)}
                        placeholder={t('auth.fullname_placeholder')}
                        className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-hidden focus:border-emerald-500"
                        required
                      />
                      <User className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    {t('auth.username')}
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder={selectedRole === 'officer' ? 'officer_sharma' : t('auth.username_placeholder')}
                      className={`w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-hidden ${
                        selectedRole === 'officer'
                          ? 'focus:border-cyan-500'
                          : 'focus:border-emerald-500'
                      }`}
                      required
                    />
                    <KeyRound className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="block text-xs font-medium text-slate-300">
                      {t('auth.password')}
                    </label>
                    {selectedRole === 'citizen' && citizenMode === 'register' && (
                      <span className="text-[10px] text-slate-500 font-mono">
                        {lang === 'hi' ? 'कम से कम 8 अक्षर' : 'Min 8 chars'}
                      </span>
                    )}
                  </div>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder={t('auth.password_placeholder')}
                      className={`w-full pl-9 pr-10 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-hidden ${
                        selectedRole === 'officer'
                          ? 'focus:border-cyan-500'
                          : 'focus:border-emerald-500'
                      }`}
                      required
                    />
                    <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300 cursor-pointer"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full py-2.5 px-4 rounded-lg text-xs font-bold text-white transition-all cursor-pointer shadow-lg disabled:opacity-50 disabled:cursor-not-allowed ${
                    selectedRole === 'officer'
                      ? 'bg-blue-600 hover:bg-blue-500 shadow-blue-600/20'
                      : 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-600/20'
                  }`}
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="w-3.5 h-3.5 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                      <span>{citizenMode === 'register' ? t('auth.registering') : t('auth.signing_in')}</span>
                    </span>
                  ) : selectedRole === 'officer' ? (
                    'Authenticate Officer Credentials'
                  ) : citizenMode === 'register' ? (
                    t('auth.register_btn')
                  ) : (
                    lang === 'hi' ? 'नागरिक के रूप में साइन इन करें' : 'Sign In as Citizen'
                  )}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="relative z-10 max-w-5xl w-full mx-auto text-center py-2 text-[11px] text-slate-500">
        {t('footer.disclaimer')}
      </div>
    </div>
  );
}
