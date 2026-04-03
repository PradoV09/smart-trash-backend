#!/bin/bash

# La base de datos ya está lista gracias a depends_on en docker-compose

echo "Ejecutando migraciones..."
alembic upgrade head

echo "Iniciando aplicación..."
uvicorn main:app --host 0.0.0.0 --port 8000