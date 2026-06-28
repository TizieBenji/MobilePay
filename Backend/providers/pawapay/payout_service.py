import re, time, logging
from datetime import datetime, timezone

from providers.pawapay import client
from providers.pawapay.config import PawaPayConfig
from providers.pawapay.phone_utils import (
    normalize_msisdn,
    detect_correspondent,
    validate_amount_for_cameroon,
)

logger = logging.getLogger(__name__)


def initiate_payout(payout_id: str, phone: str, amount, statement_description: str = "MobilePay payout") -> dict:
    
    msisdn = normalize_msisdn(phone)
    
    if not msisdn:
        return _error(payout_id, f"Invalid phone number: {phone}")

    correspondent = detect_correspondent(phone)
    
    if not correspondent:
        return _error(payout_id, f"Could not determine MTN/Orange network for {phone}.")

    amount_valid, amount_err = validate_amount_for_cameroon(amount, correspondent)

    if not amount_valid:
        return _error(payout_id, amount_err)

    desc = _sanitize_description(statement_description)

    payload = {
        "payoutId": payout_id,
        "amount": str(int(amount)),
        "currency": PawaPayConfig.CURRENCY,
        "country": PawaPayConfig.COUNTRY,
        "correspondent": correspondent,
        "recipient": {"type": "MSISDN", "address": {"value": msisdn}},
        "customerTimestamp": _now_iso(),
        "statementDescription": desc,
        "metadata": [{"fieldName": "payoutId", "fieldValue": payout_id}],
    }

    logger.info("Initiating PawaPay payout | id=%s | correspondent=%s | amount=%s XAF", payout_id, correspondent, int(amount),)

    result = client.post("/payouts", payload)
    data = result.get("data", {})
    pawa_status = data.get("status", "")

    if result["ok"] and pawa_status in ("ACCEPTED", "DUPLICATE_IGNORED", "ENQUEUED"):
        logger.info("PawaPay payout %s: %s", payout_id, pawa_status)
        return {
            "ok": True,
            "payout_id": payout_id,
            "status": pawa_status,
            "correspondent": correspondent,
            "error_detail": None,
            "raw": data,
        }

    rejection = data.get("rejectionReason", {})
    detail = (rejection.get("rejectionCode") or result.get("error") or result.get("raw_text") or "Unknown error")
    
    logger.warning("PawaPay payout %s rejected/failed: %s", payout_id, detail)
    
    return {
        "ok": False,
        "payout_id": payout_id,
        "status": pawa_status or "ERROR",
        "correspondent": correspondent,
        "error_detail": detail,
        "raw": data,
    }


def check_payout_status(payout_id: str) -> dict:
    result = client.get(f"/payouts/{payout_id}") or {}
    data = result.get("data", {})
    
    if isinstance(data, list) and len(data) > 0:
        payout_info = data[0]
    elif isinstance(data, dict):
        payout_info = data
    else:
        payout_info = {}
    
    pawa_status = payout_info.get("status", "")
    failure = payout_info.get("failureReason", {})
    
    return {
        "ok": result.get("ok", False),
        "payout_id": payout_id,
        "pawa_status": pawa_status or ("ERROR" if not result.get("ok") else "UNKNOWN"),
        "failure_code": failure.get("failureCode"),
        "failure_message": failure.get("failureMessage"),
        "raw": data,
    }


def poll_payout_until_final(payout_id: str) -> dict:
    """ Blocking poll — only use in local dev when webhooks cannot reach your server.
    In production this blocks the Flask worker thread; use a task queue instead.
    """
    max_attempts = PawaPayConfig.POLL_MAX_ATTEMPTS
    interval = PawaPayConfig.POLL_INTERVAL_SECONDS

    for attempt in range(1, max_attempts + 1):
        status_result = check_payout_status(payout_id)
        pawa_status = status_result.get("pawa_status", "")
        logger.info("Poll payout %s [%d/%d]: %s", payout_id, attempt, max_attempts, pawa_status)
        if pawa_status in ("COMPLETED", "FAILED"):
            return status_result
        if attempt < max_attempts:
            time.sleep(interval)

    logger.warning("Polling timed out for payout %s after %d attempts.", payout_id, max_attempts)
    return {
        "ok": False,
        "payout_id": payout_id,
        "pawa_status": "TIMEOUT",
        "failure_code": "POLL_TIMEOUT",
        "failure_message": f"Payout still processing after {max_attempts} polling attempts.",
        "raw": {},
    }


def _error(payout_id: str, detail: str) -> dict:
    return {"ok": False, "payout_id": payout_id, "status": "ERROR", "correspondent": None, "error_detail": detail, "raw": {}}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sanitize_description(desc: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9]", "", desc)
    if len(clean) < 4:
        clean = (clean + "MobilePay payout")[:22]
    return clean[:22]