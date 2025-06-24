# Guía de Despliegue FastAPI con Docker en Ubuntu

## 📋 Requisitos Previos

### 1. Actualizar el sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instalar Docker
```bash
# Remover versiones antiguas
sudo apt remove docker docker-engine docker.io containerd runc

# Instalar dependencias
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release

# Agregar clave GPG oficial de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Agregar repositorio
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### 3. Configurar Docker (opcional pero recomendado)
```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar:
newgrp docker

# Verificar instalación
docker --version
docker compose version
```

### 4. Instalar Docker Compose (si no está incluido)
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 🚀 Pasos de Despliegue

### 1. Crear estructura del proyecto
```bash
mkdir fastapi-project
cd fastapi-project
```

### 2. Crear archivos necesarios
Crea los siguientes archivos con el contenido proporcionado:
- `main.py` (código de la API)
- `requirements.txt` (dependencias)
- `Dockerfile` (imagen Docker)
- `docker-compose.yml` (orquestación)
- `deploy.sh` (script de despliegue)

### 3. Hacer ejecutable el script de despliegue
```bash
chmod +x deploy.sh
```

### 4. Ejecutar el despliegue
```bash
./deploy.sh
```

### Alternativa manual:
```bash
# Construir y ejecutar
docker-compose up --build -d

# Verificar estado
docker-compose ps
```

## 🔧 Comandos Útiles

### Gestión de contenedores
```bash
# Ver logs
docker-compose logs fastapi-app
docker-compose logs -f fastapi-app  # En tiempo real

# Reiniciar servicio
docker-compose restart fastapi-app

# Detener servicios
docker-compose down

# Reconstruir imagen
docker-compose build --no-cache
```

### Monitoreo
```bash
# Estado de contenedores
docker-compose ps

# Uso de recursos
docker stats

# Acceder al contenedor
docker-compose exec fastapi-app bash
```

## 🌐 Acceso a la API

Una vez desplegada, tu API estará disponible en:

- **API Principal**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔒 Configuración de Producción

### 1. Variables de entorno
Crea un archivo `.env`:
```bash
ENVIRONMENT=production
LOG_LEVEL=info
SECRET_KEY=tu-clave-secreta-muy-segura
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 2. Proxy reverso con Nginx (recomendado)
```bash
# Instalar Nginx
sudo apt install nginx

# Configurar sitio
sudo nano /etc/nginx/sites-available/fastapi
```

Contenido del archivo de configuración Nginx:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Firewall
```bash
# Configurar UFW
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 🔧 Solución de Problemas

### Puerto ocupado
```bash
# Ver qué proceso usa el puerto 8000
sudo lsof -i :8000

# Matar proceso si es necesario
sudo kill -9 <PID>
```

### Problemas de permisos Docker
```bash
# Verificar que el usuario esté en el grupo docker
groups $USER

# Si no está, agregarlo
sudo usermod -aG docker $USER
# Luego cerrar sesión y volver a entrar
```

### Logs de depuración
```bash
# Ver logs detallados del contenedor
docker-compose logs --details fastapi-app

# Logs del sistema Docker
journalctl -u docker.service
```

## 📊 Monitoreo y Mantenimiento

### Backup automático (opcional)
```bash
# Crear script de backup
#!/bin/bash
docker-compose exec postgres pg_dump -U myuser mydb > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Actualizaciones
```bash
# Actualizar imagen
docker-compose pull
docker-compose up -d

# Limpiar imágenes antiguas
docker image prune -a
```

¡Tu API FastAPI ahora está desplegada y lista para producción! 🎉