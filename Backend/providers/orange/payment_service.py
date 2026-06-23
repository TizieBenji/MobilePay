# Backend/providers/orange/payment_service.py

import uuid
import requests
from providers.orange.config import OrangeConfig


def orange_request_payment(token, phone, amount):

    reference = str(uuid.uuid4())

    payload = {
        "merchant_key": OrangeConfig.CLIENT_ID,
        "currency": "XAF",
        "order_id": reference,
        "amount": amount,
        "return_url": "http://localhost:5000/api/orange/callback",
        "cancel_url": "http://localhost:5000/api/orange/cancel",
        "notif_url": "http://localhost:5000/api/orange/webhook",
        "lang": "en",
        "reference": reference
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        OrangeConfig.PAYMENT_URL,
        json=payload,
        headers=headers
    )

    return {
        "reference_id": reference,
        "response": response.json(),
        "status_code": response.status_code
    }