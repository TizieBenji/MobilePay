import { router, Link } from 'expo-router';
import { useState } from 'react';
import { Alert, KeyboardAvoidingView, Platform, StyleSheet, View } from 'react-native';
import { AppText } from '@/components/ui/AppText';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Screen } from '@/components/layout/Screen';
import { useAuth } from '@/context/AuthContext';
import { colors } from '@/constants/colors';
import { detectNetwork, normalizePhone } from '@/utils/phone';
import { validateEmail } from '@/utils/validators';

export default function RegisterScreen() {
  const { register } = useAuth();
  const [fullname, setFullname] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const network = detectNetwork(phone);

  async function handleRegister() {
    if (!fullname.trim() || !dateOfBirth.trim() || !phone.trim() || !email.trim() || !password.trim()) {
      Alert.alert('Missing information', 'Please fill all fields.');
      return;
    }

    if (!validateEmail(email)) {
      Alert.alert('Invalid email', 'Please enter a valid email address.');
      return;
    }

    if (!network) {
      Alert.alert('Unsupported number', 'Use a valid MTN or Orange Cameroon number.');
      return;
    }

    if (password.length < 6) {
      Alert.alert('Weak password', 'Password must contain at least 6 characters.');
      return;
    }

    setIsSubmitting(true);
    try {
      await register({
        fullname,
        dateOfBirth,
        phone: normalizePhone(phone),
        email,
        password,
        network
      });
      router.replace('/(onboarding)/kyc');
    } catch (error) {
      Alert.alert('Registration failed', error instanceof Error ? error.message : 'Unable to create account.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Screen scrollable>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.container}>
        <View>
          <AppText size={30} weight="bold">Create your account</AppText>
          <AppText color={colors.muted} style={styles.subtitle}>
            Your phone network will be detected automatically from your number.
          </AppText>
        </View>

        <View style={styles.form}>
          <Input label="Full name" value={fullname} onChangeText={setFullname} placeholder="Temate Durel" />
          <Input label="Date of birth" value={dateOfBirth} onChangeText={setDateOfBirth} placeholder="YYYY-MM-DD" />
          <Input label="Phone number" value={phone} onChangeText={setPhone} keyboardType="phone-pad" placeholder="670123456" helperText={network ? `Detected network: ${network}` : 'MTN: 67/65/68 | Orange: 69/655/656'} />
          <Input label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" placeholder="you@mail.com" autoCapitalize="none" />
          <Input label="Password" value={password} onChangeText={setPassword} placeholder="Minimum 6 characters" secureTextEntry />
          <Button title="Register and continue" loading={isSubmitting} onPress={handleRegister} />
        </View>

        <View style={styles.footer}>
          <AppText color={colors.muted}>Already registered? </AppText>
          <Link href="/(auth)/login">
            <AppText color={colors.primary} weight="semibold">Login</AppText>
          </Link>
        </View>
      </KeyboardAvoidingView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingTop: 28, gap: 28 },
  subtitle: { marginTop: 8, lineHeight: 22 },
  form: { gap: 14 },
  footer: { flexDirection: 'row', justifyContent: 'center', marginTop: 16 }
});
