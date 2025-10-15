# app/routes/students.py
from flask import Blueprint, request, jsonify
import logging
from app.models.mongo import get_teachers_copy_collection, get_students_collection, get_admins_collection, get_subjects_collection
from app.utils.auth_decorator import login_required
student_bp = Blueprint('student', __name__)


@student_bp.route('/get_students/<subject_code>', methods=['GET'])
@login_required
def get_students(decoded_token,subject_code):
    try:
        logging.info(f"Fetching students for Subject Code: {subject_code}")
        subject = get_subjects_collection().find_one({"subjectId": subject_code}, {"_id": 0})
        if not subject:
            return jsonify({"status": "error", "message": "Subject not found"}), 404
        sem = int(subject["sem"])
        branch = subject["Branch"]
        students = list(get_students_collection().find({
            "Course_Code": subject_code,
            "Course_Status": "New",
            "Current_Term": f"Semester {sem}"
        }, {"_id": 0}))
        response = {
            "status": "success",
            "students": students,
            "branch": branch
        }
        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error in get_students API: {e}")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500
