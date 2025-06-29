# utils/utils_async.py

import yfinance as yf
import asyncio
import numpy as np
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def get_market_cap(ticker):
    """Synchronous market cap fetcher using yfinance"""
    try:
        return yf.Ticker(ticker).info.get('marketCap')
    except Exception as e:
        logger.error(f'Error fetching {ticker}: {e}')
        return None


async def get_market_cap_async(ticker):
    """Async wrapper for market cap fetching"""
    return await asyncio.to_thread(get_market_cap, ticker)


async def process_single_ticker(semaphore: asyncio.Semaphore, ticker: str, index: int, total: int):
    """Process single ticker with concurrency control and rate limiting"""
    async with semaphore:
        try:
            # Add small delay to avoid rate limiting
            await asyncio.sleep(0.1)  # 100ms delay between requests

            market_cap = await get_market_cap_async(ticker)

            # Progress logging every 100 items
            if (index + 1) % 100 == 0:
                logger.info(f'Processed: {index + 1} out of {total} ({((index + 1) / total) * 100:.1f}%)')

            return index, ticker, market_cap

        except Exception as e:
            logger.error(f'Error downloading {ticker}. Ticker {index + 1} out of {total}. \nError: {e}')
            return index, ticker, np.nan


async def fetch_all_market_caps(tickers: List[str], max_concurrent: int = 3) -> List:
    """
    Fetch all market caps concurrently using yfinance with rate limiting

    This is the function you're calling from your main code:
    marketcap_all = asyncio.run(fetch_all_market_caps(filtered_tickers))

    Args:
        tickers: List of ticker symbols
        max_concurrent: Maximum number of concurrent requests (3-5 recommended to avoid rate limits)

    Returns:
        List of market caps in same order as input tickers
    """
    total = len(tickers)
    logger.info(f'Starting to fetch market caps for {total} tickers with max {max_concurrent} concurrent requests...')
    logger.info(f'Using rate limiting to avoid yfinance "Too Many Requests" errors')

    # Create semaphore to limit concurrent requests (much lower for yfinance)
    semaphore = asyncio.Semaphore(max_concurrent)

    # Create tasks for ALL tickers at once - this enables true concurrency
    tasks = [
        process_single_ticker(semaphore, ticker, i, total)
        for i, ticker in enumerate(tickers)
    ]

    # Execute ALL tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Sort results back to original order and handle errors
    marketcap_all = [None] * total
    success_count = 0
    error_count = 0

    for result in results:
        if isinstance(result, Exception):
            logger.error(f'Task failed with exception: {result}')
            error_count += 1
            continue

        index, ticker, market_cap = result

        if market_cap is not None and not (isinstance(market_cap, float) and np.isnan(market_cap)):
            marketcap_all[index] = market_cap
            success_count += 1
        else:
            marketcap_all[index] = np.nan
            error_count += 1

    logger.info(
        f'Fetch completed! Success: {success_count}, Errors: {error_count}, Success rate: {(success_count / total) * 100:.1f}%')
    return marketcap_all


# Alternative functions with different rate limiting strategies
async def fetch_all_market_caps_conservative(tickers: List[str]) -> List:
    """Very conservative version - slowest but most reliable"""
    return await fetch_all_market_caps(tickers, max_concurrent=1)


async def fetch_all_market_caps_balanced(tickers: List[str]) -> List:
    """Balanced version - good speed vs reliability (recommended)"""
    return await fetch_all_market_caps(tickers, max_concurrent=3)


async def fetch_all_market_caps_with_retry(tickers: List[str], max_concurrent: int = 3, max_retries: int = 3) -> List:
    """
    Version with retry logic for failed requests
    Recommended for large ticker lists
    """
    total = len(tickers)
    logger.info(f'Starting to fetch market caps for {total} tickers with retry logic...')

    # First attempt
    results = await fetch_all_market_caps(tickers, max_concurrent)

    # Find failed tickers (None or NaN values)
    failed_indices = []
    failed_tickers = []

    for i, result in enumerate(results):
        if result is None or (isinstance(result, float) and np.isnan(result)):
            failed_indices.append(i)
            failed_tickers.append(tickers[i])

    # Retry failed tickers with even more conservative settings
    if failed_tickers and max_retries > 0:
        logger.info(f'Retrying {len(failed_tickers)} failed tickers with more conservative settings...')

        # Wait a bit before retry
        await asyncio.sleep(2)

        # Retry with max_concurrent=1 and longer delays
        retry_results = await fetch_all_market_caps_conservative(failed_tickers)

        # Update original results with retry results
        for i, retry_result in enumerate(retry_results):
            original_index = failed_indices[i]
            if retry_result is not None and not (isinstance(retry_result, float) and np.isnan(retry_result)):
                results[original_index] = retry_result

    return results