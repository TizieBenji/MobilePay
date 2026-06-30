import { StyleSheet, View } from 'react-native';
import { AppText } from './AppText';
import { colors } from '@/constants/colors';

export function Badge({ label, tone = 'neutral' }: { label: string; tone?: 'success' | 'warning' | 'danger' | 'neutral' }) {
  return (
    <View style={[styles.badge, styles[tone]]}>
      <AppText size={12} weight="bold" color={getColor(tone)}>{label}</AppText>
    </View>
  );
}

function getColor(tone: 'success' | 'warning' | 'danger' | 'neutral') {
  if (tone === 'success') return colors.success;
  if (tone === 'warning') return colors.warning;
  if (tone === 'danger') return colors.danger;
  return colors.muted;
}

const styles = StyleSheet.create({
  badge: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 999 },
  success: { backgroundColor: colors.successSoft },
  warning: { backgroundColor: colors.warningSoft },
  danger: { backgroundColor: colors.dangerSoft },
  neutral: { backgroundColor: colors.surface }
});
