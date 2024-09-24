from django.urls import path
from .views import SearchVideos

urlpatterns = [
    path('search-videos/', SearchVideos.as_view(), name='search_videos'),
]