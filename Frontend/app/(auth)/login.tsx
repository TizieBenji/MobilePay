import { Link, router } from 'expo-router';
import { useState } from 'react';
import { Alert, KeyboardAvoidingView, Platform, StyleSheet, View } from 'react-native';
import { AppText } from '@/components/ui/AppText';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Screen } from '@/components/layout/Screen';
import { useAuth } from '@/context/AuthContext';
import { colors } from '@/constants/colors';
import { validateEmail } from '@/utils/validators';

export default function LoginScreen() {
  const { signIn } = useAuth();
  const [emailOrPhone, setEmailOrPhone] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleLogin() {
    if (!emailOrPhone.trim() || !password.trim()) {
      Alert.alert('Missing information', 'Please enter your email/phone and password.');
      return;
    }

    if (emailOrPhone.includes('@') && !validateEmail(emailOrPhone)) {
      Alert.alert('Invalid email', 'Please enter a valid email address.');
      return;
    }

    setIsSubmitting(true);
    try {
      await signIn({ emailOrPhone, password });
      router.replace('/(tabs)/dashboard');
    } catch (error) {
      Alert.alert('Login failed', error instanceof Error ? error.message : 'Unable to login.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Screen scrollable>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.container}>
        <View>
          <AppText size={32} weight="bold">Welcome back</AppText>
          <AppText color={colors.muted} style={styles.subtitle}>
            Login to access your wallet and continue your transfers.
          </AppText>
        </View>

        <View style={styles.form}>
          <Input label="Email or phone" value={emailOrPhone} onChangeText={setEmailOrPhone} keyboardType="email-address" placeholder="example@mail.com" autoCapitalize="none" />
          <Input label="Password" value={password} onChangeText={setPassword} placeholder="Your password" secureTextEntry />
          <Button title="Login" loading={isSubmitting} onPress={handleLogin} />
        </View>

        <View style={styles.footer}>
          <Link href="/(auth)/forgot-password">
            <AppText color={colors.primary} weight="semibold">Forgot password?</AppText>
          </Link>
          <View style={styles.row}>
            <AppText color={colors.muted}>No account? </AppText>
            <Link href="/(auth)/register">
              <AppText color={colors.primary} weight="semibold">Create one</AppText>
            </Link>
          </View>
        </View>
      </KeyboardAvoidingView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingTop: 36, gap: 32 },
  subtitle: { marginTop: 8, lineHeight: 22 },
  form: { gap: 16 },
  footer: { alignItems: 'center', gap: 16, marginTop: 20 },
  row: { flexDirection: 'row', alignItems: 'center' }
});
