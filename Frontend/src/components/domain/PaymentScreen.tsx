import { useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, StyleSheet, View } from 'react-native';
import { showAlert } from '@/utils/dialog';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { AppText } from '@/components/ui/AppText';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Screen } from '@/components/layout/Screen';
import { NetworkPill } from '@/components/domain/NetworkPill';
import { colors } from '@/constants/colors';
import { detectNetwork } from '@/utils/phone';
import { formatCurrency } from '@/utils/currency';
import { PaymentRequest, PaymentResult } from '@/types/payment';

type Props = {
  title: string;
  subtitle: string;
  phoneLabel: string;
  phoneHelper: string;
  actionLabel: string;
  note: string;
  // The PawaPay call (collect or disburse).
  onSubmit: (payload: PaymentRequest) => Promise<PaymentResult>;
  // Called after a terminal result so the caller can refresh the wallet balance.
  onDone?: () => void;
};

export function PaymentScreen({ title, subtitle, phoneLabel, phoneHelper, actionLabel, note, onSubmit, onDone }: Props) {
  const [phone, setPhone] = useState('');
  const [amount, setAmount] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const network = detectNetwork(phone);
  const numericAmount = Number(amount.replace(/[^0-9.]/g, ''));

  async function handleSubmit() {
    if (!phone.trim() || !amount.trim()) {
      showAlert('Missing information', 'Enter a phone number and an amount.');
      return;
    }
    if (!network) {
      showAlert('Unsupported number', 'Use a valid MTN or Orange Cameroon number.');
      return;
    }
    if (!numericAmount || numericAmount <= 0) {
      showAlert('Invalid amount', 'Enter an amount greater than zero.');
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await onSubmit({ phone, amount: numericAmount });
      const status = String(result.pawaStatus).toUpperCase();

      if (status === 'COMPLETED' || result.walletProcessed) {
        showAlert('Success', result.message || 'Payment completed.');
        onDone?.();
        router.back();
      } else if (status === 'FAILED') {
        showAlert('Payment failed', result.message || 'The mobile-money operator rejected the payment.');
      } else {
        // ACCEPTED / PENDING / TIMEOUT — still processing.
        showAlert(
          'Processing',
          result.message || 'Payment is still processing. It will appear in your history once confirmed.'
        );
        onDone?.();
        router.back();
      }
    } catch (error) {
      showAlert(title, error instanceof Error ? error.message : 'Something went wrong.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Screen scrollable>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.container}>
        <View style={styles.headerRow}>
          <Pressable onPress={() => router.back()} hitSlop={12} style={styles.back}>
            <Ionicons name="arrow-back" size={24} color={colors.text} />
          </Pressable>
          <AppText size={26} weight="bold">{title}</AppText>
        </View>
        <AppText color={colors.muted}>{subtitle}</AppText>

        <View style={styles.form}>
          <Input
            label={phoneLabel}
            value={phone}
            onChangeText={setPhone}
            keyboardType="phone-pad"
            placeholder="690123456"
            helperText={phoneHelper}
          />
          {network ? (
            <View style={styles.networkRow}>
              <AppText color={colors.muted}>Detected network</AppText>
              <NetworkPill network={network} />
            </View>
          ) : null}
          <Input
            label="Amount (XAF)"
            value={amount}
            onChangeText={setAmount}
            keyboardType="numeric"
            placeholder="5000"
            helperText={numericAmount ? formatCurrency(numericAmount) : 'Minimum 100 XAF'}
          />
          <Button title={actionLabel} loading={isSubmitting} onPress={handleSubmit} />
        </View>

        <Card style={styles.infoCard}>
          <AppText weight="bold">Routed through PawaPay</AppText>
          <AppText color={colors.muted} style={styles.infoText}>{note}</AppText>
        </Card>
      </KeyboardAvoidingView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: { paddingTop: 12, gap: 14 },
  headerRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  back: { padding: 4 },
  form: { gap: 14, marginTop: 8 },
  networkRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  infoCard: { gap: 8, backgroundColor: colors.primarySoft, marginTop: 4 },
  infoText: { lineHeight: 21 }
});
