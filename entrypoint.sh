#!/bin/sh
set -e

echo "=========================================="
echo "  Running database migrations (alembic)"
echo "=========================================="
alembic upgrade head
echo "=========================================="
echo "  Migrations complete. Starting backend..."
echo "=========================================="
exec uvicorn app.main:app --host 0.0.0.0 --port 8000