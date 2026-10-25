from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.utils.cache import add_never_cache_headers
from itertools import chain
from .models import *
from .serializers import *

def get_query_string(request, param):
    query_string = request.query_params.get(param, None)
    try:
        query_string = str(query_string)
    except ValueError:
        query_string = None
    return query_string

class SongView(generics.ListAPIView):

    serializer_class_song = SongSerializer
    def get_queryset(self):
        title = get_query_string(self.request, "title")
        artist = get_query_string(self.request, "artist")
        source = get_query_string(self.request, "source")

        if title != 'None':
            title_queryset = Song.objects.filter(search_title__icontains=title)
        else:
            title_queryset = Song.objects.all()

        if artist != 'None':
            artist_queryset = Song.objects.filter(artist__icontains=artist)
        else:
            artist_queryset = Song.objects.all()

        if source != 'None':
            source_queryset = Song.objects.filter(source_media__icontains=source)
        else:
            source_queryset = Song.objects.all()
            
        return (title_queryset & artist_queryset & source_queryset).distinct()

    def get(self, request, *args, **kwargs):
        songs = self.serializer_class_song(self.get_queryset(), context={'request': request}, many=True).data
        response = Response({})
        response.data = songs
        add_never_cache_headers(response)
        return response