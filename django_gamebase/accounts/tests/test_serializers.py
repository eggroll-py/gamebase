from django.test import TestCase
from django.contrib.auth import get_user_model
from games.tests.factories import UserFactory, CollectionEntryFactory, GameFactory, PlaySessionFactory, ReviewFactory
from accounts.serializers import UserProfileSerializer

User = get_user_model()

class UserStatsSerializerTest(TestCase):
    def setUp(self):
        self.user1 = UserFactory()
        self.game1 = GameFactory()
        self.game2 = GameFactory()
        self.game3 = GameFactory()
        self.entry1 = CollectionEntryFactory(user=self.user1, game=self.game1, status='completed')
        self.entry2 = CollectionEntryFactory(user=self.user1, game=self.game2, status='playing')
        self.session1 = PlaySessionFactory(user=self.user1, game=self.game1, duration_minutes=120)
        self.review1 = ReviewFactory(user=self.user1, game=self.game1, rating=8)

        self.serializer = UserProfileSerializer(self.user1)
        self.stats = self.serializer.data['stats']

    def test_total_games_count(self):
        self.assertEqual(self.stats['total_games'], 2)

    def test_games_by_status_breakdown(self):
        self.assertEqual(self.stats['games_by_status']['completed'], 1)
        self.assertEqual(self.stats['games_by_status']['playing'], 1)

    def test_total_minutes(self):
        self.assertEqual(self.stats['total_minutes'], 120)

    def test_reviews_written(self):
        self.assertEqual(self.stats['reviews_written'], 1)

    def test_average_rating(self):
        self.assertEqual(self.stats['average_rating'], '8.0')

    def test_empty_stats_for_new_user(self):
        user2 = UserFactory()
        serialized = UserProfileSerializer(user2)
        self.assertEqual(serialized.data['stats']['total_games'], 0)
        self.assertEqual(serialized.data['stats']['total_minutes'], 0)
        self.assertIsNone(serialized.data['stats']['favourite_genre'])



