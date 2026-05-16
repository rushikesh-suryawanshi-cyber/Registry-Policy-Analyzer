import axios from 'axios';

// Relative base URL so all requests go through Vite's dev proxy (no CORS issues)
const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000, // 60s for LLM calls
});

// ── Search Endpoints ──────────────────────────────────────────────────────────

export const searchByKeyword = async (q, page = 1, pageSize = 50, sortBy = 'rank') => {
  const { data } = await api.get('/search/keyword', {
    params: { q, page, page_size: pageSize, sort_by: sortBy }
  });
  return data;
};

export const searchByRegistry = async (key, value, page = 1, pageSize = 50) => {
  const { data } = await api.get('/search/registry', {
    params: { key, value, page, page_size: pageSize }
  });
  return data;
};

export const searchByCategory = async (path, page = 1, pageSize = 50) => {
  const { data } = await api.get('/search/category', {
    params: { path, page, page_size: pageSize }
  });
  return data;
};

export const searchByVendor = async (name, page = 1, pageSize = 50) => {
  const { data } = await api.get('/search/vendor', {
    params: { name, page, page_size: pageSize }
  });
  return data;
};

// ── AI Assistant Endpoint ─────────────────────────────────────────────────────

export const chatWithAssistant = async (question, classFilter = null, k = 5) => {
  const { data } = await api.post('/assistant/chat', {
    question,
    class_filter: classFilter,
    k,
  });
  return data; // { answer: string, question: string }
};

// For backward compat
export const searchPolicies = searchByKeyword;

// ── Registry Explorer Endpoints ───────────────────────────────────────────────

export const getRegistryHives = async () => {
  const { data } = await api.get('/registry/hives');
  return data; // { hives: string[] }
};

export const getRegistryChildren = async (path) => {
  const { data } = await api.get('/registry/children', { params: { path } });
  return data; // { path, children: string[], has_policies: bool }
};

export const getRegistryPolicies = async (key, page = 1, pageSize = 100, exact = false) => {
  const { data } = await api.get('/registry/policies', {
    params: { key, page, page_size: pageSize, exact }
  });
  return data; // { key, total_count, items: [...] }
};

export const getRegistryStats = async () => {
  const { data } = await api.get('/registry/stats');
  return data; // { unique_keys, total_policies }
};

export default api;

