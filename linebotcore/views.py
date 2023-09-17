from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
from .handler import Handler
from .models import ChatGPT
from .chatgpt import chat_to_gpt3, num_tokens_from_string

import os
from pyngrok import ngrok
import requests

def run_ngrok():
    http_tunnel = ngrok.connect(8000, 'http')
    return http_tunnel.public_url
    
def set_webhook(public_url):
    headers = {
        'Authorization': 'Bearer {}'.format(settings.LINE_CHANNEL_ACCESS_TOKEN),
        'Content-Type': 'application/json'
    }
    r = requests.put('https://api.line.me/v2/bot/channel/webhook/endpoint',
                        headers=headers,
                     json={
                         'endpoint': public_url + '/callback'
                     })
    if r.status_code == 200:
        print('Set webhook OK')
    else:
        print('Set webhook NG')
        print(r.text)
        os._exit(0)

public_url = run_ngrok()
set_webhook(public_url)

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError as e:
            return HttpResponseForbidden()
        except LineBotApiError as e:
            return HttpResponseBadRequest()

        for event in events:
            if not ChatGPT.objects.filter(user_id=event.source.user_id).exists():
                ChatGPT.objects.create(user_id=event.source.user_id)
                
            handler = Handler(event, line_bot_api)
            if handler.messages:
                messages: list = handler.messages[:5]
                line_bot_api.reply_message(handler.reply_token, messages)
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='沒有相關資訊，點選右下角ChatGPT圖示以開啟ChatGPT功能。若有任何需要協助，請聯絡客服中心!'))

        return HttpResponse()
    else:
        return HttpResponseBadRequest()