from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Avg, Sum
from rest_framework.decorators import action

from .models import Game, Review, CollectionEntry, PlaySession
from .serializers import GameListSerializer, GameDetailSerializer, ReviewSerializer, CollectionEntrySerializer, PlaySessionSerializer
from .igdb_import import search_and_import

class GameSearchView(APIView):
    #GET /api/games/search/?q=query
    def get(self, request):
        permission_classes = [IsAuthenticatedOrReadOnly]
        query = request.query_params.get('q', '').strip()

        if not query:
            return Response({'error': 'Search query "q" is required.'}, status=status.HTTP_400_BAD_REQUEST)

        local_results = Game.objects.filter(title__icontains=query).prefetch_related('genres', 'platforms')

        if local_results.exists():
            serializer = GameListSerializer(local_results, many=True)
            return Response({'source': local_results,
                         'results': serializer.data})

        try:
            games = search_and_import(query)
        except Exception as e:
            return Response({'error': 'Could not reach IGDB. Please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        serializer = GameListSerializer(games, many=True)
        return Response({'source': 'igdb',
                         'results': serializer.data})

class GameViewSet(ModelViewSet):
    queryset = Game.objects.prefetch_related('genres', 'platforms').all()
    permission_class = [IsAuthenticatedOrReadOnly]

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

class CollectionEntryViewSet(ModelViewSet):
    # /api/collection/
    serializer_class = CollectionEntrySerializer
    permission_classes = [IsAuthenticated]
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

    def get_queryset(self):
        return PlaySession.objects.filter(user=self.request.user).select_related('game').order_by('-started_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        sessions = PlaySession.objects.filter(user=self.request.user).all()
        total_sessions = sessions.count()
        total_minutes = sessions.aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
        games_played = sessions.values('game').distinct().count()

        return Response({
            'total_sessions': total_sessions,
            'total_minutes': total_minutes,
            'games_played': games_played
        })




