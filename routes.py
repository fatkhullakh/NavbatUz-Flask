from flask import Blueprint, request, jsonify
from models import db, User
# from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash, check_password_hash

from flask import request, jsonify
from functools import wraps
import jwt
import datetime
import os


# Create a Blueprint instead of directly using 'app'
auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.environ.get('SECRET_KEY', "e600375948b530326802ac7271b5afe0f16819955f0118f8d827a4d6137eaa01")

@auth_bp.route('/api/register', methods=['POST'])
def register():
    print("📌 Received a request!")  # Debugging

    data = request.json
    if not data.get("name") or not data.get("email") or not data.get("password"):
        print("❌ Missing required fields!")
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = generate_password_hash(data["password"])
    new_user = User(name=data["name"], email=data["email"], password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    print("✅ User registered successfully!")
    return jsonify({"message": "User registered successfully!"})

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate JWT Token
    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)},
        SECRET_KEY,
        algorithm="HS256"
    )
    return jsonify({"message": "Login successful!", "token": token})

# Middleware to protect routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])
            if not current_user:
                return jsonify({"error": "Invalid token!"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@auth_bp.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    })

