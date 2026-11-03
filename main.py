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
        self.exchange = "NASDAQ"
        self.api_key = api_key
        self.current_year = datetime.datetime.now().year
        self.today = datetime.datetime.now().date()
        # self.today = datetime.date(2025, 1, 20)
        self.current_hour = datetime.datetime.now().hour
        self.current_minute = datetime.datetime.now().minute
        self.day_of_week = self.today.strftime('%A')
        self.market_open = None

        # Weekday slots are decided in New York time, so US/EU daylight-saving mismatches
        # (a few weeks in March and Oct/Nov) and a few minutes of delay after waking the PC don't matter.
        from zoneinfo import ZoneInfo
        ny = datetime.datetime.now(ZoneInfo("America/New_York"))
        ny_minutes = ny.hour * 60 + ny.minute
        if ny_minutes < 6 * 60:
            self.weekday_slot = "morning"       # scheduler 08:00 Spain  -> 02:00/03:00 ET
        elif 9 * 60 + 30 <= ny_minutes < 11 * 60:
            self.weekday_slot = "open"          # scheduler 15:31 Spain  -> 09:31/10:31 ET
        elif 12 * 60 <= ny_minutes < 14 * 60 + 30:
            self.weekday_slot = "midday"        # scheduler 18:30 Spain  -> 12:30/13:30 ET
        elif 16 * 60 <= ny_minutes < 18 * 60:
            self.weekday_slot = "close"         # scheduler 22:00 Spain  -> 16:00/17:00 ET
        else:
            self.weekday_slot = None
        logger.info(f"New York time {ny:%H:%M} -> weekday slot: {self.weekday_slot}")

    def is_market_open(self):
        """
        Check if the market is open by checking against local holiday calendar.
        Uses config/market_holidays.json to determine if today is a market holiday.

        returns -> None (sets self.market_open to True/False)
        """
        import json
        import os

        try:
            # Load market holidays from local JSON file
            holidays_file = os.path.join(os.path.dirname(__file__), 'utils', 'market_holidays.json')
            with open(holidays_file, 'r') as f:
                all_holidays = json.load(f)

            # Get holidays for current year
            year_str = str(self.current_year)
            holidays_this_year = all_holidays.get(year_str, {})

            today_str = self.today.strftime('%Y-%m-%d')
            current_date = self.today.strftime("%A, %d of %B")

            # Check if today is a holiday
            if today_str in holidays_this_year:
                reason = holidays_this_year[today_str]
                if self.weekday_slot == "morning":
                    logger.info(f"Today {current_date} the market is closed due to: {reason}.")
                    post_twitter(f"🏖️ US markets are closed today ({current_date}) for {reason}.\n\nSee you next session! #StockMarket")
                self.market_open = False
            else:
                # Not a holiday - market is open
                if self.weekday_slot == "morning":
                    logger.info(f"Today {current_date} the {self.exchange} is open.")
                    post_twitter(f"🔔 Good morning! US markets are open today, {current_date}.\n\n"
                                 f"🕤 09:30 – 16:00 ET (15:30 – 22:00 CET)\n\n#StockMarket #NASDAQ #SP500")
                self.market_open = True

        except FileNotFoundError:
            logger.error(f"Market holidays file not found. Assuming market is open.")
            bot_send_text(f"⚠️ Market holidays file not found. Assuming market is open.")
            self.market_open = True
        except Exception as e:
            logger.error(f"Error checking market holidays: {e}")
            bot_send_text(f"⚠️ Error checking market holidays: {e}\nAssuming market is open on weekday.")
            self.market_open = True

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
        if not wait_for_internet():
            return None
        bot_send_text('Running main.py')
        self.is_weekend()

        if self.day_of_week in self.WEEKDAYS and self.market_open==True:
            logger.info("Today the market opens")


            if self.weekday_slot == "morning":
                logger.info("Running Earnings + Dividends + Splits")
                try:
                    bot = EarningsBot()
                    bot.run()
                except Exception as e:
                    logger.error(f"EarningsBot failed: {e}")
                    bot_send_text(f"❌ EarningsBot Error: {type(e).__name__}: {str(e)}")

                time.sleep(300)

                try:
                    bot = DividendBot()
                    bot.run()
                except Exception as e:
                    logger.error(f"DividendBot failed: {e}")
                    bot_send_text(f"❌ DividendBot Error: {type(e).__name__}: {str(e)}")

                time.sleep(300)

                try:
                    bot = SplitBot()
                    bot.run()
                except Exception as e:
                    logger.error(f"SplitBot failed: {e}")
                    bot_send_text(f"❌ SplitBot Error: {type(e).__name__}: {str(e)}")

            elif self.weekday_slot == "open":
                logger.info('The market just opened -> ')
                try:
                    market = Market_Daily_Performance()
                    market.market_just_open()
                except Exception as e:
                    logger.error(f"Market open performance failed: {e}")
                    bot_send_text(f"❌ Market Open Error: {type(e).__name__}: {str(e)}")

            elif self.weekday_slot == "midday":
                logger.info('The market has been opened for 3 hours -> ')
                try:
                    market = Market_Daily_Performance()
                    market.market_is_open()
                except Exception as e:
                    logger.error(f"Market performance check failed: {e}")
                    bot_send_text(f"❌ Market Performance Error: {type(e).__name__}: {str(e)}")

            elif self.weekday_slot == "close":
                logger.info('The market just closed -> ')
                try:
                    market = Market_Daily_Performance()
                    market.market_is_just_closed()
                    market.market_1_week()
                except Exception as e:
                    logger.error(f"Market close performance failed: {e}")
                    bot_send_text(f"❌ Market Close Error: {type(e).__name__}: {str(e)}")

        elif self.day_of_week in self.WEEKENDS:
            logger.info('Today the market is closed -> Weekend.')

            if self.day_of_week == self.performance_markets[0] and self.current_hour == self.performance_markets[1]:
                try:
                    tracker = MarketPerformanceTracker()
                    tracker.run()
                except Exception as e:
                    logger.error(f"MarketPerformanceTracker failed: {e}")
                    bot_send_text(f"❌ Market Performance Tracker Error: {type(e).__name__}: {str(e)}")

            elif self.day_of_week == self.performance_US_ALL[0] and self.current_hour == self.performance_US_ALL[1]:
                try:
                    US_stocks = US_StocksPerformance()
                    US_stocks.run()
                except Exception as e:
                    logger.error(f"US_StocksPerformance failed: {e}")
                    bot_send_text(f"❌ US Stocks Performance Error: {type(e).__name__}: {str(e)}")

            elif self.day_of_week == self.performance_mag_7[0] and self.current_hour == self.performance_mag_7[1]:
                try:
                    stock_performance = StockSevenMagnificenPerformance()
                    stock_performance.run()
                except Exception as e:
                    logger.error(f"Magnificent 7 Performance failed: {e}")
                    bot_send_text(f"❌ Mag 7 Performance Error: {type(e).__name__}: {str(e)}")

            elif self.day_of_week == self.performance_Sector[0] and self.current_hour == self.performance_Sector[1]:
                try:
                    stock_perf = SectorPerformance()
                    stock_perf.run()
                except Exception as e:
                    logger.error(f"SectorPerformance failed: {e}")
                    bot_send_text(f"❌ Sector Performance Error: {type(e).__name__}: {str(e)}")

            else:
                logger.info('Nothing to post...')
                bot_send_text('Nothing to post...')
        else:
            logger.info('Nothing to post...')
            bot_send_text('Nothing to post...')
        return None

if __name__ == "__main__":
    try:
        twitting = Execution_twitter_information()
        processed_data = twitting.run()
    except Exception as e:
        error_msg = f"🚨 CRITICAL ERROR in main.py:\n{type(e).__name__}: {str(e)}"
        logger.exception("Critical error in main execution")
        try:
            bot_send_text(error_msg)
        except:
            pass  # Don't fail if telegram notification fails
        raise  # Re-raise to see full traceback
