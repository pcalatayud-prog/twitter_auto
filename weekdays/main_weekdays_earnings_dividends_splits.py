# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import requests
from loguru import logger
from utils.utils import *
import datetime

from weekdays.Dividends import DividendBot
from weekdays.Earnings import EarningsBot
from weekdays.Splits import SplitBot
from weekdays.Open_Market_Performance import Market_Daily_Performance

from weekends.performance_Automatization_US_ALL import US_StocksPerformance
from weekends.Performance_Mag_7 import StockSevenMagnificenPerformance
from weekends.Performance_Markets import MarketPerformanceTracker
from weekends.Performance_Sector import SectorPerformance

from utils.utils import post_twitter,bot_send_text
from config.api_keys import api_key


if __name__ == "__main__":

    logger.info("Running Earnings + Dividends + Splits")
    bot = EarningsBot()
    bot.run()
    time.sleep(300)
    bot = DividendBot()
    bot.run()
    time.sleep(300)
    bot = SplitBot()
    bot.run()