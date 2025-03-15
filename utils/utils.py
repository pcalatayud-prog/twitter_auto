# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import tweepy
import requests
import pandas as pd
from loguru import logger
from datetime import datetime, timedelta, UTC
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib.parse
import time
import io
import random
from typing import List
import yfinance as yf
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
        logger.error(f"Tweet Error\nTweet Error\n: {e}\n{message}")

    random_number = random.randint(180, 600)
    logger.info(f"Pausing for {random_number} seconds to maintain proper intervals between Twitter posts.")
    time.sleep(random_number)
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


import pandas as pd


def get_sp500_tickers():
    """
    Retrieves the current list of S&P 500 constituent tickers from Wikipedia.
    Returns:
        list: A list of strings containing the ticker symbols of S&P 500 companies
    """
    # Wikipedia maintains an updated list of S&P 500 companies
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    try:
        # Read the first table from the Wikipedia page
        tables = pd.read_html(url)
        sp500_table = tables[0]

        # Extract the ticker symbols (usually in the first column)
        tickers = sp500_table['Symbol'].tolist()

        # Clean the tickers (remove any extra whitespace)
        tickers = [ticker.strip() for ticker in tickers]

        return tickers

    except Exception as e:
        print(f"Error retrieving S&P 500 tickers: {e}")
        return []

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

        # # Get S&P 500 constituents
        # sp500_response = requests.get(
        #     f"{base_url}/sp500_constituent",
        #     params={'apikey': api_key}
        # )

        sp500 = get_sp500_tickers()

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

    logger.info('earnings')

    from config.api_keys import alpha_key
    try:

        url = f'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&horizon=1month&apikey={alpha_key}'

        # Make the request and get the CSV data
        with requests.Session() as s:
            download = s.get(url,timeout=10)

            # Check if request was successful
            if download.status_code != 200:
                raise Exception(f"API request failed with status code {download.status_code}")

            # Decode the content
            decoded_content = download.content.decode('utf-8')

            # Use pandas to read the CSV directly from the string content
            df = pd.read_csv(io.StringIO(decoded_content))

            unique_tickers = getting_nasdaq100_sp500_tickers()

            df = df[df['symbol'].isin(unique_tickers)]

            df = df.rename(columns={'reportDate': 'date'})

            return df

    except Exception as e:
        logger.error(f"Error getting earnings calendar: {str(e)}")
        return pd.DataFrame()

def unix_to_yyyy_mm_dd(unix_date: int) -> str:
    date_str = datetime.fromtimestamp(unix_date,UTC).strftime('%Y-%m-%d')
    return date_str


def get_dividends(tickers_symbol) -> List:

    tickers_to_save = []

    for ticker_symbol in tickers_symbol:
        try:
            stock = yf.Ticker(ticker_symbol)
            info = stock.info
            dividends_date = info['dividendDate']
            date_str = unix_to_yyyy_mm_dd(dividends_date)

            today_date_str = datetime.now(UTC).strftime('%Y-%m-%d')
            print(f'{date_str} = {today_date_str}')
            print(today_date_str)
            if date_str==today_date_str:
                tickers_to_save.append(ticker_symbol)
        except Exception as e:
            print(f'Error ticker {ticker_symbol}. {e}')
        return tickers_to_save

def get_dividend_calendar() -> List:
    """
    Fetch dividend calendar data for SP500 and NASDAQ stocks.

    Returns:
        List: Filtered dividend calendar data for SP500 and NASDAQ stocks
    """

    unique_tickers = getting_nasdaq100_sp500_tickers()
    tickers = get_dividends(unique_tickers)
    return tickers


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

    A = get_dividend_calendar()
