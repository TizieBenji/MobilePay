"""One-off script to promote a user to admin.

Usage (from Backend/, with venv active):
    python scripts/make_admin.py user@example.com
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database.db import db
from models.user import User

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/make_admin.py <email>")
        sys.exit(1)

    email = sys.argv[1]

    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"No user found with email {email}")
            sys.exit(1)

        user.is_admin = True
        db.session.commit()
        print(f"{email} is now an admin.")
