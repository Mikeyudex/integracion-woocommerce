#!/bin/bash

# Script de despliegue para FastAPI con Docker
echo "🚀 Iniciando despliegue de FastAPI..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    error "Docker no está instalado. Por favor instala Docker primero."
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    warn "docker-compose no encontrado, intentando con 'docker compose'"
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

# Detener contenedores existentes
log "Deteniendo contenedores existentes..."
$DOCKER_COMPOSE_CMD down

# Construir la imagen
log "Construyendo la imagen Docker..."
$DOCKER_COMPOSE_CMD build --no-cache

# Ejecutar contenedores
log "Iniciando contenedores..."
$DOCKER_COMPOSE_CMD up -d

# Verificar que el servicio esté corriendo
log "Verificando el estado del servicio..."
sleep 5

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log "✅ API desplegada exitosamente!"
    log "📍 API disponible en: http://localhost:8000"
    log "📖 Documentación en: http://localhost:8000/docs"
    log "🔍 Logs del contenedor: docker-compose logs -f fastapi-app"
else
    error "❌ La API no responde. Revisa los logs: docker-compose logs fastapi-app"
fi

# Mostrar logs en tiempo real (opcional)
read -p "¿Deseas ver los logs en tiempo real? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $DOCKER_COMPOSE_CMD logs -f fastapi-app
fi