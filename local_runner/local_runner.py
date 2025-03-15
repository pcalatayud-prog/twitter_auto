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

def get_dividend_dates(ticker):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    stock = yf.Ticker(ticker, session=session)
    dividends = stock.dividends
    return dividends.index.strftime('%Y-%m-%d').tolist() if not dividends.empty else "No data available."


if __name__ == "__main__":
    ticker = 'AAPL'
    dates = get_dividend_dates(ticker)
    print("Dividend dates:", dates)

