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

from utils.utils import post_twitter,getting_nasdaq100_sp500_tickers,get_sp500_tickers

def getting_emojis():

    tickets = get_sp500_tickers()

    sector = []
    industry = []

    for ticker in tickets:
        stock = yf.Ticker(ticker)
        info = stock.info
        try:
            sector.append(info['sector'])
        except:
            pass

        try:
            industry.append(info['industry'])
        except:
            pass
    
    sector = list(set(sector))
    industry = list(set(industry))

    return None




if __name__ == "__main__":
    stop=1