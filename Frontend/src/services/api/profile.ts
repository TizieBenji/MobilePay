import { apiClient, getApiError } from './client';
import { User } from '@/types/user';

export const profileApi = {
  async getProfile(): Promise<User> {
    try {
      const response = await apiClient.get<any>('/user/me');
      return normalizeUser(response.data?.data || response.data);
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to fetch profile.'));
    }
  },

  async updateProfile(payload: Partial<User>): Promise<User> {
    try {
      const response = await apiClient.patch<any>('/user/me', {
        fullname: payload.fullname,
        email: payload.email
      });
      return normalizeUser(response.data?.data || response.data);
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to update profile.'));
    }
  }
};

function normalizeUser(data: any): User {
  return {
    id: String(data.id || ''),
    fullname: data.fullname || data.full_name || '',
    email: data.email || '',
    phone: data.phone || '',
    network: data.network || null,
    kycStatus: data.kyc_status || data.kycStatus || 'PENDING',
    createdAt: data.created_at || data.createdAt || ''
  };
}
