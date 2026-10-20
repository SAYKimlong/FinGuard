/**
 * FinGuard API Client
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiOptions {
  method?: string;
  body?: any;
  headers?: Record<string, string>;
  isFormData?: boolean;
}

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function apiRequest<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {}, isFormData = false } = options;

  const token = typeof window !== 'undefined' ? localStorage.getItem('finguard_token') : null;

  const requestHeaders: Record<string, string> = {
    ...headers,
  };

  if (token) {
    requestHeaders['Authorization'] = `Bearer ${token}`;
  }

  if (!isFormData && body) {
    requestHeaders['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    method,
    headers: requestHeaders,
    body: isFormData ? body : body ? JSON.stringify(body) : undefined,
  });

  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('finguard_token');
      localStorage.removeItem('finguard_refresh');
      localStorage.removeItem('finguard_user');
      window.location.href = '/login';
    }
    throw new ApiError('Unauthorized', 401);
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(errorData.detail || 'An error occurred', response.status);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const api = {
  get: <T>(endpoint: string) => apiRequest<T>(endpoint),
  post: <T>(endpoint: string, body?: any) => apiRequest<T>(endpoint, { method: 'POST', body }),
  put: <T>(endpoint: string, body?: any) => apiRequest<T>(endpoint, { method: 'PUT', body }),
  delete: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'DELETE' }),
  upload: <T>(endpoint: string, formData: FormData) =>
    apiRequest<T>(endpoint, { method: 'POST', body: formData, isFormData: true }),
};

// Auth API
export const authApi = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post<{ access_token: string; refresh_token: string }>('/api/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post<{ access_token: string; refresh_token: string }>('/api/auth/login', data),
  me: () => api.get<any>('/api/auth/me'),
  logout: () => api.post('/api/auth/logout'),
};

// Documents API
export const documentsApi = {
  list: (page = 1, pageSize = 20) =>
    api.get<any>(`/api/documents/?page=${page}&page_size=${pageSize}`),
  get: (id: string) => api.get<any>(`/api/documents/${id}`),
  getStatus: (id: string) => api.get<any>(`/api/documents/${id}/status`),
  getAnalysis: (id: string) => api.get<any>(`/api/documents/${id}/analysis`),
  getClauses: (id: string) => api.get<any>(`/api/documents/${id}/clauses`),
  upload: (formData: FormData) => api.upload<any>('/api/documents/upload', formData),
  delete: (id: string) => api.delete(`/api/documents/${id}`),
};

// Financial API
export const financialApi = {
  getProfile: () => api.get<any>('/api/financial/profile'),
  updateProfile: (data: any) => api.put<any>('/api/financial/profile', data),
  calculateRepayment: (data: any) => api.post<any>('/api/financial/repayment/calculate', data),
  getAffordability: (proposedPayment = 0) =>
    api.get<any>(`/api/financial/affordability?proposed_payment=${proposedPayment}`),
  createStressTest: (data: any) => api.post<any>('/api/financial/stress-tests', data),
  listStressTests: () => api.get<any>('/api/financial/stress-tests'),
};

// Chat API
export const chatApi = {
  askAboutClause: (documentId: string, data: { clause_id: string; question: string; language?: string }) =>
    api.post<any>(`/api/chat/clause?document_id=${documentId}`, data),
};

// Reports API
export const reportsApi = {
  getReport: (documentId: string) => api.get<any>(`/api/reports/${documentId}`),
};

export { ApiError };
