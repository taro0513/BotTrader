from .stock import *
from .exchange import *
from .news import *
from .command import *

import os
from pathlib import Path, PurePath
import speech_recognition
from speech_recognition import AudioFile, Recognizer
from pydub import AudioSegment
from linebot.models import *
from .chatgpt import chat_to_gpt3, num_tokens_from_string
from .models import HistoricalRecord

AudioSegment.converter = 'ffmpeg.exe'


class Handler:
    def __init__(self, event, line_bot_api):
        self.line_bot_api = line_bot_api
        self.event = event
        self.reply_token = event.reply_token
        self.user_id = self.event.source.user_id
        self.messages = []
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

    def MessageEventTextHandler(self, message_id=None, message_text=None, message_type=None):
        __key = None
        message_id = message_id or self.event.message.id 
        message_text = message_text or self.event.message.text
        message_type = message_type or self.event.message.type
        
        if message_text == '操作說明':
            self.messages.append(
                TextSendMessage(text='操作說明:\n')
            )
            return

        elif message_text == '歷史紀錄':
            records = HistoricalRecord.objects.filter(user_id=self.user_id).order_by('-created_at')[:5]
            print(records)
            self.messages.append(
                TextSendMessage(text='歷史紀錄')
            )

        if ChatGPT.objects.filter(user_id=self.event.source.user_id).exists():
            chatgpt = ChatGPT.objects.get(user_id=self.event.source.user_id)
            if chatgpt.active:
                response = chat_to_gpt3(message_text)
                if response:
                    self.messages.append(TextSendMessage(text='ChatGPT回答: '))
                    self.messages.append(TextSendMessage(text=response))
                else:
                    self.messages.append(TextSendMessage(text='ChatGPT無法回答'))
                return
            
                
            

        if '取消關注' in message_text:
            __key = '取消關注'
            message_text = message_text.replace('取消關注', '').upper().strip()
            data = StockWatchList.objects.filter(user_id=self.user_id, code=message_text).first()
            if not data:
                self.messages.append(
                    TextSendMessage(text='您並未關注此關鍵字')
                )
            else:
                StockWatchList.objects.filter(user_id=self.user_id, code=message_text).delete()
                self.messages.append(
                    TextSendMessage(text='已取消關注{}'.format(message_text)
                )
            )
            return


        if '關注' in message_text:
            __key = '關注'
            message_text = message_text.replace('關注', '')
        elif '取消' in message_text:
            __key = '取消'
            message_text = message_text.replace('取消', '')

        if '新聞' in message_text:
            message_text = message_text.replace('新聞', '')
            news = NewsHandler(message_text, key=__key, user_id=self.user_id) #  Detect if a message has a keyword in a news title
            news.detect()
            self.messages.extend(news.messages)
            return


        stock = StockHandler(message_text, self.user_id, key=__key) #  Detect if a message has a stock code or keyword
        stock.detect()
        self.messages.extend(stock.messages)

        exchange = ExchangeHandler(message_text) #  Detects if currency-related keywords in messages
        exchange.detect()
        self.messages.extend(exchange.messages)

        

    def MessageEventHandler(self):
        if isinstance(self.event.message, TextMessage):
            self.MessageEventTextHandler()

        elif isinstance(self.event.message, ImageMessage):
            ...
        elif isinstance(self.event.message, VideoMessage):
            ...
        elif isinstance(self.event.message, AudioMessage):
            audio_content = self.line_bot_api.get_message_content(self.event.message.id)
            Path("./static/sound/{}".format(self.user_id)).mkdir(parents=True, exist_ok=True)
            m4a_path = './static/sound/{}/{}.m4a'.format(self.user_id, self.event.message.id)
            with open(m4a_path, 'wb+') as fd:
                for chunk in audio_content.iter_content(): fd.write(chunk)
            recognizer = Recognizer()
            
            sound = AudioSegment.from_file_using_temporary_files(m4a_path)
            
            wav_path = Path(m4a_path).with_suffix('.wav')
            sound.export(wav_path, format="wav")

            with AudioFile(str(wav_path)) as source:
                audio = recognizer.record(source)
            
            # speech_to_text = r.recognize_google(audio, language='zh-Hant')
            try:
                speech_to_text = recognizer.recognize_google(audio, language='en-US')
                text = "語音訊息: {}".format(speech_to_text.lower())
                self.messages.append(TextSendMessage(text=text))
                self.MessageEventTextHandler(message_text=speech_to_text.lower())
            except:
                self.messages.append(TextSendMessage(text="無法辨識語音訊息"))
            
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
        command = CommandHandler(self.event.postback.data, self.user_id)
        self.messages.extend(command.messages)
