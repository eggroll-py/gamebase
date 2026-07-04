from django.contrib import admin
from .models import Game, CollectionEntry, Review, Platform, Genre, PlaySession, PriceEntry

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['title', 'igdb_id', 'last_synced']
    search_fields = ['title']
    list_filter = ['platforms', 'genres']

@admin.register(CollectionEntry)
class CollectionEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'status']
    list_filter = ['status']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'rating']

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Genre)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(PlaySession)
admin.site.register(PriceEntry)

