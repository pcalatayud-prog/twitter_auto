#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests
import numpy as np
import yfinance as yf
import tweepy
import json

# # Replace 'your_file.csv' with the actual path to your .csv file
# file_path = 'ticker_info.csv'

# # Read the .csv file into a pandas DataFrame
# df = pd.read_csv(file_path, index_col=0)

# columns = list(df.keys())

# columns.append("marketCap")

# df_to_fill = pd.DataFrame(columns = columns)
# df_to_fill

data = {
    "name": ["Energy","Real","Health","Financial","Comm","Utilities","Materials","IT","Indust","Staples","Discrec","SemiCond"],
    "symbol": ["VDE", "VNQ", "VHT", "VFH", "VOX", "VPU", "VAW", "VGT", "VIS", "VDC", "VCR" , "SOXX"]
}

tickers = pd.DataFrame(data)
tickers


# In[2]:


filtered_tickers = tickers["symbol"].tolist()
print(len(filtered_tickers))
filtered_tickers


# In[3]:


tickers


# In[ ]:





# In[4]:


from auth import api_key
from auth import api_key_secret
from auth import access_token
from auth import access_token_secret
from auth import bearer


# In[ ]:





# In[5]:


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


# In[6]:


df = tickers.copy()


# In[7]:


import warnings
warnings.filterwarnings('ignore')


# In[8]:


tickers = list(df["symbol"])
tickers


# In[9]:


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


# In[10]:


lista_hastaghs = ["\n#Stockmarket"]


# In[ ]:





# In[11]:


df_performance = pd.DataFrame(columns = ["ticker","ytd","hf","3mtd","mtd","wtd","dtd"])

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
            price_open = stock_data_1YTD["Adj Close"].iloc[0]
            price_close = stock_data_1YTD["Adj Close"].iloc[-1]
            return_ytd = round(100*(price_close-price_open)/price_open,1)
            #print("Year To Day Return",return_ytd)
        except:
            return_ytd = np.nan
    
        try:
            # Half YEAR TO DAY
            stock_data_HF = stock_data.copy()
            stock_data_HF = stock_data_HF[stock_data_HF.index>=start_date_half]
            price_open = stock_data_HF["Adj Close"].iloc[0]
            price_close = stock_data_HF["Adj Close"].iloc[-1]
            return_hf = round(100*(price_close-price_open)/price_open,1)
            #print("Year To Day Return",return_ytd)
        except:
            return_hf = np.nan
    
        
    
        try:
            # 3 MONTH TO DAY
            stock_data_3M = stock_data.copy()
            stock_data_3M = stock_data_3M[stock_data_3M.index>=start_date_3month]
            price_open = stock_data_3M["Adj Close"].iloc[0]
            price_close = stock_data_3M["Adj Close"].iloc[-1]
            return_3mtd = round(100*(price_close-price_open)/price_open,1)
            #print("Year To Day Return",return_ytd)
        except:
            return_3mtd = np.nan          
            
            
        try:
            # MONTH TO DAY
            stock_data_MTD = stock_data.copy()
            stock_data_MTD = stock_data_MTD[stock_data_MTD.index>=start_date_month]
            price_open = stock_data_MTD["Adj Close"].iloc[0]
            price_close = stock_data_MTD["Adj Close"].iloc[-1]
            return_mtd = round(100*(price_close-price_open)/price_open,1)
            #print("Month To Day Return",return_mtd)
        except:
            return_mtd = np.nan
        
        try:
            # WEEK TO DAY
            stock_data_WTD = stock_data.copy()
            stock_data_WTD = stock_data_WTD[stock_data_WTD.index>=start_date_week]
            price_open = stock_data_WTD["Adj Close"].iloc[0]
            price_close = stock_data_WTD["Adj Close"].iloc[-1]
            return_wtd = round(100*(price_close-price_open)/price_open,1)
            #print("Month To Day Return",return_wtd)
        except:
            return_wtd = np.nan
    
        try:
            # DAY TO DAY
            stock_data_DTD = stock_data.tail(2)
            stock_data_DTD["returns"] = round(100 * stock_data_DTD["Close"].pct_change(),1)
            return_dtd = stock_data_DTD["returns"].iloc[-1]
            #print("Day To Day Return",return_dtd)
        except:
            return_dtd = np.nan
    
        row = [ticker,return_ytd,return_hf,return_3mtd,return_mtd,return_wtd,return_dtd]

        df_performance.loc[len(df_performance)] = row
    
    except:
        
        pass


# In[12]:


df_performance


# In[13]:


df_performance.dropna(inplace=True)


# In[14]:


df["ticker"] = df["symbol"]
df


# In[15]:


merged_df = pd.merge(df, df_performance, on='ticker')
merged_df["Company"] = merged_df["name"]
merged_df


# ## Best Today

# In[16]:


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
    
    top_11_ticker = df_performance_sorted_1y["ticker"].iloc[-11]
    top_11_company = df_performance_sorted_1y["Company"].iloc[-11]
    top_11_perc = df_performance_sorted_1y["dtd"].iloc[-11]
    
    top_12_ticker = df_performance_sorted_1y["ticker"].iloc[-12]
    top_12_company = df_performance_sorted_1y["Company"].iloc[-12]
    top_12_perc = df_performance_sorted_1y["dtd"].iloc[-12]
    
    best_1y = f"#Sectors -> 1-Day\n" 
    best_1y = best_1y + f"1. #{top_1_company} -> {top_1_perc} %\n"
    best_1y = best_1y + f"2. #{top_2_company} -> {top_2_perc} %\n"
    best_1y = best_1y + f"3. #{top_3_company} -> {top_3_perc} %\n"
    best_1y = best_1y + f"4. #{top_4_company} -> {top_4_perc} %\n"
    best_1y = best_1y + f"5. #{top_5_company} -> {top_5_perc} %\n"
    best_1y = best_1y + f"6. #{top_6_company} -> {top_6_perc} %\n"
    best_1y = best_1y + f"7. #{top_7_company} -> {top_7_perc} %\n"
    best_1y = best_1y + f"8. #{top_8_company} -> {top_8_perc} %\n"
    best_1y = best_1y + f"9. #{top_9_company} -> {top_9_perc} %\n"
    best_1y = best_1y + f"10. #{top_10_company} -> {top_10_perc} %\n"
    best_1y = best_1y + f"11. #{top_11_company} -> {top_11_perc} %\n"
    best_1y = best_1y + f"12. #{top_12_company} -> {top_12_perc} %\n"
    
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
    
    return None


# In[17]:


# performance_today(merged_df)


# ## Best Week

# In[18]:


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
    
    top_11_ticker = df_performance_sorted_1y["ticker"].iloc[-11]
    top_11_company = df_performance_sorted_1y["Company"].iloc[-11]
    top_11_perc = df_performance_sorted_1y["dtd"].iloc[-11]
    
    top_12_ticker = df_performance_sorted_1y["ticker"].iloc[-12]
    top_12_company = df_performance_sorted_1y["Company"].iloc[-12]
    top_12_perc = df_performance_sorted_1y["dtd"].iloc[-12]
    
    best_1y = f"#Sectors -> 1-WTD:\n\n" 
    best_1y = best_1y + f"1. #{top_1_company} -> {top_1_perc} %\n"
    best_1y = best_1y + f"2. #{top_2_company} -> {top_2_perc} %\n"
    best_1y = best_1y + f"3. #{top_3_company} -> {top_3_perc} %\n"
    best_1y = best_1y + f"4. #{top_4_company} -> {top_4_perc} %\n"
    best_1y = best_1y + f"5. #{top_5_company} -> {top_5_perc} %\n"
    best_1y = best_1y + f"6. #{top_6_company} -> {top_6_perc} %\n"
    best_1y = best_1y + f"7. #{top_7_company} -> {top_7_perc} %\n"
    best_1y = best_1y + f"8. #{top_8_company} -> {top_8_perc} %\n"
    best_1y = best_1y + f"9. #{top_9_company} -> {top_9_perc} %\n"
    best_1y = best_1y + f"10. #{top_10_company} -> {top_10_perc} %\n"
    best_1y = best_1y + f"11. #{top_11_company} -> {top_11_perc} %\n"
    best_1y = best_1y + f"12. #{top_12_company} -> {top_12_perc} %\n"
    
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

    
    return None


# In[19]:


# performance_week(merged_df)


# In[ ]:





# ## Best Month

# In[20]:


merged_df.head(3)


# In[21]:


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
    
    top_11_ticker = df_performance_sorted_1y["ticker"].iloc[-11]
    top_11_company = df_performance_sorted_1y["Company"].iloc[-11]
    top_11_perc = df_performance_sorted_1y["dtd"].iloc[-11]
    
    top_12_ticker = df_performance_sorted_1y["ticker"].iloc[-12]
    top_12_company = df_performance_sorted_1y["Company"].iloc[-12]
    top_12_perc = df_performance_sorted_1y["dtd"].iloc[-12]
    
    best_1y = f"#Sectors -> 1-MTD:\n\n" 
    best_1y = best_1y + f"1. #{top_1_company} -> {top_1_perc} %\n"
    best_1y = best_1y + f"2. #{top_2_company} -> {top_2_perc} %\n"
    best_1y = best_1y + f"3. #{top_3_company} -> {top_3_perc} %\n"
    best_1y = best_1y + f"4. #{top_4_company} -> {top_4_perc} %\n"
    best_1y = best_1y + f"5. #{top_5_company} -> {top_5_perc} %\n"
    best_1y = best_1y + f"6. #{top_6_company} -> {top_6_perc} %\n"
    best_1y = best_1y + f"7. #{top_7_company} -> {top_7_perc} %\n"
    best_1y = best_1y + f"8. #{top_8_company} -> {top_8_perc} %\n"
    best_1y = best_1y + f"9. #{top_9_company} -> {top_9_perc} %\n"
    best_1y = best_1y + f"10. #{top_10_company} -> {top_10_perc} %\n"
    best_1y = best_1y + f"11. #{top_11_company} -> {top_11_perc} %\n"
    best_1y = best_1y + f"12. #{top_12_company} -> {top_12_perc} %\n"
    
    
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
    
    return None


# In[22]:


# performance_month(merged_df)


# In[ ]:





# ## Best 3-Month 

# In[23]:


merged_df.head(3)


# In[24]:


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
    
    top_11_ticker = df_performance_sorted_1y["ticker"].iloc[-11]
    top_11_company = df_performance_sorted_1y["Company"].iloc[-11]
    top_11_perc = df_performance_sorted_1y["dtd"].iloc[-11]
    
    top_12_ticker = df_performance_sorted_1y["ticker"].iloc[-12]
    top_12_company = df_performance_sorted_1y["Company"].iloc[-12]
    top_12_perc = df_performance_sorted_1y["dtd"].iloc[-12]
    
    #best_1y = f"#US Companies over $1B 3-Months-To-Day:\n\nTop-10\n" 
    best_1y = f"#Sectors -> 3-MTD:\n\n" 
    best_1y = best_1y + f"1. #{top_1_company} -> {top_1_perc} %\n"
    best_1y = best_1y + f"2. #{top_2_company} -> {top_2_perc} %\n"
    best_1y = best_1y + f"3. #{top_3_company} -> {top_3_perc} %\n"
    best_1y = best_1y + f"4. #{top_4_company} -> {top_4_perc} %\n"
    best_1y = best_1y + f"5. #{top_5_company} -> {top_5_perc} %\n"
    best_1y = best_1y + f"6. #{top_6_company} -> {top_6_perc} %\n"
    best_1y = best_1y + f"7. #{top_7_company} -> {top_7_perc} %\n"
    best_1y = best_1y + f"8. #{top_8_company} -> {top_8_perc} %\n"
    best_1y = best_1y + f"9. #{top_9_company} -> {top_9_perc} %\n"
    best_1y = best_1y + f"10. #{top_10_company} -> {top_10_perc} %\n"
    best_1y = best_1y + f"11. #{top_11_company} -> {top_11_perc} %\n"
    best_1y = best_1y + f"12. #{top_12_company} -> {top_12_perc} %\n"
    
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

    return None


# In[25]:


# performance_3month(merged_df)


# In[ ]:





# ## Best Half Year

# In[26]:


merged_df.head(3)


# In[27]:


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
    
    top_11_ticker = df_performance_sorted_1y["ticker"].iloc[-11]
    top_11_company = df_performance_sorted_1y["Company"].iloc[-11]
    top_11_perc = df_performance_sorted_1y["hf"].iloc[-11]
    
    top_12_ticker = df_performance_sorted_1y["ticker"].iloc[-12]
    top_12_company = df_performance_sorted_1y["Company"].iloc[-12]
    top_12_perc = df_performance_sorted_1y["hf"].iloc[-12]

    
    best_1y = f"#Sectors -> 6-MTD:\n\n" 
    best_1y = best_1y + f"1. #{top_1_company} -> {top_1_perc} %\n"
    best_1y = best_1y + f"2. #{top_2_company} -> {top_2_perc} %\n"
    best_1y = best_1y + f"3. #{top_3_company} -> {top_3_perc} %\n"
    best_1y = best_1y + f"4. #{top_4_company} -> {top_4_perc} %\n"
    best_1y = best_1y + f"5. #{top_5_company} -> {top_5_perc} %\n"
    best_1y = best_1y + f"6. #{top_6_company} -> {top_6_perc} %\n"
    best_1y = best_1y + f"7. #{top_7_company} -> {top_7_perc} %\n"
    best_1y = best_1y + f"8. #{top_8_company} -> {top_8_perc} %\n"
    best_1y = best_1y + f"9. #{top_9_company} -> {top_9_perc} %\n"
    best_1y = best_1y + f"10. #{top_10_company} -> {top_10_perc} %\n"
    best_1y = best_1y + f"11. #{top_11_company} -> {top_11_perc} %\n"
    best_1y = best_1y + f"12. #{top_12_company} -> {top_12_perc} %\n"
    
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
    
    return None


# In[28]:


# performance_hy(merged_df)


# ## Best Year

# In[29]:


merged_df.head(3)


# In[30]:


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
    
    top_11_ticker = df_performance_sorted_1y["ticker"].iloc[-11]
    top_11_company = df_performance_sorted_1y["Company"].iloc[-11]
    top_11_perc = df_performance_sorted_1y["hf"].iloc[-11]
    
    top_12_ticker = df_performance_sorted_1y["ticker"].iloc[-12]
    top_12_company = df_performance_sorted_1y["Company"].iloc[-12]
    top_12_perc = df_performance_sorted_1y["hf"].iloc[-12]
    
    
    best_1y = f"#Sectors -> 1YTD:\n\n" 
    best_1y = best_1y + f"1. #{top_1_company} -> {top_1_perc} %\n"
    best_1y = best_1y + f"2. #{top_2_company} -> {top_2_perc} %\n"
    best_1y = best_1y + f"3. #{top_3_company} -> {top_3_perc} %\n"
    best_1y = best_1y + f"4. #{top_4_company} -> {top_4_perc} %\n"
    best_1y = best_1y + f"5. #{top_5_company} -> {top_5_perc} %\n"
    best_1y = best_1y + f"6. #{top_6_company} -> {top_6_perc} %\n"
    best_1y = best_1y + f"7. #{top_7_company} -> {top_7_perc} %\n"
    best_1y = best_1y + f"8. #{top_8_company} -> {top_8_perc} %\n"
    best_1y = best_1y + f"9. #{top_9_company} -> {top_9_perc} %\n"
    best_1y = best_1y + f"10. #{top_10_company} -> {top_10_perc} %\n"
    best_1y = best_1y + f"11. #{top_11_company} -> {top_11_perc} %\n"
    best_1y = best_1y + f"12. #{top_12_company} -> {top_12_perc} %\n"    
    
    
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
    return None


# In[ ]:





# ### Calculation

# In[31]:


import time


# In[32]:


#performance_today(merged_df)


# In[33]:


#time.sleep(60*2)


# In[34]:


performance_week(merged_df)


# In[35]:


time.sleep(60)


# In[36]:


#performance_month(merged_df)


# In[37]:


#time.sleep(60*2)


# In[38]:


performance_3month(merged_df)


# In[39]:


#time.sleep(60*2)


# In[40]:


#performance_hy(merged_df)


# In[41]:


time.sleep(60*1)


# In[42]:


performance_y(merged_df)



