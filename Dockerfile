FROM python:3.10-slim

WORKDIR /app

# Instalar gcc u otras dependencias necesarias
RUN apt-get update && apt-get install -y bash gcc && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código
COPY . .

COPY start.sh .
RUN chmod +x start.sh

# Usuario no root opcional (si ya lo tienes configurado)
# RUN adduser --disabled-password --gecos '' appuser
# RUN chown -R appuser:appuser /app
# USER appuser

EXPOSE 8000

# Ejecutar el script de arranque
CMD ["./start.sh"]
