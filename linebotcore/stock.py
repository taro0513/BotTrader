from django.conf import settings
from .utils import Utils
from linebot.models import *
import cryptocompare
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import mplfinance as mpf
import yfinance as yf
from datetime import datetime, timedelta, timezone
import pyimgur
import time
from pathlib import Path
import re

cryptocompare.cryptocompare._set_api_key_parameter(settings.CRYPTOCOMPARE_KEY)


def timestamp_to_utc8(timestamp):
    dt_utc = datetime.fromtimestamp(timestamp, timezone.utc)
    dt_utc8 = dt_utc.astimezone(timezone(timedelta(hours=8)))
    formatted_datetime = dt_utc8.strftime("%Y-%m-%d %H:%M:%S")
    return "{}(utc+8)".format(formatted_datetime)


class StockHandler:
    def __init__(self, text):
        self.text = text
        self.messages = []
        self.columns = []
        self.detect()

    def detect(self):
        supported_currencies = cryptocompare.get_coin_list()
        pattern = r'\b(' + '|'.join(re.escape(currency) for currency in supported_currencies) + r')\b'
        matches = re.findall(pattern, self.text, re.IGNORECASE)
        result = [word.upper() for word in matches]
        if not result:
            return

        for currency in result:
            data = self.generate_candlestick_chart(currency)
            self.generate_candlestick_chart_column(currency,
                                                   data['link'],
                                                   'https://www.cryptocompare.com/coins/' + currency + '/overview/USDT')
            if data['valid']:
                self.generate_bubble(currency, data['open'], data['high'], data['low'], data['close'],
                                     timestamp_to_utc8(data['timestamp']))

        self.generate_candlestick_chart_carousel()

    def generate_candlestick_chart(self, fsym: str, tsym: str = 'USD', limit: int = 100):
        timestamp = int(time.time())
        data = cryptocompare.get_historical_price_hour(fsym, tsym, limit=limit)
        if not data:
            return {
                'valid': False,
                'link': 'https://cdn.dribbble.com/users/683081/screenshots/2728654/media/d6f3cc39f60fcd48bc2236264b4748b9.png',
                'open': 0,
                'high': 0,
                'low': 0,
                'close': 0,
                'timestamp': timestamp
            }
        timestamps = [entry['time'] for entry in data]
        opens = [entry['open'] for entry in data]
        highs = [entry['high'] for entry in data]
        lows = [entry['low'] for entry in data]
        closes = [entry['close'] for entry in data]
        volumes = [entry['volumeto'] for entry in data]
        df = pd.DataFrame({'Open': opens, 'High': highs, 'Low': lows, 'Close': closes, 'Volume': volumes},
                          index=timestamps)
        df.index = pd.to_datetime(df.index, unit='s')

        filename = "linebotcore/image/{}-{}.jpg".format(fsym, timestamp)

        mpf.plot(df, type='candle', volume=False, style='yahoo', title='{} Candlestick Chart'.format(fsym),
                 savefig=dict(fname=filename))

        im = pyimgur.Imgur(settings.IMGUR_CLIENT_ID)
        uploaded_image = im.upload_image(filename, title="{} candlestick chart({})".format(fsym, timestamp))
        path = Path(filename)
        if path.exists():
            path.unlink()

        today_open, today_high, today_low, today_close, _t = self.get_today_cryptocurrency_data(fsym)

        return {
            'valid': True,
            'link': uploaded_image.link,
            'open': today_open,
            'high': today_high,
            'low': today_low,
            'close': today_close,
            'timestamp': _t
        }

    def generate_candlestick_chart_column(self, title: str, candlestick_chart_url: str, visiting_url: str):
        print(title, candlestick_chart_url, visiting_url)
        self.columns.append(
            CarouselColumn(
                thumbnail_image_url=candlestick_chart_url,
                title=title,
                text='{} candlestick chart'.format(title),
                actions=[
                    URIAction(
                        label='View {} chart'.format(title),
                        uri=visiting_url
                    )
                ]
            )
        )

    def generate_candlestick_chart_carousel(self):
        if self.columns:
            self.messages.append(
                TemplateSendMessage(
                    alt_text='Carousel template',
                    template=CarouselTemplate(
                        columns=self.columns
                    )
                )
            )

    def get_today_cryptocurrency_data(self, symbol):
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        price_data = cryptocompare.get_historical_price_day(symbol, currency="USD", limit=1)[-1]
        today_open_price = price_data['open']
        today_high_price = price_data['high']
        today_low_price = price_data['low']
        today_close_price = price_data['close']
        time_stamp = price_data['time']

        return today_open_price, today_high_price, today_low_price, today_close_price, time_stamp

    def generate_bubble(self, title: str, open: float, high: float, low: float, close: float, time: str):
        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text=title, weight='bold', size='xl'),
                    SeparatorComponent(),
                    BoxComponent(
                        layout='vertical',
                        contents=[
                            BoxComponent(
                                layout='horizontal',
                                contents=[],
                                height='30px'
                            ),
                            BoxComponent(
                                layout='horizontal',
                                contents=[
                                    BoxComponent(
                                        layout='horizontal',
                                        contents=[
                                            TextComponent(
                                                text='開盤價',
                                                size='md',
                                                weight='bold',
                                                color='#808080'
                                            ),
                                            TextComponent(
                                                text="{:.5f}".format(open),
                                                size='md',
                                                color='#3F3F3F'
                                            )
                                        ]
                                    ),
                                    BoxComponent(
                                        layout='horizontal',
                                        contents=[
                                            TextComponent(
                                                text='收盤價',
                                                weight='bold',
                                                size='md',
                                                color='#808080'
                                            ),
                                            TextComponent(
                                                text="{:.5f}".format(close),
                                                size='md',
                                                color='#3F3F3F'
                                            )
                                        ]
                                    )
                                ]
                            ),
                            BoxComponent(
                                layout='horizontal',
                                contents=[
                                    BoxComponent(
                                        layout='horizontal',
                                        contents=[
                                            TextComponent(
                                                text='最高點',
                                                weight='bold',
                                                size='md',
                                                color='#808080'
                                            ),
                                            TextComponent(
                                                text="{:.5f}".format(high),
                                                size='md',
                                                color='#3F3F3F'
                                            )
                                        ]
                                    ),
                                    BoxComponent(
                                        layout='horizontal',
                                        contents=[
                                            TextComponent(
                                                text='最低點',
                                                weight='bold',
                                                size='md',
                                                color='#808080'
                                            ),
                                            TextComponent(
                                                text="{:.5f}".format(low),
                                                size='md',
                                                color='#3F3F3F'
                                            )
                                        ]
                                    )
                                ]
                            ),
                            TextComponent(
                                text=time,
                                size='xs',
                                style='italic',
                                color='#808080'
                            )

                            # BoxComponent(
                            #     layout='horizontal',
                            #     contents=[
                            #         BoxComponent(
                            #             layout='horizontal',
                            #             contents=[
                            #                 TextComponent(
                            #                     text='交易量',
                            #                     weight='bold',
                            #                     size='md',
                            #                     color='#808080'
                            #                 ),
                            #                 TextComponent(
                            #                     text="{}".format(volume),
                            #                     size='md',
                            #                     color='#3F3F3F'
                            #                 )
                            #             ]
                            #         )
                            #     ]
                            # )
                        ]
                    )
                ]
            )
        )

        self.messages.append(FlexSendMessage(alt_text='Flex Message', contents=bubble))


VIRTUAL_CURRENCY_KEY = {
    'BTC-USD': ['xbt', 'btc', 'bitcoin', '比特幣'],
    'ETH-USD': ['eth', 'ether', 'ethereum', '以太幣'],
    'USDT-USD': ['usdt', 'tether', '泰達幣'],
    'BNB-USD': ['bnb', 'binance', '幣安幣'],
    'USDC-USD': ['usdc', 'usd coin', '美元幣'],

}
