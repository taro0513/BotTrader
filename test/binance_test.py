from binance.client import Client

client = Client('14SckuzWkbMSMidF5nncQ7M3DMxTVJEGKCKdD2oQBYZZKXpUV1FXHmMYzChmQ1mc',
                'vAITSCoiHZGk26j8ob39cn4AORLuJPPy70W29mLBdSifbm9qX3p1dv5oKW6DHNCA')

prices = client.get_all_tickers()

