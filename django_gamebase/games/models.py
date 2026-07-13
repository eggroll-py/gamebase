from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Game(models.Model):
    igdb_id = models.IntegerField(unique=True)
    title = models.TextField()
    slug = models.SlugField(unique=True)
    cover_url = models.URLField(blank=True, null=True)
    summary = models.TextField(blank=True)
    release_date = models.DateField(null=True)
    igdb_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    platforms = models.ManyToManyField('Platform')
    genres = models.ManyToManyField('Genre')
    last_synced = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Platform(models.Model):
    igdb_id = models.IntegerField(unique=True)
    name = models.TextField()
    slug = models.SlugField(unique=True)
    def __str__(self):
        return self.name

class Genre(models.Model):
    igdb_id = models.IntegerField(unique=True)
    name = models.TextField()
    slug = models.SlugField(unique=True)
    def __str__(self):
        return self.name

class GameStatus(models.TextChoices):
    PLAYING = 'playing', 'Playing'
    COMPLETED = 'completed', 'Completed'
    DROPPED = 'dropped', 'Dropped'
    WANT = 'want', 'Want'
    BACKLOG = 'backlog', 'Backlog'

class CollectionEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
    related_name='collection', on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name='collection_entries', on_delete=models.CASCADE)
    status = models.TextField(choices=GameStatus.choices)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f'{self.user} - {self.game}'

class PlaySession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True)
    duration_minutes = models.PositiveIntegerField(null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.user} - {self.game}'

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    contains_spoilers = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f'{self.game} - {self.rating}'

class Store(models.TextChoices):
    STEAM = 'steam', 'Steam'
    PSN = 'psn', 'PSN'
    NINTENDO = 'nintendo', 'Nintendo'
    XBOX = 'xbox', 'Xbox'


class PriceEntry(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    store = models.TextField(choices=Store.choices)
    price = models.DecimalField
    currency = models.TextField(default='EUR')
    fetched_at = models.DateTimeField(auto_now_add=True)
    is_on_sale = models.BooleanField(default=False)
    original_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    def __str__(self):
        return f'{self.game} - {self.price}'




