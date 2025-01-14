# Stock Market Twitter Bot

## Author
**Created by:** Pablo Calatayud  
**Email:** pablocalatayudpelayo@gmail.com  
**LinkedIn:** [Pablo Calatayud Pelayo](https://www.linkedin.com/in/pablo-calatayud-pelayo/)  
**Copyright:** © 2025, Pablo Calatayud. All rights reserved.

## Project Description
This project is an automated Twitter bot that provides stock market updates, including earnings reports, dividends, splits, and market performance metrics. The bot operates during market hours and provides specialized reports during weekends.

## Features
- Real-time market status monitoring
- Automated posts for:
  - Market opening and closing
  - Earnings announcements
  - Dividend payments
  - Stock splits
  - Market performance metrics
- Weekend analysis reports for:
  - Overall market performance
  - US stocks analysis
  - Magnificent Seven stocks performance
  - Sector-wise performance

## Project Structure
```
project/
├── weekdays/
│   ├── Dividends.py
│   ├── Earnings.py
│   ├── Splits.py
│   └── Open_Market_Performance.py
├── utils/
│   └── utils.py
├── config/
│   ├── api_keys.py
│   └── telegram.py
└── logs/
    └── main.log
```

## Schedule
### Weekday Operations
- **Morning Update (8:00)**: Earnings, Dividends, and Splits reports
- **Market Open (15:30)**: Opening market status
- **Mid-Day (18:30)**: Market performance update
- **Market Close (21:00)**: Closing summary and weekly review

### Weekend Operations
#### Saturday
- **08:00**: Market Performance Tracking
- **17:00**: US Stocks Analysis

#### Sunday
- **08:00**: Magnificent Seven Performance Analysis
- **17:00**: Sector Performance Analysis

## Setup
1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API keys in `config/api_keys.py`:
```python
api_key = "your_financial_modeling_prep_api_key"
```

3. Configure Telegram settings in `config/telegram.py`:
```python
bot_token = "your_telegram_bot_token"
bot_chatID = "your_telegram_chat_id"
```

## Usage
Run the main script to start the bot:
```bash
python main.py
```

## Dependencies
- `requests`
- `loguru`
- `pandas`
- `numpy`
- `yfinance`
- `datetime`

## API Requirements
- Financial Modeling Prep API key
- Twitter API credentials
- Telegram Bot credentials

## Error Handling
The system includes comprehensive error handling and logging:
- API connection errors
- Market status verification
- Data processing errors
- Message posting failures

## Logs
Logs are stored in `logs/main.log` with a 500 MB rotation policy.

## Future Enhancements
- Additional market indicators
- More granular performance metrics
- Enhanced error reporting
- Extended weekend analysis features

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is protected under copyright © 2025, Pablo Calatayud. All rights reserved.

---
*Note: Make sure to comply with all API usage terms and conditions when deploying this bot.*
