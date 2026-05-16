#!/bin/sh
set -e

python -c "from app.db.base import init_db; init_db()"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000