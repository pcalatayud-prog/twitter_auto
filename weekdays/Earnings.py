# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import pandas as pd
import yfinance as yf
from loguru import logger
import time

from datetime import datetime, timedelta
from utils.utils import post_twitter, get_market_cap, get_earnings_calendar, sort_tickers_by_market_cap
from constants import green_icon,red_icon, sector_emojis, industry_emojis


def format_company_message(ticker: str, performance_data: dict, company_info: dict) -> str:
    """Format the message for a specific company."""
    try:
        price_ytd = performance_data["price_change_ytd"]
        mdd_ytd = performance_data["MDD_ytd"]

        try:
            icon_sector = sector_emojis[company_info['sector']]
        except:
            icon_sector = ''
        try:
            icon_industry = industry_emojis[company_info['industry']]
        except:
            icon_industry = ''


        message_0 = (f"Today Publish Results: \n #{company_info['company_name']}, "
                     f"-> ${ticker} \n ->  Industry {icon_industry}: #{company_info['industry']} "
                     f"\n ->   Sector {icon_sector}: #{company_info['sector']}")

        message_1 = (f" \n Year To Day Performance: \n ->  Price Change YTD = "
                     f"{price_ytd} % icono, \n ->  Max DrawDown YTD = {mdd_ytd} %")

        if price_ytd>=0:
            message_1.replace("icono",'\U0001F7E2')
        else:
            message_1.replace("icono",'\U0001F534')

        return message_0 + message_1 + "\n #Earnings"

    except Exception as e:
        logger.error(f"Error formatting company message for {ticker}: {e}")
        return ""


class EarningsBot:
    """
    A class to handle earnings announcements and post them to Twitter.
    """
    def __init__(self):
        """Initialize the EarningsBot with necessary configurations."""
        logger.add("logs/earnings_bot.log", rotation="500 MB")
        logger.info('Initialising Earnings')
        # Set up date information
        self.current_date = datetime.now().strftime('%Y-%m-%d')

        # Add emoji indicators
        self.green = "\U0001F7E2"  # Green Circle
        self.red = "\U0001F534"  # Red Circle
        self.number_tickers_to_print = 2

    def _get_historical_price(self, ticker: str, start_date: str, end_date: str):
        """Download historical price data for a ticker."""
        try:
            return yf.download(ticker, start=start_date, end=end_date, progress=False)
        except Exception as e:
            logger.error(f"Error downloading historical data for {ticker}: {e}")
            return None

    def calculate_performance_score(self, ticker: str) -> dict:
        """Calculate performance metrics for a given ticker."""
        try:
            # Initialize DataFrame for performance metrics

            # Calculate dates
            current_date_date = datetime.strptime(self.current_date, '%Y-%m-%d')
            first_day_current_year = current_date_date.replace(month=1, day=1).strftime('%Y-%m-%d')
            current_date_str = current_date_date.strftime('%Y-%m-%d')
            current_date_plus_one_day = current_date_date + timedelta(days=1)
            current_date_plus_one_day_str = current_date_plus_one_day.strftime('%Y-%m-%d')

            # Get historical data
            df_1y = self._get_historical_price(ticker, first_day_current_year, current_date_plus_one_day_str)

            # Calculate returns and metrics
            df_1y["returns"] = df_1y["Close"].pct_change()
            df_1y["returns_perc"] = df_1y["returns"] + 1
            df_1y["creturns"] = df_1y["returns_perc"].cumprod()
            df_1y["cummax_BH"] = df_1y.creturns.cummax()
            df_1y["drawdown_BH"] = (df_1y["cummax_BH"] - df_1y["creturns"]) / df_1y["cummax_BH"]


            metrics = {}

            metrics["price_change_ytd"] = round(100 * (df_1y["creturns"].iloc[-1] - 1),2)
            metrics["MDD_ytd"] = round(100 * df_1y["drawdown_BH"].max(),2)
            metrics = {key: float(value) for key, value in metrics.items()}

            return metrics

        except Exception as e:
            logger.error(f"Error calculating performance score for {ticker}: {e}")
            return None

    def retrieve_earnings_tickers(self) -> list:
        """Retrieve list of tickers with earnings announcements."""
        try:
            df = get_earnings_calendar()
            df_today = df[df['date']==self.current_date]
            return df_today['symbol'].to_list()
        except Exception as e:
            logger.error(f"Error retrieving earnings tickers: {e}")
            return []

    @staticmethod
    def format_earnings_message(tickers: list) -> str:
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

            # Load ticker information once (outside the loop)
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                "config/top_3000_tickers.csv",
                os.path.join(script_dir, "config/top_3000_tickers.csv"),
                os.path.join(script_dir, "../config/top_3000_tickers.csv"),
            ]

            df_data = None
            for path in possible_paths:
                if os.path.exists(path):
                    df_data = pd.read_csv(path)
                    logger.info(f"Successfully loaded ticker information from {path}")
                    break

            if df_data is None:
                logger.error(f"Could not find top_3000_tickers.csv in any of these locations: {possible_paths}")
                return

            for ticker in tickers[:self.number_tickers_to_print]:  # Limit to first 10 tickers
                try:
                    # Calculate performance metrics
                    performance_data = self.calculate_performance_score(ticker)

                    if performance_data is None:
                        logger.warning(f"Could not calculate performance for {ticker}, skipping")
                        continue

                    # Get company information from CSV first
                    ticker_data = df_data[df_data['ticker']==ticker]

                    if ticker_data.empty:
                        # Ticker not in CSV, fetch from Yahoo Finance
                        logger.info(f"Ticker {ticker} not in CSV, fetching from Yahoo Finance")
                        try:
                            stock = yf.Ticker(ticker)
                            info = stock.info

                            # Create a company_info dict from yfinance data
                            company_info = {
                                'ticker': ticker,
                                'company_name': info.get('longName', ticker),
                                'industry': info.get('industry', 'Unknown'),
                                'sector': info.get('sector', 'Unknown')
                            }
                            logger.info(f"Successfully fetched info for {ticker} from Yahoo Finance")
                        except Exception as e:
                            logger.error(f"Could not fetch {ticker} from Yahoo Finance: {e}")
                            continue
                    else:
                        company_info = ticker_data.iloc[0]

                    # Format and post company message
                    company_message = format_company_message(
                        ticker, performance_data, company_info
                    )
                    if company_message:
                        post_twitter(company_message)
                        time.sleep(20)  # Wait between tweets

                except Exception as e:
                    logger.error(f"Error processing ticker {ticker}: {e}")
                    continue

            logger.info("Completed EarningsBot workflow successfully")

        except Exception as e:
            logger.error(f"Error in main workflow: {e}")


if __name__ == "__main__":
    bot = EarningsBot()
    bot.run()