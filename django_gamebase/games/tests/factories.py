import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from games.models import Game, Review, CollectionEntry, PlaySession

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda n: f'{n.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Game

    title = factory.Sequence(lambda n: f'Game {n}')
    igdb_id = factory.Sequence(lambda n: n + 1000)
    slug = factory.LazyAttribute(lambda o: f'game-{o.igdb_id}')
    last_synced = factory.LazyFunction(timezone.now)

class CollectionEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CollectionEntry

    user = factory.SubFactory(UserFactory)
    game = factory.SubFactory(GameFactory)
    status = 'playing'

class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    user = factory.SubFactory(UserFactory)
    game = factory.SubFactory(GameFactory)
    rating = 7
    body = 'test review body'

class PlaySessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PlaySession

    user = factory.SubFactory(UserFactory)
    game = factory.SubFactory(GameFactory)
    started_at = factory.LazyFunction(timezone.now)
    duration_minutes = 60






