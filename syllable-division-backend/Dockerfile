FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dependencias del sistema (psycopg2 y netcat para el wait)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala requerimientos
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia el proyecto y habilita entrypoint
COPY . /app
RUN chmod +x /app/scripts/entrypoint.sh

EXPOSE 8000
CMD ["sh", "./scripts/entrypoint.sh"]