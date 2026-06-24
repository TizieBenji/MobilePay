import logging
import os
import uuid as _uuid_mod

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.pawapay_service import (
    pawapay_collect,
    pawapay_collection_status,
    pawapay_disburse,
    pawapay_payout_status,
    handle_deposit_webhook,
    handle_payout_webhook,
    verify_pawapay_signature,
    XAF_MINIMUM_AMOUNT,
    XAF_MAXIMUM_AMOUNT,
)

logger = logging.getLogger(__name__)

pawapay_bp = Blueprint("pawapay", __name__)



# ---------------------------------------------------------------------------
# Polling guard
# ---------------------------------------------------------------------------
# polling=true blocks a Flask worker thread for up to POLL_MAX_ATTEMPTS * POLL_INTERVAL_SECONDS = 50s.
_POLLING_ALLOWED = os.getenv("PAWAPAY_ALLOW_POLLING", "true").lower() == "true"


# ===========================================================================
# INPUT VALIDATION HELPER
# ===========================================================================

def _parse_payment_body(data: dict) -> tuple[str | None, float | None, bool, str | None]:
    """
    Parse and validate phone, amount, polling from a request body.

    Returns (phone, amount, use_polling, error_message).
    error_message is None on success.
    """
    if not data:
        return None, None, False, "JSON body required"

    phone = data.get("phone", "")
    if not isinstance(phone, str) or not phone.strip():
        return None, None, False, "'phone' is required and must be a string"
    phone = phone.strip()

    amount_raw = data.get("amount")
    if amount_raw is None:
        return None, None, False, "'amount' is required"

    try:
        amount = float(amount_raw)
    except (TypeError, ValueError):
        return None, None, False, "'amount' must be a number"

    if amount < XAF_MINIMUM_AMOUNT:
        return None, None, False, f"Minimum amount is {XAF_MINIMUM_AMOUNT} XAF"

    if amount > XAF_MAXIMUM_AMOUNT:
        return None, None, False, f"Maximum amount is {XAF_MAXIMUM_AMOUNT:,} XAF"

    # Polling is server-config-gated, not freely caller-controlled
    polling_requested = bool(data.get("polling", False))
    use_polling = polling_requested and _POLLING_ALLOWED
    if polling_requested and not _POLLING_ALLOWED:
        logger.info("polling=true requested but PAWAPAY_ALLOW_POLLING is not set — ignoring")

    return phone, amount, use_polling, None



def _is_valid_uuid(value: str) -> bool:
    """Reject path parameters that are not valid UUIDs before hitting the DB."""
    try:
        _uuid_mod.UUID(value, version=4)
        return True
    except (ValueError, AttributeError):
        return False




# ===========================================================================
# COLLECTION (MTN / Orange → platform)
# ===========================================================================

@pawapay_bp.route("/collect", methods=["POST"])
@jwt_required()
def initiate_collection():
    """ Request money FROM a customer's MTN or Orange wallet. """
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)
    phone, amount, use_polling, err = _parse_payment_body(data)

    if err:
        return {"success": False, "message": err}, 400

    response, status_code = pawapay_collect(user_id=user_id, phone=phone, amount=amount, use_polling=use_polling)
    return response, status_code


@pawapay_bp.route("/collect/<deposit_id>", methods=["GET"])
@jwt_required()
def collection_status(deposit_id: str):
    """ Check the status of a collection. Only returns data if the deposit belongs to the requesting user. """
    
    if not _is_valid_uuid(deposit_id):
        return {"success": False, "message": "Invalid transaction ID"}, 400
    
    user_id = int(get_jwt_identity())
    response, status_code = pawapay_collection_status(deposit_id, requesting_user_id=user_id)
    return response, status_code




# ===========================================================================
# DISBURSEMENT (platform → MTN / Orange)
# ===========================================================================

@pawapay_bp.route("/disburse", methods=["POST"])
@jwt_required()
def initiate_disbursement():
    """ Send money FROM the platform TO a customer's MTN or Orange wallet. """

    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)
    phone, amount, use_polling, err = _parse_payment_body(data)

    if err:
        return {"success": False, "message": err}, 400

    response, status_code = pawapay_disburse(user_id=user_id, phone=phone, amount=amount, use_polling=use_polling)
    return response, status_code


@pawapay_bp.route("/disburse/<payout_id>", methods=["GET"])
@jwt_required()
def disbursement_status(payout_id: str):
    """ Check the status of a disbursement. Only returns data if the payout belongs to the requesting user. """
    
    if not _is_valid_uuid(payout_id):
        return {"success": False, "message": "Invalid transaction ID"}, 400
    
    user_id = int(get_jwt_identity())
    response, status_code = pawapay_payout_status(payout_id, requesting_user_id=user_id)
    return response, status_code




# ===========================================================================
# WEBHOOKS — no JWT, HMAC-verified, called by PawaPay servers
# ===========================================================================

@pawapay_bp.route("/webhook/deposit", methods=["POST"])
def deposit_webhook():
    """PawaPay calls this when a deposit reaches COMPLETED or FAILED."""
    raw_body = request.get_data()
    signature = request.headers.get("x-pawapay-signature")

    if not verify_pawapay_signature(raw_body, signature):
        logger.warning("Deposit webhook: invalid signature — rejected")
        return {"success": False, "message": "Invalid signature"}, 401

    payload = request.get_json(silent=True)
    if not payload:
        return {"success": False, "message": "Empty payload"}, 400

    logger.info("Deposit webhook received: depositId=%s status=%s", payload.get("depositId"), payload.get("status"))
    return handle_deposit_webhook(payload)


@pawapay_bp.route("/webhook/payout", methods=["POST"])
def payout_webhook():
    """PawaPay calls this when a payout reaches COMPLETED or FAILED."""
    raw_body = request.get_data()
    signature = request.headers.get("x-pawapay-signature")

    if not verify_pawapay_signature(raw_body, signature):
        logger.warning("Payout webhook: invalid signature — rejected")
        return {"success": False, "message": "Invalid signature"}, 401

    payload = request.get_json(silent=True)
    if not payload:
        return {"success": False, "message": "Empty payload"}, 400

    logger.info("Payout webhook received: payoutId=%s status=%s",payload.get("payoutId"), payload.get("status"),)
    
    return handle_payout_webhook(payload)
