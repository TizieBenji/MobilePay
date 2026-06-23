from flask import Blueprint, request

from flask_jwt_extended import jwt_required, get_jwt_identity

# reuse SAME transaction engine
from services.transaction_service import update_transaction_status
from services.wallet_service import credit_wallet_from_transaction


from services.orange_service import (
    orange_deposit,
    orange_withdraw
)
# Backend/routes/orange_routes.py

from flask import Blueprint, request

orange_bp = Blueprint("orange", __name__)


@orange_bp.route("/webhook", methods=["POST"])
def orange_webhook():

    payload = request.get_json()

    reference_id = payload.get("order_id")
    status = payload.get("status")


    tx = update_transaction_status(
        reference_id,
        "SUCCESS" if status == "SUCCESS" else "FAILED",
        raw_response=payload
    )

    if status == "SUCCESS":
        credit_wallet_from_transaction(reference_id)

    return {"success": True}, 200


orange_bp = Blueprint("orange", __name__)

@orange_bp.route("/deposit", methods=["POST"])
@jwt_required()
def deposit_orange():

    user_id = int(get_jwt_identity())
    data = request.get_json()

    amount = float(data.get("amount", 0))

    return orange_deposit(user_id, amount)



@orange_bp.route("/withdraw", methods=["POST"])
@jwt_required()
def withdraw_orange():

    user_id = int(get_jwt_identity())
    data = request.get_json()

    amount = float(data.get("amount", 0))

    return orange_withdraw(user_id, amount)
