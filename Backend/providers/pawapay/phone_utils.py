import re, math
from providers.pawapay import client
from providers.pawapay.config import PawaPayConfig


def normalize_msisdn(raw_phone: str) -> str | None:
    """
    Normalize a phone number to the 237XXXXXXXXX format PawaPay expects.
    Accepts: +237xxxxxxxxx / 237xxxxxxxxx / xxxxxxxxx (9 digits)
    Returns None if invalid.

    Cameroon mobile numbers are 9 national digits beginning with 6
    (e.g. 6XXXXXXXX); landlines and other ranges cannot hold a mobile-money
    account, so we reject anything whose national part does not start with 6.
    """
    digits = re.sub(r"\D", "", raw_phone)

    if digits.startswith("237"):
        msisdn = digits
    elif len(digits) == 9:
        msisdn = "237" + digits
    else:
        return None

    if len(msisdn) != 12:
        return None

    # National part (after the 237 country code) must be a mobile number.
    if msisdn[3] != "6":
        return None

    return msisdn


def detect_correspondent(raw_phone: str) -> str | None:
    """
    Return the PawaPay correspondent ('MTN_MOMO_CMR' / 'ORANGE_CMR') for a
    Cameroon number, or None if it is invalid or cannot be resolved.

    Routing is delegated to PawaPay's predict-correspondent service rather than
    a local prefix table. The previous static table was wrong for ~30% of the
    Cameroon mobile range (whole MTN blocks rejected, others routed to the wrong
    operator) and could never track number portability, where the operator is
    determined by the full MSISDN — not a fixed prefix. PawaPay is the source of
    truth, so we ask it directly and avoid misrouting money.
    """
    msisdn = normalize_msisdn(raw_phone)
    if not msisdn:
        return None

    return client.predict_correspondent(msisdn)


def validate_amount_for_cameroon(amount, correspondent: str | None = None) -> tuple[bool, str]:
    """
    XAF must be a positive whole number within the operator's allowed range.
    Returns (is_valid, error_message).

    The cap is operator-specific (PawaPay rejects out-of-range amounts), so when
    the correspondent is known we enforce that operator's limit; otherwise we
    fall back to the highest cap across CMR operators as a coarse bound.
    """
    try:
        numeric = float(amount)
    except (TypeError, ValueError):
        return False, "Amount must be a number"

    if math.isinf(numeric) or math.isnan(numeric):
        return False, "Amount must be a finite number"

    if numeric <= 0:
        return False, "Amount must be greater than zero"

    if numeric != int(numeric):
        return False, (
            f"XAF does not support decimal amounts. "
            f"Use a whole number (e.g. {int(numeric)})."
        )

    limits = PawaPayConfig.CORRESPONDENT_LIMITS.get(correspondent)
    max_allowed = limits["max"] if limits else PawaPayConfig.MAX_TRANSACTION_LIMIT

    if int(numeric) > max_allowed:
        operator = correspondent or "this operator"
        return False, (
            f"Amount exceeds the maximum allowed per transaction for "
            f"{operator} ({max_allowed:,} XAF)."
        )

    return True, ""
