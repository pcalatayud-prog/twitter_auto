# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import requests
from loguru import logger
from utils.utils import *
import datetime

class Execution_twitter_information:
    WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    WEEKENDS = ['Saturday', 'Sunday']
    def __init__(self):
        self.time = None
        self.exchange = "NYSE"
        self.api_key = "CjEKqo8XMebmmlyMciRaTX7UxkYtfEGj"
        self.current_year = datetime.datetime.now().year
        # today = datetime.date(2025, 1, 20)
        self.today = datetime.datetime.now().date()
        self.day_of_week = self.today.strftime('%A')
        self.market_open = None

    def is_market_open(self, api_key: str, exchange: str):
        """
        Check if the specified market is open using the Financial Modeling Prep API.

        params: str api_key of financial modelling
        ecxchange: str exchange of the american stock exchange to check if it is open or not today
        returns -> str: A message indicating whether the market is open or closed.
        """
        url = f"https://financialmodelingprep.com/api/v3/is-the-market-open?exchange={exchange}"
        params = {"apikey": api_key}

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

            if today_str in holidays:
                reason = holidays[today_str]
                logger.info(f"Today ({current_date}) the market is closed due to: {reason}.")
                self.market_open = False
            else:
                open_hour = data['stockMarketHours']['openingHour']
                close_hour = data['stockMarketHours']['closingHour']
                logger.info(
                    f"Today ({current_date}) the market is open from {open_hour} to {close_hour}."
                )
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

        self.is_weekend()





        stop=1
        return None

if __name__ == "__main__":

    twitting = Execution_twitter_information()
    processed_data = twitting.run()
