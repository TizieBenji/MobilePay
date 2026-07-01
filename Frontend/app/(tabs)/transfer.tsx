import { useState } from 'react';
import { KeyboardAvoidingView, Platform, StyleSheet, View } from 'react-native';
import { showAlert } from '@/utils/dialog';
import { Ionicons } from '@expo/vector-icons';
import { AppText } from '@/components/ui/AppText';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Screen } from '@/components/layout/Screen';
import { NetworkPill } from '@/components/domain/NetworkPill';
import { useAuth } from '@/context/AuthContext';
import { transferApi } from '@/services/api/transfer';
import { colors } from '@/constants/colors';
import { detectNetwork, normalizePhone } from '@/utils/phone';
import { formatCurrency } from '@/utils/currency';

export default function TransferScreen() {
  const { user } = useAuth();
  const [receiver, setReceiver] = useState('');
  const [amount, setAmount] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const receiverNetwork = detectNetwork(receiver);
  const numericAmount = Number(amount.replace(/[^0-9.]/g, ''));

  async function handleTransfer() {
    if (!user?.phone) {
      showAlert('Missing sender', 'Your profile phone number is missing.');
      return;
    }

    if (!receiver.trim() || !amount.trim()) {
      showAlert('Missing information', 'Enter recipient number and amount.');
      return;
    }

    if (!receiverNetwork) {
      showAlert('Unsupported recipient', 'Recipient must be an MTN or Orange Cameroon number.');
      return;
    }

    if (!numericAmount || numericAmount <= 0) {
      showAlert('Invalid amount', 'Enter an amount greater than zero.');
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await transferApi.createTransfer({
        sender: normalizePhone(user.phone),
        receiver: normalizePhone(receiver),
        amount: numericAmount
      });
      showAlert('Transfer submitted', `Status: ${result.status}\nReference: ${result.referenceId}`);
      setReceiver('');
      setAmount('');
    } catch (error) {
      showAlert('Transfer failed', error instanceof Error ? error.message : 'Unable to complete transfer.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Screen scrollable>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.container}>
        <View style={styles.header}>
          <AppText size={28} weight="bold">Send money</AppText>
          <AppText color={colors.muted}>Cross-network transfer between MTN and Orange wallets.</AppText>
        </View>

        <Card style={styles.senderCard}>
          <View style={styles.iconCircle}>
            <Ionicons name="person-outline" size={22} color={colors.primary} />
          </View>
          <View style={{ flex: 1 }}>
            <AppText color={colors.muted}>Sender</AppText>
            <AppText weight="bold">{user?.phone || 'Not available'}</AppText>
          </View>
          <NetworkPill network={user?.network || null} />
        </Card>

        <View style={styles.form}>
          <Input label="Recipient number" value={receiver} onChangeText={setReceiver} keyboardType="phone-pad" placeholder="690123456" helperText={receiverNetwork ? `Recipient network: ${receiverNetwork}` : 'Example: 670123456 or 690123456'} />
          <Input label="Amount" value={amount} onChangeText={setAmount} keyboardType="numeric" placeholder="5000" helperText={numericAmount ? `You are sending ${formatCurrency(numericAmount)}` : 'Amount in XAF'} />
          <Button title="Transfer money" loading={isSubmitting} onPress={handleTransfer} />
        </View>

        <Card style={styles.infoCard}>
          <AppText weight="bold">Transfer workflow</AppText>
          <AppText color={colors.muted} style={styles.infoText}>
            The frontend sends sender, receiver and amount to Flask. The backend will detect networks, debit sender provider, update the system ledger and credit the receiver provider.
          </AppText>
        </Card>
      </KeyboardAvoidingView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: { paddingTop: 20, gap: 18 },
  header: { gap: 8 },
  senderCard: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  iconCircle: { width: 48, height: 48, borderRadius: 16, backgroundColor: colors.primarySoft, alignItems: 'center', justifyContent: 'center' },
  form: { gap: 14 },
  infoCard: { gap: 8, backgroundColor: colors.warningSoft },
  infoText: { lineHeight: 21 }
});
