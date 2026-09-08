from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg
from games.models import Game, CollectionEntry, Genre, PlaySession, Review
from accounts.services import get_user_stats

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
        return UserStatsSerializer(get_user_stats(obj)).data

class UserPublicSerializer(serializers.ModelSerializer):
    collection_summary = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'bio', 'avatar_url', 'favourite_platform', 'date_joined', 'collection_summary']
        read_only_fields = fields

    def get_collection_summary(self, obj):
        stats = get_user_stats(obj)

        return {
            'total_games': stats['total_games'],
            'completed': stats['games_by_status'].get('completed', 0),
            'playing': stats['games_by_status'].get('playing', 0),
            'favourite_genre': stats['favourite_genre']
        }














