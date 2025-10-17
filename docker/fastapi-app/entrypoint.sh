#!/bin/bash
set -e

echo "Running database migrations..."
cd /app/models/db_schemas/
alembic upgrade head
cd /app

exec "$@"
