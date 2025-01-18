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

from utils.utils import post_twitter,bot_send_text
from config.api_keys import api_key

class CompanySentiment:
    """
    A class to handle earnings announcements and post them to Twitter.
    """
    def __init__(self):
        """Initialize the Company Sentiment Class """
        logger.add("../logs/company_sentiment.log", rotation="500 MB")
        logger.info('Initialising company_sentiment')

        self.tickers = getting_nasdaq100_sp500_tickers()
        self.api_key = api_key

        self.trendy_ticker = None
        self.message =  None

    def fetch_social_sentiment(self,symbol: str, page: int = 0):
        """
        Fetches social sentiment data for a given stock symbol.
        Parameters:
            symbol (str): Stock symbol (e.g., "AAPL").
            page (int): Page number for pagination (default is 0).
            api_key (str): API key for authentication.
        Returns:
            dict or np.nan: Social sentiment data as a dictionary, or np.nan if no data is available or an error occurs.
        """
        url = "https://financialmodelingprep.com/api/v4/historical/social-sentiment"
        params = {
            "symbol": symbol,
            "page": page,
            "apikey": self.api_key
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            # Check if data is empty
            if not data:
                logger.error("No data found.")
                return np.nan
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            return np.nan

    def calculate_composite_score(self,df):
        """
        Normalize metrics and calculate composite score
        """



        # Create copy to avoid modifying original
        df_scored = df.copy()

        # Normalize each metric
        df_scored['sentiment_normalized'] = df_scored['twitterSentiment']/df_scored['twitterSentiment'].median()
        df_scored['posts_normalized'] = df_scored['twitterPosts']/df_scored['twitterPosts'].median()
        df_scored['impressions_normalized'] = df_scored['twitterImpressions']/df_scored['twitterImpressions'].median()

        # Calculate composite score (equal weights: 1/3 each)
        df_scored['composite_score'] = (
                                               df_scored['sentiment_normalized']/3 +
                                               df_scored['posts_normalized']/3 +
                                               df_scored['impressions_normalized']/3
                                       )

        return df_scored[['ticker', 'twitterSentiment', 'twitterPosts', 'twitterImpressions','composite_score']]

    def getting_sentiment(self):

        rows = []

        for ticker in self.tickers:
            try:
                # Fetch the social sentiment data
                data = self.fetch_social_sentiment(ticker)
                last_data = data[0]
                date = last_data['date']
                twitter_sentiment = last_data['twitterSentiment']
                twitterPosts = last_data['twitterPosts']
                twitterImpressions = last_data['twitterImpressions']
                # Add a new row with the fetched data

                rows.append({"ticker": ticker, "date": date, "twitterSentiment": twitter_sentiment, "twitterPosts": twitterPosts, "twitterImpressions": twitterImpressions})
            except Exception as e:
                logger.error(f"Error when getting sentiment score for {ticker}: {e}")
                # Add a row with NaN values in case of an error
                rows.append({"ticker": ticker, "date": np.nan, "twitterSentiment": np.nan, "twitterPosts": np.nan, "twitterImpressions": np.nan})

        df_key_sentiment = pd.DataFrame(rows, columns=["ticker", "date", "twitterSentiment",'twitterPosts','twitterImpressions'])
        df_key_sentiment = df_key_sentiment.sort_values(by=['date', 'twitterSentiment'], ascending=[False, False])

        logger.info(f'Last 2 dates: {df_key_sentiment['date'].unique()[:2]}')

        df_key_sentiment = df_key_sentiment[df_key_sentiment['date'].isin(df_key_sentiment['date'].unique()[:2])]
        df_key_sentiment = df_key_sentiment.drop('date', axis=1)

        df_key_sentiment = df_key_sentiment[df_key_sentiment['twitterSentiment']>df_key_sentiment['twitterSentiment'].median()]
        df_key_sentiment = df_key_sentiment[df_key_sentiment['twitterPosts']>df_key_sentiment['twitterPosts'].median()]
        df_key_sentiment = df_key_sentiment[df_key_sentiment['twitterImpressions']>df_key_sentiment['twitterImpressions'].median()]

        df_key_sentiment = self.calculate_composite_score(df_key_sentiment)
        df_key_sentiment = df_key_sentiment.sort_values(by=['composite_score'], ascending=[False]).reset_index(drop=True)

        best_tickers = df_key_sentiment['ticker'].unique().tolist()

        self.trendy_ticker = best_tickers[0]

        return None

    def generate_trend_tweet(self) -> None:
        """
        Generate a tweet about a trending company with YTD performance metrics.

        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            str: Formatted tweet text
        """
        try:
            # Get stock data
            stock = yf.Ticker(self.trendy_ticker)

            # Get YTD data
            start_date = datetime.datetime(datetime.datetime.now().year, 1, 1)
            hist = stock.history(start=start_date)

            data = self.fetch_social_sentiment(self.trendy_ticker)
            data_last = data[0]

            if hist.empty:
                logger.error(f"Error: No data available for {self.trendy_ticker}")
                return f"Error: No data available for {self.trendy_ticker}"

            # Calculate YTD performance
            ytd_start_price = hist['Close'].iloc[0]
            current_price = hist['Close'].iloc[-1]
            ytd_performance = ((current_price - ytd_start_price) / ytd_start_price) * 100

            # Calculate maximum drawdown
            rolling_max = hist['Close'].expanding().max()
            drawdowns = (hist['Close'] - rolling_max) / rolling_max * 100
            max_drawdown = drawdowns.min()

            # Get company name
            company_name = stock.info.get('shortName', self.trendy_ticker)

            # Generate tweet
            tweet = (
                f"🔥{company_name}: -> ${self.trendy_ticker} is trending on X! \n"
                f"Posts of ${self.trendy_ticker} last hour: {data_last['twitterPosts']}\n"
                f"Impressions of ${self.trendy_ticker} last hour: {data_last['twitterImpressions']}\n"
                f"Likes of ${self.trendy_ticker} last hour: {data_last['twitterLikes']}\n"
                f"Comments of ${self.trendy_ticker} last hour: {data_last['twitterComments']}\n"
                f"Sentiment Score of ${self.trendy_ticker} last hour: {data_last['twitterSentiment']}\n"
                f"📈 YTD: {ytd_performance:.1f}%\n"
                f"📉 Max Drawdown: {max_drawdown:.1f}%\n"
            )
            logger.info(tweet)

            self.message = tweet

            return None

        except Exception as e:
            logger.error(f"Error generating tweet for {self.trendy_ticker}: {str(e)}")
            return None


    def run(self):

        self.getting_sentiment()

        self.generate_trend_tweet()

        post_twitter(self.message)

        return None

if __name__ == "__main__":

    company = CompanySentiment()
    company.run()