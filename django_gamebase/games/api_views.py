from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Avg, Sum, Min, Max, prefetch_related_objects
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .models import Game, Review, CollectionEntry, PlaySession, PriceEntry
from .serializers import GameListSerializer, GameDetailSerializer, ReviewSerializer, CollectionEntrySerializer, PlaySessionSerializer, PriceEntrySerializer
from .igdb_import import search_and_import
from .embeddings import get_avg_recommendations, get_clustered_recommendations, get_mixed_reccs, get_similar_games

class GameSearchView(GenericAPIView):
    #GET /api/games/search/?q=query
    serializer_class = GameListSerializer
    def get(self, request):
        query = request.query_params.get('q', '').strip()

        if not query:
            return Response({'error': 'Search query "q" is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if len(query) < 2:
            return Response({'error': 'Search query must be at least 2 characters'}, status=status.HTTP_400_BAD_REQUEST)

        local_results = Game.objects.filter(title__icontains=query).prefetch_related('genres', 'platforms')

        if local_results.exists():
            serializer = self.get_serializer(local_results, many=True)
            return Response({'source': 'cached',
                         'results': serializer.data})

        try:
            games = search_and_import(query)
        except Exception as e:
            return Response({'error': 'Could not reach IGDB. Please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        prefetch_related_objects(games, 'genres', 'platforms')
        serializer = self.get_serializer(games, many=True)
        return Response({'source': 'igdb',
                         'results': serializer.data})

class GameViewSet(ModelViewSet):
    queryset = Game.objects.prefetch_related('genres', 'platforms').all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GameDetailSerializer
        return GameListSerializer

    http_method_names = ['get', 'head', 'options']

@action(detail=True, methods=['get'], url_path='reviews')
def reviews(self, request, pk=None):
    #GET /api/games/<pk>/reviews/
    game = self.get_object()
    reviews = Review.objects.filter(game=game).select_related('user')
    serializer = ReviewSerializer(reviews, many=True)

    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    return Response({
        'average_rating': round(avg_rating, 1) if avg_rating else None,
        'review_count': reviews.count(),
        'reviews': serializer.data
    })

@action(detail=True, methods=['get'], url_path='price-summary')
def price_summary(self, request, pk=None):
    game = self.get_object()
    entries = PriceEntry.objects.filter(game=game)

    if not entries.exists():
        return Response(f'No price entries for {game.title} yet')

    aggregates = entries.aggregate(
        lowest=Min('price'),
        highest=Max('price'),
        last_updated=Max('fetched_at'))

    on_sale_count = entries.filter(is_on_sale=True).count()
    stores = [{
        'store': entry.store,
        'price': entry.price,
        'is_on_sale': entry.is_on_sale,
        'url': entry.url
    } for entry in entries.order_by('price')]

    return Response({
        'game_title': game.title,
        'lowest_price': aggregates['lowest'],
        'highest_price': aggregates['highest'],
        'on_sale_count': on_sale_count,
        'stores': stores,
        'last_updated': aggregates['last_updated']
    })






class CollectionEntryViewSet(ModelViewSet):
    # /api/collection/
    serializer_class = CollectionEntrySerializer
    permission_classes = [IsAuthenticated]
    queryset = CollectionEntry.objects.none()

    def get_queryset(self):
        return CollectionEntry.objects.filter(user=self.request.user).select_related('game').prefetch_related('game__genres', 'game__platforms')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.select_related('user','game').all()
        game_id = self.request.query_params.get('game')
        if game_id:
            queryset = queryset.filter(game=game_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != self.request.user:
            return Response({'You can only edit your own reviews'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != self.request.user:
            return Response({'You can only delete your own reviews'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class PlaySessionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PlaySessionSerializer
    queryset = PlaySession.objects.none()

    def get_queryset(self):
        return PlaySession.objects.filter(user=self.request.user).select_related('game').order_by('-started_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        sessions = PlaySession.objects.filter(user=self.request.user)
        total_sessions = sessions.count()
        total_minutes = sessions.aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
        games_played = sessions.values('game').distinct().count()

        return Response({
            'total_sessions': total_sessions,
            'total_minutes': total_minutes,
            'games_played': games_played
        })

class PriceEntryViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PriceEntrySerializer
    http_method_names = ['get', 'head', 'options']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['game']

    def get_queryset(self):
        return PriceEntry.objects.select_related('game').all()


class AVGRecommendationsView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GameListSerializer

    def get(self, request):
        games = get_avg_recommendations(request.user)
        prefetch_related_objects(games, 'genres', 'platforms')
        serializer = self.get_serializer(games, many=True)
        return Response(serializer.data)

class ClusteredRecommendationsView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GameListSerializer

    def get(self, request):
        clusters = get_clustered_recommendations(request.user)
        all_games = [game for cluster in clusters for game in cluster]
        prefetch_related_objects(all_games, 'genres', 'platforms')
        serialized = [self.get_serializer(cluster, many=True).data for cluster in clusters]
        return Response(serialized)

class MixedRecommendationsView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GameListSerializer

    def get(self, request):
        games = get_mixed_reccs(request.user)
        prefetch_related_objects(games, 'genres', 'platforms')
        serializer = self.get_serializer(games, many=True)
        return Response(serializer.data)

class SimilarGamesView(GenericAPIView):
    serializer_class = GameListSerializer

    def get(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        results = get_similar_games(game)
        prefetch_related_objects(results, 'genres', 'platforms')
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)










