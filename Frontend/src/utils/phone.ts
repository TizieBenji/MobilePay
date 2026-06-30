import { Network } from '@/types/user';

export function normalizePhone(phone: string) {
  return phone.replace(/\s+/g, '').replace(/^\+237/, '').replace(/^237/, '');
}

export function detectNetwork(phone: string): Network | null {
  const normalized = normalizePhone(phone);

  if (/^(670|671|672|673|674|675|676|677|678|679|650|651|652|653|654|680|681|682|683|684)\d{6}$/.test(normalized)) {
    return 'MTN';
  }

  if (/^(690|691|692|693|694|695|696|697|698|699|655|656|657|658|659)\d{6}$/.test(normalized)) {
    return 'ORANGE';
  }

  return null;
}
