FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /srv
USER appuser

EXPOSE 8000
# gunicorn (1 worker for demo; discuss worker/DB connections tradeoff)
CMD ["gunicorn","-w","1","-b","0.0.0.0:8000","app:app"]
