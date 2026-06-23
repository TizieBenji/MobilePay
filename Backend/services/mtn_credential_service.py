# services/mtn_credential_service.py

from models.mtn_credentials import MTNCredentials


def get_mtn_credential(user_id, product_type="COLLECTION"):

    credential = MTNCredentials.query.filter_by(
        user_id=user_id,
        product_type=product_type
    ).first()

    if not credential:
        return None

    return credential