# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import pandas as pd
import numpy as np
import yfinance as yf
import warnings
from loguru import logger
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from utils.utils import post_twitter
import time
import requests


class US_StocksPerformance:
    def __init__(self):
        # Initialize DataFrame for tickers
        self.tickers_data = {
            "name": ["Energy","Real","Health","Financial","Comm","Utilities","Materials","IT","Indust","Staples","Discrec","SemiCond"],
            "symbol": ["VDE", "VNQ", "VHT", "VFH", "VOX", "VPU", "VAW", "VGT", "VIS", "VDC", "VCR", "SOXX"]
        }
        self.df = pd.DataFrame(self.tickers_data)
        self.tickers = self.df["symbol"].tolist()
        self.url = "https://financialmodelingprep.com/api/v3/stock/list"
        self.api_key = 'c8cda59957e87eead4f323aab454cefa'
        # Initialize

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
        tickers = tickers[tickers["type"]=="stock"]
        tickers = tickers[tickers["price"]>5]
        tickers = tickers[~tickers['symbol'].str.contains(r'[-.]')]
        filtered_tickers = tickers["symbol"].tolist()

        marketcap_all = []
        for ticker in filtered_tickers:
            try:
                ticker_data = yf.Ticker(ticker)
                market_cap = ticker_data.info['marketCap']
                marketcap_all.append(market_cap)
            except:
                marketcap_all.append(np.nan)

        tickers["marketCap"] = marketcap_all

        billion = 1000000000
        tickers['marketCap'] = pd.to_numeric(tickers['marketCap'], errors='coerce')
        tickers.dropna(inplace=True)
        tickers = tickers[tickers["marketCap"]>billion]
        return tickers["symbol"].tolist()

    def performance_y_week(self) -> None:
        """
        Calculates the performance (percentage change) of the filtered tickers over the past week
        and identifies the top and bottom performers.
        """
        top_performers = []
        bottom_performers = []

        # Loop through filtered tickers and fetch their historical data
        for ticker in self.tickers:
            try:
                ticker_data = yf.Ticker(ticker)
                hist = ticker_data.history(period="7d")  # Last 7 days
                if len(hist) > 1:  # Ensure there's enough data
                    start_price = hist.iloc[0]["Close"]
                    end_price = hist.iloc[-1]["Close"]
                    performance = ((end_price - start_price) / start_price) * 100
                    top_performers.append((ticker, performance))
                else:
                    logger.warning(f"Not enough data to calculate performance for {ticker}")
            except Exception as e:
                logger.warning(f"Error fetching data for {ticker}: {e}")

        # Sort the tickers by performance
        top_performers_sorted = sorted(top_performers, key=lambda x: x[1], reverse=True)
        bottom_performers_sorted = sorted(top_performers, key=lambda x: x[1])

        # Build Twitter message
        message = "#US Companies over $1B - Weekly Performance\n\nBest Performers:\n"
        for idx, (ticker, performance) in enumerate(top_performers_sorted[:5], 1):
            message += f"{idx}. ${ticker} -> +{performance:.2f}%\n"

        message += "\nWorst Performers:\n"
        for idx, (ticker, performance) in enumerate(bottom_performers_sorted[:5], 1):
            message += f"{idx}. ${ticker} -> {performance:.2f}%\n"

        # Log the message
        logger.info(f"Posting the following message on Twitter:\n{message}")

        # Attempt to post on Twitter
        try:
            post_twitter(message)
            logger.info("Message posted successfully on Twitter.")
        except Exception as e:
            logger.error(f"Error posting message on Twitter: {e}")

    def performance_y(self) -> None:
        """
        Calculates the performance (percentage change) of the filtered tickers over the last year
        and identifies the top and bottom performers.
        """
        top_performers = []
        bottom_performers = []

        # Loop through filtered tickers and fetch their historical data
        for ticker in self.tickers:
            try:
                ticker_data = yf.Ticker(ticker)
                hist = ticker_data.history(period="1y")  # Last 1 year
                if len(hist) > 1:  # Ensure there's enough data
                    start_price = hist.iloc[0]["Close"]
                    end_price = hist.iloc[-1]["Close"]
                    performance = ((end_price - start_price) / start_price) * 100
                    top_performers.append((ticker, performance))
                else:
                    logger.warning(f"Not enough data to calculate performance for {ticker}")
            except Exception as e:
                logger.warning(f"Error fetching data for {ticker}: {e}")

        # Sort the tickers by performance
        top_performers_sorted = sorted(top_performers, key=lambda x: x[1], reverse=True)
        bottom_performers_sorted = sorted(top_performers, key=lambda x: x[1])

        # Build Twitter message
        message = "#US Companies over $1B - Yearly Performance\n\nBest Performers:\n"
        for idx, (ticker, performance) in enumerate(top_performers_sorted[:5], 1):
            message += f"{idx}. ${ticker} -> +{performance:.2f}%\n"

        message += "\nWorst Performers:\n"
        for idx, (ticker, performance) in enumerate(bottom_performers_sorted[:5], 1):
            message += f"{idx}. ${ticker} -> {performance:.2f}%\n"

        # Log the message
        logger.info(f"Posting the following message on Twitter:\n{message}")

        # Attempt to post on Twitter
        try:
            post_twitter(message)
            logger.info("Message posted successfully on Twitter.")
        except Exception as e:
            logger.error(f"Error posting message on Twitter: {e}")

if __name__ == "__main__":
    US_stocks = US_StocksPerformance()

    # Filtering tickers for those meeting the market cap criteria
    filtered_tickers = US_stocks.filtering_tickers()

    # Perform weekly and yearly performance calculations
    if filtered_tickers:
        logger.info("Performance over the last week:")
        US_stocks.performance_y_week()

        logger.info("\nPerformance over the last year:")
        US_stocks.performance_y()
