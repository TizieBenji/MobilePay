import { createContext, PropsWithChildren, useContext, useEffect, useMemo, useState } from 'react';
import { authApi, LoginRequest, RegisterRequest } from '@/services/api/auth';
import { clearSession, getStoredUser, getToken, saveToken, saveUser } from '@/storage/tokenStorage';
import { User } from '@/types/user';

type AuthContextValue = {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signIn: (payload: LoginRequest) => Promise<void>;
  register: (payload: RegisterRequest) => Promise<void>;
  signOut: () => Promise<void>;
  setUser: (user: User) => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUserState] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function restore() {
      const [storedToken, storedUser] = await Promise.all([getToken(), getStoredUser()]);
      setToken(storedToken);
      setUserState(storedUser);
      setIsLoading(false);
    }
    restore();
  }, []);

  async function signIn(payload: LoginRequest) {
    const response = await authApi.login(payload);
    setToken(response.token);
    setUserState(response.user);
    await Promise.all([saveToken(response.token), saveUser(response.user)]);
  }

  async function register(payload: RegisterRequest) {
    const response = await authApi.register(payload);
    setToken(response.token);
    setUserState(response.user);
    await Promise.all([saveToken(response.token), saveUser(response.user)]);
  }

  async function signOut() {
    try {
      await authApi.logout();
    } finally {
      setToken(null);
      setUserState(null);
      await clearSession();
    }
  }

  function setUser(userValue: User) {
    setUserState(userValue);
    saveUser(userValue);
  }

  const value = useMemo<AuthContextValue>(() => ({
    user,
    token,
    isLoading,
    isAuthenticated: Boolean(token),
    signIn,
    register,
    signOut,
    setUser
  }), [user, token, isLoading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return context;
}
