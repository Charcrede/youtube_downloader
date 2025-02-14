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

# Installer Google Chrome (sans spécifier de version pour éviter les problèmes)
RUN apt-get update && apt-get install -y google-chrome-stable && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier le code de l'application dans le conteneur
COPY . /app

# Télécharger et installer ChromeDriver dans /usr/local/bin/
RUN curl -sSL https://chromedriver.storage.googleapis.com/$(google-chrome --version | awk '{print $3}')/chromedriver_linux64.zip -o chromedriver.zip \
    && unzip chromedriver.zip \
    && mv chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver.zip

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port
EXPOSE 8000

# Lancer l'application Django avec Gunicorn
ENTRYPOINT ["gunicorn", "youtube_downloader.wsgi:application", "--bind", "0.0.0.0:8000"]
