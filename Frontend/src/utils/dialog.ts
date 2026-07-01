import { Alert, Platform } from 'react-native';

type DialogButton = {
  text: string;
  onPress?: () => void;
  style?: 'default' | 'cancel' | 'destructive';
};

// react-native-web's Alert.alert is a no-op (it never renders anything), so
// on web this falls back to window.alert/window.confirm. Use this instead of
// importing Alert directly anywhere a user-facing message needs to be seen.
export function showAlert(title: string, message?: string, buttons?: DialogButton[]) {
  if (Platform.OS !== 'web') {
    Alert.alert(title, message, buttons);
    return;
  }

  const text = [title, message].filter(Boolean).join('\n\n');

  if (!buttons || buttons.length <= 1) {
    window.alert(text);
    buttons?.[0]?.onPress?.();
    return;
  }

  const confirmButton = buttons.find((b) => b.style !== 'cancel') || buttons[buttons.length - 1];
  const cancelButton = buttons.find((b) => b.style === 'cancel');

  if (window.confirm(text)) {
    confirmButton.onPress?.();
  } else {
    cancelButton?.onPress?.();
  }
}
