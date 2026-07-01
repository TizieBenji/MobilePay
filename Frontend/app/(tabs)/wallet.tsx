import { useCallback, useState } from 'react';
import { RefreshControl, StyleSheet, View } from 'react-native';
import { useFocusEffect } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { AppText } from '@/components/ui/AppText';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Screen } from '@/components/layout/Screen';
import { walletApi } from '@/services/api/wallet';
import { Wallet } from '@/types/wallet';
import { colors } from '@/constants/colors';
import { formatCurrency } from '@/utils/currency';
import { mockWallet } from '@/utils/mockData';
import { router } from 'expo-router';
import { showAlert } from '@/utils/dialog';

export default function WalletScreen() {
  const [wallet, setWallet] = useState<Wallet>(mockWallet);
  const [refreshing, setRefreshing] = useState(false);

  async function loadWallet() {
    try {
      setWallet(await walletApi.getWallet());
    } catch (error) {
      showAlert('Unable to load wallet', error instanceof Error ? error.message : 'Could not reach the server.');
    }
  }

  // Reload whenever the tab regains focus (e.g. after a top-up or withdrawal)
  // so the balance reflects the latest wallet state.
  useFocusEffect(
    useCallback(() => {
      loadWallet();
    }, [])
  );

  async function onRefresh() {
    setRefreshing(true);
    await loadWallet();
    setRefreshing(false);
  }

  return (
    <Screen scrollable refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <View style={styles.header}>
        <AppText size={28} weight="bold">My wallet</AppText>
        <AppText color={colors.muted}>Monitor your balance and wallet status.</AppText>
      </View>

      <Card style={styles.cardDark}>
        <View style={styles.rowBetween}>
          <AppText color={colors.mutedLight}>Current balance</AppText>
          <Ionicons name="wallet-outline" size={24} color={colors.white} />
        </View>
        <AppText size={38} weight="bold" color={colors.white}>{formatCurrency(wallet.balance, wallet.currency)}</AppText>
        <AppText color={colors.mutedLight}>Last update: {wallet.updatedAt || 'Waiting for backend'}</AppText>
      </Card>

      <View style={styles.statsGrid}>
        <Card style={styles.statCard}>
          <Ionicons name="call-outline" size={22} color={colors.primary} />
          <AppText color={colors.muted}>Phone</AppText>
          <AppText weight="bold">{wallet.phone}</AppText>
        </Card>
        <Card style={styles.statCard}>
          <Ionicons name="cellular-outline" size={22} color={colors.secondary} />
          <AppText color={colors.muted}>Network</AppText>
          <AppText weight="bold">{wallet.network}</AppText>
        </Card>
      </View>

      <View style={styles.actionRow}>
        <Button title="Top up" onPress={() => router.push('/topup')} />
        <Button title="Withdraw" variant="secondary" onPress={() => router.push('/withdraw')} />
      </View>
      <Button title="Send money" variant="outlineDark" onPress={() => router.push('/(tabs)/transfer')} />
      <Button title="View transaction history" variant="ghost" onPress={() => router.push('/(tabs)/transactions')} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: { paddingTop: 20, marginBottom: 22, gap: 8 },
  cardDark: { backgroundColor: colors.background, gap: 12, padding: 22, marginBottom: 18 },
  rowBetween: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  statsGrid: { flexDirection: 'row', gap: 12, marginBottom: 18 },
  statCard: { flex: 1, gap: 8 },
  actionRow: { flexDirection: 'row', gap: 12, marginBottom: 12 }
});
