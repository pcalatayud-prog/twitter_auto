import pandas as pd
import numpy as np
import yfinance as yf
import warnings
from loguru import logger
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from utils.utils import post_twitter, get_market_cap
import time
import requests


class US_StocksPerformance:
    def __init__(self):
        self.tickers = None
        self.url = "https://financialmodelingprep.com/api/v3/stock/list"
        from config.api_keys import api_key
        self.api_key = api_key
        # Initialize
        logger.add("logs/performance_us_all_bot.log", rotation="500 MB")
        logger.info("initialize Performance US all")

        # Add emoji indicators
        self.green = "\U0001F7E2"  # Green Circle
        self.red = "\U0001F534"  # Red Circle

        # Initialize DataFrame for storing performances
        self.df_performance = pd.DataFrame(columns=["ticker", "weekly", "yearly"])

    def filtering_tickers(self):
        url = self.url
        api_key = self.api_key
        # Parameters
        params = {
            "apikey": api_key
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            # Extract tickers from response JSON
            data = response.json()

        tickers = pd.DataFrame(data)
        tickers = tickers[tickers["exchangeShortName"].isin(['NYSE', 'NASDAQ'])]
        tickers = tickers[tickers["type"] == "stock"]
        tickers = tickers[tickers["price"] > 5]
        tickers = tickers[~tickers['symbol'].str.contains(r'[-.]')]
        filtered_tickers = tickers["symbol"].tolist()

        # filtered_tickers = filtered_tickers[:20]
        # tickers = tickers[tickers['symbol'].isin(filtered_tickers)]

        marketcap_all = []
        logger.info('Number of tickets to evaluate: {}'.format(len(filtered_tickers)))
        count = 0
        for ticker in filtered_tickers:
            try:
                market_cap = get_market_cap(ticker)
                marketcap_all.append(market_cap)
            except Exception as e:
                logger.error(f'Error downloaded {ticker}. Tickers {count} out of {len(filtered_tickers)}. \nError: {e}')
                marketcap_all.append(np.nan)
            count += 1
            if count % 100 == 0:
                logger.info(f'Processed: {count} out of {len(filtered_tickers)}')
                perc_process = round(count / len(filtered_tickers) * 100, 2)
                logger.info(f'Processed: {perc_process}')

        tickers["marketCap"] = marketcap_all

        billion = 1_000_000_000
        tickers['marketCap'] = pd.to_numeric(tickers['marketCap'], errors='coerce')
        tickers.dropna(inplace=True)
        tickers = tickers[tickers["marketCap"] > billion]

        self.tickers = tickers["symbol"].tolist()

    def fetch_stock_data(self, ticker: str, period: str) -> pd.DataFrame:
        """Fetch stock data for a given ticker and period."""
        try:
            stock_data = yf.download(ticker, period=period, progress=False, multi_level_index=False)
            return stock_data
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()

    def calculate_returns(self, stock_data: pd.DataFrame) -> float:
        """Calculate returns from stock data."""
        try:
            if len(stock_data) > 1:
                price_open = stock_data["Open"].iloc[0]
                price_close = stock_data["Close"].iloc[-1]
                return round(100 * (price_close - price_open) / price_open, 1)
            return np.nan
        except:
            return np.nan

    def process_tickers(self):
        """Process all tickers and calculate their performance."""
        for ticker in self.tickers:
            weekly_data = self.fetch_stock_data(ticker, "5d")
            yearly_data = self.fetch_stock_data(ticker, "1y")

            weekly_return = self.calculate_returns(weekly_data)
            yearly_return = self.calculate_returns(yearly_data)

            self.df_performance.loc[len(self.df_performance)] = [
                ticker,
                weekly_return,
                yearly_return
            ]

        # Clean the dataframe by removing rows with NaN values
        self.df_performance.dropna(inplace=True)

    def generate_performance_message(self, period: str) -> str:
        """Generate performance message for a given period."""
        period_map = {"weekly": "Weekly", "yearly": "Yearly"}
        sorted_df = self.df_performance.sort_values(by=period, ascending=False)

        message = f"#US Companies over $1B - {period_map[period]} Performance\nBest Performers:\n"

        # Top 5 performers
        for i, row in sorted_df.head(5).iterrows():
            emoji = self.green if row[period] > 0 else self.red
            message += f"{emoji} ${row['ticker']} -> {row[period]}%\n"

        message += "Worst Performers:\n"

        # Bottom 5 performers
        for i, row in sorted_df.tail(5).iterrows():
            emoji = self.green if row[period] > 0 else self.red
            message += f"{emoji} ${row['ticker']} -> {row[period]}%\n"

        return message

    def post_performance(self, message: str):
        """Post performance message to Twitter."""
        try:
            logger.info(f"Posting the following message:\n{message}")
            logger.info(f'Length of message: {len(message)}')
            post_twitter(message)
            logger.info("Message posted successfully on Twitter.")
        except Exception as e:
            logger.error(f"Error posting message: {e}")

    def run(self):
        # Filtering tickers for those meeting the market cap criteria
        logger.info('Starting to filter companies')
        self.filtering_tickers()

        # Process all tickers
        logger.info('Processing tickers')
        self.process_tickers()

        # Generate and post messages for both periods
        # for period in ['weekly', 'yearly']:
        for period in ['weekly']:
            message = self.generate_performance_message(period)
            self.post_performance(message)


if __name__ == "__main__":
    US_stocks = US_StocksPerformance()
    US_stocks.run()