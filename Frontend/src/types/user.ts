export type Network = 'MTN' | 'ORANGE';

export type User = {
  id: string;
  fullname: string;
  email: string;
  phone: string;
  network: Network | null;
  kycStatus?: 'PENDING' | 'APPROVED' | 'REJECTED' | string;
  createdAt?: string;
};
