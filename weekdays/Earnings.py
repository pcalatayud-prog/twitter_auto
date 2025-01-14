# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import os
import json
import pandas as pd
import yfinance as yf
import tweepy
from loguru import logger
import time

from datetime import datetime, timedelta
from utils.utils import post_twitter, get_market_cap, get_earnings_calendar, sort_tickers_by_market_cap

class EarningsBot:
    """
    A class to handle earnings announcements and post them to Twitter.
    """
    def __init__(self):
        """Initialize the EarningsBot with necessary configurations."""
        logger.add("logs/earnings_bot.log", rotation="500 MB")
        logger.info('Intilizing Earnings')
        # Set up date information
        self.current_date = datetime.now().strftime('%Y-%m-%d')

        self.number_tickers_to_print = 3



    def _get_historical_price(self, ticker: str, start_date: str, end_date: str):
        """Download historical price data for a ticker."""
        try:
            return yf.download(ticker, start=start_date, end=end_date, progress=False)
        except Exception as e:
            logger.error(f"Error downloading historical data for {ticker}: {e}")
            return None

    def calculate_performance_score(self, ticker: str) -> pd.DataFrame:
        """Calculate performance metrics for a given ticker."""
        try:
            # Initialize DataFrame for performance metrics
            df_performance = pd.DataFrame(columns=[
                "ticker", "price_change_ytd", "MDD_ytd",
                "price_change_last_year", "MDD_last_year",
                "price_change_last_5_years", "MDD_5y"
            ])

            # Calculate dates
            date_five_years = (self.current_date - timedelta(days=365 * 5)).strftime('%Y-%m-%d')
            date_last_year = (self.current_date - timedelta(days=365)).strftime('%Y-%m-%d')
            first_day_current_year = self.current_date.replace(month=1, day=1).strftime('%Y-%m-%d')
            current_date = self.current_date.strftime('%Y-%m-%d')

            # Get historical data
            df_5y = self._get_historical_price(ticker, date_five_years, current_date)
            if df_5y is None:
                return None

            # Calculate returns and metrics
            df_5y["returns"] = df_5y["Adj Close"].pct_change()
            df_5y["returns_perc"] = df_5y["returns"] + 1
            df_5y["creturns"] = df_5y["returns_perc"].cumprod()

            # Calculate metrics for different time periods
            metrics = self._calculate_period_metrics(df_5y, date_last_year, first_day_current_year)

            # Add row to performance DataFrame
            df_performance.loc[0] = [ticker] + list(metrics.values())

            return df_performance

        except Exception as e:
            logger.error(f"Error calculating performance score for {ticker}: {e}")
            return None

    def _calculate_period_metrics(self, df: pd.DataFrame, date_last_year: str, first_day_current_year: str) -> dict:
        """Calculate metrics for different time periods."""
        metrics = {}

        # Calculate 5-year metrics
        df["cummax_BH"] = df.creturns.cummax()
        df["drawdown_BH"] = (df["cummax_BH"] - df["creturns"]) / df["cummax_BH"]

        # 5-year calculations
        metrics["price_change_5y"] = 100 * (df["creturns"].iloc[-1] - 1)
        metrics["MDD_5y"] = 100 * df["drawdown_BH"].max()

        # 1-year calculations
        df_1y = df[df.index > date_last_year].copy()
        df_1y["creturns"] = df_1y["returns_perc"].cumprod()
        df_1y["cummax_BH"] = df_1y.creturns.cummax()
        df_1y["drawdown_BH"] = (df_1y["cummax_BH"] - df_1y["creturns"]) / df_1y["cummax_BH"]

        metrics["price_change_1y"] = 100 * (df_1y["creturns"].iloc[-1] - 1)
        metrics["MDD_1y"] = 100 * df_1y["drawdown_BH"].max()

        # YTD calculations
        df_ytd = df[df.index > first_day_current_year].copy()
        df_ytd["creturns"] = df_ytd["returns_perc"].cumprod()
        df_ytd["cummax_BH"] = df_ytd.creturns.cummax()
        df_ytd["drawdown_BH"] = (df_ytd["cummax_BH"] - df_ytd["creturns"]) / df_ytd["cummax_BH"]

        metrics["price_change_ytd"] = 100 * (df_ytd["creturns"].iloc[-1] - 1)
        metrics["MDD_ytd"] = 100 * df_ytd["drawdown_BH"].max()

        return metrics

    def retrieve_earnings_tickers(self) -> list:
        """Retrieve list of tickers with earnings announcements."""
        try:
            df = get_earnings_calendar()
            df_today = df[df['date']==self.current_date]
            return df_today['symbol'].to_list()
        except Exception as e:
            logger.error(f"Error retrieving earnings tickers: {e}")
            return []

    def format_earnings_message(self, tickers: list) -> str:
        """Format the earnings announcement message."""
        current_date = datetime.now()
        day = current_date.day
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        formatted_date = current_date.strftime(f"%A, %d{suffix} of %B of %Y")

        tickers_symbol = ' '.join(f'${ticker}' for ticker in tickers)

        if tickers:
            return (f"#SP500 and #NASDAQ100 Companies that #publish #results today "
                    f"{formatted_date}: \n #tickers -> {tickers_symbol} \n "
                    f"More #information in the next tweets -> \n")
        else:
            return (f"#Today {formatted_date}, there are not #Scheduled #Earnings "
                    f"#Releases for #SP500 and #Nasdaq100 #Companies.")



    def format_company_message(self, ticker: str, performance_data: pd.DataFrame,
                               company_info: dict) -> str:
        """Format the message for a specific company."""
        try:
            price_ytd = round(performance_data.iloc[0]["price_change_ytd"], 2)
            mdd_ytd = round(performance_data.iloc[0]["MDD_ytd"], 2)

            message_0 = (f"Today Publish Results: \n #{company_info['company_name']}, "
                         f"-> ${ticker} \n ---->  Industry: #{company_info['industry']} "
                         f"\n ---->   Sector: #{company_info['sector']}")

            message_1 = (f" \n Year To Day Performance: \n ---->  Price Change YTD = "
                         f"{price_ytd} %, \n ---->  Max DrawDown YTD = {mdd_ytd} %")

            return message_0 + message_1 + "\n #Earnings #Report #Stocks"

        except Exception as e:
            logger.error(f"Error formatting company message for {ticker}: {e}")
            return ""

    def run(self):
        """Execute the main bot workflow."""
        logger.info("Starting EarningsBot workflow")

        try:
            # Get earnings tickers for today
            tickers = self.retrieve_earnings_tickers()
            tickers = sort_tickers_by_market_cap(tickers)

            logger.info(f"Retrieved {len(tickers)} tickers for earnings announcements")

            initial_message = self.format_earnings_message(tickers)
            logger.info('Initial Message:')
            logger.info(initial_message)
            post_twitter(initial_message)

            if not tickers:
                return

            for ticker in tickers[:self.number_tickers_to_print]:  # Limit to first 10 tickers
                try:
                    # Calculate performance metrics
                    performance_data = self.calculate_performance_score(ticker)
                    if performance_data is None:
                        continue

                    # Get company information
                    company_info = self._get_ticker_info(ticker)
                    if not company_info:
                        continue

                    # Format and post company message
                    company_message = self.format_company_message(
                        ticker, performance_data, company_info
                    )
                    if company_message:
                        post_twitter(company_message)
                        logger.info(company_message)
                        time.sleep(120)  # Wait 2 minutes between tweets

                except Exception as e:
                    logger.error(f"Error processing ticker {ticker}: {e}")
                    continue

            logger.info("Completed EarningsBot workflow successfully")

        except Exception as e:
            logger.error(f"Error in main workflow: {e}")


if __name__ == "__main__":
    bot = EarningsBot()
    bot.run()