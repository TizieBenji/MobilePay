import uuid

from database.db import db
from models.wallet import Wallet
from models.transaction import Transaction
from models.kyc import KYC

def is_kyc_approved(user_id):

    kyc = KYC.query.filter_by(user_id=user_id).first()

    return kyc and kyc.status == "APPROVED"

def generate_reference():
    return str(uuid.uuid4())

def transfer(sender_id, receiver_id, amount, channel="INTERNAL"):

    if amount <= 0:
        return {"success": False, "message": "Invalid amount"}, 400

    # KYC enforcement (important for compliance)
    if not is_kyc_approved(sender_id):
        return {"success": False, "message": "Sender KYC not approved"}, 403

    sender_wallet = Wallet.query.filter_by(user_id=sender_id).first()
    receiver_wallet = Wallet.query.filter_by(user_id=receiver_id).first()

    if not sender_wallet or not receiver_wallet:
        return {"success": False, "message": "Wallet not found"}, 404

    if sender_wallet.balance < amount:
        return {"success": False, "message": "Insufficient balance"}, 400
    
    try:
        # Debit sender
        sender_wallet.balance -= amount

        # Credit receiver
        receiver_wallet.balance += amount

        # Create ledger entry
        trx = Transaction(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            type="TRANSFER",
            status="SUCCESS",
            reference=generate_reference()
        )

        db.session.add(trx)
        db.session.commit()
        
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
        "reference": trx.reference,
        "sender_balance": sender_wallet.balance,
        "receiver_balance": receiver_wallet.balance,
        "channel": channel
    }, 200