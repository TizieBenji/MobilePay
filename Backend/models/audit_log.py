from database.db import db

class AuditLog(db.Model):

    __tablename__ = "audit_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    action = db.Column(
        db.String(255),
        nullable=False
    )

    ip_address = db.Column(
        db.String(50)
    )

    timestamp = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )