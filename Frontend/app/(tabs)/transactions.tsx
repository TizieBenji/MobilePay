import { useEffect, useMemo, useState } from 'react';
import { RefreshControl, StyleSheet, View } from 'react-native';
import { AppText } from '@/components/ui/AppText';
import { Input } from '@/components/ui/Input';
import { Screen } from '@/components/layout/Screen';
import { TransactionItem } from '@/components/domain/TransactionItem';
import { transactionApi } from '@/services/api/transactions';
import { Transaction } from '@/types/transaction';
import { colors } from '@/constants/colors';
import { mockTransactions } from '@/utils/mockData';
import { showAlert } from '@/utils/dialog';

export default function TransactionsScreen() {
  const [transactions, setTransactions] = useState<Transaction[]>(mockTransactions);
  const [query, setQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  async function loadTransactions() {
    try {
      setTransactions(await transactionApi.getTransactions());
    } catch (error) {
      showAlert('Unable to load transactions', error instanceof Error ? error.message : 'Could not reach the server.');
    }
  }

  useEffect(() => {
    loadTransactions();
  }, []);

  async function onRefresh() {
    setRefreshing(true);
    await loadTransactions();
    setRefreshing(false);
  }

  const filtered = useMemo(() => {
    const normalized = query.toLowerCase().trim();
    if (!normalized) return transactions;
    return transactions.filter((transaction) =>
      transaction.receiverPhone.toLowerCase().includes(normalized) ||
      transaction.senderPhone.toLowerCase().includes(normalized) ||
      transaction.status.toLowerCase().includes(normalized) ||
      transaction.referenceId.toLowerCase().includes(normalized)
    );
  }, [transactions, query]);

  return (
    <Screen scrollable refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <View style={styles.header}>
        <AppText size={28} weight="bold">Transactions</AppText>
        <AppText color={colors.muted}>Search and review money movements.</AppText>
      </View>

      <Input label="Search" value={query} onChangeText={setQuery} placeholder="Phone, status, reference" />

      <View style={styles.list}>
        {filtered.map((transaction) => <TransactionItem key={transaction.id} transaction={transaction} />)}
        {filtered.length === 0 && (
          <View style={styles.emptyState}>
            <AppText weight="bold">No transaction found</AppText>
            <AppText color={colors.muted}>Try another search keyword.</AppText>
          </View>
        )}
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: { paddingTop: 20, marginBottom: 18, gap: 8 },
  list: { gap: 12, paddingBottom: 28 },
  emptyState: { alignItems: 'center', padding: 30, gap: 8 }
});
