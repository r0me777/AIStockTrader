import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from db_management import StockDataManager


class SimpleNeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        self.weights_input_hidden = np.random.rand(input_size, hidden_size)
        self.weights_hidden_output = np.random.rand(hidden_size, output_size)
        self.bias_hidden = np.zeros((1, hidden_size))
        self.bias_output = np.zeros((1, output_size))

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def forward(self, X):
        self.hidden_layer_activation = np.dot(X, self.weights_input_hidden) + self.bias_hidden
        self.hidden_layer_output = self.sigmoid(self.hidden_layer_activation)
        self.output_layer_activation = np.dot(self.hidden_layer_output, self.weights_hidden_output) + self.bias_output
        output = self.sigmoid(self.output_layer_activation)
        return output

    def backward(self, X, y, output, learning_rate):
        output_error = y - output
        output_delta = output_error * self.sigmoid_derivative(output)

        hidden_layer_error = output_delta.dot(self.weights_hidden_output.T)
        hidden_layer_delta = hidden_layer_error * self.sigmoid_derivative(self.hidden_layer_output)

        self.weights_hidden_output += self.hidden_layer_output.T.dot(output_delta) * learning_rate
        self.bias_output += np.sum(output_delta, axis=0, keepdims=True) * learning_rate
        self.weights_input_hidden += X.T.dot(hidden_layer_delta) * learning_rate
        self.bias_hidden += np.sum(hidden_layer_delta, axis=0, keepdims=True) * learning_rate

    def train(self, X, y, epochs, learning_rate):
        for epoch in range(epochs):
            output = self.forward(X)
            self.backward(X, y, output, learning_rate)
            if epoch % 100 == 0:
                loss = np.mean(np.square(y - output))
                print(f'Epoch {epoch}, Loss: {loss}')

    def predict(self, X):
        return self.forward(X)


# Prepare stock data by normalizing it
def prepare_data(stock_data):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(stock_data)

    X = []
    y = []
    for i in range(len(scaled_data) - 1):
        X.append(scaled_data[i])
        y.append(scaled_data[i + 1])

    X = np.array(X)
    y = np.array(y)
    return X, y, scaler


# Train the neural network using StockDataManager
def train_model(ticker, stock_data_manager):
    stock_data = stock_data_manager.fetch_data_from_db(ticker, '1d')  # Fetch daily data from DB
    if stock_data.empty:
        print(f"No data available for {ticker}")
        return None, None

    X, y, scaler = prepare_data(stock_data[['Close']])  # Only use 'Close' price

    nn = SimpleNeuralNetwork(input_size=X.shape[1], hidden_size=5, output_size=y.shape[1])
    nn.train(X, y, epochs=1000, learning_rate=0.1)

    return nn, scaler


# Predict future prices using the trained neural network
def predict_future_prices(nn, scaler, stock_data_manager, ticker):
    recent_data = stock_data_manager.fetch_data_from_db(ticker, '1d').tail(5)  # Last 5 days of data
    if recent_data.empty:
        print(f"No recent data for {ticker}")
        return None

    recent_data = recent_data[['Close']]
    recent_data_scaled = scaler.transform(recent_data)

    prediction = nn.predict(recent_data_scaled)
    prediction = scaler.inverse_transform(prediction)  # Denormalize prediction

    return prediction


if __name__ == "__main__":
    # Set up StockDataManager
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '1626st0cks!',
        'database': 'testcase'
    }

    stock_data_manager = StockDataManager(db_config)

    # Train the model for a specific stock
    ticker = 'AMZN'
    nn, scaler = train_model(ticker, stock_data_manager)

    # Make future price predictions if training was successful
    if nn and scaler:
        predicted_prices = predict_future_prices(nn, scaler, stock_data_manager, ticker)
        print(f"Predicted future prices for {ticker}:\n", predicted_prices)
