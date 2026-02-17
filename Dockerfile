# 1. Base image con Python 3.12
FROM python:3.12-slim

# 2. Directorio de trabajo
WORKDIR /app

# 3. Copiar archivos de dependencias
COPY requirements.txt .

# 4. Instalar dependencias
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del proyecto
COPY . .

# 6. Exponer puerto (fijo para Docker, Render usará PORT env)
EXPOSE 8000

# 7. Comando por defecto
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
