from flask import Blueprint, request, jsonify
from app.services.dashboard_service import DashboardService
from app.middleware.auth_middleware import require_role

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/summary", methods=["GET"])
@require_role("viewer", "analyst", "admin")
def get_summary():
    """
    Get overall financial summary - total income, expenses, and net balance
    ---
    tags:
      - Dashboard
    security:
      - Bearer: []
    responses:
      200:
        description: Financial summary
    """
    return jsonify(DashboardService.get_summary()), 200


@dashboard_bp.route("/categories", methods=["GET"])
@require_role("viewer", "analyst", "admin")
def get_category_totals():
    """
    Get totals grouped by category
    ---
    tags:
      - Dashboard
    security:
      - Bearer: []
    responses:
      200:
        description: Category-wise totals
    """
    return jsonify({"categories": DashboardService.get_category_totals()}), 200


@dashboard_bp.route("/trends", methods=["GET"])
@require_role("analyst", "admin")
def get_trends():
    """
    Get monthly or weekly income/expense trends (Analyst and Admin only)
    ---
    tags:
      - Dashboard
    security:
      - Bearer: []
    parameters:
      - in: query
        name: period
        type: string
        enum: [monthly, weekly]
        default: monthly
      - in: query
        name: year
        type: integer
        description: Filter by year e.g. 2026
    responses:
      200:
        description: Trend data grouped by period
      400:
        description: Invalid period value
    """
    try:
        trends = DashboardService.get_trends(
            period=request.args.get("period", "monthly"),
            year=request.args.get("year", type=int)
        )
        return jsonify({"period": request.args.get("period", "monthly"), "trends": trends}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@dashboard_bp.route("/recent", methods=["GET"])
@require_role("viewer", "analyst", "admin")
def get_recent_activity():
    """
    Get recent financial activity
    ---
    tags:
      - Dashboard
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        default: 10
    responses:
      200:
        description: Recent records
    """
    records = DashboardService.get_recent_activity(
        limit=request.args.get("limit", 10, type=int)
    )
    return jsonify({"recent_activity": [r.to_dict() for r in records], "count": len(records)}), 200
