from flask import Flask, request, jsonify
import logging, json, sys, time, socket, os
from sqlalchemy import create_engine, text

app = Flask(__name__)

# --- structured logger (single-line JSON) ---
class JsonFormatter(logging.Formatter):
    def format(self, record):
        base = {
            "event": getattr(record, "event", "log"),
            "level": record.levelname,
            "message": record.getMessage(),
            "ts": int(time.time() * 1000),
        }
        extra = getattr(record, "extra", {})
        base.update(extra if isinstance(extra, dict) else {})
        return json.dumps(base)

h = logging.StreamHandler(sys.stdout)
h.setFormatter(JsonFormatter())
log = logging.getLogger("app")
log.setLevel(logging.INFO)
log.addHandler(h)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:dev@db:5432/appdb")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

@app.before_request
def _access_start():
    request._start = time.time()

@app.after_request
def _access_log(response):
    dur = int((time.time() - getattr(request, "_start", time.time())) * 1000)
    log.info("access", extra={
        "event":"http_access",
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "duration_ms": dur,
        "trace_id": request.headers.get("x-trace-id")
    })
    return response

@app.get("/alive")
def alive():
    log.info("alive", extra={"event":"alive","ok":True})
    return jsonify(status="ok")

@app.get("/identity")
def identity():
    host = socket.gethostname()
    log.info("who", extra={"event":"whoami","host":host})
    return jsonify(host=host)

# --- simple notes endpoints (intentionally minimal) ---
@app.post("/notes")
def create_note():
    body = request.json.get("body")
    # TODO: validate body (non-empty string), handle errors gracefully
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS notes(id SERIAL PRIMARY KEY, body TEXT);"))
        conn.execute(text("INSERT INTO notes(body) VALUES (:b)"), {"b": body})
    return jsonify(ok=True), 201

@app.get("/notes")
def list_notes():
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS notes(id SERIAL PRIMARY KEY, body TEXT);"))
        rows = conn.execute(text("SELECT id, body FROM notes ORDER BY id")).mappings().all()
    return jsonify(notes=[dict(r) for r in rows])

if __name__ == "__main__":
    # Dev server (Compose will use gunicorn)
    app.run(host="0.0.0.0", port=8000)
