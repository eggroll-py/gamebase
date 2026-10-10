from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register('games', api_views.GameViewSet, basename='games')
router.register('collection', api_views.CollectionEntryViewSet, basename='collection')
router.register('reviews', api_views.ReviewViewSet, basename='reviews')
router.register('sessions', api_views.PlaySessionViewSet, basename='session')
router.register('prices', api_views.PriceEntryViewSet, basename='prices')

urlpatterns = [
    path('games/search/', api_views.GameSearchView.as_view(), name='game-search'),
    path('recommendations/avg', api_views.AVGRecommendationsView.as_view()),
    path('games/<int:game_id>/similar/', api_views.SimilarGamesView.as_view()),
    path('recommendations/clustered/', api_views.ClusteredRecommendationsView.as_view()),
    path('recommendations/', api_views.MixedRecommendationsView.as_view())


] + router.urls