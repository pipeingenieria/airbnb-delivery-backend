# Usamos una imagen oficial y ligera de Python
FROM python:3.12-slim

# Evita que Python genere archivos .pyc y fuerza a que los logs salgan directo a la terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo en el contenedor
WORKDIR /code

# Copiar primero los requerimientos para aprovechar el caché de Docker
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY ./app /code/app

# Exponer el puerto que usará Fly.io
EXPOSE 8080

# Comando para arrancar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
