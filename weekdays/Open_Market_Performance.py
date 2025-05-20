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


class Market_Daily_Performance:


    def __init__(self, tickers=None):

        logger.add("logs/open_market_performance.log", rotation="500 MB")
        logger.info('Initialising Open Market Performance')

        # Emojis for positive/negative returns
        self.green = "\U0001F7E2"  # Green Circle
        self.red = "\U0001F534"    # Red Circle

        self.tickers = getting_nasdaq100_sp500_tickers()
        self.df_performance = None

    def getting_tickers_data(self):
        """Get performance data for all tickers at different time periods."""
        data = []

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
                row = {'ticker': ticker}
                if len(stock_data) >= 2:
                    last_close = stock_data['Close'].iloc[-1].item()
                    prev_close = stock_data['Close'].iloc[-2].item()
                    daily_return = round(((last_close / prev_close) - 1) * 100, 1)
                else:
                    daily_return = np.nan
                row['dtd'] = daily_return
                for period, start_date in dates.items():
                    period_data = stock_data[stock_data.index >= start_date]
                    if len(period_data) >= 2:
                        start_price = period_data['Close'].iloc[0].item()
                        end_price = period_data['Close'].iloc[-1].item()
                        period_return = round(((end_price / start_price) - 1) * 100, 1)
                    else:
                        period_return = np.nan
                    row[period] = period_return
                data.append(row)
                logger.info(f"Successfully processed {ticker}")
            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                # Add the ticker with NaN values if there's an error
                row = {
                    'ticker': ticker,
                    'ytd': np.nan,
                    'hf': np.nan,
                    '3mtd': np.nan,
                    'mtd': np.nan,
                    'wtd': np.nan,
                    'dtd': np.nan
                }
                data.append(row)
                continue
        # Create DataFrame from list of dictionaries
        df_performance = pd.DataFrame(data)
        # Ensure correct column order
        column_order = ['ticker', 'ytd', 'hf', '3mtd', 'mtd', 'wtd', 'dtd']
        df_performance = df_performance[column_order]
        # Convert all numeric columns to float
        numeric_columns = ['ytd', 'hf', '3mtd', 'mtd', 'wtd', 'dtd']
        for col in numeric_columns:
            df_performance[col] = pd.to_numeric(df_performance[col], errors='coerce')
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
        larger = "Nasdaq-100 &S SP-500 are Closed NOW!. \nToday's -> Top 10 Gainers & Losers: \n"

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

            value = round(df_today_top['ytd'].iloc[i])
            ticket = df_today_top['ticker'].iloc[i]

            emoji = self.green if value > 0 else self.red
            larger = larger + f"{emoji} ${ticket} -> {value} %\n"

        logger.info('market_1_year()')
        logger.info(larger)
        post_twitter(larger)


        return None

if __name__ == "__main__":
    print('main')
    market = Market_Daily_Performance()
    #
    # market.market_just_open()
    market.market_is_open()
    # market.market_is_just_closed()
    # market.market_1_week()
    # market.market_1_year()

