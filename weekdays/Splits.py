# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import os
import json
import pandas as pd
import yfinance as yf
import requests
import time
from loguru import logger
from datetime import datetime, timedelta
from utils.utils import post_twitter, get_market_cap,get_splits_calendar
from typing import List, Dict, Optional


class SplitBot:
    """
    A class to handle stock split announcements and post them to Twitter.
    """

    def __init__(self):
        """Initialize the SplitBot with necessary configurations."""
        logger.add("logs/split_bot.log", rotation="500 MB")
        logger.info('Initializing SplitBot')

        # Set up date information
        self.current_date = datetime.now()
        self.current_date_str = self.current_date.strftime('%Y-%m-%d')

        # Load ticker information
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                "config/top_3000_tickers.csv",
                os.path.join(script_dir, "config/top_3000_tickers.csv"),
                os.path.join(script_dir, "../config/top_3000_tickers.csv"),
                os.path.join(script_dir, "top_3000_tickers.csv"),
                "top_3000_tickers.csv"
            ]

            csv_loaded = False
            for path in possible_paths:
                if os.path.exists(path):
                    self.ticker_df = pd.read_csv(path)
                    logger.info(f"Successfully loaded ticker information from {path}")
                    csv_loaded = True
                    break

            if not csv_loaded:
                logger.error(f"Could not find top_3000_tickers.csv in any of these locations: {possible_paths}")
                self.ticker_df = pd.DataFrame(columns=['ticker', 'company_name', 'industry', 'sector'])

        except Exception as e:
            logger.error(f"Error loading ticker information: {e}")
            self.ticker_df = pd.DataFrame(columns=['ticker', 'company_name', 'industry', 'sector'])

        # API configuration
        try:
            from config.api_keys import api_key
            self.api_key = api_key
        except ImportError:
            logger.error("Could not import API key from config.api_keys")
            self.api_key = None

        self.base_url = 'https://financialmodelingprep.com/api/v3'

        # Track posted messages to avoid duplicates
        self.posted_messages = set()

    def get_ticker_info(self, ticker: str) -> Dict:
        """Get information about a specific ticker."""
        try:
            if self.ticker_df.empty:
                logger.warning(f"No ticker data available, using default info for {ticker}")
                return {
                    'ticker': ticker,
                    'company_name': ticker,
                    'industry': 'Unknown',
                    'sector': 'Unknown'
                }

            ticker_info = self.ticker_df[self.ticker_df["ticker"] == ticker]
            if ticker_info.empty:
                logger.warning(f"No information found for ticker {ticker}")
                return {
                    'ticker': ticker,
                    'company_name': ticker,
                    'industry': 'Unknown',
                    'sector': 'Unknown'
                }

            result = ticker_info.to_dict(orient='records')[0]
            logger.info(f"Successfully retrieved info for {ticker}")
            return result

        except Exception as e:
            logger.error(f"Error getting ticker info for {ticker}: {e}")
            return {
                'ticker': ticker,
                'company_name': ticker,
                'industry': 'Unknown',
                'sector': 'Unknown'
            }

    def get_historical_price(self, ticker: str, start_date: str, end_date: str):
        """Download historical price data for a ticker."""
        try:
            return yf.download(ticker, start=start_date, end=end_date, progress=False)
        except Exception as e:
            logger.error(f"Error downloading historical data for {ticker}: {e}")
            return None

    def get_performance_score(self, ticker: str) -> pd.DataFrame:
        """Calculate performance metrics for a given ticker."""
        try:
            df_performance = pd.DataFrame(columns=[
                "ticker", "price_change_ytd", "MDD_ytd",
                "price_change_last_year", "MDD_last_year",
                "price_change_last_5_years", "MDD_5y"
            ])

            # Calculate dates
            date_five_years = (self.current_date - timedelta(days=365 * 5)).strftime('%Y-%m-%d')
            date_last_year = (self.current_date - timedelta(days=365)).strftime('%Y-%m-%d')
            first_day_current_year = self.current_date.replace(month=1, day=1).strftime('%Y-%m-%d')

            df_5y = self.get_historical_price(ticker, date_five_years, self.current_date_str)
            if df_5y is None or df_5y.empty:
                logger.warning(f"No historical data available for {ticker}")
                return pd.DataFrame()

            # Calculate returns and metrics
            df_5y["returns"] = df_5y["Adj Close"].pct_change()
            df_5y["returns_perc"] = df_5y["returns"] + 1
            df_5y["creturns"] = df_5y["returns_perc"].cumprod()
            df_5y.dropna(inplace=True)

            # Calculate metrics for different time periods
            metrics = self._calculate_period_metrics(df_5y, date_last_year, first_day_current_year)

            # Add row to performance DataFrame
            df_performance.loc[0] = [ticker] + list(metrics.values())

            return df_performance

        except Exception as e:
            logger.error(f"Error calculating performance score for {ticker}: {e}")
            return pd.DataFrame()

    def _calculate_period_metrics(self, df: pd.DataFrame, date_last_year: str, first_day_current_year: str) -> dict:
        """Calculate metrics for different time periods."""
        try:
            # Calculate 5-year metrics
            df["cummax_BH"] = df.creturns.cummax()
            df["drawdown_BH"] = (df["cummax_BH"] - df["creturns"]) / df["cummax_BH"]

            price_change_5y = round(df["creturns"].iloc[-1], 2)
            MDD_5y = round(df["drawdown_BH"].max(), 2)

            # Calculate 1-year metrics
            df_1y = df[df.index > date_last_year].copy()
            df_1y["creturns"] = df_1y["returns_perc"].cumprod()
            df_1y["cummax_BH"] = df_1y.creturns.cummax()
            df_1y["drawdown_BH"] = (df_1y["cummax_BH"] - df_1y["creturns"]) / df_1y["cummax_BH"]

            price_change_1y = round(df_1y["creturns"].iloc[-1], 2)
            MDD_1y = round(df_1y["drawdown_BH"].max(), 2)

            # Calculate YTD metrics
            df_ytd = df[df.index > first_day_current_year].copy()
            df_ytd["creturns"] = df_ytd["returns_perc"].cumprod()
            df_ytd["cummax_BH"] = df_ytd.creturns.cummax()
            df_ytd["drawdown_BH"] = (df_ytd["cummax_BH"] - df_ytd["creturns"]) / df_ytd["cummax_BH"]

            price_change_ytd = round(df_ytd["creturns"].iloc[-1], 2)
            MDD_ytd = round(df_ytd["drawdown_BH"].max(), 2)

            # Convert to percentages
            metrics = {
                "price_change_ytd": 100 * (price_change_ytd - 1),
                "MDD_ytd": 100 * MDD_ytd,
                "price_change_1y": 100 * (price_change_1y - 1),
                "MDD_1y": 100 * MDD_1y,
                "price_change_5y": 100 * (price_change_5y - 1),
                "MDD_5y": 100 * MDD_5y
            }

            return metrics

        except Exception as e:
            logger.error(f"Error calculating period metrics: {e}")
            return {
                "price_change_ytd": 0, "MDD_ytd": 0,
                "price_change_1y": 0, "MDD_1y": 0,
                "price_change_5y": 0, "MDD_5y": 0
            }

    def get_split_data(self) -> pd.DataFrame:
        """Get stock split data from the API."""
        try:
            df_splits = get_splits_calendar(today=self.current_date_str)

            return df_splits

        except Exception as e:
            logger.error(f"Error getting split data: {e}")
            return pd.DataFrame()

    def format_split_message(self, ticker: str, company_info: Dict, split_info: Dict,
                             performance_data: Optional[pd.DataFrame] = None) -> str:
        """Format the split announcement message."""
        try:
            message_0 = (f"Today Split Stock: \n #{company_info['company_name']}, -> ${ticker} "
                         f"\n ---->  Industry: #{company_info['industry']} "
                         f"\n ---->   Sector: #{company_info['sector']}")

            numerator = split_info['numerator']
            denominator = split_info['denominator']
            split_ratio = round(numerator / denominator, 8)

            message_2 = (f"\n Split Information: \n ----> Numerator {numerator} : {denominator} Denominator"
                         f"\n ----> Split -> {split_ratio} ")

            final_message = message_0 + message_2 + "\n #Split #Report #Stocks"

            # Check for duplicates
            if final_message in self.posted_messages:
                logger.warning(f"Duplicate message detected for {ticker}")
                return ""

            self.posted_messages.add(final_message)
            logger.info(f"Created split message for {ticker}")
            return final_message

        except Exception as e:
            logger.error(f"Error formatting split message for {ticker}: {e}")
            return ""

    def run(self):
        """Execute the main bot workflow."""
        logger.info("Starting SplitBot workflow")

        try:
            # Get split data
            today_splits = self.get_split_data()
            if today_splits.empty:
                logger.info("No splits scheduled for today")
                return

            logger.info(f"Found {len(today_splits)} splits for today")

            # Process each split
            for _, split in today_splits.iterrows():
                try:
                    ticker = split['symbol']

                    # Get company information
                    company_info = self.get_ticker_info(ticker)
                    if not company_info:
                        continue

                    # Get performance data
                    performance_data = self.get_performance_score(ticker)

                    # Format and post message
                    split_message = self.format_split_message(
                        ticker=ticker,
                        company_info=company_info,
                        split_info={
                            'numerator': split['numerator'],
                            'denominator': split['denominator']
                        },
                        performance_data=performance_data
                    )

                    if split_message:
                        post_twitter(split_message)
                        logger.info(f"Posted split message for {ticker}")
                        time.sleep(120)  # Wait 2 minutes between tweets
                    else:
                        logger.warning(f"No message generated for {ticker}")

                except Exception as e:
                    logger.error(f"Error processing split for {ticker}: {e}")
                    continue

            logger.info("Completed SplitBot workflow successfully")

        except Exception as e:
            logger.error(f"Error in main workflow: {e}")


if __name__ == "__main__":
    bot = SplitBot()
    bot.run()