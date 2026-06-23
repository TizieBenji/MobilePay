from models.wallet import Wallet
from database.db import db


class OrangeWalletProvider:

    PROVIDER_NAME = "ORANGE"

    # Deposit via Orange channel
    def deposit(self, user_id, amount):

        wallet = Wallet.query.filter_by(user_id=user_id).first()

        if not wallet:
            return {"success": False, "message": "Wallet not found"}, 404

        wallet.balance += amount
        db.session.commit()

        return {
            "success": True,
            "provider": self.PROVIDER_NAME,
            "message": "Orange deposit successful",
            "balance": wallet.balance
        }, 200

    # Withdrawal via Orange channel
    def withdraw(self, user_id, amount):

        wallet = Wallet.query.filter_by(user_id=user_id).first()

        if not wallet:
            return {"success": False, "message": "Wallet not found"}, 404

        if wallet.balance < amount:
            return {"success": False, "message": "Insufficient balance"}, 400

        wallet.balance -= amount
        db.session.commit()

        return {
            "success": True,
            "provider": self.PROVIDER_NAME,
            "message": "Orange withdrawal successful",
            "balance": wallet.balance
        }, 200