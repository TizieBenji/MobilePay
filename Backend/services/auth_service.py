from database.db import db

from models.user import User
from models.token_blocklist import TokenBlocklist


from utils.password_utils import (
    hash_password,
    verify_password

)

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token
)

from services.wallet_service import (
     create_wallet,
    create_wallet_internal
)
from services.provider_router import route_provider


def register_user(
    fullname,
    email,
    phone,
    password,
    network=None
):

    existing_user = User.query.filter(
        (User.email == email) |
        (User.phone == phone)
    ).first()

    if existing_user:

        return {
            "success": False,
            "message": "User already exists"
        }, 400

    user = User(
        fullname=fullname,
        email=email,
        phone=phone,
        password_hash=hash_password(password),
        network=(network or route_provider(phone))
    )

    db.session.add(user)

    # Flush gets the user ID without committing yet
    db.session.flush()

    # Create wallet automatically
    wallet = create_wallet_internal(user.id)

    if not wallet:
        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to create wallet"
        }, 500

    db.session.commit()

    identity = str(user.id)
    token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return {
        "success": True,
        "message": "User created",
        "user_id": user.id,
        "token": token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "fullname": user.fullname,
            "email": user.email,
            "phone": user.phone,
            "network": user.network,
            "is_admin": user.is_admin
        }
    }, 201



def login_user(email, password):

    user = User.query.filter_by(email=email).first()

    if not user:
        return {
            "success": False,
            "message": "Invalid email or password"
        }, 401

    # use your helper function
    if not verify_password(password, user.password_hash):
        return {
            "success": False,
            "message": "Invalid email or password"
        }, 401
    
    identity = str(user.id)
    token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "fullname": user.fullname,
            "email": user.email,
            "phone": user.phone,
            "network": user.network,
            "is_admin": user.is_admin
        }
    }, 200


def logout_user(jti):
    """Revoke the access token by recording its jti in the blocklist."""
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()

    return {
        "success": True,
        "message": "Logged out"
    }, 200


def refresh_access_token(user_id):
    """Issue a fresh access token for the identity carried by a refresh token."""
    return {
        "success": True,
        "token": create_access_token(identity=str(user_id))
    }, 200