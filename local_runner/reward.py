import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def get_bitcoin_price_data(start_date, end_date):
    """
    Fetch Bitcoin price data from Yahoo Finance
    """
    try:
        btc = yf.Ticker("BTC-USD")
        hist = btc.history(start=start_date, end=end_date)
        return hist['Close']
    except Exception as e:
        print(f"Error fetching Bitcoin price data: {e}")
        return None

def get_block_reward_by_date(date):
    """
    Calculate block reward based on halving schedule
    Bitcoin halving dates and rewards:
    - Genesis (2009-01-03) to 2012-11-28: 50 BTC
    - 2012-11-28 to 2016-07-09: 25 BTC
    - 2016-07-09 to 2020-05-11: 12.5 BTC
    - 2020-05-11 to 2024-04-20: 6.25 BTC
    - 2024-04-20 onwards: 3.125 BTC
    """
    halving_dates = [
        (datetime(2009, 1, 3), 50.0),      # Genesis block
        (datetime(2012, 11, 28), 25.0),    # First halving
        (datetime(2016, 7, 9), 12.5),      # Second halving
        (datetime(2020, 5, 11), 6.25),     # Third halving
        (datetime(2024, 4, 20), 3.125),    # Fourth halving
    ]

    # Convert input date to datetime if it's a string
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    elif isinstance(date, pd.Timestamp):
        date = date.to_pydatetime()

    # Remove timezone info if present to avoid comparison issues
    if hasattr(date, 'tz') and date.tz is not None:
        date = date.replace(tzinfo=None)
    elif hasattr(date, 'tzinfo') and date.tzinfo is not None:
        date = date.replace(tzinfo=None)

    # Find the appropriate reward for the given date
    for i in range(len(halving_dates) - 1):
        if halving_dates[i][0] <= date < halving_dates[i + 1][0]:
            return halving_dates[i][1]

    # If date is after the last halving, use the most recent reward
    return halving_dates[-1][1]

def calculate_daily_mining_rewards(start_date, end_date, avg_fees_per_block=0.1):
    """
    Calculate daily mining rewards in USD

    Parameters:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - avg_fees_per_block: Average fees per block in BTC (default 0.1)

    Returns:
    - DataFrame with daily mining rewards
    """

    print("Fetching Bitcoin price data...")
    btc_prices = get_bitcoin_price_data(start_date, end_date)

    if btc_prices is None:
        return None

    print("Calculating mining rewards...")

    # Create results DataFrame
    results = []

    # Average blocks per day (approximately 144 blocks per day)
    avg_blocks_per_day = 144

    for date, price in btc_prices.items():
        # Get block reward for this date
        block_reward_btc = get_block_reward_by_date(date)

        # Calculate total BTC reward per block (block reward + fees)
        total_btc_per_block = block_reward_btc + avg_fees_per_block

        # Calculate daily BTC rewards (assuming 144 blocks per day)
        daily_btc_reward = total_btc_per_block * avg_blocks_per_day

        # Calculate daily USD rewards
        daily_usd_reward = daily_btc_reward * price

        results.append({
            'Date': date.strftime('%Y-%m-%d'),
            'BTC_Price_USD': round(price, 2),
            'Block_Reward_BTC': block_reward_btc,
            'Fees_Per_Block_BTC': avg_fees_per_block,
            'Total_BTC_Per_Block': total_btc_per_block,
            'Blocks_Per_Day': avg_blocks_per_day,
            'Daily_BTC_Reward': round(daily_btc_reward, 4),
            'Daily_USD_Reward': round(daily_usd_reward, 2)
        })

    return pd.DataFrame(results)

def main():
    # Example usage
    start_date = "2020-01-01"  # You can change this date
    end_date = "2024-12-31"    # You can change this date

    print(f"Calculating Bitcoin mining rewards from {start_date} to {end_date}")
    print("=" * 60)

    # Calculate mining rewards
    df = calculate_daily_mining_rewards(start_date, end_date)

    if df is not None:
        print(f"\nFirst 10 days:")
        print(df.head(10).to_string(index=False))

        print(f"\nLast 10 days:")
        print(df.tail(10).to_string(index=False))

        print(f"\nSummary Statistics:")
        print(f"Total days analyzed: {len(df)}")
        print(f"Average daily USD reward: ${df['Daily_USD_Reward'].mean():,.2f}")
        print(f"Maximum daily USD reward: ${df['Daily_USD_Reward'].max():,.2f}")
        print(f"Minimum daily USD reward: ${df['Daily_USD_Reward'].min():,.2f}")

        # Save to CSV
        output_file = "bitcoin_mining_rewards.csv"
        df.to_csv(output_file, index=False)
        print(f"\nResults saved to {output_file}")

        return df
    else:
        print("Failed to calculate mining rewards")
        return None

if __name__ == "__main__":
    # Install required packages if not already installed
    # pip install yfinance pandas numpy

    df = main()

    # Optional: Create a simple plot
    try:
        import matplotlib.pyplot as plt

        if df is not None:
            plt.figure(figsize=(12, 8))

            # Convert Date column to datetime for plotting
            df['Date'] = pd.to_datetime(df['Date'])

            # Calculate USD reward per block (Total_BTC_Per_Block * BTC_Price_USD)
            df['USD_Reward_Per_Block'] = df['Total_BTC_Per_Block'] * df['BTC_Price_USD']

            # Plot average reward per block in USD (in thousands)
            plt.subplot(2, 1, 1)
            plt.plot(df['Date'], df['USD_Reward_Per_Block'] / 1000, linewidth=1)
            plt.title('Average Bitcoin Mining Reward Per Block (USD)')
            plt.ylabel('USD Reward per Block (Thousands)')
            plt.grid(True, alpha=0.3)

            # Plot Bitcoin price
            plt.subplot(2, 1, 2)
            plt.plot(df['Date'], df['BTC_Price_USD'], linewidth=1, color='orange')
            plt.title('Bitcoin Price (USD)')
            plt.ylabel('Price (USD)')
            plt.xlabel('Date')
            plt.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.show()

    except ImportError:
        print("\nNote: Install matplotlib to see plots: pip install matplotlib")

# Function to get mining rewards for a single day
def get_single_day_reward(date_str, avg_fees_per_block=0.1):
    """
    Get mining reward for a single specific day

    Parameters:
    - date_str: Date in YYYY-MM-DD format
    - avg_fees_per_block: Average fees per block in BTC

    Returns:
    - Dictionary with mining reward information
    """
    try:
        # Get Bitcoin price for that day
        btc = yf.Ticker("BTC-USD")
        date = datetime.strptime(date_str, '%Y-%m-%d')
        end_date = date + timedelta(days=1)

        hist = btc.history(start=date_str, end=end_date.strftime('%Y-%m-%d'))

        if len(hist) == 0:
            print(f"No price data available for {date_str}")
            return None

        price = hist['Close'].iloc[0]

        # Get block reward
        block_reward_btc = get_block_reward_by_date(date)
        total_btc_per_block = block_reward_btc + avg_fees_per_block
        daily_btc_reward = total_btc_per_block * 144  # 144 blocks per day
        daily_usd_reward = daily_btc_reward * price

        return {
            'Date': date_str,
            'BTC_Price_USD': round(price, 2),
            'Block_Reward_BTC': block_reward_btc,
            'Total_BTC_Per_Block': total_btc_per_block,
            'Daily_BTC_Reward': round(daily_btc_reward, 4),
            'Daily_USD_Reward': round(daily_usd_reward, 2)
        }

    except Exception as e:
        print(f"Error getting reward for {date_str}: {e}")
        return None

# Example: Get reward for today
# today_reward = get_single_day_reward("2024-12-01")
# if today_reward:
#     print(f"Mining reward for {today_reward['Date']}: ${today_reward['Daily_USD_Reward']:,}")