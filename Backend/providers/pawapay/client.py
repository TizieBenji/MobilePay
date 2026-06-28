import time, requests, random, logging
from requests.exceptions import (ConnectionError as RequestsConnectionError, Timeout, RequestException)
from providers.pawapay.config import PawaPayConfig

logger = logging.getLogger(__name__)


def _auth_headers() -> dict:
    token = PawaPayConfig.API_TOKEN
    if not token:
        raise RuntimeError("PAWAPAY_API_TOKEN is not set. Add it to your .env file.")
    
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _url(path: str) -> str:
    return f"{PawaPayConfig.base_url()}{path}"


def _parse_response(response: requests.Response) -> dict:
    ok = 200 <= response.status_code < 300
    try:
        data = response.json()
    except ValueError:
        data = {}
    return {
        "ok": ok,
        "status_code": response.status_code,
        "data": data,
        "raw_text": response.text,
    }


def _safe_request(method: str, path: str, **kwargs) -> dict:
    timeout = kwargs.pop("timeout", PawaPayConfig.REQUEST_TIMEOUT_SECONDS)
    url = _url(path)

    try:
        resp = requests.request(method, url, headers=_auth_headers(), timeout=timeout, **kwargs)
        return _parse_response(resp)

    except Timeout:
        logger.error("PawaPay request timed out: %s %s", method, url)
        return {"ok": False, "status_code": 504, "data": {}, "raw_text": "Request timed out", "error": "TIMEOUT"}

    except RequestsConnectionError as exc:
        logger.error("PawaPay connection error: %s %s | %s", method, url, exc)
        return {"ok": False, "status_code": 503, "data": {}, "raw_text": str(exc), "error": "CONNECTION_ERROR"}

    except RequestException as exc:
        logger.error("PawaPay request error: %s %s | %s", method, url, exc)
        return {"ok": False, "status_code": 500, "data": {}, "raw_text": str(exc), "error": "REQUEST_ERROR"}


def get(path: str, params: dict | None = None) -> dict:
    """
    Safe GET with retry + exponential backoff + jitter.
    Jitter prevents all retrying workers from waking at the same moment
    after a shared outage (thundering herd problem).
    """
    max_retries = 3
    backoff = 1.0

    for attempt in range(1, max_retries + 1):
        result = _safe_request("GET", path, params=params)

        if result["ok"] or (400 <= result["status_code"] < 500):
            return result

        if attempt < max_retries:
            # Full jitter: sleep between 0 and backoff seconds
            sleep_time = random.uniform(0, backoff)
            logger.warning("PawaPay GET %s failed (attempt %d/%d, status %d). Retrying in %.1fs...",
                path, attempt, max_retries, result["status_code"], sleep_time,
            )
            time.sleep(sleep_time)
            backoff *= 2  # 1s → 2s → 4s ceiling, jittered

    logger.error("PawaPay GET %s failed after %d attempts.", path, max_retries)
    return result


def post(path: str, payload: dict) -> dict:
    """
    Safe POST — no auto-retry (POST creates resources; caller controls retries
    via stored idempotency key).
    """
    return _safe_request("POST", path, json=payload)


def predict_correspondent(msisdn: str) -> str | None:
    """
    Ask PawaPay which correspondent (mobile money operator) owns an MSISDN.

    This is the authoritative routing source: it accounts for full-number
    operator allocation and mobile number portability, which a static phone
    prefix table cannot. Lookups are idempotent, so we use the retrying GET-
    style behaviour by calling the predict endpoint and treating a 4xx as a
    definitive "cannot resolve".

    Returns the correspondent code (e.g. "MTN_MOMO_CMR") or None.
    """
    result = _safe_request("POST", "/v1/predict-correspondent", json={"msisdn": msisdn})
    if not result["ok"]:
        logger.warning("predict-correspondent could not resolve MSISDN (status %s)", result["status_code"])
        return None
    return result["data"].get("correspondent") or None
