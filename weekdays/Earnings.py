# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import os
import sys
import time
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from loguru import logger

from utils.utils import post_twitter, get_earnings_calendar, sort_tickers_by_market_cap, fit_tweet, tweet_length
from constants import sector_emojis

GREEN = "\U0001F7E2"
RED = "\U0001F534"
SESSION_LABEL = {"pre-market": ("🌅", "before the open"), "post-market": ("🌙", "after the close")}


def fmt_market_cap(value) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ""
    for unit, size in (("T", 1e12), ("B", 1e9), ("M", 1e6)):
        if value >= size:
            return f"${value / size:.1f}{unit}"
    return ""


def fmt_pct(value: float) -> str:
    return f"{value:+.1f}%"


def ticker_line(label: str, tickers: list, budget: int) -> str:
    """'🌅 Before open: $A $B $C +5 more' trimmed to fit `budget` weighted chars."""
    for n in range(len(tickers), 0, -1):
        rest = len(tickers) - n
        line = f"{label} " + " ".join(f"${t}" for t in tickers[:n]) + (f" +{rest} more" if rest else "")
        if tweet_length(line) <= budget:
            return line
    return f"{label} {len(tickers)} companies"


def format_company_message(ticker: str, performance: dict, info: dict, when_word: str) -> str:
    """Build the per-company tweet."""
    emoji, session_text = SESSION_LABEL.get(info.get("session"), ("📊", ""))
    name = info.get("company_name") or ticker
    header = f"{emoji} ${ticker} | {name} reports {when_word}" + (f" {session_text}" if session_text else "")

    lines = [header, ""]
    sector, industry = info.get("sector"), info.get("industry")
    if sector:
        lines.append(f"{sector_emojis.get(sector, '🏢')} {sector}" + (f" · {industry}" if industry else ""))
    cap = fmt_market_cap(info.get("market_cap"))
    if cap:
        lines.append(f"🏦 Market cap: {cap}")
    eps = info.get("eps_estimate")
    if eps is not None and not pd.isna(eps):
        lines.append(f"🎯 EPS estimate: ${eps:.2f}")
    lines.append("")

    ytd = performance["price_change_ytd"]
    lines.append(f"📈 YTD: {fmt_pct(ytd)} {GREEN if ytd >= 0 else RED}")
    lines.append(f"📉 Max drawdown YTD: -{performance['MDD_ytd']:.1f}%")
    off_high = performance.get("off_52w_high")
    if off_high is not None:
        lines.append("🚀 At its 52-week high" if off_high < 0.5 else f"📍 {off_high:.1f}% below 52-week high")

    lines += ["", "Beat or miss? 👇 #Earnings"]
    return fit_tweet("\n".join(lines))


class EarningsBot:
    """Posts an earnings thread: one summary tweet + replies for the biggest reporters."""

    def __init__(self, target_date: str | None = None, number_tickers_to_print: int = 2):
        logger.add("logs/earnings_bot.log", rotation="500 MB")
        logger.info("Initialising Earnings")
        today = datetime.now().date()
        self.target = datetime.strptime(target_date, "%Y-%m-%d").date() if target_date else today
        self.current_date = self.target.strftime("%Y-%m-%d")
        if self.target == today:
            self.when_word = "today"
        elif self.target == today + timedelta(days=1):
            self.when_word = "tomorrow"
        else:
            self.when_word = "on " + self.target.strftime("%a %b %-d") if os.name != "nt" else "on " + self.target.strftime("%a %b %#d")
        self.number_tickers_to_print = number_tickers_to_print

    def calculate_performance_score(self, ticker: str) -> dict | None:
        """YTD return, YTD max drawdown and distance from the 52-week high (data up to now)."""
        try:
            now = datetime.now()
            df = yf.download(ticker, start=(now - timedelta(days=372)).strftime("%Y-%m-%d"),
                             end=(now + timedelta(days=1)).strftime("%Y-%m-%d"), progress=False, auto_adjust=True)
            close = df["Close"]
            if isinstance(close, pd.DataFrame):  # newer yfinance returns multi-index columns
                close = close.iloc[:, 0]
            close = close.dropna()
            ytd = close[close.index >= pd.Timestamp(now.year, 1, 1)]
            # Base YTD on last year's final close so the first trading day counts too
            prev = close[close.index < pd.Timestamp(now.year, 1, 1)]
            base = prev.iloc[-1] if not prev.empty else ytd.iloc[0]
            series = pd.concat([pd.Series([base]), ytd.reset_index(drop=True)])
            drawdown = (series.cummax() - series) / series.cummax()
            high_52w = close[close.index >= pd.Timestamp(now - timedelta(days=365))].max()
            return {
                "price_change_ytd": float(100 * (ytd.iloc[-1] / base - 1)),
                "MDD_ytd": float(100 * drawdown.max()),
                "off_52w_high": float(100 * (1 - close.iloc[-1] / high_52w)),
            }
        except Exception as e:
            logger.error(f"Error calculating performance for {ticker}: {e}")
            return None

    def retrieve_earnings(self) -> pd.DataFrame:
        try:
            df = get_earnings_calendar()
            return df[df["date"] == self.current_date].copy()
        except Exception as e:
            logger.error(f"Error retrieving earnings calendar: {e}")
            return pd.DataFrame()

    def format_earnings_message(self, df: pd.DataFrame) -> str:
        """Summary tweet split by session, trimmed to fit."""
        nice_date = self.target.strftime("%a, %b ") + str(self.target.day)
        if df.empty:
            return (f"📅 No S&P 500 or Nasdaq-100 earnings {self.when_word} ({nice_date}).\n\n"
                    f"Quiet day on the calendar. #Earnings")

        head = f"📅 Earnings {self.when_word} · {nice_date}\n\n{len(df)} S&P 500 & Nasdaq-100 companies report\n\n"
        tail = "\n\nWhich one are you watching? 👇\n#Earnings"
        pre = df[df["timeOfTheDay"] == "pre-market"]["symbol"].tolist()
        post = df[df["timeOfTheDay"] == "post-market"]["symbol"].tolist()
        other = df[~df["timeOfTheDay"].isin(["pre-market", "post-market"])]["symbol"].tolist()
        groups = [g for g in (("🌅 Before open:", pre), ("🌙 After close:", post), ("🕒 Time TBA:", other)) if g[1]]

        budget = 280 - tweet_length(head + tail) - (len(groups) - 1)
        per_line = budget // max(len(groups), 1)
        body = "\n".join(ticker_line(label, tickers, per_line) for label, tickers in groups)
        return fit_tweet(head + body + tail)

    def company_info(self, ticker: str, row: pd.Series, df_data: pd.DataFrame | None) -> dict:
        info = {"session": row.get("timeOfTheDay"), "eps_estimate": row.get("estimate")}
        try:
            yinfo = yf.Ticker(ticker).info
            info.update(company_name=yinfo.get("shortName") or yinfo.get("longName"),
                        sector=yinfo.get("sector"), industry=yinfo.get("industry"),
                        market_cap=yinfo.get("marketCap"))
        except Exception as e:
            logger.warning(f"Yahoo Finance info failed for {ticker}: {e}")
        if df_data is not None and not info.get("company_name"):
            match = df_data[df_data["ticker"] == ticker]
            if not match.empty:
                r = match.iloc[0]
                info.update(company_name=r["company_name"], sector=r["sector"], industry=r["industry"],
                            market_cap=r["marketCap"])
        info["company_name"] = info.get("company_name") or str(row.get("name", ticker)).title()
        return info

    def run(self):
        logger.info(f"Starting EarningsBot workflow for {self.current_date}")
        try:
            df = self.retrieve_earnings()
            if not df.empty:
                order = sort_tickers_by_market_cap(df["symbol"].tolist())
                df = df.set_index("symbol").loc[order].reset_index()
            logger.info(f"Retrieved {len(df)} tickers for earnings announcements")

            thread_id = post_twitter(self.format_earnings_message(df))
            if df.empty:
                return

            csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "top_3000_tickers.csv")
            df_data = pd.read_csv(csv_path) if os.path.exists(csv_path) else None

            for _, row in df.head(self.number_tickers_to_print).iterrows():
                ticker = row["symbol"]
                performance = self.calculate_performance_score(ticker)
                if performance is None:
                    continue
                message = format_company_message(ticker, performance, self.company_info(ticker, row, df_data),
                                                 self.when_word)
                # Reply to the previous tweet so everything reads as one thread
                new_id = post_twitter(message, reply_to=thread_id if thread_id != "dry-run" else None,
                                      add_grok=False)
                thread_id = new_id or thread_id
                time.sleep(0 if os.getenv("TWEET_DRY_RUN") == "1" else 20)

            logger.info("Completed EarningsBot workflow successfully")
        except Exception as e:
            logger.error(f"Error in main workflow: {e}")


if __name__ == "__main__":
    # Usage: python -m weekdays.Earnings [YYYY-MM-DD]   (set TWEET_DRY_RUN=1 to preview for free)
    EarningsBot(target_date=sys.argv[1] if len(sys.argv) > 1 else None).run()
