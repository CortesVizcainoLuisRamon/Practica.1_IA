# ══════════════════════════════════════════════
#  Dockerfile — Búsqueda Ciega (DFS & BFS)
#  Incluye soporte para GUI con Tkinter
# ══════════════════════════════════════════════
FROM python:3.11-slim

# Variables de entorno para display (necesario para Tkinter en Docker)
ENV DISPLAY=:0
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependencias del sistema para Tkinter y Xorg
RUN apt-get update && apt-get install -y \
    python3-tk \
    tk-dev \
    x11-apps \
    libx11-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar proyecto
COPY . .

# Instalar dependencias Python (si agregas más paquetes al requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Ejecutar tests primero, luego la app
CMD ["sh", "-c", "python -m pytest tests/ -v && python main.py"]
