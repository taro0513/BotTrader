from linebot.models import *
from urllib.parse import parse_qs


class CommandHandler:
    def __init__(self, data):
        self.data = data
        self.messages = []
        self.execute()

    def execute(self):
        commands = parse_qs(self.data).get("command", None)
        for command in commands:
            if command == "info":
                self.display_info()


    def display_info(self):
        self.messages.append(

            ImagemapSendMessage(
                base_url='https://i.imgur.com/6bCT53Y.jpg',
                alt_text='組圖訊息',
                base_size=BaseSize(width=1040, height=642),
                actions=[
                    URIImagemapAction(
                        link_uri='https://www.youtube.com/',
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
                    PostbackAction
                    ,
                    MessageImagemapAction(
                        text='操作說明',
                        area=ImagemapArea(
                            x=520, y=321, width=520, height=321
                        )
                    )
                ]
            )
        )