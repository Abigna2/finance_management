from app import create_app, db
from app.models.models import User, FinancialRecord, RoleEnum
import os

app = create_app(os.getenv("FLASK_ENV", "development"))


@app.cli.command("seed")
def seed_db():
    """Seed the database with sample data for testing."""
    if not User.query.filter_by(email="admin@finance.com").first():
        admin = User(name="Admin User", email="admin@finance.com", role=RoleEnum.admin)
        admin.set_password("admin123")
        db.session.add(admin)

    if not User.query.filter_by(email="analyst@finance.com").first():
        analyst = User(name="Analyst User", email="analyst@finance.com", role=RoleEnum.analyst)
        analyst.set_password("analyst123")
        db.session.add(analyst)

    if not User.query.filter_by(email="viewer@finance.com").first():
        viewer = User(name="Viewer User", email="viewer@finance.com", role=RoleEnum.viewer)
        viewer.set_password("viewer123")
        db.session.add(viewer)

    db.session.commit()
    print("Database seeded successfully!")
    print("Admin:    admin@finance.com / admin123")
    print("Analyst:  analyst@finance.com / analyst123")
    print("Viewer:   viewer@finance.com / viewer123")


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "FinancialRecord": FinancialRecord}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
