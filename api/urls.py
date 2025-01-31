from django.urls import path
from .views import get_video_streams, download_video_by_itag

urlpatterns = [
    path('streams/', get_video_streams, name='get_video_streams'),
    path('download/', download_video_by_itag, name='download_video'),
]
