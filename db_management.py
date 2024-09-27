from flask import Flask, render_template, request, jsonify, send_from_directory
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import os

class StockDataManager:

    def __init__(self, db_config):
        """
        :param db_config:
        StockDataManager object allows retrevail, downloading of stock
        data and manages the schema of SQL database.
        """
        self.db_config = db_config
        self.engine = self.connect_to_mysql()

    # Connect to MySQL database using SQLAlchemy
    def connect_to_mysql(self):
        try:
            engine = create_engine(
                f"mysql+mysqlconnector://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}/{self.db_config['database']}")
            return engine
        except Exception as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    # Create tickers and intervals tables
    def create_main_tables(self):
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
            with self.engine.connect() as connection:
                connection.execute(text(create_tickers_query))
                connection.execute(text(create_intervals_query))
                print("Main tables created successfully.")
        except Exception as e:
            print(f"Error creating main tables: {e}")

    # Get or create ticker in tickers table
    # Get or create ticker in tickers table
    def get_or_create_ticker(self, ticker):
        query = "SELECT `ticker_id` FROM `tickers` WHERE `ticker` = :ticker;"
        insert_query = "INSERT INTO `tickers` (`ticker`) VALUES (:ticker);"
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), {'ticker': ticker}).fetchone()
                if result:
                    print(f'Ticker found: {result[0]}')
                    return result[0]  # Access by index
                else:
                    # Insert the new ticker and fetch it again
                    connection.execute(text(insert_query), {'ticker': ticker})
                    connection.commit()
                    result = connection.execute(text(query), {'ticker': ticker}).fetchone()
                    if result:  # Ensure result is not None before accessing
                        print(f"Ticker inserted and found: {result[0]}")
                        return result[0]
                    else:
                        print("Error: Inserted ticker but unable to fetch.")
                        return None

        except Exception as e:
            print(f"Error fetching or inserting ticker: {e}")
            return None

    # Get or create interval in intervals table
    def get_or_create_interval(self, interval):
        query = "SELECT `interval_id` FROM `intervals` WHERE `interval_name` = :interval;"
        insert_query = "INSERT INTO `intervals` (`interval_name`) VALUES (:interval);"
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), {'interval': interval}).fetchone()
                if result:
                    print(f"Interval found: {result[0]}")
                    return result[0]  # Access by index

                else:
                    # Insert the new interval and fetch it again
                    connection.execute(text(insert_query), {'interval': interval})
                    connection.commit()
                    result = connection.execute(text(query), {'interval': interval}).fetchone()
                    if result:  # Ensure result is not None before accessing
                        print(f"Interval inserted and found: {result[0]}")
                        return result[0]
                    else:
                        print("Error: Inserted interval but unable to fetch.")
                        return None

        except Exception as e:
            print(f"Error fetching or inserting interval: {e}")
            return None

    # Create stock_data table to hold financial data
    def create_stock_data_table(self):
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
            with self.engine.connect() as connection:
                connection.execute(text(create_table_query))
                print("stock_data table created successfully.")
        except Exception as e:
            print(f"Error creating stock_data table: {e}")

    # Save data to MySQL using Pandas df.to_sql()
    def save_data_to_db(self, data, ticker, interval):
        try:
            # Create main tables if they don't exist
            self.create_main_tables()
            self.create_stock_data_table()

            # Get ticker_id and interval_id
            ticker_id = self.get_or_create_ticker(ticker)
            print(f'Ticker ID: {ticker_id}')
            interval_id = self.get_or_create_interval(interval)
            print(f'Interval ID: {interval_id}')
            if ticker_id and interval_id:
                table_name = "stock_data"

                # Insert data into stock_data table
                with self.engine.connect() as connection:
                    for index, row in data.iterrows():
                        print(f'Inserting data: Ticker ID: {ticker_id}, Interval ID: {interval_id}, Date: {index}')
                        insert_query = f"""
                            INSERT INTO `{table_name}` (`ticker_id`, `interval_id`, `date`, `open`, `high`, `low`, `close`)
                            VALUES (:ticker_id, :interval_id, :date, :open, :high, :low, :close)
                            ON DUPLICATE KEY UPDATE `open` = :open, `high` = :high, `low` = :low, `close` = :close;
                        """
                        connection.execute(text(insert_query), {
                            'ticker_id': ticker_id,
                            'interval_id': interval_id,
                            'date': index,
                            'open': row['Open'],  # Open
                            'high': row['High'],  # High
                            'low': row['Low'],  # Low
                            'close': row['Close']  # Close
                        })
                        connection.commit() # ALWAYS after execute method
                        #connection.close() # CLOSES Connection!!! ANYTHING AFTER CANNOT SAVE
                    print(f"Successfully saved data for {ticker} ({interval}) to MySQL.")
        except Exception as e:
            print(f"Error saving data to MySQL: {e}")
        finally:
            if self.engine:
                self.engine.dispose()

    # Download data from Yahoo Finance
    def download_data(self, ticker, startdate, enddate, interval):
        try:
            data = yf.download(ticker, start=startdate, end=enddate, interval=interval)
            print(data)
            if data.empty:
                raise ValueError(f"No data found for {ticker} ({interval})")
            return data[['Open', 'High', 'Low', 'Close']].drop_duplicates()
        except Exception as e:
            print(f"Error downloading data: {e}")
            return pd.DataFrame()

    def fetch_data_from_db(self, ticker, interval, start_time=None, end_time=None):
        query = """
            SELECT date, close FROM stock_data
            JOIN tickers ON stock_data.ticker_id = tickers.ticker_id
            JOIN intervals ON stock_data.interval_id = intervals.interval_id
            WHERE tickers.ticker = :ticker AND intervals.interval_name = :interval
        """

        # Add conditions for start_time and end_time if provided
        if start_time:
            query += " AND date >= :start_time"
        if end_time:
            query += " AND date <= :end_time"

        query += " ORDER BY date;"

        try:
            with self.engine.connect() as connection:
                params = {'ticker': ticker, 'interval': interval}
                if start_time:
                    params['start_time'] = start_time
                if end_time:
                    params['end_time'] = end_time

                result = connection.execute(text(query), params)
                data = result.fetchall()
                df = pd.DataFrame(data, columns=['Date', 'Close'])
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                return df
        except Exception as e:
            print(f"Error fetching data from database: {e}")
            return pd.DataFrame()


if __name__ == "__main__":
    # Example usage
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '1626st0cks!',
        'database': 'testcase'
    }

    manager = StockDataManager(db_config)

    ticker = 'AMZN'
    startdate = '2023-01-01'
    enddate = '2023-09-01'
    interval = '1d'

    data = manager.download_data(ticker, startdate, enddate, interval)

    if not data.empty:
        manager.save_data_to_db(data, ticker, interval)

    #TODO: Check why other tickers besides Amazon won't work.
        # - Fixed connection.close() caused the problem

    ticker1 = 'AAPL'
    startdate1 = '2023-01-01'
    enddate1 = '2023-09-01'
    interval1 = '1d'

    data1 = manager.download_data(ticker1,startdate1,enddate1,interval1)
    if not data.empty:
        manager.save_data_to_db(data1,ticker1,interval1)

    #TODO: Make sure retrevial works for all tickers and make interval range for method
        # Fixed for works for all tickers still need to focus on interval range
        # Fixed for data range

    def test_data_retrieval():
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '1626st0cks!',  # Replace with your actual password
            'database': 'testcase'
        }

        manager = StockDataManager(db_config)

        # Attempt to fetch data for a specific ticker and interval
        ticker = 'AMZN'
        interval = '1d'
        start_time = '2023-01-01'
        end_time = '2023-01-31'
        stock_data = manager.fetch_data_from_db(ticker, interval, start_time, end_time)
        print(stock_data)



    test_data_retrieval()
    
