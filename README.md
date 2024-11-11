# AIStockTrader
Web application that displays real-time stock data and AI (Python Built Neural Network) predictions. It integrates yfinance for data retrieval and MySQL for storage.

---

## Features

- **Real-Time Stock Data**: Fetch and display live stock prices.
- **AI Predictions**: Provides stock price forecasts based on historical data using a neural network model.
- **Data Storage**: Stores stock data in a MySQL database.
- **User-Friendly Interface**: Simple and interactive web UI built with Flask.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/AIStockTrader.git
   cd AIStockTrader
   ```

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Required Packages**:
   Install dependencies listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up MySQL Database**:
   - Create a MySQL database to store stock data.
   - Update the database connection information in the application’s configuration file (e.g., `config.py`).

5. **Run the Application**:
   ```bash
   flask run
   ```
   Access the application at `http://127.0.0.1:5000`.

## Usage

1. **Fetch and Display Stock Data**: Select or input a stock symbol to view its real-time data.
2. **AI Prediction**: Run the neural network model to generate predictions based on historical stock data.
3. **View Graphs and Analysis**: Visualize the stock's historical trends and the AI’s forecasted prices.

## Project Structure

```plaintext
AIStockTrader/
├── app/                # Application code
│   ├── templates/      # HTML templates
│   ├── static/         # Static files (CSS, JS)
│   ├── src/            # Program files
│   
│   
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation
```

## Requirements

- Python 3.7+
- MySQL Database

### Dependencies (from `requirements.txt`)

- `Flask`: Web framework
- `yfinance`: For retrieving stock data
- `mysql-connector-python`: For MySQL database connections
- `matplotlib`: For plotting stock data and predictions
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `scikit-learn`: Machine learning for model training
- `sqlalchemy`: ORM for database management

## Contributing

1. **Fork the repository**.
2. **Create a new branch**: `git checkout -b feature-name`
3. **Commit your changes**: `git commit -m 'Add feature'`
4. **Push to the branch**: `git push origin feature-name`
5. **Submit a pull request**.

## License

This project is licensed under the MIT License.

---
