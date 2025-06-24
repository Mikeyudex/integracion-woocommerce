#!/bin/bash

# Script de inicio para FastAPI con uvicorn
set -e

# Directorio del proyecto
PROJECT_DIR="/app"
cd $PROJECT_DIR

PORT=8000

# Activar entorno virtual
#source venv/bin/activate

# Cargar variables de entorno desde .env
if [ -f .env ]; then
    set -a  # exporta todas las variables definidas
    source .env
    set +a
fi

# Crear directorio de logs si no existe
mkdir -p logs

# Verificar que la aplicación se puede importar
echo "Verificando aplicación..."
python -c "from app.main import app; print('✅ Aplicación importada correctamente')"

# Función para manejo de señales
cleanup() {
    echo "🛑 Deteniendo aplicación..."
    kill -TERM $PID 2>/dev/null || true
    wait $PID 2>/dev/null || true
    echo "✅ Aplicación detenida"
}

# Configurar traps para señales
trap cleanup SIGTERM SIGINT

# Iniciar uvicorn
echo "🚀 Iniciando FastAPI con uvicorn..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 4 \
    --log-level info \
    --access-log \
    --use-colors \
    --loop uvloop \
    --http httptools