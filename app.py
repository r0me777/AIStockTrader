from flask import Flask, render_template, request, jsonify
import yfinance as yf
from ai_module import train_model, predict_future_prices
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

app = Flask(__name__)

# Dummy AI profit percentage function
def calculate_ai_profit_percentage():
    # In a real application, this would calculate based on AI performance
    return 12.5


@app.route('/')
def index():
    ticker = 'AAPL'  # Example ticker
    stock_data = fetch_stock_data(ticker)
    nn, scaler = train_model(ticker)
    prediction = predict_future_prices(nn, scaler, stock_data.tail(5), ticker)

    # Generate the graph
    img = io.BytesIO()
    plt.figure(figsize=(10, 6))
    plt.plot(stock_data.index, stock_data['Close'], label='Close Price')
    plt.title(f'Stock Prices for {ticker}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode('utf8')

    return render_template('index.html',
                           prediction=prediction,
                           stock_data=stock_data.to_dict(),
                           graph_url=f'data:image/png;base64,{graph_url}')


@app.route('/stock/<ticker>')
def stock(ticker):
    stock_data = fetch_stock_data(ticker)
    ai_profit = calculate_ai_profit_percentage()
    return render_template('stock.html', stock_data=stock_data, ai_profit=ai_profit, ticker=ticker)

def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    return hist

if __name__ == '__main__':
    app.run(debug=True)
