from unittest.mock import MagicMock, patch
from django.test import TestCase
from games.igdb_import import import_game_from_igdb_data
from games.models import Game

GAME_DATA = {
    'igdb_id': 999,
    'title': 'Test Game',
    'cover_url': None,
    'summary': '',
    'release_date': None,
    'igdb_rating': None,
    'genres': [],
    'platforms': [],
}


@patch('games.igdb_import.igdb_client.get_external_ids')
@patch('games.igdb_import.resolve_psn_product_id')
@patch('games.igdb_import.resolve_eshop_id')
class ImportGameFromIGDBDataTest(TestCase):
    def test_external_ids_wire_correctly(self, mock_eshop, mock_psn, mock_get_ids):
        mock_get_ids.return_value = {'steam_id': 220, 'psn_id': '10002648', 'amazon_id': None}
        mock_psn.return_value = 'EP4484-PPSA03711_00-3235764131417729'
        mock_eshop.return_value = {
            'eshop_id': '70010000033132', 'eshop_verified': True,
            'eshop_url': 'https://www.nintendo.com/au/games/hades/',
        }

        game = import_game_from_igdb_data(GAME_DATA)
        self.assertEqual(game.steam_id, 220)
        self.assertEqual(game.psn_id, '10002648')
        self.assertEqual(game.psn_product_id, 'EP4484-PPSA03711_00-3235764131417729')
        self.assertEqual(game.eshop_id, '70010000033132')
        self.assertTrue(game.eshop_verified)

    def test_handles_no_external_ids_smoothly(self, mock_eshop, mock_psn, mock_get_ids):
        mock_get_ids.return_value = {'steam_id': None, 'psn_id': None, 'amazon_id': None}
        mock_psn.return_value = None
        mock_eshop.return_value = {'eshop_id': None, 'eshop_verified': False, 'eshop_url': None}

        game = import_game_from_igdb_data(GAME_DATA)

        self.assertIsNone(game.steam_id)
        self.assertIsNone(game.psn_product_id)
        self.assertIsNone(game.eshop_id)
        self.assertFalse(game.eshop_verified)


