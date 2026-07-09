# School Result & Attendance Portal

Full-stack school management system with role-based access, attendance tracking, exam scores, ML-powered risk prediction, and PDF report cards.

## Features

- **Role-based access** — Admin, Teacher, Student, Parent (each with dedicated dashboards)
- **Attendance management** — Daily attendance marking per class (present/absent/excused)
- **Exam scores** — Term-based scores with midterm, final, and assignment types; automatic grade calculation
- **Report cards** — Web view and PDF download via weasyprint
- **Risk prediction** — Logistic Regression model predicts at-risk students based on attendance, scores, and absence patterns
- **Scheduled analysis** — Celery Beat runs weekly risk analysis (Mondays at 2am)
- **Fully Dockerized** — PostgreSQL, Redis, Gunicorn, Celery worker & beat

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web | Flask, Jinja2, Tailwind CSS |
| Database | PostgreSQL (prod), SQLite (tests) |
| Async | Celery + Redis |
| ML | scikit-learn (LogisticRegression) |
| PDF | weasyprint |
| Infra | Docker Compose, GitHub Actions |

## Quick Start

### Prerequisites

- Docker & Docker Compose

### Run

```bash
docker compose up
```

Access the app at **http://localhost:5000** (or **http://localhost:5001** if port 5000 is in use).

### Seed Demo Data

After the app is running, run the seed script inside the container:

```bash
docker compose exec web python seed.py
```

### Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@school.gov | admin123 |
| Teacher | teacher@school.gov | teacher123 |
| Student | fatou.sillah@student.school.gov | student123 |
| Parent | parent@school.gov | parent123 |

## Local Development (without Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=sqlite:///dev.db
export FLASK_SECRET=dev-secret
export CELERY_BROKER_URL=redis://localhost:6379/0

flask db upgrade
python seed.py
flask run
```

## Project Structure

```
school-portal/
├── app/
│   ├── models/          # SQLAlchemy models (User, Class, Subject, Score, Attendance, RiskPrediction)
│   ├── routes/          # Blueprints (auth, dashboard, attendance, scores, reports, risk, admin)
│   ├── services/        # Celery tasks, risk predictor (ML), PDF generator
│   └── templates/       # Jinja2 templates
├── migrations/          # Alembic database migrations
├── tests/               # Pytest tests
├── docker-compose.yml   # Multi-service orchestration
├── Dockerfile           # Container image
└── seed.py              # Demo data seeder
```

## API Routes

| Endpoint | Methods | Access |
|----------|---------|--------|
| `/auth/login` | GET, POST | Public |
| `/auth/logout` | GET | Authenticated |
| `/` | GET | Authenticated (role-based dashboard) |
| `/admin/users` | GET, POST | Admin |
| `/admin/users/<id>/edit` | GET, POST | Admin |
| `/admin/users/<id>/delete` | POST | Admin |
| `/admin/classes` | GET, POST | Admin |
| `/admin/classes/<id>/edit` | GET, POST | Admin |
| `/attendance/<class_id>` | GET, POST | Teacher |
| `/scores/<class_id>` | GET, POST | Teacher |
| `/reports/<student_id>` | GET | Teacher, Student, Parent |
| `/reports/<student_id>/pdf` | GET | Teacher, Student, Parent |
| `/risk/<class_id>` | GET | Teacher |
| `/risk/run/<class_id>` | POST | Teacher |

## Tests

```bash
pytest -v
```

CI runs lint (ruff), tests, and Docker build on every push/PR to `main`.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_SECRET` | `dev-secret` | Flask secret key |
| `DATABASE_URL` | `postgresql://school:school@localhost:5432/school` | Database connection string |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Redis connection string (falls back to `REDIS_URL`) |

## Deploy to Railway

### Prerequisites

- [Railway](https://railway.com) account (sign up with GitHub — $5 free trial credit, no credit card required)

### Steps

1. **Create a Railway project**
   - Go to [dashboard](https://railway.com/dashboard) → **+ New Project** → **Empty Project**

2. **Add PostgreSQL**
   - Click **+ New** → **Database** → **Add PostgreSQL**
   - Railway exposes `DATABASE_URL` automatically

3. **Add Redis**
   - Click **+ New** → **Database** → **Add Redis**
   - Railway exposes `REDIS_URL` automatically

4. **Add the web service**
   - Click **+ New** → **GitHub Repo** → select `tamsirdev/school-portal`
   - Under **Variables**, set `FLASK_SECRET` to a random secret
   - Add a **Reference Variable**: `DATABASE_URL` → select the PostgreSQL service
   - Add a **Reference Variable**: `CELERY_BROKER_URL` → select the Redis service → use its `REDIS_URL`
   - Under **Settings → Networking**, click **Generate Domain**
   - Under **Settings → Deploy**, set **Command** to:
     ```
     sh -c "flask db upgrade && gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - manage:app"
     ```
   - Railway auto-detects the Dockerfile and builds

5. **Add the Celery worker**
   - Click **+ New** → **GitHub Repo** → same repo
   - Same **Variables** as the web service (`FLASK_SECRET`, `DATABASE_URL`, `CELERY_BROKER_URL`)
   - Set **Command** to:
     ```
     celery -A app.services.celery_app worker --loglevel=info
     ```

6. **Add the Celery beat** (scheduled risk analysis)
   - Click **+ New** → **GitHub Repo** → same repo
   - Same **Variables**
   - Set **Command** to:
     ```
     celery -A app.services.celery_app beat --loglevel=info
     ```

7. **Seed demo data** (after all services deploy)
   - In the Railway dashboard, open the web service → **Shell** tab
   - Run: `python seed.py`

### Notes

- Railway's $5 free trial credit covers the PostgreSQL, Redis, and all three services for a small app
- The app listens on port 5000 (Railway sets `PORT=5000` by default for Dockerfile deploys)
- No `railway.json` needed — all config is done through the dashboard
