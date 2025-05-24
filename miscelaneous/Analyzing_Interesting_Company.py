# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import requests
from loguru import logger
from utils.utils import *
import datetime
import numpy as np
import yfinance as yf
from finvizfinance.quote import finvizfinance
from utils.utils import post_twitter,bot_send_text
from config.api_keys import api_key

class finviz_companies:
    def __init__(self):
        self.tickers = None
        self.url = "https://financialmodelingprep.com/api/v3/stock/list"
        from config.api_keys import api_key
        self.api_key = api_key
        # Initialize
        logger.add("logs/analyzing_interesting_companies.log", rotation="500 MB")
        logger.info("initialize Analyzing Interesting Company")

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

        # filtered_tickers = filtered_tickers[:50]
        tickers = tickers[tickers['symbol'].isin(filtered_tickers)]

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


    def run(self):

        self.filtering_tickers()

        # Getting all the columns....
        stock = finvizfinance('TSLA')
        stock_fundament = stock.ticker_fundament()
        data = pd.DataFrame(columns=["ticker"] + list(stock_fundament.keys()))

        for ticker in self.tickers:
            try:
                time.sleep(0.2)
                stock = finvizfinance(ticker)
                stock_fundament = stock.ticker_fundament()
                new_tickers= {"ticker" : ticker}

                stock_fundamental_update = {**new_tickers,**stock_fundament}
                data.loc[len(data)] = stock_fundamental_update
            except Exception as e:
                logger.info(f'Error with ticker {ticker}, \nError:{e}')

        data['Perf Week'] = data['Perf Week'].str.replace('%', ' %')
        data['Perf Month'] = data['Perf Month'].str.replace('%', ' %')
        data['Perf Quarter'] = data['Perf Quarter'].str.replace('%', ' %')
        data['Perf Half Y'] = data['Perf Half Y'].str.replace('%', ' %')
        data['Perf YTD'] = data['Perf YTD'].str.replace('%', ' %')
        data['Perf Year'] = data['Perf Year'].str.replace('%', ' %')

        keys = ['ticker', 'Perf Week', 'Perf Month', 'Perf Quarter', 'Perf Half Y', 'Perf YTD', 'Perf Year']

        data = data[keys]

        data = data[~data.isin(['-']).any(axis=1)]

        text = generate_performance_tweet(data)

        return None


def generate_performance_tweet(df):
    """
    Generate a tweet-ready message with best and worst performing stocks
    based on multiple performance metrics.

    Parameters:
    df (pd.DataFrame): DataFrame with ticker and performance columns

    Returns:
    str: Tweet-ready message
    """

    # Performance columns to analyze
    perf_columns = ['Perf Week', 'Perf Month', 'Perf Quarter', 'Perf Half Y', 'Perf YTD', 'Perf Year']

    # Create a copy of the dataframe to work with
    data = df.copy()

    # Function to convert percentage strings to float
    def clean_percentage(value):
        if pd.isna(value) or value == '-':
            return np.nan
        try:
            # Remove % sign and convert to float
            return float(str(value).replace('%', '').strip())
        except:
            return np.nan

    # Clean and convert all performance columns
    for col in perf_columns:
        if col in data.columns:
            data[col + '_clean'] = data[col].apply(clean_percentage)

    # Calculate weighted performance score
    # Give more weight to recent performance and longer-term stability
    weights = {
        'Perf Week_clean': 0.15,
        'Perf Month_clean': 0.20,
        'Perf Quarter_clean': 0.20,
        'Perf Half Y_clean': 0.15,
        'Perf YTD_clean': 0.15,
        'Perf Year_clean': 0.15
    }

    # Calculate weighted score for each ticker
    data['score'] = 0
    data['valid_metrics'] = 0

    for col, weight in weights.items():
        if col in data.columns:
            # Add weighted score only for non-null values
            mask = ~data[col].isna()
            data.loc[mask, 'score'] += data.loc[mask, col] * weight
            data.loc[mask, 'valid_metrics'] += weight

    # Normalize score by the sum of weights for valid metrics
    data['normalized_score'] = data['score'] / data['valid_metrics']

    # Remove tickers with insufficient data (less than 3 valid metrics)
    min_weight_threshold = 0.4  # At least 40% of total possible weight
    valid_tickers = data[data['valid_metrics'] >= min_weight_threshold].copy()

    if len(valid_tickers) < 2:
        return "📊 Insufficient data to generate performance comparison tweet! 📈"

    # Find best and worst performers
    best_performer = valid_tickers.loc[valid_tickers['normalized_score'].idxmax()]
    worst_performer = valid_tickers.loc[valid_tickers['normalized_score'].idxmin()]

    # Format the scores
    best_score = best_performer['normalized_score']
    worst_score = worst_performer['normalized_score']

    # Create emoji indicators based on performance
    def get_performance_emoji(score):
        if score > 10:
            return "🚀🔥"
        elif score > 5:
            return "📈✨"
        elif score > 0:
            return "📊💚"
        elif score > -5:
            return "📉⚠️"
        elif score > -10:
            return "🔻😰"
        else:
            return "💥🆘"

    best_emoji = get_performance_emoji(best_score)
    worst_emoji = get_performance_emoji(worst_score)

    # Get actual performance values for best and worst performers
    best_ticker = best_performer['ticker']
    worst_ticker = worst_performer['ticker']

    # Build compact performance strings (only non-NaN values)
    time_periods = [
        ('1W', 'Perf Week'),
        ('1M', 'Perf Month'),
        ('3M', 'Perf Quarter'),
        ('6M', 'Perf Half Y'),
        ('YTD', 'Perf YTD'),
        ('1Y', 'Perf Year')
    ]

    best_perfs = []
    worst_perfs = []

    for period_name, col_name in time_periods:
        if col_name in data.columns:
            best_clean = best_performer[col_name + '_clean']
            worst_clean = worst_performer[col_name + '_clean']

            # Only add non-NaN values
            if not pd.isna(best_clean):
                best_perfs.append(f"{period_name}:{best_clean:+.1f}%")
            if not pd.isna(worst_clean):
                worst_perfs.append(f"{period_name}:{worst_clean:+.1f}%")

    # Build detailed performance with emojis for each period
    time_periods = [
        ('📅 1 Week', 'Perf Week'),
        ('📆 1 Month', 'Perf Month'),
        ('🗓️ 3 Months', 'Perf Quarter'),
        ('📊 6 Months', 'Perf Half Y'),
        ('🎯 Year-to-Date', 'Perf YTD'),
        ('🗓️ 1 Year', 'Perf Year')
    ]

    def get_period_emoji(value):
        if value > 5:
            return "🚀"
        elif value > 0:
            return "📈"
        elif value > -5:
            return "📉"
        else:
            return "🔻"

    best_lines = []
    worst_lines = []

    for period_name, col_name in time_periods:
        if col_name in data.columns:
            best_clean = best_performer[col_name + '_clean']
            worst_clean = worst_performer[col_name + '_clean']

            # Add lines for non-NaN values
            if not pd.isna(best_clean):
                emoji = get_period_emoji(best_clean)
                best_lines.append(f"{period_name}: {best_clean:+.1f}% {emoji}")
            if not pd.isna(worst_clean):
                emoji = get_period_emoji(worst_clean)
                worst_lines.append(f"{period_name}: {worst_clean:+.1f}% {emoji}")

    # Force both to show the same specific periods (including 1 Year)
    priority_periods = [
        ('📅 1W', 'Perf Week'),
        ('📆 1M', 'Perf Month'),
        ('🎯 YTD', 'Perf YTD'),
        ('📊 1Y', 'Perf Year')
    ]

    best_display = []
    worst_display = []

    for period_name, col_name in priority_periods:
        if col_name in data.columns:
            best_clean = best_performer[col_name + '_clean']
            worst_clean = worst_performer[col_name + '_clean']

            # Include if either stock has this data, show "N/A" for missing
            if not pd.isna(best_clean) or not pd.isna(worst_clean):
                if not pd.isna(best_clean):
                    best_emoji = get_period_emoji(best_clean)
                    best_display.append(f"{period_name}: {best_clean:+.1f}% {best_emoji}")
                else:
                    best_display.append(f"{period_name}: N/A")

                if not pd.isna(worst_clean):
                    worst_emoji = get_period_emoji(worst_clean)
                    worst_display.append(f"{period_name}: {worst_clean:+.1f}% {worst_emoji}")
                else:
                    worst_display.append(f"{period_name}: N/A")

    # Create detailed tweet with more context (under 280 characters)
    tweet = f"""📊MARKET PERFORMANCE ANALYSIS 📈

🏆 TOP PERFORMER: ${best_ticker} {best_emoji}
{chr(10).join(best_display)}

⚠️ UNDERPERFORMER: ${worst_ticker} {worst_emoji}
{chr(10).join(worst_display)}

💡 Market insights: Performance varies across timeframes 📈 🎯 ✨"""

    return tweet

if __name__ == "__main__":
    companies = finviz_companies()
    companies.run()