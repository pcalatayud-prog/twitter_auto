# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import pandas as pd
import numpy as np
import datetime
import yfinance as yf
from datetime import timedelta
import warnings
from loguru import logger
import time

from utils.utils import post_twitter

class StockSevenMagnificenPerformance:
    def __init__(self, tickers=None):

        # Initialize
        logger.add("logs/performance_mag_7_bot.log", rotation="500 MB")
        logger.info("initialize Mag_7")

        self.tickers = tickers or ["NVDA", "META", "AMZN", "MSFT", "GOOG", "AAPL", "TSLA"]
        self.df = pd.DataFrame({"symbol": self.tickers})
        self.df_performance = pd.DataFrame(columns=["ticker", "ytd", "hf", "3mtd", "mtd", "wtd", "dtd","3y"])
        self.lista_hastaghs = ["\n#Stocks"," #StockMarket"]

        # Emojis for positive/negative returns
        self.green = "\U0001F7E2"  # Green Circle
        self.red = "\U0001F534"    # Red Circle

        # Suppress warnings
        warnings.filterwarnings('ignore')

        # Get the current date
        current_date = datetime.datetime.now()
        self.current_year = current_date.year
        self.current_month = current_date.month
        self.current_week = int(current_date.strftime("%U"))



    def download_data(self):
        """Download stock data for each ticker and calculate performance."""
        for ticker in self.tickers:
            try:
                stock_data = yf.download(ticker, start="2024-01-01", end=datetime.datetime.now(), progress=False)
                stock_data.columns = stock_data.columns.get_level_values(0)

                stock_data['day-of-week'] = stock_data.index.dayofweek
                stock_data['week-of-year'] = stock_data.index.isocalendar().week
                stock_data['month-of-year'] = stock_data.index.month
                stock_data['year'] = stock_data.index.year

                # Performance calculations for multiple periods
                performance = {
                    "ticker": ticker,
                    "3-YTD": self.calculate_return(stock_data, self.get_start_date('3-YTD')),
                    "ytd": self.calculate_return(stock_data, self.get_start_date('ytd')),
                    "hf": self.calculate_return(stock_data, self.get_start_date('half')),
                    "3mtd": self.calculate_return(stock_data, self.get_start_date('3m')),
                    "mtd": self.calculate_return(stock_data, self.get_start_date('1m')),
                    "wtd": self.calculate_return(stock_data, self.get_start_date('1w')),
                    "dtd": self.calculate_dtd(stock_data).item()
                }

                self.df_performance = pd.concat([self.df_performance, pd.DataFrame([performance])], ignore_index=True)


            except Exception as e:
                logger.error(f"Error with ticker {ticker}: {e}")
                pass

    def get_start_date(self, period):
        """ Helper function to get the start date based on the period input """
        if period == 'ytd':
            return datetime.datetime(datetime.datetime.now().year, 1, 1)
        elif period == 'half':
            return datetime.datetime.now() - timedelta(days=365 // 2)
        elif period == '3m':
            return datetime.datetime.now() - timedelta(days=90)
        elif period == '1m':
            return datetime.datetime.now() - timedelta(days=30)
        elif period == '1w':
            return datetime.datetime.now() - timedelta(days=7)
        elif period == '3-YTD':
            return datetime.datetime.now() - timedelta(days=365*5)
        else:
            raise ValueError("Invalid period specified")

    def calculate_return(self, stock_data, start_date):
        """ Helper function to calculate returns for a given time period """
        stock_data_period = stock_data[stock_data.index >= start_date]
        if len(stock_data_period) > 1:
            price_open = stock_data_period["Open"].iloc[0]
            price_close = stock_data_period["Close"].iloc[-1]
            return round(100 * (price_close - price_open) / price_open, 1).item()
        else:
            return np.nan

    def calculate_dtd(self, stock_data):
        """ Calculate Day-to-Day return """
        stock_data_dtd = stock_data.tail(2)
        stock_data_dtd["returns"] = round(100 * stock_data_dtd["Close"].pct_change(), 1)
        return stock_data_dtd["returns"].iloc[-1] if len(stock_data_dtd) > 1 else np.nan

    def merge_data(self):
        """ Merge performance data with tickers."""
        self.df['ticker'] = self.df['symbol']
        self.merged_df = pd.merge(self.df, self.df_performance, on='ticker')
        self.merged_df["Company"] = self.merged_df["symbol"].map(dict(zip(self.tickers, self.tickers)))

    def post_performance(self, frequency='dtd'):
        """ Post the top performance based on the chosen frequency."""
        sorted_df = self.merged_df.sort_values(by=frequency, ascending=False)
        top_7 = sorted_df.head(7)

        message = f"\nMagnificent-7 -> {frequency.upper()}:\n\n"
        for idx, row in top_7.iterrows():
            performance_value = row[frequency]
            # Add emoji based on the performance value
            emoji = self.green if performance_value > 0 else self.red
            message += f"{idx+1}. {emoji} #{row['Company']} -> {performance_value} %\n"

        message_with_hashtags = message + ''.join(self.lista_hastaghs)

        logger.info(f"Message length: {len(message_with_hashtags)}")

        # Here you would include logic to post the message (e.g., post() function)
        try:
            self.post(message_with_hashtags)
            logger.success(message_with_hashtags)
        except Exception as e:
            logger.error(f"Error posting {frequency}: {e}")

    def post(self, message):
        """ Placeholder for the post function (you should define how the post happens) """
        logger.info("Posting message...")
        logger.info(message)  # Simulate posting
        post_twitter(message)
        time.sleep(120)

    def run(self):
        """ Method to run all steps: download data, merge, and post performance."""
        logger.info("Starting the stock performance evaluation.")
        self.download_data()
        self.merge_data()

        # Post the top performance for different frequencies
        logger.info("Posting top performance for different frequencies.")
        # frequencies = ['dtd', 'wtd', 'mtd', '3mtd']
        frequencies = ['wtd','ytd']
        for frequency in frequencies:
            self.post_performance(frequency=frequency)

# Main block to run the script
if __name__ == "__main__":
    stock_performance = StockSevenMagnificenPerformance()
    stock_performance.run()
    logger.success('Peformance Mag-7 cCompleted')
