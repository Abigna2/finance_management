from app import db
from app.models.models import FinancialRecord, RecordTypeEnum
from sqlalchemy import func, extract


class DashboardService:

    @staticmethod
    def get_summary():
        """Return total income, expenses, net balance, and record count."""
        total_income = db.session.query(
            func.coalesce(func.sum(FinancialRecord.amount), 0)
        ).filter(
            FinancialRecord.is_deleted == False,
            FinancialRecord.type == RecordTypeEnum.income
        ).scalar()

        total_expenses = db.session.query(
            func.coalesce(func.sum(FinancialRecord.amount), 0)
        ).filter(
            FinancialRecord.is_deleted == False,
            FinancialRecord.type == RecordTypeEnum.expense
        ).scalar()

        record_count = FinancialRecord.query.filter_by(is_deleted=False).count()

        return {
            "total_income": float(total_income),
            "total_expenses": float(total_expenses),
            "net_balance": float(total_income) - float(total_expenses),
            "record_count": record_count
        }

    @staticmethod
    def get_category_totals():
        """Return income and expense totals grouped by category."""
        results = db.session.query(
            FinancialRecord.category,
            FinancialRecord.type,
            func.sum(FinancialRecord.amount).label("total"),
            func.count(FinancialRecord.id).label("count")
        ).filter(
            FinancialRecord.is_deleted == False
        ).group_by(
            FinancialRecord.category, FinancialRecord.type
        ).order_by(
            func.sum(FinancialRecord.amount).desc()
        ).all()

        categories = {}
        for row in results:
            cat = row.category
            if cat not in categories:
                categories[cat] = {"category": cat, "income": 0, "expense": 0, "total_count": 0}
            categories[cat][row.type.value] = float(row.total)
            categories[cat]["total_count"] += row.count

        return list(categories.values())

    @staticmethod
    def get_trends(period="monthly", year=None):
        """
        Return income/expense trends grouped by month or week.
        Raises ValueError on invalid period.
        """
        if period not in ["monthly", "weekly"]:
            raise ValueError("Period must be 'monthly' or 'weekly'")

        base_filter = [FinancialRecord.is_deleted == False]
        if year:
            base_filter.append(extract("year", FinancialRecord.date) == year)

        if period == "monthly":
            results = db.session.query(
                extract("year", FinancialRecord.date).label("year"),
                extract("month", FinancialRecord.date).label("month"),
                FinancialRecord.type,
                func.sum(FinancialRecord.amount).label("total")
            ).filter(*base_filter).group_by(
                extract("year", FinancialRecord.date),
                extract("month", FinancialRecord.date),
                FinancialRecord.type
            ).order_by("year", "month").all()

            trends = {}
            for row in results:
                key = f"{int(row.year)}-{int(row.month):02d}"
                if key not in trends:
                    trends[key] = {"period": key, "income": 0, "expense": 0}
                trends[key][row.type.value] = float(row.total)

        else:
            results = db.session.query(
                extract("year", FinancialRecord.date).label("year"),
                extract("week", FinancialRecord.date).label("week"),
                FinancialRecord.type,
                func.sum(FinancialRecord.amount).label("total")
            ).filter(*base_filter).group_by(
                extract("year", FinancialRecord.date),
                extract("week", FinancialRecord.date),
                FinancialRecord.type
            ).order_by("year", "week").all()

            trends = {}
            for row in results:
                key = f"{int(row.year)}-W{int(row.week):02d}"
                if key not in trends:
                    trends[key] = {"period": key, "income": 0, "expense": 0}
                trends[key][row.type.value] = float(row.total)

        trend_list = list(trends.values())
        for t in trend_list:
            t["net"] = t["income"] - t["expense"]

        return trend_list

    @staticmethod
    def get_recent_activity(limit=10):
        """Return the most recent financial records."""
        limit = min(limit, 50)
        records = FinancialRecord.query.filter_by(is_deleted=False).order_by(
            FinancialRecord.date.desc(),
            FinancialRecord.created_at.desc()
        ).limit(limit).all()
        return records
