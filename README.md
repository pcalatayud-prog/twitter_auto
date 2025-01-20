# Stock Market Twitter Bot

## Twitter account where all is published: https://x.com/AI_Investor_py

## Author
**Created by:** Pablo Calatayud  
**Email:** pablocalatayudpelayo@gmail.com  
**LinkedIn:** [Pablo Calatayud Pelayo](https://www.linkedin.com/in/pablo-calatayud-pelayo/)  
**Copyright:** Take what is useful, discard what is not, mentioning it is up to you, but it would be appreciated.

## Project Description
This project is an automated Twitter bot that provides stock market updates, including earnings reports, dividends, splits, and market performance metrics. 
As well, errors in production are flagged through a Telegram bot.

## Project Structure
```
twitter_auto/
├── main.py                 # Main execution script
├── requirements.txt        # Project dependencies
├── run.bat                # Batch file for execution
│
├── config/                # Configuration files
│   ├── api_keys.py        # API keys and credentials
│   ├── auth.py           # Authentication settings
│   ├── telegram.py       # Telegram bot configuration
│   └── top_3000_tickers.csv  # Stock tickers data
│
├── utils/
│   └── utils.py          # Utility functions
│
├── weekdays/             # Weekday operations
│   ├── Dividends.py      # Dividend announcements
│   ├── Earnings.py       # Earnings reports
│   ├── Open_Market_Performance.py  # Market performance tracking
│   ├── Splits.py         # Stock splits tracking
│   └── logs/             # Weekday-specific logs
│
├── weekends/             # Weekend analysis scripts
│   ├── performance_Automatization_US_ALL.py
│   ├── Performance_Mag_7.py
│   ├── Performance_Markets.py
│   └── Performance_Sector.py
│
├── logs/                 # Application logs
│   └── main.log
│
└── miscelaneous/         # Additional analysis scripts
    └── Analyzing_Interesting_Company.py
```

## Analytics
![1 year Analitis.](https://github.com/pcalatayud-prog/twitter_auto/blob/main/AI_Investor_py.PNG)

## Features
### Weekday Operations
- Market status monitoring
- Earnings announcements
- Dividend payment tracking
- Stock splits reporting
- Market performance metrics

### Weekend Analysis
- Overall market performance tracking
- US stocks comprehensive analysis
- Magnificent Seven stocks performance
- Sector-wise performance analysis

## Setup and Installation
1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the necessary files in `config/`:
   - `api_keys.py`: API credentials
   - `auth.py`: Authentication settings for twitter
   - `telegram.py`: Telegram bot configuration

## Configuration Files
### Required Configurations
1. `config/api_keys.py`:
```python
api_key = "your_financial_modeling_prep_api_key"
```

2. `config/telegram.py`:
```python
bot_token = "your_telegram_bot_token"
bot_chatID = "your_telegram_chat_id"
```

3. `config/auth.py`:
```python
api_key = ""
api_key_secret = ""
access_token = ""
access_token_secret = ""
bearer = ""
```

## Execution
Run the bot using either:
```bash
python main.py
```
or
```bash
run.bat
```

## Schedule
### Weekday Operations (`weekdays/`)
- **Morning Update (8:00)**: Earnings, Dividends, and Splits reports
- **Market Open (15:30)**: Opening status
- **Mid-Day (18:30)**: Performance update
- **Market Close (21:00)**: Closing summary

### Weekend Operations (`weekends/`)
#### Saturday
- **08:00**: Markets Performance Analysis
- **17:00**: US Stocks Analysis

#### Sunday
- **08:00**: Magnificent Seven Analysis
- **17:00**: Sector Performance Analysis

## Dependencies
See `requirements.txt` for full list of dependencies. Key packages include:
- requests
- loguru
- pandas
- numpy
- yfinance

## Logging
- Main application logs: `logs/main.log`
- Weekday-specific logs: `weekdays/logs/`
- Log rotation: 500 MB

## Contributing
Please contact the author for contribution guidelines.

## License
[Take what is useful, discard what is not, mentioning it is up to you, but it would be appreciated.](https://opensource.org/license/MIT)

---
*Note: Ensure all API credentials are properly configured before running the bot.*
