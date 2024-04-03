#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests
import numpy as np
import yfinance as yf
# # Replace 'your_file.csv' with the actual path to your .csv file
# file_path = 'ticker_info.csv'

# # Read the .csv file into a pandas DataFrame
# df = pd.read_csv(file_path, index_col=0)

# columns = list(df.keys())

# columns.append("marketCap")

# df_to_fill = pd.DataFrame(columns = columns)
# df_to_fill


# In[2]:


import time

start_time = time.time()


# In[3]:


import requests

# API endpoint
url = "https://financialmodelingprep.com/api/v3/stock/list"

# API key (replace with your own)
api_key = "c8cda59957e87eead4f323aab454cefa"

# Parameters
params = {
    "apikey": api_key
}

# Send GET request
response = requests.get(url, params=params)

# Check if request was successful
if response.status_code == 200:
    # Extract tickers from response JSON
    data = response.json()

tickers = pd.DataFrame(data)

tickers = tickers[tickers["exchangeShortName"].isin(['NYSE', 'NASDAQ'])]


# In[4]:


tickers = tickers[tickers["type"]=="stock"]
tickers


# In[5]:


tickers = tickers[tickers["price"]>5]
tickers


# In[6]:


tickers = tickers[~tickers['symbol'].str.contains(r'[-.]')]
tickers


# In[7]:


tickers = tickers[tickers['symbol'].str.len() <= 4]
tickers


# In[8]:


filtered_tickers = tickers["symbol"].tolist()
print(len(filtered_tickers))
filtered_tickers


# In[ ]:





# In[9]:


import yfinance as yf
marketcap_all = []
for ticker in filtered_tickers:

    try:

        # Fetch the data for the ticker
        ticker_data = yf.Ticker(ticker)
        
        # Get the market capitalization
        market_cap = ticker_data.info['marketCap']
    
        marketcap_all.append(market_cap)

    except:
        
        marketcap_all.append(np.nan)


# In[10]:


tickers["marketCap"] = marketcap_all
tickers


# In[11]:


billion = 1000000000


# In[12]:


tickers['marketCap'] = pd.to_numeric(tickers['marketCap'], errors='coerce')

# Remove rows with NaN values in the 'marketCap' column
tickers.dropna(inplace=True)

tickers


# In[13]:


tickers = tickers[tickers["marketCap"]>billion]


# In[14]:


tickers


# In[ ]:





# In[15]:


from auth import api_key
from auth import api_key_secret
from auth import access_token
from auth import access_token_secret
from auth import bearer


# In[16]:


import tweepy
import json
import pandas as pd
import numpy as np
import pandas as pd


# In[17]:


def post(text: str):

    from auth import api_key
    from auth import api_key_secret
    from auth import access_token
    from auth import access_token_secret
    from auth import bearer
    
    # Authenticate to Twitter
    client = tweepy.Client(
        bearer_token = bearer,
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    # Post Tweet
    message = text
    client.create_tweet(text=message)
    
    return None


# In[18]:


df = tickers.copy()


# In[19]:


import warnings
warnings.filterwarnings('ignore')


# In[20]:


tickers = list(df["symbol"])


# In[21]:


import datetime

# Get the current date
current_date = datetime.datetime.now()

# Extract year, month, and week of the year
current_year = current_date.year
current_month = current_date.month
current_week = int(current_date.strftime("%U"))  # %U gives the week number (0-53), where the week starts on Sunday

# Print the results
print("Current Year:", current_year)
print("Current Month:", current_month)
print("Current Week of the Year:", current_week)


# In[22]:


lista_hastaghs = ["\n#Stocks",' #Nasdaq',' #Investor',' #Stockmarket', ' #trader']


# In[ ]:





# In[23]:


df_performance = pd.DataFrame(columns = ["ticker","ytd","hf","3mtd","mtd","wtd","dtd"])

import yfinance as yf
from datetime import datetime, timedelta

for ticker in tickers:
    try:
            
        year = "2024"
    
        # Define the start date for the analysis
        start_date_1y = datetime.now() - timedelta(days=365)  # YTD
        start_date_half = datetime.now() - timedelta(days=int(365/2))  # YTD
        start_date_3month = datetime.now() - timedelta(days=90)  
        start_date_month = datetime.now() - timedelta(days=30)  # MTD
        start_date_week = datetime.now() - timedelta(days=7)  # WTD
        
        #print("1 year ago:", start_date_1y)
        #print("3 months ago:", start_date_3month)
        #print("1 month ago:", start_date_month)
        #print("1 wekek ago:", start_date_week)
    
        # Download historical stock data from Yahoo Finance
        stock_data = yf.download(ticker, start=start_date_1y, end=datetime.now(), progress=False)
        stock_data['day-of-week'] = stock_data.index.dayofweek
        stock_data['week-of-year'] = stock_data.index.isocalendar().week
        stock_data['month-of-year'] = stock_data.index.month
        stock_data['year'] = stock_data.index.year
        
        try:
            # YEAR TO DAY
            stock_data_1YTD = stock_data.copy()
            stock_data_1YTD = stock_data_1YTD[stock_data_1YTD.index>=start_date_1y]
            price_open = stock_data_1YTD["Close"].iloc[0]
            price_close = stock_data_1YTD["Close"].iloc[-1]
            return_ytd = round(100*(price_close-price_open)/price_open,2)
            #print("Year To Day Return",return_ytd)
        except:
            return_ytd = np.nan
    
        try:
            # Half YEAR TO DAY
            stock_data_HF = stock_data.copy()
            stock_data_HF = stock_data_HF[stock_data_HF.index>=start_date_half]
            price_open = stock_data_HF["Close"].iloc[0]
            price_close = stock_data_HF["Close"].iloc[-1]
            return_hf = round(100*(price_close-price_open)/price_open,2)
            #print("Year To Day Return",return_ytd)
        except:
            return_hf = np.nan
    
        
    
        try:
            # 3 MONTH TO DAY
            stock_data_3M = stock_data.copy()
            stock_data_3M = stock_data_3M[stock_data_3M.index>=start_date_3month]
            price_open = stock_data_3M["Close"].iloc[0]
            price_close = stock_data_3M["Close"].iloc[-1]
            return_3mtd = round(100*(price_close-price_open)/price_open,2)
            #print("Year To Day Return",return_ytd)
        except:
            return_3mtd = np.nan          
            
            
        try:
            # MONTH TO DAY
            stock_data_MTD = stock_data.copy()
            stock_data_MTD = stock_data_MTD[stock_data_MTD.index>=start_date_month]
            price_open = stock_data_MTD["Close"].iloc[0]
            price_close = stock_data_MTD["Close"].iloc[-1]
            return_mtd = round(100*(price_close-price_open)/price_open,2)
            #print("Month To Day Return",return_mtd)
        except:
            return_mtd = np.nan
        
        try:
            # WEEK TO DAY
            stock_data_WTD = stock_data.copy()
            stock_data_WTD = stock_data_WTD[stock_data_WTD.index>=start_date_week]
            price_open = stock_data_WTD["Close"].iloc[0]
            price_close = stock_data_WTD["Close"].iloc[-1]
            return_wtd = round(100*(price_close-price_open)/price_open,2)
            #print("Month To Day Return",return_wtd)
        except:
            return_wtd = np.nan
    
        try:
            # DAY TO DAY
            stock_data_DTD = stock_data.tail(2)
            stock_data_DTD["returns"] = round(100 * stock_data_DTD["Close"].pct_change(),2)
            return_dtd = stock_data_DTD["returns"].iloc[-1]
            #print("Day To Day Return",return_dtd)
        except:
            return_dtd = np.nan
    
        row = [ticker,return_ytd,return_hf,return_3mtd,return_mtd,return_wtd,return_dtd]

        df_performance.loc[len(df_performance)] = row
    
    except:
        
        pass


# In[ ]:





# In[24]:


df_performance


# In[25]:


df_performance.dropna(inplace=True)


# In[26]:


df_performance


# In[27]:


df["ticker"] = df["symbol"]


# In[28]:


merged_df = pd.merge(df, df_performance, on='ticker')
merged_df


# In[29]:


merged_df = merged_df.rename(columns={'name': 'Company'})


# In[30]:


merged_df


# In[ ]:





# ## Best Today

# In[31]:


merged_df


# In[32]:


def performance_today(merged_df):

    import pandas as pd
    # Assuming df_performance is your DataFrame
    # Sort the DataFrame based on the 'gap' column in ascending order
    df_performance_sorted_1y = merged_df.sort_values(by='dtd')
    
    top_1_ticker = df_performance_sorted_1y["ticker"].iloc[-1]
    top_1_company = df_performance_sorted_1y["Company"].iloc[-1]
    top_1_perc = df_performance_sorted_1y["dtd"].iloc[-1]
    
    top_2_ticker = df_performance_sorted_1y["ticker"].iloc[-2]
    top_2_company = df_performance_sorted_1y["Company"].iloc[-2]
    top_2_perc = df_performance_sorted_1y["dtd"].iloc[-2]
    
    top_3_ticker = df_performance_sorted_1y["ticker"].iloc[-3]
    top_3_company = df_performance_sorted_1y["Company"].iloc[-3]
    top_3_perc = df_performance_sorted_1y["dtd"].iloc[-3]
    
    top_4_ticker = df_performance_sorted_1y["ticker"].iloc[-4]
    top_4_company = df_performance_sorted_1y["Company"].iloc[-4]
    top_4_perc = df_performance_sorted_1y["dtd"].iloc[-4]
    
    top_5_ticker = df_performance_sorted_1y["ticker"].iloc[-5]
    top_5_company = df_performance_sorted_1y["Company"].iloc[-5]
    top_5_perc = df_performance_sorted_1y["dtd"].iloc[-5]
    
    top_6_ticker = df_performance_sorted_1y["ticker"].iloc[-6]
    top_6_company = df_performance_sorted_1y["Company"].iloc[-6]
    top_6_perc = df_performance_sorted_1y["dtd"].iloc[-6]
    
    top_7_ticker = df_performance_sorted_1y["ticker"].iloc[-7]
    top_7_company = df_performance_sorted_1y["Company"].iloc[-7]
    top_7_perc = df_performance_sorted_1y["dtd"].iloc[-7]
    
    top_8_ticker = df_performance_sorted_1y["ticker"].iloc[-8]
    top_8_company = df_performance_sorted_1y["Company"].iloc[-8]
    top_8_perc = df_performance_sorted_1y["dtd"].iloc[-8]
    
    top_9_ticker = df_performance_sorted_1y["ticker"].iloc[-9]
    top_9_company = df_performance_sorted_1y["Company"].iloc[-9]
    top_9_perc = df_performance_sorted_1y["dtd"].iloc[-9]
    
    top_10_ticker = df_performance_sorted_1y["ticker"].iloc[-10]
    top_10_company = df_performance_sorted_1y["Company"].iloc[-10]
    top_10_perc = df_performance_sorted_1y["dtd"].iloc[-10]
    
    best_1y = f"#US Companies over $1B  1-Day:\n\nTop-10\n" 
    best_1y = best_1y + f"1. ${top_1_ticker} -> +{top_1_perc} %\n"
    best_1y = best_1y + f"2. ${top_2_ticker} -> +{top_2_perc} %\n"
    best_1y = best_1y + f"3. ${top_3_ticker} -> +{top_3_perc} %\n"
    best_1y = best_1y + f"4. ${top_4_ticker} -> +{top_4_perc} %\n"
    best_1y = best_1y + f"5. ${top_5_ticker} -> +{top_5_perc} %\n"
    best_1y = best_1y + f"6. ${top_6_ticker} -> +{top_6_perc} %\n"
    best_1y = best_1y + f"7. ${top_7_ticker} -> +{top_7_perc} %\n"
    best_1y = best_1y + f"8. ${top_8_ticker} -> +{top_8_perc} %\n"
    best_1y = best_1y + f"9. ${top_9_ticker} -> +{top_9_perc} %\n"
    best_1y = best_1y + f"10. ${top_10_ticker} -> +{top_10_perc} %\n"
    
    message_1d_hastahs = best_1y
    
    for element in lista_hastaghs:
        
        new_word_distance = len(element) + 1 
        
        message_1d_hastahs_distance = len(message_1d_hastahs)
        
        if new_word_distance+message_1d_hastahs_distance<=280:
            
            message_1d_hastahs = message_1d_hastahs+element
            
    #print(len(message_1d_hastahs))
    #print()
    #print(message_1d_hastahs)
    
    best_1y = message_1d_hastahs
    
    print(best_1y)
    
    print(len(best_1y))
    
    try:
        post(best_1y)
    except:
        print("ERROR TODAY 10-TOP")
        print(len(best_1y))
        print("ALREADY POSTED ?? ")
    time.sleep(30)
    top_1_ticker = df_performance_sorted_1y["ticker"].iloc[0]
    top_1_company = df_performance_sorted_1y["Company"].iloc[0]
    top_1_perc = df_performance_sorted_1y["dtd"].iloc[0]
    
    top_2_ticker = df_performance_sorted_1y["ticker"].iloc[1]
    top_2_company = df_performance_sorted_1y["Company"].iloc[1]
    top_2_perc = df_performance_sorted_1y["dtd"].iloc[1]
    
    top_3_ticker = df_performance_sorted_1y["ticker"].iloc[2]
    top_3_company = df_performance_sorted_1y["Company"].iloc[2]
    top_3_perc = df_performance_sorted_1y["dtd"].iloc[2]
    
    top_4_ticker = df_performance_sorted_1y["ticker"].iloc[3]
    top_4_company = df_performance_sorted_1y["Company"].iloc[3]
    top_4_perc = df_performance_sorted_1y["dtd"].iloc[3]
    
    top_5_ticker = df_performance_sorted_1y["ticker"].iloc[4]
    top_5_company = df_performance_sorted_1y["Company"].iloc[4]
    top_5_perc = df_performance_sorted_1y["dtd"].iloc[4]
    
    top_6_ticker = df_performance_sorted_1y["ticker"].iloc[5]
    top_6_company = df_performance_sorted_1y["Company"].iloc[5]
    top_6_perc = df_performance_sorted_1y["dtd"].iloc[5]
    
    top_7_ticker = df_performance_sorted_1y["ticker"].iloc[6]
    top_7_company = df_performance_sorted_1y["Company"].iloc[6]
    top_7_perc = df_performance_sorted_1y["dtd"].iloc[6]
    
    top_8_ticker = df_performance_sorted_1y["ticker"].iloc[7]
    top_8_company = df_performance_sorted_1y["Company"].iloc[7]
    top_8_perc = df_performance_sorted_1y["dtd"].iloc[7]
    
    top_9_ticker = df_performance_sorted_1y["ticker"].iloc[8]
    top_9_company = df_performance_sorted_1y["Company"].iloc[8]
    top_9_perc = df_performance_sorted_1y["dtd"].iloc[8]
    
    top_10_ticker = df_performance_sorted_1y["ticker"].iloc[9]
    top_10_company = df_performance_sorted_1y["Company"].iloc[9]
    top_10_perc = df_performance_sorted_1y["dtd"].iloc[9]
    
    best_1y = f"#US Companies over $1B 1-Day:\n\nBottom-10\n" 
    best_1y = best_1y + f"1. ${top_1_ticker} -> {top_1_perc} %\n"
    best_1y = best_1y + f"2. ${top_2_ticker} -> {top_2_perc} %\n"
    best_1y = best_1y + f"3. ${top_3_ticker} -> {top_3_perc} %\n"
    best_1y = best_1y + f"4. ${top_4_ticker} -> {top_4_perc} %\n"
    best_1y = best_1y + f"5. ${top_5_ticker} -> {top_5_perc} %\n"
    best_1y = best_1y + f"6. ${top_6_ticker} -> {top_6_perc} %\n"
    best_1y = best_1y + f"7. ${top_7_ticker} -> {top_7_perc} %\n"
    best_1y = best_1y + f"8. ${top_8_ticker} -> {top_8_perc} %\n"
    best_1y = best_1y + f"9. ${top_9_ticker} -> {top_9_perc} %\n"
    best_1y = best_1y + f"10. ${top_10_ticker} -> {top_10_perc} %\n"
    
    message_1d_hastahs = best_1y
    
    for element in lista_hastaghs:
        
        new_word_distance = len(element) + 1 
        
        message_1d_hastahs_distance = len(message_1d_hastahs)
        
        if new_word_distance+message_1d_hastahs_distance<=280:
            
            message_1d_hastahs = message_1d_hastahs+element
            
    #print(len(message_1d_hastahs))
    #print()
    #print(message_1d_hastahs)
    
    best_1y = message_1d_hastahs
    
    print(best_1y)
    
    print(len(best_1y))

    try:
        post(best_1y)
    except:
        print("ERROR TODAY 10-BOTTOM")
        print(len(best_1y))
        print("ALREADY POSTED ?? ")
    
    return None


# ## Best Week

# In[33]:


def performance_week(merged_df):

    import pandas as pd
    # Assuming df_performance is your DataFrame
    # Sort the DataFrame based on the 'gap' column in ascending order
    df_performance_sorted_1y = merged_df.sort_values(by='wtd')
    
    top_1_ticker = df_performance_sorted_1y["ticker"].iloc[-1]
    top_1_company = df_performance_sorted_1y["Company"].iloc[-1]
    top_1_perc = df_performance_sorted_1y["wtd"].iloc[-1]
    
    top_2_ticker = df_performance_sorted_1y["ticker"].iloc[-2]
    top_2_company = df_performance_sorted_1y["Company"].iloc[-2]
    top_2_perc = df_performance_sorted_1y["wtd"].iloc[-2]
    
    top_3_ticker = df_performance_sorted_1y["ticker"].iloc[-3]
    top_3_company = df_performance_sorted_1y["Company"].iloc[-3]
    top_3_perc = df_performance_sorted_1y["wtd"].iloc[-3]
    
    top_4_ticker = df_performance_sorted_1y["ticker"].iloc[-4]
    top_4_company = df_performance_sorted_1y["Company"].iloc[-4]
    top_4_perc = df_performance_sorted_1y["wtd"].iloc[-4]
    
    top_5_ticker = df_performance_sorted_1y["ticker"].iloc[-5]
    top_5_company = df_performance_sorted_1y["Company"].iloc[-5]
    top_5_perc = df_performance_sorted_1y["wtd"].iloc[-5]
    
    top_6_ticker = df_performance_sorted_1y["ticker"].iloc[-6]
    top_6_company = df_performance_sorted_1y["Company"].iloc[-6]
    top_6_perc = df_performance_sorted_1y["wtd"].iloc[-6]
    
    top_7_ticker = df_performance_sorted_1y["ticker"].iloc[-7]
    top_7_company = df_performance_sorted_1y["Company"].iloc[-7]
    top_7_perc = df_performance_sorted_1y["wtd"].iloc[-7]
    
    top_8_ticker = df_performance_sorted_1y["ticker"].iloc[-8]
    top_8_company = df_performance_sorted_1y["Company"].iloc[-8]
    top_8_perc = df_performance_sorted_1y["wtd"].iloc[-8]
    
    top_9_ticker = df_performance_sorted_1y["ticker"].iloc[-9]
    top_9_company = df_performance_sorted_1y["Company"].iloc[-9]
    top_9_perc = df_performance_sorted_1y["wtd"].iloc[-9]
    
    top_10_ticker = df_performance_sorted_1y["ticker"].iloc[-10]
    top_10_company = df_performance_sorted_1y["Company"].iloc[-10]
    top_10_perc = df_performance_sorted_1y["wtd"].iloc[-10]
    
    best_1y = f"#US Companies over $1B 1-Week-To-Day:\n\nTop-10\n" 
    best_1y = best_1y + f"1. ${top_1_ticker} -> +{top_1_perc} %\n"
    best_1y = best_1y + f"2. ${top_2_ticker} -> +{top_2_perc} %\n"
    best_1y = best_1y + f"3. ${top_3_ticker} -> +{top_3_perc} %\n"
    best_1y = best_1y + f"4. ${top_4_ticker} -> +{top_4_perc} %\n"
    best_1y = best_1y + f"5. ${top_5_ticker} -> +{top_5_perc} %\n"
    best_1y = best_1y + f"6. ${top_6_ticker} -> +{top_6_perc} %\n"
    best_1y = best_1y + f"7. ${top_7_ticker} -> +{top_7_perc} %\n"
    best_1y = best_1y + f"8. ${top_8_ticker} -> +{top_8_perc} %\n"
    best_1y = best_1y + f"9. ${top_9_ticker} -> +{top_9_perc} %\n"
    best_1y = best_1y + f"10. ${top_10_ticker} -> +{top_10_perc} %\n"
    
    message_1d_hastahs = best_1y
    
    for element in lista_hastaghs:
        
        new_word_distance = len(element) + 1 
        
        message_1d_hastahs_distance = len(message_1d_hastahs)
        
        if new_word_distance+message_1d_hastahs_distance<=280:
            
            message_1d_hastahs = message_1d_hastahs+element
            
    #print(len(message_1d_hastahs))
    #print()
    #print(message_1d_hastahs)
    
    best_1y = message_1d_hastahs
    
    print(best_1y)
    
    print(len(best_1y))
    
    try:
        post(best_1y)
    except:
        print("ERROR WEEK 10-TOP")
        print(len(best_1y))
        print("ALREADY POSTED ?? ")
    time.sleep(30)
    top_1_ticker = df_performance_sorted_1y["ticker"].iloc[0]
    top_1_company = df_performance_sorted_1y["Company"].iloc[0]
    top_1_perc = df_performance_sorted_1y["wtd"].iloc[0]
    
    top_2_ticker = df_performance_sorted_1y["ticker"].iloc[1]
    top_2_company = df_performance_sorted_1y["Company"].iloc[1]
    top_2_perc = df_performance_sorted_1y["wtd"].iloc[1]
    
    top_3_ticker = df_performance_sorted_1y["ticker"].iloc[2]
    top_3_company = df_performance_sorted_1y["Company"].iloc[2]
    top_3_perc = df_performance_sorted_1y["wtd"].iloc[2]
    
    top_4_ticker = df_performance_sorted_1y["ticker"].iloc[3]
    top_4_company = df_performance_sorted_1y["Company"].iloc[3]
    top_4_perc = df_performance_sorted_1y["wtd"].iloc[3]
    
    top_5_ticker = df_performance_sorted_1y["ticker"].iloc[4]
    top_5_company = df_performance_sorted_1y["Company"].iloc[4]
    top_5_perc = df_performance_sorted_1y["wtd"].iloc[4]
    
    top_6_ticker = df_performance_sorted_1y["ticker"].iloc[5]
    top_6_company = df_performance_sorted_1y["Company"].iloc[5]
    top_6_perc = df_performance_sorted_1y["wtd"].iloc[5]
    
    top_7_ticker = df_performance_sorted_1y["ticker"].iloc[6]
    top_7_company = df_performance_sorted_1y["Company"].iloc[6]
    top_7_perc = df_performance_sorted_1y["wtd"].iloc[6]
    
    top_8_ticker = df_performance_sorted_1y["ticker"].iloc[7]
    top_8_company = df_performance_sorted_1y["Company"].iloc[7]
    top_8_perc = df_performance_sorted_1y["wtd"].iloc[7]
    
    top_9_ticker = df_performance_sorted_1y["ticker"].iloc[8]
    top_9_company = df_performance_sorted_1y["Company"].iloc[8]
    top_9_perc = df_performance_sorted_1y["wtd"].iloc[8]
    
    top_10_ticker = df_performance_sorted_1y["ticker"].iloc[9]
    top_10_company = df_performance_sorted_1y["Company"].iloc[9]
    top_10_perc = df_performance_sorted_1y["wtd"].iloc[9]
    
    best_1y = f"#US Companies over $1B 1-Week-To-Day:\n\nBottom-10\n" 
    best_1y = best_1y + f"1. ${top_1_ticker} -> {top_1_perc} %\n"
    best_1y = best_1y + f"2. ${top_2_ticker} -> {top_2_perc} %\n"
    best_1y = best_1y + f"3. ${top_3_ticker} -> {top_3_perc} %\n"
    best_1y = best_1y + f"4. ${top_4_ticker} -> {top_4_perc} %\n"
    best_1y = best_1y + f"5. ${top_5_ticker} -> {top_5_perc} %\n"
    best_1y = best_1y + f"6. ${top_6_ticker} -> {top_6_perc} %\n"
    best_1y = best_1y + f"7. ${top_7_ticker} -> {top_7_perc} %\n"
    best_1y = best_1y + f"8. ${top_8_ticker} -> {top_8_perc} %\n"
    best_1y = best_1y + f"9. ${top_9_ticker} -> {top_9_perc} %\n"
    best_1y = best_1y + f"10. ${top_10_ticker} -> {top_10_perc} %\n"
    
    message_1d_hastahs = best_1y
    
    for element in lista_hastaghs:
        
        new_word_distance = len(element) + 1 
        
        message_1d_hastahs_distance = len(message_1d_hastahs)
        
        if new_word_distance+message_1d_hastahs_distance<=280:
            
            message_1d_hastahs = message_1d_hastahs+element
            
    #print(len(message_1d_hastahs))
    #print()
    #print(message_1d_hastahs)
    
    best_1y = message_1d_hastahs
    
    print(best_1y)
    
    print(len(best_1y))

    try:
        post(best_1y)
    except:
        print("ERROR WEEK 10-BOTTOM")
        print(len(best_1y))
        print("ALREADY POSTED ?? ")
    
    return None


# ## Best Month

# In[34]:


merged_df.head(3)


# In[35]:


def performance_month(merged_df):

    import pandas as pd
    # Assuming df_performance is your DataFrame
    # Sort the DataFrame based on the 'gap' column in ascending order
    df_performance_sorted_1y = merged_df.sort_values(by='mtd')
    
    top_1_ticker = df_performance_sorted_1y["ticker"].iloc[-1]
    top_1_company = df_performance_sorted_1y["Company"].iloc[-1]
    top_1_perc = df_performance_sorted_1y["mtd"].iloc[-1]
    
    top_2_ticker = df_performance_sorted_1y["ticker"].iloc[-2]
    top_2_company = df_performance_sorted_1y["Company"].iloc[-2]
    top_2_perc = df_performance_sorted_1y["mtd"].iloc[-2]
    
    top_3_ticker = df_performance_sorted_1y["ticker"].iloc[-3]
    top_3_company = df_performance_sorted_1y["Company"].iloc[-3]
    top_3_perc = df_performance_sorted_1y["mtd"].iloc[-3]
    
    top_4_ticker = df_performance_sorted_1y["ticker"].iloc[-4]
    top_4_company = df_performance_sorted_1y["Company"].iloc[-4]
    top_4_perc = df_performance_sorted_1y["mtd"].iloc[-4]
    
    top_5_ticker = df_performance_sorted_1y["ticker"].iloc[-5]
    top_5_company = df_performance_sorted_1y["Company"].iloc[-5]
    top_5_perc = df_performance_sorted_1y["mtd"].iloc[-5]
    
    top_6_ticker = df_performance_sorted_1y["ticker"].iloc[-6]
    top_6_company = df_performance_sorted_1y["Company"].iloc[-6]
    top_6_perc = df_performance_sorted_1y["mtd"].iloc[-6]
    
    top_7_ticker = df_performance_sorted_1y["ticker"].iloc[-7]
    top_7_company = df_performance_sorted_1y["Company"].iloc[-7]
    top_7_perc = df_performance_sorted_1y["mtd"].iloc[-7]
    
    top_8_ticker = df_performance_sorted_1y["ticker"].iloc[-8]
    top_8_company = df_performance_sorted_1y["Company"].iloc[-8]
    top_8_perc = df_performance_sorted_1y["mtd"].iloc[-8]
    
    top_9_ticker = df_performance_sorted_1y["ticker"].iloc[-9]
    top_9_company = df_performance_sorted_1y["Company"].iloc[-9]
    top_9_perc = df_performance_sorted_1y["mtd"].iloc[-9]
    
    top_10_ticker = df_performance_sorted_1y["ticker"].iloc[-10]
    top_10_company = df_performance_sorted_1y["Company"].iloc[-10]
    top_10_perc = df_performance_sorted_1y["mtd"].iloc[-10]
    
    best_1y = f"#US Companies over $1B 1-Month-To-Day:\n\nTop-10\n" 
    best_1y = best_1y + f"1. ${top_1_ticker} -> +{top_1_perc} %\n"
    best_1y = best_1y + f"2. ${top_2_ticker} -> +{top_2_perc} %\n"
    best_1y = best_1y + f"3. ${top_3_ticker} -> +{top_3_perc} %\n"
    best_1y = best_1y + f"4. ${top_4_ticker} -> +{top_4_perc} %\n"
    best_1y = best_1y + f"5. ${top_5_ticker} -> +{top_5_perc} %\n"
    best_1y = best_1y + f"6. ${top_6_ticker} -> +{top_6_perc} %\n"
    best_1y = best_1y + f"7. ${top_7_ticker} -> +{top_7_perc} %\n"
    best_1y = best_1y + f"8. ${top_8_ticker} -> +{top_8_perc} %\n"
    best_1y = best_1y + f"9. ${top_9_ticker} -> +{top_9_perc} %\n"
    best_1y = best_1y + f"10. ${top_10_ticker} -> +{top_10_perc} %\n"
    
    message_1d_hastahs = best_1y
    
    for element in lista_hastaghs:
        
        new_word_distance = len(element) + 1 
        
        message_1d_hastahs_distance = len(message_1d_hastahs)
        
        if new_word_distance+message_1d_hastahs_distance<=280:
            
            message_1d_hastahs = message_1d_hastahs+element
            
    #print(len(message_1d_hastahs))
    #print()
    #print(message_1d_hastahs)
    
    best_1y = message_1d_hastahs
    
    print(best_1y)
    
    print(len(best_1y))
    
    try:
        post(best_1y)
    except:
        print("ERROR MONTH 10-TOP")
        print(len(best_1y))
        print("ALREADY POSTED ?? ")
    time.sleep(30)
    top_1_ticker = df_performance_sorted_1y["ticker"].iloc[0]
    top_1_company = df_performance_sorted_1y["Company"].iloc[0]
    top_1_perc = df_performance_sorted_1y["mtd"].iloc[0]
    
    top_2_ticker = df_performance_sorted_1y["ticker"].iloc[1]
    top_2_company = df_performance_sorted_1y["Company"].iloc[1]
    top_2_perc = df_performance_sorted_1y["mtd"].iloc[1]
    
    top_3_ticker = df_performance_sorted_1y["ticker"].iloc[2]
    top_3_company = df_performance_sorted_1y["Company"].iloc[2]
    top_3_perc = df_performance_sorted_1y["mtd"].iloc[2]
    
    top_4_ticker = df_performance_sorted_1y["ticker"].iloc[3]
    top_4_company = df_performance_sorted_1y["Company"].iloc[3]
    top_4_perc = df_performance_sorted_1y["mtd"].iloc[3]
    
    top_5_ticker = df_performance_sorted_1y["ticker"].iloc[4]
    top_5_company = df_performance_sorted_1y["Company"].iloc[4]
    top_5_perc = df_performance_sorted_1y["mtd"].iloc[4]
    
    top_6_ticker = df_performance_sorted_1y["ticker"].iloc[5]
    top_6_company = df_performance_sorted_1y["Company"].iloc[5]
    top_6_perc = df_performance_sorted_1y["mtd"].iloc[5]
    
    top_7_ticker = df_performance_sorted_1y["ticker"].iloc[6]
    top_7_company = df_performance_sorted_1y["Company"].iloc[6]
    top_7_perc = df_performance_sorted_1y["mtd"].iloc[6]
    
    top_8_ticker = df_performance_sorted_1y["ticker"].iloc[7]
    top_8_company = df_performance_sorted_1y["Company"].iloc[7]
    top_8_perc = df_performance_sorted_1y["mtd"].iloc[7]
    
    top_9_ticker = df_performance_sorted_1y["ticker"].iloc[8]
    top_9_company = df_performance_sorted_1y["Company"].iloc[8]
    top_9_perc = df_performance_sorted_1y["mtd"].iloc[8]
    
    top_10_ticker = df_performance_sorted_1y["ticker"].iloc[9]
    top_10_company = df_performance_sorted_1y["Company"].iloc[9]
    top_10_perc = df_performance_sorted_1y["mtd"].iloc[9]
    
    best_1y = f"#US Companies over $1B 1-Month-To-Day:\n\nBottom-10\n" 
    best_1y = best_1y + f"1. ${top_1_ticker} -> {top_1_perc} %\n"
    best_1y = best_1y + f"2. ${top_2_ticker} -> {top_2_perc} %\n"
    best_1y = best_1y + f"3. ${top_3_ticker} -> {top_3_perc} %\n"
    best_1y = best_1y + f"4. ${top_4_ticker} -> {top_4_perc} %\n"
    best_1y = best_1y + f"5. ${top_5_ticker} -> {top_5_perc} %\n"
    best_1y = best_1y + f"6. ${top_6_ticker} -> {top_6_perc} %\n"
    best_1y = best_1y + f"7. ${top_7_ticker} -> {top_7_perc} %\n"
    best_1y = best_1y + f"8. ${top_8_ticker} -> {top_8_perc} %\n"
    best_1y = best_1y + f"9. ${top_9_ticker} -> {top_9_perc} %\n"
    best_1y = best_1y + f"10. ${top_10_ticker} -> {top_10_perc} %\n"
    
    message_1d_hastahs = best_1y
    
    for element in lista_hastaghs:
        
        new_word_distance = len(element) + 1 
        
        message_1d_hastahs_distance = len(message_1d_hastahs)
        
        if new_word_distance+message_1d_hastahs_distance<=280:
            
            message_1d_hastahs = message_1d_hastahs+element
            
    #print(len(message_1d_hastahs))
    #print()
    #print(message_1d_hastahs)
    
    best_1y = message_1d_hastahs
    
    print(best_1y)
    
    print(len(best_1y))

    try:
        post(best_1y)
    except:
        print("ERROR MONTH 10-BOTTOM")
        print(len(best_1y))
        print("ALREADY POSTED ?? ")
    
    return None


# ## Best 3-Month 

# In[36]:


merged_df.head(3)


# In[37]:


def performance_3month(merged_df):

    import pandas as pd
    # Assuming df_performance is your DataFrame
    # Sort the DataFrame based on the 'gap' column in ascending order
    df_performance_sorted_1y = merged_df.sort_values(by='3mtd')
    
    top_1_ticker = df_performance_sorted_1y["ticker"].iloc[-1]
    top_1_company = df_performance_sorted_1y["Company"].iloc[-1]
    top_1_perc = df_performance_sorted_1y["3mtd"].iloc[-1]
    
    top_2_ticker = df_performance_sorted_1y["ticker"].iloc[-2]
    top_2_company = df_performance_sorted_1y["Company"].iloc[-2]
    top_2_perc = df_performance_sorted_1y["3mtd"].iloc[-2]
    
    top_3_ticker = df_performance_sorted_1y["ticker"].iloc[-3]
    top_3_company = df_performance_sorted_1y["Company"].iloc[-3]
    top_3_perc = df_performance_sorted_1y["3mtd"].iloc[-3]
    
    top_4_ticker = df_performance_sorted_1y["ticker"].iloc[-4]
    top_4_company = df_performance_sorted_1y["Company"].iloc[-4]
    top_4_perc = df_performance_sorted_1y["3mtd"].iloc[-4]
    
    top_5_ticker = df_performance_sorted_1y["ticker"].iloc[-5]
    top_5_company = df_performance_sorted_1y["Company"].iloc[-5]
    top_5_perc = df_performance_sorted_1y["3mtd"].iloc[-5]
    
    top_6_ticker = df_performance_sorted_1y["ticker"].iloc[-6]
    top_6_company = df_performance_sorted_1y["Company"].iloc[-6]
    top_6_perc = df_performance_sorted_1y["3mtd"].iloc[-6]
    
    top_7_ticker = df_performance_sorted_1y["ticker"].iloc[-7]
    top_7_company = df_performance_sorted_1y["Company"].iloc[-7]
    top_7_perc = df_performance_sorted_1y["3mtd"].iloc[-7]
    
    top_8_ticker = df_performance_sorted_1y["ticker"].iloc[-8]
    top_8_company = df_performance_sorted_1y["Company"].iloc[-8]
    top_8_perc = df_performance_sorted_1y["3mtd"].iloc[-8]
    
    top_9_ticker = df_performance_sorted_1y["ticker"].iloc[-9]
    top_9_company = df_performance_sorted_1y["Company"].iloc[-9]
    top_9_perc = df_performance_sorted_1y["3mtd"].iloc[-9]
    
    top_10_ticker = df_performance_sorted_1y["ticker"].iloc[-10]
    top_10_company = df_performance_sorted_1y["Company"].iloc[-10]
    top_10_perc = df_performance_sorted_1y["3mtd"].iloc[-10]
    
    best_1y = f"#US Companies over $1B 3-Months-To-Day:\n\nTop-10\n" 
    best_1y = best_1y + f"1. ${top_1_ticker} -> +{top_1_perc} %\n"
    best_1y = best_1y + f"2. ${top_2_ticker} -> +{top_2_perc} %\n"
    best_1y = best_1y + f"3. ${top_3_ticker} -> +{top_3_perc} %\n"
    best_1y = best_1y + f"4. ${top_4_ticker} -> +{top_4_perc} %\n"
    best_1y = best_1y + f"5. ${top_5_ticker} -> +{top_5_perc} %\n"
    best_1y = best_1y + f"6. ${top_6_ticker} -> +{top_6_perc} %\n"
    best_1y = best_1y + f"7. ${top_7_ticker} -> +{top_7_perc} %\n"
    best_1y = best_1y + f"8. ${top_8_ticker} -> +{top_8_perc} %\n"
    best_1y = best_1y + f"9. ${top_9_ticker} -> +{top_9_perc} %\n"
    best_1y = best_1y + f"10. ${top_10_ticker} -> +{top_10_perc} %\n"
    
    message_1d_hastahs = best_1y
    
    for element in lista_hastaghs:
        
        new_word_distance = len(element) + 1 
        
        message_1d_hastahs_distance = len(message_1d_hastahs)
        
        if new_word_distance+message_1d_hastahs_distance<=280:
            
            message_1d_hastahs = message_1d_hastahs+element
            
    #print(len(message_1d_hastahs))
    #print()
    #print(message_1d_hastahs)
    
    best_1y = message_1d_hastahs
    
    print(best_1y)
    
    print(len(best_1y))
    
    try:
        post(best_1y)
    except:
        print("ERROR 3-month 10-TOP")
        print(len(best_1y))
        print("ALREADY POSTED ?? ")
    time.sleep(30)
    top_1_ticker = df_performance_sorted_1y["ticker"].iloc[0]
    top_1_company = df_performance_sorted_1y["Company"].iloc[0]
    top_1_perc = df_performance_sorted_1y["3mtd"].iloc[0]
    
    top_2_ticker = df_performance_sorted_1y["ticker"].iloc[1]
    top_2_company = df_performance_sorted_1y["Company"].iloc[1]
    top_2_perc = df_performance_sorted_1y["3mtd"].iloc[1]
    
    top_3_ticker = df_performance_sorted_1y["ticker"].iloc[2]
    top_3_company = df_performance_sorted_1y["Company"].iloc[2]
    top_3_perc = df_performance_sorted_1y["3mtd"].iloc[2]
    
    top_4_ticker = df_performance_sorted_1y["ticker"].iloc[3]
    top_4_company = df_performance_sorted_1y["Company"].iloc[3]
    top_4_perc = df_performance_sorted_1y["3mtd"].iloc[3]
    
    top_5_ticker = df_performance_sorted_1y["ticker"].iloc[4]
    top_5_company = df_performance_sorted_1y["Company"].iloc[4]
    top_5_perc = df_performance_sorted_1y["3mtd"].iloc[4]
    
    top_6_ticker = df_performance_sorted_1y["ticker"].iloc[5]
    top_6_company = df_performance_sorted_1y["Company"].iloc[5]
    top_6_perc = df_performance_sorted_1y["3mtd"].iloc[5]
    
    top_7_ticker = df_performance_sorted_1y["ticker"].iloc[6]
    top_7_company = df_performance_sorted_1y["Company"].iloc[6]
    top_7_perc = df_performance_sorted_1y["3mtd"].iloc[6]
    
    top_8_ticker = df_performance_sorted_1y["ticker"].iloc[7]
    top_8_company = df_performance_sorted_1y["Company"].iloc[7]
    top_8_perc = df_performance_sorted_1y["3mtd"].iloc[7]
    
    top_9_ticker = df_performance_sorted_1y["ticker"].iloc[8]
    top_9_company = df_performance_sorted_1y["Company"].iloc[8]
    top_9_perc = df_performance_sorted_1y["3mtd"].iloc[8]
    
    top_10_ticker = df_performance_sorted_1y["ticker"].iloc[9]
    top_10_company = df_performance_sorted_1y["Company"].iloc[9]
    top_10_perc = df_performance_sorted_1y["3mtd"].iloc[9]
    
    best_1y = f"#US Companies over $1B 3-Months-To-Day:\n\nBottom-10\n" 
    best_1y = best_1y + f"1. ${top_1_ticker} -> {top_1_perc} %\n"
    best_1y = best_1y + f"2. ${top_2_ticker} -> {top_2_perc} %\n"
    best_1y = best_1y + f"3. ${top_3_ticker} -> {top_3_perc} %\n"
    best_1y = best_1y + f"4. ${top_4_ticker} -> {top_4_perc} %\n"
    best_1y = best_1y + f"5. ${top_5_ticker} -> {top_5_perc} %\n"
    best_1y = best_1y + f"6. ${top_6_ticker} -> {top_6_perc} %\n"
    best_1y = best_1y + f"7. ${top_7_ticker} -> {top_7_perc} %\n"
    best_1y = best_1y + f"8. ${top_8_ticker} -> {top_8_perc} %\n"
    best_1y = best_1y + f"9. ${top_9_ticker} -> {top_9_perc} %\n"
    best_1y = best_1y + f"10. ${top_10_ticker} -> {top_10_perc} %\n"
    
    message_1d_hastahs = best_1y
    
    for element in lista_hastaghs:
        
        new_word_distance = len(element) + 1 
        
        message_1d_hastahs_distance = len(message_1d_hastahs)
        
        if new_word_distance+message_1d_hastahs_distance<=280:
            
            message_1d_hastahs = message_1d_hastahs+element
            
    #print(len(message_1d_hastahs))
    #print()
    #print(message_1d_hastahs)
    
    best_1y = message_1d_hastahs
    
    print(best_1y)
    
    print(len(best_1y))

    try:
        post(best_1y)
    except:
        print("ERROR 3-month 10-BOTTOM")
        print(len(best_1y))
        print("ALREADY POSTED ?? ")
    
    return None


# ## Best Half Year

# In[38]:


merged_df.head(3)


# In[39]:


def performance_hy(merged_df):

    import pandas as pd
    # Assuming df_performance is your DataFrame
    # Sort the DataFrame based on the 'gap' column in ascending order
    df_performance_sorted_1y = merged_df.sort_values(by='hf')
    
    top_1_ticker = df_performance_sorted_1y["ticker"].iloc[-1]
    top_1_company = df_performance_sorted_1y["Company"].iloc[-1]
    top_1_perc = df_performance_sorted_1y["hf"].iloc[-1]
    
    top_2_ticker = df_performance_sorted_1y["ticker"].iloc[-2]
    top_2_company = df_performance_sorted_1y["Company"].iloc[-2]
    top_2_perc = df_performance_sorted_1y["hf"].iloc[-2]
    
    top_3_ticker = df_performance_sorted_1y["ticker"].iloc[-3]
    top_3_company = df_performance_sorted_1y["Company"].iloc[-3]
    top_3_perc = df_performance_sorted_1y["hf"].iloc[-3]
    
    top_4_ticker = df_performance_sorted_1y["ticker"].iloc[-4]
    top_4_company = df_performance_sorted_1y["Company"].iloc[-4]
    top_4_perc = df_performance_sorted_1y["hf"].iloc[-4]
    
    top_5_ticker = df_performance_sorted_1y["ticker"].iloc[-5]
    top_5_company = df_performance_sorted_1y["Company"].iloc[-5]
    top_5_perc = df_performance_sorted_1y["hf"].iloc[-5]
    
    top_6_ticker = df_performance_sorted_1y["ticker"].iloc[-6]
    top_6_company = df_performance_sorted_1y["Company"].iloc[-6]
    top_6_perc = df_performance_sorted_1y["hf"].iloc[-6]
    
    top_7_ticker = df_performance_sorted_1y["ticker"].iloc[-7]
    top_7_company = df_performance_sorted_1y["Company"].iloc[-7]
    top_7_perc = df_performance_sorted_1y["hf"].iloc[-7]
    
    top_8_ticker = df_performance_sorted_1y["ticker"].iloc[-8]
    top_8_company = df_performance_sorted_1y["Company"].iloc[-8]
    top_8_perc = df_performance_sorted_1y["hf"].iloc[-8]
    
    top_9_ticker = df_performance_sorted_1y["ticker"].iloc[-9]
    top_9_company = df_performance_sorted_1y["Company"].iloc[-9]
    top_9_perc = df_performance_sorted_1y["hf"].iloc[-9]
    
    top_10_ticker = df_performance_sorted_1y["ticker"].iloc[-10]
    top_10_company = df_performance_sorted_1y["Company"].iloc[-10]
    top_10_perc = df_performance_sorted_1y["hf"].iloc[-10]
    
    best_1y = f"#US Companies over $1B 6-Months-To-Day:\n\nTop-10\n" 
    best_1y = best_1y + f"1. ${top_1_ticker} -> +{top_1_perc} %\n"
    best_1y = best_1y + f"2. ${top_2_ticker} -> +{top_2_perc} %\n"
    best_1y = best_1y + f"3. ${top_3_ticker} -> +{top_3_perc} %\n"
    best_1y = best_1y + f"4. ${top_4_ticker} -> +{top_4_perc} %\n"
    best_1y = best_1y + f"5. ${top_5_ticker} -> +{top_5_perc} %\n"
    best_1y = best_1y + f"6. ${top_6_ticker} -> +{top_6_perc} %\n"
    best_1y = best_1y + f"7. ${top_7_ticker} -> +{top_7_perc} %\n"
    best_1y = best_1y + f"8. ${top_8_ticker} -> +{top_8_perc} %\n"
    best_1y = best_1y + f"9. ${top_9_ticker} -> +{top_9_perc} %\n"
    best_1y = best_1y + f"10. ${top_10_ticker} -> +{top_10_perc} %\n"
    
    message_1d_hastahs = best_1y
    
    for element in lista_hastaghs:
        
        new_word_distance = len(element) + 1 
        
        message_1d_hastahs_distance = len(message_1d_hastahs)
        
        if new_word_distance+message_1d_hastahs_distance<=280:
            
            message_1d_hastahs = message_1d_hastahs+element
            
    #print(len(message_1d_hastahs))
    #print()
    #print(message_1d_hastahs)
    
    best_1y = message_1d_hastahs
    
    print(best_1y)
    
    print(len(best_1y))
    
    try:
        post(best_1y)
    except:
        print("ERROR 6-month 10-TOP")
        print(len(best_1y))
        print("ALREADY POSTED ?? ")
    time.sleep(30)
    top_1_ticker = df_performance_sorted_1y["ticker"].iloc[0]
    top_1_company = df_performance_sorted_1y["Company"].iloc[0]
    top_1_perc = df_performance_sorted_1y["hf"].iloc[0]
    
    top_2_ticker = df_performance_sorted_1y["ticker"].iloc[1]
    top_2_company = df_performance_sorted_1y["Company"].iloc[1]
    top_2_perc = df_performance_sorted_1y["hf"].iloc[1]
    
    top_3_ticker = df_performance_sorted_1y["ticker"].iloc[2]
    top_3_company = df_performance_sorted_1y["Company"].iloc[2]
    top_3_perc = df_performance_sorted_1y["hf"].iloc[2]
    
    top_4_ticker = df_performance_sorted_1y["ticker"].iloc[3]
    top_4_company = df_performance_sorted_1y["Company"].iloc[3]
    top_4_perc = df_performance_sorted_1y["hf"].iloc[3]
    
    top_5_ticker = df_performance_sorted_1y["ticker"].iloc[4]
    top_5_company = df_performance_sorted_1y["Company"].iloc[4]
    top_5_perc = df_performance_sorted_1y["hf"].iloc[4]
    
    top_6_ticker = df_performance_sorted_1y["ticker"].iloc[5]
    top_6_company = df_performance_sorted_1y["Company"].iloc[5]
    top_6_perc = df_performance_sorted_1y["hf"].iloc[5]
    
    top_7_ticker = df_performance_sorted_1y["ticker"].iloc[6]
    top_7_company = df_performance_sorted_1y["Company"].iloc[6]
    top_7_perc = df_performance_sorted_1y["hf"].iloc[6]
    
    top_8_ticker = df_performance_sorted_1y["ticker"].iloc[7]
    top_8_company = df_performance_sorted_1y["Company"].iloc[7]
    top_8_perc = df_performance_sorted_1y["hf"].iloc[7]
    
    top_9_ticker = df_performance_sorted_1y["ticker"].iloc[8]
    top_9_company = df_performance_sorted_1y["Company"].iloc[8]
    top_9_perc = df_performance_sorted_1y["hf"].iloc[8]
    
    top_10_ticker = df_performance_sorted_1y["ticker"].iloc[9]
    top_10_company = df_performance_sorted_1y["Company"].iloc[9]
    top_10_perc = df_performance_sorted_1y["hf"].iloc[9]
    
    best_1y = f"#US Companies over $1B 6-Months-To-Day:\n\nBottom-10\n" 
    best_1y = best_1y + f"1. ${top_1_ticker} -> {top_1_perc} %\n"
    best_1y = best_1y + f"2. ${top_2_ticker} -> {top_2_perc} %\n"
    best_1y = best_1y + f"3. ${top_3_ticker} -> {top_3_perc} %\n"
    best_1y = best_1y + f"4. ${top_4_ticker} -> {top_4_perc} %\n"
    best_1y = best_1y + f"5. ${top_5_ticker} -> {top_5_perc} %\n"
    best_1y = best_1y + f"6. ${top_6_ticker} -> {top_6_perc} %\n"
    best_1y = best_1y + f"7. ${top_7_ticker} -> {top_7_perc} %\n"
    best_1y = best_1y + f"8. ${top_8_ticker} -> {top_8_perc} %\n"
    best_1y = best_1y + f"9. ${top_9_ticker} -> {top_9_perc} %\n"
    best_1y = best_1y + f"10. ${top_10_ticker} -> {top_10_perc} %\n"
    
    message_1d_hastahs = best_1y
    
    for element in lista_hastaghs:
        
        new_word_distance = len(element) + 1 
        
        message_1d_hastahs_distance = len(message_1d_hastahs)
        
        if new_word_distance+message_1d_hastahs_distance<=280:
            
            message_1d_hastahs = message_1d_hastahs+element
            
    #print(len(message_1d_hastahs))
    #print()
    #print(message_1d_hastahs)
    
    best_1y = message_1d_hastahs
    
    print(best_1y)
    
    print(len(best_1y))

    try:
        post(best_1y)
    except:
        print("ERROR 6-month 10-BOTTOM")
        print(len(best_1y))
        print("ALREADY POSTED ?? ")
    
    return None


# In[ ]:





# ## Best Year

# In[40]:


merged_df.head(3)


# In[41]:


def performance_y(merged_df):

    import pandas as pd
    # Assuming df_performance is your DataFrame
    # Sort the DataFrame based on the 'gap' column in ascending order
    df_performance_sorted_1y = merged_df.sort_values(by='ytd')
    
    top_1_ticker = df_performance_sorted_1y["ticker"].iloc[-1]
    top_1_company = df_performance_sorted_1y["Company"].iloc[-1]
    top_1_perc = df_performance_sorted_1y["ytd"].iloc[-1]
    
    top_2_ticker = df_performance_sorted_1y["ticker"].iloc[-2]
    top_2_company = df_performance_sorted_1y["Company"].iloc[-2]
    top_2_perc = df_performance_sorted_1y["ytd"].iloc[-2]
    
    top_3_ticker = df_performance_sorted_1y["ticker"].iloc[-3]
    top_3_company = df_performance_sorted_1y["Company"].iloc[-3]
    top_3_perc = df_performance_sorted_1y["ytd"].iloc[-3]
    
    top_4_ticker = df_performance_sorted_1y["ticker"].iloc[-4]
    top_4_company = df_performance_sorted_1y["Company"].iloc[-4]
    top_4_perc = df_performance_sorted_1y["ytd"].iloc[-4]
    
    top_5_ticker = df_performance_sorted_1y["ticker"].iloc[-5]
    top_5_company = df_performance_sorted_1y["Company"].iloc[-5]
    top_5_perc = df_performance_sorted_1y["ytd"].iloc[-5]
    
    top_6_ticker = df_performance_sorted_1y["ticker"].iloc[-6]
    top_6_company = df_performance_sorted_1y["Company"].iloc[-6]
    top_6_perc = df_performance_sorted_1y["ytd"].iloc[-6]
    
    top_7_ticker = df_performance_sorted_1y["ticker"].iloc[-7]
    top_7_company = df_performance_sorted_1y["Company"].iloc[-7]
    top_7_perc = df_performance_sorted_1y["ytd"].iloc[-7]
    
    top_8_ticker = df_performance_sorted_1y["ticker"].iloc[-8]
    top_8_company = df_performance_sorted_1y["Company"].iloc[-8]
    top_8_perc = df_performance_sorted_1y["ytd"].iloc[-8]
    
    top_9_ticker = df_performance_sorted_1y["ticker"].iloc[-9]
    top_9_company = df_performance_sorted_1y["Company"].iloc[-9]
    top_9_perc = df_performance_sorted_1y["ytd"].iloc[-9]
    
    top_10_ticker = df_performance_sorted_1y["ticker"].iloc[-10]
    top_10_company = df_performance_sorted_1y["Company"].iloc[-10]
    top_10_perc = df_performance_sorted_1y["ytd"].iloc[-10]
    
    best_1y = f"#US Companies over $1B 1-Year-To-Day:\n\nTop-10\n" 
    best_1y = best_1y + f"1. ${top_1_ticker} -> +{top_1_perc} %\n"
    best_1y = best_1y + f"2. ${top_2_ticker} -> +{top_2_perc} %\n"
    best_1y = best_1y + f"3. ${top_3_ticker} -> +{top_3_perc} %\n"
    best_1y = best_1y + f"4. ${top_4_ticker} -> +{top_4_perc} %\n"
    best_1y = best_1y + f"5. ${top_5_ticker} -> +{top_5_perc} %\n"
    best_1y = best_1y + f"6. ${top_6_ticker} -> +{top_6_perc} %\n"
    best_1y = best_1y + f"7. ${top_7_ticker} -> +{top_7_perc} %\n"
    best_1y = best_1y + f"8. ${top_8_ticker} -> +{top_8_perc} %\n"
    best_1y = best_1y + f"9. ${top_9_ticker} -> +{top_9_perc} %\n"
    best_1y = best_1y + f"10. ${top_10_ticker} -> +{top_10_perc} %\n"
    
    message_1d_hastahs = best_1y
    
    for element in lista_hastaghs:
        
        new_word_distance = len(element) + 1 
        
        message_1d_hastahs_distance = len(message_1d_hastahs)
        
        if new_word_distance+message_1d_hastahs_distance<=280:
            
            message_1d_hastahs = message_1d_hastahs+element
            
    #print(len(message_1d_hastahs))
    #print()
    #print(message_1d_hastahs)
    
    best_1y = message_1d_hastahs
    
    print(best_1y)
    
    print(len(best_1y))
    
    try:
        post(best_1y)
    except:
        print("ERROR 1-Year-To-Day 10-TOP")
        print(len(best_1y))
        print("ALREADY POSTED ?? ")
    time.sleep(30)
    top_1_ticker = df_performance_sorted_1y["ticker"].iloc[0]
    top_1_company = df_performance_sorted_1y["Company"].iloc[0]
    top_1_perc = df_performance_sorted_1y["ytd"].iloc[0]
    
    top_2_ticker = df_performance_sorted_1y["ticker"].iloc[1]
    top_2_company = df_performance_sorted_1y["Company"].iloc[1]
    top_2_perc = df_performance_sorted_1y["ytd"].iloc[1]
    
    top_3_ticker = df_performance_sorted_1y["ticker"].iloc[2]
    top_3_company = df_performance_sorted_1y["Company"].iloc[2]
    top_3_perc = df_performance_sorted_1y["ytd"].iloc[2]
    
    top_4_ticker = df_performance_sorted_1y["ticker"].iloc[3]
    top_4_company = df_performance_sorted_1y["Company"].iloc[3]
    top_4_perc = df_performance_sorted_1y["ytd"].iloc[3]
    
    top_5_ticker = df_performance_sorted_1y["ticker"].iloc[4]
    top_5_company = df_performance_sorted_1y["Company"].iloc[4]
    top_5_perc = df_performance_sorted_1y["ytd"].iloc[4]
    
    top_6_ticker = df_performance_sorted_1y["ticker"].iloc[5]
    top_6_company = df_performance_sorted_1y["Company"].iloc[5]
    top_6_perc = df_performance_sorted_1y["ytd"].iloc[5]
    
    top_7_ticker = df_performance_sorted_1y["ticker"].iloc[6]
    top_7_company = df_performance_sorted_1y["Company"].iloc[6]
    top_7_perc = df_performance_sorted_1y["ytd"].iloc[6]
    
    top_8_ticker = df_performance_sorted_1y["ticker"].iloc[7]
    top_8_company = df_performance_sorted_1y["Company"].iloc[7]
    top_8_perc = df_performance_sorted_1y["ytd"].iloc[7]
    
    top_9_ticker = df_performance_sorted_1y["ticker"].iloc[8]
    top_9_company = df_performance_sorted_1y["Company"].iloc[8]
    top_9_perc = df_performance_sorted_1y["ytd"].iloc[8]
    
    top_10_ticker = df_performance_sorted_1y["ticker"].iloc[9]
    top_10_company = df_performance_sorted_1y["Company"].iloc[9]
    top_10_perc = df_performance_sorted_1y["ytd"].iloc[9]
    
    best_1y = f"#US Companies over $1B 1-Year-To-Day:\n\nBottom-10\n" 
    best_1y = best_1y + f"1. ${top_1_ticker} -> {top_1_perc} %\n"
    best_1y = best_1y + f"2. ${top_2_ticker} -> {top_2_perc} %\n"
    best_1y = best_1y + f"3. ${top_3_ticker} -> {top_3_perc} %\n"
    best_1y = best_1y + f"4. ${top_4_ticker} -> {top_4_perc} %\n"
    best_1y = best_1y + f"5. ${top_5_ticker} -> {top_5_perc} %\n"
    best_1y = best_1y + f"6. ${top_6_ticker} -> {top_6_perc} %\n"
    best_1y = best_1y + f"7. ${top_7_ticker} -> {top_7_perc} %\n"
    best_1y = best_1y + f"8. ${top_8_ticker} -> {top_8_perc} %\n"
    best_1y = best_1y + f"9. ${top_9_ticker} -> {top_9_perc} %\n"
    best_1y = best_1y + f"10. ${top_10_ticker} -> {top_10_perc} %\n"
    
    message_1d_hastahs = best_1y
    
    for element in lista_hastaghs:
        
        new_word_distance = len(element) + 1 
        
        message_1d_hastahs_distance = len(message_1d_hastahs)
        
        if new_word_distance+message_1d_hastahs_distance<=280:
            
            message_1d_hastahs = message_1d_hastahs+element
            
    #print(len(message_1d_hastahs))
    #print()
    #print(message_1d_hastahs)
    
    best_1y = message_1d_hastahs
    
    print(best_1y)
    
    print(len(best_1y))

    try:
        post(best_1y)
    except:
        print("ERROR 1-Year-To-Day 10-BOTTOM")
        print(len(best_1y))
        print("ALREADY POSTED ?? ")
    
    return None


# In[ ]:





# ### Calculation

# In[42]:


import time


# In[43]:


time.sleep(60*15)


# In[44]:


merged_df


# In[45]:


end_time = time.time()

execution_time = end_time - start_time

# Convert seconds to hours, minutes, and seconds
hours = int(execution_time // 3600)
minutes = int((execution_time % 3600) // 60)
seconds = int(execution_time % 60)

print("Execution time:", hours, "hours", minutes, "minutes", seconds, "seconds")


# In[46]:


performance_today(merged_df)


# In[47]:


time.sleep(60*15)


# In[48]:


performance_week(merged_df)


# In[49]:


time.sleep(60*15)


# In[50]:


performance_month(merged_df)


# In[51]:


time.sleep(60*15)


# In[52]:


performance_3month(merged_df)


# In[53]:


time.sleep(60*15)


# In[54]:


performance_hy(merged_df)


# In[55]:


time.sleep(60*15)


# In[56]:


performance_y(merged_df)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




