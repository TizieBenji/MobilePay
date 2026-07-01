import { apiClient, getApiError } from './client';
import { AuthResponse } from '@/types/auth';
import { Network, User } from '@/types/user';

export type LoginRequest = {
  emailOrPhone: string;
  password: string;
};

export type RegisterRequest = {
  fullname: string;
  dateOfBirth: string;
  phone: string;
  email: string;
  password: string;
  network: Network;
};

type BackendAuthResponse = {
  access_token?: string;
  token?: string;
  refresh_token?: string;
  user?: Partial<User> & { is_admin?: boolean };
  data?: {
    access_token?: string;
    token?: string;
    refresh_token?: string;
    user?: Partial<User> & { is_admin?: boolean };
  };
};

export const authApi = {
  async register(payload: RegisterRequest): Promise<AuthResponse> {
    try {
      // Backend (/api/auth/register) expects exactly these fields; dateOfBirth
      // is collected in the UI but not yet stored server-side.
      const response = await apiClient.post<BackendAuthResponse>('/auth/register', {
        fullname: payload.fullname,
        email: payload.email,
        phone: payload.phone,
        password: payload.password,
        network: payload.network
      });
      return normalizeAuthResponse(response.data, payload);
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to register.'));
    }
  },

  async login(payload: LoginRequest): Promise<AuthResponse> {
    try {
      // Backend logs in by email only. The UI field accepts "email or phone";
      // we forward it as email (phone login is not yet supported server-side).
      const response = await apiClient.post<BackendAuthResponse>('/auth/login', {
        email: payload.emailOrPhone,
        password: payload.password
      });
      return normalizeAuthResponse(response.data, payload);
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to login.'));
    }
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch {
      // Local logout must still continue even if the backend logout endpoint is unavailable.
    }
  },

  async forgotPassword(emailOrPhone: string): Promise<void> {
    try {
      await apiClient.post('/forgot-password', { emailOrPhone });
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to submit password reset request.'));
    }
  }
};

function normalizeAuthResponse(data: BackendAuthResponse, fallback: Partial<User> & { emailOrPhone?: string }): AuthResponse {
  const body = data.data || data;
  const token = body.access_token || body.token;
  if (!token) {
    throw new Error('Server response did not include an auth token.');
  }
  const refreshToken = body.refresh_token || null;
  const backendUser = body.user || {};

  const user: User = {
    id: backendUser.id != null ? String(backendUser.id) : 'local-user',
    fullname: backendUser.fullname || fallback.fullname || 'MobilePay User',
    email: backendUser.email || fallback.email || (fallback.emailOrPhone?.includes('@') ? fallback.emailOrPhone : ''),
    phone: backendUser.phone || fallback.phone || (!fallback.emailOrPhone?.includes('@') ? fallback.emailOrPhone || '' : ''),
    network: backendUser.network || fallback.network || null,
    kycStatus: backendUser.kycStatus || 'PENDING',
    createdAt: backendUser.createdAt || new Date().toISOString(),
    isAdmin: backendUser.is_admin || false
  };

  return { token, refreshToken, user };
}
