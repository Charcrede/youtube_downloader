from django.http import StreamingHttpResponse,FileResponse
from rest_framework.decorators import api_view
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.response import Response
# from pytube import YouTube
import os
# import requests
import yt_dlp
import subprocess
import os
import tempfile
from django.conf import settings

from channels.layers import get_channel_layer
import asyncio

def check_and_get_cookies():
    """Vérifie si le fichier cookies.json existe, sinon le crée en exécutant get_cookies.py"""
    cookies_file = "cookies.json"
    
    if not os.path.exists(cookies_file):
        # Si le fichier de cookies n'existe pas, lance le script get_cookies.py
        print("Cookies non trouvés, récupération des cookies...")
        subprocess.run(["python", "get_cookies.py"])
        
        # Vérifie à nouveau si le fichier de cookies existe après exécution du script
        if not os.path.exists(cookies_file):
            raise FileNotFoundError("Le fichier de cookies n'a pas pu être créé.")
        print("Cookies récupérés avec succès.")

# Fonction pour récupérer les flux vidéo disponibles
@api_view(['POST'])
def get_video_info(request):
    """Récupérer les informations de la vidéo (titre, image et tous les formats disponibles)"""
    video_url = request.data.get("url")

    if not video_url:
        return Response({"error": "URL manquante"}, status=400)

    try:
        check_and_get_cookies()  # Lancer le script pour récupérer les cookies si nécessaire
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    cookies_file = "cookies.json"
    
    # Vérifier l'existence du fichier de cookies
    if not os.path.exists(cookies_file):
        return Response({"error": "Le fichier de cookies est introuvable"}, status=500)

    try:
        ydl_opts = {
            "quiet": True,
            "cookies": cookies_file  # Charger les cookies depuis le fichier
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        # Liste de tous les formats disponibles
        formats = []
        for format in info["formats"]:
            formats.append({
                "format_id": format.get("format_id"),
                "resolution": f"{format.get('height', 'Inconnu')}p",  # Récupère la résolution si elle existe
                "filesize": format.get("filesize", "Inconnu"),
                "has_audio": format.get("acodec") != "none",  # Vérifier si l'audio est présent
                "has_video": format.get("vcodec") != "none"
            })

        return Response({
            "title": info.get("title", "Vidéo"),
            "thumbnail": info.get("thumbnail"),  # Image de la vidéo
            "formats": formats  # Tous les formats disponibles
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def download_video(request, output_path="downloads/"):
    """Télécharge la vidéo avec la résolution sélectionnée et fusionne si nécessaire"""
    video_url = request.data.get("url")
    format_id = request.data.get("format_id")

    if not video_url or not format_id:
        return Response({"error": "URL ou format manquant"}, status=400)

    try:
        check_and_get_cookies()  # Lancer le script pour récupérer les cookies si nécessaire
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    # Vérifier l'existence du fichier de cookies
    cookies_file = "cookies.json"
    if not os.path.exists(cookies_file):
        return Response({"error": "Le fichier de cookies est introuvable"}, status=500)

    try:
        temp_dir = tempfile.mkdtemp()

        # Vérifier si la vidéo sélectionnée contient déjà l’audio
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
        
        selected_format = next((f for f in info["formats"] if f["format_id"] == format_id), None)

        if not selected_format:
            return Response({"error": "Format introuvable"}, status=400)

        has_audio = selected_format.get("acodec") != "none"

        # Options de téléchargement
        ydl_opts = {
            "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
            "quiet": True,
            "ffmpeg_location": "C:/Program Files/ffmpeg-7.1-essentials_build/bin",
            "cookies": cookies_file  # Ajout des cookies ici
        }

        if has_audio:
            ydl_opts["format"] = format_id
        else:
            ydl_opts["format"] = f"{format_id}+bestaudio"
            ydl_opts["merge_output_format"] = "mp4"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url)
            file_path = ydl.prepare_filename(info)

        return FileResponse(open(file_path, "rb"), as_attachment=True)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


# Hook pour envoyer la progression du téléchargement via WebSocket
def progress_hook(d):
    """Envoie le pourcentage via WebSocket"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "download_progress",
            {"type": "send_progress", "progress": percent}
        )