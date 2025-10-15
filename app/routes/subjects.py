# app/routes/subjects.py
from flask import Blueprint, jsonify
import logging
from app.models.mongo import get_subjects_collection
from app.utils.auth_decorator import login_required

subjects_bp = Blueprint('subject', __name__)

@subjects_bp.route('/<semester>', methods=['GET'])
@login_required
def get_subjects(decoded_token,semester):
    try:
        logging.info(f"Fetching subjects for Semester: {semester}")
        subjects = list(get_subjects_collection().find({"sem": {"$lte": semester}}, {"_id": 0}))
        if not subjects:
            return jsonify({"status": "error", "message": "No subjects found"}), 404
        return jsonify({"status": "success", "subjects": subjects}), 200
    except Exception as e:
        logging.error(f"Error in get_subjects API: {e}")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500
