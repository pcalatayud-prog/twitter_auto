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

class Execution_twitter_information:
    WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    WEEKENDS = ['Saturday', 'Sunday']
    def __init__(self):

        # These days and hours are just used for the task scheduler to know what to run at different times.
        self.morning_update = [8]
        self.time_open = [15,30]
        self.time_close = [22,00]
        self.time_performance = [18,30]
        self.performance_markets = ['Saturday',8]
        self.performance_US_ALL = ['Saturday', 17]
        self.performance_mag_7= ['Sunday', 8]
        self.performance_Sector = ['Sunday', 17]


        logger.add("logs/main.log", rotation="500 MB")
        logger.info('Initialising Main')

        self.time = None
        self.exchange = "NYSE"
        self.api_key = api_key
        self.current_year = datetime.datetime.now().year
        self.today = datetime.datetime.now().date()
        # self.today = datetime.date(2025, 1, 20)
        self.current_hour = datetime.datetime.now().hour
        self.current_minute = datetime.datetime.now().minute
        self.day_of_week = self.today.strftime('%A')
        self.market_open = None

    def is_market_open(self):
        """
        Check if the specified market is open using the Financial Modeling Prep API.

        params: str api_key of financial modelling
        ecxchange: str exchange of the american stock exchange to check if it is open or not today
        returns -> str: A message indicating whether the market is open or closed.
        """
        url = f"https://financialmodelingprep.com/api/v3/is-the-market-open?exchange={self.exchange}"
        params = {"apikey": self.api_key}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            data_stockMarketHolidays = data['stockMarketHolidays']

            holidays_this_year = next(item for item in data_stockMarketHolidays if item['year'] == self.current_year)

            if holidays_this_year:
                holidays_this_year = {value: key for key, value in holidays_this_year.items()}
            else:
                holidays_this_year = {}

            today_str = self.today.strftime('%Y-%m-%d')
            current_date = self.today.strftime("%A, %d of %B")

            if today_str in holidays_this_year:
                reason = holidays_this_year[today_str]
                if self.morning_update[0]==self.current_hour:
                    logger.info(f"Today {current_date} the market is closed due to: {reason}.")
                    post_twitter(f"Today {current_date} the market is closed due to: {reason}.")
                self.market_open = False
            else:
                open_hour = data['stockMarketHours']['openingHour']
                close_hour = data['stockMarketHours']['closingHour']
                if self.morning_update[0] == self.current_hour:
                    logger.info(
                        f"Today {current_date} the market is open from {open_hour} to {close_hour}."
                    )
                    post_twitter(f"Today {current_date} the NYSE is open from {open_hour} to {close_hour}.")
                self.market_open = True

        except requests.RequestException as e:
            logger.error(f"Failed to fetch market data: {e}")
            self.market_open = None

        return None

    def is_weekend(self):
        """
        Check if today is a weekend and update the market status.
        """

        if self.day_of_week in self.WEEKENDS:
            logger.info(f"{self.day_of_week} is a weekend. The market is closed.")
            self.market_open = False
        else:
            logger.info(f"{self.day_of_week} is a weekday. The market could be open.")
            self.is_market_open()

        return None


    def run(self):
        send_telegram_message('Running main.py')
        self.is_weekend()

        if self.day_of_week in self.WEEKDAYS and self.market_open==True:
            logger.info("Today the market opens")


            if self.current_hour == self.morning_update[0]:
                logger.info("Running Earnings + Dividends + Splits")
                bot = EarningsBot()
                bot.run()
                time.sleep(300)
                bot = DividendBot()
                bot.run()
                time.sleep(300)
                bot = SplitBot()
                bot.run()

            elif self.current_hour == self.time_open[0] and self.current_minute >= self.time_open[1]:
                logger.info('The market just opened -> ')
                market = Market_Daily_Performance()
                market.market_just_open()

            elif self.current_hour == self.time_performance[0]:
                logger.info('The market has been opened for 3 hours -> ')
                market = Market_Daily_Performance()
                market.market_is_open()

            elif self.current_hour == self.time_close[0]:
                logger.info('The market just closed -> ')
                market = Market_Daily_Performance()
                market.market_is_just_closed()
                market.market_1_week()

        elif self.day_of_week in self.WEEKENDS:
            logger.info('Today the market is closed -> Weekend.')

            if self.day_of_week == self.performance_markets[0] and self.current_hour == self.performance_markets[1]:
                    tracker = MarketPerformanceTracker()
                    tracker.run()

            elif self.day_of_week == self.performance_US_ALL[0] and self.current_hour == self.performance_US_ALL[1]:
                    US_stocks = US_StocksPerformance()
                    US_stocks.run()
            elif self.day_of_week == self.performance_mag_7[0] and self.current_hour == self.performance_mag_7[1]:
                    stock_performance = StockSevenMagnificenPerformance()
                    stock_performance.run()

            elif self.day_of_week == self.performance_Sector[0] and self.current_hour == self.performance_Sector[1]:
                    stock_perf = SectorPerformance()
                    stock_perf.run()
            else:
                logger.info('Nothing to post...')
                bot_send_text('Nothing to post...')
        else:
            logger.info('Nothing to post...')
            bot_send_text('Nothing to post...')
        return None

if __name__ == "__main__":

    twitting = Execution_twitter_information()
    processed_data = twitting.run()
