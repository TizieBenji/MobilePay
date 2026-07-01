import uuid

from database.db import db
from models.wallet import Wallet
from models.transaction import Transaction
from models.kyc import KYC
from models.user import User
from utils.money import to_decimal, to_amount

def is_kyc_approved(user_id):

    kyc = KYC.query.filter_by(user_id=user_id).first()

    return kyc and kyc.status == "APPROVED"

def generate_reference():
    return str(uuid.uuid4())

def _lock_wallet(user_id):
    """Read a wallet row with a FOR UPDATE row lock held until commit/rollback."""
    return (
        Wallet.query
        .filter_by(user_id=user_id)
        .with_for_update()
        .first()
    )


def transfer(sender_id, receiver_id, amount, channel="INTERNAL"):

    if amount <= 0:
        return {"success": False, "message": "Invalid amount"}, 400

    if sender_id == receiver_id:
        return {"success": False, "message": "Cannot transfer to self"}, 400

    # KYC enforcement (important for compliance)
    if not is_kyc_approved(sender_id):
        return {"success": False, "message": "Sender KYC not approved"}, 403

    amount = to_decimal(amount)
    reference = generate_reference()

    try:
        # Lock both wallet rows in a deterministic order (lowest user_id first)
        # so concurrent A->B and B->A transfers can never deadlock.
        first_id, second_id = sorted((sender_id, receiver_id))
        _lock_wallet(first_id)
        _lock_wallet(second_id)

        # Re-fetch under the lock so the balance check sees committed state,
        # not a value another transaction may have changed before we locked.
        sender_wallet = Wallet.query.filter_by(user_id=sender_id).first()
        receiver_wallet = Wallet.query.filter_by(user_id=receiver_id).first()

        if not sender_wallet or not receiver_wallet:
            db.session.rollback()
            return {"success": False, "message": "Wallet not found"}, 404

        sender_user = User.query.get(sender_id)
        receiver_user = User.query.get(receiver_id)

        if sender_wallet.status != "ACTIVE":
            db.session.rollback()
            return {"success": False, "message": "Sender wallet is not active"}, 403

        if to_decimal(sender_wallet.balance) < amount:
            db.session.rollback()
            return {"success": False, "message": "Insufficient balance"}, 400

        # Debit sender
        sender_wallet.balance = to_decimal(sender_wallet.balance) - amount

        # Credit receiver
        receiver_wallet.balance = to_decimal(receiver_wallet.balance) + amount

        # Create one ledger entry per party so each user's own transaction
        # history shows the transfer (previously only the sender got a row,
        # so the receiver's balance changed with no matching history entry).
        sender_trx = Transaction(
            reference_id=reference,
            user_id=sender_id,
            amount=amount,
            type="TRANSFER",
            status="SUCCESS",
            sender_phone=sender_user.phone,
            receiver_phone=receiver_user.phone,
            provider="INTERNAL",
            sender_network=sender_user.network,
            receiver_network=receiver_user.network,
        )

        receiver_trx = Transaction(
            reference_id=f"{reference}-r",
            user_id=receiver_id,
            amount=amount,
            type="TRANSFER",
            status="SUCCESS",
            sender_phone=sender_user.phone,
            receiver_phone=receiver_user.phone,
            provider="INTERNAL",
            sender_network=sender_user.network,
            receiver_network=receiver_user.network,
        )

        db.session.add(sender_trx)
        db.session.add(receiver_trx)

        sender_balance = to_amount(sender_wallet.balance)
        receiver_balance = to_amount(receiver_wallet.balance)

        db.session.commit()  # releases both FOR UPDATE locks

    except Exception as e:
        db.session.rollback()
        return {
            "success": False,
            "message": "Transfer failed",
            "error": str(e)
        }, 500

    return {
        "success": True,
        "message": "Transfer successful",
        "reference": reference,
        "sender_balance": sender_balance,
        "receiver_balance": receiver_balance,
        "channel": channel
    }, 200