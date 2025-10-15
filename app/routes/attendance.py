# app/routes/attendance.py
from flask import Blueprint, request, jsonify
import json
import logging
from datetime import datetime
from app.models.mongo import get_attendance_collection, get_attendance_string_collection,get_subjects_collection
from app.routes.utils import get_all_students_for_subject  # helper function
from app.utils.auth_decorator import login_required
attendance_bp = Blueprint('attendance', __name__)



@attendance_bp.route('/student_attendance', methods=['POST'])
@login_required
def get_attendance(decoded_token):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request body"}), 400
        batch_session = data.get("batchSession")
        course_code = data.get("courseCode")
        student_branch = data.get("branch")
        if not all([batch_session, course_code, student_branch]):
            return jsonify({"error": "Missing parameters"}), 400
        subject = get_subjects_collection().find_one({"subjectId": course_code}, {"_id": 0})
        if not subject:
            return jsonify({"error": "Subject not found"}), 404
        subject_branch = subject["Branch"]
        query = {"batchSession": batch_session, "coursecode": course_code}
        if subject_branch != "0":
            query["branch"] = student_branch
        attendance_docs = list(get_attendance_collection().find(query, {"_id": 0}))
        return jsonify({"status": "success", "data": attendance_docs}), 200
    except Exception as e:
        logging.error(f"Error fetching attendance: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@attendance_bp.route('/save_attendance', methods=['POST'])
@login_required
def save_attendance(decoded_token):
    try:
        req_data = request.json
        required_fields = ["coursecode", "coursename", "date", "absentees", "session", "branch", "batchSession"]
        if not all(field in req_data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        coursecode = req_data["coursecode"]
        coursename = req_data["coursename"]
        date = req_data["date"]
        absentees = req_data["absentees"]
        session = int(req_data["session"])
        branch = req_data["branch"]
        batchSession = req_data["batchSession"]
        attendance_data = {
            "coursecode": coursecode,
            "coursename": coursename,
            "date": date,
            "absentees": absentees,
            "session": session,
            "branch": branch,
            "batchSession": batchSession
        }
        get_attendance_collection().insert_one(attendance_data)
        attendance_string_doc = get_attendance_string_collection().find_one({
            "subject code": coursecode,
            "batchSession": batchSession,
            "Branch": branch
        })
        if attendance_string_doc:
            existing_attendance = attendance_string_doc.get("attendance string", "")
            updated_attendance = {}
            if existing_attendance:
                for entry in existing_attendance.split():
                    admission_no, classes_present, total_classes = entry.split(',')
                    updated_attendance[admission_no] = [int(classes_present), int(total_classes)]
            for admission_no in updated_attendance:
                updated_attendance[admission_no][1] += session
            for admission_no in updated_attendance:
                if admission_no not in absentees:
                    updated_attendance[admission_no][0] += session
            new_attendance_string = " ".join(f"{adm},{data[0]},{data[1]}" for adm, data in updated_attendance.items())
            get_attendance_string_collection().update_one(
                {"_id": attendance_string_doc["_id"]},
                {"$set": {"attendance string": new_attendance_string}}
            )
        else:
            student_list = get_all_students_for_subject(coursecode, batchSession, branch)
            new_attendance_string = " ".join(f"{student},{0 if student in absentees else session},{session}" for student in student_list)
            new_attendance_data = {
                "Branch": branch,
                "subject code": coursecode,
                "subject name": coursename,
                "batchSession": batchSession,
                "attendance string": new_attendance_string
            }
            get_attendance_string_collection().insert_one(new_attendance_data)
        return jsonify({"status": "success", "message": "Attendance saved successfully"}), 200
    except Exception as e:
        logging.error(f"Error saving attendance: {str(e)}")
        return jsonify({"status": "error", "message": f"Internal Server Error: {str(e)}"}), 500

@attendance_bp.route('/update_attendance', methods=['POST'])
@login_required
def update_attendance(decoded_token):
    try:
        req_data = request.json
        required_fields = ["coursecode", "date", "absentees", "session", "branch", "batchSession"]
        if not all(field in req_data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        coursecode = req_data["coursecode"]
        date = req_data["date"]
        absentees = req_data["absentees"]
        new_session = int(req_data["session"])
        branch = req_data["branch"]
        batchSession = req_data["batchSession"]
        attendance_record = get_attendance_collection().find_one({
            "coursecode": coursecode,
            "date": date,
            "branch": branch,
            "batchSession": batchSession
        })
        if not attendance_record:
            return jsonify({"status": "error", "message": "Attendance record not found"}), 404
        old_session = attendance_record["session"]
        previous_absentees = set(attendance_record["absentees"])
        new_absentees = set(absentees)
        get_attendance_collection().update_one(
            {"_id": attendance_record["_id"]},
            {"$set": {"absentees": absentees, "session": new_session}}
        )
        attendance_string_doc = get_attendance_string_collection().find_one({
            "subject code": coursecode,
            "batchSession": batchSession,
            "Branch": branch
        })
        if not attendance_string_doc:
            return jsonify({"status": "error", "message": "Attendance string document not found"}), 404
        existing_attendance = attendance_string_doc.get("attendance string", "")
        updated_attendance = {}
        if existing_attendance:
            for entry in existing_attendance.split():
                admission_no, classes_present, total_classes = entry.split(',')
                updated_attendance[admission_no] = [int(classes_present), int(total_classes)]
        if new_session != old_session:
            session_diff = new_session - old_session
            for admission_no in updated_attendance:
                updated_attendance[admission_no][1] += session_diff
        for admission_no in updated_attendance:
            if admission_no in previous_absentees and admission_no not in new_absentees:
                updated_attendance[admission_no][0] += new_session
            elif admission_no not in previous_absentees and admission_no in new_absentees:
                updated_attendance[admission_no][0] -= old_session
        new_attendance_string = " ".join(f"{adm},{data[0]},{data[1]}" for adm, data in updated_attendance.items())
        get_attendance_string_collection().update_one(
            {"_id": attendance_string_doc["_id"]},
            {"$set": {"attendance string": new_attendance_string}}
        )
        return jsonify({"status": "success", "message": "Attendance updated successfully"}), 200
    except Exception as e:
        logging.error(f"Error updating attendance: {str(e)}")
        return jsonify({"status": "error", "message": f"Internal Server Error: {str(e)}"}), 500

@attendance_bp.route('/get_attendance_record', methods=['POST'])
@login_required
def get_attendance_record(decoded_token):
    try:
        data = request.get_json()
        coursecode = data.get('coursecode')
        date = data.get('date')
        batchSession = data.get('batchSession')
        branch = data.get('branch')
        if not all([coursecode, date, batchSession, branch]):
            return jsonify({"status": "error", "message": "Missing required parameters"}), 400
        query = {
            "coursecode": coursecode,
            "batchSession": batchSession,
            "branch": branch,
            "date": {"$regex": f"^{date}"}
        }
        attendance_records = list(get_attendance_collection().find(query, {"_id": 0}))
        attendance_string_record = get_attendance_string_collection().find_one({
            "subject code": coursecode,
            "batchSession": batchSession,
            "Branch": branch
        }, {"_id": 0})
        if attendance_records and attendance_string_record:
            return jsonify({"status": "success", "data": attendance_records, "data2": attendance_string_record.get("attendance string", "")}), 200
        elif not attendance_records:
            return jsonify({"status": "error", "message": "No attendance records found"}), 404
        else:
            return jsonify({"status": "error", "message": "No attendance string found"}), 404
    except Exception as e:
        logging.error(f"Error fetching attendance records: {e}")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500

@attendance_bp.route('/download_report', methods=['POST'])
@login_required
def downloadReport(decoded_token):
    try:
        data = request.get_json()
        coursecode = data.get('coursecode')
        batchSession = data.get('batchSession')
        branch = data.get('branch')
        if not all([coursecode, batchSession, branch]):
            return jsonify({"status": "error", "message": "Missing required parameters"}), 400
        query = {"coursecode": coursecode, "batchSession": batchSession, "branch": branch}
        attendance_records = list(get_attendance_collection().find(query, {"_id": 0}))
        attendance_string_record = get_attendance_string_collection().find_one({
            "subject code": coursecode,
            "batchSession": batchSession,
            "Branch": branch
        }, {"_id": 0})
        if attendance_records and attendance_string_record:
            return jsonify({"status": "success", "data": attendance_records, "data2": attendance_string_record.get("attendance string", "")}), 200
        elif not attendance_records:
            return jsonify({"status": "error", "message": "No attendance records found"}), 404
        else:
            return jsonify({"status": "error", "message": "No attendance string found"}), 404
    except Exception as e:
        logging.error(f"Error fetching attendance records: {e}")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500
