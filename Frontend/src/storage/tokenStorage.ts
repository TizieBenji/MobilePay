import AsyncStorage from '@react-native-async-storage/async-storage';
import { User } from '@/types/user';

const TOKEN_KEY = 'mobilepay.accessToken';
const USER_KEY = 'mobilepay.user';

export async function saveToken(token: string) {
  await AsyncStorage.setItem(TOKEN_KEY, token);
}

export async function getToken() {
  return AsyncStorage.getItem(TOKEN_KEY);
}

export async function removeToken() {
  await AsyncStorage.removeItem(TOKEN_KEY);
}

export async function saveUser(user: User) {
  await AsyncStorage.setItem(USER_KEY, JSON.stringify(user));
}

export async function getStoredUser(): Promise<User | null> {
  const value = await AsyncStorage.getItem(USER_KEY);
  return value ? JSON.parse(value) as User : null;
}

export async function removeStoredUser() {
  await AsyncStorage.removeItem(USER_KEY);
}

export async function clearSession() {
  await Promise.all([removeToken(), removeStoredUser()]);
}
