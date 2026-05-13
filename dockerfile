FROM ghcr.io/marioaran/python-base:3.10-slim

WORKDIR /app

# Crear requirements.txt directamente en el Dockerfile (para evitar errores de copia)
RUN echo "flask==3.0.3" > requirements.txt

# Instalar Flask
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación
COPY app.py .

# Exponer el puerto
EXPOSE 5000

# Comando para ejecutar la app
CMD ["python", "app.py"]