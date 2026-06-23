from providers.mtn_wallet import MTNWalletProvider


mtn_provider = MTNWalletProvider()


def mtn_deposit(user_id, amount):
    return mtn_provider.deposit(user_id, amount)


def mtn_withdraw(user_id, amount):
    return mtn_provider.withdraw(user_id, amount)