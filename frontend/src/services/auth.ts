import { apiClient } from './api';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  display_name: string;
  active: boolean;
  roles: string[];
  tenant_id: string;
}

export const authApi = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('spendshield_token', response.data.access_token);
    }
    return response.data;
  },

  logout: async (): Promise<void> => {
    const refreshToken = localStorage.getItem('spendshield_refresh_token');
    try {
      await apiClient.post('/auth/logout', { refresh_token: refreshToken || '' });
    } catch (e) {
      // Ignore network errors on logout
    }
    localStorage.removeItem('spendshield_token');
    localStorage.removeItem('spendshield_refresh_token');
    window.location.href = '/login';
  },

  getMe: async (): Promise<UserResponse> => {
    const response = await apiClient.get<UserResponse>('/auth/me');
    return response.data;
  }
};
