# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import pandas as pd
import numpy as np
import datetime
import yfinance as yf
from datetime import datetime, timedelta
import warnings
from loguru import logger

from utils.utils import post_twitter,getting_nasdaq100_sp500_tickers

class Market_Daily_Performance :
    def __init__(self, tickers=None):

        logger.add("logs/open_market_performance.log", rotation="500 MB")
        logger.info('Initializing Open Market Performance')

        # Emojis for positive/negative returns
        self.green = "\U0001F7E2"  # Green Circle
        self.red = "\U0001F534"    # Red Circle

        self.tickers = getting_nasdaq100_sp500_tickers()
        self.df_performance = None

    def getting_tickers_data(self):
        """Get performance data for all tickers at different time periods."""
        df_performance = pd.DataFrame(columns=["ticker", "ytd", "hf", "3mtd", "mtd", "wtd", "dtd"])

        dates = {
            'ytd': datetime.now() - timedelta(days=365),
            'hf': datetime.now() - timedelta(days=int(365 / 2)),
            '3mtd': datetime.now() - timedelta(days=90),
            'mtd': datetime.now() - timedelta(days=30),
            'wtd': datetime.now() - timedelta(days=7)
        }

        for ticker in self.tickers:
            try:
                stock_data = yf.download(ticker, start=dates['ytd'], end=datetime.now(), progress=False)
                returns = {}
                returns['dtd'] = round(100 * stock_data['Close'].pct_change().iloc[-1], 2)

                for period, start_date in dates.items():
                    period_data = stock_data[stock_data.index >= start_date]
                    if not period_data.empty:
                        price_open = period_data['Close'].iloc[0]
                        price_close = period_data['Close'].iloc[-1]
                        returns[period] = round(100 * (price_close - price_open) / price_open, 2)
                    else:
                        returns[period] = np.nan

                df_performance.loc[len(df_performance)] = [
                    ticker,
                    returns.get('ytd', np.nan),
                    returns.get('hf', np.nan),
                    returns.get('3mtd', np.nan),
                    returns.get('mtd', np.nan),
                    returns.get('wtd', np.nan),
                    returns.get('dtd', np.nan)
                ]

                logger.info(f"Successfully processed {ticker}")

            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                continue

        self.df_performance = df_performance

        return None

    def market_just_open(self):

        if self.df_performance is None:
            self.getting_tickers_data()

        df_today = pd.DataFrame(self.df_performance)
        df_today['dtd_abs'] = df_today['dtd'].abs()
        df_today_top = df_today.sort_values(by='dtd_abs', ascending=False).head(10)
        larger = "Nasdaq-100 &S SP-500 are open NOW! \nToday's Top-10 #GAPS: -> \n"

        for i in range(10):

            value = df_today_top['dtd'].iloc[i]
            ticket = df_today_top['ticker'].iloc[i]

            emoji = self.green if value > 0 else self.red
            larger = larger + f"{emoji} ${ticket} -> {value} %\n"

        logger.info('market_just_open()')
        logger.info(larger)
        post_twitter(larger)

        return None

    def market_is_open(self):

        if self.df_performance is None:
            self.getting_tickers_data()

        df_today = pd.DataFrame(self.df_performance)
        df_today['dtd_abs'] = df_today['dtd'].abs()
        df_today_top = df_today.sort_values(by='dtd_abs', ascending=False).head(10)
        larger = "Nasdaq-100 &S SP-500 are open. \nToday's Biggest Movers: \n"

        for i in range(10):

            value = df_today_top['dtd'].iloc[i]
            ticket = df_today_top['ticker'].iloc[i]

            emoji = self.green if value > 0 else self.red
            larger = larger + f"{emoji} ${ticket} -> {value} %\n"

        logger.info('market_is_open()')
        logger.info(larger)
        post_twitter(larger)

        return None

    def market_is_just_closed(self):

        if self.df_performance is None:
            self.getting_tickers_data()

        df_today = pd.DataFrame(self.df_performance)
        df_today['dtd_abs'] = df_today['dtd'].abs()
        df_today_top = df_today.sort_values(by='dtd_abs', ascending=False).head(10)
        larger = "Nasdaq-100 &S SP-500 are Closed NOW!. \nToday's Top 10 Gainers & Losers: \n"

        for i in range(10):

            value = df_today_top['dtd'].iloc[i]
            ticket = df_today_top['ticker'].iloc[i]

            emoji = self.green if value > 0 else self.red
            larger = larger + f"{emoji} ${ticket} -> {value} %\n"

        logger.info('market_is_just_closed()')
        logger.info(larger)
        post_twitter(larger)

        return None


    def market_1_week(self):

        if self.df_performance is None:
            self.getting_tickers_data()

        df_today = pd.DataFrame(self.df_performance)
        df_today['wtd_abs'] = df_today['wtd'].abs()
        df_today_top = df_today.sort_values(by='wtd_abs', ascending=False).head(10)
        larger = "Nasdaq-100 &S SP-500 are Closed NOW!. \n1-Week-To-Day -> Top 10 Gainers & Losers: \n"

        for i in range(10):

            value = df_today_top['wtd'].iloc[i]
            ticket = df_today_top['ticker'].iloc[i]

            emoji = self.green if value > 0 else self.red
            larger = larger + f"{emoji} ${ticket} -> {value} %\n"

        logger.info('market_1_week()')
        logger.info(larger)
        post_twitter(larger)

        return None


    def market_1_year(self):

        if self.df_performance is None:
            self.getting_tickers_data()

        df_today = pd.DataFrame(self.df_performance)
        df_today['ytd_abs'] = df_today['ytd'].abs()
        df_today_top = df_today.sort_values(by='ytd_abs', ascending=False).head(10)
        larger = "Nasdaq-100 &S SP-500 are Closed NOW!. \n1-Year-To-Day -> Top 10 Gainers & Losers: \n"

        for i in range(10):

            value = df_today_top['ytd'].iloc[i]
            ticket = df_today_top['ticker'].iloc[i]

            emoji = self.green if value > 0 else self.red
            larger = larger + f"{emoji} ${ticket} -> {value} %\n"

        logger.info('market_1_week()')
        logger.info(larger)
        post_twitter(larger)


        return None

if __name__ == "__main__":
    market = Market_Daily_Performance()

    market.market_just_open()
    market.market_is_open()
    market.market_is_just_closed()
    market.market_1_week()
    market.market_1_year()

