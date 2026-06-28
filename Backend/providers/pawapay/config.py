import os
from dotenv import load_dotenv

load_dotenv()


class PawaPayConfig:

    ENVIRONMENT: str = os.getenv("PAWAPAY_ENVIRONMENT", "sandbox")
    API_TOKEN: str | None = os.getenv("PAWAPAY_API_TOKEN")

    SANDBOX_BASE_URL = "https://api.sandbox.pawapay.io"
    PRODUCTION_BASE_URL = "https://api.pawapay.io"

    COUNTRY = "CMR"
    CURRENCY = "XAF"

    # Per-correspondent transaction limits (XAF), sourced from PawaPay's active
    # configuration for Cameroon (GET /v1/active-conf). PawaPay rejects any
    # amount outside these bounds, so we validate against them before calling
    # the API. Caps differ by operator (Orange is lower than MTN), so the cap
    # must be looked up by correspondent — not a single global value.
    CORRESPONDENT_LIMITS = {
        "MTN_MOMO_CMR": {"min": 1, "max": 1_000_000},
        "ORANGE_CMR": {"min": 1, "max": 500_000},
    }

    # Highest cap across all CMR operators — a coarse outer bound used before
    # the correspondent is known. The precise per-operator cap is enforced
    # afterwards, once detect_correspondent has resolved the network.
    MAX_TRANSACTION_LIMIT = max(limit["max"] for limit in CORRESPONDENT_LIMITS.values())

    REQUEST_TIMEOUT_SECONDS = 30
    POLL_MAX_ATTEMPTS = 10
    POLL_INTERVAL_SECONDS = 5

    @classmethod
    def base_url(cls) -> str:
        if cls.ENVIRONMENT == "production":
            return cls.PRODUCTION_BASE_URL
        return cls.SANDBOX_BASE_URL

    @classmethod
    def reload(cls) -> None:
        """Re-read env vars without restarting the process. Call after os.environ changes."""
        cls.ENVIRONMENT = os.getenv("PAWAPAY_ENVIRONMENT", "sandbox")
        cls.API_TOKEN = os.getenv("PAWAPAY_API_TOKEN")
