from database.db import db

class Transaction(db.Model):

    __tablename__ = "transactions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    reference_id = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    sender_phone = db.Column(
        db.String(20),
        nullable=False
    )

    receiver_phone = db.Column(
        db.String(20),
        nullable=False
    )

    sender_network = db.Column(
        db.String(20)
    )

    receiver_network = db.Column(
        db.String(20)
    )

    amount = db.Column(
        db.Numeric(15,2),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="PENDING"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )