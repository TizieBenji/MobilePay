from database.db import db
from sqlalchemy.sql import func


class KYC(db.Model):
    __tablename__ = "kyc"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    national_id_number = db.Column(db.String(50), nullable=False)

    document_type = db.Column(db.String(20), nullable=False)

    document_front = db.Column(db.Text, nullable=False)
    document_back = db.Column(db.Text, nullable=True)
    selfie_image = db.Column(db.Text, nullable=True)

    status = db.Column(
        db.String(20),
        default="PENDING",
        nullable=False
    )

    rejection_reason = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )