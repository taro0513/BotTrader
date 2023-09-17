from linebot.models import *
from urllib.parse import parse_qs
from .utils import currency_dict_alphabet
from .exchange import ExchangeHandler
from .models import StockWatchList, ChatGPT
from .stock import StockHandler
from .news import NewsHandler


class CommandHandler:
    def __init__(self, data, user_id):
        self.user_id = user_id
        self.data = data
        self.messages = []
        self.execute()

    def execute(self):
        self.commands = parse_qs(self.data).get("command", None)
        self.variables = parse_qs(self.data)
        for command in self.commands:
            print(command)
            if command == "info":
                self.display_info()
            elif command == 'exchange':
                self.display_exchange_list()
            elif command == 'display_exchange_info':
                self.display_exchange()
            elif command == 'watch_list':
                self.display_watch_list_confirmation_box()
            elif command == 'display_watch_list':
                self.display_watch_list()
            elif command == 'news':
                self.display_news()
            elif command == 'display_exchange_list_head':
                self.display_exchange_list_head()
            elif command == 'display_exchange_list_by_alphabet':
                self.display_exchange_list_by_alphabet()
            elif command == 'display_news_with_type':
                self.display_news_with_type()
            elif command == 'chatgpt':
                self.chat_gpt()
            elif command == 'futures':
                self.display_futures()
            elif command == 'display_futures_with_type':
                self.display_futures_with_type()
            elif command == 'display_futures_info':
                self.display_futures_info()

    def chat_gpt(self):
        if not ChatGPT.objects.filter(user_id=self.user_id).exists():
            ChatGPT.objects.create(user_id=self.user_id, active=True)
            self.messages.append(
                TextSendMessage(text='已開啟chatgpt')
            )
        else:
            if ChatGPT.objects.filter(user_id=self.user_id).first().active:
                ChatGPT.objects.filter(user_id=self.user_id).update(active=False)
                self.messages.append(
                    TextSendMessage(text='已關閉chatgpt')
                )
            else:
                ChatGPT.objects.filter(user_id=self.user_id).update(active=True)
                self.messages.append(
                    TextSendMessage(text='已開啟chatgpt')
                )
            
                

    def display_news(self):
        self.messages.append(
            TextSendMessage(
                text="新聞類型",
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label='頭條新聞', data='command=display_news_with_type&type=default')
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label='台股新聞', data='command=display_news_with_type&type=stock')
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label='國際新聞', data='command=display_news_with_type&type=world')
                        )
                    ]
                )
            )
        )

    def display_news_with_type(self):
        type = self.variables.get('type', ['stock'])[0]
        news = NewsHandler()
        news.command(type=type)
        self.messages.extend(news.messages)

    def display_watch_list(self):
        watch_list = StockWatchList.objects.filter(user_id=self.user_id)
        print(watch_list)
        for key in watch_list:
            print(key.code_type)
            if key.code_type == 'cryptocurrency':
                crypt = StockHandler(text=key.code)
                crypt.detect()
                self.messages.extend(crypt.messages)
            

            if key.code_type == 'News':
                news = NewsHandler(message_text=key.code)
                news.detect()
                print(news.messages)
                self.messages.extend(news.messages)
            
    def display_watch_list_confirmation_box(self):
        if StockWatchList.objects.filter(user_id=self.user_id).exists() == False:
            self.messages.append(
                TextSendMessage(text='目前關注清單為空，請新增關鍵字至關注\n(使用方法，輸入: ...關注)')
            )
        else:
            self.messages.append(
                TextSendMessage(
                    text="顯示關注清單需要一些時間，是否顯示",
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=PostbackAction(label='是', data='command=display_watch_list')
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label='否', data='command=None')
                            )
                        ]
                    )
                )
            )


    
    def display_exchange_list_by_alphabet(self):
        alphabet = self.variables.get('alphabet', ['A'])[0]
        pages = int(self.variables.get('page', [0])[0])
        from_c = self.variables.get('from_c', [None])[0]
        items = []
        if from_c:
            if pages == 0 and len(currency_dict_alphabet[alphabet]) > 10:
                items.extend(
                    [
                        QuickReplyButton(action=PostbackAction(label=currency_dict_alphabet[alphabet][i], data="command=display_exchange_info&from_c={}&to_c={}".format(from_c, currency_dict_alphabet[alphabet][i]))) for i in range(10)
                    ]
                )
                items.append(
                    QuickReplyButton(action=PostbackAction(label='下一頁', data="command=display_exchange_list_by_alphabet&alphabet={}&page={}&from_c={}".format(alphabet, pages+1, from_c)))
                )
            elif pages == 0:
                items.extend(
                    [
                        QuickReplyButton(action=PostbackAction(label=currency_dict_alphabet[alphabet][i], data="command=display_exchange_info&from_c={}&to_c={}".format(from_c, currency_dict_alphabet[alphabet][i]))) for i in range(len(currency_dict_alphabet[alphabet]))
                    ]
                )
            else:
                items.append(
                    QuickReplyButton(action=PostbackAction(label='上一頁', data="command=display_exchange_list_by_alphabet&alphabet={}&page={}&from_c={}".format(alphabet, pages-1, from_c)))
                )
                items.extend(
                    [
                        QuickReplyButton(action=PostbackAction(label=currency_dict_alphabet[alphabet][i], data="command=display_exchange_info&from_c={}&to_c={}".format(from_c, currency_dict_alphabet[alphabet][i]))) for i in range(10*pages, 10*(pages+1))
                    ]
                )
        else:
            if pages == 0 and len(currency_dict_alphabet[alphabet]) > 10:
                items.extend(
                    [
                        QuickReplyButton(action=PostbackAction(label=currency_dict_alphabet[alphabet][i], data="command=display_exchange_info&from_c={}".format(currency_dict_alphabet[alphabet][i]))) for i in range(10)
                    ]
                )
                items.append(
                    QuickReplyButton(action=PostbackAction(label='下一頁', data="command=display_exchange_list_by_alphabet&alphabet={}&page={}".format(alphabet, pages+1)))
                )
            elif pages == 0:
                items.extend(
                    [
                        QuickReplyButton(action=PostbackAction(label=currency_dict_alphabet[alphabet][i], data="command=display_exchange_info&from_c={}".format(currency_dict_alphabet[alphabet][i]))) for i in range(len(currency_dict_alphabet[alphabet]))
                    ]
                )
            else:
                items.append(
                    QuickReplyButton(action=PostbackAction(label='上一頁', data="command=display_exchange_list_by_alphabet&alphabet={}&page={}".format(alphabet, pages-1)))
                )
                items.extend(
                    [
                        QuickReplyButton(action=PostbackAction(label=currency_dict_alphabet[alphabet][i], data="command=display_exchange_info&from_c={}".format(currency_dict_alphabet[alphabet][i]))) for i in range(10*pages, 10*(pages+1))
                    ]
                )
        self.messages.append(
            TextSendMessage(
                text="請選擇要顯示的匯率(字母: {})".format(alphabet),
                quick_reply=QuickReply(
                    items=items
                )
            )
        )


    def display_exchange(self):
        from_c = self.variables.get('from_c', [None])[0]
        to_c = self.variables.get('to_c', [None])[0]

        if not to_c:
            self.display_exchange_list(from_c=from_c)

        if from_c and to_c:
            if len(self.variables.get('to_c')) > 1:
                from_c = from_c[-3:]
                to_c = self.variables.get('to_c')
                exchange_info = ExchangeHandler().get_exchange_conversion(from_c=from_c, to_c=to_c)
                self.messages.append(exchange_info)

            else:
                from_c = from_c[-3:]
                to_c = to_c[-3:]

                exchange_info = ExchangeHandler().get_exchange_conversion(from_c=from_c, to_c=to_c)
                self.messages.append(exchange_info)
    
    def display_exchange_list_head(self):
        from_c = self.variables.get('from_c', [None])[0]
        pages = int(self.variables.get('page', [0])[0])
        alphabet_list = (
            ('ABCDEFGHIJ'),
            ('KLMNOPQRST'),
            ('UVWXYZ')
        )
        items = []
        if from_c:
            if pages > 0:
                items.append(
                    QuickReplyButton(action=PostbackAction(label='上一頁', data="command=display_exchange_list_head&page={}&from_c={}".format(pages-1, from_c)))
                )
            items.extend([
                QuickReplyButton(action=PostbackAction(label=alphabet, data="command=display_exchange_list_by_alphabet&alphabet={}&from_c={}".format(alphabet, from_c))) for alphabet in alphabet_list[pages]
                ])
            if pages < 2:
                items.append(
                    QuickReplyButton(action=PostbackAction(label='下一頁', data="command=display_exchange_list_head&page={}&from_c".format(pages+1, from_c)))
                )
            self.messages.append(
                TextSendMessage(
                    text="請選擇要顯示的匯率({})".format(alphabet_list[pages]),
                    quick_reply=QuickReply(
                        items=items
                    )
                )
            )
        else:
            if pages > 0:
                items.append(
                    QuickReplyButton(action=PostbackAction(label='上一頁', data="command=display_exchange_list_head&page={}".format(pages-1)))
                )
            items.extend([
                QuickReplyButton(action=PostbackAction(label=alphabet, data="command=display_exchange_list_by_alphabet&alphabet={}".format(alphabet))) for alphabet in alphabet_list[pages]
                ])
            if pages < 2:
                items.append(
                    QuickReplyButton(action=PostbackAction(label='下一頁', data="command=display_exchange_list_head&page={}".format(pages+1)))
                )
            self.messages.append(
                TextSendMessage(
                    text="請選擇要顯示的匯率({})".format(alphabet_list[pages]),
                    quick_reply=QuickReply(
                        items=items
                    )
                )
            )

    def display_exchange_list(self, from_c = None):
        if not from_c:
            self.messages.append(
            TextSendMessage(
                text="請選擇要顯示的匯率-基底貨幣",
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label="台幣TWD", data="command=display_exchange_info&from_c=TWD")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="美金USD", data="command=display_exchange_info&from_c=USD")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="人民幣CNY", data="command=display_exchange_info&from_c=CNY")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="日幣JPY", data="command=display_exchange_info&from_c=JPY")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="歐元EUR", data="command=display_exchange_info&from_c=EUR")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="港幣HKD", data="command=display_exchange_info&from_c=HKD")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="英鎊GBP", data="command=display_exchange_info&from_c=GBP")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="依字母選擇", data="command=display_exchange_list_head&page=0")
                            )
                    ]
                )
            )
        )
        else:
            self.messages.append(
                TextSendMessage(
                    text="請選擇要顯示的匯率-兌換貨幣",
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=PostbackAction(label="顯示多數常用", 
                                                      data="command=display_exchange_info&"
                                                           "from_c={}&to_c=TWD&to_c=USD&to_c=CNY&to_c=JPY&to_c=EUR&to_c=HKD&to_c=GBP".format(from_c))
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label="台幣TWD", data="command=display_exchange_info&from_c=TWD")
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label="美金USD", data="command=display_exchange_info&from_c={}&to_c=USD".format(from_c))
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label="人民幣CNY", data="command=display_exchange_info&from_c={}&to_c=CNY".format(from_c))
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label="日幣JPY", data="command=display_exchange_info&from_c={}&to_c=JPY".format(from_c))
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label="歐元EUR", data="command=display_exchange_info&from_c={}&to_c=EUR".format(from_c))
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label="港幣HKD", data="command=display_exchange_info&from_c={}&to_c=HKD".format(from_c))
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label="英鎊GBP", data="command=display_exchange_info&from_c={}&to_c=GBP".format(from_c))
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label="依字母選擇", data="command=display_exchange_list_head&page=0&from_c={}".format(from_c))
                                )
                        ]
                    )
                )
            )

    def display_info(self):

        self.messages.append(

            ImagemapSendMessage(
                base_url='https://i.imgur.com/6bCT53Y.jpg',
                alt_text='組圖訊息',
                base_size=BaseSize(width=1040, height=642),
                actions=[
                    MessageImagemapAction(
                        text='歷史紀錄',
                        area=ImagemapArea(
                            x=0, y=0, width=520, height=321
                        )
                    ),
                    URIImagemapAction(
                        link_uri='https://www.youtube.com/',
                        area=ImagemapArea(
                            x=520, y=0, width=520, height=321
                        )
                    ),
                    URIImagemapAction(
                        link_uri='https://www.youtube.com/',
                        area=ImagemapArea(
                            x=0, y=321, width=520, height=321
                        )
                    ),
                    MessageImagemapAction(
                        text='操作說明',
                        area=ImagemapArea(
                            x=520, y=321, width=520, height=321
                        )
                    )
                ]
            )
        )
    
    def display_futures(self):
        self.messages.append(
            TextSendMessage(
                text="期貨類型",
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label='股票型期貨', data='command=display_futures_with_type&type=stock')
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label='指數型期貨', data='command=display_futures_with_type&type=index')
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label='ETF型期貨', data='command=display_futures_with_type&type=etf')
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label='綜合型期貨', data='command=display_futures_with_type&type=comprehensive')
                        )
                    ]
                )
            )
        )
    
    def display_futures_with_type(self):
        type = self.variables.get('type', ['stock'])[0]
        print(type)
        if type == 'stock':
            self.messages.append(
                TextSendMessage(
                    text="股票型期貨",
                    quick_reply=QuickReply(
                        items = [
                            QuickReplyButton(
                                action=PostbackAction(label='台積電', data='command=display_futures_info&code=2330')
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label='聯電', data='command=display_futures_info&code=2303')
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label='大立光', data='command=display_futures_info&code=3008')
                            ),
                        ]
                    )
                )
            )
        elif type == 'index':
            self.messages.append(
                TextSendMessage(
                    text = "指數型期貨",
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=PostbackAction(label='台指期', data='command=display_futures_info&code=TX')
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label='道瓊', data='command=display_futures_info&code=DJI')
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label='那斯達克', data='command=display_futures_info&code=NAS')
                            )
                        ]
                    )
                )
            )
        elif type == 'etf':
            self.messages.append(
                TextSendMessage(
                    text = "ETF型期貨",
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=PostbackAction(label='元大高股息', data='command=display_futures_info&code=0056')
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label='國泰永續高股息', data='command=display_futures_info&code=006208')
                            )
                        ]
                    )
                )
            )
        elif type == 'comprehensive':
            self.messages.append(
                TextSendMessage(
                    text = "綜合型期貨",
                    quick_reply = QuickReply(
                        # 石油、黃金、原油、歐元
                        items=[
                            QuickReplyButton(
                                action=PostbackAction(label='石油', data='command=display_futures_info&code=CL')
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label='黃金', data='command=display_futures_info&code=GC')
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label='原油', data='command=display_futures_info&code=CL')
                            ),
                            QuickReplyButton(
                                action=PostbackAction(label='歐元', data='command=display_futures_info&code=6E')
                            )
                        ]
                    )
                )
            )

    def display_futures_info(self):
        code = self.variables.get('code', [None])[0]
        print(code)
        # if code:
        #     futures = FuturesHandler(text=code)
        #     futures.detect()
        #     self.messages.extend(futures.messages)