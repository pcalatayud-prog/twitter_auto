import tweepy
import requests
from PIL import Image
from io import BytesIO
import yfinance as yf
import tempfile
import os

class TwitterBot:
    def __init__(self, bearer_token, consumer_key, consumer_secret, access_token, access_token_secret):
        """
        Initialize Twitter API client with credentials
        """
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )

        # For media upload, we need the API v1.1 client
        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret,
            access_token, access_token_secret
        )
        self.api = tweepy.API(auth)

    def get_company_logo(self, ticker):
        """
        Get company logo by ticker symbol.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Try Yahoo Finance logo URL first
            logo_url = info.get('logo_url')
            if logo_url:
                response = requests.get(logo_url)
                if response.status_code == 200:
                    return Image.open(BytesIO(response.content)), info

            # Fallback to Clearbit
            website = info.get('website', '')
            if website:
                domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
                clearbit_url = f"https://logo.clearbit.com/{domain}"
                response = requests.get(clearbit_url)
                if response.status_code == 200:
                    return Image.open(BytesIO(response.content)), info

            return None, info

        except Exception as e:
            print(f"Error fetching logo for {ticker}: {str(e)}")
            return None, None

    def post_stock_with_logo(self, ticker, custom_message=None):
        """
        Post a tweet with company logo and stock information.

        Args:
            ticker (str): Stock ticker symbol
            custom_message (str): Optional custom message

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get logo and company info
            logo, info = self.get_company_logo(ticker)

            if not info:
                print(f"Could not fetch information for {ticker}")
                return False

            # Create tweet message
            if custom_message:
                message = custom_message
            else:
                company_name = info.get('longName', ticker)
                current_price = info.get('currentPrice', 'N/A')
                message = f"📈 {company_name} (${ticker})\nCurrent Price: ${current_price}"

            # If we have a logo, upload it
            if logo:
                # Save logo to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    logo.save(temp_file.name)
                    temp_filename = temp_file.name

                try:
                    # Upload media
                    media = self.api.media_upload(temp_filename)

                    # Post tweet with image
                    tweet = self.client.create_tweet(
                        text=message,
                        media_ids=[media.media_id]
                    )

                    print(f"Successfully posted tweet with logo for {ticker}")
                    print(f"Tweet ID: {tweet.data['id']}")
                    return True

                finally:
                    # Clean up temporary file
                    os.unlink(temp_filename)

            else:
                # Post tweet without image
                tweet = self.client.create_tweet(text=message)
                print(f"Successfully posted tweet for {ticker} (no logo available)")
                print(f"Tweet ID: {tweet.data['id']}")
                return True

        except Exception as e:
            print(f"Error posting tweet for {ticker}: {str(e)}")
            return False

    def post_multiple_stocks(self, tickers, delay=60):
        """
        Post tweets for multiple stocks with delay between posts.

        Args:
            tickers (list): List of ticker symbols
            delay (int): Delay in seconds between posts
        """
        import time

        for ticker in tickers:
            print(f"Posting for {ticker}...")
            self.post_stock_with_logo(ticker)

            if ticker != tickers[-1]:  # Don't delay after last tweet
                print(f"Waiting {delay} seconds before next post...")
                time.sleep(delay)

# Example usage
if __name__ == "__main__":
    # You need to get these from Twitter Developer Portal
    BEARER_TOKEN = "your_bearer_token_here"
    CONSUMER_KEY = "your_consumer_key_here"
    CONSUMER_SECRET = "your_consumer_secret_here"
    ACCESS_TOKEN = "your_access_token_here"
    ACCESS_TOKEN_SECRET = "your_access_token_secret_here"

    # Initialize bot
    bot = TwitterBot(
        bearer_token=BEARER_TOKEN,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    # Post single stock
    bot.post_stock_with_logo('AAPL')

    # Post multiple stocks
    popular_stocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    bot.post_multiple_stocks(popular_stocks, delay=60)

    # Post with custom message
    bot.post_stock_with_logo('AAPL', "🍎 Apple is looking strong today! #AAPL #Stocks")