from unittest.mock import patch, MagicMock
from django.test import TestCase
from datetime import date
from games.eshop_client import resolve_eshop_id
from games.tests.factories import GameFactory, PlatformFactory

def make_mock_response(json_data):
    mock_response = MagicMock()
    mock_response.json.return_value = json_data
    return mock_response

@patch('games.eshop_client.requests.post')
class ResolveEshopIdTest(TestCase):
    def setUp(self):
        self.switch = PlatformFactory(name='Nintendo Switch')
        self.game = GameFactory(title='Hades', release_date=date(2020, 9, 17))
        self.game.platforms.add(self.switch)

    def test_all_three_checks_pass_verified(self, mock_post):
        mock_post.return_value = make_mock_response({'results': [{'hits': [
            {'title': 'Hades', 'console': 'Nintendo Switch', 'dateTag': {'year': 2020}, 'nsuid': '70010000033132'}
        ]}]})
        result = resolve_eshop_id(self.game)
        self.assertEqual(result['eshop_id'], '70010000033132')
        self.assertTrue(result['eshop_verified'])

    def test_title_only_match_not_verified(self, mock_post):
        mock_post.return_value = make_mock_response({'results': [{'hits': [
            {'title': 'Hades', 'console': 'PlayStation 5', 'dateTag': {'year': 1995}, 'nsuid': 'wrong-game-id'}
        ]}]})
        result = resolve_eshop_id(self.game)
        nsuid = result['eshop_id']
        verified = result['eshop_verified']
        self.assertFalse(verified)

    def test_handles_datetag_as_plain_string(self, mock_post):
        mock_post.return_value = make_mock_response({'results': [{'hits': [
            {'title': 'Hades', 'console': 'Nintendo Switch', 'dateTag': '2020', 'nsuid': '70010000033132'}
        ]}]})
        result = resolve_eshop_id(self.game)
        nsuid = result['eshop_id']
        verified = result['eshop_verified']
        self.assertTrue(verified)

    def test_no_hits_returns_none_unverified(self, mock_post):
        mock_post.return_value = make_mock_response({'results': [{'hits': []}]})
        result = resolve_eshop_id(self.game)
        nsuid = result['eshop_id']
        verified = result['eshop_verified']
        self.assertIsNone(nsuid)
        self.assertFalse(verified)