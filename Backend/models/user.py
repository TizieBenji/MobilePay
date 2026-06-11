from database.db import db

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    fullname = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.Text,
        nullable=False
    )

    network = db.Column(
        db.String(20)
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )