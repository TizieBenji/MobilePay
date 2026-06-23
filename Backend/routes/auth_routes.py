from flask import Blueprint, request
from services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
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
        password=data["password"]
    )


@auth_bp.route("/login", methods=["POST"])
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