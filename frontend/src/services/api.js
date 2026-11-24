const getApiBase = () => {
  const envBase = import.meta.env.VITE_API_BASE_URL;
  if (envBase) {
    return envBase.replace(/\/+$/, '');
  }
  const host = typeof window !== 'undefined' && window.location.hostname === '127.0.0.1' 
    ? '127.0.0.1' 
    : 'localhost';
  return `http://${host}:8000/api`;
};

const API_BASE = getApiBase();

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const defaultHeaders = {
    'Accept': 'application/json',
  };

  const token = typeof window !== 'undefined' ? sessionStorage.getItem('linkshield_token') : null;
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  if (!(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorJson.message || JSON.stringify(errorJson);
    } catch {
      // fallback
    }
    const error = new Error(errorDetail);
    error.status = response.status;
    throw error;
  }

  return response.json();
}

export const api = {
  // Auth & User
  login: (username, password) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  register: (username, password, display_name) =>
    request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password, display_name }),
    }),

  logout: () =>
    request('/auth/logout', {
      method: 'POST',
    }),

  getMe: () => request('/auth/me'),

  // Public Awareness (Aggregate only for citizens & officers)
  getPublicAwareness: () => request('/public/awareness'),

  // Health
  getHealth: () => request('/health'),

  // Dashboard Stats
  getDashboardStats: () => request('/dashboard/stats'),

  // Analysis
  analyzeMessage: (content, subject) =>
    request('/analyze/message', {
      method: 'POST',
      body: JSON.stringify({ content, subject }),
    }),

  analyzeUrl: (url, subject, performLiveCheck = false) =>
    request('/analyze/url', {
      method: 'POST',
      body: JSON.stringify({ url, subject, perform_live_check: performLiveCheck }),
    }),

  analyzeWebsite: (payload) => {
    if (payload instanceof FormData) {
      return request('/analyze/website', {
        method: 'POST',
        body: payload,
      });
    }
    return request('/analyze/website', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Cases
  getCases: (params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.q) searchParams.append('q', params.q);
    if (params.risk && params.risk !== 'ALL') searchParams.append('risk', params.risk);
    if (params.category && params.category !== 'ALL') searchParams.append('category', params.category);
    if (params.input_type && params.input_type !== 'ALL') searchParams.append('input_type', params.input_type);
    if (params.date_from) searchParams.append('date_from', params.date_from);
    if (params.date_to) searchParams.append('date_to', params.date_to);
    if (params.include_demo !== undefined) searchParams.append('include_demo', params.include_demo);
    if (params.page) searchParams.append('page', params.page);
    if (params.page_size) searchParams.append('page_size', params.page_size);

    const qs = searchParams.toString();
    return request(`/cases${qs ? `?${qs}` : ''}`);
  },

  getCaseDetail: (caseId) => request(`/cases/${encodeURIComponent(caseId)}`),

  updateCaseNotes: (caseId, notes) =>
    request(`/cases/${encodeURIComponent(caseId)}/notes`, {
      method: 'PATCH',
      body: JSON.stringify({ notes }),
    }),

  // Demo management
  loadDemoData: () =>
    request('/demo/load', {
      method: 'POST',
    }),

  clearDemoData: () =>
    request('/demo/clear', {
      method: 'POST',
      body: JSON.stringify({ confirm: true }),
    }),

  // Intelligence
  getGraph: (includeDemo = true, minCases = 2) =>
    request(`/intelligence/graph?include_demo=${includeDemo}&min_cases=${minCases}`),
  getHeatlist: (params = {}) => {
    const sp = new URLSearchParams();
    if (params.type) sp.append('type', params.type);
    if (params.include_demo !== undefined) sp.append('include_demo', params.include_demo);
    if (params.limit) sp.append('limit', params.limit);
    const qs = sp.toString();
    return request(`/intelligence/heatlist${qs ? `?${qs}` : ''}`);
  },

  // Reports
  getPdfUrl: (caseId) => {
    const cleanId = String(caseId || '').trim();
    return `${API_BASE}/reports/${encodeURIComponent(cleanId)}/pdf`;
  },
  downloadCasePdf: async (caseId) => {
    const cleanId = String(caseId || '').trim();
    if (!cleanId) throw new Error('Missing case ID for PDF generation');
    const url = `${API_BASE}/reports/${encodeURIComponent(cleanId)}/pdf`;

    try {
      const token = typeof window !== 'undefined' ? sessionStorage.getItem('linkshield_token') : null;
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const res = await fetch(url, { headers, credentials: 'include' });
      if (!res.ok) {
        let errMessage = `Server returned status ${res.status}`;
        try {
          const j = await res.json();
          if (j.detail) errMessage = j.detail;
        } catch {
          // not JSON
        }
        throw new Error(errMessage);
      }

      const blob = await res.blob();
      if (!blob || blob.size === 0) {
        throw new Error('Received empty PDF payload from server');
      }

      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `LinkShield_Report_${cleanId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      // Keep blob alive for 60 seconds so browser download manager has completed disk write
      setTimeout(() => {
        try {
          window.URL.revokeObjectURL(blobUrl);
        } catch {}
      }, 60000);
      return true;
    } catch (err) {
      console.warn(`Direct blob download failed for case ${cleanId}: ${err.message}. Trying direct browser fallback...`);
      // If error was NOT a specific HTTP status error, attempt native link fallback
      if (!err.message.includes('status') && !err.message.includes('not found') && !err.message.includes('Failed to generate')) {
        try {
          const a = document.createElement('a');
          a.href = url;
          a.download = `LinkShield_Report_${cleanId}.pdf`;
          a.target = '_blank';
          document.body.appendChild(a);
          a.click();
          a.remove();
          return true;
        } catch {}
      }
      throw err;
    }
  },

  // Investigation Assistant
  getAssistantStatus: () => request('/assistant/status'),
  askAssistant: (question, useEnhanced = true, history = []) =>
    request('/assistant/ask', {
      method: 'POST',
      body: JSON.stringify({ question, use_enhanced: useEnhanced, history }),
    }),
};
