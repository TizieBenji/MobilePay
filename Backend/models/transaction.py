# Backend/models/transaction.py

from database.db import db
from sqlalchemy.sql import func


class Transaction(db.Model):

    __tablename__ = "transactions"

    # -----------------------------
    # PRIMARY KEY
    # -----------------------------
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------
    # UNIQUE TRANSACTION REFERENCE
    # (MTN / Orange / Internal)
    # -----------------------------
    reference_id = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True
    )

    # -----------------------------
    # INTERNAL USER LINK
    # -----------------------------
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # -----------------------------
    # TRANSACTION TYPE
    # -----------------------------
    type = db.Column(
        db.String(30),
        nullable=False,
        index=True
    )
    # DEPOSIT | WITHDRAW | TRANSFER |
    # MTN_COLLECTION | MTN_DISBURSEMENT | ORANGE_COLLECTION | ORANGE_DISBURSEMENT

    # -----------------------------
    # INTERNAL STATUS MACHINE
    # -----------------------------
    status = db.Column(
        db.String(20),
        nullable=False,
        default="PENDING",
        index=True
    )
    # PENDING | SUCCESS | FAILED

    # -----------------------------
    # AMOUNT + CURRENCY
    # -----------------------------
    amount = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    currency = db.Column(
        db.String(10),
        nullable=False,
        default="XAF",
        index=True
    )

    # -----------------------------
    # SENDER / RECEIVER INFO
    # -----------------------------
    sender_phone = db.Column(
        db.String(20),
        nullable=True
    )

    receiver_phone = db.Column(
        db.String(20),
        nullable=True
    )

    sender_network = db.Column(
        db.String(20),
        nullable=True
    )
    # MTN | ORANGE | INTERNAL

    receiver_network = db.Column(
        db.String(20),
        nullable=True
    )

    # -----------------------------
    # PROVIDER TRACKING (MTN / ORANGE)
    # -----------------------------
    provider = db.Column(
        db.String(20),
        nullable=True,
        index=True
    )
    # MTN_COLLECTION | MTN_DISBURSEMENT | ORANGE

    provider_status = db.Column(
        db.String(50),
        nullable=True
    )
    # SUCCESSFUL | FAILED | PENDING (raw provider response)

    # -----------------------------
    # WEBHOOK RAW DATA (AUDIT LOGGING)
    # -----------------------------
    callback_payload = db.Column(
        db.JSON,
        nullable=True
    )

    # -----------------------------
    # IDEMPOTENCY FLAG
    # (PREVENT DOUBLE WALLET CREDIT/DEBIT)
    # -----------------------------
    wallet_processed = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
    )

    # -----------------------------
    # TIMESTAMPS
    # -----------------------------
    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    # -----------------------------
    # DEBUG / DEV REPRESENTATION
    # -----------------------------
    def __repr__(self):
        return f"<Transaction {self.reference_id} | {self.type} | {self.status}>"