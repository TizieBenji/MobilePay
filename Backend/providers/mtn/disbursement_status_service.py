# Backend/providers/mtn/disbursement_status_service.py

import requests

from providers.mtn.config import MTNConfig


def check_disbursement_status(
    reference_id,
    token
):

    url = (
        f"{MTNConfig.BASE_URL}"
        f"/disbursement/v1_0/transfer/{reference_id}"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Target-Environment":
            MTNConfig.TARGET_ENVIRONMENT,
        "Ocp-Apim-Subscription-Key":
            MTNConfig.DISBURSEMENT_PRIMARY_KEY
    }

    response = requests.get(
        url,
        headers=headers
    )

    return (
        response.json(),
        response.status_code
    )