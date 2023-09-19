#下載資料套件
import urllib3
from bs4 import BeautifulSoup

#資料處理套件
import pandas as pd
from datetime import date

#畫圖套件
import matplotlib.pyplot as plt

from plotly.subplots import make_subplots
import plotly.graph_objects as go

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
    
    return df
df = get_tw_futures(start_year = 2023, 
                    start_month = 8, 
                    start_day = 1, 
                    end_year = 2023, 
                    end_month = 9, 
                    end_day = 1,
                    timeform='%Y/%m/%d')

df_tx = df.loc[(df['到期 月份 (週別)'] == 202309.0)]
print(df_tx.keys())
fig = go.Figure(data = [go.Candlestick(x = df_tx['Date'],
                                       open = df_tx['開盤價'],
                                       high = df_tx['最高價'],
                                       low = df_tx['最低價'],
                                       close = df_tx['最後 成交價'],
                                       increasing_line_color = 'red', 
                                       decreasing_line_color = 'green')])
# 設x軸標題
fig.update_xaxes(title_text = "日期")

# 設y軸標題
fig.update_yaxes(title_text = "指數")

# 設圖標及圖長寬
fig.update_layout(
    title_text = "台指期K線圖 - 到期月份2021/10 ",
    width = 800,
    height = 400
)

fig.show()