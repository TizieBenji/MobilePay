# services/mtn_token_service.py

import time
from providers.mtn.auth_service import generate_token


_token_cache = {}


def get_valid_token(user_id, product_type="COLLECTION"):

    key = f"{user_id}:{product_type}"
    now = time.time()

    cached = _token_cache.get(key)

    if cached and now < cached["expires_at"]:
        return cached["token"]

    token_response = generate_token(user_id, product_type)

    token = token_response["access_token"]
    expires_in = token_response.get("expires_in", 3600)

    _token_cache[key] = {
        "token": token,
        "expires_at": now + expires_in - 60
    }

    return token