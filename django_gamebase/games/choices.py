from django.db import models

class GameType(models.IntegerChoices):
    MAIN_GAME = 0, 'Main Game'
    DLC = 1, 'DLC'
    EXPANSION = 2, 'Expansion'
    BUNDLE = 3, 'Bundle'
    STANDALONE_EXPANSION = 4, 'Standalone Expansion'
    MOD = 5, 'Mod'
    EPISODE = 6, 'Episode'
    SEASON = 7, 'Season'
    REMAKE = 8, 'Remake'
    REMASTER = 9, 'Remaster'
    EXPANDED_GAME = 10, 'Expanded Game'
    PORT = 11, 'Port'
    FORK = 12, 'Fork'
    PACK = 13, 'Pack / Addon'
    UPDATE = 14, 'Update'

class GameStatus(models.TextChoices):
    PLAYING = 'playing', 'Playing'
    COMPLETED = 'completed', 'Completed'
    DROPPED = 'dropped', 'Dropped'
    WANT = 'want', 'Want'
    BACKLOG = 'backlog', 'Backlog'

class Store(models.TextChoices):
    STEAM = 'steam', 'Steam'
    PSN = 'psn', 'PSN'
    NINTENDO = 'nintendo', 'Nintendo'
    XBOX = 'xbox', 'Xbox'
