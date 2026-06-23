#MobilePay/Backend/providers/mtn/config.py
import os
from dotenv import load_dotenv

load_dotenv()

import os
from dotenv import load_dotenv

loaded = load_dotenv()

print("DOTENV LOADED:", loaded)
print("CURRENT WORKDIR:", os.getcwd())
print(
    "MTN_COLLECTION_PRIMARY_KEY:",
    os.getenv("MTN_COLLECTION_PRIMARY_KEY")
)

class MTNConfig:

    BASE_URL = "https://sandbox.momodeveloper.mtn.com"

    TARGET_ENVIRONMENT = "sandbox"

    COLLECTION_PRIMARY_KEY = os.getenv(
        "MTN_COLLECTION_PRIMARY_KEY"
    )

    COLLECTION_SECONDARY_KEY = os.getenv(
        "MTN_COLLECTION_SECONDARY_KEY"
    )

    DISBURSEMENT_PRIMARY_KEY = os.getenv(
        "MTN_DISBURSEMENT_PRIMARY_KEY"
    )

    DISBURSEMENT_SECONDARY_KEY = os.getenv(
        "MTN_DISBURSEMENT_SECONDARY_KEY"
    )