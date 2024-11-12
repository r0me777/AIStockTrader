import unittest
from AIStockTrader import app
from unittest.mock import patch
from AIStockTrader import db_management
import json


class TestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
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
