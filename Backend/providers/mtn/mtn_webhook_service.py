#Backend/services/mtn_webhook_service.py
from database.db import db

from models.transaction import Transaction

from services.wallet_service import (
    credit_wallet_from_transaction
)

from models.wallet import Wallet


def process_mtn_webhook(
    reference_id,
    status,
    payload
):

    tx = Transaction.query.filter_by(
        reference_id=reference_id
    ).first()

    if not tx:
        return

    tx.provider_response = payload

    if status == "SUCCESSFUL":

        tx.status = "SUCCESS"

        # COLLECTION
        if tx.type == "MTN_COLLECTION":

            credit_wallet_from_transaction(
                reference_id
            )

        # DISBURSEMENT
        elif tx.type == "MTN_DISBURSEMENT":

            wallet = Wallet.query.filter_by(
                user_id=tx.user_id
            ).first()

            if wallet:
                wallet.balance -= float(
                    tx.amount
                )

        db.session.commit()

    elif status == "FAILED":

        tx.status = "FAILED"

        db.session.commit()