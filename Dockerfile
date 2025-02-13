# Utiliser une image Debian avec Python et FFmpeg
FROM python:3.10-slim

# Installer FFmpeg et les dépendances système
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    unzip \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Ajouter la clé Google et le dépôt Chrome
RUN wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list

# Spécifier la version de Google Chrome à installer
ARG CHROME_VERSION="133.0.6943.99"

RUN apt-get update && apt-get install -y google-chrome-stable=${CHROME_VERSION} && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port
EXPOSE 8000

# Lancer l'application Django avec Gunicorn
CMD ["gunicorn", "youtube_downloader.wsgi:application", "--bind", "0.0.0.0:8000"]
