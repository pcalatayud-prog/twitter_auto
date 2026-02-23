# Script Created by: Pablo Calatayud
# Test script to mock main.py with different dates and times

import requests
from loguru import logger
from utils.utils import *
import datetime
from unittest.mock import patch, MagicMock

from weekdays.Dividends import DividendBot
from weekdays.Earnings import EarningsBot
from weekdays.Splits import SplitBot
from weekdays.Open_Market_Performance import Market_Daily_Performance

from weekends.performance_Automatization_US_ALL import US_StocksPerformance
from weekends.Performance_Mag_7 import StockSevenMagnificenPerformance
from weekends.Performance_Markets import MarketPerformanceTracker
from weekends.Performance_Sector import SectorPerformance

from utils.utils import post_twitter, bot_send_text
from config.api_keys import api_key


class MockedExecution_twitter_information:
    """Mocked version for testing with custom dates/times"""
    WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    WEEKENDS = ['Saturday', 'Sunday']

    def __init__(self, mock_date=None, mock_hour=None, mock_minute=None, dry_run=True):
        """
        Args:
            mock_date: datetime.date object (e.g., datetime.date(2025, 2, 24) for Monday Feb 24)
            mock_hour: int (0-23)
            mock_minute: int (0-59)
            dry_run: bool - if True, won't actually post to Twitter or run actual bots
        """
        # These days and hours are just used for the task scheduler to know what to run at different times.
        self.morning_update = [8]
        self.time_open = [15, 30]
        self.time_close = [22, 00]
        self.time_performance = [18, 30]
        self.performance_markets = ['Saturday', 8]
        self.performance_US_ALL = ['Saturday', 17]
        self.performance_mag_7 = ['Sunday', 8]
        self.performance_Sector = ['Sunday', 17]

        logger.add("logs/test_main.log", rotation="500 MB")
        logger.info('Initialising TEST Main')

        self.time = None
        self.exchange = "NASDAQ"
        self.api_key = api_key
        self.dry_run = dry_run

        # Use mocked date/time if provided, otherwise use current
        self.current_year = mock_date.year if mock_date else datetime.datetime.now().year
        self.today = mock_date if mock_date else datetime.datetime.now().date()
        self.current_hour = mock_hour if mock_hour is not None else datetime.datetime.now().hour
        self.current_minute = mock_minute if mock_minute is not None else datetime.datetime.now().minute
        self.day_of_week = self.today.strftime('%A')
        self.market_open = None

        logger.info(f"🧪 TEST MODE - Mocked to: {self.day_of_week}, {self.today}, {self.current_hour:02d}:{self.current_minute:02d}")
        print(f"🧪 TEST MODE - Mocked to: {self.day_of_week}, {self.today}, {self.current_hour:02d}:{self.current_minute:02d}")

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
                if self.morning_update[0] == self.current_hour:
                    logger.info(f"Today {current_date} the market is closed due to: {reason}.")
                    if not self.dry_run:
                        post_twitter(f"Today {current_date} the market is closed due to: {reason}.")
                    else:
                        print(f"[DRY RUN] Would tweet: Today {current_date} the market is closed due to: {reason}.")
                self.market_open = False
            else:
                # Not a holiday - market is open
                if self.morning_update[0] == self.current_hour:
                    logger.info(f"Today {current_date} the {self.exchange} is open.")
                    if not self.dry_run:
                        post_twitter(f"Today {current_date} the {self.exchange} is open (09:30 - 16:00 ET).")
                    else:
                        print(f"[DRY RUN] Would tweet: Today {current_date} the {self.exchange} is open (09:30 - 16:00 ET).")
                self.market_open = True

        except FileNotFoundError:
            logger.error(f"Market holidays file not found. Assuming market is open.")
            if not self.dry_run:
                bot_send_text(f"⚠️ Market holidays file not found. Assuming market is open.")
            else:
                print(f"[DRY RUN] Would send telegram: ⚠️ Market holidays file not found.")
            self.market_open = True
        except Exception as e:
            logger.error(f"Error checking market holidays: {e}")
            if not self.dry_run:
                bot_send_text(f"⚠️ Error checking market holidays: {e}\nAssuming market is open on weekday.")
            else:
                print(f"[DRY RUN] Would send telegram: ⚠️ Error checking market holidays: {e}")
            self.market_open = True

        return None

    def is_weekend(self):
        """
        Check if today is a weekend and update the market status.
        """
        if self.day_of_week in self.WEEKENDS:
            logger.info(f"{self.day_of_week} is a weekend. The market is closed.")
            print(f"✓ {self.day_of_week} is a weekend. The market is closed.")
            self.market_open = False
        else:
            logger.info(f"{self.day_of_week} is a weekday. The market could be open.")
            print(f"✓ {self.day_of_week} is a weekday. Checking market status...")
            self.is_market_open()

        return None

    def run(self):
        print(f"\n{'='*60}")
        print(f"Starting test run for: {self.day_of_week}, {self.today}, {self.current_hour:02d}:{self.current_minute:02d}")
        print(f"{'='*60}\n")

        if not self.dry_run:
            send_telegram_message('🧪 Running TEST main.py')

        self.is_weekend()

        if self.day_of_week in self.WEEKDAYS and self.market_open == True:
            logger.info("Today the market opens")
            print(f"✓ Market is open today ({self.day_of_week})")

            if self.current_hour == self.morning_update[0]:
                print(f"\n🔔 MATCH: Morning update time (8am)")
                logger.info("Running Earnings + Dividends + Splits")

                if self.dry_run:
                    print("  [DRY RUN] Would run EarningsBot")
                    print("  [DRY RUN] Would run DividendBot")
                    print("  [DRY RUN] Would run SplitBot")
                else:
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

            elif self.current_hour == self.time_open[0] and self.current_minute >= self.time_open[1]:
                print(f"\n🔔 MATCH: Market just opened (15:30+)")
                logger.info('The market just opened -> ')

                if self.dry_run:
                    print("  [DRY RUN] Would run Market_Daily_Performance.market_just_open()")
                else:
                    try:
                        market = Market_Daily_Performance()
                        market.market_just_open()
                    except Exception as e:
                        logger.error(f"Market open performance failed: {e}")
                        bot_send_text(f"❌ Market Open Error: {type(e).__name__}: {str(e)}")

            elif self.current_hour == self.time_performance[0]:
                print(f"\n🔔 MATCH: Market performance check (18:30)")
                logger.info('The market has been opened for 3 hours -> ')

                if self.dry_run:
                    print("  [DRY RUN] Would run Market_Daily_Performance.market_is_open()")
                else:
                    try:
                        market = Market_Daily_Performance()
                        market.market_is_open()
                    except Exception as e:
                        logger.error(f"Market performance check failed: {e}")
                        bot_send_text(f"❌ Market Performance Error: {type(e).__name__}: {str(e)}")

            elif self.current_hour == self.time_close[0]:
                print(f"\n🔔 MATCH: Market just closed (22:00)")
                logger.info('The market just closed -> ')

                if self.dry_run:
                    print("  [DRY RUN] Would run Market_Daily_Performance.market_is_just_closed()")
                    print("  [DRY RUN] Would run Market_Daily_Performance.market_1_week()")
                else:
                    try:
                        market = Market_Daily_Performance()
                        market.market_is_just_closed()
                        market.market_1_week()
                    except Exception as e:
                        logger.error(f"Market close performance failed: {e}")
                        bot_send_text(f"❌ Market Close Error: {type(e).__name__}: {str(e)}")
            else:
                print(f"\n⏰ No scheduled task for {self.current_hour:02d}:{self.current_minute:02d} on weekdays")

        elif self.day_of_week in self.WEEKENDS:
            logger.info('Today the market is closed -> Weekend.')
            print(f"✓ Weekend detected ({self.day_of_week})")

            if self.day_of_week == self.performance_markets[0] and self.current_hour == self.performance_markets[1]:
                print(f"\n🔔 MATCH: Market Performance (Saturday 8am)")

                if self.dry_run:
                    print("  [DRY RUN] Would run MarketPerformanceTracker")
                else:
                    try:
                        tracker = MarketPerformanceTracker()
                        tracker.run()
                    except Exception as e:
                        logger.error(f"MarketPerformanceTracker failed: {e}")
                        bot_send_text(f"❌ Market Performance Tracker Error: {type(e).__name__}: {str(e)}")

            elif self.day_of_week == self.performance_US_ALL[0] and self.current_hour == self.performance_US_ALL[1]:
                print(f"\n🔔 MATCH: US Stocks Performance (Saturday 17:00)")

                if self.dry_run:
                    print("  [DRY RUN] Would run US_StocksPerformance")
                else:
                    try:
                        US_stocks = US_StocksPerformance()
                        US_stocks.run()
                    except Exception as e:
                        logger.error(f"US_StocksPerformance failed: {e}")
                        bot_send_text(f"❌ US Stocks Performance Error: {type(e).__name__}: {str(e)}")

            elif self.day_of_week == self.performance_mag_7[0] and self.current_hour == self.performance_mag_7[1]:
                print(f"\n🔔 MATCH: Magnificent 7 Performance (Sunday 8am)")

                if self.dry_run:
                    print("  [DRY RUN] Would run StockSevenMagnificenPerformance")
                else:
                    try:
                        stock_performance = StockSevenMagnificenPerformance()
                        stock_performance.run()
                    except Exception as e:
                        logger.error(f"Magnificent 7 Performance failed: {e}")
                        bot_send_text(f"❌ Mag 7 Performance Error: {type(e).__name__}: {str(e)}")

            elif self.day_of_week == self.performance_Sector[0] and self.current_hour == self.performance_Sector[1]:
                print(f"\n🔔 MATCH: Sector Performance (Sunday 17:00)")

                if self.dry_run:
                    print("  [DRY RUN] Would run SectorPerformance")
                else:
                    try:
                        stock_perf = SectorPerformance()
                        stock_perf.run()
                    except Exception as e:
                        logger.error(f"SectorPerformance failed: {e}")
                        bot_send_text(f"❌ Sector Performance Error: {type(e).__name__}: {str(e)}")
            else:
                print(f"\n⏰ No scheduled task for {self.current_hour:02d}:{self.current_minute:02d} on {self.day_of_week}")
                logger.info('Nothing to post...')
        else:
            print(f"\n❌ No tasks - Market closed or not a valid time")
            logger.info('Nothing to post...')

        print(f"\n{'='*60}")
        print(f"Test run completed")
        print(f"{'='*60}\n")
        return None


def run_test_scenarios():
    """Run multiple test scenarios to verify all scheduled tasks"""

    scenarios = [
        # Weekday scenarios
        ("Monday morning - Earnings/Dividends/Splits", datetime.date(2025, 2, 24), 8, 0),
        ("Monday market open", datetime.date(2025, 2, 24), 15, 30),
        ("Tuesday market performance", datetime.date(2025, 2, 25), 18, 30),
        ("Wednesday market close", datetime.date(2025, 2, 26), 22, 0),
        ("Thursday wrong time", datetime.date(2025, 2, 27), 12, 0),

        # Weekend scenarios
        ("Saturday market performance", datetime.date(2025, 2, 22), 8, 0),
        ("Saturday US stocks", datetime.date(2025, 2, 22), 17, 0),
        ("Sunday Mag 7", datetime.date(2025, 2, 23), 8, 0),
        ("Sunday Sector", datetime.date(2025, 2, 23), 17, 0),
        ("Sunday wrong time", datetime.date(2025, 2, 23), 12, 0),
    ]

    print("\n" + "="*80)
    print("RUNNING ALL TEST SCENARIOS")
    print("="*80 + "\n")

    for scenario_name, test_date, test_hour, test_minute in scenarios:
        print(f"\n{'*'*80}")
        print(f"SCENARIO: {scenario_name}")
        print(f"{'*'*80}")

        try:
            twitting = MockedExecution_twitter_information(
                mock_date=test_date,
                mock_hour=test_hour,
                mock_minute=test_minute,
                dry_run=True  # Set to False to actually run the bots
            )
            twitting.run()
        except Exception as e:
            print(f"❌ ERROR in scenario '{scenario_name}': {e}")
            logger.exception(f"Error in test scenario: {scenario_name}")

    print("\n" + "="*80)
    print("ALL SCENARIOS COMPLETED")
    print("="*80 + "\n")


def test_with_actual_bot_content(mock_date, mock_hour, mock_minute, bot_name="EarningsBot"):
    """
    Run actual bots but mock Twitter/Telegram to see what would be posted.
    This shows you the REAL content without actually posting.

    Args:
        mock_date: datetime.date object
        mock_hour: hour (0-23)
        mock_minute: minute (0-59)
        bot_name: Which bot to test (EarningsBot, DividendBot, etc.)
    """
    print(f"\n{'='*80}")
    print(f"TESTING ACTUAL BOT CONTENT - {bot_name}")
    print(f"Date: {mock_date}, Time: {mock_hour:02d}:{mock_minute:02d}")
    print(f"{'='*80}\n")

    # Lists to capture tweets and telegram messages
    captured_tweets = []
    captured_telegrams = []

    def mock_post_twitter(text):
        """Capture what would be tweeted"""
        print(f"\n📱 WOULD TWEET:")
        print(f"{'─'*60}")
        print(text)
        print(f"{'─'*60}")
        captured_tweets.append(text)

    def mock_bot_send_text(text):
        """Capture what would be sent to Telegram"""
        print(f"\n💬 WOULD SEND TO TELEGRAM:")
        print(f"{'─'*60}")
        print(text)
        print(f"{'─'*60}")
        captured_telegrams.append(text)

    # Mock the Twitter and Telegram functions
    with patch('utils.utils.post_twitter', side_effect=mock_post_twitter):
        with patch('utils.utils.bot_send_text', side_effect=mock_bot_send_text):
            with patch('utils.utils.send_telegram_message', side_effect=mock_bot_send_text):
                try:
                    if bot_name == "EarningsBot":
                        bot = EarningsBot()
                        bot.run()
                    elif bot_name == "DividendBot":
                        bot = DividendBot()
                        bot.run()
                    elif bot_name == "SplitBot":
                        bot = SplitBot()
                        bot.run()
                    elif bot_name == "MarketPerformance":
                        market = Market_Daily_Performance()
                        # You can call specific methods based on the time
                        if mock_hour == 15 and mock_minute >= 30:
                            market.market_just_open()
                        elif mock_hour == 18:
                            market.market_is_open()
                        elif mock_hour == 22:
                            market.market_is_just_closed()
                    elif bot_name == "MarketPerformanceTracker":
                        tracker = MarketPerformanceTracker()
                        tracker.run()
                    elif bot_name == "US_StocksPerformance":
                        us_stocks = US_StocksPerformance()
                        us_stocks.run()
                    elif bot_name == "Mag7Performance":
                        mag7 = StockSevenMagnificenPerformance()
                        mag7.run()
                    elif bot_name == "SectorPerformance":
                        sector = SectorPerformance()
                        sector.run()

                    print(f"\n✅ Bot completed successfully")
                    print(f"Total tweets captured: {len(captured_tweets)}")
                    print(f"Total telegram messages captured: {len(captured_telegrams)}")

                except Exception as e:
                    print(f"\n❌ Bot failed with error: {e}")
                    logger.exception(f"Error running {bot_name}")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    import sys

    # Check if user wants to see actual bot content
    if len(sys.argv) > 1 and sys.argv[1] == "--show-content":
        print("\n" + "="*80)
        print("🎯 TESTING BOTS WITH REAL DATA (NO POSTING TO TWITTER)")
        print("="*80)
        print("\nThis will:")
        print("  ✅ Run the actual bots")
        print("  ✅ Fetch real data from APIs")
        print("  ✅ Generate real tweet content")
        print("  ❌ NOT post anything to Twitter (mocked)")
        print("\n" + "="*80 + "\n")

        # Test DividendBot
        print("\n" + "🔷"*40)
        print("TESTING: DividendBot - Shows dividend announcements")
        print("🔷"*40)
        test_with_actual_bot_content(
            mock_date=datetime.date.today(),
            mock_hour=8,
            mock_minute=0,
            bot_name="DividendBot"
        )

        # Test SplitBot
        print("\n" + "🔶"*40)
        print("TESTING: SplitBot - Shows stock splits")
        print("🔶"*40)
        test_with_actual_bot_content(
            mock_date=datetime.date.today(),
            mock_hour=8,
            mock_minute=0,
            bot_name="SplitBot"
        )

        # Test EarningsBot
        print("\n" + "🟢"*40)
        print("TESTING: EarningsBot - Shows earnings reports")
        print("🟢"*40)
        test_with_actual_bot_content(
            mock_date=datetime.date.today(),
            mock_hour=8,
            mock_minute=0,
            bot_name="EarningsBot"
        )

        # Test MarketPerformance at market open
        print("\n" + "🔵"*40)
        print("TESTING: Market Performance - Market Just Opened")
        print("🔵"*40)
        test_with_actual_bot_content(
            mock_date=datetime.date.today(),
            mock_hour=15,
            mock_minute=30,
            bot_name="MarketPerformance"
        )

        # Test MarketPerformance at market close
        print("\n" + "🟣"*40)
        print("TESTING: Market Performance - Market Just Closed")
        print("🟣"*40)
        test_with_actual_bot_content(
            mock_date=datetime.date.today(),
            mock_hour=22,
            mock_minute=0,
            bot_name="MarketPerformance"
        )

        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80)
        print("\nNote: If you see 'No data' messages, it means there were no")
        print("dividends/splits/earnings scheduled for today in the APIs.")
        print("="*80 + "\n")

    else:
        # Option 1: Run all test scenarios (default)
        print("\n💡 TIP: Run with --show-content to see actual tweet content")
        print("   Example: python test_main.py --show-content\n")
        run_test_scenarios()

        # Option 2: Test a specific date/time (uncomment to use)
        # print("\n🧪 Testing specific scenario:")
        # twitting = MockedExecution_twitter_information(
        #     mock_date=datetime.date(2025, 2, 24),  # Monday, Feb 24, 2025
        #     mock_hour=8,
        #     mock_minute=0,
        #     dry_run=True  # Set to False to actually run the bots
        # )
        # twitting.run()