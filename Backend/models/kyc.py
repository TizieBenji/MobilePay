from database.db import db

class KYC(db.Model):

    __tablename__ = "kyc"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    national_id = db.Column(
        db.String(50),
        nullable=False
    )

    selfie = db.Column(
        db.String(255)
    )

    id_front = db.Column(
        db.String(255)
    )

    id_back = db.Column(
        db.String(255)
    )

    status = db.Column(
        db.String(20),
        default="PENDING"
    )

    submitted_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )