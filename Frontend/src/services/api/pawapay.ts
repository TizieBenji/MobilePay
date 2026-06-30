import { apiClient, getApiError } from './client';
import { PaymentRequest, PaymentResult } from '@/types/payment';
import { normalizePhone } from '@/utils/phone';

// The backend "polling" path blocks while it polls PawaPay for a final status
// (up to ~50s). That is longer than the client's default 15s timeout, so we
// give these requests their own generous timeout. This is the intended local
// dev flow (PAWAPAY_ALLOW_POLLING=true) when webhooks can't reach the server.
const POLL_TIMEOUT_MS = 60000;

function normalizeResult(raw: any): PaymentResult {
  const data = raw?.data || raw || {};
  return {
    success: Boolean(data.success),
    message: data.message || '',
    id: data.deposit_id || data.payout_id || data.id || '',
    pawaStatus: data.pawa_status || data.status || 'PENDING',
    walletProcessed: Boolean(data.wallet_credited ?? data.wallet_debited ?? false),
    correspondent: data.correspondent,
    amount: data.amount,
    currency: data.currency
  };
}

export const pawapayApi = {
  // Collection = customer pays IN from a mobile-money number; wallet is credited.
  async collect({ phone, amount }: PaymentRequest): Promise<PaymentResult> {
    try {
      const response = await apiClient.post<any>(
        '/pawapay/collect',
        { phone: normalizePhone(phone), amount, polling: true },
        { timeout: POLL_TIMEOUT_MS }
      );
      return normalizeResult(response.data);
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to start the top-up.'));
    }
  },

  // Disbursement = platform pays OUT to a mobile-money number; wallet is debited.
  async disburse({ phone, amount }: PaymentRequest): Promise<PaymentResult> {
    try {
      const response = await apiClient.post<any>(
        '/pawapay/disburse',
        { phone: normalizePhone(phone), amount, polling: true },
        { timeout: POLL_TIMEOUT_MS }
      );
      return normalizeResult(response.data);
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to start the withdrawal.'));
    }
  },

  async getCollectionStatus(depositId: string): Promise<PaymentResult> {
    try {
      const response = await apiClient.get<any>(`/pawapay/collect/${depositId}`);
      return normalizeResult(response.data);
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to fetch top-up status.'));
    }
  },

  async getDisbursementStatus(payoutId: string): Promise<PaymentResult> {
    try {
      const response = await apiClient.get<any>(`/pawapay/disburse/${payoutId}`);
      return normalizeResult(response.data);
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to fetch withdrawal status.'));
    }
  }
};
