import { router } from 'expo-router';
import { useState } from 'react';
import { Alert, StyleSheet, View } from 'react-native';
import { AppText } from '@/components/ui/AppText';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Screen } from '@/components/layout/Screen';
import { authApi } from '@/services/api/auth';
import { colors } from '@/constants/colors';

export default function ForgotPasswordScreen() {
  const [emailOrPhone, setEmailOrPhone] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit() {
    if (!emailOrPhone.trim()) {
      Alert.alert('Missing information', 'Enter your email or phone number.');
      return;
    }

    setIsSubmitting(true);
    try {
      await authApi.forgotPassword(emailOrPhone);
      Alert.alert('Request sent', 'If this account exists, password reset instructions will be sent.', [
        { text: 'OK', onPress: () => router.replace('/(auth)/login') }
      ]);
    } catch (error) {
      Alert.alert('Error', error instanceof Error ? error.message : 'Unable to submit request.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Screen>
      <View style={styles.container}>
        <View>
          <AppText size={30} weight="bold">Reset password</AppText>
          <AppText color={colors.muted} style={styles.subtitle}>
            Enter your account email or phone number. Your backend can later send SMS or email instructions.
          </AppText>
        </View>
        <Input label="Email or phone" value={emailOrPhone} onChangeText={setEmailOrPhone} placeholder="example@mail.com" />
        <Button title="Send reset request" loading={isSubmitting} onPress={handleSubmit} />
        <Button title="Back to login" variant="ghost" onPress={() => router.back()} />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingTop: 40, gap: 18 },
  subtitle: { marginTop: 8, lineHeight: 22 }
});
