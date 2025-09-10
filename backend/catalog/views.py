from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from catalog.models import Artist, Album, AlbumSong, Song
from catalog.serializers import ArtistSerializer, AlbumSerializer, AlbumSongSerializer, SongSerializer


class ArtistViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()


class AlbumViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = AlbumSerializer

    def get_queryset(self):
        return Album.objects.filter(artist_id=self.kwargs.get('artist_pk'))

    def perform_create(self, serializer):
        artist = get_object_or_404(Artist, pk=self.kwargs.get('artist_pk'))
        serializer.save(artist=artist)


class SongViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ["partial_update"]:
            return SongSerializer
        return AlbumSongSerializer

    def get_queryset(self):
        if self.action in ["partial_update"]:
            return Song.objects.filter(albums__album=self.kwargs.get('album_pk'))
        return AlbumSong.objects.filter(album_id=self.kwargs.get('album_pk'))

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if getattr(self, 'swagger_fake_view', False):
            return context

        context['album'] = get_object_or_404(Album, pk=self.kwargs.get('album_pk'))
        return context

    @swagger_auto_schema(operation_description='Удаляет песню из альбома.'
                                               'Если песня была только в этом альбоме, она тоже удаляется.')
    def destroy(self, request, *args, **kwargs):
        album_pk = kwargs.get('album_pk')
        song_pk = kwargs.get('pk')
        album_song = get_object_or_404(AlbumSong, album_id=album_pk, song_id=song_pk)

        with transaction.atomic():
            album_song.delete()
            if not AlbumSong.objects.filter(song_id=song_pk).exists():
                Song.objects.filter(pk=song_pk).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(operation_description='Добавляет песню в альбом.'
                                               'Трек получает порядковый номер, следующий за максимальным.'
                                               'Если песни с таким названием нет в другом альбоме она создается.')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
