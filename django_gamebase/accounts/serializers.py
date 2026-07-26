from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg
from games.models import Game, CollectionEntry, Genre, PlaySession, Review

User = get_user_model()

class UserStatsSerializer(serializers.Serializer):
    total_games = serializers.IntegerField()
    games_by_status = serializers.DictField(child=serializers.IntegerField())
    total_sessions = serializers.IntegerField()
    total_minutes = serializers.IntegerField()
    reviews_written = serializers.IntegerField()
    average_rating = serializers.DecimalField(allow_null=True, max_digits=3, decimal_places=1)
    favourite_genre = serializers.CharField(allow_null=True)

class UserProfileSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'avatar_url', 'favourite_platform', 'date_joined', 'stats']
        read_only_fields = ['username', 'email', 'date_joined']

    def get_stats(self, obj):
        gbs_query = CollectionEntry.objects.values('status').filter(user=obj).annotate(Count('id'))
        games_by_status = {item['status']: item['count'] for item in gbs_query}
        total_games = sum(games_by_status.values())
        total_sessions = PlaySession.objects.filter(user=obj).aggregate(total=Count('id'), duration_minutes=Sum('duration_minutes'))
        total_reviews = Review.objects.filter(user=obj).aggregate(total_reviews=Count('id'),avg_rating=Avg('rating'))
        favourite_genre = Genre.objects.filter(games__collection_entries__user=obj).annotate(count=Count('games__collection_entries')).order_by('-count').first()

        stats = {
            'total_games': total_games,
            'games_by_status': games_by_status,
            'total_sessions': total_sessions['total'] or 0,
            'total_minutes': total_sessions['duration_minutes'] or 0,
            'reviews_written': total_reviews['total_reviews'] or 0,
            'average_rating': total_reviews['avg_rating'],
            'favourite_genre': favourite_genre or None
        }
        return UserStatsSerializer(stats).data

class UserPublicSerializer(serializers.ModelSerializer):
    collection_summary = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'bio', 'avatar_url', 'favourite_platform', 'date_joined', 'collection_summary']
        read_only_fields = fields

    def get_collection_summary(self, obj):
        entries = CollectionEntry.objects.filter(user=obj)

        top_genres = Genre.objects.filter(games__collection_entries__user=obj).annotate(count=Count('games__collection_entries')).order_by('-count')[:3]

        return {
            'total_games': entries.count(),
            'completed': entries.filter(status='completed').count(),
            'playing': entries.filter(status='playing').count(),
            'top_genres': [g.name for g in top_genres]
        }














