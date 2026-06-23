# Backend/providers/orange/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class OrangeConfig:

    BASE_URL = "https://api.orange.com"

    CLIENT_ID = os.getenv("ORANGE_CLIENT_ID")
    CLIENT_SECRET = os.getenv("ORANGE_CLIENT_SECRET")

    AUTH_URL = "https://api.orange.com/oauth/v3/token"

    PAYMENT_URL = "https://api.orange.com/orange-money-webpay/dev/v1/payments"