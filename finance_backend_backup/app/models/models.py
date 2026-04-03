from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import enum


class RoleEnum(str, enum.Enum):
    viewer = "viewer"
    analyst = "analyst"
    admin = "admin"


class StatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False, default=RoleEnum.viewer)
    status = db.Column(db.Enum(StatusEnum), nullable=False, default=StatusEnum.active)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    records = db.relationship("FinancialRecord", backref="created_by_user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class RecordTypeEnum(str, enum.Enum):
    income = "income"
    expense = "expense"


class FinancialRecord(db.Model):
    __tablename__ = "financial_records"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    type = db.Column(db.Enum(RecordTypeEnum), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)  # soft delete
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "amount": float(self.amount),
            "type": self.type.value,
            "category": self.category,
            "date": self.date.isoformat(),
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
