import uuid
import requests
import base64


from database.db import db

from models.mtn_credentials import (
    MTNCredentials
)

from providers.mtn.config import (
    MTNConfig
)


def create_api_user(
    product_type,
    callback_host=None
):
    api_user = str(
        uuid.uuid4()
    )

    url = (
        f"{MTNConfig.BASE_URL}"
        "/v1_0/apiuser"
    )

    headers = {
        "X-Reference-Id": api_user,
        "Ocp-Apim-Subscription-Key":
            MTNConfig.COLLECTION_PRIMARY_KEY,
        "Content-Type":
            "application/json"
    }

    payload = {
        "providerCallbackHost":
            callback_host or "localhost"
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    if response.status_code not in [
        201,
        202
    ]:

        return {
            "success": False,
            "message":
                response.text
        }, response.status_code

    credential = MTNCredentials(
        product_type=product_type,
        api_user=api_user,
        callback_host=callback_host
    )

    db.session.add(
        credential
    )

    db.session.commit()

    return {
        "success": True,
        "api_user": api_user
    }, 201
    



def create_api_key(
    credential_id
):

    credential = (
        MTNCredentials.query.get(
            credential_id
        )
    )

    if not credential:

        return {
            "success": False,
            "message":
                "Credential not found"
        }, 404

    url = (
        f"{MTNConfig.BASE_URL}"
        f"/v1_0/apiuser/"
        f"{credential.api_user}"
        f"/apikey"
    )

    headers = {
        "Ocp-Apim-Subscription-Key":
            MTNConfig.COLLECTION_PRIMARY_KEY
    }

    response = requests.post(
        url,
        headers=headers
    )

    if response.status_code != 201:

        return {
            "success": False,
            "message":
                response.text
        }, response.status_code

    data = response.json()

    credential.api_key = (
        data["apiKey"]
    )

    db.session.commit()

    return {
        "success": True,
        "api_key":
            credential.api_key
    }, 200


# providers/mtn/auth_service.py

from services.mtn_credential_service import get_mtn_credential
import requests


def generate_token(user_id, product_type):

    credential = get_mtn_credential(user_id, product_type)

    if not credential:
        return {"error": "MTN credential not found"}

    url = f"https://sandbox.momodeveloper.mtn.com/collection/token/"

    response = requests.post(
        url,
        auth=(credential.api_user, credential.api_key),
        headers={
            "Ocp-Apim-Subscription-Key": credential.api_key
        }
    )

    return response.json()

def request_to_pay(
    token,
    phone,
    amount
):

    reference_id = str(
        uuid.uuid4()
    )

    url = (
        f"{MTNConfig.BASE_URL}"
        "/collection/v1_0/requesttopay"
    )

    headers = {
        "Authorization":
            f"Bearer {token}",
        "X-Reference-Id":
            reference_id,
        "X-Target-Environment":
            "sandbox",
        "Ocp-Apim-Subscription-Key":
            MTNConfig.COLLECTION_PRIMARY_KEY
    }

    payload = {
        "amount": str(amount),
        "currency": "XAF",
        "externalId": reference_id,
        "payer": {
            "partyIdType": "MSISDN",
            "partyId": phone
        },
        "payerMessage":
            "MobilePay Deposit",
        "payeeNote":
            "Wallet Funding"
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    return reference_id, response

def get_request_status(
    token,
    reference_id
):

    url = (
        f"{MTNConfig.BASE_URL}"
        f"/collection/v1_0/requesttopay/{reference_id}"
    )

    headers = {
        "Authorization":
            f"Bearer {token}",
        "X-Target-Environment":
            "sandbox",
        "Ocp-Apim-Subscription-Key":
            MTNConfig.COLLECTION_PRIMARY_KEY
    }

    response = requests.get(
        url,
        headers=headers
    )

    return response.json()






