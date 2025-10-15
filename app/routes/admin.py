from flask import Blueprint, request, jsonify
import logging
from firebase_admin import auth
from app.models.mongo import get_admins_collection, get_collection_map, get_teachers_copy_collection
from app.utils.auth_decorator import login_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/change_admin_password', methods=['POST'])
@login_required
def change_admin_password(decoded_token):
    try:
        admin_email = decoded_token.get("email")
        data = request.json
        hashed_current_password = data.get("hashedCurrentPassword")
        hashed_new_password = data.get("hashedNewPassword")

        if not hashed_current_password or not hashed_new_password:
            return jsonify({"error": "Current password and new password are required"}), 400

        admin = get_admins_collection().find_one({"Email_Id": admin_email})
        if not admin:
            return jsonify({"error": "Admin not found"}), 404

        if admin.get("password") != hashed_current_password:
            return jsonify({"error": "Current password is incorrect"}), 403

        get_admins_collection().update_one(
            {"Email_Id": admin_email},
            {"$set": {"password": hashed_new_password}}
        )

        return jsonify({"message": "Password updated successfully"}), 200

    except Exception as e:
        logging.error(f"Error updating password: {e}")
        return jsonify({"error": "Internal server error"}), 500


@admin_bp.route('/upload', methods=['POST'])
@login_required
def upload_data(decoded_token):
    try:
        admin_email = decoded_token.get("email")
        req_data = request.json
        data_type = req_data.get("type")
        parsed_data = req_data.get("parsedData", [])

        if not data_type or not parsed_data:
            return jsonify({"error": "Missing required parameters"}), 400
        
        collection_map = get_collection_map()

        if data_type not in collection_map:
            return jsonify({"success": False, "message": "Invalid type"}), 400

        if not isinstance(parsed_data, list) or len(parsed_data) == 0:
            return jsonify({"success": False, "message": "Invalid or empty data"}), 400

        admin = get_admins_collection().find_one({"Email_Id": admin_email})
        if not admin:
            return jsonify({"success": False, "message": "Admin not found"}), 404

        col = collection_map[data_type]
        if(data_type=="Teachers"):
            get_teachers_copy_collection.insert_many(parsed_data)

        col.delete_many({})
    
        col.insert_many(parsed_data)

        return jsonify({"success": True, "message": f"{data_type} uploaded successfully"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
