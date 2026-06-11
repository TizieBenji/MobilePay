from database.db import db

class Wallet(db.Model):

    __tablename__ = "wallets"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    balance = db.Column(
        db.Numeric(15,2),
        default=0.00
    )

    currency = db.Column(
        db.String(10),
        default="XAF"
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )