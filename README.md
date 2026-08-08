# User Service API

A modular, API-first REST service for managing users, built with **Flask** and **MySQL**.
It supports CRUD-style listing/creation, search, pagination, validation, structured error
handling, and (bonus) JWT-protected write access, fully Dockerized.

---

## Tech Stack

| Layer            | Choice                          |
|-------------------|----------------------------------|
| Framework         | Flask 3 + Blueprints             |
| ORM               | Flask-SQLAlchemy                 |
| Database          | MySQL 8                          |
| Auth (bonus)      | Flask-JWT-Extended               |
| Containerization  | Docker + docker-compose (bonus)  |

---

## Project Structure

```
user-service/
├── app/
│   ├── __init__.py          # App factory, blueprint registration, error handlers
│   ├── config.py            # Environment-based configuration
│   ├── extensions.py        # db, jwt singletons
│   ├── models/
│   │   └── user.py          # User SQLAlchemy model
│   ├── routes/
│   │   ├── user_routes.py   # /users endpoints
│   │   └── auth_routes.py   # /auth/login endpoint (JWT bonus)
│   ├── services/
│   │   └── user_service.py  # Business logic (search, pagination, create)
│   └── utils/
│       ├── validators.py    # Email + required-field validation
│       └── responses.py     # Consistent JSON response helpers
├── schema.sql                # MySQL schema (DB + table)
├── run.py                    # Entry point
├── requirements.txt
├── Dockerfile                 # Bonus
├── docker-compose.yml         # Bonus
├── .env.example
└── README.md
```

Routes stay thin (HTTP concerns only); all business logic lives in `services/`, matching
the `/routes`, `/models`, `/services` structure requested in the assignment.

---

## Setup Instructions

### Option A — Docker (recommended, includes MySQL)

```bash
docker-compose up --build
```

This starts MySQL (with `schema.sql` auto-applied) and the API on `http://localhost:5000`.

### Option B — Local / manual

1. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up MySQL**
   ```bash
   mysql -u root -p < schema.sql
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # edit .env with your DB credentials
   ```

4. **Initialize tables via the app (alternative to schema.sql)**
   ```bash
   flask --app run.py init-db
   ```

5. **Run the server**
   ```bash
   python run.py
   ```
   API available at `http://localhost:5000`.

---

## API Endpoints

All responses follow a consistent JSON envelope:

```json
{ "success": true, "data": { ... }, "meta": { ... } }
```

```json
{ "success": false, "error": "message or list of messages" }
```

### 1. Get all users
`GET /users`

```bash
curl http://localhost:5000/users
```

```json
{
  "success": true,
  "data": [
    { "id": 1, "name": "Jane Doe", "email": "jane@example.com", "role": "admin",
      "created_at": "2026-08-08T10:00:00", "updated_at": "2026-08-08T10:00:00" }
  ],
  "meta": { "page": 1, "limit": 10, "total": 1, "total_pages": 1 }
}
```

### 2. Search users
`GET /users?search=jane`

Matches against **name** or **email** (case-insensitive, partial match).

### 3. Paginated results
`GET /users?page=2&limit=5`

Search and pagination can be combined: `GET /users?search=jane&page=1&limit=10`.

### 4. Get user by ID
`GET /users/<id>`

```bash
curl http://localhost:5000/users/1
```

Not found:
```json
{ "success": false, "error": "User not found" }
```
→ HTTP 404

### 5. Create a user (requires JWT — see bonus auth below)
`POST /users`

```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"name": "Jane Doe", "email": "jane@example.com", "role": "admin"}'
```

Success (`201`):
```json
{
  "success": true,
  "message": "User created successfully",
  "data": { "id": 1, "name": "Jane Doe", "email": "jane@example.com", "role": "admin", ... }
}
```

Validation error (`400`):
```json
{ "success": false, "error": ["'email' is required"] }
```

Duplicate email (`409`):
```json
{ "success": false, "error": "A user with this email already exists" }
```

### 6. (Bonus) Login for JWT token
`POST /auth/login`

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

```json
{ "success": true, "data": { "access_token": "eyJhbGciOi..." } }
```

Use the token in the `Authorization: Bearer <token>` header for `POST /users`.
Default demo credentials are set via `ADMIN_USERNAME` / `ADMIN_PASSWORD` in `.env`.

### 7. Health check
`GET /health` — simple liveness probe, useful for Docker/Kubernetes.

---

## Database Schema

**Database:** `users`
**Table:** `users`

| Column     | Type          | Constraints                  |
|------------|---------------|-------------------------------|
| id         | INT           | PRIMARY KEY, AUTO_INCREMENT   |
| name       | VARCHAR(120)  | NOT NULL                      |
| email      | VARCHAR(150)  | NOT NULL, UNIQUE               |
| role       | VARCHAR(50)   | NOT NULL                      |
| created_at | DATETIME      | DEFAULT CURRENT_TIMESTAMP     |
| updated_at | DATETIME      | ON UPDATE CURRENT_TIMESTAMP   |

See `schema.sql` for the full DDL.

---

## Assumptions Made

- `role` is a free-text field (e.g. `admin`, `user`) rather than a foreign key to a
  separate roles table, since no roles table was specified.
- Emails are stored lower-cased and trimmed to keep the uniqueness check case-insensitive.
- `search` performs a partial, case-insensitive match on **both** `name` and `email`.
- `page` defaults to `1` and `limit` defaults to `10`; `limit` is capped at `100` to avoid
  accidentally returning huge result sets.
- Only `POST /users` is protected with JWT (write operation); `GET` endpoints are left
  public for read access, since no specific auth scope was defined in the brief. This is
  easy to extend by adding `@jwt_required()` to any other route.
- Authentication uses a single demo admin account (env-based) rather than a full user/
  credentials table, since user login wasn't part of the core task list — only the bonus
  "JWT authentication" line item.
- No `DELETE`/`PUT` endpoints were implemented since they weren't listed in Task 1;
  the modular structure (`services/user_service.py`) makes them straightforward to add.

---

## Short Answers

**1. Why did you choose Flask?**
Flask is lightweight and unopinionated, which is a good fit for a small, focused,
API-first service like this one. Its Blueprint system gives clean route separation
without the overhead of Django's full-stack conventions (admin panel, templating,
ORM-specific migrations), and Flask-SQLAlchemy + Flask-JWT-Extended cover everything
this assignment needs. For a larger system with many models, built-in admin, and
heavier ORM/migration needs, Django would be the stronger choice.

**2. How would you scale this system?**
- **Horizontal scaling:** run multiple stateless API instances (already stateless here
  since JWT carries auth state) behind a load balancer; `gunicorn` with multiple workers
  is the first step, then multiple containers/pods.
- **Database:** add read replicas for the heavy `GET /users` traffic, connection pooling
  (SQLAlchemy pool tuning), and proper indexes (already indexed on `email`; would add a
  composite index on `name` for search-heavy workloads, or move search to a dedicated
  search engine like Elasticsearch/OpenSearch at higher scale).
- **Caching:** cache frequent reads (e.g. `GET /users/<id>`) with Redis and invalidate
  on writes.
- **Pagination:** already implemented; would move to cursor-based pagination for very
  large tables where `OFFSET` becomes slow.
- **Async/background work:** offload anything non-critical-path (e.g. sending a welcome
  email on user creation) to a task queue (Celery/RQ) rather than blocking the request.

**3. What changes would you make for production?**
- Replace the demo admin/env-based login with a real users/credentials table, hashed
  passwords (bcrypt/argon2), and refresh tokens; add rate limiting on `/auth/login`.
- Use Alembic (Flask-Migrate) for versioned schema migrations instead of `db.create_all()`.
- Add structured logging, request tracing, and monitoring/alerting (e.g. Prometheus +
  Grafana, or a hosted APM).
- Add automated tests (unit tests for `services/`, integration tests for routes) and CI
  to run them on every PR.
- Turn off `debug=True`, serve via `gunicorn`/`uwsgi` behind Nginx, and terminate TLS at
  the load balancer.
- Tighten CORS, add input size limits, and run periodic dependency/security scans.
- Move secrets (`SECRET_KEY`, `JWT_SECRET_KEY`, DB credentials) out of `.env` files and
  into a secrets manager (AWS Secrets Manager / Vault) for production deployments.

---

## AI Usage Declaration

- **AI tools used:** Claude (Anthropic) was used to scaffold this project.
- **Manual modifications** Given time constraints, I used Claude to scaffold the majority of the project (structure, boilerplate, routes, service layer, Docker setup, and README) rather than writing every line from scratch. I reviewed the full implementation to ensure I understand each part — the request/response flow, the validation logic, the search/pagination query, and the JWT auth flow — and can explain any part of it.
