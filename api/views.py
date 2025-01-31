from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pytube import YouTube
import os
import requests
import yt_dlp
import subprocess

from django.conf import settings

# Fonction pour récupérer les flux vidéo disponibles
@api_view(['POST'])
def get_video_streams(request):
    url = request.data.get('url')
    if not url:
        return Response({"error": "URL manquant"}, status=400)
    
    try:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True, file_extension='mp4')
        
        # Utiliser un dictionnaire pour ne garder qu'un flux par résolution
        unique_streams = {}
        for stream in streams:
            if stream.resolution not in unique_streams:
                unique_streams[stream.resolution] = {
                    "itag": stream.itag,
                    "resolution": stream.resolution,
                    "fps": stream.fps,
                    "mime_type": stream.mime_type,
                    "filesize": round(stream.filesize / (1024 * 1024), 2),  # Taille en Mo
                }
        
        return Response({
            "title": yt.title,
            "author": yt.author,
            "thumbnail_url": yt.thumbnail_url,  # URL de l'image miniature
            "streams": list(unique_streams.values())
        })
    except Exception:
        # Si Pytube échoue, essayez avec yt-dlp
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Utiliser un dictionnaire pour ne garder qu'un flux par résolution
                unique_streams = {}
                for f in info['formats']:
                    if f['ext'] == 'mp4' and f.get('height'):  # Filtrer uniquement les MP4 avec vidéo
                        resolution = f"{f['height']}p"
                        if resolution not in unique_streams:
                            unique_streams[resolution] = {
                                "itag": f['format_id'],
                                "resolution": resolution,
                                "fps": f.get('fps', None),
                                "mime_type": f['ext'],
                                "filesize": round(f['filesize'] / (1024 * 1024), 2) if f.get('filesize') else None,
                            }
                
                return Response({
                    "title": info['title'],
                    "author": info.get('uploader', 'Inconnu'),
                    "thumbnail_url": info.get('thumbnail'),  # URL de l'image miniature
                    "streams": list(unique_streams.values())
                })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": f"Erreur interne : {str(e)}"}, status=500)
        


# Fonction pour télécharger une vidéo en fonction de son itag
@api_view(['POST'])
def download_video_by_itag(request):
    url = request.data.get('url')
    itag = request.data.get('itag')

    if not url or not itag:
        return Response({"error": "URL ou itag manquant"}, status=400)

    # Méthode 1 : Pytube
    try:
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(itag)
        if not stream:
            return Response({"error": "Flux vidéo non trouvé avec Pytube"}, status=404)

        # Fonction génératrice pour streamer la vidéo avec Pytube
        def pytube_stream():
            with stream.stream() as file_stream:
                for chunk in iter(lambda: file_stream.read(8192), b''):
                    yield chunk

        # Réponse HTTP en streaming pour Pytube
        response = StreamingHttpResponse(pytube_stream(), content_type='video/mp4')
        response['Content-Disposition'] = f'attachment; filename="{stream.default_filename}"'
        return response

    except Exception as e:
        print(f"Erreur avec Pytube : {str(e)}")

        # Méthode 2 : yt-dlp
        try:
            ydl_opts = {
            'format': f'{itag}',  # Spécifie le format en fonction de l'itag
            'noplaylist': True,   # Désactiver les playlists
            'quiet': True,  # Désactiver les logs
            }

            # Fonction génératrice pour streamer la vidéo avec yt-dlp
            def ytdlp_stream():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(url, download=False)
                
                # Extraire l'URL du flux vidéo correspondant à l'itag
                    video_url = next(
                        (f['url'] for f in result['formats'] if str(f['format_id']) == str(itag)),
                        None
                    )
                
                    if video_url is None:
                        raise Exception("Flux vidéo non trouvé pour cet itag.")

                    # Récupérer la vidéo en streaming avec requests
                    with requests.get(video_url, stream=True) as r:
                        # Vérifier le statut de la réponse
                        r.raise_for_status()

                        # Lire le contenu de la vidéo par morceaux (chunks)
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                yield chunk

            # Réponse HTTP en streaming pour yt-dlp
            response = StreamingHttpResponse(ytdlp_stream(), content_type='video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{itag}_video.mp4"'
            return response


        except Exception as e2:
            print(f"Erreur avec yt-dlp : {str(e2)}")
            return Response({"error": f"Erreur interne : {str(e2)}"}, status=500)
