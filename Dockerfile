
# 1. La Base: Empezamos con una imagen oficial de Python.
# Usamos la versión 'slim' porque es más ligera.
FROM python:3.9-slim

# 2. El Entorno de Trabajo: Creamos una carpeta dentro del contenedor para nuestro código.
WORKDIR /app

# 3. La Copia: Copiamos TODO desde tu repositorio a la carpeta /app del contenedor.
# Esto incluye tu .py, tu .pkl y tu requirements.txt.
COPY . .

# 4. La Instalación: Ejecutamos pip para instalar todas las librerías de tu archivo.
# Asumo que tu archivo se llama requirements.txt. Si no, cámbialo aquí.
RUN pip install --no-cache-dir -r requirements.txt

# 5. El Comando de Ejecución: Esto es lo que se ejecuta cuando el contenedor arranca.
# ¡IMPORTANTE! No usamos el servidor de desarrollo de Dash. Usamos un servidor de producción como Gunicorn.
# Cloud Run espera que la aplicación escuche en el puerto 8080.

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app_RH:server"]
