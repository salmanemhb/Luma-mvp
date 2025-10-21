import axios from 'axios';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/api/auth/login', { email, password }),
  
  signup: (data: { email: string; password: string; company_name: string; sector?: string; country?: string }) =>
    api.post('/api/auth/signup', data),
  
  me: () =>
    api.get('/api/auth/me'),
  
  logout: () =>
    api.post('/api/auth/logout'),
};

// Upload APIs
export const uploadAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  listDocuments: () =>
    api.get('/api/upload/documents'),
  
  getDocument: (id: string) =>
    api.get(`/api/upload/documents/${id}`),
  
  deleteDocument: (id: string) =>
    api.delete(`/api/upload/documents/${id}`),
};

// Analysis APIs
export const analyzeAPI = {
  analyze: (documentId: string) =>
    api.post(`/api/analyze/${documentId}`),
  
  getStatus: (documentId: string) =>
    api.get(`/api/analyze/status/${documentId}`),
};

// Dashboard APIs
export const dashboardAPI = {
  getData: (params?: { year?: number; start_date?: string; end_date?: string }) =>
    api.get('/api/dashboard/', { params }),
  
  getRecords: (params?: { limit?: number; offset?: number }) =>
    api.get('/api/dashboard/records', { params }),
  
  getStats: () =>
    api.get('/api/dashboard/stats'),
};

// Report APIs
export const reportAPI = {
  generate: (companyId: string, year?: number) =>
    api.post(`/api/report/${companyId}`, null, { params: { year } }),
  
  list: () =>
    api.get('/api/report/list'),
  
  getReport: (reportId: string) =>
    api.get(`/api/report/${reportId}`),
  
  downloadPDF: (reportId: string) =>
    api.get(`/api/report/${reportId}/download/pdf`, { responseType: 'blob' }),
  
  downloadExcel: (reportId: string) =>
    api.get(`/api/report/${reportId}/download/excel`, { responseType: 'blob' }),
};

// Admin APIs
export const adminAPI = {
  listCompanies: (params?: { status_filter?: string; sector?: string }) =>
    api.get('/api/admin/companies', { params }),
  
  getCompanyDetail: (companyId: string) =>
    api.get(`/api/admin/company/${companyId}`),
  
  getActivity: (params?: { event_type?: string; company_id?: string; page?: number; page_size?: number }) =>
    api.get('/api/admin/activity', { params }),
  
  getInsights: (params?: { from_date?: string; to_date?: string }) =>
    api.get('/api/admin/insights', { params }),
  
  exportData: (format: 'csv' | 'xlsx', range: 'last_month' | 'last_12m' | 'all') =>
    api.get('/api/admin/export', {
      params: { format, range },
      responseType: 'blob',
    }),
  
  aggregateStats: (month?: string) =>
    api.post('/api/admin/aggregate-stats', null, { params: { month } }),
  
  // Waitlist management from landing page
  getWaitlistSubmissions: (params?: { skip?: number; limit?: number; role?: string; search?: string }) =>
    api.get('/api/admin/waitlist', { params }),
  
  getWaitlistDetail: (id: number) =>
    api.get(`/api/admin/waitlist/${id}`),
  
  promoteWaitlistUser: (id: number) =>
    api.post(`/api/admin/waitlist/${id}/promote`),
  
  deleteWaitlistSubmission: (id: number) =>
    api.delete(`/api/admin/waitlist/${id}`),
  
  getWaitlistStats: () =>
    api.get('/api/admin/stats'),
};

export default api;
