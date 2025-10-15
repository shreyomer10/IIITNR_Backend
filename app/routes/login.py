from flask import Blueprint, request, jsonify
import logging
from app.models.mongo import get_teachers_copy_collection, get_students_collection, get_admins_collection

login_bp = Blueprint('login', __name__)

@login_bp.route('/<role>/<email>', methods=['GET'])

def check_login(role, email):
    try:
        logging.info(f"Checking login: Role = {role}, Email = {email}")

        if role == "teacher":
            collection = get_teachers_copy_collection()
            user = collection.find({"Email": email}, {"_id": 0})
        elif role == "student":
            collection = get_students_collection()
            user = collection.find({"Email_Id": email}, {"_id": 0})
        elif role == "admin":
            collection = get_admins_collection()
            user = collection.find_one({"Email_Id": email}, {"_id": 0, "password": 0})
        else:
            return jsonify({"status": "error", "message": "Invalid role"}), 400

        if user:
            return jsonify({"status": "success", "data": user}), 200
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404
    except Exception as e:
        logging.error(f"Unexpected Error in login API: {e}")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500
