from flask import Blueprint, request, jsonify
from app.services.record_service import RecordService
from app.middleware.auth_middleware import require_role, get_current_user

records_bp = Blueprint("records", __name__)


@records_bp.route("/", methods=["GET"])
@require_role("viewer", "analyst", "admin")
def get_records():
    """
    Get all financial records with optional filters and pagination
    ---
    tags:
      - Financial Records
    security:
      - Bearer: []
    parameters:
      - in: query
        name: type
        type: string
        enum: [income, expense]
      - in: query
        name: category
        type: string
      - in: query
        name: start_date
        type: string
        description: Format YYYY-MM-DD
      - in: query
        name: end_date
        type: string
        description: Format YYYY-MM-DD
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 10
    responses:
      200:
        description: Paginated list of financial records
      400:
        description: Invalid filter parameters
    """
    try:
        paginated = RecordService.get_filtered_records(
            record_type=request.args.get("type"),
            category=request.args.get("category"),
            start_date=request.args.get("start_date"),
            end_date=request.args.get("end_date"),
            page=request.args.get("page", 1, type=int),
            per_page=request.args.get("per_page", 10, type=int)
        )
        return jsonify({
            "records": [r.to_dict() for r in paginated.items],
            "pagination": {
                "page": paginated.page,
                "per_page": paginated.per_page,
                "total": paginated.total,
                "pages": paginated.pages,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev
            }
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@records_bp.route("/<int:record_id>", methods=["GET"])
@require_role("viewer", "analyst", "admin")
def get_record(record_id):
    """
    Get a single financial record by ID
    ---
    tags:
      - Financial Records
    security:
      - Bearer: []
    parameters:
      - in: path
        name: record_id
        type: integer
        required: true
    responses:
      200:
        description: Financial record details
      404:
        description: Record not found
    """
    record = RecordService.get_record_by_id(record_id)
    if not record:
        return jsonify({"error": "Record not found"}), 404
    return jsonify({"record": record.to_dict()}), 200


@records_bp.route("/", methods=["POST"])
@require_role("admin")
def create_record():
    """
    Create a new financial record (Admin only)
    ---
    tags:
      - Financial Records
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [amount, type, category, date]
          properties:
            amount:
              type: number
              example: 5000.00
            type:
              type: string
              enum: [income, expense]
            category:
              type: string
              example: Salary
            date:
              type: string
              example: "2026-04-01"
            notes:
              type: string
              example: Monthly salary credit
    responses:
      201:
        description: Record created successfully
      400:
        description: Validation error
    """
    try:
        user = get_current_user()
        record = RecordService.create_record(request.get_json(), created_by_id=user.id)
        return jsonify({"message": "Record created successfully", "record": record.to_dict()}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@records_bp.route("/<int:record_id>", methods=["PUT"])
@require_role("admin")
def update_record(record_id):
    """
    Update an existing financial record (Admin only)
    ---
    tags:
      - Financial Records
    security:
      - Bearer: []
    parameters:
      - in: path
        name: record_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            amount:
              type: number
            type:
              type: string
              enum: [income, expense]
            category:
              type: string
            date:
              type: string
            notes:
              type: string
    responses:
      200:
        description: Record updated
      400:
        description: Validation error
      404:
        description: Record not found
    """
    try:
        record = RecordService.update_record(record_id, request.get_json())
        if not record:
            return jsonify({"error": "Record not found"}), 404
        return jsonify({"message": "Record updated successfully", "record": record.to_dict()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@records_bp.route("/<int:record_id>", methods=["DELETE"])
@require_role("admin")
def delete_record(record_id):
    """
    Soft delete a financial record (Admin only)
    ---
    tags:
      - Financial Records
    security:
      - Bearer: []
    parameters:
      - in: path
        name: record_id
        type: integer
        required: true
    responses:
      200:
        description: Record deleted
      404:
        description: Record not found
    """
    deleted = RecordService.delete_record(record_id)
    if not deleted:
        return jsonify({"error": "Record not found"}), 404
    return jsonify({"message": "Record deleted successfully"}), 200
