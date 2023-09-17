from linebot import (
    LineBotApi
)
from linebot.models import *
# from django.conf import settings

# LINE_CHANNEL_ACCESS_TOKEN = '/fy59BPAm+en4Mj38LoBySuiR02g3eNpOGmiwgqhoXGHLjLXldcp9B1v8D2zGylC0XQB5lmNPliUTESV57uJ5xV2TLbsQhAb0G/qDgEuBxIRk5qxh0slpl8P8Nt25UZ4VUpQ2AUp7/s2s9+bAEGwAwdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_ACCESS_TOKEN = 'rsB4KZ3J1JMXNHQZbleM+1aAvdrpvnJR5aj4LsPZpY0bF+ebjDLmijtZSGx4I+B8kPdTFQ+cGKTzlb6JBJss7w4H7Cblq56WTIgCyLfXJ7rKsP665MQofQaZh4hvsPwQZVJkfguKI0XwzQSBdId2TwdB04t89/1O/w1cDnyilFU='
# LINE_CHANNEL_ACCESS_TOKEN = 'Ifr0DyhLP7T/z9P7jv9Wa7tkfsmHLA8UOPNd2PDu8cxyPCC/7Vuk1xqJL0v88uARO6gIFUgDtjnb+2DhF4fVBbAFeCHt/5FMZSoryyZvqFrMMNaje7TlXW1DOo04aUrXIwKHQlOe6ens+SesS57JhgdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def create_stock_menu():
    stock_menu = RichMenu(
        size = RichMenuSize(width=2500, height=1686),
        selected = True,
        name = "StockMenuNew",
        chat_bar_text = "我的頁面",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
                action=PostbackAction(label='news',data='command=news')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=833, y=0, width=833, height=843),
                action=PostbackAction(label='ind_stock',data='command=watch_list')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=1666, y=0, width=833, height=843),
                action=PostbackAction(label='exchange',data='command=exchange')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=843, width=833, height=843),
                action=PostbackAction(label='futures',data='command=futures')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=833, y=843, width=833, height=843),
                action=PostbackAction(label='info',data='command=info')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=1666, y=843, width=833, height=843),
                action=PostbackAction(label='vc',data='command=chatgpt')
            )

        ]
    )

    menu_id = line_bot_api.create_rich_menu(rich_menu=stock_menu)
    # richmenu-442aae2f19c05b9cdd7ede6bb6fc9c75 - now (prod)
    print(menu_id)
    return menu_id

def setup_stock_menu_image(menu_id):
    with open(r'menu_v2.jpg','rb') as f:
        line_bot_api.set_rich_menu_image(menu_id, 'image/jpeg', f)

def set_default_menu(menu_id):
    line_bot_api.set_default_rich_menu(menu_id)

if __name__ == '__main__':
    menu_id = create_stock_menu()
    setup_stock_menu_image(menu_id=menu_id)
    set_default_menu(menu_id=menu_id)

