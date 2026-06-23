from database.db import db
from models.kyc import KYC


def create_kyc(
    user_id,
    national_id_number,
    document_type,
    front_path,
    back_path,
    selfie_path
):

    # Validate required fields
    if not national_id_number or not document_type:
        return {
            "success": False,
            "message": "Missing required fields"
        }, 400

    existing = KYC.query.filter_by(user_id=user_id).first()

    # Prevent duplicate PENDING submissions
    if existing and existing.status == "PENDING":
        return {
            "success": False,
            "message": "KYC already under review"
        }, 400

    # If APPROVED, block changes permanently
    if existing and existing.status == "APPROVED":
        return {
            "success": False,
            "message": "KYC already approved"
        }, 403

    # If REJECTED → allow resubmission (update record)
    if existing and existing.status == "REJECTED":
        existing.national_id_number = national_id_number
        existing.document_type = document_type
        existing.document_front = front_path
        existing.document_back = back_path
        existing.selfie_image = selfie_path
        existing.status = "PENDING"
        existing.rejection_reason = None

        db.session.commit()

        return {
            "success": True,
            "message": "KYC resubmitted",
            "status": "PENDING"
        }, 200

    # New KYC submission
    kyc = KYC(
        user_id=user_id,
        national_id_number=national_id_number,
        document_type=document_type,
        document_front=front_path,
        document_back=back_path,
        selfie_image=selfie_path,
        status="PENDING"
    )

    db.session.add(kyc)
    db.session.commit()

    return {
        "success": True,
        "message": "KYC submitted",
        "status": "PENDING"
    }, 201