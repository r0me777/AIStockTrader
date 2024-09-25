from flask import Flask, render_template, request, jsonify, send_from_directory
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'database'
}

# Connect to MySQL database using SQLAlchemy
def connect_to_mysql():
    try:
        engine = create_engine(
            f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")
        return engine
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Create tickers and intervals tables
def create_main_tables(engine):
    try:
        create_tickers_query = """
            CREATE TABLE IF NOT EXISTS `tickers` (
                `ticker_id` INT AUTO_INCREMENT PRIMARY KEY,
                `ticker` VARCHAR(10) UNIQUE NOT NULL
            );
        """
        create_intervals_query = """
            CREATE TABLE IF NOT EXISTS `intervals` (
                `interval_id` INT AUTO_INCREMENT PRIMARY KEY,
                `interval_name` VARCHAR(10) UNIQUE NOT NULL
            );
        """
        with engine.connect() as connection:
            connection.execute(text(create_tickers_query))
            connection.execute(text(create_intervals_query))
            print("Main tables created successfully.")
    except Exception as e:
        print(f"Error creating main tables: {e}")

# Get or create ticker in tickers table
def get_or_create_ticker(engine, ticker):
    query = "SELECT `ticker_id` FROM `tickers` WHERE `ticker` = :ticker;"
    insert_query = "INSERT INTO `tickers` (`ticker`) VALUES (:ticker);"
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query), {'ticker': ticker}).fetchone()
            if result:
                return result['ticker_id']
            else:
                connection.execute(text(insert_query), {'ticker': ticker})
                return connection.execute(text(query), {'ticker': ticker}).fetchone()['ticker_id']
    except Exception as e:
        print(f"Error fetching or inserting ticker: {e}")
        return None

# Get or create interval in intervals table
def get_or_create_interval(engine, interval):
    query = "SELECT `interval_id` FROM `intervals` WHERE `interval_name` = :interval;"
    insert_query = "INSERT INTO `intervals` (`interval_name`) VALUES (:interval);"
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query), {'interval': interval}).fetchone()
            if result:
                return result['interval_id']
            else:
                connection.execute(text(insert_query), {'interval': interval})
                return connection.execute(text(query), {'interval': interval}).fetchone()['interval_id']
    except Exception as e:
        print(f"Error fetching or inserting interval: {e}")
        return None

# Create stock_data table to hold financial data
def create_stock_data_table(engine):
    create_table_query = """
        CREATE TABLE IF NOT EXISTS `stock_data` (
            `data_id` INT AUTO_INCREMENT PRIMARY KEY,
            `ticker_id` INT,
            `interval_id` INT,
            `date` DATETIME NOT NULL,
            `open` FLOAT,
            `high` FLOAT,
            `low` FLOAT,
            `close` FLOAT,
            UNIQUE KEY `unique_data` (`ticker_id`, `interval_id`, `date`),
            FOREIGN KEY (`ticker_id`) REFERENCES `tickers`(`ticker_id`),
            FOREIGN KEY (`interval_id`) REFERENCES `intervals`(`interval_id`)
        ) ENGINE=InnoDB;
    """
    try:
        with engine.connect() as connection:
            connection.execute(text(create_table_query))
            print("stock_data table created successfully.")
    except Exception as e:
        print(f"Error creating stock_data table: {e}")

# Save data to MySQL using Pandas df.to_sql()
def save_data_to_db(data, ticker, interval):
    try:
        engine = connect_to_mysql()
        if engine:
            # Create main tables if they don't exist
            create_main_tables(engine)
            create_stock_data_table(engine)

            # Get ticker_id and interval_id
            ticker_id = get_or_create_ticker(engine, ticker)
            interval_id = get_or_create_interval(engine, interval)
            if ticker_id and interval_id:
                table_name = "stock_data"

                # Insert data into stock_data table
                with engine.connect() as connection:
                    for index, row in data.iterrows():
                        insert_query = f"""
                            INSERT INTO `{table_name}` (`ticker_id`, `interval_id`, `date`, `open`, `high`, `low`, `close`)
                            VALUES (:ticker_id, :interval_id, :date, :open, :high, :low, :close)
                            ON DUPLICATE KEY UPDATE `open` = :open, `high` = :high, `low` = :low, `close` = :close;
                        """
                        connection.execute(text(insert_query), {
                            'ticker_id': ticker_id,
                            'interval_id': interval_id,
                            'date': index,
                            'open': row['Open'],
                            'high': row['High'],
                            'low': row['Low'],
                            'close': row['Close']
                        })
                    print(f"Successfully saved data for {ticker} ({interval}) to MySQL.")
    except Exception as e:
        print(f"Error saving data to MySQL: {e}")
    finally:
        if engine:
            engine.dispose()

# Download data from Yahoo Finance
def download_data(ticker, startdate, enddate, interval):
    try:
        data = yf.download(ticker, start=startdate, end=enddate, interval=interval)
        print(data)
        if data.empty:
            raise ValueError(f"No data found for {ticker} ({interval})")
        return data[['Open', 'High', 'Low', 'Close']].drop_duplicates()
    except Exception as e:
        print(f"Error downloading data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Example usage
    ticker = 'AAPL'
    startdate = '2023-01-01'
    enddate = '2023-09-01'
    interval = '1d'

    data = download_data(ticker, startdate, enddate, interval)
    if not data.empty:
        save_data_to_db(data, ticker, interval)

