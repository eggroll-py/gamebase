from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from games.models import CollectionEntry
from games.tests.factories import GameFactory, UserFactory, CollectionEntryFactory

class CollectionEntryViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.game1 = GameFactory()
        self.game2 = GameFactory()
        self.game3 = GameFactory()
        self.collection_entry1 = CollectionEntryFactory(user=self.user1, game=self.game1, status='completed')
        self.collection_entry2 = CollectionEntryFactory(user=self.user1, game=self.game2, status='want')
        self.collection_entry3 = CollectionEntryFactory(user=self.user2, game=self.game3, status='playing')

    def authenticate(self, user):
        token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_list_returns_only_own_entries(self):
        self.authenticate(self.user1)
        response = self.client.get(reverse('collection-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data),2)
        result_ids = [entry['id'] for entry in response.data]
        self.assertNotIn(self.collection_entry3.id, result_ids)

    def test_unauthenticated_request_returns_401(self):
        response = self.client.get(reverse('collection-list'))
        self.assertEqual(response.status_code, 401)

    def test_create_entry_sets_correct_user(self):
        self.authenticate(self.user1)
        response = self.client.post(reverse('collection-list'),{'game_id': self.game3.id, 'status': 'playing'}, format='json')
        self.assertEqual(response.status_code, 201)
        created = CollectionEntry.objects.get(pk=response.data['id'])
        self.assertEqual(created.user, self.user1)

    def test_cannot_create_duplicate_entry(self):
        self.authenticate(self.user1)
        response = self.client.post(reverse('collection-list'),{'game_id': self.game1.id, 'status': 'playing'}, format='json')
        self.assertEqual(response.status_code, 400)

class GameSearchViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_search_without_query_returns_400(self):
        response = self.client.get(reverse('game-search'))
        self.assertEqual(response.status_code, 400)

    def test_search_with_short_query_returns_400(self):
        response = self.client.get(reverse('game-search'), {'q': 'a'})
        self.assertEqual(response.status_code, 400)

    @patch('games.igdb_client.requests.post')
    def test_search_returns_cached_results_when_game_exists(self, mock_post):
        game = GameFactory(title='Hades')
        response = self.client.get(reverse('game-search'),{'q': 'Hades'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['source'], 'cached')
        mock_post.assert_not_called()

    @patch('games.api_views.search_and_import')
    def test_search_calls_igdb_when_game_not_in_database(self, mock_import):
        game = GameFactory()
        mock_import.return_value = [game]
        response = self.client.get(reverse('game-search'),{'q':'SomeGame'})
        self.assertEqual(response.status_code, 200)
        print(response.data['source'])
        self.assertEqual(response.data['source'], 'igdb')
        mock_import.assert_called_once_with('SomeGame')















