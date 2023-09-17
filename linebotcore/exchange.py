import requests
from django.conf import settings
from linebot.models import *
from .utils import currency_dict

exchange_api_url = 'https://v6.exchangerate-api.com/v6/{API_KEY}'.format(API_KEY=settings.EXCHANGERATE_KEY)



class ExchangeHandler:
    def __init__(self, text = '', from_c=None, to_c=None):
        self.messages = []
        self.text = text
        self.columns = []
        self.from_c = from_c
        self.to_c = to_c
        # self.detect()

    def detect(self):
        currency = self.text.strip().upper()
        if currency in currency_dict.keys():
            self.get_exchange_rate(currency)
        else:
            return


    def get_exchange_rate(self, currency):
        response = requests.get(exchange_api_url + '/latest/TWD')
        rate = response.json()['conversion_rates'][currency]
        message = "{}({}) 匯率: {:.3f}".format(currency_dict[currency], currency, rate)
        self.messages.append(TextSendMessage(text=message))

    @classmethod
    def get_exchange_conversion(cls, from_c = None, to_c = None, amount = 1):
        if (isinstance(to_c, list)):
            response = requests.get(exchange_api_url + 'latest/{}'.format(from_c))
            rates = response.json()['conversion_rates']
            message = '{}({}) 對\n'.format(currency_dict[from_c], from_c)
            for currency in to_c:
                rate = rates[currency]
                message += "{}({}) 匯率: {:.3f}\n".format(currency_dict[currency], currency, amount/rate)
        else:
            response = requests.get(exchange_api_url + '/pair/{}/{}/{}'.format(from_c, to_c, amount))
            rate = response.json()['conversion_rate']
            message = "{}({}) 對 {}({}) 匯率: {:.3f}".format(
                currency_dict[from_c], from_c,
                currency_dict[to_c], to_c, 
                amount/rate)
        return TextSendMessage(text=message)