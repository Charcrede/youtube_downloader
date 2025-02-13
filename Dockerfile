# Utiliser une image de base avec Python et FFmpeg
FROM jrottenberg/ffmpeg:4.4-alpine

# Installer les dépendances système
RUN apk add --no-cache python3 py3-pip


# Installer Google Chrome
RUN apt update && apt install -y wget
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb"



# Installer les dépendances nécessaires pour Chrome et ChromeDriver
RUN apt-get update && apt-get install -y wget unzip curl \
    && wget -O /usr/bin/chromedriver https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.9/linux64/chromedriver-linux64.zip \
    && unzip /usr/bin/chromedriver -d /usr/bin/ \
    && chmod +x /usr/bin/chromedriver \
    && wget -O /usr/bin/google-chrome https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i /usr/bin/google-chrome || apt-get install -fy

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


