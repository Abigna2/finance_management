from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.models import User, RoleEnum

ROLE_HIERARCHY = {
    RoleEnum.viewer: 1,
    RoleEnum.analyst: 2,
    RoleEnum.admin: 3
}


def require_role(*allowed_roles):
    """
    Decorator to restrict access to specific roles.
    Usage: @require_role("admin") or @require_role("admin", "analyst")
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return jsonify({"error": "User not found"}), 404

            if user.status.value == "inactive":
                return jsonify({"error": "Account is inactive. Contact admin."}), 403

            if user.role.value not in allowed_roles:
                return jsonify({
                    "error": "Access denied",
                    "message": f"This action requires one of the following roles: {', '.join(allowed_roles)}"
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user():
    """Helper to get the current logged-in user object."""
    user_id = get_jwt_identity()
    return User.query.get(user_id)
