from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import json
import os

def get_youtube_cookies():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Mode sans interface
    chrome_options.add_argument("--no-sandbox")  # Nécessaire sur les serveurs
    chrome_options.add_argument("--disable-dev-shm-usage")  # Évite certains crashs
    chrome_options.add_argument("--disable-gpu")  # Désactive le rendu GPU
    chrome_options.add_argument("--remote-debugging-port=9222")

    # Chemin du chromedriver
    chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")

    # Donner les permissions d'exécution au chromedriver
    os.chmod(chromedriver_path, 0o755)

    # Lancer Chrome avec le driver
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://www.youtube.com")
    time.sleep(5)  # Laisser le temps au site de se charger

    # Récupérer les cookies
    cookies = driver.get_cookies()
    driver.quit()

    # Sauvegarder les cookies dans un fichier JSON
    with open("cookies.json", "w") as f:
        json.dump(cookies, f)

    print("✅ Cookies YouTube récupérés avec succès !")

if __name__ == "__main__":
    get_youtube_cookies()
