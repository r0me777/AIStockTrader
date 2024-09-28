from db_management import StockDataManager
from ai_module import train_model, predict_future_prices
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#Example of what AI would look like predicting stock values

def test_data_retrieval_and_prediction():
    # Database configuration
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '1626st0cks!',  # Replace with your actual password
        'database': 'testcase'
    }

    # Initialize StockDataManager
    manager = StockDataManager(db_config)

    # Define ticker and interval
    ticker = 'AMZN'
    interval = '1d'

    # Fetch stock data from the database
    stock_data = manager.fetch_data_from_db(ticker, interval)

    if stock_data.empty:
        print(f"No data available for {ticker}. Exiting.")
        return

    # Train the neural network model
    nn, scaler = train_model(ticker, manager)

    # Predict future prices if the model was successfully trained
    if nn and scaler:
        predicted_prices = predict_future_prices(nn, scaler, manager, ticker)

        if predicted_prices is not None:
            # Combine the predicted prices with actual stock data
            prediction_dates = pd.date_range(stock_data.index[-1] + pd.Timedelta(days=1), periods=len(predicted_prices))
            predicted_df = pd.DataFrame(predicted_prices, index=prediction_dates, columns=['Predicted Close'])

            # Plotting actual vs predicted prices
            plt.figure(figsize=(10, 6))
            plt.plot(stock_data.index, stock_data['Close'], label="Actual Close Prices", color="blue")
            plt.plot(predicted_df.index, predicted_df['Predicted Close'], label="Predicted Close Prices",
                     color="orange")
            plt.xlabel("Date")
            plt.ylabel("Close Price")
            plt.title(f"{ticker} Stock Price Prediction")
            plt.legend()
            plt.show()
        else:
            print("Prediction failed.")
    else:
        print("Model training failed.")


if __name__ == "__main__":
    test_data_retrieval_and_prediction()
