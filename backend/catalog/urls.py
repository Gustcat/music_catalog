from django.urls import include, path
from rest_framework_nested import routers

from .views import (
    ArtistViewSet,
    AlbumViewSet,
    SongViewSet
    )

app_name = 'catalog'

router = routers.DefaultRouter()
router.register(r'artists', ArtistViewSet)

artists_router = routers.NestedDefaultRouter(router, r'artists', lookup='artist')
artists_router.register(r'albums', AlbumViewSet, basename='artist-albums')

albums_router = routers.NestedDefaultRouter(artists_router, r'albums', lookup='album')
albums_router.register(r'songs', SongViewSet, basename='artist-album-songs')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(artists_router.urls)),
    path('', include(albums_router.urls)),
]

