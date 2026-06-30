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

  // The backend does not yet expose a profile-update endpoint, so this merges
  // the edits onto the current server profile and returns them for local/UI
  // use only. Wire this to a real PUT once the backend supports it.
  async updateProfile(payload: Partial<User>): Promise<User> {
    try {
      const current = await this.getProfile();
      return { ...current, ...payload };
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
