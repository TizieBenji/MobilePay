import { TextInput, TextInputProps, StyleSheet, View } from 'react-native';
import { AppText } from './AppText';
import { colors } from '@/constants/colors';

type Props = TextInputProps & {
  label: string;
  helperText?: string;
  error?: string;
};

export function Input({ label, helperText, error, style, ...props }: Props) {
  return (
    <View style={styles.container}>
      <AppText weight="semibold" style={styles.label}>{label}</AppText>
      <TextInput
        placeholderTextColor={colors.placeholder}
        style={[styles.input, props.multiline ? styles.multiline : null, error ? styles.errorBorder : null, style]}
        {...props}
      />
      {error ? <AppText size={12} color={colors.danger}>{error}</AppText> : null}
      {helperText && !error ? <AppText size={12} color={colors.muted}>{helperText}</AppText> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { gap: 7, marginBottom: 6 },
  label: { marginLeft: 2 },
  input: {
    minHeight: 52,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.white,
    paddingHorizontal: 16,
    color: colors.text,
    fontSize: 15
  },
  multiline: { minHeight: 92, textAlignVertical: 'top', paddingTop: 14 },
  errorBorder: { borderColor: colors.danger }
});
