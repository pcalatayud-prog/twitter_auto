#!/usr/bin/env python3
# Script Created by: Pablo Calatayud
# Simple bot runner to test individual bots with option to post to Twitter or not

"""
Usage:
    python run_bots.py dividends --dry-run          # Test DividendBot without posting
    python run_bots.py dividends                    # Run DividendBot and post to Twitter
    python run_bots.py earnings --dry-run           # Test EarningsBot without posting
    python run_bots.py splits --dry-run             # Test SplitBot without posting
    python run_bots.py all --dry-run                # Test all bots without posting
"""

import sys
from unittest.mock import patch
from loguru import logger

from weekdays.Dividends import DividendBot
from weekdays.Earnings import EarningsBot
from weekdays.Splits import SplitBot
from weekdays.Open_Market_Performance import Market_Daily_Performance

from weekends.performance_Automatization_US_ALL import US_StocksPerformance
from weekends.Performance_Mag_7 import StockSevenMagnificenPerformance
from weekends.Performance_Markets import MarketPerformanceTracker
from weekends.Performance_Sector import SectorPerformance

logger.add("logs/run_bots.log", rotation="500 MB")


def print_header(bot_name: str, dry_run: bool):
    """Print a nice header for the bot being run."""
    print("\n" + "=" * 80)
    print(f"{'🧪 TEST MODE' if dry_run else '🚀 LIVE MODE'} - Running {bot_name}")
    print("=" * 80)
    if dry_run:
        print("📝 DRY RUN: Will show what would be tweeted (NO ACTUAL POSTING)")
    else:
        print("⚠️  LIVE: Will POST to Twitter!")
    print("=" * 80 + "\n")


def mock_post_twitter(text):
    """Mock function to capture and display tweets without posting."""
    print("\n📱 WOULD TWEET:")
    print("─" * 70)
    print(text)
    print("─" * 70)


def mock_bot_send_text(text):
    """Mock function to capture and display Telegram messages without sending."""
    print("\n💬 WOULD SEND TO TELEGRAM:")
    print("─" * 70)
    print(text)
    print("─" * 70)


def run_dividend_bot(dry_run: bool = True):
    """Run the DividendBot."""
    print_header("DividendBot - Dividend Announcements", dry_run)

    if dry_run:
        with patch('utils.utils.post_twitter', side_effect=mock_post_twitter):
            with patch('utils.utils.bot_send_text', side_effect=mock_bot_send_text):
                try:
                    bot = DividendBot()
                    bot.run()
                    print("\n✅ DividendBot completed successfully!")
                except Exception as e:
                    print(f"\n❌ DividendBot failed: {e}")
                    logger.exception("DividendBot error")
    else:
        try:
            bot = DividendBot()
            bot.run()
            print("\n✅ DividendBot completed successfully!")
        except Exception as e:
            print(f"\n❌ DividendBot failed: {e}")
            logger.exception("DividendBot error")


def run_earnings_bot(dry_run: bool = True):
    """Run the EarningsBot."""
    print_header("EarningsBot - Earnings Reports", dry_run)

    if dry_run:
        with patch('utils.utils.post_twitter', side_effect=mock_post_twitter):
            with patch('utils.utils.bot_send_text', side_effect=mock_bot_send_text):
                try:
                    bot = EarningsBot()
                    bot.run()
                    print("\n✅ EarningsBot completed successfully!")
                except Exception as e:
                    print(f"\n❌ EarningsBot failed: {e}")
                    logger.exception("EarningsBot error")
    else:
        try:
            bot = EarningsBot()
            bot.run()
            print("\n✅ EarningsBot completed successfully!")
        except Exception as e:
            print(f"\n❌ EarningsBot failed: {e}")
            logger.exception("EarningsBot error")


def run_split_bot(dry_run: bool = True):
    """Run the SplitBot."""
    print_header("SplitBot - Stock Splits", dry_run)

    if dry_run:
        with patch('utils.utils.post_twitter', side_effect=mock_post_twitter):
            with patch('utils.utils.bot_send_text', side_effect=mock_bot_send_text):
                try:
                    bot = SplitBot()
                    bot.run()
                    print("\n✅ SplitBot completed successfully!")
                except Exception as e:
                    print(f"\n❌ SplitBot failed: {e}")
                    logger.exception("SplitBot error")
    else:
        try:
            bot = SplitBot()
            bot.run()
            print("\n✅ SplitBot completed successfully!")
        except Exception as e:
            print(f"\n❌ SplitBot failed: {e}")
            logger.exception("SplitBot error")


def run_market_open(dry_run: bool = True):
    """Run the Market Open performance."""
    print_header("Market Performance - Market Just Opened", dry_run)

    if dry_run:
        with patch('utils.utils.post_twitter', side_effect=mock_post_twitter):
            with patch('utils.utils.bot_send_text', side_effect=mock_bot_send_text):
                try:
                    market = Market_Daily_Performance()
                    market.market_just_open()
                    print("\n✅ Market Open completed successfully!")
                except Exception as e:
                    print(f"\n❌ Market Open failed: {e}")
                    logger.exception("Market Open error")
    else:
        try:
            market = Market_Daily_Performance()
            market.market_just_open()
            print("\n✅ Market Open completed successfully!")
        except Exception as e:
            print(f"\n❌ Market Open failed: {e}")
            logger.exception("Market Open error")


def run_market_close(dry_run: bool = True):
    """Run the Market Close performance."""
    print_header("Market Performance - Market Just Closed", dry_run)

    if dry_run:
        with patch('utils.utils.post_twitter', side_effect=mock_post_twitter):
            with patch('utils.utils.bot_send_text', side_effect=mock_bot_send_text):
                try:
                    market = Market_Daily_Performance()
                    market.market_is_just_closed()
                    print("\n✅ Market Close completed successfully!")
                except Exception as e:
                    print(f"\n❌ Market Close failed: {e}")
                    logger.exception("Market Close error")
    else:
        try:
            market = Market_Daily_Performance()
            market.market_is_just_closed()
            print("\n✅ Market Close completed successfully!")
        except Exception as e:
            print(f"\n❌ Market Close failed: {e}")
            logger.exception("Market Close error")


def run_all_weekday_bots(dry_run: bool = True):
    """Run all weekday bots (morning update)."""
    print("\n" + "🔷" * 40)
    print("Running ALL Weekday Morning Bots")
    print("🔷" * 40 + "\n")

    run_earnings_bot(dry_run)
    run_dividend_bot(dry_run)
    run_split_bot(dry_run)


def print_usage():
    """Print usage instructions."""
    print("""
Usage: python run_bots.py <bot> [--dry-run]

Available bots:
    dividends       - Run DividendBot (dividend announcements)
    earnings        - Run EarningsBot (earnings reports)
    splits          - Run SplitBot (stock splits)
    market-open     - Run Market Open performance
    market-close    - Run Market Close performance
    all             - Run all morning bots (earnings, dividends, splits)

Flags:
    --dry-run       - Test mode: show what would be tweeted without posting
    (no flag)       - Live mode: actually post to Twitter

Examples:
    python run_bots.py dividends --dry-run       # Test dividends without posting
    python run_bots.py dividends                 # Post dividends to Twitter
    python run_bots.py all --dry-run             # Test all bots without posting
    python run_bots.py earnings                  # Post earnings to Twitter
    """)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("❌ Error: No bot specified")
        print_usage()
        sys.exit(1)

    bot_name = sys.argv[1].lower()
    dry_run = '--dry-run' in sys.argv

    # Map of bot names to functions
    bot_map = {
        'dividends': run_dividend_bot,
        'earnings': run_earnings_bot,
        'splits': run_split_bot,
        'market-open': run_market_open,
        'market-close': run_market_close,
        'all': run_all_weekday_bots,
    }

    if bot_name in ['help', '-h', '--help']:
        print_usage()
        sys.exit(0)

    if bot_name not in bot_map:
        print(f"❌ Error: Unknown bot '{bot_name}'")
        print_usage()
        sys.exit(1)

    # Run the selected bot
    bot_map[bot_name](dry_run)

    print("\n" + "=" * 80)
    print("✅ Done!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # ========================================================================
    # 🎯 CONFIGURATION - Change these values to run different bots
    # ========================================================================

    # Which bot to run:
    # Options: 'dividends', 'earnings', 'splits', 'market-open', 'market-close', 'all'
    BOT_TO_RUN = 'earnings'  # <-- CHANGE THIS

    # Tweet or just test?
    # True  = Test mode (show what would be tweeted, don't actually post)
    # False = Live mode (ACTUALLY POST TO TWITTER!)
    DRY_RUN = False  # <-- CHANGE THIS (set to False to actually tweet!)

    # ========================================================================

    print("\n" + "🔧" * 40)
    print("CONFIGURATION:")
    print(f"  Bot to run: {BOT_TO_RUN}")
    print(f"  Mode: {'🧪 TEST MODE (dry-run)' if DRY_RUN else '🚀 LIVE MODE (will post to Twitter!)'}")
    print("🔧" * 40 + "\n")

    # Map of bot names to functions
    bot_map = {
        'dividends': run_dividend_bot,
        'earnings': run_earnings_bot,
        'splits': run_split_bot,
        # 'market-open': run_market_open,
        # 'market-close': run_market_close,
        # 'all': run_all_weekday_bots,
    }

    # Check if bot exists
    if BOT_TO_RUN.lower() not in bot_map:
        print(f"❌ Error: Unknown bot '{BOT_TO_RUN}'")
        print(f"Available bots: {', '.join(bot_map.keys())}")
        sys.exit(1)

    # Run the selected bot
    bot_map[BOT_TO_RUN.lower()](DRY_RUN)

    print("\n" + "=" * 80)
    print("✅ Done!")
    print("=" * 80 + "\n")