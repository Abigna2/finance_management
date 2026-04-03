from app import db
from app.models.models import User, RoleEnum, StatusEnum


class UserService:

    @staticmethod
    def get_all_users():
        """Return all users."""
        return User.query.all()

    @staticmethod
    def get_user_by_id(user_id):
        """Return a user by ID or None."""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email):
        """Return a user by email or None."""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def create_user(data):
        """
        Validate and create a new user.
        Raises ValueError on invalid or duplicate input.
        """
        required = ["name", "email", "password"]
        for field in required:
            if not data.get(field):
                raise ValueError(f"'{field}' is required")

        if len(data["password"]) < 6:
            raise ValueError("Password must be at least 6 characters")

        if User.query.filter_by(email=data["email"]).first():
            raise ValueError("Email already registered")

        role_value = data.get("role", "viewer")
        if role_value not in [r.value for r in RoleEnum]:
            raise ValueError("Invalid role. Choose from: viewer, analyst, admin")

        user = User(
            name=data["name"],
            email=data["email"],
            role=RoleEnum(role_value)
        )
        user.set_password(data["password"])

        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_role(user_id, new_role):
        """
        Update a user's role.
        Returns updated user or None if not found. Raises ValueError on bad role.
        """
        if new_role not in [r.value for r in RoleEnum]:
            raise ValueError("Invalid role. Choose from: viewer, analyst, admin")

        user = User.query.get(user_id)
        if not user:
            return None

        user.role = RoleEnum(new_role)
        db.session.commit()
        return user

    @staticmethod
    def update_status(user_id, new_status):
        """
        Activate or deactivate a user.
        Returns updated user or None if not found. Raises ValueError on bad status.
        """
        if new_status not in [s.value for s in StatusEnum]:
            raise ValueError("Invalid status. Choose from: active, inactive")

        user = User.query.get(user_id)
        if not user:
            return None

        user.status = StatusEnum(new_status)
        db.session.commit()
        return user

    @staticmethod
    def verify_login(email, password):
        """
        Validate login credentials.
        Returns user on success, raises ValueError on failure.
        """
        if not email or not password:
            raise ValueError("Email and password are required")

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            raise ValueError("Invalid email or password")

        if user.status.value == "inactive":
            raise PermissionError("Account is inactive. Contact an admin.")

        return user
