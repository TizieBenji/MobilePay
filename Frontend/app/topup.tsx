import { PaymentScreen } from '@/components/domain/PaymentScreen';
import { pawapayApi } from '@/services/api/pawapay';

export default function TopUpScreen() {
  return (
    <PaymentScreen
      title="Top up"
      subtitle="Pull money into your wallet from a mobile-money account."
      phoneLabel="Pay-in number"
      phoneHelper="The MTN or Orange number that will receive the payment prompt."
      actionLabel="Request top up"
      note="A collection request is sent to the number you enter. Once the customer approves it on their phone, your wallet is credited automatically."
      onSubmit={pawapayApi.collect}
    />
  );
}
