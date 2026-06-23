#Backend/services/wallet_service.py
from database.db import db
from models.wallet import Wallet
from models.transaction import Transaction


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
        "balance": wallet.balance
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
        "balance": wallet.balance,
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

    wallet.balance += float(tx.amount)

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

    amount = float(tx.amount)

    # Safety guard
    if wallet.balance < amount:
        return False

    wallet.balance -= amount

    tx.wallet_processed = True

    db.session.commit()

    return True

# -----------------------------
# DEPOSIT (MANUAL TEST ONLY)
# -----------------------------
def deposit(user_id, amount):

    if amount <= 0:
        return {"success": False, "message": "Invalid amount"}, 400

    wallet = Wallet.query.filter_by(user_id=user_id).first()

    if not wallet:
        return {"success": False, "message": "Wallet not found"}, 404

    wallet.balance += amount

    db.session.commit()

    return {
        "success": True,
        "message": "Deposit successful",
        "new_balance": wallet.balance
    }, 200


# -----------------------------
# WITHDRAW (BASIC)
# -----------------------------
def withdraw(user_id, amount):

    if amount <= 0:
        return {"success": False, "message": "Invalid amount"}, 400

    wallet = Wallet.query.filter_by(user_id=user_id).first()

    if not wallet:
        return {"success": False, "message": "Wallet not found"}, 404

    if wallet.balance < amount:
        return {"success": False, "message": "Insufficient balance"}, 400

    wallet.balance -= amount

    db.session.commit()

    return {
        "success": True,
        "message": "Withdrawal successful",
        "new_balance": wallet.balance
    }, 200


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