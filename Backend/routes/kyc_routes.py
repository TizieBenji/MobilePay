import os
import uuid

from flask import Blueprint, request

from flask_jwt_extended import jwt_required, get_jwt_identity

from werkzeug.utils import secure_filename

from services.kyc_service import create_kyc


kyc_bp = Blueprint("kyc", __name__)

UPLOAD_FOLDER = "uploads/kyc"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@kyc_bp.route("/submit", methods=["POST"])
@jwt_required()
def submit_kyc():

    user_id = int(get_jwt_identity())

    national_id_number = request.form.get("national_id_number")
    document_type = request.form.get("document_type")

    if not national_id_number or not document_type:
        return {
            "success": False,
            "message": "Missing required fields"
        }, 400

    front = request.files.get("front")
    back = request.files.get("back")
    selfie = request.files.get("selfie")

    if not front:
        return {"success": False, "message": "Front document required"}, 400

    if not back:
        return {"success": False, "message": "Back document required"}, 400

    if not selfie:
        return {"success": False, "message": "Selfie required"}, 400

    # Validate file types
    for file, name in [(front, "front"), (back, "back"), (selfie, "selfie")]:
        if file and not allowed_file(file.filename):
            return {
                "success": False,
                "message": f"Invalid file type for {name}"
            }, 400

    def save_file(file):
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)
        return path

    front_path = save_file(front)
    back_path = save_file(back)
    selfie_path = save_file(selfie)

    return create_kyc(
        user_id=user_id,
        national_id_number=national_id_number,
        document_type=document_type,
        front_path=front_path,
        back_path=back_path,
        selfie_path=selfie_path
    )