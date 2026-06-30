from flask import Blueprint, request

from flask_jwt_extended import jwt_required, get_jwt_identity

#from services.transfer_service import transfer

from services.provider_router import route_transfer
from models.user import User


transfer_bp = Blueprint("transfer", __name__)

@transfer_bp.route("", methods=["POST"])
@jwt_required()
def transfer_route():

    sender_id = int(get_jwt_identity())
    data = request.get_json() or {}

    # Internal P2P is keyed on the recipient's user id. The app sends a phone
    # number (better UX than asking users for an internal id), so resolve the
    # phone to a user here. A raw receiver_id is still accepted as a fallback.
    receiver_id = data.get("receiver_id")
    if receiver_id is None:
        receiver_phone = (data.get("receiver_phone") or data.get("receiver") or "").strip()
        if not receiver_phone:
            return {"success": False, "message": "receiver_phone is required"}, 400

        receiver = User.query.filter_by(phone=receiver_phone).first()
        if not receiver:
            return {"success": False, "message": "No MobilePay account found for that number"}, 404
        receiver_id = receiver.id

    try:
        receiver_id = int(receiver_id)
    except (TypeError, ValueError):
        return {"success": False, "message": "Invalid recipient"}, 400

    amount = float(data.get("amount", 0))
    channel = data.get("channel", "INTERNAL")

    return route_transfer(
        sender_id,
        receiver_id,
        amount,
        channel
    )
