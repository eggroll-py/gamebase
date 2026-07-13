from rest_framework import serializers
from .models import Game, Platform, Genre, CollectionEntry, GameStatus, Review, PlaySession

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'igdb_id', 'name', 'slug']

class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['id', 'igdb_id', 'name', 'slug']

class GameListSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    platforms = PlatformSerializer(many=True, read_only=True)

    class Meta:
        model = Game

        fields = ['id', 'igdb_id', 'title', 'slug', 'cover_url', 'release_date', 'igdb_rating', 'genres', 'platforms']

class GameDetailSerializer(serializers.ModelSerializer):

    genres = GenreSerializer(many=True, read_only=True)
    platforms = PlatformSerializer(many=True, read_only=True)
    class Meta:
        model = Game
        fields = ['id', 'igdb_id', 'title', 'slug', 'cover_url', 'summary', 'release_date', 'igdb_rating', 'genres', 'platforms', 'last_synced']

class CollectionEntrySerializer(serializers.ModelSerializer):
    game = GameListSerializer(read_only=True)
    game_id = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all(), source='game', write_only=True)

    class Meta:
        model = CollectionEntry
        fields = ['id', 'game', 'game_id', 'status', 'added_at', 'updated_at']
        read_only_fields = ['id', 'added_at', 'updated_at']

    def validate_status(self, value):
        valid = GameStatus.values
        if value not in valid:
            raise serializers.ValidationError(f'Status must be one of: {valid}')
        return value

class ReviewSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='user.username', read_only=True)
    game_title = serializers.CharField(source='game.title', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'game', 'author_username', 'game_title', 'rating', 'body', 'contains_spoilers', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author_username' 'game_title', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError('Rating must be between 1 and 10')
        return value

class PlaySessionSerializer(serializers.ModelSerializer):
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all(), write_only=True)
    game_title = serializers.CharField(source='game.title', read_only=True)
    class Meta:
        model = PlaySession
        fields = ['id', 'game', 'game_title', 'started_at', 'ended_at', 'duration_minutes', 'notes']
        read_only_fields = ['id', 'game_title']

    def validate(self, data):
        start = data.get('started_at')
        end = data.get('ended_at')
        if start and end and start >= end:
            return serializers.ValidationError('Start time cannot be greater than End time')
        return data





