# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import tweepy
import requests
import pandas as pd
from loguru import logger
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib.parse
import time
from typing import List

from config.auth import api_key
from config.auth import api_key_secret
from config.auth import access_token
from config.auth import access_token_secret
from config.auth import bearer
from config.telegram import bot_token, bot_chatID

def post_twitter(text: str):

    client = tweepy.Client(
        bearer_token=bearer,
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    message = text
    logger.info(f"Tweet lenght: {len(message)}")
    try:
        client.create_tweet(text=message)
        bot_send_text("Tweet posted: {}".format(message))
        logger.success("Tweet posted: {}".format(message))
    except Exception as e:
        logger.error(e)
        bot_send_text(f"Tweet Error\nTweet Error\n: {e}\n{message}")


    return None


def get_market_cap(symbol):
    from config.api_keys import api_key
    url = f"https://financialmodelingprep.com/api/v3/market-capitalization/{symbol}?apikey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data:
            market_cap = data[0].get('marketCap', None)
            return market_cap
        else:
            return None  # No data for the given symbol
    else:
        return None  # API request failed

def getting_nasdaq100_sp500_tickers():

    from config.api_keys import api_key
    try:
        base_url = 'https://financialmodelingprep.com/api/v3'

        # Get NASDAQ constituents
        nasdaq_response = requests.get(
            f"{base_url}/nasdaq_constituent",
            params={'apikey': api_key}
        )
        nasdaq = [item["symbol"] for item in nasdaq_response.json()]

        # Get S&P 500 constituents
        sp500_response = requests.get(
            f"{base_url}/sp500_constituent",
            params={'apikey': api_key}
        )
        sp500 = [item["symbol"] for item in sp500_response.json()]

        # Get unique tickers
        unique_tickers = list(set(nasdaq + sp500))

        return unique_tickers
    except Exception as e:
        logger.error(e)
        return []


def get_earnings_calendar() -> pd.DataFrame():
    """
    Get earnings calendar for S&P 500 and NASDAQ constituents.

    Args:
        api_key (str): Financial Modeling Prep API key

    Returns:
        pd.DataFrame: Filtered earnings calendar data for S&P 500 and NASDAQ stocks
    """
    from config.api_keys import api_key
    try:
        base_url = 'https://financialmodelingprep.com/api/v3'

        # Get unique tickers
        unique_tickers = getting_nasdaq100_sp500_tickers()

        # Get earnings calendar
        earnings_response = requests.get(
            f"{base_url}/earning_calendar",
            params={'apikey': api_key}
        )

        # Convert to DataFrame and filter
        df_earnings = pd.DataFrame(earnings_response.json())
        filtered_df = df_earnings[df_earnings["symbol"].isin(unique_tickers)]
        logger.info(f'dataframe: \n{filtered_df.head(5)}')
        return filtered_df

    except Exception as e:
        logger.error(f"Error getting earnings calendar: {str(e)}")
        return pd.DataFrame()

def get_dividend_calendar(today: str, days_forward: int = 5) -> pd.DataFrame:
    """
    Fetch dividend calendar data for SP500 and NASDAQ stocks.

    Args:
        api_key (str): Financial Modeling Prep API key
        days_forward (int): Number of days to look forward (default: 5)

    Returns:
        pd.DataFrame: Filtered dividend calendar data for SP500 and NASDAQ stocks
    """
    from config.api_keys import api_key
    try:
        # Get unique tickers
        unique_tickers = getting_nasdaq100_sp500_tickers()
        if not unique_tickers:
            logger.error("No tickers retrieved")
            return pd.DataFrame()

        # Calculate date range
        today_date = today
        end_date = (datetime.now() + timedelta(days=days_forward)).strftime('%Y-%m-%d')

        # Get dividend calendar
        try:
            response = requests.get(
                'https://financialmodelingprep.com/api/v3/stock_dividend_calendar',
                params={
                    'from': today_date,
                    'to': end_date,
                    'apikey': api_key
                }
            )
            response.raise_for_status()

            # Convert to DataFrame
            df_dividends = pd.DataFrame(response.json())

            if df_dividends.empty:
                logger.warning("No dividend data found for the date range")
                return []

            # Sort by date
            df_dividends.sort_values(by='date', inplace=True)

            # Filter for our tickers
            filtered_df = df_dividends[df_dividends["symbol"].isin(unique_tickers)]

            logger.info(f"Found {len(filtered_df)} dividend entries for tracked tickers")

            tickers = filtered_df[filtered_df['date']==today_date]['symbol'].tolist()
            logger.info(f'Searching for companies that publish dividends today {today_date}')
            return tickers

        except requests.RequestException as e:
            logger.error(f"Error getting dividend calendar: {e}")
            return []

    except Exception as e:
        logger.error(f"Unexpected error in get_dividend_calendar: {e}")
        return []

def get_splits_calendar(today: str):
    # Define the API endpoint URL with your API key.
    api_url = 'https://financialmodelingprep.com/api/v3/stock_split_calendar'
    from config.api_keys import api_key
    # Define the parameters for the request (none needed for this specific endpoint).
    params = {
        'apikey': api_key
    }
    # Make a GET request to the API.
    response = requests.get(api_url, params=params)
    # Check if the request was successful (HTTP status code 200).
    if response.status_code == 200:

        data = response.json()
        df_tickers = pd.DataFrame(data)
        df = df_tickers[df_tickers["symbol"].isin(getting_nasdaq100_sp500_tickers())]
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['date']==today]

        return df
    else:
        return pd.DataFrame()

def send_telegram_message(bot_message, max_retries=3):
    """
    Send message to Telegram bot with retry logic and better error handling.
    Args:
        bot_message (str): Message to send
        max_retries (int): Maximum number of retry attempts
    """
    try:
        # Log the credentials (be careful with this in production)
        logger.info(f"Using bot_token: {bot_token[:10]}...")
        logger.info(f"Sending to chat_id: {bot_chatID}")

        # Create session with retry strategy
        session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)

        # URL encode the message
        encoded_message = urllib.parse.quote(bot_message)

        # Construct the URL
        send_text = (f'https://api.telegram.org/bot{bot_token}/sendMessage'
                     f'?chat_id={bot_chatID}'
                     f'&parse_mode=Markdown'
                     f'&text={encoded_message}')

        logger.info(f"Attempting to send message to Telegram")

        # Try to send the message
        response = session.get(send_text, timeout=10)
        response.raise_for_status()

        logger.info(f"Message sent successfully. Status code: {response.status_code}")
        return response

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {e}")
        time.sleep(2)  # Wait before retrying
        if max_retries > 0:
            logger.info(f"Retrying... {max_retries} attempts remaining")
            return send_telegram_message(bot_message, max_retries - 1)
        raise

    except requests.exceptions.Timeout as e:
        logger.error(f"Request timed out: {e}")
        if max_retries > 0:
            return send_telegram_message(bot_message, max_retries - 1)
        raise

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        if response.status_code == 429:  # Too Many Requests
            time.sleep(int(response.headers.get('Retry-After', 30)))
            return send_telegram_message(bot_message, max_retries - 1)
        raise

    except Exception as e:
        logger.error(f"Unexpected error sending message: {e}")
        raise

def bot_send_text(message):
    """Wrapper function for sending Telegram messages."""
    try:
        return send_telegram_message(message)
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return None


def sort_tickers_by_market_cap(tickers: List[str]) -> List[str]:
    """
    Sort a list of stock tickers by their market capitalization.

    Args:
        tickers (List[str]): List of stock ticker symbols

    Returns:
        List[str]: List of tickers sorted by market cap in descending order
    """
    # Create a list to store ticker-marketcap pairs
    market_caps = []

    # Get market cap for each ticker
    for ticker in tickers:
        market_cap = get_market_cap(ticker)

        # Only include tickers with valid market cap data
        if market_cap is not None:
            market_caps.append((ticker, market_cap))

        # Add delay between API calls
        time.sleep(1)

    # Sort the list by market cap in descending order
    sorted_tickers = sorted(market_caps, key=lambda x: x[1], reverse=True)

    # Return just the sorted ticker symbols
    return [ticker for ticker, _ in sorted_tickers]

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META","NVDA"]
    sorted_tickers = sort_tickers_by_market_cap(tickers)
    print(sorted_tickers)
