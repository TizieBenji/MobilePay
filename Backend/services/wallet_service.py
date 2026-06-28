#Backend/services/wallet_service.py
from database.db import db
from models.wallet import Wallet
from models.transaction import Transaction
from utils.money import to_decimal, to_amount


# -----------------------------
# INTERNAL WALLET CREATION
# -----------------------------
def create_wallet_internal(user_id):

    existing = Wallet.query.filter_by(
        user_id=user_id
    ).first()

    if existing:
        return existing

    wallet = Wallet(
        user_id=user_id,
        balance=0.0,
        currency="XAF",
        status="ACTIVE"
    )

    db.session.add(wallet)
    return wallet


def create_wallet(user_id):

    wallet = create_wallet_internal(user_id)

    db.session.commit()

    return {
        "success": True,
        "message": "Wallet created",
        "balance": to_amount(wallet.balance)
    }, 201


# -----------------------------
# GET WALLET
# -----------------------------
def get_wallet(user_id):

    wallet = Wallet.query.filter_by(user_id=user_id).first()

    if not wallet:
        return {
            "success": False,
            "message": "Wallet not found"
        }, 404

    return {
        "success": True,
        "balance": to_amount(wallet.balance),
        "currency": wallet.currency,
        "status": wallet.status
    }, 200


# Safe auto-provision wallet
def get_wallet_safe(user_id):

    wallet = Wallet.query.filter_by(user_id=user_id).first()

    if not wallet:
        wallet = Wallet(
            user_id=user_id,
            balance=0.0,
            currency="XAF",
            status="ACTIVE"
        )
        db.session.add(wallet)
        db.session.commit()

    return wallet


# -----------------------------
# CORE CREDIT ENGINE (NEW)
# -----------------------------
def credit_wallet_from_transaction(reference_id):

    tx = Transaction.query.filter_by(
        reference_id=reference_id
    ).first()

    if not tx:
        return False

    if tx.status != "SUCCESS":
        return False

    if tx.wallet_processed:
        return True

    wallet = Wallet.query.filter_by(
        user_id=tx.user_id
    ).first()

    if not wallet:
        return False

    wallet.balance = to_decimal(wallet.balance) + to_decimal(tx.amount)

    tx.wallet_processed = True

    db.session.commit()

    return True

def debit_wallet_from_transaction(reference_id):

    tx = Transaction.query.filter_by(
        reference_id=reference_id
    ).first()

    if not tx:
        return False

    if tx.status != "SUCCESS":
        return False

    # Prevent duplicate debits
    if tx.wallet_processed:
        return True

    wallet = Wallet.query.filter_by(
        user_id=tx.user_id
    ).first()

    if not wallet:
        return False

    amount = to_decimal(tx.amount)

    # Safety guard
    if to_decimal(wallet.balance) < amount:
        return False

    wallet.balance = to_decimal(wallet.balance) - amount

    tx.wallet_processed = True

    db.session.commit()

    return True

# Deposit / withdraw live in transaction_service (ledger-backed, KYC-gated).
# The previous un-ledgered duplicates here were removed to keep one source
# of truth; wallet routes now delegate to transaction_service.


# -----------------------------
# FREEZE / UNFREEZE (NEW)
# -----------------------------
def freeze_wallet(user_id):

    wallet = Wallet.query.filter_by(user_id=user_id).first()

    if not wallet:
        return False

    wallet.status = "FROZEN"
    db.session.commit()

    return True


def unfreeze_wallet(user_id):

    wallet = Wallet.query.filter_by(user_id=user_id).first()

    if not wallet:
        return False

    wallet.status = "ACTIVE"
    db.session.commit()

    return True