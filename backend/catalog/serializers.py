from django.db import transaction, IntegrityError
from rest_framework import serializers

from catalog.models import Album, Song, Artist, AlbumSong


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['id', 'title', 'year']


class AlbumSongSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='song.title', allow_blank=False)
    song_id = serializers.IntegerField(source='song.id', read_only=True)
    track_number = serializers.IntegerField(read_only=True)

    class Meta:
        model = AlbumSong
        fields = ['track_number', 'title', 'song_id']

    def create(self, validated_data):
        song = validated_data.pop('song')
        album = self.context['album']

        with transaction.atomic():
            song, _ = Song.objects.get_or_create(title=song.get('title'))

            next_track_number = AlbumSong.get_next_track_number(album)

            try:
                album_song = AlbumSong.objects.create(
                    album=album,
                    song=song,
                    track_number=next_track_number
                )
            except IntegrityError as e:
                if getattr(e.__cause__, 'pgcode', None) == '23505':
                    raise serializers.ValidationError('Эта песня уже добавлена в альбом или '
                                                      'песня c таким порядковым номером уже добавлена в другой альбом')
                raise

        return album_song


class SongSerializer(serializers.ModelSerializer):
    song_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Song
        fields = ['title', 'song_id']
