# Backend/providers/mtn/disbursement_service.py

import uuid
import requests

from providers.mtn.config import MTNConfig


def transfer(
    token,
    phone_number,
    amount,
    external_id=None
):

    reference_id = str(uuid.uuid4())

    url = (
        f"{MTNConfig.BASE_URL}"
        "/disbursement/v1_0/transfer"
    )

    payload = {
        "amount": str(amount),
        "currency": "EUR",
        "externalId": external_id or reference_id,
        "payee": {
            "partyIdType": "MSISDN",
            "partyId": phone_number
        },
        "payerMessage": "MobilePay Withdrawal",
        "payeeNote": "MobilePay Transfer"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Reference-Id": reference_id,
        "X-Target-Environment": MTNConfig.TARGET_ENVIRONMENT,
        "Ocp-Apim-Subscription-Key":
            MTNConfig.DISBURSEMENT_PRIMARY_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    return {
        "reference_id": reference_id,
        "response": (
            response.json()
            if response.text else {}
        ),
        "status_code": response.status_code
    }