// PawaPay collection (pay-in / top-up) and disbursement (pay-out / withdraw).

export type PaymentRequest = {
  phone: string;
  amount: number;
};

// PawaPay status as surfaced by the backend.
export type PawaStatus =
  | 'ACCEPTED'
  | 'PENDING'
  | 'COMPLETED'
  | 'FAILED'
  | 'DUPLICATE_IGNORED'
  | string;

export type PaymentResult = {
  success: boolean;
  message: string;
  // deposit_id for collections, payout_id for disbursements.
  id: string;
  pawaStatus: PawaStatus;
  // True once the wallet has actually been credited (collect) / debited (disburse).
  walletProcessed: boolean;
  correspondent?: string;
  amount?: number;
  currency?: string;
};
