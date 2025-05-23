# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import pandas as pd
import numpy as np
import datetime
import yfinance as yf
import warnings
import time
from loguru import logger
from datetime import timedelta
from typing import List, Dict, Tuple, Optional

from utils.utils import post_twitter

class MarketPerformanceTracker:
    def __init__(self):
        """Initialize the market performance tracker with default settings."""

        # Initialize
        logger.add("logs/performance_markets_bot.log", rotation="500 MB")
        logger.info("initialize Performance Markets")

        self.data = {
            "name": ["NASDAQ_100", "SP_500", "Russell_2000", "DowJones", "FTSE_100",
                     "Nikkei_225", "DAX", "CAC_40", "EuroStoxx_50", "Ibex_35"],
            "symbol": ["^NDX", "^GSPC", "^RUT", "^DJI", "^FTSE",
                       "^N225", "^GDAXI", "^FCHI", "^STOXX50E", "^IBEX"]
        }
        self.hashtags = ['']
        self.performance_df = None
        self.merged_df = None
        self.green = "\U0001F7E2"  # Green Circle
        self.red = "\U0001F534"    # Red Circle


    def initialize_data(self) -> None:
        """Initialize dataframes and prepare data for analysis."""
        self.tickers = pd.DataFrame(self.data)
        self.performance_df = pd.DataFrame(columns=["ticker", "ytd", "hf", "3mtd", "mtd", "wtd", "dtd"])

    def post_tweet(self, text: str) -> None:
        """Post a tweet with the given text."""
        logger.info(text)
        post_twitter(text)
        time.sleep(300)

    def calculate_returns(self, stock_data: pd.DataFrame, start_date: datetime) -> float:
        """Calculate returns for a given time period."""
        filtered_data = stock_data[stock_data.index >= start_date]
        if len(filtered_data) < 2:
            return np.nan

        price_open = filtered_data["Open"].iloc[0]
        price_close = filtered_data["Close"].iloc[-1]
        return round(100 * (price_close - price_open) / price_open, 1)

    def fetch_stock_data(self, ticker: str) -> Dict[str, float]:
        """Fetch and calculate performance metrics for a given ticker."""
        try:
            dates = {
                'ytd': datetime.datetime(datetime.datetime.now().year, 1, 1),
                'hf': datetime.datetime.now() - timedelta(days=int(365 / 2)),
                '3mtd': datetime.datetime.now() - timedelta(days=90),
                'mtd': datetime.datetime.now() - timedelta(days=30),
                'wtd': datetime.datetime.now() - timedelta(days=7)
            }

            stock_data = yf.download(ticker,
                                     start=dates['ytd'],
                                     progress=False,
                                     multi_level_index=False)

            returns = {period: self.calculate_returns(stock_data, start_date)
                       for period, start_date in dates.items()}

            # Calculate day-to-day return
            stock_data_dtd = stock_data.tail(2)
            returns['dtd'] = round(100 * stock_data_dtd["Close"].pct_change().iloc[-1], 1)

            return returns

        except Exception as e:
            logger.error(f"Error processing {ticker}: {str(e)}")
            return {k: np.nan for k in ['ytd', 'hf', '3mtd', 'mtd', 'wtd', 'dtd']}

    def process_all_tickers(self) -> None:
        """Process all tickers and prepare the merged dataframe."""
        for ticker in self.tickers["symbol"]:
            returns = self.fetch_stock_data(ticker)
            if returns:
                row = [ticker] + [returns[k] for k in ['ytd', 'hf', '3mtd', 'mtd', 'wtd', 'dtd']]
                self.performance_df.loc[len(self.performance_df)] = row

        self.performance_df.dropna(inplace=True)
        self.tickers["ticker"] = self.tickers["symbol"]
        self.merged_df = pd.merge(self.tickers, self.performance_df, on='ticker')
        self.merged_df["Company"] = self.merged_df["name"]

    def format_performance_message(self, period: str, title: str) -> str:
        """Format performance message for a given period."""
        df_sorted = self.merged_df.sort_values(by=period)

        message = f"\nGlobal Markets {title}:\n"
        for i in range(1, 11):
            company = df_sorted["Company"].iloc[-i]
            perc = df_sorted[period].iloc[-i]
            emoji = self.green if perc > 0 else self.red
            message += f"{emoji} #{company} -> {perc} %\n"

        # Add hashtags while respecting Twitter's character limit
        for hashtag in self.hashtags:
            if len(message) + len(hashtag) + 1 <= 280:
                message += hashtag

        return message

    def post_performance(self, period: str, title: str) -> None:
        """Post performance for a specific period."""
        try:
            message = self.format_performance_message(period, title)
            logger.info(f"Posting message ({len(message)} chars):")
            self.post_tweet(message)
        except Exception as e:
            logger.error(f"Error posting {title}: {str(e)}")

    def run(self) -> None:
        """Run all performance reports."""
        self.initialize_data()
        self.process_all_tickers()

        reports = [
            # ('dtd', '1-Day'),
            ('wtd', '1-WTD'),
            # ('mtd', '1-MTD'),
            # ('3mtd', '3-MTD'),
            # ('hf', '6-MTD'),
            ('ytd', 'YTD')
        ]

        for period, title in reports:
            self.post_performance(period, title)


if __name__ == "__main__":
    tracker = MarketPerformanceTracker()
    tracker.run()