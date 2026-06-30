import * as ImagePicker from 'expo-image-picker';
import { router } from 'expo-router';
import { useState } from 'react';
import { Alert, Image, Pressable, StyleSheet, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { AppText } from '@/components/ui/AppText';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Screen } from '@/components/layout/Screen';
import { kycApi } from '@/services/api/kyc';
import { colors } from '@/constants/colors';
import { ImageAsset } from '@/types/kyc';

export default function KycScreen() {
  const [nationalId, setNationalId] = useState('');
  const [address, setAddress] = useState('');
  const [idFront, setIdFront] = useState<ImageAsset | null>(null);
  const [idBack, setIdBack] = useState<ImageAsset | null>(null);
  const [selfie, setSelfie] = useState<ImageAsset | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function pickImage(type: 'gallery' | 'camera', setter: (asset: ImageAsset) => void) {
    const permission = type === 'camera'
      ? await ImagePicker.requestCameraPermissionsAsync()
      : await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!permission.granted) {
      Alert.alert('Permission required', 'Please allow access to continue KYC verification.');
      return;
    }

    const result = type === 'camera'
      ? await ImagePicker.launchCameraAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images, allowsEditing: true, quality: 0.8 })
      : await ImagePicker.launchImageLibraryAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images, allowsEditing: true, quality: 0.8 });

    if (!result.canceled && result.assets[0]) {
      const asset = result.assets[0];
      setter({ uri: asset.uri, name: asset.fileName || `kyc-${Date.now()}.jpg`, type: asset.mimeType || 'image/jpeg' });
    }
  }

  async function handleSubmit() {
    if (!nationalId.trim() || !address.trim() || !idFront || !idBack || !selfie) {
      Alert.alert('Incomplete KYC', 'Please provide your ID number, address, ID front, ID back and selfie.');
      return;
    }

    setIsSubmitting(true);
    try {
      await kycApi.uploadKyc({ nationalId, residentialAddress: address, idFront, idBack, selfie });
      Alert.alert('KYC submitted', 'Your documents have been sent for verification.', [
        { text: 'Continue', onPress: () => router.replace('/(tabs)/dashboard') }
      ]);
    } catch (error) {
      Alert.alert('Upload failed', error instanceof Error ? error.message : 'Unable to upload KYC.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Screen scrollable>
      <View style={styles.header}>
        <AppText size={30} weight="bold">KYC verification</AppText>
        <AppText color={colors.muted} style={styles.subtitle}>
          Upload your identification documents to unlock secure wallet transfers.
        </AppText>
      </View>

      <Input label="National ID number" value={nationalId} onChangeText={setNationalId} placeholder="ID card or passport number" />
      <Input label="Residential address" value={address} onChangeText={setAddress} placeholder="City, quarter, street" multiline />

      <UploadBox title="ID front image" asset={idFront} onPress={() => pickImage('gallery', setIdFront)} />
      <UploadBox title="ID back image" asset={idBack} onPress={() => pickImage('gallery', setIdBack)} />
      <UploadBox title="Selfie photograph" asset={selfie} onPress={() => pickImage('camera', setSelfie)} icon="camera-outline" />

      <Button title="Submit KYC" loading={isSubmitting} onPress={handleSubmit} />
      <Button title="Skip for now" variant="ghost" onPress={() => router.replace('/(tabs)/dashboard')} />
    </Screen>
  );
}

function UploadBox({ title, asset, onPress, icon = 'image-outline' }: { title: string; asset: ImageAsset | null; onPress: () => void; icon?: keyof typeof Ionicons.glyphMap }) {
  return (
    <Pressable onPress={onPress} style={styles.uploadBox}>
      {asset ? (
        <Image source={{ uri: asset.uri }} style={styles.preview} />
      ) : (
        <View style={styles.uploadIcon}>
          <Ionicons name={icon} size={26} color={colors.primary} />
        </View>
      )}
      <View style={{ flex: 1 }}>
        <AppText weight="semibold">{title}</AppText>
        <AppText size={13} color={colors.muted}>{asset ? 'Image selected. Tap to change.' : 'Tap to upload image'}</AppText>
      </View>
      <Ionicons name="chevron-forward" size={22} color={colors.muted} />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  header: { paddingTop: 28, marginBottom: 18 },
  subtitle: { marginTop: 8, lineHeight: 22 },
  uploadBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.white,
    borderRadius: 18,
    padding: 14,
    marginBottom: 12
  },
  uploadIcon: {
    width: 54,
    height: 54,
    borderRadius: 18,
    backgroundColor: colors.primarySoft,
    alignItems: 'center',
    justifyContent: 'center'
  },
  preview: { width: 54, height: 54, borderRadius: 18 }
});
