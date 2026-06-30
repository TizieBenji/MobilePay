import { apiClient, getApiError } from './client';
import { TransferRequest, TransferResponse } from '@/types/transfer';

export const transferApi = {
  async createTransfer(payload: TransferRequest): Promise<TransferResponse> {
    try {
      // Internal wallet-to-wallet transfer. The backend resolves the recipient
      // by phone number (see transfer_routes.py).
      const response = await apiClient.post<any>('/transfer', {
        receiver_phone: payload.receiver,
        amount: payload.amount
      });
      const data = response.data?.data || response.data;
      return {
        id: data.id || data.transaction_id || data.reference || data.reference_id || String(Date.now()),
        referenceId: data.reference || data.reference_id || data.referenceId || `MP-${Date.now()}`,
        status: data.status || (data.success ? 'SUCCESS' : 'PENDING')
      };
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to complete transfer.'));
    }
  }
};
