# Configuración para uvicorn
import os
import multiprocessing

# Configuración del servidor
HOST = "0.0.0.0"
PORT = 8003
WORKERS = multiprocessing.cpu_count()

# Configuración de rendimiento
LOOP = "uvloop"  # Usa uvloop para mejor rendimiento
HTTP = "httptools"  # Usa httptools para mejor rendimiento HTTP

# Configuración de logs
LOG_LEVEL = "info"
ACCESS_LOG = True
USE_COLORS = True

# Configuración de SSL (si es necesario)
# SSL_KEYFILE = "/path/to/keyfile.pem"
# SSL_CERTFILE = "/path/to/certfile.pem"

# Configuración de desarrollo
RELOAD = False  # Cambiar a True solo en desarrollo
RELOAD_DIRS = ["app"]  # Directorios a monitorear para reload

# Variables de entorno
def get_config():
    return {
        "host": os.getenv("HOST", HOST),
        "port": int(os.getenv("PORT", PORT)),
        "workers": int(os.getenv("WORKERS", WORKERS)),
        "loop": os.getenv("LOOP", LOOP),
        "http": os.getenv("HTTP", HTTP),
        "log_level": os.getenv("LOG_LEVEL", LOG_LEVEL),
        "access_log": os.getenv("ACCESS_LOG", "true").lower() == "true",
        "use_colors": os.getenv("USE_COLORS", "true").lower() == "true",
        "reload": os.getenv("RELOAD", "false").lower() == "true",
    }