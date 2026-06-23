from flask import Blueprint, request

from flask_jwt_extended import jwt_required, get_jwt_identity

from services.wallet_service import (
    create_wallet,
    get_wallet,
    deposit,
    withdraw,
    create_wallet_internal
)

wallet_bp = Blueprint("wallet", __name__)


# Create wallet (manual or auto later)
@wallet_bp.route("/create", methods=["POST"])
@jwt_required()
def create_user_wallet():

    user_id = int(get_jwt_identity())
    return create_wallet(user_id)


# Get wallet info
@wallet_bp.route("/", methods=["GET"])
@jwt_required()
def wallet_info():

    user_id = int(get_jwt_identity())
    return get_wallet(user_id)


# Deposit
@wallet_bp.route("/deposit", methods=["POST"])
@jwt_required()
def wallet_deposit():

    user_id = int(get_jwt_identity())
    data = request.get_json()

    amount = data.get("amount", 0)

    return deposit(user_id, float(amount))


# Withdraw
@wallet_bp.route("/withdraw", methods=["POST"])
@jwt_required()
def wallet_withdraw():

    user_id = int(get_jwt_identity())
    data = request.get_json()

    amount = data.get("amount", 0)

    return withdraw(user_id, float(amount))