# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import pandas as pd
import numpy as np
import yfinance as yf
import warnings
from loguru import logger
import datetime
from datetime import timedelta
from typing import List, Dict, Tuple, Optional

from utils.utils import post_twitter


class SectorPerformance:
    def __init__(self):
        # Initialize DataFrame for tickers

        # Initialize
        logger.add("logs/performance_sector.log", rotation="500 MB")
        logger.info("initialize Performance sector")

        self.tickers_data = {
            "name": ["Energy","Real","Health","Financial","Comm","Utilities","Materials","IT","Indust","Staples","Discrec","SemiCond"],
            "symbol": ["VDE", "VNQ", "VHT", "VFH", "VOX", "VPU", "VAW", "VGT", "VIS", "VDC", "VCR", "SOXX"]
        }
        self.df = pd.DataFrame(self.tickers_data)
        self.tickers = self.df["symbol"].tolist()

        # Initialize other attributes
        self.current_date = datetime.datetime.now()
        self.start_date_1y =  datetime.datetime(datetime.datetime.now().year, 1, 1)
        self.start_date_half = self.current_date - timedelta(days=int(365 / 2))
        self.start_date_3month = self.current_date - timedelta(days=90)
        self.start_date_month = self.current_date - timedelta(days=30)
        self.start_date_week = self.current_date - timedelta(days=7)

        self.df_performance = pd.DataFrame(columns=["ticker", "1YTD", "hf", "3mtd", "mtd", "WTD", "dtd"])

        self.green = "\U0001F7E2"  # Green Circle
        self.red = "\U0001F534"    # Red Circle

    def fetch_stock_data(self, ticker):
        # Download historical stock data
        stock_data = yf.download(ticker, start=self.start_date_1y.strftime("%Y-%m-%d"), progress=False,multi_level_index=False)
        stock_data['day-of-week'] = stock_data.index.dayofweek
        stock_data['week-of-year'] = stock_data.index.isocalendar().week
        stock_data['month-of-year'] = stock_data.index.month
        stock_data['year'] = stock_data.index.year
        return stock_data

    def calculate_returns(self, stock_data, start_date, time_frame):
        try:
            # Filter data based on the start date
            stock_data_filtered = stock_data[stock_data.index >= start_date]
            price_open = stock_data_filtered["Open"].iloc[0]
            price_close = stock_data_filtered["Close"].iloc[-1]
            return_value = round(100 * (price_close - price_open) / price_open, 1)
            return return_value
        except:
            return np.nan

    def process_tickers(self):
        for ticker in self.tickers:
            stock_data = self.fetch_stock_data(ticker)
            row = [
                ticker,
                self.calculate_returns(stock_data, self.start_date_1y, "YTD"),
                self.calculate_returns(stock_data, self.start_date_half, "Half"),
                self.calculate_returns(stock_data, self.start_date_3month, "3M"),
                self.calculate_returns(stock_data, self.start_date_month, "MTD"),
                self.calculate_returns(stock_data, self.start_date_week, "WTD"),
                self.calculate_returns(stock_data.tail(2), self.start_date_week, "DTD")
            ]
            self.df_performance.loc[len(self.df_performance)] = row

        # Clean the dataframe by removing rows with NaN values
        self.df_performance.dropna(inplace=True)
        df_0 = self.df
        df_0['ticker'] = df_0['symbol']
        self.df = df_0

        self.df = pd.merge(self.df, self.df_performance, on='ticker')
        self.df["Company"] = self.df["name"]

    def generate_top_performance_message(self, sorted_df, period):
        top_12 = sorted_df.head(12)
        message = f"\n#Industrial Sectors -> {period}:\n"
        for i, row in top_12.iterrows():
            emoji = self.green if row[period] > 0 else self.red
            message += f"{emoji} #{row['Company']} -> {row[period]}%\n"
        return message

    def post_performance(self, message):
        # Assuming post function is defined elsewhere
        try:
            logger.info(message)
            logger.info(f'length message: {len(message)}')
            post_twitter(message)
        except Exception as e:
            logger.error(f"Error posting: {e}")

    def analyze_performance(self):
        # Sorting based on different time periods and generating messages
        for period in ['WTD', '1YTD']:
            sorted_df = self.df.sort_values(by=period)
            top_performance_message = self.generate_top_performance_message(sorted_df, period)
            self.post_performance(top_performance_message)

    def run(self):

        self.process_tickers()

        self.analyze_performance()

        return None
# Usage
if __name__ == "__main__":
    stock_perf = SectorPerformance()
    stock_perf.run()