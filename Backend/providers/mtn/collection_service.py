import uuid
import requests

from providers.mtn.config import MTNConfig


def request_to_pay(
    token,
    phone_number,
    amount,
    external_id=None
):

    reference_id = str(uuid.uuid4())

    url = (
        f"{MTNConfig.BASE_URL}"
        "/collection/v1_0/requesttopay"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Reference-Id": reference_id,
        "X-Target-Environment": "sandbox",
        "Ocp-Apim-Subscription-Key": MTNConfig.COLLECTION_PRIMARY_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "amount": str(amount),
        "currency": "EUR",
        "externalId": external_id or reference_id,
        "payer": {
            "partyIdType": "MSISDN",
            "partyId": phone_number
        },
        "payerMessage": "MobilePay Deposit",
        "payeeNote": "Wallet funding"
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    return {
        "reference_id": reference_id,
        "status_code": response.status_code,
        "response": response.json() if response.text else {}
    }