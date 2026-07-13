from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register('games', api_views.GameViewSet, basename='games')
router.register('collection', api_views.CollectionEntryViewSet, basename='collection')
router.register('reviews', api_views.ReviewViewSet, basename='reviews')
router.register('sessions', api_views.PlaySessionViewSet, basename='session')

urlpatterns = [
    path('games/search/', api_views.GameSearchView.as_view(), name='game-search')

] + router.urls