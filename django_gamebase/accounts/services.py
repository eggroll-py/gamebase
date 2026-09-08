from .models import Visibility
from django.db.models import Count, Sum, Avg
from games.models import Game, CollectionEntry, Genre, PlaySession, Review


def can_view_profile(viewer, profile_owner) -> bool:
    if viewer.is_authenticated and viewer.id == profile_owner.id:
        return True

    visibility = profile_owner.profile_visibility
    if visibility == Visibility.PUBLIC:
        return True
    if visibility == Visibility.PRIVATE:
        return False
    if visibility == Visibility.FOLLOWERS:
        return False #will come back once feat. is added

    return False

def get_user_stats(user) -> dict:
    gbs_query = CollectionEntry.objects.values('status').filter(user=user).annotate(count=Count('id'))
    games_by_status = {item['status']: item['count'] for item in gbs_query}
    total_games = sum(games_by_status.values())
    total_sessions = PlaySession.objects.filter(user=user).aggregate(total=Count('id'), duration_minutes=Sum('duration_minutes'))
    total_reviews = Review.objects.filter(user=user).aggregate(total_reviews=Count('id'),avg_rating=Avg('rating'))
    favourite_genre = Genre.objects.filter(games__collection_entries__user=user).annotate(count=Count('games__collection_entries')).order_by('-count').first()

    return {
        'total_games': total_games,
        'games_by_status': games_by_status,
        'total_sessions': total_sessions['total'] or 0,
        'total_minutes': total_sessions['duration_minutes'] or 0,
        'reviews_written': total_reviews['total_reviews'] or 0,
        'average_rating': total_reviews['avg_rating'],
        'favourite_genre': favourite_genre.name if favourite_genre else None
    }