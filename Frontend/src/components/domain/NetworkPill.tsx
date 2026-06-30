import { StyleSheet, View } from 'react-native';
import { AppText } from '@/components/ui/AppText';
import { colors } from '@/constants/colors';
import { Network } from '@/types/user';

export function NetworkPill({ network }: { network?: Network | string | null }) {
  const label = network || 'UNKNOWN';
  const isMtn = label === 'MTN';
  const isOrange = label === 'ORANGE';

  return (
    <View style={[styles.pill, isMtn ? styles.mtn : isOrange ? styles.orange : styles.neutral]}>
      <AppText size={12} weight="bold" color={isMtn ? colors.background : isOrange ? colors.white : colors.muted}>{label}</AppText>
    </View>
  );
}

const styles = StyleSheet.create({
  pill: { paddingHorizontal: 12, paddingVertical: 7, borderRadius: 999 },
  mtn: { backgroundColor: colors.secondary },
  orange: { backgroundColor: colors.orange },
  neutral: { backgroundColor: colors.surface }
});
