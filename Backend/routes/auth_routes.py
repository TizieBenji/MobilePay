from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.auth_service import register_user, login_user, refresh_access_token, logout_user
from extensions import limiter

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()

    if not data:
        return {"success": False, "message": "No JSON body received"}, 400

    required_fields = ["fullname", "email", "phone", "password"]

    for field in required_fields:
        if field not in data:
            return {"success": False, "message": f"Missing field: {field}"}, 400

    return register_user(
        fullname=data["fullname"],
        email=data["email"],
        phone=data["phone"],
        password=data["password"],
        network=data.get("network")
    )


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()

    if not data:
        return {"success": False, "message": "No JSON body received"}, 400

    if "email" not in data or "password" not in data:
        return {"success": False, "message": "Email and password required"}, 400

    return login_user(
        email=data["email"],
        password=data["password"]
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    return refresh_access_token(get_jwt_identity())


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return logout_user(get_jwt()["jti"])