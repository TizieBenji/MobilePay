import { apiClient, getApiError } from './client';
import { Wallet } from '@/types/wallet';

export const walletApi = {
  async getWallet(): Promise<Wallet> {
    try {
      const response = await apiClient.get<Partial<Wallet>>('/wallet/');
      return normalizeWallet(response.data);
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to fetch wallet.'));
    }
  },

  async getBalance(): Promise<number> {
    // Backend has no dedicated balance endpoint; derive it from the wallet.
    const wallet = await this.getWallet();
    return wallet.balance;
  }
};

function normalizeWallet(data: Partial<Wallet>): Wallet {
  return {
    id: data.id || 'wallet',
    userId: data.userId || data.user_id || 'user',
    balance: Number(data.balance || 0),
    currency: data.currency || 'XAF',
    phone: data.phone || '',
    network: data.network || 'UNKNOWN',
    updatedAt: data.updatedAt || data.updated_at || ''
  } as Wallet;
}
