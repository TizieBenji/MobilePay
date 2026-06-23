# Backend/models/mtn_credentials.py

from database.db import db
from sqlalchemy.sql import func


class MTNCredentials(db.Model):

    __tablename__ = "mtn_credentials"

    # -----------------------------
    # PRIMARY KEY
    # -----------------------------
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------
    # PRODUCT TYPE
    # -----------------------------
    product_type = db.Column(
        db.String(30),
        nullable=False,
        index=True
    )
    # COLLECTION | DISBURSEMENT

    # -----------------------------
    # MTN API USER (UUID)
    # -----------------------------
    api_user = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
        index=True
    )

    # -----------------------------
    # MTN API KEY (SUBSCRIPTION KEY)
    # -----------------------------
    api_key = db.Column(
        db.Text,
        nullable=True
    )

    # -----------------------------
    # ENVIRONMENT
    # -----------------------------
    target_environment = db.Column(
        db.String(50),
        nullable=False,
        default="sandbox",
        index=True
    )
    # sandbox | production

    # -----------------------------
    # CALLBACK CONFIG
    # -----------------------------
    callback_host = db.Column(
        db.String(255),
        nullable=True
    )

    # -----------------------------
    # STATUS CONTROL
    # -----------------------------
    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        index=True
    )

    # -----------------------------
    # OWNER LINK (IMPORTANT ADDITION)
    # -----------------------------
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True
    )
    # This is CRITICAL for:
    # → get_valid_token(user_id)
    # → credential resolution per user

    # -----------------------------
    # AUDIT TRAIL
    # -----------------------------
    created_at = db.Column(
        db.DateTime,
        server_default=func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    # -----------------------------
    # DEBUG REPRESENTATION
    # -----------------------------
    def __repr__(self):
        return f"<MTNCredentials {self.product_type} | user_id={self.user_id}>"