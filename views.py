from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi,WebhookParser
from linebot.exceptions import InvalidSignatureError,LineBotApiError
from linebot.models import MessageEvent, TextSendMessage ,TextMessage

import googlemaps
import random
import os


line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
def get_weigth(id):
    path = './ID' + str(id) + '.txt'
    if os.path.isfile(path):
        f = open(path, 'r')
        weight = list()
        for i in f.readline():
            if i != ' ':
                weight.append(int(i))
        f.close()
        f = open(path, 'w')
    else:
        f = open(path, 'w')
        weight = [5, 5, 5, 5, 5, 5]
    return weight, f



@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        ids = []
        stores_info = []
        choices = ['中式', '西式', '飯', '麵', '小吃', '港式']
        gmaps = googlemaps.Client(key='AIzaSyD3bgEOAkulGGTWeUMQTafiFCLtPFJq1uU')    


        for event in events:
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessage):
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))
                else:
                    place = event.message.address
                    geocode_result = gmaps.geocode(place)
                    loc = geocode_result[0]['geometry']['location']
                    weight, f = get_weigth(event.source.user_id)
                    for i in range(0, 6):
                        stores = gmaps.places_nearby(keyword=choices[i], location=loc, radius=1000000)['results']
                        for j in range(0, weight[i]):
                            if j < stores.length():
                                ids.append(stores[j])
                    ids = list(ids)
                    for id in ids:
                        stores_info.append(gmaps.place(place_id=id,language='zh-TW')['result']['name'])
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=str(stores_info)))
                    f.write(str(weight))
                    
        return HttpResponse()
    else:
        return HttpResponseBadRequest()        



# Create your views here.
