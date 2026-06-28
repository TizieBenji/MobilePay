from services.transfer_service import transfer

def route_transfer(sender_id, receiver_id, amount, channel):
    
    channel = channel.upper() if channel else "INTERNAL"

    if channel in ("MTN", "ORANGE", "MTN_TO_ORANGE", "ORANGE_TO_MTN"):
        return transfer(
            sender_id,
            receiver_id,
            amount,
            channel=channel
        )

    return transfer(
        sender_id,
        receiver_id,
        amount,
        channel="INTERNAL"
    )
    
    # Backend/services/provider_router.py

def route_provider(phone):

    if phone.startswith("67") or phone.startswith("650"):
        return "MTN"

    if phone.startswith("69") or phone.startswith("655"):
        return "ORANGE"

    return "MTN"  # default fallback

def initiate_payment(user_id, phone, amount, token_mtn, token_orange):

    provider = route_provider(phone)

    if provider == "MTN":
        from providers.mtn.collection_service import request_to_pay
        return request_to_pay(token_mtn, phone, amount)

    elif provider == "ORANGE":
        from providers.orange.payment_service import orange_request_payment
        return orange_request_payment(token_orange, phone, amount)