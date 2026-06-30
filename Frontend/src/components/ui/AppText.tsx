import { PropsWithChildren } from 'react';
import { StyleProp, Text, TextProps, TextStyle } from 'react-native';
import { colors } from '@/constants/colors';

type Weight = 'regular' | 'medium' | 'semibold' | 'bold';

type Props = PropsWithChildren<TextProps & {
  size?: number;
  color?: string;
  weight?: Weight;
  style?: StyleProp<TextStyle>;
}>;

const weightMap: Record<Weight, TextStyle['fontWeight']> = {
  regular: '400',
  medium: '500',
  semibold: '600',
  bold: '700'
};

export function AppText({ children, size = 15, color = colors.text, weight = 'regular', style, ...props }: Props) {
  return (
    <Text
      {...props}
      style={[{ fontSize: size, color, fontWeight: weightMap[weight] }, style]}
    >
      {children}
    </Text>
  );
}
