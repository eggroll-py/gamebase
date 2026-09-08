from unittest.mock import patch, MagicMock
from django.test import TestCase
from games.psn_client import resolve_psn_product_id

def make_mock_response(json_data):
    mock_response = MagicMock()
    mock_response.json.return_value = json_data
    return mock_response

@patch('games.psn_client.requests.post')
class ResolvePsnProductIdTest(TestCase):
    def test_finds_exact_concept_id_match(self, mock_post):
        mock_post.return_value = make_mock_response({
            'results': [{'hits': [
                {'conceptId': '10018449', 'skuIds': ['SOME-ID-0912328937643383-E001']},
                {'conceptId': '10002648', 'skuIds': ['EP4484-PPSA03711_00-3235764131417729-E003']},
            ]}]
        })

        result = resolve_psn_product_id('10002648', 'Hades')
        self.assertEqual(result, 'EP4484-PPSA03711_00-3235764131417729')

    def test_returns_none_when_no_matching_concept_id(self, mock_post):
        mock_post.return_value = make_mock_response({
            'results': [{'hits': [{'conceptId': '99999999', 'skuIds': ['irrelevant-E001']}]}]
        })
        result = resolve_psn_product_id('10002648', 'Hades')
        self.assertIsNone(result)

    def test_returns_none_when_hit_has_no_sku_ids(self, mock_post):
        mock_post.return_value = make_mock_response({
            'results': [{'hits': [{'conceptId': '10002648', 'skuIds': []}]}]
        })
        result = resolve_psn_product_id('10002648', 'Hades')
        self.assertIsNone(result)

