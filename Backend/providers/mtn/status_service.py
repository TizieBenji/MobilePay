import requests

from providers.mtn.config import MTNConfig


def check_payment_status(reference_id, token):

    url = (
        f"{MTNConfig.BASE_URL}"
        f"/collection/v1_0/requesttopay/{reference_id}"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Target-Environment": "sandbox",
        "Ocp-Apim-Subscription-Key": MTNConfig.COLLECTION_PRIMARY_KEY
    }

    response = requests.get(url, headers=headers)

    return response.json(), response.status_code