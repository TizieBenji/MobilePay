import { Platform } from 'react-native';
import { apiClient, getApiError } from './client';
import { ImageAsset, KycUploadPayload } from '@/types/kyc';

// On native, RN's fetch/FormData accepts the {uri, name, type} shape directly.
// On web, asset.uri is a blob: URL that must be fetched into a real Blob first.
async function toFormValue(asset: ImageAsset): Promise<any> {
  if (Platform.OS !== 'web') {
    return asset as any;
  }
  const blob = await (await fetch(asset.uri)).blob();
  return new File([blob], asset.name, { type: asset.type });
}

export const kycApi = {
  async uploadKyc(payload: KycUploadPayload): Promise<void> {
    try {
      const [front, back, selfie] = await Promise.all([
        toFormValue(payload.idFront),
        toFormValue(payload.idBack),
        toFormValue(payload.selfie)
      ]);

      const formData = new FormData();
      formData.append('national_id_number', payload.nationalId);
      formData.append('residential_address', payload.residentialAddress);
      formData.append('document_type', 'NATIONAL_ID');
      formData.append('front', front);
      formData.append('back', back);
      formData.append('selfie', selfie);

      // Do not set Content-Type manually: the browser/axios needs to generate
      // it itself so the multipart boundary is included, otherwise Flask
      // can't parse request.form/request.files and returns 400.
      await apiClient.post('/kyc/submit', formData);
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
