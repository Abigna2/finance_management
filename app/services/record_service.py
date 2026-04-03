from app import db
from app.models.models import FinancialRecord, RecordTypeEnum
from datetime import datetime


class RecordService:

    @staticmethod
    def get_filtered_records(record_type=None, category=None, start_date=None, end_date=None, page=1, per_page=10):
        """
        Fetch financial records with optional filters and pagination.
        Returns a pagination object or raises ValueError on bad input.
        """
        query = FinancialRecord.query.filter_by(is_deleted=False)

        if record_type:
            if record_type not in [r.value for r in RecordTypeEnum]:
                raise ValueError("Invalid type. Use 'income' or 'expense'")
            query = query.filter_by(type=RecordTypeEnum(record_type))

        if category:
            query = query.filter(FinancialRecord.category.ilike(f"%{category}%"))

        if start_date:
            try:
                query = query.filter(FinancialRecord.date >= datetime.strptime(start_date, "%Y-%m-%d").date())
            except ValueError:
                raise ValueError("Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                query = query.filter(FinancialRecord.date <= datetime.strptime(end_date, "%Y-%m-%d").date())
            except ValueError:
                raise ValueError("Invalid end_date format. Use YYYY-MM-DD")

        per_page = min(per_page, 100)
        return query.order_by(FinancialRecord.date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def get_record_by_id(record_id):
        """Fetch a single non-deleted record by ID. Returns None if not found."""
        return FinancialRecord.query.filter_by(id=record_id, is_deleted=False).first()

    @staticmethod
    def create_record(data, created_by_id):
        """
        Validate and create a new financial record.
        Raises ValueError on invalid input.
        """
        required = ["amount", "type", "category", "date"]
        for field in required:
            if data.get(field) is None:
                raise ValueError(f"'{field}' is required")

        if data["type"] not in [r.value for r in RecordTypeEnum]:
            raise ValueError("Invalid type. Use 'income' or 'expense'")

        try:
            amount = float(data["amount"])
            if amount <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError("Amount must be a positive number")

        try:
            date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")

        record = FinancialRecord(
            amount=amount,
            type=RecordTypeEnum(data["type"]),
            category=data["category"].strip(),
            date=date,
            notes=data.get("notes", ""),
            created_by=created_by_id
        )

        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def update_record(record_id, data):
        """
        Apply partial updates to a record.
        Raises ValueError on bad input, or None if record not found.
        """
        record = FinancialRecord.query.filter_by(id=record_id, is_deleted=False).first()
        if not record:
            return None

        if "amount" in data:
            try:
                amount = float(data["amount"])
                if amount <= 0:
                    raise ValueError()
                record.amount = amount
            except (ValueError, TypeError):
                raise ValueError("Amount must be a positive number")

        if "type" in data:
            if data["type"] not in [r.value for r in RecordTypeEnum]:
                raise ValueError("Invalid type. Use 'income' or 'expense'")
            record.type = RecordTypeEnum(data["type"])

        if "category" in data:
            record.category = data["category"].strip()

        if "date" in data:
            try:
                record.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")

        if "notes" in data:
            record.notes = data["notes"]

        db.session.commit()
        return record

    @staticmethod
    def delete_record(record_id):
        """
        Soft delete a record. Returns True if deleted, False if not found.
        """
        record = FinancialRecord.query.filter_by(id=record_id, is_deleted=False).first()
        if not record:
            return False

        record.is_deleted = True
        db.session.commit()
        return True
