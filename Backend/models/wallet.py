from database.db import db
from sqlalchemy.sql import func


class Wallet(db.Model):
    __tablename__ = "wallets"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    balance = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    currency = db.Column(
        db.String(10),
        default="XAF"
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ACTIVE"
        # ACTIVE | FROZEN | SUSPENDED | CLOSED
    )

    created_at = db.Column(
        db.DateTime,
        server_default=func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )