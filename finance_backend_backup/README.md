# Finance Data Processing and Access Control Backend

A Flask-based backend for a finance dashboard system with role-based access control, financial records management, and summary analytics.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Framework | Flask 3.0 |
| Database | PostgreSQL |
| ORM | SQLAlchemy + Flask-Migrate |
| Auth | JWT (flask-jwt-extended) |
| API Docs | Flasgger (Swagger UI) |

---

## Project Structure

```
finance_backend/
├── app/
│   ├── __init__.py          # App factory, extensions, Swagger config
│   ├── models/
│   │   └── models.py        # User, FinancialRecord models
│   ├── routes/
│   │   ├── auth.py          # Register, Login
│   │   ├── users.py         # User management
│   │   ├── records.py       # Financial records CRUD
│   │   └── dashboard.py     # Summary and analytics APIs
│   ├── middleware/
│   │   └── auth_middleware.py  # Role-based access control decorator
│   └── schemas/             # Reserved for future marshmallow schemas
├── config.py                # Environment config
├── run.py                   # Entry point + CLI seed command
├── requirements.txt
└── .env.example
```

---

## Setup Instructions

### 1. Clone and create virtual environment

```bash
git clone <your-repo-url>
cd finance_backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
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
DATABASE_URL=postgresql://username:password@localhost:5432/finance_db
```

### 4. Create database and run migrations

```bash
flask db init
flask db migrate -m "initial migration"
flask db upgrade
```

### 5. Seed sample users (optional)

```bash
flask seed
```

This creates:
| Email | Password | Role |
|---|---|---|
| admin@finance.com | admin123 | Admin |
| analyst@finance.com | analyst123 | Analyst |
| viewer@finance.com | viewer123 | Viewer |

### 6. Run the server

```bash
python run.py
```

Server runs at: `http://localhost:5000`  
Swagger docs at: `http://localhost:5000/docs/`

---

## API Reference

### Authentication

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/api/auth/register` | Register a new user | No |
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
| GET | `/api/records/` | List records (with filters + pagination) | All |
| GET | `/api/records/:id` | Get single record | All |
| POST | `/api/records/` | Create a record | Admin |
| PUT | `/api/records/:id` | Update a record | Admin |
| DELETE | `/api/records/:id` | Soft delete a record | Admin |

**Query filters for GET /api/records/:**
- `type` — `income` or `expense`
- `category` — partial match
- `start_date` — format `YYYY-MM-DD`
- `end_date` — format `YYYY-MM-DD`
- `page` — default 1
- `per_page` — default 10, max 100

### Dashboard

| Method | Endpoint | Description | Roles |
|---|---|---|---|
| GET | `/api/dashboard/summary` | Total income, expenses, net balance | All |
| GET | `/api/dashboard/categories` | Totals grouped by category | All |
| GET | `/api/dashboard/trends` | Monthly or weekly trends | Analyst, Admin |
| GET | `/api/dashboard/recent` | Recent activity | All |

**Query params for GET /api/dashboard/trends:**
- `period` — `monthly` (default) or `weekly`
- `year` — filter by year (e.g. `2026`)

---

## Role-Based Access Control

| Action | Viewer | Analyst | Admin |
|---|---|---|---|
| View records | ✅ | ✅ | ✅ |
| View summary | ✅ | ✅ | ✅ |
| View trends | ❌ | ✅ | ✅ |
| Create/update/delete records | ❌ | ❌ | ✅ |
| Manage users | ❌ | View only | ✅ |

Access control is enforced via the `@require_role()` decorator in `app/middleware/auth_middleware.py`.

---

## Assumptions Made

1. **Role assignment at registration** — The role can be passed during registration for simplicity. In production, a new user would always default to `viewer` and only an admin could upgrade them.
2. **Soft deletes** — Records are never hard deleted; `is_deleted=True` hides them from all queries. This preserves data integrity and audit trails.
3. **Amount validation** — Amounts must be positive numbers. The sign of the entry is determined by the `type` field (`income` or `expense`), not the amount itself.
4. **Single token auth** — No refresh tokens are implemented. Tokens expire after 1 hour.
5. **No multi-tenancy** — All users share the same financial records pool. An admin manages the whole system.

## Tradeoffs Considered

- **SQLite vs PostgreSQL** — Chose PostgreSQL for correctness with aggregation queries (especially `extract` for trends). SQLite handles these differently and can cause issues.
- **Flask vs FastAPI** — Flask requires slightly more manual wiring, but its simplicity makes the architecture very readable and easy to follow for reviewers.
- **Soft delete vs hard delete** — Soft delete adds an `is_deleted` flag. This is better practice in financial systems where audit history matters.

---

## Author

Abigna Katakam  
Backend Developer Intern Assignment — Zorvyn FinTech Pvt. Ltd.
