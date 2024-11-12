import unittest
from unittest.mock import patch, Mock
from AIStockTrader.db_management import StockDataManager


class TestStockDataManager(unittest.TestCase):

    @patch('db_management.create_engine')
    def setUp(self, mock_create_engine):
        db_config = {'host': 'localhost', 'user': 'root', 'password': 'password', 'database': 'test_db'}
        self.manager = StockDataManager(db_config)

    @patch.object(StockDataManager, 'fetch_data_from_db')
    def test_fetch_data_from_db(self, mock_fetch_data):
        mock_fetch_data.return_value = Mock()
        data = self.manager.fetch_data_from_db('AAPL', '1d', '2023-01-01', '2023-02-01')
        self.assertIsNotNone(data)

    @patch.object(StockDataManager, 'save_data_to_db')
    def test_save_data_to_db(self, mock_save_data):
        stock_data = Mock()
        ticker = 'AAPL'
        interval = '1d'
        self.manager.save_data_to_db(stock_data, ticker, interval)
        mock_save_data.assert_called_with(stock_data, ticker, interval)


if __name__ == '__main__':
    unittest.main()
