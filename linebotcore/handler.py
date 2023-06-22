from linebot.models import *
from .stock import *
from .exchange import *
from .news import *
from .command import *
class Handler:
    def __init__(self, event):
        self.event = event
        self.reply_token = event.reply_token
        self.message = []
        self.execute()

    def execute(self):
        if isinstance(self.event, MessageEvent):
            self.MessageEventHandler()
        elif isinstance(self.event, FollowEvent):
            self.FollowEventHandler()
        elif isinstance(self.event, UnfollowEvent):
            self.UnfollowEventHandler()
        elif isinstance(self.event, JoinEvent):
            self.JoinEventHandler()
        elif isinstance(self.event, LeaveEvent):
            self.LeaveEventHandler()
        elif isinstance(self.event, MemberJoinedEvent):
            self.MemberJoinedEventHandler()
        elif isinstance(self.event, PostbackEvent):
            self.PostbackEventHandler()



    def MessageEventHandler(self):
        if isinstance(self.event.message, TextMessage):
            message_id = self.event.message.id
            message_text = self.event.message.text
            message_type = self.event.message.type

            stock = StockHandler(message_text) #  Detect whether the message has a stock code or keyword
            self.message.extend(stock.messages)
            exchange = ExchangeHandler(message_text) #  Detect whether the message has a currency keyword
            self.message.extend(exchange.messages)
            news = NewsHandler(message_text) #  Detect whether the message has a news keyword
            self.message.extend(news.messages)


        elif isinstance(self.event.message, ImageMessage):
            ...
        elif isinstance(self.event.message, VideoMessage):
            ...
        elif isinstance(self.event.message, AudioMessage):
            ...
        elif isinstance(self.event.message, FileMessage):
            ...
        elif isinstance(self.event.message, LocationMessage):
            ...
        elif isinstance(self.event.message, StickerMessage):
            ...
    def FollowEventHandler(event):
        ...
    def UnfollowEventHandler(event):
        ...
    def JoinEventHandler(event):
        ...
    def LeaveEventHandler(event):
        ...
    def MemberJoinedEventHandler(event):
        ...
    def MemberLeaveEventHandler(event):
        ...
    def PostbackEventHandler(self):
        command = CommandHandler(self.event.postback.data)
        self.message.extend(command.messages)
