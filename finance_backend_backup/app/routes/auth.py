from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.services.user_service import UserService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [name, email, password]
          properties:
            name:
              type: string
              example: Abigna Katakam
            email:
              type: string
              example: abigna@example.com
            password:
              type: string
              example: securepassword123
            role:
              type: string
              enum: [viewer, analyst, admin]
              example: viewer
    responses:
      201:
        description: User registered successfully
      400:
        description: Validation error or email already exists
    """
    data = request.get_json()
    try:
        user = UserService.create_user(data)
        return jsonify({"message": "User registered successfully", "user": user.to_dict()}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login and receive a JWT token
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [email, password]
          properties:
            email:
              type: string
              example: abigna@example.com
            password:
              type: string
              example: securepassword123
    responses:
      200:
        description: Login successful, returns JWT token
      401:
        description: Invalid credentials
      403:
        description: Account inactive
    """
    data = request.get_json()
    try:
        user = UserService.verify_login(data.get("email"), data.get("password"))
        token = create_access_token(identity=user.id)
        return jsonify({
            "message": "Login successful",
            "access_token": token,
            "user": user.to_dict()
        }), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
