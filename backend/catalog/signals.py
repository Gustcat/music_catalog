from django.db.models.signals import pre_delete
from django.dispatch import receiver

from catalog.models import Album, AlbumSong


@receiver(pre_delete, sender=Album)
def delete_songs_with_album(sender, instance, **kwargs):
    for album_song in instance.songs.all():
        song = album_song.song
        if AlbumSong.objects.filter(song=song).exclude(album=instance).exists() is False:
            song.delete()
