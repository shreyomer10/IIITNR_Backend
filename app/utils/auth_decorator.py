# app/utils/auth_decorator.py
import functools
import logging
from flask import request, jsonify ,g
from firebase_admin import auth as firebase_auth

def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header is missing"}), 401

        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            return jsonify({"error": "Invalid Authorization header format. Must be: Bearer <token>"}), 401

        token = parts[1]
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            # You can pass the token to kwargs if you want to access it in the view function
            kwargs['decoded_token'] = decoded_token
        except Exception as e:
            logging.error(f"Error verifying Firebase token: {e}")
            return jsonify({"error": "Invalid or expired token"}), 401

        return func(*args, **kwargs)
    return wrapper
