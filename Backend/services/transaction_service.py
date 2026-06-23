#Backend/services/transaction_service.py
import uuid

from database.db import db
from models.transaction import Transaction
from models.wallet import Wallet
from models.kyc import KYC


# -----------------------------
# UTILS
# -----------------------------
def generate_reference():
    return str(uuid.uuid4())


def is_kyc_approved(user_id):

    kyc = KYC.query.filter_by(user_id=user_id).first()

    return kyc is not None and kyc.status == "APPROVED"


# -----------------------------
# CREATE TRANSACTION RECORD
# (CORE MTN ENTRY POINT)
# -----------------------------
def create_transaction(
    user_id,
    amount,
    type,
    sender_phone=None,
    receiver_phone=None,
    sender_network=None,
    receiver_network=None,
    provider="INTERNAL",
    currency="XAF",
    reference_id=None
):

    tx = Transaction(
        reference_id=reference_id or generate_reference(),
        user_id=user_id,
        amount=amount,
        type=type,
        status="PENDING",
        sender_phone=sender_phone,
        receiver_phone=receiver_phone,
        sender_network=sender_network,
        receiver_network=receiver_network,
        provider=provider,
        currency=currency
    )

    db.session.add(tx)
    db.session.commit()

    return tx


# -----------------------------
# DEPOSIT (INTERNAL OR MTN CALLBACK)
# -----------------------------
def deposit(user_id, amount):

    if amount <= 0:
        return {"success": False, "message": "Invalid amount"}, 400

    wallet = Wallet.query.filter_by(user_id=user_id).first()

    if not wallet:
        return {"success": False, "message": "Wallet not found"}, 404

    wallet.balance += amount

    tx = create_transaction(
        user_id=user_id,
        amount=amount,
        type="DEPOSIT",
        provider="INTERNAL"
    )

    db.session.commit()

    return {
        "success": True,
        "message": "Deposit successful",
        "reference": tx.reference_id,
        "balance": wallet.balance
    }, 200


# -----------------------------
# WITHDRAW (KYC-GATED)
# -----------------------------
def withdraw(user_id, amount):

    if amount <= 0:
        return {"success": False, "message": "Invalid amount"}, 400

    if not is_kyc_approved(user_id):
        return {"success": False, "message": "KYC not approved"}, 403

    wallet = Wallet.query.filter_by(user_id=user_id).first()

    if not wallet:
        return {"success": False, "message": "Wallet not found"}, 404

    if wallet.balance < amount:
        return {"success": False, "message": "Insufficient balance"}, 400

    wallet.balance -= amount

    tx = create_transaction(
        user_id=user_id,
        amount=amount,
        type="WITHDRAW",
        provider="INTERNAL"
    )

    db.session.commit()

    return {
        "success": True,
        "message": "Withdrawal successful",
        "reference": tx.reference_id,
        "balance": wallet.balance
    }, 200


# -----------------------------
# TRANSFER (INTERNAL P2P)
# -----------------------------
def transfer(sender_id, receiver_id, amount):

    if amount <= 0:
        return {"success": False, "message": "Invalid amount"}, 400

    if not is_kyc_approved(sender_id):
        return {"success": False, "message": "Sender KYC not approved"}, 403

    sender_wallet = Wallet.query.filter_by(user_id=sender_id).first()
    receiver_wallet = Wallet.query.filter_by(user_id=receiver_id).first()

    if not sender_wallet or not receiver_wallet:
        return {"success": False, "message": "Wallet not found"}, 404

    if sender_wallet.balance < amount:
        return {"success": False, "message": "Insufficient balance"}, 400

    # atomic transfer
    sender_wallet.balance -= amount
    receiver_wallet.balance += amount

    tx = create_transaction(
        user_id=sender_id,
        amount=amount,
        type="TRANSFER",
        sender_phone=None,
        receiver_phone=None,
        provider="INTERNAL"
    )

    db.session.commit()

    return {
        "success": True,
        "message": "Transfer successful",
        "reference": tx.reference_id,
        "sender_balance": sender_wallet.balance
    }, 200


# -----------------------------
# GET TRANSACTIONS
# -----------------------------
def get_transactions(user_id):

    transactions = Transaction.query.filter(
        (Transaction.user_id == user_id)
    ).order_by(Transaction.created_at.desc()).all()

    return {
        "success": True,
        "transactions": [
            {
                "reference_id": t.reference_id,
                "type": t.type,
                "amount": float(t.amount),
                "status": t.status,
                "provider": t.provider,
                "sender_phone": t.sender_phone,
                "receiver_phone": t.receiver_phone,
                "created_at": str(t.created_at)
            }
            for t in transactions
        ]
    }, 200


# -----------------------------
# UPDATE STATUS (MTN WEBHOOK / POLLING)
# -----------------------------
def update_transaction_status(reference_id, status, raw_response=None):

    tx = Transaction.query.filter_by(reference_id=reference_id).first()

    if not tx:
        return None

    tx.status = status

    # optional debug trace
    if raw_response:
        tx.callback_payload = raw_response

    db.session.commit()

    return tx