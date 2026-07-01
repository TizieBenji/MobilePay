from database.db import db
from models.kyc import KYC


def create_kyc(
    user_id,
    national_id_number,
    document_type,
    front_path,
    back_path,
    selfie_path,
    residential_address=None
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
        existing.residential_address = residential_address
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
        residential_address=residential_address,
        status="PENDING"
    )

    db.session.add(kyc)
    db.session.commit()

    return {
        "success": True,
        "message": "KYC submitted",
        "status": "PENDING"
    }, 201


def list_pending_kyc():
    records = KYC.query.filter_by(status="PENDING").order_by(KYC.created_at.asc()).all()

    return {
        "success": True,
        "records": [_serialize_kyc(record) for record in records]
    }, 200


def approve_kyc(kyc_id):
    kyc = KYC.query.get(kyc_id)

    if not kyc:
        return {"success": False, "message": "KYC record not found"}, 404

    if kyc.status == "APPROVED":
        return {"success": False, "message": "KYC already approved"}, 400

    kyc.status = "APPROVED"
    kyc.rejection_reason = None
    db.session.commit()

    return {"success": True, "message": "KYC approved", "status": "APPROVED"}, 200


def reject_kyc(kyc_id, rejection_reason=None):
    kyc = KYC.query.get(kyc_id)

    if not kyc:
        return {"success": False, "message": "KYC record not found"}, 404

    if kyc.status == "APPROVED":
        return {"success": False, "message": "Cannot reject an already approved KYC"}, 400

    if not rejection_reason or not rejection_reason.strip():
        return {"success": False, "message": "Rejection reason is required"}, 400

    kyc.status = "REJECTED"
    kyc.rejection_reason = rejection_reason.strip()
    db.session.commit()

    return {"success": True, "message": "KYC rejected", "status": "REJECTED"}, 200


def _serialize_kyc(kyc):
    return {
        "id": kyc.id,
        "user_id": kyc.user_id,
        "national_id_number": kyc.national_id_number,
        "document_type": kyc.document_type,
        "residential_address": kyc.residential_address,
        "document_front": kyc.document_front,
        "document_back": kyc.document_back,
        "selfie_image": kyc.selfie_image,
        "status": kyc.status,
        "rejection_reason": kyc.rejection_reason,
        "created_at": kyc.created_at.isoformat() if kyc.created_at else None
    }