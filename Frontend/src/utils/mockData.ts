import { Transaction } from '@/types/transaction';
import { Wallet } from '@/types/wallet';

export const mockWallet: Wallet = {
  id: 'wallet-demo',
  userId: 'user-demo',
  balance: 125000,
  currency: 'XAF',
  phone: '670123456',
  network: 'MTN',
  updatedAt: 'Waiting for backend'
};

export const mockTransactions: Transaction[] = [
  {
    id: '1',
    referenceId: 'MP-10001',
    senderPhone: '670123456',
    receiverPhone: '690123456',
    senderNetwork: 'MTN',
    receiverNetwork: 'ORANGE',
    amount: 5000,
    status: 'SUCCESS',
    createdAt: '2026-06-25 10:12'
  },
  {
    id: '2',
    referenceId: 'MP-10002',
    senderPhone: '670123456',
    receiverPhone: '651222333',
    senderNetwork: 'MTN',
    receiverNetwork: 'MTN',
    amount: 12000,
    status: 'PENDING',
    createdAt: '2026-06-25 12:20'
  },
  {
    id: '3',
    referenceId: 'MP-10003',
    senderPhone: '690333222',
    receiverPhone: '670123456',
    senderNetwork: 'ORANGE',
    receiverNetwork: 'MTN',
    amount: 7500,
    status: 'FAILED',
    createdAt: '2026-06-24 18:42'
  },
  {
    id: '4',
    referenceId: 'MP-10004',
    senderPhone: '670123456',
    receiverPhone: '655444555',
    senderNetwork: 'MTN',
    receiverNetwork: 'ORANGE',
    amount: 3000,
    status: 'SUCCESS',
    createdAt: '2026-06-24 09:05'
  }
];
