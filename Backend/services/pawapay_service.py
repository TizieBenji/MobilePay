

import uuid, hmac, hashlib, logging, os
from decimal import Decimal
from datetime import datetime, timedelta

from sqlalchemy import select

from database.db import db
from models.transaction import Transaction
from models.wallet import Wallet

from providers.pawapay.collection_service import (initiate_deposit, check_deposit_status, poll_deposit_until_final,)
from providers.pawapay.payout_service import (
    initiate_payout,
    check_payout_status,
    poll_payout_until_final,
)
from providers.pawapay.config import PawaPayConfig

logger = logging.getLogger(__name__)

# Business floor for a PawaPay transaction. Stricter than PawaPay's own minimum
# (1 XAF) — this is a product rule, not a provider constraint.
XAF_MINIMUM_AMOUNT = 100

# Coarse upper bound for early rejection at the route layer, before the operator
# is known. Equals the highest cap across CMR operators; the precise per-operator
# cap is enforced in the provider layer after correspondent detection.
XAF_MAXIMUM_AMOUNT = PawaPayConfig.MAX_TRANSACTION_LIMIT




# PENDING disbursements older than this threshold are treated as stale and
# excluded from the reserved-balance sum. Must match POLL_MAX_ATTEMPTS * POLL_INTERVAL_SECONDS plus a safety margin.
PENDING_STALE_MINUTES = 30




# ===========================================================================
# COLLECTION (customer pays IN)
# ===========================================================================

def pawapay_collect(user_id: int, phone: str, amount, use_polling: bool = False) -> tuple[dict, int]:

    deposit_id = str(uuid.uuid4())

    try:
        tx = _create_pawapay_transaction(
            reference_id=deposit_id,
            user_id=user_id,
            amount=amount,
            tx_type="PAWAPAY_COLLECTION",
            sender_phone=phone,
        )
    
    except Exception as exc:
        logger.error("Failed to create collection transaction record: %s", exc)
        db.session.rollback()
        return {"success": False, "message": "Internal error — could not record transaction"}, 500

    result = initiate_deposit(deposit_id=deposit_id, phone=phone, amount=amount)

    if not result["ok"]:
        _safe_update_tx(tx, "FAILED", raw=result.get("raw"))
        return {
            "success": False,
            "message": result.get("error_detail", "Payment initiation failed"),
            "deposit_id": deposit_id,
            "pawa_status": result.get("status"),
        }, 400

    _safe_update_tx(tx, "PENDING", raw=result.get("raw"))

    if use_polling:
        final = poll_deposit_until_final(deposit_id)
        return _handle_collection_final(tx, final, deposit_id)

    return {
        "success": True,
        "message": (
            "Collection initiated. Customer will receive a payment prompt. "
            "Final status delivered via webhook."
        ),
        "deposit_id": deposit_id,
        "pawa_status": result.get("status"),
        "correspondent": result.get("correspondent"),
        "amount": int(amount),
        "currency": "XAF",
    }, 202


def pawapay_collection_status(deposit_id: str, requesting_user_id: int) -> tuple[dict, int]:
    tx = Transaction.query.filter_by(reference_id=deposit_id).first()
    if not tx:
        return {"success": False, "message": "Transaction not found"}, 404

    # Return 404 not 403 — don't confirm the ID exists to other users
    if tx.user_id != requesting_user_id:
        return {"success": False, "message": "Transaction not found"}, 404

    if tx.status in ("SUCCESS", "FAILED"):
        return {
            "success": True,
            "deposit_id": deposit_id,
            "internal_status": tx.status,
            "pawa_status": tx.provider_status,
            "wallet_credited": tx.wallet_processed,
        }, 200

    result = check_deposit_status(deposit_id)
    return _handle_collection_final(tx, result, deposit_id)


def _handle_collection_final(tx, pawa_result: dict, deposit_id: str):
    pawa_status = pawa_result.get("pawa_status", "")

    if pawa_status == "COMPLETED":
        _safe_update_tx(tx, "SUCCESS", raw=pawa_result.get("raw"), provider_status="COMPLETED")
        credited = _credit_wallet(tx)
        return {
            "success": True,
            "message": "Payment completed. Wallet credited.",
            "deposit_id": deposit_id,
            "pawa_status": "COMPLETED",
            "wallet_credited": credited,
        }, 200

    if pawa_status == "FAILED":
        _safe_update_tx(tx, "FAILED", raw=pawa_result.get("raw"), provider_status="FAILED")
        return {
            "success": False,
            "message": "Payment failed.",
            "deposit_id": deposit_id,
            "pawa_status": "FAILED",
            "failure_code": pawa_result.get("failure_code"),
            "failure_message": pawa_result.get("failure_message"),
        }, 200

    if pawa_status == "TIMEOUT":
        return {
            "success": False,
            "message": "Payment still processing. Poll /status later.",
            "deposit_id": deposit_id,
            "pawa_status": "PENDING",
        }, 202

    return {
        "success": True,
        "message": "Payment still processing.",
        "deposit_id": deposit_id,
        "pawa_status": pawa_status,
    }, 202






# ===========================================================================
# PAYOUT (platform pays OUT to customer)
# ===========================================================================

def pawapay_disburse(user_id: int, phone: str, amount, use_polling: bool = False) -> tuple[dict, int]:
    """ Initiate a PawaPay payout. """
    
    # LOCKED BALANCE CHECK
    wallet = (Wallet.query.filter_by(user_id=user_id).with_for_update().first())

    if not wallet:
        db.session.rollback()
        return {"success": False, "message": "Wallet not found"}, 404

    if wallet.status != "ACTIVE":
        db.session.rollback()
        return {"success": False, "message": "Wallet is not active"}, 403

    
    # STALE-AWARE PENDING RESERVATION
    # Transaction.created_at is stored as a naive UTC datetime
    # (db.DateTime, no tz info). We use datetime.utcnow() — also naive —
    # so the comparison is type-consistent and won't raise TypeError.
    stale_cutoff = datetime.utcnow() - timedelta(minutes=PENDING_STALE_MINUTES)

    pending_reserved = db.session.execute(
        select(db.func.coalesce(db.func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == "PAWAPAY_DISBURSEMENT",
            Transaction.status == "PENDING",
            Transaction.created_at >= stale_cutoff,
        )
    ).scalar()

    available_balance = Decimal(str(wallet.balance)) - Decimal(str(pending_reserved))

    if available_balance < Decimal(str(int(amount))):
        db.session.rollback()
        return {
            "success": False,
            "message": (
                f"Insufficient available balance. "
                f"Balance: {float(wallet.balance):.0f} XAF, "
                f"Reserved in pending payouts: {float(pending_reserved):.0f} XAF, "
                f"Available: {float(available_balance):.0f} XAF."
            ),
        }, 400


    # PERSIST PENDING TRANSACTION (still holding lock)
    payout_id = str(uuid.uuid4())
    try:
        tx = Transaction(
            reference_id=payout_id,
            user_id=user_id,
            amount=Decimal(str(int(amount))),
            type="PAWAPAY_DISBURSEMENT",
            status="PENDING",
            receiver_phone=phone,
            provider="PAWAPAY",
            provider_status="PENDING",
            currency="XAF",
            wallet_processed=False,
        )
        db.session.add(tx)
        db.session.commit() # ← releases the FOR UPDATE lock
    
    except Exception as exc:
        logger.error("Failed to persist payout transaction: %s", exc)
        db.session.rollback()
        return {"success": False, "message": "Internal error — could not record transaction"}, 500

    # CALL PAWAPAY
    result = initiate_payout(payout_id=payout_id, phone=phone, amount=amount)

    if not result["ok"]:
        _safe_update_tx(tx, "FAILED", raw=result.get("raw"))
        return {
            "success": False,
            "message": result.get("error_detail", "Payout initiation failed"),
            "payout_id": payout_id,
            "pawa_status": result.get("status"),
        }, 400

    _safe_update_tx(tx, "PENDING", raw=result.get("raw"))

    if use_polling:
        final = poll_payout_until_final(payout_id)
        return _handle_payout_final(tx, final, payout_id)

    return {
        "success": True,
        "message": "Payout initiated. Final status delivered via webhook.",
        "payout_id": payout_id,
        "pawa_status": result.get("status"),
        "correspondent": result.get("correspondent"),
        "amount": int(amount),
        "currency": "XAF",
    }, 202


def pawapay_payout_status(payout_id: str, requesting_user_id: int) -> tuple[dict, int]:
    tx = Transaction.query.filter_by(reference_id=payout_id).first()
    if not tx:
        return {"success": False, "message": "Transaction not found"}, 404

    if tx.user_id != requesting_user_id:
        return {"success": False, "message": "Transaction not found"}, 404

    if tx.status in ("SUCCESS", "FAILED"):
        return {
            "success": True,
            "payout_id": payout_id,
            "internal_status": tx.status,
            "pawa_status": tx.provider_status,
            "wallet_debited": tx.wallet_processed,
        }, 200

    result = check_payout_status(payout_id)
    return _handle_payout_final(tx, result, payout_id)


def _handle_payout_final(tx, pawa_result: dict, payout_id: str):
    pawa_status = pawa_result.get("pawa_status", "")

    if pawa_status == "COMPLETED":
        _safe_update_tx(tx, "SUCCESS", raw=pawa_result.get("raw"), provider_status="COMPLETED")
        debited = _debit_wallet(tx)
        return {
            "success": True,
            "message": "Payout completed. Wallet debited.",
            "payout_id": payout_id,
            "pawa_status": "COMPLETED",
            "wallet_debited": debited,
        }, 200

    if pawa_status == "FAILED":
        _safe_update_tx(tx, "FAILED", raw=pawa_result.get("raw"), provider_status="FAILED")
        return {
            "success": False,
            "message": "Payout failed.",
            "payout_id": payout_id,
            "pawa_status": "FAILED",
            "failure_code": pawa_result.get("failure_code"),
            "failure_message": pawa_result.get("failure_message"),
        }, 200

    if pawa_status == "TIMEOUT":
        return {
            "success": False,
            "message": "Payout still processing. Poll /status later.",
            "payout_id": payout_id,
            "pawa_status": "PENDING",
        }, 202

    return {
        "success": True,
        "message": "Payout still processing.",
        "payout_id": payout_id,
        "pawa_status": pawa_status,
    }, 202




# ===========================================================================
# WEBHOOK SIGNATURE VERIFICATION
# ===========================================================================

def verify_pawapay_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """
    Verify the x-pawapay-signature header (HMAC-SHA256).
    If PAWAPAY_WEBHOOK_SECRET is unset, logs a warning and passes through
    (allows sandbox testing without configuring the secret).
    """
    secret = os.getenv("PAWAPAY_WEBHOOK_SECRET")
    environment = os.getenv("PAWAPAY_ENVIRONMENT", "sandbox").lower()

    if not secret:
        # Fail closed in production: an unsigned-and-unverifiable webhook must
        # never be allowed to move money. Only skip verification in sandbox.
        if environment == "production":
            logger.error("PAWAPAY_WEBHOOK_SECRET not set in production — rejecting webhook.")
            return False
        logger.warning("PAWAPAY_WEBHOOK_SECRET not set — skipping webhook signature verification (sandbox only).")
        return True

    if not signature_header:
        logger.warning("PawaPay webhook received with no x-pawapay-signature header")
        return False

    expected = hmac.new(key=secret.encode("utf-8"), msg=raw_body, digestmod=hashlib.sha256,).hexdigest()

    return hmac.compare_digest(expected, signature_header.lower())




# ===========================================================================
# WEBHOOK HANDLERS
# ===========================================================================

def handle_deposit_webhook(payload: dict) -> tuple[dict, int]:
    deposit_id = payload.get("depositId")
    pawa_status = payload.get("status")

    if not deposit_id or not pawa_status:
        logger.warning("Deposit webhook: missing depositId or status")
        return {"success": False, "message": "Invalid payload"}, 400

    tx = Transaction.query.filter_by(reference_id=deposit_id).first()
    if not tx:
        logger.warning("Deposit webhook: unknown depositId %s", deposit_id)
        return {"success": True, "message": "Unknown transaction — ignored"}, 200

    if tx.status in ("SUCCESS", "FAILED"):
        logger.info("Deposit webhook: %s already terminal (%s) — skipping", deposit_id, tx.status)
        return {"success": True, "message": "Already processed"}, 200

    if pawa_status == "COMPLETED":
        _safe_update_tx(tx, "SUCCESS", raw=payload, provider_status="COMPLETED")
        _credit_wallet(tx)
        logger.info("Deposit %s COMPLETED via webhook. Wallet credited.", deposit_id)

    elif pawa_status == "FAILED":
        _safe_update_tx(tx, "FAILED", raw=payload, provider_status="FAILED")
        logger.info("Deposit %s FAILED via webhook.", deposit_id)

    else:
        # Intermediate status — store raw payload for audit only
        _store_webhook_payload(tx, payload)

    return {"success": True}, 200


def handle_payout_webhook(payload: dict) -> tuple[dict, int]:
    payout_id = payload.get("payoutId")
    pawa_status = payload.get("status")

    if not payout_id or not pawa_status:
        logger.warning("Payout webhook: missing payoutId or status")
        return {"success": False, "message": "Invalid payload"}, 400

    tx = Transaction.query.filter_by(reference_id=payout_id).first()
    if not tx:
        logger.warning("Payout webhook: unknown payoutId %s", payout_id)
        return {"success": True, "message": "Unknown transaction — ignored"}, 200

    if tx.status in ("SUCCESS", "FAILED"):
        logger.info("Payout webhook: %s already terminal — skipping", payout_id)
        return {"success": True, "message": "Already processed"}, 200

    if pawa_status == "COMPLETED":
        _safe_update_tx(tx, "SUCCESS", raw=payload, provider_status="COMPLETED")
        _debit_wallet(tx)
        logger.info("Payout %s COMPLETED via webhook. Wallet debited.", payout_id)

    elif pawa_status == "FAILED":
        _safe_update_tx(tx, "FAILED", raw=payload, provider_status="FAILED")
        logger.info("Payout %s FAILED via webhook.", payout_id)

    else:
        _store_webhook_payload(tx, payload)

    return {"success": True}, 200




# ===========================================================================
# Private DB helpers
# ===========================================================================


def _store_webhook_payload(tx: Transaction, payload: dict) -> None:
    """Store intermediate webhook payload for audit without changing status."""
    try:
        tx.callback_payload = payload
        db.session.commit()
    except Exception as exc:
        logger.error("Failed to store webhook payload for %s: %s", tx.reference_id, exc)
        db.session.rollback()


def _create_pawapay_transaction(reference_id: str, user_id: int, amount, tx_type: str, sender_phone: str | None = None, receiver_phone: str | None = None) -> Transaction:
    tx = Transaction(
        reference_id=reference_id,
        user_id=user_id,
        amount=Decimal(str(int(amount))),
        type=tx_type,
        status="PENDING",
        sender_phone=sender_phone,
        receiver_phone=receiver_phone,
        sender_network=None,
        receiver_network=None,
        provider="PAWAPAY",
        provider_status="PENDING",
        currency="XAF",
        wallet_processed=False,
    )
    db.session.add(tx)
    db.session.commit()
    return tx


def _safe_update_tx(tx: Transaction, status: str, raw: dict | None = None, provider_status: str | None = None) -> None:
    """
    Update transaction status. Swallows DB errors so a failed status write
    never causes a 500 back to PawaPay's webhook (which would trigger retries).
    """
    
    try:
        tx.status = status
        if provider_status:
            tx.provider_status = provider_status
        if raw is not None:
            tx.callback_payload = raw
        db.session.commit()
    except Exception as exc:
        logger.error("Failed to update transaction %s to status %s: %s", tx.reference_id, status, exc)
        db.session.rollback()


def _credit_wallet(tx: Transaction) -> bool:
    """ Credit wallet exactly once. """
    
    try:
        # Lock wallet row first, then re-read tx — both inside one DB transaction
        wallet = (Wallet.query.filter_by(user_id=tx.user_id).with_for_update().first())
        if not wallet:
            logger.error("No wallet for user %s — cannot credit", tx.user_id)
            db.session.rollback()
            return False

        # Re-read tx from DB *after* acquiring the wallet lock so we see the
        # committed wallet_processed value, not the stale in-memory copy
        fresh_tx = db.session.get(Transaction, tx.id)
        if fresh_tx is None or fresh_tx.wallet_processed:
            db.session.rollback()
            logger.info("Wallet already credited for %s — skipping", tx.reference_id)
            return True

        wallet.balance = Decimal(str(wallet.balance)) + Decimal(str(fresh_tx.amount))
        fresh_tx.wallet_processed = True
        db.session.commit()
        logger.info("Wallet credited: user=%s amount=%s new_balance=%s",fresh_tx.user_id, fresh_tx.amount, wallet.balance)
        return True
    except Exception as exc:
        logger.error("Failed to credit wallet for tx %s: %s", tx.reference_id, exc)
        db.session.rollback()
        return False


def _debit_wallet(tx: Transaction) -> bool:
    """ Debit wallet exactly once. """
    try:
        wallet = (Wallet.query.filter_by(user_id=tx.user_id).with_for_update().first())
        
        if not wallet:
            logger.error("No wallet for user %s — cannot debit", tx.user_id)
            db.session.rollback()
            return False

        fresh_tx = db.session.get(Transaction, tx.id)
        
        if fresh_tx is None or fresh_tx.wallet_processed:
            db.session.rollback()
            logger.info("Wallet already debited for %s — skipping", tx.reference_id)
            return True

        if Decimal(str(wallet.balance)) < Decimal(str(fresh_tx.amount)):
            logger.error(
                "Safety-net balance check failed on debit: user=%s balance=%s amount=%s",
                tx.user_id, wallet.balance, fresh_tx.amount,
            )
            db.session.rollback()
            return False

        wallet.balance = Decimal(str(wallet.balance)) - Decimal(str(fresh_tx.amount))
        fresh_tx.wallet_processed = True
        db.session.commit()
        
        logger.info("Wallet debited: user=%s amount=%s new_balance=%s", fresh_tx.user_id, fresh_tx.amount, wallet.balance)
        
        return True
    
    except Exception as exc:
        logger.error("Failed to debit wallet for tx %s: %s", tx.reference_id, exc)
        db.session.rollback()
        return False
