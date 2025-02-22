from flask import Blueprint, request, jsonify
from models import db, User, Business
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from functools import wraps

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.environ.get('SECRET_KEY') or "e600375948b530326802ac7271b5afe0f16819955f0118f8d827a4d6137eaa01"

# Middleware to Protect Routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            token = token.split(" ")[1]  # Remove 'Bearer' from token
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

# User Registration
@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = generate_password_hash(data["password"])
    new_user = User(name=data["name"], email=data["email"], password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"})

# User Login
@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
        SECRET_KEY,
        algorithm="HS256"
    )
    return jsonify({"message": "Login successful!", "token": token})

# Get User Profile (Protected)
@auth_bp.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    })

# Business Registration (Protected)
@auth_bp.route('/api/business', methods=['POST'])
@token_required
def register_business(current_user):
    data = request.json
    if not data.get("name") or not data.get("category") or not data.get("address") or not data.get("phone"):
        return jsonify({"error": "Missing required fields"}), 400

    new_business = Business(
        name=data["name"],
        category=data["category"],
        address=data["address"],
        phone=data["phone"],
        user_id=current_user.id
    )

    db.session.add(new_business)
    db.session.commit()

    return jsonify({"message": "Business registered successfully!"})
