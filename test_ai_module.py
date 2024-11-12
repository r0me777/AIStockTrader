import unittest
import numpy as np
from AIStockTrader.ai_module import SimpleNeuralNetwork, prepare_data, train_model, predict_future_prices
from unittest.mock import Mock
import pandas as pd


class TestSimpleNeuralNetwork(unittest.TestCase):

    def setUp(self):
        self.nn = SimpleNeuralNetwork(input_size=2, hidden_size=3, output_size=1)
        self.X = np.array([[0.1, 0.2], [0.3, 0.4]])
        self.y = np.array([[0.3], [0.5]])

    def test_forward(self):
        output = self.nn.forward(self.X)
        self.assertEqual(output.shape, (self.X.shape[0], 1))

    def test_backward(self):
        output = self.nn.forward(self.X)
        self.nn.backward(self.X, self.y, output, learning_rate=0.01)
        # Check that weights are updated
        self.assertFalse(np.array_equal(self.nn.weights_input_hidden, np.random.rand(2, 3)))

    def test_predict(self):
        output = self.nn.predict(self.X)
        self.assertEqual(output.shape, (self.X.shape[0], 1))


class TestPrepareData(unittest.TestCase):

    def test_prepare_data(self):
        stock_data = pd.DataFrame({'Close': [10, 20, 30, 40, 50]})
        X, y, scaler = prepare_data(stock_data)
        self.assertEqual(X.shape, (4, 1))
        self.assertEqual(y.shape, (4, 1))
        self.assertTrue(np.all(X >= 0) and np.all(X <= 1))


class TestTrainAndPredict(unittest.TestCase):

    def test_train_model(self):
        mock_manager = Mock()
        mock_manager.fetch_data_from_db.return_value = pd.DataFrame({'Close': [100, 101, 102, 103, 104]})
        nn, scaler = train_model('AAPL', mock_manager)
        self.assertIsNotNone(nn)
        self.assertIsNotNone(scaler)

    def test_predict_future_prices(self):
        mock_manager = Mock()
        mock_manager.fetch_data_from_db.return_value = pd.DataFrame({'Close': [100, 101, 102, 103, 104]})
        scaler = Mock()
        scaler.transform.return_value = np.array([[0.5]])
        scaler.inverse_transform.return_value = np.array([[110]])
        nn = SimpleNeuralNetwork(input_size=1, hidden_size=5, output_size=1)
        prediction = predict_future_prices(nn, scaler, mock_manager, 'AAPL')
        self.assertIsNotNone(prediction)
        self.assertEqual(prediction.shape[1], 1)


if __name__ == '__main__':
    unittest.main()
