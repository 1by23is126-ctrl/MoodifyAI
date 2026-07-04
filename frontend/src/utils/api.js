const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:5000').replace(/\/$/, '');
const SESSION_STORAGE_KEY = 'moodify-session-id';

const buildUrl = (path) => `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;

export function getSessionId() {
  if (typeof window === 'undefined') return 'local-session';
  const existing = window.localStorage.getItem(SESSION_STORAGE_KEY);
  if (existing) return existing;
  const next = `session-${Math.random().toString(36).slice(2, 10)}`;
  window.localStorage.setItem(SESSION_STORAGE_KEY, next);
  return next;
}

export async function request(path, { method = 'GET', body, signal, sessionId } = {}) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    credentials: 'include',
    signal,
  };

  if (sessionId) {
    options.headers['X-Session-Id'] = sessionId;
  }

  if (body !== undefined) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(buildUrl(path), options);
  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json') ? await response.json() : await response.text();

  if (!response.ok) {
    const message = typeof payload === 'object' && payload && payload.error ? payload.error : 'Request failed';
    throw new Error(message);
  }

  return payload;
}

export async function analyze(text, signal, sessionId) {
  return request('/api/analyze', { method: 'POST', body: { text, session_id: sessionId }, signal, sessionId });
}

export async function getCurrentUser() {
  return request('/api/auth/me');
}

export async function loginWithGoogle(idToken) {
  return request('/api/auth/google', { method: 'POST', body: { id_token: idToken } });
}

export async function logout() {
  return request('/api/auth/logout', { method: 'POST' });
}

export async function fetchHistory(params = {}) {
  const url = new URL(buildUrl('/api/history'));
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, value);
    }
  });
  const response = await fetch(url.toString(), { method: 'GET', credentials: 'include' });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || 'Failed to fetch history');
  }
  return payload;
}

export async function fetchJournal(params = {}) {
  const url = new URL(buildUrl('/api/user/journal'));
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, value);
    }
  });
  const response = await fetch(url.toString(), { method: 'GET', credentials: 'include' });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || 'Failed to fetch journal');
  }
  return payload;
}

export async function saveJournalEntry(entry) {
  return request('/api/user/journal', { method: 'POST', body: entry });
}

export async function getSpotifyAuthorizeUrl() {
  return request('/api/spotify/authorize');
}

export async function getHealth() {
  return request('/health');
}
