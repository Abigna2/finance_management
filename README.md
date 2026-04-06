# Finance Data Processing and Access Control Backend

A Flask-based backend for a finance dashboard system with role-based access control, financial records management, and summary analytics — built for Zorvyn FinTech internship assessment.

**Live Demo:** https://financemanagement-production.up.railway.app
**API Docs (Swagger):** https://financemanagement-production.up.railway.app/docs/

---

## Tech Stack

| Layer | Choice |
|---|---|
| Framework | Flask 3.0 |
| Database | PostgreSQL (Neon cloud) |
| ORM | SQLAlchemy + Flask-Migrate |
| Auth | JWT (flask-jwt-extended) |
| API Docs | Flasgger (Swagger UI) |
| Deployment | Railway |

---

## Project Structure

```
finance_backend/
├── app/
│   ├── __init__.py              # App factory, extensions, Swagger config, frontend serving
│   ├── models/
│   │   └── models.py            # User, FinancialRecord models with enums
│   ├── routes/
│   │   ├── auth.py              # Register, Login
│   │   ├── users.py             # User management (thin HTTP handlers)
│   │   ├── records.py           # Financial records CRUD (thin HTTP handlers)
│   │   └── dashboard.py         # Summary and analytics APIs (thin HTTP handlers)
│   ├── services/
│   │   ├── record_service.py    # All business logic for records
│   │   ├── user_service.py      # All business logic for users
│   │   └── dashboard_service.py # All aggregation and analytics logic
│   ├── middleware/
│   │   └── auth_middleware.py   # @require_role() RBAC decorator
│   └── schemas/
├── frontend/
│   └── index.html               # Single-page dashboard (served by Flask)
├── config.py                    # Environment config with Neon SSL options
├── run.py                       # Entry point + CLI seed command
├── Procfile                     # Railway deployment config
├── railway.json                 # Railway build config
├── requirements.txt
└── .env.example
```

---

## Setup Instructions

### 1. Clone and create virtual environment

```bash
git clone https://github.com/Abigna2/finance_management
cd finance_management
py -3.11 -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

`.env` contents:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://username:password@host:5432/finance_db?sslmode=require
```

### 4. Run migrations

```bash
set FLASK_APP=run.py        # Windows
export FLASK_APP=run.py     # Mac/Linux
flask db upgrade
```

### 5. Seed sample users

```bash
flask seed
```

| Email | Password | Role |
|---|---|---|
| admin@finance.com | admin123 | Admin |
| analyst@finance.com | analyst123 | Analyst |
| viewer@finance.com | viewer123 | Viewer |

### 6. Run the server

```bash
python run.py
```

- App: `http://localhost:5000`
- Swagger docs: `http://localhost:5000/docs/`
- Frontend dashboard: `http://localhost:5000`

---

## API Reference

### Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/auth/register` | Register (always assigned viewer role) | No |
| POST | `/api/auth/login` | Login, returns JWT token | No |

### Users

| Method | Endpoint | Description | Roles |
|---|---|---|---|
| GET | `/api/users/` | List all users | Admin, Analyst |
| GET | `/api/users/me` | Get own profile | All |
| GET | `/api/users/:id` | Get user by ID | Admin, Analyst |
| PATCH | `/api/users/:id/role` | Update user role | Admin |
| PATCH | `/api/users/:id/status` | Activate/deactivate user | Admin |

### Financial Records

| Method | Endpoint | Description | Roles |
|---|---|---|---|
| GET | `/api/records/` | List records (filters + pagination) | All |
| GET | `/api/records/:id` | Get single record | All |
| POST | `/api/records/` | Create a record | Admin |
| PUT | `/api/records/:id` | Update a record | Admin |
| DELETE | `/api/records/:id` | Soft delete a record | Admin |

**Filters for GET /api/records/:**
- `type` — `income` or `expense`
- `category` — partial match
- `start_date` / `end_date` — format `YYYY-MM-DD`
- `page` / `per_page` — pagination (max 100)

### Dashboard

| Method | Endpoint | Description | Roles |
|---|---|---|---|
| GET | `/api/dashboard/summary` | Total income, expenses, net balance | All |
| GET | `/api/dashboard/categories` | Totals grouped by category | All |
| GET | `/api/dashboard/trends` | Monthly or weekly trends | Analyst, Admin |
| GET | `/api/dashboard/recent` | Recent activity | All |

---

## Role-Based Access Control

| Action | Viewer | Analyst | Admin |
|---|---|---|---|
| View records | ✅ | ✅ | ✅ |
| View summary & categories | ✅ | ✅ | ✅ |
| View trends | ❌ | ✅ | ✅ |
| Create/update/delete records | ❌ | ❌ | ✅ |
| Manage users | ❌ | View only | ✅ |

Enforced via `@require_role()` decorator in `app/middleware/auth_middleware.py`. Inactive users are blocked before role checks.

---

## Assumptions Made

1. **Shared data model** — This is an internal company finance dashboard, not a personal finance app. All users interact with the same financial records based on their role. This matches the assignment scenario of a "finance dashboard system where different users interact with financial records based on their role."
2. **Registration defaults to viewer** — New users always get the viewer role. Only an admin can upgrade roles via `/api/users/:id/role`. This reflects how real internal systems work.
3. **Soft deletes** — Records are never hard deleted; `is_deleted=True` hides them from all queries. Preserves data integrity and audit trails — important in financial systems.
4. **Amount validation** — Amounts must be positive. The type field (`income`/`expense`) determines the sign, not the amount.
5. **JWT only, no refresh tokens** — Tokens expire after 24 hours. Refresh tokens not implemented for simplicity.

## Tradeoffs Considered

- **Service layer vs fat routes** — Chose to separate business logic into `services/` so routes are thin HTTP handlers only. Makes logic independently testable and easier to read.
- **PostgreSQL vs SQLite** — PostgreSQL chosen for correct `extract()` behavior in trend queries. SQLite handles date extraction differently and can produce inconsistent results.
- **Flask vs FastAPI** — Flask requires more manual wiring but its explicit structure makes the architecture easier to follow for reviewers. Auto-docs via Flasgger compensates for missing FastAPI schema generation.
- **Soft delete vs hard delete** — `is_deleted` flag chosen over hard delete. Financial records should never be permanently destroyed for audit purposes.

---

## Author

Abigna Katakam
Backend Developer Intern Assessment — Zorvyn FinTech Pvt. Ltd.
