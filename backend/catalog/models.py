from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Max
from django.utils import timezone


class Artist(models.Model):
    name = models.CharField(max_length=200, verbose_name='Имя', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'


class Album(models.Model):
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="albums",
        verbose_name='Исполнитель'
    )
    title = models.CharField(max_length=200, verbose_name='Название альбома', unique=True)
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(timezone.now().year)
        ],
        verbose_name='Год выпуска'
    )

    class Meta:
        ordering = ["-year"]
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'

    def __str__(self):
        return f"{self.title} ({self.artist.name})"


class Song(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название песни', unique=True)

    class Meta:
        verbose_name = 'Песня'
        verbose_name_plural = 'Песни'

    def __str__(self):
        return f"{self.title}"


class AlbumSong(models.Model):
    album: Album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="songs",
        verbose_name='Альбом'
    )
    song: Song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name="albums",
        verbose_name='Песня'
    )
    track_number = models.PositiveSmallIntegerField(verbose_name='Номер трека')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['album', 'song', 'track_number'],
                name='unique_track_number_song_album'
            ),
            models.UniqueConstraint(
                fields=['album', 'song'],
                name='unique_song_album'
            )
        ]
        verbose_name = 'Песня в альбоме'
        verbose_name_plural = 'Песни в альбомах'

    def __str__(self):
        return f"{self.track_number}. {self.song.title} ({self.album.title})"

    @classmethod
    def get_next_track_number(cls, album):
        max_num = cls.objects.filter(album=album).aggregate(max_num=Max('track_number'))['max_num'] or 0
        return max_num + 1
