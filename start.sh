#!/bin/bash

# Ejecutar migraciones de Alembic
echo "Ejecutando migraciones..."
alembic upgrade head || echo "Migraciones fallaron o ya estaban aplicadas"

# Iniciar aplicación con el puerto de Railway
echo "Iniciando aplicación..."

# Crear vehículos requeridos si no existen
python scripts/seed_vehiculos.py || echo "Fallo al ejecutar seed_vehiculos.py"

uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --ws websockets --ws-ping-interval 30 --ws-ping-timeout 60