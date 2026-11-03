# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import os
import re
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


_SECRET_RE = re.compile(r"(apikey=|api_key=|/bot)([A-Za-z0-9:_-]{6,})", re.IGNORECASE)


def _redact_secrets(record):
    """Mask API keys / bot tokens that appear in log lines (e.g. inside request URLs)."""
    record["message"] = _SECRET_RE.sub(lambda m: m.group(1) + "***", record["message"])


logger.configure(patcher=_redact_secrets)


_URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
_DOMAIN_RE = re.compile(
    r"\b([A-Za-z0-9-]+)\.(?:com|net|org|io|co|ai|app|ly|me|info|biz|us|uk|es|de|fr|it|eu|tv|gg|xyz|finance|news|dev)\b",
    re.IGNORECASE,
)


def remove_links(text: str) -> str:
    """Strip anything X would turn into a link: posts with links cost ~13x more via the API."""
    cleaned = _URL_RE.sub("", text)
    cleaned = _DOMAIN_RE.sub(r"\1", cleaned)  # "Amazon.com" -> "Amazon"
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    if cleaned != text:
        logger.warning("Removed link(s) from tweet to avoid the X API link surcharge")
    return cleaned


TWEET_LIMIT = 280
GROK_TAG = "\n@Grok context"
_credits_depleted = False  # set after a 402 so the remaining bots stop spending calls


def _char_weight(ch: str) -> int:
    """X counts Latin/most punctuation as 1 and everything else (emoji, CJK...) as 2."""
    cp = ord(ch)
    if cp <= 4351 or 8192 <= cp <= 8205 or 8208 <= cp <= 8223 or 8242 <= cp <= 8247:
        return 1
    return 2


def tweet_length(text: str) -> int:
    """Approximate X's weighted length (slightly conservative for emoji sequences)."""
    return sum(_char_weight(ch) for ch in text)


def fit_tweet(text: str, limit: int = TWEET_LIMIT) -> str:
    """Trim text to X's weighted limit, dropping whole lines first so nothing is cut mid-word."""
    if tweet_length(text) <= limit:
        return text
    lines = text.split("\n")
    while len(lines) > 1 and tweet_length("\n".join(lines)) > limit:
        lines.pop(-2 if len(lines) > 2 else -1)  # keep the last line (usually hashtags)
    text = "\n".join(lines)
    while tweet_length(text) > limit:
        text = text[:-1]
    return text.rstrip()


def post_twitter(text: str, reply_to: str | None = None, add_grok: bool = True):
    """Post a tweet (optionally as a reply, to build threads). Returns the tweet id or None.

    Set the env var TWEET_DRY_RUN=1 to only log the tweet without calling the X API (free).
    """
    global _credits_depleted
    text = remove_links(text).strip()
    if add_grok and tweet_length(text + GROK_TAG) <= TWEET_LIMIT:
        text = text + GROK_TAG
    message = fit_tweet(text)
    logger.info(f"Tweet length (X weighted): {tweet_length(message)}")

    if os.getenv("TWEET_DRY_RUN") == "1":
        logger.info(f"[DRY RUN] Would post{' (reply)' if reply_to else ''}:\n{message}")
        return "dry-run"

    if _credits_depleted:
        logger.warning("Skipping tweet: X API credits are depleted")
        return None

    client = tweepy.Client(
        bearer_token=bearer,
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    try:
        response = client.create_tweet(text=message, in_reply_to_tweet_id=reply_to)
        bot_send_text("Tweet posted: {}".format(message))
        logger.success("Tweet posted: {}".format(message))
        return response.data["id"]
    except Exception as e:
        error_message = str(e)

        if "duplicate content" in error_message.lower():
            logger.warning(f"Skipping duplicate tweet: {message[:50]}...")
            bot_send_text(f"⚠️ Skipped duplicate tweet")
        elif "402" in error_message:
            _credits_depleted = True
            logger.error(f"Tweet Error: {e}")
            bot_send_text("❌ X API credits depleted. Top up in the developer console; skipping remaining tweets.")
        else:
            logger.error(f"Tweet Error: {e}")
            bot_send_text(f"❌ Tweet Error: {e}")
        return None

def get_market_cap(symbol) -> int:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        marketcap = info.get('marketCap')

    except:

        marketcap = 0
        logger.warning(f'Error downloading the marketCap for ticker {symbol}')

    return  marketcap


def get_sp500_tickers():
    """
    Retrieves the current list of S&P 500 constituent tickers from Wikipedia.
    Returns:
        list: A list of strings containing the ticker symbols of S&P 500 companies
    """
    # Wikipedia maintains an updated list of S&P 500 companies
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    try:
        # Wikipedia returns 403 without a browser-like User-Agent
        html = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (twitter_auto bot)"}, timeout=15).text
        tables = pd.read_html(io.StringIO(html))
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
    """
    Get combined list of S&P 500 and NASDAQ 100 tickers.
    Uses local JSON files as fallback when APIs fail.

    Returns:
        list: Combined unique tickers from both indices
    """
    import json
    import os
    from config.api_keys import api_key

    nasdaq = []
    sp500 = []

    # Try to get NASDAQ from API
    try:
        base_url = 'https://financialmodelingprep.com/api/v3'
        nasdaq_response = requests.get(
            f"{base_url}/nasdaq_constituent",
            params={'apikey': api_key},
            timeout=10
        )

        if nasdaq_response.status_code == 200:
            nasdaq_data = nasdaq_response.json()
            if isinstance(nasdaq_data, list):
                nasdaq = [item["symbol"] for item in nasdaq_data]
                logger.info(f"Successfully fetched {len(nasdaq)} NASDAQ tickers from API")
            else:
                logger.warning(f"NASDAQ API returned unexpected format")
        else:
            logger.warning(f"NASDAQ API request failed with status {nasdaq_response.status_code}")
    except Exception as e:
        logger.warning(f"NASDAQ API error: {e}")

    # If NASDAQ API failed, use local file
    if not nasdaq:
        try:
            nasdaq_file = os.path.join(os.path.dirname(__file__), 'nasdaq100_tickers.json')
            with open(nasdaq_file, 'r') as f:
                nasdaq_data = json.load(f)
                nasdaq = nasdaq_data.get('tickers', [])
                logger.info(f"Loaded {len(nasdaq)} NASDAQ tickers from local file")
        except Exception as e:
            logger.error(f"Error loading NASDAQ from local file: {e}")

    # Try to get S&P 500 from Wikipedia
    try:
        sp500 = get_sp500_tickers()
        if sp500:
            logger.info(f"Successfully fetched {len(sp500)} S&P 500 tickers")
    except Exception as e:
        logger.warning(f"S&P 500 scraping error: {e}")

    # If S&P 500 scraping failed, use local file
    if not sp500:
        try:
            sp500_file = os.path.join(os.path.dirname(__file__), 'sp500_tickers.json')
            with open(sp500_file, 'r') as f:
                sp500_data = json.load(f)
                sp500 = sp500_data.get('tickers', [])
                logger.info(f"Loaded {len(sp500)} S&P 500 tickers from local file")
        except Exception as e:
            logger.error(f"Error loading S&P 500 from local file: {e}")

    # Get unique tickers
    unique_tickers = list(set(nasdaq + sp500))
    logger.info(f"Total unique tickers: {len(unique_tickers)}")

    return unique_tickers


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
            download = s.get(url, timeout=10)

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
    date_str = datetime.fromtimestamp(unix_date, UTC).strftime('%Y-%m-%d')
    return date_str


def get_dividends(tickers_symbol) -> List:
    today_str = datetime.now().strftime('%Y-%m-%d')
    logger.info(f"Today's date: {today_str}")

    tickers_to_save = []
    dates_to_save = []

    for ticker_symbol in tickers_symbol:
        try:
            stock = yf.Ticker(ticker_symbol)
            info = stock.info
            dividends_date = info['dividendDate']
            date_str = unix_to_yyyy_mm_dd(dividends_date)
            tickers_to_save.append(ticker_symbol)
            dates_to_save.append(date_str)
            logger.info(f"ticker:{ticker_symbol}, dates:{date_str}")
        except Exception as e:
            logger.warning(f'Error ticker {ticker_symbol}. {e}')
        time.sleep(0.25)
    # Create and return DataFrame
    df = pd.DataFrame({
        'ticker': tickers_to_save,
        'date': dates_to_save
    })

    df['date'] = pd.to_datetime(df['date'])
    df_today = df[df['date'] == today_str]
    tickers_today = df_today['ticker'].tolist()

    return tickers_today


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
        df = df[df['date'] == today]

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
    """Wrapper function for sending Telegram messages. Never raises."""
    try:
        return send_telegram_message(message)
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return None


def wait_for_internet(max_wait_seconds: int = 300, check_every: int = 10) -> bool:
    """After the PC wakes from sleep Wi-Fi can take a while to reconnect; wait for it."""
    import socket
    waited = 0
    while waited <= max_wait_seconds:
        try:
            socket.create_connection(("api.x.com", 443), timeout=5).close()
            if waited:
                logger.info(f"Internet available after {waited}s")
            return True
        except OSError:
            time.sleep(check_every)
            waited += check_every
    logger.error(f"No internet connection after {max_wait_seconds}s")
    return False


def sort_tickers_by_market_cap(tickers: List[str]) -> List[str]:
    """
    Sort a list of stock tickers by their market capitalization.
    Tickers with no market cap data (0 or None) are placed at the end.

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

        # Include all tickers, use 0 for missing/invalid market cap
        if market_cap is None or market_cap == 0:
            market_caps.append((ticker, 0))
        else:
            market_caps.append((ticker, market_cap))

        # Add delay between API calls
        time.sleep(1)

    # Sort the list by market cap in descending order
    # Tickers with 0 market cap will naturally go to the end
    sorted_tickers = sorted(market_caps, key=lambda x: x[1], reverse=True)

    # Return just the sorted ticker symbols
    return [ticker for ticker, _ in sorted_tickers]


if __name__ == "__main__":
    A = get_dividend_calendar()

    stop = 1
