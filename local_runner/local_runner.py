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
from datetime import datetime, UTC
import yfinance as yf

def unix_to_yyyy_mm_dd(unix_date: int):
    date_str = datetime.fromtimestamp(unix_date,UTC).strftime('%Y-%m-%d')
    return date_str


def get_dividends(tickers_symbol):

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

if __name__ == "__main__":

    ticker = ["COKE","ZIM"]  # Replace with your desired ticker symbol
    dividends = get_dividends(ticker)

    print(dividends)

