import talib
import urllib3
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import pandas_datareader as pdr
import matplotlib.pyplot as plt
import mplfinance as mpf
import seaborn as sns
import datetime as datetime
import talib

def get_tw_futures(start_year, start_month, start_day, 
                   end_year, end_month, end_day, 
                   market_code = 0,
                   commodity_id = 'TX',
                   timeform = '%Y-%m-%d'):
    start_date = str(date(start_year, start_month, start_day))
    end_date = str(date(end_year, end_month, end_day))
    date_list = pd.date_range(start_date, end_date, freq='D').strftime(timeform).tolist()

    df = pd.DataFrame()
    http = urllib3.PoolManager()
    url = "https://www.taifex.com.tw/cht/3/futDailyMarketReport"
    for day in date_list:  
        res = http.request(
             'POST',
              url,
              fields={
                 'queryType': 2,
                 'marketCode': market_code,
                 'commodity_id': 'TX',
                 'queryDate': day,
                 'MarketCode': market_code,
                 'commodity_idt': 'TX'
              }
         )
        html_doc = res.data
        soup = BeautifulSoup(html_doc, 'html.parser')
        table = soup.findAll('table')[2]
        try:
            df_day = pd.read_html(str(table))[2]
        except:
            continue
        df_day.insert(0, 'Date', day)
        df = df._append(df_day, ignore_index = True)
    # df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df.index = pd.DatetimeIndex(df['Date'])     
    # df._append(date_list)
    print(df.keys())
    df = df.rename(index={
        '開盤價': 'Open',
        '最高價': 'High',
        '最低價': 'Low',
        '最後 成交價': 'Close',
        '*合計成交量': 'Volume',
    })
    print(df)
    return df

data = get_tw_futures(start_year = 2023,
                        start_month = 9,
                        start_day = 14,
                        end_year = 2023,
                        end_month = 9,
                        end_day = 15,
                        timeform='%Y-%m-%d')
print(data['開盤價'])
data['Open'] = data['開盤價']
data['High'] = data['最高價']
data['Low'] = data['最低價']
data['Close'] = data['最後 成交價']
data['Volume'] = data['*合計成交量']
print(data)
pl = mpf.plot(data=data, type='candle', style='binance')