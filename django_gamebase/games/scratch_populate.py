from accounts.models import User
from games.models import Game, Review, CollectionEntry

def populate():
    user = User.objects.get(username='testuser1')

    reviews_by_rating = {
        7: ['StarCraft', 'Resident Evil'],
        8: ['Pico Valley'],
        9: ['Catherine', 'Grim Fandango']
    }

    for rating, titles in reviews_by_rating.items():
        games = Game.objects.filter(title__in=titles)

        for game in games:
            Review.objects.update_or_create(user=user, game=game, defaults={'rating': rating})
