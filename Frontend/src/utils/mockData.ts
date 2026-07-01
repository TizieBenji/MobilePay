import { Transaction } from '@/types/transaction';
import { Wallet } from '@/types/wallet';

// Placeholder shown only until the first real fetch resolves. Values must
// stay at zero/empty so the UI never displays fabricated numbers.
export const emptyWallet: Wallet = {
  id: '',
  userId: '',
  balance: 0,
  currency: 'XAF',
  phone: '',
  network: '',
  updatedAt: ''
};

export const emptyTransactions: Transaction[] = [];
