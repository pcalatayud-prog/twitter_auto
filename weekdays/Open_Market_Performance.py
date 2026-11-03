# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf
from loguru import logger

from utils.utils import post_twitter, getting_nasdaq100_sp500_tickers, fit_tweet

NY = ZoneInfo("America/New_York")
INDICES = {"^GSPC": "S&P 500", "^IXIC": "Nasdaq", "^DJI": "Dow"}
VIX = "^VIX"
GREEN, RED = "🟢", "🔴"


def pct(value: float) -> str:
    return f"{value:+.1f}%"


def arrow(value: float) -> str:
    return GREEN if value >= 0 else RED


class Market_Daily_Performance:
    """Intraday / close market updates for S&P 500 + Nasdaq-100 constituents."""

    def __init__(self, tickers=None):
        logger.add("logs/open_market_performance.log", rotation="500 MB")
        logger.info("Initialising Open Market Performance")
        self.tickers = tickers or getting_nasdaq100_sp500_tickers()
        self.closes = None  # DataFrame: dates x symbols (stocks + indices)

    # ------------------------------------------------------------------ data
    def getting_tickers_data(self):
        """Download ~1 year of daily closes for every ticker in ONE batched request."""
        yf_symbols = {t.replace(".", "-"): t for t in self.tickers}  # BRK.B -> BRK-B for Yahoo
        symbols = list(yf_symbols) + list(INDICES) + [VIX]
        data = yf.download(symbols, period="1y", auto_adjust=True, progress=False, threads=True)
        closes = data["Close"].rename(columns=yf_symbols)
        self.closes = closes.dropna(how="all")
        logger.info(f"Downloaded closes for {closes.shape[1]} symbols, last bar {self.closes.index[-1].date()}")

    def _returns(self, periods: int = 1) -> pd.Series:
        """% change over the last `periods` trading days, stocks only."""
        if self.closes is None:
            self.getting_tickers_data()
        stocks = self.closes.drop(columns=list(INDICES) + [VIX], errors="ignore")
        valid = stocks.ffill()
        ret = (valid.iloc[-1] / valid.iloc[-1 - periods] - 1) * 100
        return ret.dropna()

    def _index_line(self) -> str:
        parts = []
        for symbol, name in INDICES.items():
            col = self.closes[symbol].dropna()
            if len(col) >= 2:
                parts.append(f"{name} {pct((col.iloc[-1] / col.iloc[-2] - 1) * 100)}")
        return " · ".join(parts)

    def _vix_text(self) -> str:
        col = self.closes[VIX].dropna() if VIX in self.closes else pd.Series(dtype=float)
        if len(col) < 2:
            return ""
        return f"😨 VIX {col.iloc[-1]:.1f} ({pct((col.iloc[-1] / col.iloc[-2] - 1) * 100)})"

    @staticmethod
    def _movers(ret: pd.Series, n: int = 3) -> tuple[str, str]:
        top = ret.nlargest(n)
        bottom = ret.nsmallest(n)
        up = " · ".join(f"${t} {pct(v)}" for t, v in top.items())
        down = " · ".join(f"${t} {pct(v)}" for t, v in bottom.items())
        return up, down

    @staticmethod
    def _breadth(ret: pd.Series) -> str:
        up, down = int((ret > 0).sum()), int((ret < 0).sum())
        return f"📊 Breadth: {up} up / {down} down"

    @staticmethod
    def _today() -> str:
        now = datetime.now(NY)
        return now.strftime("%a, %b ") + str(now.day)

    def _post(self, message: str):
        message = fit_tweet(message)
        logger.info(message)
        post_twitter(message)

    # ---------------------------------------------------------------- tweets
    def market_just_open(self):
        """09:30 ET: indices + biggest opening gaps."""
        ret = self._returns(1)
        up, down = self._movers(ret)
        self._post(
            f"🔔 Opening bell | {self._today()}\n\n"
            f"{self._index_line()}\n\n"
            f"🚀 Gapping up: {up}\n"
            f"🔻 Gapping down: {down}\n\n"
            f"How are you trading today? 👇\n#StockMarket #SP500 #Nasdaq"
        )

    def market_is_open(self):
        """Intraday check (every ~2h): leaders, laggards, breadth."""
        ret = self._returns(1)
        up, down = self._movers(ret)
        now = datetime.now(NY)
        self._post(
            f"⏱️ Market check | {now:%H:%M} ET\n\n"
            f"{self._index_line()}\n\n"
            f"{GREEN} Leaders: {up}\n"
            f"{RED} Laggards: {down}\n\n"
            f"{self._breadth(ret)}\n#StockMarket"
        )

    def market_is_just_closed(self):
        """16:00 ET: full-day recap."""
        ret = self._returns(1)
        up, down = self._movers(ret)
        vix = self._vix_text()
        self._post(
            f"🔔 Closing bell | {self._today()}\n\n"
            f"{self._index_line()}\n"
            + (f"{vix}\n" if vix else "")
            + f"\n🏆 Top gainers: {up}\n"
            f"💥 Top losers: {down}\n\n"
            f"{self._breadth(ret)}\n#StockMarket #SP500 #Nasdaq"
        )

    def market_1_week(self):
        """Friday after the close: week in review."""
        ret = self._returns(5)
        up, down = self._movers(ret)
        idx = []
        for symbol, name in INDICES.items():
            col = self.closes[symbol].dropna()
            if len(col) >= 6:
                idx.append(f"{name} {pct((col.iloc[-1] / col.iloc[-6] - 1) * 100)}")
        self._post(
            f"📅 Last 5 sessions | {self._today()}\n\n"
            f"{' · '.join(idx)}\n\n"
            f"🏆 Best: {up}\n"
            f"💥 Worst: {down}\n\n"
            f"{self._breadth(ret)}\n#StockMarket #WeeklyRecap"
        )

    def market_1_year(self):
        """Trailing 12 months winners/losers."""
        ret = self._returns(len(self.closes) - 1 if self.closes is not None else 250)
        up, down = self._movers(ret)
        self._post(
            f"📆 12-month leaders & laggards | {self._today()}\n\n"
            f"🏆 {up}\n💥 {down}\n\n#StockMarket"
        )


if __name__ == "__main__":
    # Preview for free:  set TWEET_DRY_RUN=1  then  python -m weekdays.Open_Market_Performance
    market = Market_Daily_Performance()
    market.market_just_open()
    market.market_is_open()
    market.market_is_just_closed()
    market.market_1_week()
