import { User } from './user';

export type AuthResponse = {
  token: string;
  refreshToken: string | null;
  user: User;
};
