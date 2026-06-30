export type TransactionStatus = 'PENDING' | 'SUCCESS' | 'FAILED' | string;

export type Transaction = {
  id: string;
  referenceId: string;
  senderPhone: string;
  receiverPhone: string;
  senderNetwork: string;
  receiverNetwork: string;
  amount: number;
  status: TransactionStatus;
  createdAt: string;
};
