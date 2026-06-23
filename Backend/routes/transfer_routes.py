from flask import Blueprint, request

from flask_jwt_extended import jwt_required, get_jwt_identity

#from services.transfer_service import transfer

from services.provider_router import route_transfer


transfer_bp = Blueprint("transfer", __name__)

@transfer_bp.route("", methods=["POST"])
@jwt_required()
def transfer_route():

    sender_id = int(get_jwt_identity())
    data = request.get_json()

    receiver_id = int(data.get("receiver_id"))
    amount = float(data.get("amount", 0))
    channel = data.get("channel", "INTERNAL")

    return route_transfer(
        sender_id,
        receiver_id,
        amount,
        channel
    )