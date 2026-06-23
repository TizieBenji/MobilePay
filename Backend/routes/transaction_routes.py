from flask import Blueprint, request

from flask_jwt_extended import jwt_required, get_jwt_identity

from services.transaction_service import (
    deposit,
    withdraw,
    transfer,
    get_transactions
)

transaction_bp = Blueprint("transaction", __name__)

@transaction_bp.route("/deposit", methods=["POST"])
@jwt_required()
def deposit_route():

    user_id = int(get_jwt_identity())
    data = request.get_json()

    amount = float(data.get("amount", 0))

    return deposit(user_id, amount)


@transaction_bp.route("/withdraw", methods=["POST"])
@jwt_required()
def withdraw_route():

    user_id = int(get_jwt_identity())
    data = request.get_json()

    amount = float(data.get("amount", 0))

    return withdraw(user_id, amount)

@transaction_bp.route("/transfer", methods=["POST"])
@jwt_required()
def transfer_route():

    sender_id = int(get_jwt_identity())
    data = request.get_json()

    receiver_id = int(data.get("receiver_id"))
    amount = float(data.get("amount", 0))

    return transfer(sender_id, receiver_id, amount)

@transaction_bp.route("/", methods=["GET"])
@jwt_required()
def history_route():

    user_id = int(get_jwt_identity())

    return get_transactions(user_id)