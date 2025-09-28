#!/usr/bin/env sh
set -e

# Espera a Postgres
: "${DB_HOST:=db}"
: "${DB_PORT:=5432}"

echo "Esperando a la base de datos en $DB_HOST:$DB_PORT ..."
until nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done
echo "Base de datos lista."

python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

python manage.py runserver 0.0.0.0:8000