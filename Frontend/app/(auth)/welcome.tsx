import { Link } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { StyleSheet, View } from 'react-native';
import { AppText } from '@/components/ui/AppText';
import { Button } from '@/components/ui/Button';
import { colors } from '@/constants/colors';

export default function WelcomeScreen() {
  return (
    <LinearGradient colors={[colors.background, colors.primaryDark]} style={styles.container}>
      <View style={styles.logoCircle}>
        <AppText weight="bold" size={28} color={colors.white}>MP</AppText>
      </View>

      <View style={styles.content}>
        <AppText size={36} weight="bold" color={colors.white} style={styles.title}>
          MobilePay
        </AppText>
        <AppText size={16} color={colors.mutedLight} style={styles.subtitle}>
          Send money between MTN Mobile Money and Orange Money with a clean, secure and fast wallet experience.
        </AppText>
      </View>

      <View style={styles.actions}>
        <Link href="/(auth)/register" asChild>
          <Button title="Create an account" />
        </Link>
        <Link href="/(auth)/login" asChild>
          <Button title="I already have an account" variant="outline" />
        </Link>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: 'space-between' },
  logoCircle: {
    marginTop: 64,
    width: 76,
    height: 76,
    borderRadius: 38,
    backgroundColor: 'rgba(255,255,255,0.12)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
    justifyContent: 'center'
  },
  content: { marginBottom: 56 },
  title: { marginBottom: 12 },
  subtitle: { lineHeight: 24 },
  actions: { gap: 14, paddingBottom: 24 }
});
