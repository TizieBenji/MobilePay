from flask import Blueprint

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)
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
    
    print(
    "JWT USER ID:",
    user_id,
    type(user_id)
)

    return {
        "id": user.id,
        "fullname": user.fullname,
        "email": user.email,
        "phone": user.phone,
        "network": user.network
    }, 200