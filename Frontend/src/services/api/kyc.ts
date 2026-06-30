import { apiClient, getApiError } from './client';
import { KycUploadPayload } from '@/types/kyc';

export const kycApi = {
  async uploadKyc(payload: KycUploadPayload): Promise<void> {
    try {
      const formData = new FormData();
      formData.append('national_id', payload.nationalId);
      formData.append('residential_address', payload.residentialAddress);
      formData.append('id_front', payload.idFront as any);
      formData.append('id_back', payload.idBack as any);
      formData.append('selfie', payload.selfie as any);

      await apiClient.post('/kyc/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to upload KYC.'));
    }
  },

  async getStatus(): Promise<string> {
    try {
      const response = await apiClient.get<{ status: string }>('/kyc/status');
      return response.data.status;
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to fetch KYC status.'));
    }
  }
};
