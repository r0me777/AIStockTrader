from AIStockTrader import app
from unittest import TestCase
from unittest.mock import patch
from config import TestConfig
import json

class TestApp(TestCase):

    @classmethod
    def setUpClass(cls):
        app.config.from_object(TestConfig)  # Use TestConfig for testing
        cls.client = app.test_client()
    @patch('app.stock_data_manager')
    def test_index_route_with_valid_data(self, mock_manager):
        mock_manager.fetch_data_from_db.return_value = Mock()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Stock Prices", response.data)

    @patch('app.stock_data_manager')
    def test_index_route_with_no_data(self, mock_manager):
        mock_manager.fetch_data_from_db.return_value = Mock(empty=True)
        response = self.client.get('/')
        self.assertIn(b"No data available", response.data)


if __name__ == '__main__':
    unittest.main()
