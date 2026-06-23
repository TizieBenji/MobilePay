# Backend/providers/orange/auth_service.py

import requests
from providers.orange.config import OrangeConfig


def get_orange_token():

    response = requests.post(
        OrangeConfig.AUTH_URL,
        auth=(OrangeConfig.CLIENT_ID, OrangeConfig.CLIENT_SECRET),
        data={"grant_type": "client_credentials"}
    )

    data = response.json()

    return data.get("access_token")