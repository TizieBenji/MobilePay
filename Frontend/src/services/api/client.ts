import axios, { AxiosError, AxiosRequestConfig } from 'axios';
import Constants from 'expo-constants';
import { getRefreshToken, getToken, removeToken, saveToken } from '@/storage/tokenStorage';

const envUrl = process.env.EXPO_PUBLIC_API_URL;
const appConfigUrl = Constants.expoConfig?.extra?.apiUrl as string | undefined;

export const API_BASE_URL = envUrl || appConfigUrl || 'http://127.0.0.1:5000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    Accept: 'application/json'
  }
});

// AuthContext registers a handler here so that when the refresh token is also
// expired/invalid we can tear down the in-memory session and route to login.
let onSessionExpired: (() => void) | null = null;
export function setOnSessionExpired(handler: (() => void) | null) {
  onSessionExpired = handler;
}

apiClient.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Single-flight: if several requests 401 at once, only one refresh call is made
// and the rest await its result.
let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = await getRefreshToken();
  if (!refreshToken) return null;

  try {
    // Bare axios (not apiClient) so the request interceptor doesn't attach the
    // stale access token and the response interceptor doesn't recurse.
    const response = await axios.post<{ token?: string; access_token?: string }>(
      `${API_BASE_URL}/auth/refresh`,
      {},
      { headers: { Authorization: `Bearer ${refreshToken}` } }
    );
    const newToken = response.data.token || response.data.access_token || null;
    if (newToken) {
      await saveToken(newToken);
      return newToken;
    }
    return null;
  } catch {
    return null;
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (AxiosRequestConfig & { _retry?: boolean }) | undefined;
    const status = error.response?.status;
    const url = original?.url ?? '';

    // Only attempt a refresh on a genuine 401, once per request, and never for
    // the auth endpoints themselves (those 401s mean bad credentials/refresh).
    const isAuthEndpoint = url.includes('/auth/login') || url.includes('/auth/refresh');

    if (status === 401 && original && !original._retry && !isAuthEndpoint) {
      original._retry = true;

      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }
      const newToken = await refreshPromise;

      if (newToken) {
        original.headers = { ...original.headers, Authorization: `Bearer ${newToken}` };
        return apiClient(original);
      }

      // Refresh failed: drop the dead access token and let AuthContext sign out.
      await removeToken();
      onSessionExpired?.();
    }

    return Promise.reject(error);
  }
);

export function getApiError(error: unknown, fallback = 'Something went wrong.') {
  if (error instanceof AxiosError) {
    const data = error.response?.data as { message?: string; error?: string } | undefined;
    return data?.message || data?.error || error.message || fallback;
  }
  if (error instanceof Error) return error.message;
  return fallback;
}
