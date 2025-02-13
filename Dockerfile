# Utiliser une image de base avec Python et FFmpeg
FROM jrottenberg/ffmpeg:4.4-alpine

# Installer les dépendances système
RUN apk add --no-cache python3 py3-pip

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet
COPY . .

# Installer les dépendances Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Exposer le port
EXPOSE 8000

# Lancer l'application Django avec Gunicorn
CMD ["gunicorn", "youtube_downloader.wsgi:application", "--bind", "0.0.0.0:8000"]
