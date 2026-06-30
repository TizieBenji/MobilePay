import { StyleSheet, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { AppText } from '@/components/ui/AppText';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Transaction } from '@/types/transaction';
import { colors } from '@/constants/colors';
import { formatCurrency } from '@/utils/currency';

export function TransactionItem({ transaction }: { transaction: Transaction }) {
  const tone = transaction.status === 'SUCCESS' ? 'success' : transaction.status === 'FAILED' ? 'danger' : 'warning';

  return (
    <Card style={styles.container}>
      <View style={styles.iconBox}>
        <Ionicons name="swap-horizontal-outline" size={22} color={colors.primary} />
      </View>
      <View style={styles.content}>
        <View style={styles.topRow}>
          <AppText weight="bold">{transaction.receiverPhone}</AppText>
          <AppText weight="bold">{formatCurrency(transaction.amount)}</AppText>
        </View>
        <View style={styles.bottomRow}>
          <AppText size={12} color={colors.muted}>{transaction.createdAt}</AppText>
          <Badge label={transaction.status} tone={tone} />
        </View>
        <AppText size={12} color={colors.muted}>Network: {transaction.receiverNetwork} · Ref: {transaction.referenceId}</AppText>
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  container: { flexDirection: 'row', gap: 12, alignItems: 'center' },
  iconBox: { width: 44, height: 44, borderRadius: 14, backgroundColor: colors.primarySoft, alignItems: 'center', justifyContent: 'center' },
  content: { flex: 1, gap: 6 },
  topRow: { flexDirection: 'row', justifyContent: 'space-between', gap: 12 },
  bottomRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 12 }
});
