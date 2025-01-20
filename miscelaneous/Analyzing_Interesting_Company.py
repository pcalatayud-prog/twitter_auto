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

        filtered_tickers = filtered_tickers[:20]
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

        for ticker in self.tickers[:4]:
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


        stop=1



        return None


if __name__ == "__main__":
    companies = finviz_companies()
    companies.run()