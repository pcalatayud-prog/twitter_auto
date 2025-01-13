# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import pandas as pd
import numpy as np
import datetime
import yfinance as yf
from datetime import timedelta
import warnings
from loguru import logger

from utils.utils import post_twitter

class StockSevenMagnificenPerformance:
    def __init__(self, tickers=None):
        self.tickers = tickers or ["NVDA", "META", "AMZN", "MSFT", "GOOG", "AAPL", "TSLA"]
        self.df = pd.DataFrame({"symbol": self.tickers})
        self.df_performance = pd.DataFrame(columns=["ticker", "ytd", "hf", "3mtd", "mtd", "wtd", "dtd"])
        self.lista_hastaghs = ["\n#Stocks", ' #Nasdaq', ' #Investor', ' #StockMarket', ' #trader',' #tradigng',' #SP500',]

        # Emojis for positive/negative returns
        self.green = "\U0001F7E2"  # Green Circle
        self.red = "\U0001F534"    # Red Circle