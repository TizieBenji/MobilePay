# Mobilepay/Backend/routes/mtn_routes.py

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from providers.mtn.auth_service import (
    create_api_key,
    create_api_user,
    generate_token
)
from providers.mtn.disbursement_service import (
    transfer
)

from providers.mtn.disbursement_status_service import (
    check_disbursement_status
)

from providers.mtn.collection_service import request_to_pay

from providers.mtn.status_service import check_payment_status

from services.transaction_service import (
    create_transaction,
    update_transaction_status
)

from services.wallet_service import (
    credit_wallet_from_transaction,
     debit_wallet_from_transaction
)
from services.transaction_service import (
    update_transaction_status
)

from services.mtn_token_services import get_valid_token

from database.db import db

mtn_bp = Blueprint("mtn", __name__)


# -----------------------------
# 1. API USER
# -----------------------------
@mtn_bp.route("/api-user", methods=["POST"])
def create_mtn_api_user():

    data = request.get_json()

    return create_api_user(
        product_type=data.get("product_type"),
        callback_host=data.get("callback_host")
    )


# -----------------------------
# 2. API KEY
# -----------------------------
@mtn_bp.route("/api-key/<int:id>", methods=["POST"])
def create_mtn_api_key(id):

    return create_api_key(id)


# -----------------------------
# 3. TOKEN
# -----------------------------
@mtn_bp.route("/token/<int:id>", methods=["POST"])
def get_token(id):

    return generate_token(id)


# -----------------------------
# 4. REQUEST TO PAY (CORE ENTRY)
# -----------------------------
@mtn_bp.route("/request-to-pay", methods=["POST"])
@jwt_required()
def request_to_pay_route():

    user_id = int(get_jwt_identity())
    data = request.get_json()

    token = data.get("token")
    phone = data.get("phone")
    amount = data.get("amount")

    if not token or not phone or not amount:
        return {
            "success": False,
            "message": "token, phone, amount required"
        }, 400

    # 1. Call MTN
    result = request_to_pay(
        token=token,
        phone_number=phone,
        amount=amount
    )

    reference_id = result.get("reference_id")

    # 2. Create INTERNAL TRANSACTION (PENDING)
    tx = create_transaction(
        user_id=user_id,
        amount=float(amount),
        type="MTN_COLLECTION",
        sender_phone=phone,
        provider="MTN_COLLECTION",
        reference_id=reference_id,
        
    )

    return {
        "success": True,
        "message": "Payment initiated",
        "reference_id": reference_id,
        "transaction_id": tx.id,
        "mtn_response": result
    }, 202


# -----------------------------
# 5. CHECK PAYMENT STATUS
# -----------------------------
@mtn_bp.route("/check-status/<reference_id>", methods=["GET"])
@jwt_required()
def check_status(reference_id):

    data = request.get_json()
    token = data.get("token")

    if not token:
        return {
            "success": False,
            "message": "token required"
        }, 400

    # 1. Check MTN
    result, status_code = check_payment_status(reference_id, token)

    if status_code != 200:
        return {
            "success": False,
            "data": result
        }, 400

    mtn_status = result.get("status")

    # 2. Update internal transaction
    tx = update_transaction_status(
        reference_id,
        "SUCCESS" if mtn_status == "SUCCESSFUL"
        else "FAILED" if mtn_status == "FAILED"
        else "PENDING",
        raw_response=result
    )

    # 3. CREDIT WALLET ONLY ON SUCCESS
    if mtn_status == "SUCCESSFUL":
        credit_wallet_from_transaction(reference_id)

    return {
        "success": True,
        "reference_id": reference_id,
        "mtn_status": mtn_status,
        "internal_status": tx.status if tx else None
    }, 200


@ mtn_bp.route("/disbursement", methods=["POST"])
@jwt_required()
def mtn_disbursement():

    user_id = int(get_jwt_identity())
    data = request.get_json()

    phone = data.get("phone")
    amount = data.get("amount")

    token = get_valid_token(
        user_id=user_id,
        product_type="DISBURSEMENT"
    )

    result = disbursement_request(
        token=token,
        phone=phone,
        amount=amount
    )

    return {"success": True, "data": result}, 200
@mtn_bp.route(
    "/disbursement-status/<reference_id>",
    methods=["GET"]
)

@jwt_required()
def disbursement_status(
    reference_id
):

    token = request.args.get(
        "token"
    )

    result, status_code = (
        check_disbursement_status(
            reference_id,
            token
        )
    )

    return {
        "success": True,
        "data": result
    }, status_code    
# -----------------------------
# 6. WEBHOOK (READY FOR PRODUCTION)
# -----------------------------
@mtn_bp.route("/webhook", methods=["POST"])
def mtn_webhook():

    payload = request.get_json()

    reference_id = payload.get(
        "externalId"
    ) or payload.get(
        "reference_id"
    )

    status = payload.get(
        "status"
    )

    if not reference_id:
        return {
            "success": False,
            "message": "missing reference"
        }, 400

    tx = update_transaction_status(
        reference_id=reference_id,
        status="SUCCESS" if status == "SUCCESSFUL"
        else "FAILED" if status == "FAILED"
        else "PENDING",
        raw_response=payload
    )

    if not tx:
        return {
            "success": False,
            "message": "transaction not found"
        }, 404

    if status == "SUCCESSFUL":

        if tx.type == "MTN_COLLECTION":

            credit_wallet_from_transaction(
                reference_id
            )

        elif tx.type == "MTN_DISBURSEMENT":

            debit_wallet_from_transaction(
                reference_id
            )

    return {
        "success": True,
        "message": "webhook processed"
    }, 200