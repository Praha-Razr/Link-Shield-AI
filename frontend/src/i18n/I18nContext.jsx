import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { EN } from './en';
import { HI } from './hi';
import { INDICATORS_HI, INDICATOR_NAME_LOOKUP_HI } from './indicators';

const I18nContext = createContext(null);

const STORAGE_KEY = 'linkshield_lang';

export function I18nProvider({ children }) {
  const [lang, setLangState] = useState(() => {
    try {
      if (typeof window !== 'undefined') {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved === 'hi' || saved === 'en') return saved;
      }
    } catch {
      // Ignore localStorage errors
    }
    return 'en';
  });

  const setLang = useCallback((newLang) => {
    const valid = newLang === 'hi' ? 'hi' : 'en';
    setLangState(valid);
    try {
      if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, valid);
      }
    } catch {
      // Ignore localStorage errors
    }
  }, []);

  const toggleLang = useCallback(() => {
    setLang((prev) => (prev === 'en' ? 'hi' : 'en'));
  }, [setLang]);

  // t("key", paramsOrFallback)
  const t = useCallback((key, fallback) => {
    if (!key) return '';
    const dict = lang === 'hi' ? HI : EN;
    if (dict && Object.prototype.hasOwnProperty.call(dict, key)) {
      return dict[key];
    }
    // Fallback to English
    if (EN && Object.prototype.hasOwnProperty.call(EN, key)) {
      return EN[key];
    }
    return fallback !== undefined ? fallback : key;
  }, [lang]);

  // Indicator translation helper
  const translateIndicator = useCallback((ind) => {
    if (!ind) return ind;
    if (lang !== 'hi') return ind;

    // 1. Try lookup by indicator ID
    if (ind.id && INDICATORS_HI[ind.id]) {
      const hiData = INDICATORS_HI[ind.id];
      return {
        ...ind,
        name: hiData.name || ind.name,
        explanation: hiData.explanation || ind.explanation,
      };
    }

    // 2. Try lookup by exact English name
    if (ind.name && INDICATOR_NAME_LOOKUP_HI[ind.name]) {
      return {
        ...ind,
        name: INDICATOR_NAME_LOOKUP_HI[ind.name],
      };
    }

    // Fallback: original English indicator untouched
    return ind;
  }, [lang]);

  const value = useMemo(() => ({
    lang,
    isHindi: lang === 'hi',
    setLang,
    toggleLang,
    t,
    translateIndicator,
  }), [lang, setLang, toggleLang, t, translateIndicator]);

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
}
