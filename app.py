from flask import Flask, render_template, request
from db_management import StockDataManager
from ai_module import train_model, predict_future_prices
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1626st0cks!',
    'database': 'testcase'
}

# Initialize StockDataManager
stock_data_manager = StockDataManager(db_config)

"""
Loads the stock data manager object 
Initilizies with -> No data

Python (Flask) Approach:
    Once you search a stock ticker and then click the interval 
        - Renders a template (FLASK ONLY)
        --- Wayyy easier solution ---

JavaScript Approach:
    Using chart.js or plotly.js and HTML & CSS
    Jsonfiy data and have javascript get data using flask api
    --- Probably better soultion ---

"""

@app.route("/", methods=["GET"])
def index():
    # Get form input or use default values
    ticker = request.args.get("ticker", "AMZN")
    startdate = request.args.get("startdate", "2023-01-01")
    enddate = request.args.get("enddate", "2023-09-01")
    print(enddate)
    interval = request.args.get("interval", '1d') #'1d'   #'1d'  # Default interval is '1d'
    print(interval)

    # Fetch stock data from the database
    stock_data = stock_data_manager.fetch_data_from_db(ticker, interval, startdate, enddate)

    # Check if stock_data is empty, indicating it's not in the database
    if stock_data.empty:
        try:
            # Attempt to download the stock data
            stock_data = stock_data_manager.download_data(ticker, startdate, enddate, interval)
            # Optionally save this data to the database for future use
            stock_data_manager.save_data_to_db(stock_data, ticker, interval)
        except Exception as e:
            return render_template("index.html", stock_data=None, prediction=None, ticker=ticker,
                                   startdate=startdate, enddate=enddate, graph_url=None, error=str(e))

    # Train the neural network with the stock data
    nn, scaler = train_model(ticker, stock_data_manager)

    # Make predictions if training was successful
    prediction = None
    if nn and scaler:
        predicted_prices = predict_future_prices(nn, scaler, stock_data_manager, ticker)
        prediction = predicted_prices.flatten().tolist() if predicted_prices is not None else None

    # Generate the graph as a PNG image
    img = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.plot(stock_data.index, stock_data['Close'], label='Close Price')
    plt.title(f"{ticker} Stock Prices")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()

    return render_template(
        "index.html",
        stock_data=stock_data,
        prediction=prediction,
        ticker=ticker,
        startdate=startdate,
        enddate=enddate,
        graph_url=f"data:image/png;base64,{graph_url}",
        error=None  # Pass the error variable if needed
    )

if __name__ == "__main__":
    app.run(debug=True)

