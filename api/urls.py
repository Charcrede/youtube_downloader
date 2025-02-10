from django.urls import path
from .views import get_video_info, download_video

urlpatterns = [
    path('streams/', get_video_info, name='get_video_streams'),
    path('download/', download_video, name='download_video'),
]
