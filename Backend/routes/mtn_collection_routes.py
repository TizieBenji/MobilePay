#MobilePay/Backend/routes/mtn_collection_routes.py
from flask import Blueprint, request

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from providers.mtn.collection_service import (
    request_to_pay
)

mtn_collection_bp = Blueprint(
    "mtn_collection",
    __name__
)


@mtn_collection_bp.route(
    "/request-to-pay",
    methods=["POST"]
)
@jwt_required()
def pay():

    data = request.get_json()

    token = data.get("token")
    phone = data.get("phone")
    amount = data.get("amount")

    result = request_to_pay(
        token=token,
        phone_number=phone,
        amount=amount
    )

    return result, 200