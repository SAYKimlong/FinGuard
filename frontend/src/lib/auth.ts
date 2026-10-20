/**
 * FinGuard Auth Store (Zustand)
 */
import { create } from 'zustand';
import { authApi } from './api';

interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    const response = await authApi.login({ email, password });
    localStorage.setItem('finguard_token', response.access_token);
    localStorage.setItem('finguard_refresh', response.refresh_token);
    const user = await authApi.me();
    localStorage.setItem('finguard_user', JSON.stringify(user));
    set({ user, isAuthenticated: true, isLoading: false });
  },

  register: async (email: string, password: string, fullName: string) => {
    const response = await authApi.register({ email, password, full_name: fullName });
    localStorage.setItem('finguard_token', response.access_token);
    localStorage.setItem('finguard_refresh', response.refresh_token);
    const user = await authApi.me();
    localStorage.setItem('finguard_user', JSON.stringify(user));
    set({ user, isAuthenticated: true, isLoading: false });
  },

  logout: () => {
    localStorage.removeItem('finguard_token');
    localStorage.removeItem('finguard_refresh');
    localStorage.removeItem('finguard_user');
    set({ user: null, isAuthenticated: false, isLoading: false });
    window.location.href = '/login';
  },

  loadUser: async () => {
    const token = localStorage.getItem('finguard_token');
    if (!token) {
      set({ user: null, isAuthenticated: false, isLoading: false });
      return;
    }
    try {
      const user = await authApi.me();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      localStorage.removeItem('finguard_token');
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
