import { forwardRef } from 'react';
import { ActivityIndicator, Pressable, PressableProps, StyleSheet, ViewStyle } from 'react-native';
import { AppText } from './AppText';
import { colors } from '@/constants/colors';

type Variant = 'primary' | 'secondary' | 'outline' | 'outlineDark' | 'ghost' | 'danger';

type Props = PressableProps & {
  title: string;
  variant?: Variant;
  loading?: boolean;
};

export const Button = forwardRef<any, Props>(({ title, variant = 'primary', loading, disabled, style, ...props }, ref) => {
  const isDisabled = disabled || loading;
  return (
    <Pressable
      ref={ref}
      disabled={isDisabled}
      style={({ pressed }) => [
        styles.base,
        styles[variant],
        pressed && !isDisabled ? styles.pressed : null,
        isDisabled ? styles.disabled : null,
        style as ViewStyle
      ]}
      {...props}
    >
      {loading ? <ActivityIndicator color={variant === 'outline' || variant === 'ghost' ? colors.primary : colors.white} /> : (
        <AppText weight="bold" color={getTextColor(variant)}>{title}</AppText>
      )}
    </Pressable>
  );
});

function getTextColor(variant: Variant) {
  if (variant === 'outline' || variant === 'ghost' || variant === 'outlineDark') return colors.primary;
  if (variant === 'secondary') return colors.background;
  return colors.white;
}

const styles = StyleSheet.create({
  base: {
    minHeight: 52,
    paddingHorizontal: 18,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1
  },
  primary: { backgroundColor: colors.primary },
  secondary: { backgroundColor: colors.secondary },
  outline: { borderWidth: 1, borderColor: 'rgba(255,255,255,0.55)', backgroundColor: 'transparent' },
  outlineDark: { borderWidth: 1, borderColor: colors.primary, backgroundColor: 'transparent' },
  ghost: { backgroundColor: 'transparent' },
  danger: { backgroundColor: colors.danger },
  pressed: { opacity: 0.82 },
  disabled: { opacity: 0.55 }
});
