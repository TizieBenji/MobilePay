# Backend/services/mtn_disbursement_service.py

from database.db import db

from models.wallet import Wallet

from services.transaction_service import (
    create_transaction
)


def initiate_disbursement(
    user_id,
    phone,
    amount,
    reference_id
):

    wallet = Wallet.query.filter_by(
        user_id=user_id
    ).first()

    if not wallet:
        return {
            "success": False,
            "message": "Wallet not found"
        }, 404

    if wallet.status != "ACTIVE":
        return {
            "success": False,
            "message": "Wallet frozen"
        }, 403

    if wallet.balance < amount:
        return {
            "success": False,
            "message": "Insufficient balance"
        }, 400

    tx = create_transaction(
        user_id=user_id,
        amount=amount,
        type="MTN_DISBURSEMENT",
        receiver_phone=phone,
        provider="MTN_DISBURSEMENT",
        reference_id=reference_id
    )

    return tx