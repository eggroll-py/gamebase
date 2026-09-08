from unittest.mock import patch, MagicMock
from decimal import Decimal
from app.price_clients import get_steam_price, get_psn_price, get_eshop_price

def make_mock_response(json_data):
    mock_response = MagicMock()
    mock_response.json.return_value = json_data
    return mock_response

@patch('app.price_clients.requests.get')
class TestSteamPriceClient:
    def test_get_steam_price_parses_normal_price(self, mock_get):
        mock_get.return_value = make_mock_response({
          "220": {
            "success": True,
            "data": {
              "price_overview": {
                "currency": "EUR",
                "initial": 975,
                "final": 975,
                "discount_percent": 0,
              }
            }
          }
        })

        result = get_steam_price(220)
        assert result['store'] == 'steam'
        assert result['currency'] == 'EUR'
        assert result['on_sale'] == False


    def test_get_steam_price_returns_correct_for_free_game(self, mock_get):
        mock_get.return_value = make_mock_response({
          "570": {
            "success": True,
            "data": []
          }
        })
        result = get_steam_price(570)
        assert result['price'] == Decimal(0)
        assert result['on_sale'] is False

    def test_get_steam_price_returns_none_when_not_found(self, mock_get):
        mock_get.return_value = make_mock_response({
          "122634449": {
            "success": False,
          }
        })
        result = get_steam_price(122634449)
        assert result is None

@patch('app.price_clients.requests.get')
class TestPSNPriceClient:
    def test_get_psn_price_parses_normal_price(self, mock_get):
        mock_get.return_value = make_mock_response({
      "data": {
        "productRetrieve": {
          "webctas": [
            {
              "price": {
                "basePriceValue": 1999,
                "discountedValue": 1999,
                "currencyCode": "GBP",
              }
            }
          ]
        }
      }
    })
        result = get_psn_price('EP4484-PPSA03711_00-3235764131417729')
        assert result['store'] == 'psn'
        assert result['price'] == Decimal('19.99')
        assert result['currency'] == 'GBP'
        assert result['on_sale'] is False

    def test_get_psn_price_returns_none_for_no_webctas(self, mock_get):
        mock_get.return_value = make_mock_response({"data": {}})
        result = get_psn_price('some-id')
        assert result is None

@patch('app.price_clients.requests.get')
class TestEshopPriceClient:
    def test_get_eshop_price_parses_normal_price(self, mock_get):
        mock_get.return_value = make_mock_response({
          "data": {
            "prices": [
              {
                "regularPrice": {
                  "rawValue": "24.99",
                  "currency": "EUR",
                },
                "discountPrice": None,
              }
            ]
          }
        })
        result = get_eshop_price('70010000033132', 'https://www.nintendo.com/au/games/nintendo-switch/hades/')
        assert result['store'] == 'eshop'
        assert result['price'] == Decimal('24.99')
        assert result['currency'] == 'EUR'

    def test_get_eshop_price_parses_discount_price(self, mock_get):
        mock_get.return_value = make_mock_response({
            "data": {
                "prices": [
                    {
                        "regularPrice": {
                            "rawValue": "24.99",
                            "currency": "EUR",
                        },
                        "discountPrice": {
                            "rawValue": "16.99",
                            "currency": "EUR",
                        },
                    }
                ]
            }
        })
        result = get_eshop_price('11111111', 'some-url')
        assert result['store'] == 'eshop'
        assert result['price'] == Decimal('16.99')
        assert result['original_price'] == Decimal('24.99')


    def test_get_eshop_price_returns_none_with_empty_price(self, mock_get):
        mock_get.return_value = make_mock_response({
          "data": {
            "prices": []}})
        result = get_eshop_price('11111', 'some-url')
        assert result is None


