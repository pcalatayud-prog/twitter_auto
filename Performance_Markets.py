# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import pandas as pd
import requests
import numpy as np
import yfinance as yf

data = {
    "name": ["NASDAQ100", "SP500", "Russell2000", "DowJones", "FTSE100",
               "Nikkei225", "DAX", "CAC40", "EuroStoxx50", "Ibex35"],
    "symbol": ["^NDX", "^GSPC", "^RUT", "^DJI", "^FTSE", "^N225", "^GDAXI", "^FCHI", "^STOXX50E", "^IBEX"]
}

tickers = pd.DataFrame(data)
filtered_tickers = tickers["symbol"].tolist()
