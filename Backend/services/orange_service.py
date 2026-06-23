from providers.orange_wallet import OrangeWalletProvider


orange_provider = OrangeWalletProvider()


def orange_deposit(user_id, amount):
    return orange_provider.deposit(user_id, amount)


def orange_withdraw(user_id, amount):
    return orange_provider.withdraw(user_id, amount)

