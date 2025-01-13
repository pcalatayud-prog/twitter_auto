# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import tweepy
import requests
import pandas as pd
from loguru import logger
from datetime import datetime, timedelta

from config.auth import api_key
from config.auth import api_key_secret
from config.auth import access_token
from config.auth import access_token_secret
from config.auth import bearer

def post_twitter(text: str):

    client = tweepy.Client(
        bearer_token=bearer,
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    message = text
    try:
        client.create_tweet(text=message)
        logger.success("Tweet posted: {}".format(message))
    except Exception as e:
        logger.error(e)

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

            return tickers

        except requests.RequestException as e:
            logger.error(f"Error getting dividend calendar: {e}")
            return []

    except Exception as e:
        logger.error(f"Unexpected error in get_dividend_calendar: {e}")
        return []

if __name__ == "__main__":
    tickers = get_dividend_calendar()
    stop=1