import { PaymentScreen } from '@/components/domain/PaymentScreen';
import { pawapayApi } from '@/services/api/pawapay';

export default function WithdrawScreen() {
  return (
    <PaymentScreen
      title="Withdraw"
      subtitle="Send money from your wallet to a mobile-money account."
      phoneLabel="Pay-out number"
      phoneHelper="The MTN or Orange number that will receive the money."
      actionLabel="Withdraw"
      note="A disbursement is sent to the number you enter. Your wallet is debited once the operator confirms the payout."
      onSubmit={pawapayApi.disburse}
    />
  );
}
