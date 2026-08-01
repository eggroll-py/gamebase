from unittest.mock import patch, MagicMock
from django.test import TestCase
from games.igdb_client import search_games, get_game_by_igdb_id, _build_cover_url


MOCK_GAME = {
    'id': 5,
    'name': 'Splatoon',
    'cover_url': '',
    'first_release_date': 156648,
    'genres': [],
    'platforms': []

}

def make_mock_response(json_data):
    mock_response = MagicMock()
    mock_response.json.return_value = json_data
    mock_response.status_code.return_value = None
    return mock_response



class IGDBClient(TestCase):
    @patch('games.igdb_client.requests.post')
    def test_search_games_returns_parsed_list(self, mock_post):
        mock_post.return_value = make_mock_response([MOCK_GAME])
        results = search_games('Splatoon')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['igdb_id'], 5)
        self.assertEqual(results[0]['title'], 'Splatoon')

    @patch('games.igdb_client.requests.post')
    def test_search_games_calls_correct_endpoint(self, mock_post):
        mock_post.return_value = make_mock_response([MOCK_GAME])
        results = search_games('Hades')
        mock_post.assert_called_once()
        url_called = mock_post.call_args[0][0]
        self.assertIn('games', url_called)

    @patch('games.igdb_client.requests.post')
    def test_get_game_by_igdb_id(self, mock_post):
        mock_post.return_value = make_mock_response([])
        result = get_game_by_igdb_id(99999)

        self.assertEqual(result, None)

    @patch('games.igdb_client.requests.post')
    def test_cover_url_transformation(self, mock_post):
        url = _build_cover_url('www.t_thumb.com')
        self.assertIn('t_cover_big', url)

    @patch('games.igdb_client.requests.post')
    def test_cover_url_none_input(self, mock_post):
        result = _build_cover_url(None)
        self.assertIsNone(result)





