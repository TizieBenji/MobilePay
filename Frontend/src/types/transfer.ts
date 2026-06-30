export type TransferRequest = {
  sender: string;
  receiver: string;
  amount: number;
};

export type TransferResponse = {
  id: string;
  referenceId: string;
  status: string;
};
