import { Link } from 'expo-router';
import { useEffect, useState } from 'react';
import { RefreshControl, StyleSheet, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { AppText } from '@/components/ui/AppText';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { NetworkPill } from '@/components/domain/NetworkPill';
import { TransactionItem } from '@/components/domain/TransactionItem';
import { Screen } from '@/components/layout/Screen';
import { useAuth } from '@/context/AuthContext';
import { walletApi } from '@/services/api/wallet';
import { transactionApi } from '@/services/api/transactions';
import { Wallet } from '@/types/wallet';
import { Transaction } from '@/types/transaction';
import { colors } from '@/constants/colors';
import { formatCurrency } from '@/utils/currency';
import { mockTransactions, mockWallet } from '@/utils/mockData';

export default function DashboardScreen() {
  const { user } = useAuth();
  const [wallet, setWallet] = useState<Wallet>(mockWallet);
  const [transactions, setTransactions] = useState<Transaction[]>(mockTransactions.slice(0, 3));
  const [refreshing, setRefreshing] = useState(false);

  async function loadData() {
    try {
      const [walletResponse, transactionResponse] = await Promise.all([
        walletApi.getWallet(),
        transactionApi.getTransactions()
      ]);
      setWallet(walletResponse);
      setTransactions(transactionResponse.slice(0, 3));
    } catch {
      setWallet(mockWallet);
      setTransactions(mockTransactions.slice(0, 3));
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function onRefresh() {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  }

  return (
    <Screen
      scrollable
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.topBar}>
        <View>
          <AppText color={colors.muted}>Good day</AppText>
          <AppText size={24} weight="bold">{user?.fullname || 'MobilePay User'}</AppText>
        </View>
        <NetworkPill network={user?.network || wallet.network} />
      </View>

      <Card style={styles.balanceCard}>
        <View style={styles.balanceTop}>
          <AppText color={colors.mutedLight}>Available balance</AppText>
          <Ionicons name="shield-checkmark-outline" size={22} color={colors.success} />
        </View>
        <AppText size={36} weight="bold" color={colors.white}>{formatCurrency(wallet.balance, wallet.currency)}</AppText>
        <AppText color={colors.mutedLight}>Wallet number: {user?.phone || wallet.phone}</AppText>
      </Card>

      <View style={styles.quickActions}>
        <Link href="/topup" asChild>
          <Button title="Top up" />
        </Link>
        <Link href="/withdraw" asChild>
          <Button title="Withdraw" variant="secondary" />
        </Link>
      </View>
      <View style={styles.quickActionsSecondary}>
        <Link href="/(tabs)/transfer" asChild>
          <Button title="Send money" variant="outlineDark" />
        </Link>
        <Link href="/(onboarding)/kyc" asChild>
          <Button title="Complete KYC" variant="ghost" />
        </Link>
      </View>

      <View style={styles.sectionHeader}>
        <AppText size={20} weight="bold">Recent transactions</AppText>
        <Link href="/(tabs)/transactions">
          <AppText color={colors.primary} weight="semibold">View all</AppText>
        </Link>
      </View>

      <View style={styles.list}>
        {transactions.map((transaction) => <TransactionItem key={transaction.id} transaction={transaction} />)}
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  topBar: { paddingTop: 18, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 22 },
  balanceCard: { backgroundColor: colors.background, gap: 10, padding: 22 },
  balanceTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  quickActions: { flexDirection: 'row', gap: 12, marginTop: 20, marginBottom: 12 },
  quickActionsSecondary: { flexDirection: 'row', gap: 12, marginBottom: 20 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  list: { gap: 12, paddingBottom: 24 }
});
