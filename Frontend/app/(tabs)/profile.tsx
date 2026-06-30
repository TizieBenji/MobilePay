import { router } from 'expo-router';
import { useState } from 'react';
import { Alert, StyleSheet, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { AppText } from '@/components/ui/AppText';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { NetworkPill } from '@/components/domain/NetworkPill';
import { Screen } from '@/components/layout/Screen';
import { useAuth } from '@/context/AuthContext';
import { profileApi } from '@/services/api/profile';
import { colors } from '@/constants/colors';

export default function ProfileScreen() {
  const { user, setUser, signOut } = useAuth();
  const [fullname, setFullname] = useState(user?.fullname || '');
  const [email, setEmail] = useState(user?.email || '');
  const [isSaving, setIsSaving] = useState(false);

  async function handleSave() {
    setIsSaving(true);
    try {
      const updatedUser = await profileApi.updateProfile({ fullname, email });
      setUser(updatedUser);
      Alert.alert('Profile updated', 'Your profile has been saved.');
    } catch (error) {
      Alert.alert('Update failed', error instanceof Error ? error.message : 'Unable to update profile.');
    } finally {
      setIsSaving(false);
    }
  }

  async function handleLogout() {
    Alert.alert('Logout', 'Do you want to logout from MobilePay?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Logout',
        style: 'destructive',
        onPress: async () => {
          await signOut();
          router.replace('/(auth)/welcome');
        }
      }
    ]);
  }

  return (
    <Screen scrollable>
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Ionicons name="person" size={36} color={colors.white} />
        </View>
        <AppText size={26} weight="bold">{user?.fullname || 'MobilePay User'}</AppText>
        <NetworkPill network={user?.network || null} />
      </View>

      <Card style={styles.card}>
        <Input label="Full name" value={fullname} onChangeText={setFullname} placeholder="Your full name" />
        <Input label="Email" value={email} onChangeText={setEmail} placeholder="you@mail.com" keyboardType="email-address" autoCapitalize="none" />
        <Input label="Phone" value={user?.phone || ''} editable={false} helperText="Phone change should be controlled by backend verification." />
        <Button title="Save profile" loading={isSaving} onPress={handleSave} />
      </Card>

      <Card style={styles.card}>
        <View style={styles.rowBetween}>
          <View>
            <AppText weight="bold">KYC status</AppText>
            <AppText color={colors.muted}>{user?.kycStatus || 'PENDING'}</AppText>
          </View>
          <Button title="Update KYC" variant="secondary" onPress={() => router.push('/(onboarding)/kyc')} />
        </View>
      </Card>

      <Button title="Logout" variant="danger" onPress={handleLogout} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: { alignItems: 'center', paddingTop: 22, marginBottom: 22, gap: 10 },
  avatar: { width: 84, height: 84, borderRadius: 42, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center' },
  card: { gap: 14, marginBottom: 16 },
  rowBetween: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12 }
});
