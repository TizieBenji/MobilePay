import axios, { AxiosError } from 'axios';
import Constants from 'expo-constants';
import { getToken } from '@/storage/tokenStorage';

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

apiClient.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function getApiError(error: unknown, fallback = 'Something went wrong.') {
  if (error instanceof AxiosError) {
    const data = error.response?.data as { message?: string; error?: string } | undefined;
    return data?.message || data?.error || error.message || fallback;
  }
  if (error instanceof Error) return error.message;
  return fallback;
}
