from django.urls import path
from .views import *

urlpatterns = [
    path('data', SongView.as_view(), name='song_data'),
]