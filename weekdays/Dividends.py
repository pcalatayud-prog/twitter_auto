from datetime import datetime, timedelta
import os
import json
import pandas as pd
import yfinance as yf
import tweepy
import requests
import time
from loguru import logger
from utils.utils import post_twitter, get_market_cap, get_earnings_calendar, get_dividend_calendar
from typing import List, Dict, Optional


class DividendBot:
    """
    A class to handle dividend announcements and post them to Twitter.
    """

    def __init__(self):
        """Initialize the DividendBot with necessary configurations."""
        logger.add("logs/dividend_bot.log", rotation="500 MB")
        logger.info('Initializing DividendBot')

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
                os.path.join(script_dir, "../top_3000_tickers.csv"),
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

    def _get_dates(self) -> List[str]:
        """Get the next 5 dates formatted as strings."""
        days = [self.current_date.date() + timedelta(days=i) for i in range(5)]
        return [date.strftime('%Y-%m-%d').replace("-0", "-").replace(" 0", " ") for date in days]

    def _get_days_of_week(self, date_list: List[str]) -> List[str]:
        """Get day names for the given dates."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return [days[datetime.strptime(date, '%Y-%m-%d').weekday()] for date in date_list]

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

    def get_ticker_dividend_info(self, ticker: str) -> pd.DataFrame:
        """Get dividend information for a specific ticker."""
        try:
            data = {
                "ticker": [],
                "dividendYield": [],
                "payoutRatio": [],
                "fiveYearAvgDividendYield": []
            }
            df = pd.DataFrame(data)

            stock = yf.Ticker(ticker)
            info = stock.info

            # Handle potential missing keys with get()
            dividend_yield = info.get("trailingAnnualDividendYield", 0)
            payout_ratio = info.get("payoutRatio", 0)
            five_year_yield = info.get("fiveYearAvgDividendYield", 0)

            row = [
                ticker,
                round(100 * float(dividend_yield), 2) if dividend_yield else 0,
                round(100 * float(payout_ratio), 2) if payout_ratio else 0,
                round(float(five_year_yield), 2) if five_year_yield else 0
            ]

            df.loc[len(df)] = row
            logger.info(f"Retrieved dividend info for {ticker}")
            return df

        except Exception as e:
            logger.error(f"Error getting dividend info for {ticker}: {e}")
            return pd.DataFrame()

    def get_dividend_for_ticker(self, ticker: str) -> Dict:
        """Get current dividend information for a specific ticker."""
        try:
            params = {
                'from': self.current_date_str,
                'to': self.current_date_str,
                'apikey': self.api_key
            }

            response = requests.get(f"{self.base_url}/stock_dividend_calendar", params=params)
            response.raise_for_status()

            data = response.json()
            dividends = [div for div in data if div.get('symbol') == ticker]

            if dividends:
                logger.info(f"Found dividend information for {ticker}")
                return dividends[0]
            else:
                logger.warning(f"No dividend information found for {ticker}")
                return {}

        except Exception as e:
            logger.error(f"Error getting dividend for ticker {ticker}: {e}")
            return {}

    def format_dividend_message(self, tickers: List[str]) -> str:
        """Format the dividend announcement message."""
        try:
            day = self.current_date.day
            suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
            formatted_date = self.current_date.strftime(f"%A, %d{suffix} of %B")

            tickers_symbol = ' '.join(f'${ticker}' for ticker in tickers)

            if tickers:
                message = (f"#SP500 and #NASDAQ100 #Companies that pay #dividend today "
                           f"{formatted_date}: \n #tickers -> {tickers_symbol} \n "
                           f"More #information in the next tweets -> \n")
            else:
                message = (f"#Today {formatted_date}, There are not #Scheduled "
                           f"#Dividends #Payments for #SP500 and #Nasdaq100 #Companies.")

            return message[:279] if len(message) > 280 else message

        except Exception as e:
            logger.error(f"Error formatting dividend message: {e}")
            return ""

    def format_company_dividend_message(self, ticker: str, dividend_info: pd.DataFrame, api_info: Dict) -> str:
        """Format the dividend message for a specific company."""
        try:
            company_info = self.get_ticker_info(ticker)

            company_name = company_info.get('company_name', ticker)
            industry = company_info.get('industry', 'Unknown')
            sector = company_info.get('sector', 'Unknown')

            message_0 = f"Today Report Dividends: \n #{company_name}, -> ${ticker}"

            if dividend_info.empty:
                logger.warning(f"No dividend info available for {ticker}")
                return ""

            payment_date = api_info.get('paymentDate', 'N/A')
            adj_dividend = api_info.get('adjDividend', 'N/A')
            div_yield = dividend_info.iloc[0]['dividendYield']
            five_year = dividend_info.iloc[0]['fiveYearAvgDividendYield']

            message_2 = (f"\n -> Payment Date = {payment_date} "
                         f"\n -> Dividend = {adj_dividend} $ "
                         f"\n -> Dividend Yield = {div_yield} %, "
                         f"\n -> Five Years Avg Dividend Yield = {five_year} % "
                         f"\n -> Industry: #{industry} "
                         f"\n -> Sector: #{sector}")

            final_message = message_0 + message_2 + "\n #Dividends #Stocks"

            # Check for duplicates
            if final_message in self.posted_messages:
                logger.warning(f"Duplicate message detected for {ticker}")
                return ""

            self.posted_messages.add(final_message)
            logger.info(f"Created message for {ticker}")
            return final_message

        except Exception as e:
            logger.error(f"Error formatting company dividend message for {ticker}: {e}")
            return ""

    def run(self):
        """Execute the main bot workflow."""
        logger.info("Starting DividendBot workflow")

        try:
            # Get dates and tickers
            dates = self._get_dates()
            today = dates[0]  # Get just the first date

            # Get dividend tickers for today
            tickers = get_dividend_calendar(today=self.current_date)
            logger.info(f"Retrieved {len(tickers) if tickers else 0} dividend tickers")

            if not tickers:
                message = self.format_dividend_message([])
                if message not in self.posted_messages:
                    post_twitter(message)
                    self.posted_messages.add(message)
                    logger.info("Posted no dividends message")
                return

            # Post initial message
            tickers_message = self.format_dividend_message(tickers)
            if tickers_message not in self.posted_messages:
                post_twitter(tickers_message)
                self.posted_messages.add(tickers_message)
                logger.info("Posted initial dividend message")

            # Process individual tickers
            for ticker in tickers[:5]:  # Limit to first 5 tickers
                try:
                    # Get dividend information
                    dividend_info = self.get_ticker_dividend_info(ticker)
                    if dividend_info.empty:
                        logger.warning(f"No dividend info found for {ticker}")
                        continue

                    # Get API dividend information
                    api_info = self.get_dividend_for_ticker(ticker)
                    if not api_info:
                        logger.warning(f"No API dividend info found for {ticker}")
                        continue

                    # Format and post message
                    company_message = self.format_company_dividend_message(
                        ticker, dividend_info, api_info
                    )

                    if company_message:
                        post_twitter(company_message)
                        logger.info(f"Posted dividend message for {ticker}")
                        time.sleep(120)  # Wait 2 minutes between tweets
                    else:
                        logger.warning(f"No message generated for {ticker}")

                except Exception as e:
                    logger.error(f"Error processing ticker {ticker}: {e}")
                    continue

            logger.info("Completed DividendBot workflow successfully")

        except Exception as e:
            logger.error(f"Error in main workflow: {e}")


if __name__ == "__main__":
    bot = DividendBot()
    bot.run()