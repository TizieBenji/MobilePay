import { apiClient, getApiError } from './client';
import { Transaction } from '@/types/transaction';

export const transactionApi = {
  async getTransactions(): Promise<Transaction[]> {
    try {
      const response = await apiClient.get<any>('/transactions/');
      const rows = Array.isArray(response.data) ? response.data : response.data?.data || response.data?.transactions || [];
      return rows.map(normalizeTransaction);
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to fetch transactions.'));
    }
  }
};

function normalizeTransaction(row: any): Transaction {
  return {
    id: String(row.id || row.reference_id || Date.now()),
    referenceId: row.reference_id || row.referenceId || '',
    senderPhone: row.sender_phone || row.senderPhone || row.sender || '',
    receiverPhone: row.receiver_phone || row.receiverPhone || row.receiver || '',
    senderNetwork: row.sender_network || row.senderNetwork || '',
    receiverNetwork: row.receiver_network || row.receiverNetwork || row.network || '',
    amount: Number(row.amount || 0),
    status: row.status || 'PENDING',
    createdAt: row.created_at || row.createdAt || ''
  };
}
