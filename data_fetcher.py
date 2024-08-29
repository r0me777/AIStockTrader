import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker, start_date='2020-01-01', end_date='2023-01-01'):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    stock_data = stock_data[['Close']]  # Use only 'Close' price
    return stock_data

