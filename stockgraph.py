import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine, text
from ai_module import SimpleNeuralNetwork, prepare_data, fetch_stock_data
from db_management import *

def plot_stock_data_and_predictions(ticker, interval):
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '1626st0cks!',  # Replace with your actual password
        'database': 'testcase'
    }

    manager = StockDataManager(db_config)

    # Fetch actual stock data
    stock_data = manager.fetch_data_from_db(ticker, interval)

    # Check if stock_data is empty
    if stock_data.empty:
        print("No stock data found.")
        return

    # Prepare the data for training
    X, y, scaler = prepare_data(stock_data[['Close']].values)

    # Debugging: Check the shape of X and y
    print(f"X shape: {X.shape}, y shape: {y.shape}")

    # Ensure y is not empty
    if y.size == 0 or len(y.shape) < 2:
        print("Invalid shape for y, cannot proceed.")
        return

    # Initialize and train the neural network
    nn = SimpleNeuralNetwork(input_size=X.shape[1], hidden_size=5, output_size=y.shape[1])
    nn.train(X, y, epochs=1000, learning_rate=0.1)

    # Make predictions
    predictions = nn.predict(X)
    predictions = scaler.inverse_transform(predictions)  # Denormalize predictions

    # Plot the results
    plt.figure(figsize=(12, 6))
    plt.plot(stock_data.index, stock_data['Close'], label='Actual Close Prices', color='blue')
    plt.plot(stock_data.index[1:], predictions, label='Predicted Close Prices', color='orange', linestyle='dashed')
    plt.title(f'Stock Price Prediction for {ticker} - {interval}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    plot_stock_data_and_predictions('AAPL', '1d')