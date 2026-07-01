import { useCallback, useState } from 'react';
import { useFocusEffect } from 'expo-router';
import { StyleSheet, View } from 'react-native';
import { AppText } from '@/components/ui/AppText';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Screen } from '@/components/layout/Screen';
import { colors } from '@/constants/colors';
import { kycApi } from '@/services/api/kyc';
import { KycRecord } from '@/types/kyc';
import { showAlert } from '@/utils/dialog';

export default function AdminKycScreen() {
  const [records, setRecords] = useState<KycRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [rejectingId, setRejectingId] = useState<number | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      setRecords(await kycApi.getPending());
    } catch (error) {
      showAlert('Failed to load', error instanceof Error ? error.message : 'Unable to load pending KYC records.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  async function handleApprove(record: KycRecord) {
    setBusyId(record.id);
    try {
      await kycApi.approve(record.id);
      setRecords((prev) => prev.filter((r) => r.id !== record.id));
    } catch (error) {
      showAlert('Approve failed', error instanceof Error ? error.message : 'Unable to approve KYC.');
    } finally {
      setBusyId(null);
    }
  }

  async function handleReject(record: KycRecord) {
    if (!rejectionReason.trim()) {
      showAlert('Reason required', 'Enter a rejection reason before rejecting.');
      return;
    }
    setBusyId(record.id);
    try {
      await kycApi.reject(record.id, rejectionReason.trim());
      setRecords((prev) => prev.filter((r) => r.id !== record.id));
      setRejectingId(null);
      setRejectionReason('');
    } catch (error) {
      showAlert('Reject failed', error instanceof Error ? error.message : 'Unable to reject KYC.');
    } finally {
      setBusyId(null);
    }
  }

  return (
    <Screen scrollable>
      <AppText size={26} weight="bold" style={styles.title}>KYC Review</AppText>

      {!isLoading && records.length === 0 ? (
        <Card><AppText color={colors.muted}>No pending KYC submissions.</AppText></Card>
      ) : null}

      {records.map((record) => (
        <Card key={record.id} style={styles.card}>
          <AppText weight="bold">User #{record.userId}</AppText>
          <AppText color={colors.muted}>ID: {record.nationalIdNumber} ({record.documentType})</AppText>
          {record.residentialAddress ? (
            <AppText color={colors.muted}>{record.residentialAddress}</AppText>
          ) : null}
          <AppText color={colors.muted}>Submitted: {record.createdAt ? new Date(record.createdAt).toLocaleString() : 'Unknown'}</AppText>

          {rejectingId === record.id ? (
            <View style={styles.rejectRow}>
              <Input
                placeholder="Rejection reason"
                value={rejectionReason}
                onChangeText={setRejectionReason}
              />
              <View style={styles.actions}>
                <Button
                  title="Cancel"
                  variant="ghost"
                  onPress={() => {
                    setRejectingId(null);
                    setRejectionReason('');
                  }}
                />
                <Button
                  title="Confirm reject"
                  variant="danger"
                  loading={busyId === record.id}
                  onPress={() => handleReject(record)}
                />
              </View>
            </View>
          ) : (
            <View style={styles.actions}>
              <Button
                title="Reject"
                variant="danger"
                disabled={busyId !== null}
                onPress={() => setRejectingId(record.id)}
              />
              <Button
                title="Approve"
                loading={busyId === record.id}
                disabled={busyId !== null && busyId !== record.id}
                onPress={() => handleApprove(record)}
              />
            </View>
          )}
        </Card>
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  title: { marginTop: 22, marginBottom: 16 },
  card: { gap: 10, marginBottom: 16 },
  actions: { flexDirection: 'row', gap: 10, marginTop: 6 },
  rejectRow: { gap: 10, marginTop: 6 }
});
