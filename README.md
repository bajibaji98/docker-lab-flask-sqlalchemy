# Docker Basics Lab — Flask + SQLAlchemy + Postgres

Minimal Flask API containerized with Docker. Provisioned with Docker Compose alongside Postgres on a **private network** with a **named volume**. Includes structured JSON logs, a liveness endpoint, and a simple notes table to demonstrate **persistence**. Supports **horizontal scaling**.

## Tech & Tools
- Python 3.11
- Flask 3.0, SQLAlchemy 2.0, (psycopg2-binary 2.9.x or psycopg 3.x)
- Gunicorn (1 worker for demo)
- Docker Desktop (Linux engine) + Docker Compose v2
- Postgres 16

---

## Repo Structure
docker-lab-flask-sqlalchemy/
├─ app.py
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ .dockerignore
└─ README.md

---

## Quick Start

> **Windows PowerShell-friendly commands shown.** If `:8000` is busy, change host mapping to `8001:8000` in compose.

```powershell
# 0) From repo root
docker compose up -d --build
docker compose ps

# 1) Liveness
Invoke-WebRequest http://localhost:8000/alive | Select-Object -Expand Content
# expected: {"status":"ok"}

# 2) Logs (structured JSON)
docker compose logs -f web
Endpoints

GET /alive – liveness check → {"status":"ok"}

GET /identity – shows the container hostname (for scale demo) → {"host":"api-1"...}

POST /notes – create a note
Body: {"body":"hello flask"}

GET /notes – list notes → {"notes":[{"id":1,"body":"..."}]}

# Create a note
Invoke-RestMethod -Method Post -Uri http://localhost:8000/notes `
  -Body (@{body="hello flask"} | ConvertTo-Json) `
  -ContentType "application/json"

# List notes
Invoke-WebRequest http://localhost:8000/notes | Select-Object -Expand Content

docker compose logs -f web

#Sample:

{"event":"http_access","method":"GET","path":"/alive","status":200,"duration_ms":3,"trace_id":null}
{"event":"whoami","host":"web-1"}

#Persistent Demo

# Create table + insert via SQL (also done automatically in app routes)
docker compose exec db psql -U app -d appdb -c "CREATE TABLE IF NOT EXISTS notes(id SERIAL PRIMARY KEY, body TEXT);"
docker compose exec db psql -U app -d appdb -c "INSERT INTO notes(body) VALUES ('persist-demo');"
docker compose exec db psql -U app -d appdb -c "SELECT * FROM notes;"

# Restart only DB, verify row persists
docker compose restart db
docker compose exec db psql -U app -d appdb -c "SELECT * FROM notes;"

#stack teardown but keep volume

docker compose down
docker compose up -d
docker compose exec db psql -U app -d appdb -c "SELECT * FROM notes;"


