import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from data_fetcher import fetch_stock_data

# I mainly learned all this from: "Neural Networks from scratch in Python"
# Information comes in batches -> Write to save AI model to SQL database
class SimpleNeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        # Initialize weights and biases
        self.weights_input_hidden = np.random.rand(input_size, hidden_size)
        self.weights_hidden_output = np.random.rand(hidden_size, output_size)
        self.bias_hidden = np.zeros((1, hidden_size))
        self.bias_output = np.zeros((1, output_size))

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)

    # Forward prop -> Hardest part to learn
    def forward(self, X):
        # Forward pass
        self.hidden_layer_activation = np.dot(X, self.weights_input_hidden) + self.bias_hidden
        self.hidden_layer_output = self.sigmoid(self.hidden_layer_activation)
        self.output_layer_activation = np.dot(self.hidden_layer_output, self.weights_hidden_output) + self.bias_output
        output = self.sigmoid(self.output_layer_activation)
        return output
    # Second hardest part to learn
    def backward(self, X, y, output, learning_rate):
        # Backward pass (gradient descent)
        output_error = y - output
        output_delta = output_error * self.sigmoid_derivative(output)

        hidden_layer_error = output_delta.dot(self.weights_hidden_output.T)
        hidden_layer_delta = hidden_layer_error * self.sigmoid_derivative(self.hidden_layer_output)

        # Update weights and biases
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


def prepare_data(stock_data):
    # Normalize data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(stock_data)

    # Prepare training data (e.g., previous day's prices as input)
    X = []
    y = []
    for i in range(len(scaled_data) - 1):
        X.append(scaled_data[i])
        y.append(scaled_data[i + 1])

    X = np.array(X)
    y = np.array(y)
    return X, y, scaler


def train_model(ticker):
    stock_data = fetch_stock_data(ticker)
    X, y, scaler = prepare_data(stock_data)

    nn = SimpleNeuralNetwork(input_size=X.shape[1], hidden_size=5, output_size=y.shape[1])
    nn.train(X, y, epochs=1000, learning_rate=0.1)

    return nn, scaler


def predict_future_prices(nn, scaler, recent_data, ticker):
    # Fetch and prepare data for prediction
    recent_data = fetch_stock_data(ticker).tail(5)  # Example: last 5 days
    recent_data = recent_data[['Close']]  # Ensure only 'Close' is used
    recent_data = scaler.transform(recent_data)  # Transform using the scaler
    prediction = nn.predict(recent_data)
    prediction = scaler.inverse_transform(prediction)  # Denormalize prediction
    return prediction


# Example usage
if __name__ == "__main__":
    # Example stock data (features) and labels (targets)
    X = np.array([[0.1, 0.2, 0.3], [0.2, 0.3, 0.4], [0.3, 0.4, 0.5]])
    y = np.array([[0.4], [0.5], [0.6]])

    # Initialize and train the neural network
    nn = SimpleNeuralNetwork(input_size=3, hidden_size=5, output_size=1)
    nn.train(X, y, epochs=1000, learning_rate=0.1)

    # Predict using the trained neural network
    predictions = nn.predict(X)
    print("Predictions:\n", predictions)
