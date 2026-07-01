from flask import Blueprint, request

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)
from database.db import db
from models.user import User

user_bp = Blueprint(
    "user",
    __name__
)

@user_bp.route(
    "/me",
    methods=["GET"]
)
@jwt_required()
def me():

    user_id = get_jwt_identity()

    user = User.query.get(
        int(user_id)
    )

    return {
        "id": user.id,
        "fullname": user.fullname,
        "email": user.email,
        "phone": user.phone,
        "network": user.network,
        "is_admin": user.is_admin
    }, 200


@user_bp.route(
    "/me",
    methods=["PATCH"]
)
@jwt_required()
def update_me():

    user_id = get_jwt_identity()

    user = User.query.get(
        int(user_id)
    )

    data = request.get_json()

    if not data:
        return {"success": False, "message": "No JSON body received"}, 400

    fullname = data.get("fullname")
    email = data.get("email")

    if fullname is not None:
        if not fullname.strip():
            return {"success": False, "message": "Full name cannot be empty"}, 400
        user.fullname = fullname.strip()

    if email is not None:
        if not email.strip():
            return {"success": False, "message": "Email cannot be empty"}, 400
        existing = User.query.filter(
            User.email == email,
            User.id != user.id
        ).first()
        if existing:
            return {"success": False, "message": "Email already in use"}, 400
        user.email = email.strip()

    db.session.commit()

    return {
        "id": user.id,
        "fullname": user.fullname,
        "email": user.email,
        "phone": user.phone,
        "network": user.network,
        "is_admin": user.is_admin
    }, 200