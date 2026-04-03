from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.user_service import UserService
from app.middleware.auth_middleware import require_role, get_current_user

users_bp = Blueprint("users", __name__)


@users_bp.route("/", methods=["GET"])
@require_role("admin", "analyst")
def get_all_users():
    """
    Get all users (Admin and Analyst only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: List of all users
    """
    users = UserService.get_all_users()
    return jsonify({"users": [u.to_dict() for u in users], "total": len(users)}), 200


@users_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    """
    Get the currently logged-in user's profile
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: Current user profile
    """
    user = get_current_user()
    return jsonify({"user": user.to_dict()}), 200


@users_bp.route("/<int:user_id>", methods=["GET"])
@require_role("admin", "analyst")
def get_user(user_id):
    """
    Get a specific user by ID (Admin and Analyst only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
    responses:
      200:
        description: User details
      404:
        description: User not found
    """
    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200


@users_bp.route("/<int:user_id>/role", methods=["PATCH"])
@require_role("admin")
def update_user_role(user_id):
    """
    Update a user's role (Admin only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [role]
          properties:
            role:
              type: string
              enum: [viewer, analyst, admin]
    responses:
      200:
        description: Role updated
      400:
        description: Invalid role
      404:
        description: User not found
    """
    data = request.get_json()
    try:
        user = UserService.update_role(user_id, data.get("role"))
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "Role updated successfully", "user": user.to_dict()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/<int:user_id>/status", methods=["PATCH"])
@require_role("admin")
def update_user_status(user_id):
    """
    Activate or deactivate a user (Admin only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [status]
          properties:
            status:
              type: string
              enum: [active, inactive]
    responses:
      200:
        description: Status updated
      404:
        description: User not found
    """
    data = request.get_json()
    try:
        user = UserService.update_status(user_id, data.get("status"))
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "Status updated successfully", "user": user.to_dict()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
